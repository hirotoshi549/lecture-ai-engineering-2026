"""第3回: エージェントに持たせるツール。

ここに書いた関数の docstring と型ヒントが、そのままモデルへの「ツールの説明文」になる。
説明文を書き換えると、モデルがツールを使うかどうか・どんな引数で呼ぶかが変わる。
"""

import json
import random
from functools import cache
from pathlib import Path

from app.config import api_error_message

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MAX_RESULTS = 3


@cache
def load_glossary() -> list[dict]:
    with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
        return json.load(f)["terms"]


def _normalize(text: str) -> str:
    return text.casefold().replace(" ", "").replace("　", "")


def _names(entry: dict) -> list[str]:
    return [_normalize(entry["term"]), _normalize(entry["id"])] + [
        _normalize(a) for a in entry["aliases"]
    ]


def search_glossary(query: str) -> str:
    """講座の用語集から用語を検索し、定義と、どの回で扱うかを返す。

    AIエンジニアリングの用語や、この講座（AIE2026）に固有の言葉について
    答える前に使うこと。query には調べたい用語を1つだけ入れる（例: "LoRA"）。
    """
    q = _normalize(query)
    if not q:
        return "検索語が空です。調べたい用語を1つ指定してください。"
    glossary = load_glossary()

    exact = [e for e in glossary if q in _names(e)]
    # 「r」のような短い別名が何にでも当たらないよう、名前側が短いものは除く
    partial = [
        e for e in glossary
        if e not in exact and any(q in n or (len(n) >= 3 and n in q) for n in _names(e))
    ]
    in_definition = [
        e for e in glossary
        if e not in exact and e not in partial and q in _normalize(e["definition"])
    ]
    hits = (exact + partial + in_definition)[:MAX_RESULTS]

    if not hits:
        return f"用語集に「{query}」は見つかりませんでした。"
    return json.dumps(
        [
            {
                "term": e["term"],
                "lecture": e["lecture"],
                "definition": e["definition"],
                "related": e["related"],
            }
            for e in hits
        ],
        ensure_ascii=False,
    )


def get_lecture_summary(lecture: int) -> str:
    """指定した回（1始まりの整数）の講義の要点を返す。

    「第3回では何を学ぶ？」のように、回の内容や関係を聞かれたときに使う。
    """
    path = DATA_DIR / "lectures" / f"{lecture:02d}.md"
    if not path.exists():
        available = sorted(p.stem for p in (DATA_DIR / "lectures").glob("*.md"))
        return f"第{lecture}回の要点はまだありません。用意されている回: {', '.join(available)}"
    return path.read_text(encoding="utf-8")


def make_quiz(lecture: int) -> str:
    """指定した回（1始まりの整数）の用語から1つを選び、確認問題とその答えを返す。

    「第2回の内容から確認問題を出して」「LoRAの回の復習クイズがほしい」のように、
    利用者が理解を確かめる問題を求めたときに使う。用語の意味の説明を求められたときは
    search_glossary を使い、このツールは使わない。
    返り値の answer は、利用者が解答してから見せる（問題と同時に答えを出さない）。
    指定された回が講座にあるか分からないとき（例: 第99回）も、自分で判断せずにこのツールを呼ぶ。
    問題を作れる回は、このツールが返す。
    """
    available = sorted({e["lecture"] for e in load_glossary()})
    choices = "、".join(f"第{n}回" for n in available)
    # 第6回 宿題（実装）: 範囲外のときは、何が問題か・どう直すか・利用者に何を伝えるかを返す
    if lecture < 1:
        return (f"引数の誤り：lecture は 1 以上の整数で指定してください（入力値は {lecture}）。"
                f"確認問題を作れる回は {choices} です。")
    candidates = [e for e in load_glossary() if e["lecture"] == lecture]
    if not candidates:
        reason = (f"第{lecture}回は、用語集にある最後の回（第{available[-1]}回）より後です。"
                  if lecture > available[-1] else f"第{lecture}回の用語は、まだ用語集に登録されていません。")
        return (f"第{lecture}回の用語は用語集にありません。{reason}"
                f"確認問題を作れる回は {choices} です。lecture にはこのどれかを指定して呼び直してください。"
                f"利用者には、第{lecture}回の問題は作れないことと、選べる回を伝え、どの回にするか尋ねてください。"
                "用語集にない内容で問題を作らないでください。")
    entry = random.choice(candidates)
    return json.dumps(
        {
            "lecture": lecture,
            "term": entry["term"],
            "question": f"「{entry['term']}」とはどういう意味ですか？",
            "answer": entry["definition"],
        },
        ensure_ascii=False,
    )


def search_materials(query: str) -> str:
    """第1〜3回の本講義資料を検索し、関連ページの本文・タイトル・ページ番号を返す。

    queryに調べたい内容を指定する。
    """
    from google.genai.errors import APIError
    import sqlite3
    from app.config import RAG_NEIGHBOR_PAGES
    from app.retrieval import add_neighbors, search

    try:
        # 第5回 宿題（実装）: AIE_RAG_NEIGHBORS を付けたときだけ、前後のページの本文も付ける
        return json.dumps({"results": add_neighbors(search(query), RAG_NEIGHBOR_PAGES)}, ensure_ascii=False)
    except (ValueError, FileNotFoundError, sqlite3.Error) as e:
        return json.dumps({"error": str(e), "results": []}, ensure_ascii=False)
    except APIError as e:
        return json.dumps({"error": api_error_message(e.code), "results": []}, ensure_ascii=False)


def browse_tree(node_id: str | None = None) -> str:
    """目次とページの先頭文を返す。ページIDを指定すると全文を返す。

    最初はnode_idを省略する。続いて返されたIDを指定して目次をたどる。
    """
    from app.retrieval import browse_tree as browse

    try:
        return json.dumps(browse(node_id), ensure_ascii=False)
    except (ValueError, OSError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def search_graph(query: str) -> str:
    """資料を検索し、前後ページ・共通用語をたどって関連ページの本文と引用情報を返す。

    queryに調べたい内容を指定する。
    """
    import sqlite3
    from google.genai.errors import APIError
    from app.retrieval import search_graph as search

    try:
        return json.dumps(search(query), ensure_ascii=False)
    except (ValueError, OSError, sqlite3.Error) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    except APIError as e:
        return json.dumps({"error": api_error_message(e.code)}, ensure_ascii=False)
