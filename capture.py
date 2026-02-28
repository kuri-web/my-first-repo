#!/usr/bin/env python3
"""
Web Content Capture Tool for Obsidian
--------------------------------------
URL を渡すと Claude が要約・タグ付けして Obsidian ノートを生成します。

使い方:
  python capture.py <URL>
  python capture.py <URL> --vault ~/Documents/MyVault
  python capture.py <URL> --type web|x|youtube|idea

必要な環境変数:
  ANTHROPIC_API_KEY=your_api_key_here
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import anthropic
except ImportError:
    print("エラー: anthropic パッケージが必要です。以下を実行してください:")
    print("  pip install anthropic requests beautifulsoup4")
    sys.exit(1)

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("エラー: requests と beautifulsoup4 が必要です。以下を実行してください:")
    print("  pip install requests beautifulsoup4")
    sys.exit(1)


# --- 設定 ---
DEFAULT_VAULT_PATH = Path.home() / "Documents" / "MyVault"
INBOX_FOLDER = "00_Inbox"
OUTPUT_FOLDERS = {
    "web": "10_Web",
    "x": "20_X_Twitter",
    "youtube": "30_YouTube",
    "idea": "40_Ideas",
}


def detect_content_type(url: str) -> str:
    """URL からコンテンツタイプを自動判定する"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if "twitter.com" in domain or "x.com" in domain:
        return "x"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    return "web"


def fetch_content(url: str) -> dict:
    """URL からコンテンツを取得する"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # タイトル取得
        title = ""
        if soup.title:
            title = soup.title.string or ""
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content", "")

        # 本文取得（article タグ優先、次に main、なければ body）
        content = ""
        for tag in ["article", "main", "body"]:
            element = soup.find(tag)
            if element:
                # スクリプト・スタイル除去
                for s in element(["script", "style", "nav", "footer", "header"]):
                    s.decompose()
                content = element.get_text(separator="\n", strip=True)
                break

        # 長すぎる場合は先頭 4000 文字に制限
        content = content[:4000] if len(content) > 4000 else content

        return {"title": title.strip(), "content": content, "url": url}

    except requests.RequestException as e:
        print(f"警告: コンテンツ取得に失敗しました ({e})")
        return {"title": "", "content": "", "url": url}


def summarize_with_claude(data: dict, content_type: str) -> dict:
    """Claude API でコンテンツを要約・タグ付けする"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: ANTHROPIC_API_KEY 環境変数が設定されていません。")
        print("  export ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    type_instructions = {
        "web": "これはウェブ記事・ブログ記事です。",
        "x":   "これは X (Twitter) のツイート・スレッドです。",
        "youtube": "これは YouTube 動画のページです。",
        "idea": "これは個人のアイデアメモです。",
    }

    prompt = f"""以下のコンテンツを Obsidian のナレッジベース用にまとめてください。
{type_instructions.get(content_type, '')}

URL: {data['url']}
タイトル: {data['title']}
コンテンツ:
{data['content']}

以下の JSON 形式で回答してください（日本語で）:
{{
  "title": "簡潔なノートタイトル（30文字以内）",
  "summary": "3〜5文の要約",
  "key_points": ["重要ポイント1", "重要ポイント2", "重要ポイント3"],
  "tags": ["タグ1", "タグ2", "タグ3"],
  "category": "このノートが属するカテゴリ（例: テクノロジー, ビジネス, 学習, アイデアなど）"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text

    # JSON を抽出
    import json
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # JSON パース失敗時のフォールバック
    return {
        "title": data["title"] or "無題",
        "summary": response_text[:500],
        "key_points": [],
        "tags": [content_type],
        "category": "未分類",
    }


def create_obsidian_note(url: str, content_type: str, data: dict, ai_result: dict) -> str:
    """Obsidian 用 Markdown ノートを生成する"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    tags_yaml = "\n".join(f"  - {tag}" for tag in ai_result.get("tags", []))
    key_points = "\n".join(
        f"- {point}" for point in ai_result.get("key_points", [])
    )

    type_emoji = {"web": "🌐", "x": "🐦", "youtube": "▶️", "idea": "💡"}.get(content_type, "📄")
    type_label = {"web": "Web記事", "x": "X/Twitter", "youtube": "YouTube", "idea": "アイデア"}.get(content_type, "メモ")

    note = f"""---
title: "{ai_result.get('title', '無題')}"
type: {type_label}
source: {url}
date: {date_str}
tags:
{tags_yaml}
category: {ai_result.get('category', '未分類')}
created: {date_str} {time_str}
---

# {type_emoji} {ai_result.get('title', '無題')}

## 📝 要約

{ai_result.get('summary', '')}

## ✅ 重要ポイント

{key_points}

## 🔗 ソース

- **URL**: [{url}]({url})
- **取得日**: {date_str}
- **種別**: {type_label}

---

## 💬 自分のメモ

<!-- ここに自分の考えや感想を書く -->

"""
    return note


def save_note(note_content: str, title: str, content_type: str, vault_path: Path) -> Path:
    """ノートをファイルに保存する"""
    folder = OUTPUT_FOLDERS.get(content_type, INBOX_FOLDER)
    output_dir = vault_path / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    # ファイル名に使えない文字を除去
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_title = safe_title[:50].strip()
    date_prefix = datetime.now().strftime("%Y%m%d")
    filename = f"{date_prefix}_{safe_title}.md"

    filepath = output_dir / filename
    filepath.write_text(note_content, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="URL から Obsidian ノートを自動生成します"
    )
    parser.add_argument("url", help="保存したい URL（または --idea でテキスト入力）")
    parser.add_argument(
        "--vault",
        default=str(DEFAULT_VAULT_PATH),
        help=f"Obsidian Vault のパス（デフォルト: {DEFAULT_VAULT_PATH}）",
    )
    parser.add_argument(
        "--type",
        choices=["web", "x", "youtube", "idea"],
        help="コンテンツタイプを手動指定（省略時は自動判定）",
    )
    args = parser.parse_args()

    vault_path = Path(args.vault)
    url = args.url
    content_type = args.type or detect_content_type(url)

    print(f"📥 取得中: {url}")
    data = fetch_content(url)

    print("🤖 Claude で解析中...")
    ai_result = summarize_with_claude(data, content_type)

    note_content = create_obsidian_note(url, content_type, data, ai_result)

    filepath = save_note(note_content, ai_result.get("title", "無題"), content_type, vault_path)

    print(f"✅ ノートを保存しました: {filepath}")
    print(f"   タイトル : {ai_result.get('title')}")
    print(f"   タグ     : {', '.join(ai_result.get('tags', []))}")
    print(f"   カテゴリ : {ai_result.get('category')}")


if __name__ == "__main__":
    main()
