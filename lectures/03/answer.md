# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  - 第1回の `app.ask` は「lecNN タグ」を「講義回を識別する管理用タグ（教材の整理や Slack チャンネル名など）」と自信を持って答えていて、用途がまったく違っていた
  - エージェント（`app.agent`）は先に `search_glossary` で用語集を引き、「各回の演習開始時点のコードに付けた Git タグ（例：`lec03-start`）で、前の回が終わっていなくてもこのタグからブランチを作れば始められる」と、用語集の定義どおりに答えた。最後に「第1回」と関係する回も書いた
  - 素の LLM は講座固有のことを一般論から作ってしまうが、エージェントはツールで根拠を取ってから答えるので正しくなった
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  - 「lecNN-start タグとは？」→ `search_glossary({'query': 'lecNN-start タグ'})` を 1 回
  - 「LoRAとQLoRAの違いは？」→ `search_glossary({'query': 'LoRA'})` と `search_glossary({'query': 'QLoRA'})`。docstring の「query には調べたい用語を1つだけ入れる」に従って 2 回に分けて呼んでいた
  - 「第2回の内容から確認問題を1問出して」→ `make_quiz({'lecture': 2})` を 1 回
  - 実行ログ：`lectures/03/homework/pydantic_q1.txt`・`pydantic_q2.txt`、`lectures/03/exercise/make_quiz_trace.txt`
- 1つの質問での LLM 呼び出し回数（`requests`）：上の 3 問ともすべて 2 回（1 回目でツール呼び出しを決め、2 回目でツールの結果を見て回答を作る）。LoRA/QLoRA は 2 つの検索を 1 回目の応答でまとめて依頼していたので、ツール呼び出しは 2 回でも `requests` は 2 だった
- 追加したツールと、docstring に書いた説明：
  - `make_quiz(lecture: int)`：指定した回の用語から 1 つをランダムに選び、`{"lecture", "term", "question", "answer"}` の JSON を返す（問題は「『用語』とはどういう意味ですか？」、答えは用語集の定義）。用語のない回を指定したら、用語がある回の一覧を返す
  - docstring には「利用者が理解を確かめる問題を求めたときに使う」「用語の意味の説明を求められたときは search_glossary を使い、このツールは使わない」「answer は利用者が解答してから見せる（問題と同時に答えを出さない）」と書いた
  - 実行すると第2回から「PEFT」が選ばれ、エージェントは答えを伏せて問題だけを出し、「答えを考えたら教えてください」と返した。docstring の「答えを同時に出さない」が守られていた（1 回の実行で確認）
  - テスト：`tests/test_tools.py` に make_quiz の 2 件、`tests/test_agent.py` に登録と結果がモデルに戻ることの 1 件を追加。`uv run pytest -q` で 18 件すべて成功（手元と Codespaces の両方）
  - 宿題の ADK 版（`adk_agent/glossary_agent/agent.py`）の `tools` にも make_quiz を加えた（宿題の比較の実行は make_quiz 追加前に行った）

## 宿題

- 取り組んだレベル：発展（a）Google ADK で作り直す
- やったこと：
  - `adk_agent/glossary_agent/agent.py` と `__init__.py` を作り、演習と同じ `INSTRUCTIONS`（`app.agent` から import）とツール（`search_glossary`・`get_lecture_summary`）で ADK の `Agent` を組み立てた。`app/` のファイルは変えていない
  - Codespaces（lec03 ブランチ、google-adk 2.14.0）で、演習の `app.agent --trace` と `adk run` に同じ 3 問を投げた。ADK 側は `--jsonl` を付けてツール呼び出しもイベントとして記録した
  - 実行ログ：`lectures/03/homework/pydantic_q{1,2,3}.txt`、`lectures/03/homework/adk_q{1,2,3}.jsonl`
- 結果：

  **書き方の比較**

  | 項目 | 演習（Pydantic AI） | ADK |
  |---|---|---|
  | 指示 | `Agent(instructions=INSTRUCTIONS)` | `Agent(instruction=INSTRUCTIONS)`（単数形） |
  | ツール | `agent.tool_plain(tools.search_glossary)` を 1 つずつ登録 | `tools=[tools.search_glossary, ...]` に関数を並べる |
  | ツールの説明 | docstring と型ヒントから作られる | 同じ（docstring がそのまま description、型ヒントが引数スキーマ） |
  | モデル | 実行時に `run_sync(..., model=...)` で渡す（テストで TestModel に差し替えるため） | 組み立て時に `model=` で固定 |
  | 名前 | 不要 | `name` が必須。`description` も書ける |
  | API キー | `get_api_key()` で読み、`GoogleProvider(api_key=...)` に渡す | コードには書かない。環境変数 `GEMINI_API_KEY` を google-genai が自動で読んだ |
  | 動かし方 | `python -m app.agent` を自分で書いた CLI で実行 | `root_agent` という変数名の規約に従えば、`adk run` / `adk web` が CLI・UI を用意してくれる |
  | ツール呼び出しの見え方 | 自作の `--trace` で `[tool call]` / `[tool return]` を表示 | `adk run` の通常表示には出ない。`--jsonl` を付けると `functionCall` / `functionResponse` のイベントとして出る |

  **同じ質問への結果**（各 1 回ずつの実行）

  | 質問 | ツール呼び出し（両方同じ） | LLM 呼び出し回数 | 入力 / 出力トークン（Pydantic AI → ADK） |
  |---|---|---|---|
  | Q1 AIE2026の講座で使う「lecNN-start タグ」とは何ですか？ | `search_glossary(query="lecNN-start タグ")` | 2 / 2 | 783 / 104 → 943 / 109 |
  | Q2 LoRAとQLoRAの違いは？ | `search_glossary("LoRA")` と `search_glossary("QLoRA")` を 1 回の応答で並列に | 2 / 2 | 1196 / 192 → 1354 / 177 |
  | Q3 第3回では何を学ぶ？ | `get_lecture_summary(lecture=3)` | 2 / 2 | 1107 / 232 → 1267 / 198 |

  - ADK の回数とトークンは、jsonl の中で `usageMetadata` を持つモデル応答（2 件）を数えて足した値
  - 回答の中身はほぼ同じだった。どちらも用語集の定義に沿って説明し、最後に関係する回を書いた（Q1 は演習側が「第1回」、ADK 側が「関係する回：第1回」と書式だけ違った）
  - Q3 は、演習側が要点の 3（Pydantic AI / TestModel）と 4（コスト・Human-in-the-loop）を拾い、ADK 側は「Pydantic AI や ADK を使う」と安全性を拾った。同じ要点の文から選んだ項目が少し違う
- 気づき・疑問：
  - 指示とツールの関数がフレームワークから独立して書かれていたので、組み立て部分の 10 行ほどを書き換えるだけで移せた。docstring がツールの説明になる仕組みは両方同じで、ツール選択と引数も 3 問とも一致した
  - 入力トークンは 3 問とも ADK のほうが約 160 多かった。ADK のソース（`flows/llm_flows/prompt/_identity.py`）を見ると、`You are an agent. Your internal name is "..."` と `description` をシステム指示に自動で足している。これが差の一因だと考えているが、ツール定義の渡し方の違いなど他の要因は切り分けていない（未確認）
  - 演習側はモデルを実行時に渡す設計なので TestModel でテストできる。ADK は `model=` で固定するので、API を呼ばないテストをどう書くのかが疑問（ADK の評価機能 `adk eval` との関係も未確認）
  - 回答の差（Q3 で拾う項目、書式）は各 1 回の実行なので、フレームワークの違いなのか、同じ条件でも毎回変わる揺らぎなのかは区別できない。比べるなら同じ質問を複数回投げる必要がある
  - `adk web` での見え方は今回は試していない
