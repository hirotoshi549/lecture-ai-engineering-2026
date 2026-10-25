"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask --chat     # 会話履歴を保ったまま続けて質問する（宿題・実装）

ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
from collections.abc import Callable

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"

# 会話モードを終了する入力
EXIT_WORDS = {"", "exit", "quit", "終了"}


def format_usage(usage) -> str:
    """usage_metadata から入力・出力トークン数を1行の文字列にする。"""
    if usage is None:
        return "[tokens] 取得できませんでした"
    prompt = usage.prompt_token_count or 0
    output = usage.candidates_token_count or 0
    text = f"[tokens] 入力 {prompt} / 出力 {output}"
    thoughts = getattr(usage, "thoughts_token_count", None)
    if thoughts:
        text += f"（思考 {thoughts}）"
    return text


def ask(question: str, client: genai.Client | None = None) -> str:
    """1回だけ質問する（会話履歴なし）。"""
    client = client or genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    # 第1回 演習: 入力トークン数と出力トークン数を表示する
    print(format_usage(response.usage_metadata))

    return response.text


def chat_loop(
    client: genai.Client | None = None,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> list:
    """会話履歴を保ったまま、続けて質問する（宿題・実装）。

    client.chats.create で作ったチャットは、送ったメッセージと返答を内部に保持し、
    次の send_message で履歴ごとモデルに送る。空行か exit で終了する。
    戻り値は会話履歴（Content のリスト）。
    """
    client = client or genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    write("会話モード：続けて質問できます。空行か exit で終了します。")

    turn = 0
    while True:
        try:
            question = read(f"\n[質問{turn + 1}] ").strip()
        except EOFError:
            break
        if question.lower() in EXIT_WORDS:
            break
        try:
            response = chat.send_message(question)
        except errors.APIError as e:
            # 1回失敗しても会話は続けられるようにする（履歴は失敗した質問を含まない）
            write(api_error_message(e.code, e.message))
            continue
        turn += 1
        write(response.text)
        write(format_usage(response.usage_metadata))

    history = chat.get_history()
    write(f"\n会話を終了しました（{turn} 往復、履歴 {len(history)} 件）")
    return history


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--chat", action="store_true", help="会話履歴を保ったまま続けて質問する"
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    if args.chat:
        chat_loop()
        return

    print(f"[質問] {args.question}\n")
    try:
        print(ask(args.question))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
