from app.records import (
    count_by,
    get_by_id,
    load_records,
    search,
)


def test_load_records_returns_list():
    records = load_records()

    assert isinstance(records, list)
    assert len(records) > 0


def test_records_have_required_fields():
    records = load_records()

    required_fields = {
        "page_title",
        "guide_section",
        "key_concept",
        "main_symbol",
        "example_response",
        "source_url",
    }

    for record in records:
        assert required_fields.issubset(record.keys())


def test_search_finds_existing_record():
    records = load_records()
    keyword = records[0]["page_title"].split()[0]

    results = search(keyword)

    assert len(results) > 0


def test_search_returns_empty_for_unknown_keyword():
    results = search("zzzz_no_matching_fastapi_page_12345")

    assert results == []


def test_count_by_guide_section():
    counts = count_by("guide_section")

    assert isinstance(counts, dict)
    assert len(counts) > 0
    assert sum(counts.values()) == len(load_records())


def test_get_by_id_returns_existing_record():
    record = get_by_id(1)

    assert record is not None
    assert "page_title" in record
    assert "guide_section" in record

def test_get_by_id_returns_none_for_invalid_id():
    assert get_by_id(999999) is None

