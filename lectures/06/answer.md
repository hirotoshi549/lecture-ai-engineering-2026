# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview'})
- 気づき・疑問：
  - STEP 1 で `app.agent --list-tools` と `app.mcp_agent --list-tools` を比べると、どちらも名前・説明文・引数の形でモデルに渡っていた。関数を直接登録しても MCP サーバー経由でも、モデルから見える形は同じで、違うのは「誰が関数を実行するか」だけだと分かった
  - STEP 4 で `aws` を足すと、ツールが 2 個から 7 個に増えた（read_documentation・search_documentation・list_regions・get_regional_availability・retrieve_skill）。設定ファイルに 1 行足すだけで、他人が作ったツールが 5 個もモデルに見えるようになる。便利な反面、講義の「ツールが多いと最初のコンテキストが増える」話のとおり、使わないツールの説明文も毎回入力に入る。入力トークンは STEP 2 の 709 に対し、STEP 4 は 6,347 だった（検索結果の分も含む）
  - ツール名は「サーバー名_ツール名」になるので、AWS のツールは `aws_aws___search_documentation` と `aws` が重なった。サーバー側がもともと `aws___` という接頭辞を付けているためで、設定ファイルのサーバー名を短くしても重複は残る
  - STEP 3 の回答の末尾に「（関連する回：第N回）」と、番号の入らないまま出た。指示文の「関連する回を書く」に、講座と関係のない質問でも従おうとした結果だと思う。第4回の「回の表示」の基準と同じで、範囲外の質問のときにどう書くかを決めておく必要がある
  - 実行した環境について：Codespaces ではなく、ネットワークの許可先が限られたクラウドの作業環境で実行した。そのため、STEP 3・4 の前に `modelcontextprotocol.io` と `knowledge-mcp.global.api.aws` への接続を許可した。また、MCP がコマンドで起動するサーバーには、環境変数のうち一部（PATH や HOME など）しか渡らず、この環境で外部につなぐための中継（プロキシ）の設定が fetch サーバーに届かなかった。STEP 3 の実行時だけ、設定ファイルの `env` で中継の設定を渡して確かめた（提出した `app/mcp_servers.json` には入れていない）。コマンドで起動するサーバーは「親と同じ環境で動く」とは限らない、と分かった

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
