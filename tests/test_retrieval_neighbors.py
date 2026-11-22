"""第5回 宿題（実装）: 検索結果に前後のページを付ける処理（add_neighbors）のテスト。API は呼ばない。"""

from app.retrieval import add_neighbors, load_pages

PAGES = load_pages()
BY_ID = {page["page_id"]: page for page in PAGES}


def _hit(page_id):
    return dict(BY_ID[page_id])


def _first_page_of(document_id):
    return next(page["page_id"] for page in PAGES if page["document_id"] == document_id)


def test_window_zero_returns_hits_unchanged():
    hits = [_hit("lec02-main-p052")]
    assert add_neighbors(hits, 0) == hits


def test_adds_previous_and_next_page_of_same_document():
    result = add_neighbors([_hit("lec02-main-p052")], 1)
    neighbors = result[0]["neighbors"]
    assert [(n["relation"], n["page_id"]) for n in neighbors] == [
        ("前のページ", "lec02-main-p051"),
        ("次のページ", "lec02-main-p053"),
    ]
    assert neighbors[0]["content"] == BY_ID["lec02-main-p051"]["content"]


def test_does_not_cross_documents():
    first = _first_page_of("lec02-main")
    neighbors = add_neighbors([_hit(first)], 1)[0]["neighbors"]
    assert all(n["page_id"].startswith("lec02-main") for n in neighbors)
    assert [n["relation"] for n in neighbors] == ["次のページ"]


def test_does_not_duplicate_pages():
    # p.51 と p.52 が両方ヒットした場合、互いを前後ページとして付けず、p.50 と p.53 だけを付ける
    result = add_neighbors([_hit("lec02-main-p052"), _hit("lec02-main-p051")], 1)
    attached = [n["page_id"] for r in result for n in r["neighbors"]]
    assert sorted(attached) == ["lec02-main-p050", "lec02-main-p053"]
    assert len(attached) == len(set(attached))
