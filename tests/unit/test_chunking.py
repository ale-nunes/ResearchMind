from researchmind.rag.chunking import chunk_pages, normalize_text


def test_normalize_text_removes_extra_whitespace() -> None:
    assert normalize_text(" a   b \n\n\n c ") == "a b \n\n c"


def test_chunk_pages_preserves_page_metadata_and_overlap() -> None:
    chunks = chunk_pages([(7, "abcdefghij")], "sample.txt", chunk_size=6, overlap=2)
    assert len(chunks) == 2
    assert chunks[0].page == 7
    assert chunks[0].text == "abcdef"
    assert chunks[1].text == "efghij"
    assert chunks[0].chunk_id != chunks[1].chunk_id


def test_chunk_pages_rejects_invalid_overlap() -> None:
    try:
        chunk_pages([(1, "hello")], "sample.txt", chunk_size=5, overlap=5)
    except ValueError as error:
        assert "overlap" in str(error)
    else:
        raise AssertionError("Expected ValueError for invalid overlap.")
