`Inbox/` 内の未整理クリップを CLAUDE.md の方針に従って整理してください。

手順：
1. `Glob` で `Inbox/*.md` を検索し、`.gitkeep` 以外のファイルを特定する
2. 対象ファイルがなければ「整理するファイルがありません」と報告して終了
3. 各ファイルを `Read` で読み込み、カテゴリを判断する
4. frontmatter に `category` と `organized_at`（今日の日付 YYYY-MM-DD）を追加・更新する
5. `Clips/<カテゴリ>/` へファイルを移動する（`Bash` で `mv` を使用）
6. `Inbox/` の元ファイルを削除する
7. 変更を `git add` してから `git commit -m "organize: <件数>件のクリップを整理"` する
8. 整理した件数・移動先を一覧で報告する
