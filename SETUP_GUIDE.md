# 情報収集 × Obsidian 環境セットアップガイド

## 全体像

```
X / Web / YouTube
      ↓
  【キャプチャ】
  ├─ Obsidian Web Clipper (ブラウザ拡張)
  ├─ capture.py スクリプト (AI要約付き)
  └─ Readwise Reader (X/Twitterメイン)
      ↓
  【整理・タグ付け】
   Claude API が自動で要約・タグ付け
      ↓
  【蓄積・検索】
   Obsidian (ローカル Vault)
   + Smart Connections (AI検索)
      ↓
  【同期】
   PC ↔ スマホ (iCloud / Obsidian Sync)
```

---

## Step 1: Obsidian のセットアップ

### 1-1. Vault の作成
1. [Obsidian](https://obsidian.md/) をダウンロード・インストール
2. 新しい Vault を作成（例: `~/Documents/MyVault`）
3. `obsidian-vault/` フォルダの内容を Vault にコピー

### 1-2. おすすめプラグイン（Settings → Community plugins）

| プラグイン | 用途 | 優先度 |
|-----------|------|--------|
| **Templater** | テンプレートをキーボードショートカットで挿入 | ★必須 |
| **Smart Connections** | AI によるセマンティック検索（ノート横断） | ★必須 |
| **Dataview** | タグ・日付でノートを一覧表示 | 推奨 |
| **Tag Wrangler** | タグの管理・リネーム | 推奨 |
| **Calendar** | 日付ベースのナビゲーション | 任意 |

---

## Step 2: Web クリッピング（ブラウザ拡張）

### Obsidian Web Clipper（公式・無料）
1. [Chrome 拡張](https://chrome.google.com/webstore/detail/obsidian-web-clipper) または [Firefox 拡張](https://addons.mozilla.org/en-US/firefox/addon/obsidian-web-clipper/) をインストール
2. 拡張の設定で Vault を選択し、保存先フォルダを `00_Inbox` に設定
3. テンプレートに `web-article.md` の内容を設定

**使い方**: 気になるページで拡張アイコンをクリック → Obsidian に保存

---

## Step 3: X (Twitter) の取り込み（Readwise）

X の情報取り込みには **Readwise Reader** が最もスムーズです。

### Readwise Reader のセットアップ
1. [Readwise](https://readwise.io/) アカウント作成（7日間無料トライアル、$7.99/月）
2. X アカウントを連携 → ブックマークが自動同期
3. Obsidian の **Readwise Official** プラグインをインストール
4. プラグイン設定で API キーを入力 → 自動同期開始

**メリット**: X のブックマーク・ハイライトが毎日自動で Obsidian に入ってくる

---

## Step 4: AI 自動要約スクリプト（capture.py）

### セットアップ
```bash
# 依存パッケージのインストール
pip install anthropic requests beautifulsoup4

# Anthropic API キーを設定
export ANTHROPIC_API_KEY=your_api_key_here
# ※永続化する場合は ~/.zshrc や ~/.bashrc に追記
```

### 使い方
```bash
# Web 記事を保存（自動判定）
python capture.py https://example.com/article

# Vault の場所を指定
python capture.py https://example.com/article --vault ~/Documents/MyVault

# X のツイートを保存
python capture.py https://x.com/user/status/123456789

# YouTube 動画を保存
python capture.py https://youtube.com/watch?v=xxxxx

# タイプを手動指定
python capture.py https://example.com --type web
```

**実行結果のイメージ**:
```
📥 取得中: https://example.com/article
🤖 Claude で解析中...
✅ ノートを保存しました: ~/Documents/MyVault/10_Web/20240228_AIの最新動向.md
   タイトル : AIの最新動向2024
   タグ     : テクノロジー, AI, 機械学習
   カテゴリ : テクノロジー
```

---

## Step 5: スマホ対応（PC ↔ スマホ同期）

### 方法A: iCloud（Mac ユーザー推奨・無料）
1. Vault を `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault` に作成
2. iPhone の Obsidian アプリから同じ Vault を開く

### 方法B: Obsidian Sync（クロスプラットフォーム・$10/月）
1. Obsidian アカウントを作成
2. Settings → Sync → 新しい Remote Vault を作成
3. スマホの Obsidian でも同じアカウントで同期

---

## Step 6: AI 検索（Smart Connections）

Smart Connections プラグインを使うと、キーワードではなく「意味」で検索できます。

### セットアップ
1. Obsidian → Settings → Community plugins → Smart Connections をインストール
2. Settings → Smart Connections → OpenAI API key または Anthropic API key を入力
3. Ctrl+Shift+; でサイドパネルを開いて検索

**例**: 「AI について書かれたノートを全部見せて」→ 関連ノートが一覧表示

---

## 運用フロー（デイリーワークフロー）

```
【インプット時（その都度）】
  ① 気になる記事やツイートに出会う
  ② Obsidian Web Clipper で保存 or capture.py を実行
  ③ 00_Inbox に保存される

【週次レビュー（週1回・15分）】
  ④ 00_Inbox のノートを確認
  ⑤ タグ・カテゴリを確認・修正
  ⑥ 「自分のメモ」欄に気づきを追記
  ⑦ 適切なフォルダ（10_Web 等）に移動

【アウトプット時】
  ⑧ Smart Connections で関連ノートを横断検索
  ⑨ ノート間をリンク（[[ノート名]]）で繋ぐ
  ⑩ 記事・ブログ・発信の素材として活用
```

---

## コスト目安

| ツール | 料金 |
|-------|------|
| Obsidian | 無料（商用利用は $50/年） |
| Obsidian Web Clipper | 無料 |
| Readwise | $7.99/月（X 連携が必要な場合） |
| Obsidian Sync | $10/月（iCloud で代替可） |
| Anthropic API | 従量課金（capture.py、$1〜3/月程度） |
| Smart Connections | 無料（API キー別途） |

---

## よくある質問

**Q: Readwise は本当に必要？**
A: X のブックマーク自動同期が目的なら必要。Web 記事だけなら Web Clipper + capture.py で十分です。

**Q: capture.py と Web Clipper の使い分けは？**
A: AI 要約が欲しい時は capture.py、サクッと保存したい時は Web Clipper が便利です。

**Q: API キーはどこで取得する？**
A: [Anthropic Console](https://console.anthropic.com/) でアカウント作成後、API Keys から発行できます。
