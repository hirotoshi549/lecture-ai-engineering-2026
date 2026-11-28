"""ツールのテスト（LLMもAPIキーも使わない）。"""

import json

from app import tools


def test_glossary_ids_are_unique_and_related_links_exist():
    terms = tools.load_glossary()
    ids = [t["id"] for t in terms]
    assert len(ids) == len(set(ids))
    for t in terms:
        for r in t["related"]:
            assert r in ids, f"{t['id']} の related に存在しない id: {r}"


def test_search_finds_term_by_name_and_alias():
    for query in ["LoRA", "lora", "Low-Rank Adaptation"]:
        hits = json.loads(tools.search_glossary(query))
        assert hits[0]["term"] == "LoRA", query


def test_search_finds_course_specific_term():
    hits = json.loads(tools.search_glossary("lecNN-start"))
    assert hits[0]["term"] == "lecNN-start タグ"


def test_search_limits_number_of_results():
    hits = json.loads(tools.search_glossary("エージェント"))
    assert 1 <= len(hits) <= tools.MAX_RESULTS


def test_search_reports_not_found():
    assert "見つかりませんでした" in tools.search_glossary("存在しない用語xyz")


def test_lecture_summary():
    assert "エージェント" in tools.get_lecture_summary(3)
    assert "まだありません" in tools.get_lecture_summary(99)


def test_default_question_of_lecture1_is_answerable_from_glossary():
    """第1回の既定の質問（app.ask）は、第3回のエージェントが用語集で正しく答えられること。"""
    from app.ask import DEFAULT_QUESTION

    assert "3レベル" in DEFAULT_QUESTION
    hits = json.loads(tools.search_glossary("3レベル"))
    assert hits[0]["term"] == "宿題の3レベル"


def test_make_quiz_picks_a_term_of_the_lecture():
    quiz = json.loads(tools.make_quiz(2))
    assert quiz["lecture"] == 2
    lecture2_terms = {t["term"]: t for t in tools.load_glossary() if t["lecture"] == 2}
    assert quiz["term"] in lecture2_terms
    assert quiz["term"] in quiz["question"]
    assert quiz["answer"] == lecture2_terms[quiz["term"]]["definition"]


def test_make_quiz_reports_lecture_without_terms():
    assert "用語集にありません" in tools.make_quiz(99)


# 第6回 宿題（実装）: 範囲外の回では、何が問題か・選べる回・利用者に伝えることを返す
def test_make_quiz_out_of_range_explains_how_to_fix():
    message = tools.make_quiz(99)
    assert "第6回）より後" in message
    assert "第1回、第2回、第3回、第4回、第6回" in message
    assert "利用者には" in message


def test_make_quiz_lecture_without_terms_yet():
    assert "まだ用語集に登録されていません" in tools.make_quiz(5)


def test_make_quiz_rejects_non_positive_lecture():
    assert tools.make_quiz(0).startswith("引数の誤り：lecture は 1 以上の整数")


def test_mcp_server_exposes_make_quiz():
    import asyncio
    from app.mcp_server import server

    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert {"search_glossary", "make_quiz"} <= names
