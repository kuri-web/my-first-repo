## はじめに

お疲れ様です、データ事業本部の小高です。

日々の業務の中で、後で読み返したい技術記事やドキュメントに出会う場面は多いと思います。ただ、それらの情報はSlackで様々なチャンネルで共有されたリンク、ブラウザで見つけた記事など **あちこちに点在** していて、いざ必要なときに見つけられないという経験があると思います。

そこで、 **Obsidian Web Clipper** でWebページをMarkdown形式で保存し、 **Claude Codeのskills（/clip）** で記事の内容をAIに読み取らせて、AWSやGCP、Terraformのようなカテゴリ別フォルダに自動整理する仕組みを作ってみました。

## 背景と課題

### 従来の課題

気になる技術記事やドキュメントを見つけても、保存場所がバラバラになりがちでした：

- **Slack**
	- チームメンバーが共有してくれた記事のリンクが流れていく
- **ブラウザ**
	- 一時的にブックマークに入れるが、パッと探し出せない

結果として、「あの記事どこで見たっけ…」と探す時間が発生していました。

### やりたかったこと

- 情報の保存先を **一箇所に集約** したい
- 保存した記事をAWS、GCP、Terraformなどのカテゴリで自動分類したい
- フォルダ階層を自動で作成し、手動での整理作業をゼロにしたい

## 使用するツール

| ツール | 役割 |
| --- | --- |
| [Obsidian Web Clipper](https://obsidian.md/clipper) | ブラウザ拡張。WebページをMarkdown形式でObsidian Vaultに保存 |
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | AnthropicのCLIツール。カスタムスキル機能でAIによる記事分類を実現 |

## 仕組みの全体像

```
① ブラウザで記事をクリップ（Obsidian Web Clipper）
  ↓ Markdown形式で保存
② Obsidian Vault の 06_Articles/ に蓄積
  ↓ 記事が溜まったら...
③ Claude Code で /clip を実行
  ↓ AIが記事の内容を読み取り、カテゴリを判定
④ ~/Documents/articles/ 配下に自動整理
     AWS/
       S3Tables/
       IAM/
     Terraform/
       Basics/
     GCP/
       CloudRun/
```

> **補足:** 今回、Obsidian Vaultから `~/Documents/articles/` へフォルダ間移動をしているのは、私がまだObsidianを使いこなせておらず、Obsidian上で記事を一元管理する運用ができていないためです。普段使い慣れている `~/Documents/` 配下で管理する方が自分にとって扱いやすいので、このような構成にしています。Obsidianをメインのナレッジベースとして活用している方は、Vault内でフォルダ整理する構成で良いと思います。

## やってみた

### 前提条件

- Claude Codeがインストール済み
- Obsidianがインストール済み
- Obsidian Web Clipper（ブラウザ拡張）がインストール済み

### ステップ1: Obsidian Web Clipperの設定

Obsidian Web Clipperは、ブラウザで表示中のWebページをMarkdown形式に変換し、Obsidian Vaultに保存するブラウザ拡張機能です。

[Chrome ウェブストア](https://chromewebstore.google.com/detail/obsidian-web-clipper/cnjifjpddelmedmihgijeibhnjfabmlf) からインストールし、保存先フォルダを設定します。

今回は `06_Articles` というフォルダをクリップの一時保管場所としています。

### ステップ2: /clip skillの作成

Claude Codeのskills機能を使って、記事を自動分類するスキルを作成します。

`~/.claude/skills/clip/SKILL.md` に以下のファイルを作成します：

```markdown
---
name: clip
description: Obsidian Web Clipperで保存された記事を読み取り、内容に基づいてカテゴリ・サブカテゴリを判定し、~/Documents/articles/ 配下にフォルダ階層を作成して自動整理する。
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(mkdir *)
  - Bash(mv *)
  - Bash(ls *)
---

# Web Clip 記事整理スキル

Obsidian Web Clipperで保存されたMarkdown記事を読み取り、
内容を解析してカテゴリ別に自動整理する。

## パス設定

- **入力元**: \`/Users/{ユーザー名}/Documents/obsidian/06_Articles\`
- **整理先**: \`/Users/{ユーザー名}/Documents/articles\`

## ワークフロー

### 1. 未整理ファイルの検出

入力元フォルダ内の \`.md\` ファイルを全て取得する。
ファイルが0件なら「整理対象の記事はありません」と報告して終了。

### 2. 各ファイルの内容解析

各mdファイルを読み取り、以下を判定する:

#### カテゴリ（第1階層フォルダ）

記事の主要な技術領域を判定する。例:
- \`AWS\` - Amazon Web Services関連
- \`GCP\` - Google Cloud Platform関連
- \`Azure\` - Microsoft Azure関連
- \`Terraform\` - Terraform / IaC関連
- \`Kubernetes\` - Kubernetes / コンテナオーケストレーション関連
- その他、記事の内容に適した名前で新規作成

#### サブカテゴリ（第2階層フォルダ）

カテゴリ内の具体的なサービスや分野を判定する。例:
- AWS → \`IAM\`, \`EC2\`, \`Lambda\`, \`S3\`, \`S3Tables\` 等
- GCP → \`IAM\`, \`CloudRun\`, \`GKE\`, \`BigQuery\` 等
- Terraform → \`Basics\`, \`Modules\`, \`State\` 等

### 3. フォルダ作成とファイル移動

フォルダがなければ自動作成し、ファイルを移動する。

### 4. 処理結果レポート

整理結果をテーブル形式で表示する。
```

#### ポイント: スキルの設計

Claude Codeのskillには、以下の点を意識して設計しました：

1. **allowed-tools の制限**: `Read`, `Glob`, `Bash(mkdir *)`, `Bash(mv *)` など、必要最小限のツールのみ許可。意図しないファイル操作を防止
2. **カテゴリの柔軟性**: 定義済みカテゴリに限定せず、記事の内容に応じて新規カテゴリも作成可能に
3. **レポート出力**: 処理結果をテーブル形式で表示し、何がどこに移動されたか一目でわかるように

### ステップ3: 実行してみる

#### 記事をクリップ

ブラウザでObsidian Web Clipperの拡張アイコンをクリックすると、Obsidianが開き、Markdown形式で記事が保存されます。

いくつかの記事を保存して `06_Articles` に溜まった状態で、Claude Code上で `/clip` を実行します。

#### /clip の実行結果

```
> /clip

3件のmdファイルが見つかりました。内容を読んで分類します。

## 記事整理レポート

| ファイル名 | カテゴリ | サブカテゴリ | 移動先 |
|-----------|---------|------------|-------|
| 知識ゼロからTerraform...Tips.md | Terraform | Basics | articles/Terraform/Basics/ |
| アップデートAmazon S3 Tables...タグ機能...md | AWS | S3Tables | articles/AWS/S3Tables/ |
| Amazon S3 Tables...CloudTrail...md | AWS | S3Tables | articles/AWS/S3Tables/ |

処理件数: 3件
```

AIが記事の内容を読み取り、Terraform初心者向けの記事は `Terraform/Basics/` に、S3 Tablesのアップデート記事は `AWS/S3Tables/` に自動分類されました。

#### 生成されたフォルダ構造

```
~/Documents/articles/
├── AWS/
│   └── S3Tables/
│       ├── アップデートAmazon S3 Tablesでタグ機能が利用可能になりました...md
│       └── Amazon S3 TablesのメンテナンスイベントがCloudTrailで...md
└── Terraform/
    └── Basics/
        └── 知識ゼロからTerraformで実装するときに知っておくと便利なTips.md
```

カテゴリ・サブカテゴリのフォルダが自動作成され、記事が適切な場所に移動されています。

## launchdによる自動化に挑戦（と断念）

当初は、Web Clipperでファイルが保存された瞬間に自動で `/clip` が実行される仕組みを目指していました。

### launchdとは

macOSに標準搭載されているプロセス管理の仕組みです。 `WatchPaths` という機能で特定のフォルダを監視し、変更があったときに指定のスクリプトを実行できます。

### 構成

```
launchd（WatchPaths で 06_Articles を監視）
  ↓ ファイル変更を検知
clip-organizer.sh
  ↓ Claude Code を非対話モードで起動
claude -p "/clip を実行して"
  ↓ 記事を分類・移動
~/Documents/articles/ に自動整理
```

Claude Codeには `claude -p "プロンプト"` という非対話モードがあり、スクリプトからの呼び出しが可能です。これを活用して、launchdの `WatchPaths` → シェルスクリプト → `claude -p` という構成を組みました。

### ハマったポイント: macOSのセキュリティ制限

実装してlaunchdに登録したところ、"Operation not permitted"エラーが発生しました：  
macOSのプライバシー保護機能（TCC: Transparency, Consent, and Control）により、 **launchdが起動するバックグラウンドプロセスは `~/Documents` フォルダにアクセスできません** 。

「フルディスクアクセス」でターミナルを許可しても、launchdはターミナル経由で動作するわけではないため解決しませんでした。

### 対応策の検討と結論

| 対応策 | 評価 |
| --- | --- |
| スクリプトを.app にラップしてフルディスクアクセスを付与 | 手順が煩雑 |
| 監視対象フォルダを ~/Documents 外に移動 | Obsidian VaultがDocuments内にあるため不可 |
| **手動で /clip を実行する運用に変更** | **シンプルで確実** |

macOSのセキュリティ制限の回避方法をさらに調査すれば解決できた可能性はありますが、私自身このあたりの知見が十分ではなく、 `/clip` の手動実行自体が数秒で完了することを考えると、自動化の恩恵は小さいと判断し、シンプルな運用に落ち着きました。

## 技術的なポイント

### 1\. Claude Code skillsの活用

Claude Codeのskills（ `~/.claude/skills/` 配下にSKILL.mdを配置）を使うことで、 `/clip` というスラッシュコマンドで記事整理を呼び出せるようになります。

スキル定義のfrontmatterで `allowed-tools` を指定することで、実行時に使用できるツールを制限でき、安全に運用できます。

### 2\. AIによる柔軟な分類

従来のルールベース（ファイル名やキーワードマッチング）ではなく、AIが記事全文を読み取って分類するため：

- ファイル名に技術名が含まれていなくても正しく分類できる
- 新しいカテゴリが必要な場合も自動で判断・作成される
- S3とS3 Tablesのような細かいサブカテゴリの判別も可能

### 3\. claude -p による非対話実行

`claude -p "プロンプト"` を使うことで、Claude Codeをスクリプトから呼び出すことが可能です。今回はlaunchdとの組み合わせでmacOSのセキュリティ制限にぶつかりましたが、セキュリティ制限のない環境であれば、ファイル監視からの自動実行も実現可能です。

## まとめ

今回は、Obsidian Web ClipperとClaude Codeのカスタムスキルを組み合わせて、技術記事の自動分類の仕組みを構築しました。

完全自動化は実現できませんでしたが、 `/clip` コマンド一発で記事が整理される体験は十分快適です。技術記事の管理に悩んでいる方の参考になれば幸いです。

今後の改善としては、ObsidianのBases機能を活用してカテゴリやタグをデータベース的に管理できれば、フォルダ整理だけでなく記事の検索性や一覧性もさらに向上できそうです。

この記事をシェアする