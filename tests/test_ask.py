"""第1回 ask.py のテスト（APIキー不要。偽のクライアントで動かす）。"""

from types import SimpleNamespace

from app.ask import ask, chat_loop, format_usage


def _usage(prompt, output, thoughts=None):
    return SimpleNamespace(
        prompt_token_count=prompt,
        candidates_token_count=output,
        thoughts_token_count=thoughts,
    )


class FakeChat:
    """送られた質問を履歴に積み、履歴の長さに応じて入力トークンが増える偽のチャット。"""

    def __init__(self):
        self.history = []

    def send_message(self, message):
        self.history.append(("user", message))
        reply = f"答え{len(self.history) // 2 + 1}"
        self.history.append(("model", reply))
        return SimpleNamespace(text=reply, usage_metadata=_usage(10 * len(self.history), 3))

    def get_history(self):
        return list(self.history)


class FakeClient:
    def __init__(self):
        self.chat = FakeChat()
        self.chats = SimpleNamespace(create=lambda model: self.chat)
        self.models = SimpleNamespace(
            generate_content=lambda model, contents: SimpleNamespace(
                text="単発の答え", usage_metadata=_usage(5, 7)
            )
        )


def test_format_usage():
    assert format_usage(_usage(12, 34)) == "[tokens] 入力 12 / 出力 34"
    assert format_usage(_usage(12, 34, 5)) == "[tokens] 入力 12 / 出力 34（思考 5）"
    assert "取得できません" in format_usage(None)


def test_ask_prints_tokens(capsys):
    assert ask("LoRAとは？", client=FakeClient()) == "単発の答え"
    assert "[tokens] 入力 5 / 出力 7" in capsys.readouterr().out


def test_chat_loop_keeps_history():
    inputs = iter(["LoRAとは？", "それをもっと短く", "exit"])
    out = []
    client = FakeClient()
    history = chat_loop(client=client, read=lambda _: next(inputs), write=out.append)

    # 2往復分（質問と返答で4件）の履歴が同じチャットに残る
    assert len(history) == 4
    assert history[2] == ("user", "それをもっと短く")
    assert any("2 往復" in line for line in out)


def test_chat_loop_ends_on_eof():
    def read(_):
        raise EOFError

    assert chat_loop(client=FakeClient(), read=read, write=lambda _: None) == []
