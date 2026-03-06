# my-first-repo

Obsidian Vault + Claude Code による Web クリップ自動整理システム。

## セットアップ

### 1. Obsidian でこのリポジトリを Vault として開く

Obsidian を起動 → 「別のフォルダをVaultとして開く」 → このリポジトリのフォルダを選択

### 2. Obsidian Web Clipper の設定

ブラウザ拡張の設定で以下を指定する：

| 項目 | 設定値 |
|------|--------|
| Vault | `my-first-repo` |
| Note location | `Inbox` |
| Template | `Templates/Web Clip` |

### 3. pre-commit hook の有効化（クローン後のみ）

`.git/hooks/` はリポジトリに含まれないため、クローン後に一度だけ実行：

```bash
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 使い方

### Web ページをクリップする

1. ブラウザで対象ページを開く
2. Web Clipper 拡張のボタンを押す
3. `Inbox/` に Markdown ファイルが保存される

### クリップを整理する（自動）

```bash
git add Inbox/
git commit -m "add clips"
```

`Inbox/` に新しいファイルがあると pre-commit hook が Claude Code を呼び出し、
自動でカテゴリ判断 → `Clips/<カテゴリ>/` へ移動 → frontmatter 更新を行う。

### クリップを整理する（手動）

Claude Code 上で以下を実行：

```
/organize
```

## フォルダ構造

```
my-first-repo/
├── Inbox/          # Web Clipper の保存先（未整理）
├── Clips/
│   ├── AI/         # AI・機械学習・LLM
│   ├── Dev/        # 開発・プログラミング
│   ├── Cloud/      # クラウド・インフラ
│   ├── Business/   # ビジネス・マインドセット
│   └── Other/      # その他
├── Templates/      # Obsidian テンプレート
├── Assets/         # 添付ファイル
└── マインドセット/
```
