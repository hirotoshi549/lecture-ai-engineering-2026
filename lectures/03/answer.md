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

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
