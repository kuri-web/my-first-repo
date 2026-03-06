# Obsidian Vault - Claude Code 設定

このリポジトリは Obsidian Vault として使用しています。

## Vault フォルダ構造

```
my-first-repo/
├── Inbox/          # Web Clipper が保存する未整理クリップ
├── Clips/          # 整理済みクリップ（カテゴリ別）
│   ├── AI/         # AI・機械学習・LLM 関連
│   ├── Dev/        # プログラミング・開発・OSS 関連
│   ├── Cloud/      # AWS・GCP・Azure・Kubernetes・インフラ関連
│   ├── Business/   # ビジネス・マインドセット・キャリア関連
│   └── Other/      # 上記に当てはまらないもの
├── Templates/      # Obsidian テンプレート
├── Assets/         # 画像などの添付ファイル
└── マインドセット/   # マインドセット関連のノート
```

## クリップ整理の方針

`Inbox/` に溜まったクリップを整理する際は以下の手順に従う：

1. `Inbox/` 内の `.md` ファイル（`.gitkeep` 除く）を全て確認する
2. 各ファイルの frontmatter（title, source）と本文を読み、カテゴリを判断する
3. カテゴリ判断の基準：
   - **AI**: AI・機械学習・LLM・ChatGPT・Claude・画像生成など
   - **Dev**: プログラミング・GitHub・ライブラリ・フレームワーク・アーキテクチャなど
   - **Cloud**: AWS・GCP・Azure・Kubernetes・Docker・Terraform・インフラなど
   - **Business**: ビジネス・マインドセット・キャリア・組織・マネジメントなど
   - **Other**: 上記に当てはまらない場合
4. `Clips/<カテゴリ>/` フォルダへ移動する
5. frontmatter に以下を追加・更新する：
   - `category`: カテゴリ名（AI / Dev / Cloud / Business / Other）
   - `organized_at`: 整理した日付（YYYY-MM-DD 形式）
6. `Inbox/` から元ファイルを削除する
7. 整理結果をサマリーとして報告する

カテゴリの判断に迷う場合は `Other/` に分類する。
