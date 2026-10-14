"""Test Knowledge creation and querying functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage


@pytest.fixture(autouse=True)
def mock_vector_db():
    """Mock vector database operations."""
    with patch("crewai.knowledge.storage.knowledge_storage.KnowledgeStorage") as mock:
        instance = mock.return_value
        instance.query.return_value = [
            {
                "content": "Brandon's favorite color is blue and he likes Mexican food.",
                "score": 0.9,
            }
        ]
        instance.reset.return_value = None
        yield instance


@pytest.fixture(autouse=True)
def reset_knowledge_storage(mock_vector_db):
    """Fixture to reset knowledge storage before each test."""
    yield


def _saved_chunks(source):
    storage = MagicMock(spec=KnowledgeStorage)
    source.storage = storage
    source.add()
    storage.save.assert_called_once()
    return storage.save.call_args.args[0]


def test_single_short_string():
    content = "Brandon's favorite color is blue and he likes Mexican food."
    string_source = StringKnowledgeSource(
        content=content, metadata={"preference": "personal"}
    )

    assert _saved_chunks(string_source) == [
        "Brandon's favorite color is blue and he likes Mexican food."
    ]


# @pytest.mark.vcr()
def test_single_2k_character_string():
    content = (
        "Brandon is a software engineer who lives in San Francisco. "
        "He enjoys hiking and often visits the trails in the Bay Area. "
        "Brandon has a pet dog named Max, who is a golden retriever. "
        "He loves reading science fiction books, and his favorite author is Isaac Asimov. "
        "Brandon's favorite movie is Inception, and he enjoys watching it with his friends. "
        "He is also a fan of Mexican cuisine, especially tacos and burritos. "
        "Brandon plays the guitar and often performs at local open mic nights. "
        "He is learning French and plans to visit Paris next year. "
        "Brandon is passionate about technology and often attends tech meetups in the city. "
        "He is also interested in AI and machine learning, and he is currently working on a project related to natural language processing. "
        "Brandon's favorite color is blue, and he often wears blue shirts. "
        "He enjoys cooking and often tries new recipes on weekends. "
        "Brandon is a morning person and likes to start his day with a run in the park. "
        "He is also a coffee enthusiast and enjoys trying different coffee blends. "
        "Brandon is a member of a local book club and enjoys discussing books with fellow members. "
        "He is also a fan of board games and often hosts game nights at his place. "
        "Brandon is an advocate for environmental conservation and volunteers for local clean-up drives. "
        "He is also a mentor for aspiring software developers and enjoys sharing his knowledge with others. "
        "Brandon's favorite sport is basketball, and he often plays with his friends on weekends. "
        "He is also a fan of the Golden State Warriors and enjoys watching their games. "
    )
    string_source = StringKnowledgeSource(
        content=content, metadata={"preference": "personal"}
    )

    assert _saved_chunks(string_source) == [content]


def test_multiple_short_strings():
    contents = [
        "Brandon loves hiking.",
        "Brandon has a dog named Max.",
        "Brandon enjoys painting landscapes.",
    ]
    string_sources = [
        StringKnowledgeSource(content=content, metadata={"preference": "personal"})
        for content in contents
    ]

    assert [_saved_chunks(source) for source in string_sources] == [
        ["Brandon loves hiking."],
        ["Brandon has a dog named Max."],
        ["Brandon enjoys painting landscapes."],
    ]


def test_multiple_2k_character_strings():
    contents = [
        (
            "Brandon is a software engineer who lives in San Francisco. "
            "He enjoys hiking and often visits the trails in the Bay Area. "
            "Brandon has a pet dog named Max, who is a golden retriever. "
            "He loves reading science fiction books, and his favorite author is Isaac Asimov. "
            "Brandon's favorite movie is Inception, and he enjoys watching it with his friends. "
            "He is also a fan of Mexican cuisine, especially tacos and burritos. "
            "Brandon plays the guitar and often performs at local open mic nights. "
            "He is learning French and plans to visit Paris next year. "
            "Brandon is passionate about technology and often attends tech meetups in the city. "
            "He is also interested in AI and machine learning, and he is currently working on a project related to natural language processing. "
            "Brandon's favorite color is blue, and he often wears blue shirts. "
            "He enjoys cooking and often tries new recipes on weekends. "
            "Brandon is a morning person and likes to start his day with a run in the park. "
            "He is also a coffee enthusiast and enjoys trying different coffee blends. "
            "Brandon is a member of a local book club and enjoys discussing books with fellow members. "
            "He is also a fan of board games and often hosts game nights at his place. "
            "Brandon is an advocate for environmental conservation and volunteers for local clean-up drives. "
            "He is also a mentor for aspiring software developers and enjoys sharing his knowledge with others. "
            "Brandon's favorite sport is basketball, and he often plays with his friends on weekends. "
            "He is also a fan of the Golden State Warriors and enjoys watching their games. "
        )
        * 2,  # Repeat to ensure it's 2k characters
        (
            "Brandon loves traveling and has visited over 20 countries. "
            "He is fluent in Spanish and often practices with his friends. "
            "Brandon's favorite city is Barcelona, where he enjoys the architecture and culture. "
            "He is a foodie and loves trying new cuisines, with a particular fondness for sushi. "
            "Brandon is an avid cyclist and participates in local cycling events. "
            "He is also a photographer and enjoys capturing landscapes and cityscapes. "
            "Brandon is a tech enthusiast and follows the latest trends in gadgets and software. "
            "He is also a fan of virtual reality and owns a VR headset. "
            "Brandon's favorite book is 'The Hitchhiker's Guide to the Galaxy'. "
            "He enjoys watching documentaries and learning about history and science. "
            "Brandon is a coffee lover and has a collection of coffee mugs from different countries. "
            "He is also a fan of jazz music and often attends live performances. "
            "Brandon is a member of a local running club and participates in marathons. "
            "He is also a volunteer at a local animal shelter and helps with dog walking. "
            "Brandon's favorite holiday is Christmas, and he enjoys decorating his home. "
            "He is also a fan of classic movies and has a collection of DVDs. "
            "Brandon is a mentor for young professionals and enjoys giving career advice. "
            "He is also a fan of puzzles and enjoys solving them in his free time. "
            "Brandon's favorite sport is soccer, and he often plays with his friends. "
            "He is also a fan of FC Barcelona and enjoys watching their matches. "
        )
        * 2,  # Repeat to ensure it's 2k characters
    ]
    string_sources = [
        StringKnowledgeSource(content=content, metadata={"preference": "personal"})
        for content in contents
    ]

    assert [_saved_chunks(source) for source in string_sources] == [
        [contents[0]],
        [contents[1]],
    ]


def test_single_short_file(tmpdir):
    content = "Brandon's favorite sport is basketball."
    file_path = Path(tmpdir.join("short_file.txt"))
    with open(file_path, "w") as f:
        f.write(content)

    file_source = TextFileKnowledgeSource(
        file_paths=[file_path], metadata={"preference": "personal"}
    )

    assert file_source.content == {
        file_path: "Brandon's favorite sport is basketball."
    }
    assert _saved_chunks(file_source) == ["Brandon's favorite sport is basketball."]


def test_single_2k_character_file(tmpdir):
    content = (
        "Brandon is a software engineer who lives in San Francisco. "
        "He enjoys hiking and often visits the trails in the Bay Area. "
        "Brandon has a pet dog named Max, who is a golden retriever. "
        "He loves reading science fiction books, and his favorite author is Isaac Asimov. "
        "Brandon's favorite movie is Inception, and he enjoys watching it with his friends. "
        "He is also a fan of Mexican cuisine, especially tacos and burritos. "
        "Brandon plays the guitar and often performs at local open mic nights. "
        "He is learning French and plans to visit Paris next year. "
        "Brandon is passionate about technology and often attends tech meetups in the city. "
        "He is also interested in AI and machine learning, and he is currently working on a project related to natural language processing. "
        "Brandon's favorite color is blue, and he often wears blue shirts. "
        "He enjoys cooking and often tries new recipes on weekends. "
        "Brandon is a morning person and likes to start his day with a run in the park. "
        "He is also a coffee enthusiast and enjoys trying different coffee blends. "
        "Brandon is a member of a local book club and enjoys discussing books with fellow members. "
        "He is also a fan of board games and often hosts game nights at his place. "
        "Brandon is an advocate for environmental conservation and volunteers for local clean-up drives. "
        "He is also a mentor for aspiring software developers and enjoys sharing his knowledge with others. "
        "Brandon's favorite sport is basketball, and he often plays with his friends on weekends. "
        "He is also a fan of the Golden State Warriors and enjoys watching their games. "
    ) * 2  # Repeat to ensure it's 2k characters
    file_path = Path(tmpdir.join("long_file.txt"))
    with open(file_path, "w") as f:
        f.write(content)

    file_source = TextFileKnowledgeSource(
        file_paths=[file_path], metadata={"preference": "personal"}
    )

    assert _saved_chunks(file_source) == [content]


def test_multiple_short_files(tmpdir):
    contents = [
        {
            "content": "Brandon works as a software engineer.",
            "metadata": {"category": "profession", "source": "occupation"},
        },
        {
            "content": "Brandon lives in New York.",
            "metadata": {"category": "city", "source": "personal"},
        },
        {
            "content": "Brandon enjoys cooking Italian food.",
            "metadata": {"category": "hobby", "source": "personal"},
        },
    ]
    file_paths = []
    for i, item in enumerate(contents):
        file_path = Path(tmpdir.join(f"file_{i}.txt"))
        with open(file_path, "w") as f:
            f.write(item["content"])
        file_paths.append((file_path, item["metadata"]))

    file_sources = [
        TextFileKnowledgeSource(file_paths=[path], metadata=metadata)
        for path, metadata in file_paths
    ]

    assert [_saved_chunks(source) for source in file_sources] == [
        ["Brandon works as a software engineer."],
        ["Brandon lives in New York."],
        ["Brandon enjoys cooking Italian food."],
    ]


def test_multiple_2k_character_files(tmpdir):
    contents = [
        (
            "Brandon loves traveling and has visited over 20 countries. "
            "He is fluent in Spanish and often practices with his friends. "
            "Brandon's favorite city is Barcelona, where he enjoys the architecture and culture. "
            "He is a foodie and loves trying new cuisines, with a particular fondness for sushi. "
            "Brandon is an avid cyclist and participates in local cycling events. "
            "He is also a photographer and enjoys capturing landscapes and cityscapes. "
            "Brandon is a tech enthusiast and follows the latest trends in gadgets and software. "
            "He is also a fan of virtual reality and owns a VR headset. "
            "Brandon's favorite book is 'The Hitchhiker's Guide to the Galaxy'. "
            "He enjoys watching documentaries and learning about history and science. "
            "Brandon is a coffee lover and has a collection of coffee mugs from different countries. "
            "He is also a fan of jazz music and often attends live performances. "
            "Brandon is a member of a local running club and participates in marathons. "
            "He is also a volunteer at a local animal shelter and helps with dog walking. "
            "Brandon's favorite holiday is Christmas, and he enjoys decorating his home. "
            "He is also a fan of classic movies and has a collection of DVDs. "
            "Brandon is a mentor for young professionals and enjoys giving career advice. "
            "He is also a fan of puzzles and enjoys solving them in his free time. "
            "Brandon's favorite sport is soccer, and he often plays with his friends. "
            "He is also a fan of FC Barcelona and enjoys watching their matches. "
        )
        * 2,  # Repeat to ensure it's 2k characters
        (
            "Brandon is a software engineer who lives in San Francisco. "
            "He enjoys hiking and often visits the trails in the Bay Area. "
            "Brandon has a pet dog named Max, who is a golden retriever. "
            "He loves reading science fiction books, and his favorite author is Isaac Asimov. "
            "Brandon's favorite movie is Inception, and he enjoys watching it with his friends. "
            "He is also a fan of Mexican cuisine, especially tacos and burritos. "
            "Brandon plays the guitar and often performs at local open mic nights. "
            "He is learning French and plans to visit Paris next year. "
            "Brandon is passionate about technology and often attends tech meetups in the city. "
            "He is also interested in AI and machine learning, and he is currently working on a project related to natural language processing. "
            "Brandon's favorite color is blue, and he often wears blue shirts. "
            "He enjoys cooking and often tries new recipes on weekends. "
            "Brandon is a morning person and likes to start his day with a run in the park. "
            "He is also a coffee enthusiast and enjoys trying different coffee blends. "
            "Brandon is a member of a local book club and enjoys discussing books with fellow members. "
            "He is also a fan of board games and often hosts game nights at his place. "
            "Brandon is an advocate for environmental conservation and volunteers for local clean-up drives. "
            "He is also a mentor for aspiring software developers and enjoys sharing his knowledge with others. "
            "Brandon's favorite sport is basketball, and he often plays with his friends on weekends. "
            "He is also a fan of the Golden State Warriors and enjoys watching their games. "
        )
        * 2,  # Repeat to ensure it's 2k characters
    ]
    file_paths = []
    for i, content in enumerate(contents):
        file_path = Path(tmpdir.join(f"long_file_{i}.txt"))
        with open(file_path, "w") as f:
            f.write(content)
        file_paths.append(file_path)

    file_sources = [
        TextFileKnowledgeSource(file_paths=[path], metadata={"preference": "personal"})
        for path in file_paths
    ]

    assert [_saved_chunks(source) for source in file_sources] == [
        [contents[0]],
        [contents[1]],
    ]


@pytest.mark.vcr()
def test_hybrid_string_and_files(tmpdir):
    string_contents = [
        "Brandon is learning French.",
        "Brandon visited Paris last summer.",
    ]
    string_sources = [
        StringKnowledgeSource(content=content, metadata={"preference": "personal"})
        for content in string_contents
    ]

    file_contents = [
        "Brandon prefers tea over coffee.",
        "Brandon's favorite book is 'The Alchemist'.",
    ]
    file_paths = []
    for i, content in enumerate(file_contents):
        file_path = Path(tmpdir.join(f"file_{i}.txt"))
        with open(file_path, "w") as f:
            f.write(content)
        file_paths.append(file_path)

    file_sources = [
        TextFileKnowledgeSource(file_paths=[path], metadata={"preference": "personal"})
        for path in file_paths
    ]

    assert [_saved_chunks(source) for source in string_sources + file_sources] == [
        ["Brandon is learning French."],
        ["Brandon visited Paris last summer."],
        ["Brandon prefers tea over coffee."],
        ["Brandon's favorite book is 'The Alchemist'."],
    ]


def test_pdf_knowledge_source():
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "crewai_quickstart.pdf"

    pdf_source = PDFKnowledgeSource(
        file_paths=[pdf_path], metadata={"preference": "personal"}
    )

    chunks = _saved_chunks(pdf_source)

    assert len(chunks) == 3
    assert chunks[0].startswith("11/6/24, 11:29 AM Quickstart - CrewAI\n")
    assert any("crewai create crew latest-ai-development" in c for c in chunks)


@pytest.mark.vcr()
def test_csv_knowledge_source(tmpdir):
    """Test CSVKnowledgeSource with a simple CSV file."""

    csv_content = [
        ["Name", "Age", "City"],
        ["Brandon", "30", "New York"],
        ["Alice", "25", "Los Angeles"],
        ["Bob", "35", "Chicago"],
    ]
    csv_path = Path(tmpdir.join("data.csv"))
    with open(csv_path, "w", encoding="utf-8") as f:
        for row in csv_content:
            f.write(",".join(row) + "\n")

    csv_source = CSVKnowledgeSource(
        file_paths=[csv_path], metadata={"preference": "personal"}
    )

    assert csv_source.content == {
        csv_path: "Name Age City\nBrandon 30 New York\nAlice 25 Los Angeles\nBob 35 Chicago\n"
    }
    chunks = _saved_chunks(csv_source)
    assert len(chunks) == 1
    assert "Brandon 30 New York" in chunks[0]


def test_json_knowledge_source(tmpdir):
    """Test JSONKnowledgeSource with a simple JSON file."""

    json_data = {
        "people": [
            {"name": "Brandon", "age": 30, "city": "New York"},
            {"name": "Alice", "age": 25, "city": "Los Angeles"},
            {"name": "Bob", "age": 35, "city": "Chicago"},
        ]
    }
    json_path = Path(tmpdir.join("data.json"))
    with open(json_path, "w", encoding="utf-8") as f:
        import json

        json.dump(json_data, f)

    json_source = JSONKnowledgeSource(
        file_paths=[json_path], metadata={"preference": "personal"}
    )

    assert json_source.content == {
        json_path: (
            "people:   -     name: Brandon\n    age: 30\n    city: New York\n\n"
            "  -     name: Alice\n    age: 25\n    city: Los Angeles\n\n"
            "  -     name: Bob\n    age: 35\n    city: Chicago\n\n\n"
        )
    }
    chunks = _saved_chunks(json_source)
    assert len(chunks) == 1
    assert "name: Alice" in chunks[0]


def test_excel_knowledge_source(tmpdir):
    """Test ExcelKnowledgeSource with a simple Excel file."""

    import pandas as pd  # type: ignore[import-untyped]

    excel_data = {
        "Name": ["Brandon", "Alice", "Bob"],
        "Age": [30, 25, 35],
        "City": ["New York", "Los Angeles", "Chicago"],
    }
    df = pd.DataFrame(excel_data)
    excel_path = Path(tmpdir.join("data.xlsx"))
    df.to_excel(excel_path, index=False)

    excel_source = ExcelKnowledgeSource(
        file_paths=[excel_path], metadata={"preference": "personal"}
    )

    assert _saved_chunks(excel_source) == [
        "Name,Age,City\nBrandon,30,New York\nAlice,25,Los Angeles\nBob,35,Chicago\n\n"
    ]


@pytest.mark.vcr
def test_docling_source(mock_vector_db):
    docling_source = CrewDoclingSource(
        file_paths=[
            "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
        ],
    )
    mock_vector_db.sources = [docling_source]
    mock_vector_db.query.return_value = [
        {
            "content": "Reward hacking is a technique used to improve the performance of reinforcement learning agents.",
            "score": 0.9,
        }
    ]
    # Perform a query
    query = "What is reward hacking?"
    results = mock_vector_db.query(query)
    assert any("reward hacking" in result["content"].lower() for result in results)
    mock_vector_db.query.assert_called_once()


@pytest.mark.vcr
@pytest.mark.timeout(180)
def test_multiple_docling_sources() -> None:
    urls: list[Path | str] = [
        "https://lilianweng.github.io/posts/2024-11-28-reward-hacking/",
        "https://lilianweng.github.io/posts/2024-07-07-hallucination/",
    ]
    docling_source = CrewDoclingSource(file_paths=urls)

    assert docling_source.file_paths == urls
    assert docling_source.content is not None


def test_file_path_validation():
    """Test file path validation for knowledge sources."""
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "crewai_quickstart.pdf"

    source = PDFKnowledgeSource(file_path=pdf_path)
    assert source.safe_file_paths == [pdf_path]

    source = PDFKnowledgeSource(file_paths=[pdf_path])
    assert source.safe_file_paths == [pdf_path]

    source = PDFKnowledgeSource(file_path=pdf_path, file_paths=[pdf_path])
    assert source.safe_file_paths == [pdf_path]

    with pytest.raises(
        ValueError,
        match="file_path/file_paths must be a Path, str, or a list of these types",
    ):
        PDFKnowledgeSource()


def test_hash_based_id_generation_without_doc_id(mock_vector_db):
    """Test that documents without doc_id generate hash-based IDs. Duplicates are deduplicated before upsert."""
    import hashlib
    import json
    from crewai.rag.chromadb.utils import _prepare_documents_for_chromadb
    from crewai.rag.types import BaseRecord

    documents: list[BaseRecord] = [
        {"content": "First document content", "metadata": {"source": "test1", "category": "research"}},
        {"content": "Second document content", "metadata": {"source": "test2", "category": "research"}},
        {"content": "Third document content"},
    ]

    result = _prepare_documents_for_chromadb(documents)

    assert len(result.ids) == 3

    # Unique documents should get 64-character hex hashes (no suffix)
    for doc_id in result.ids:
        assert len(doc_id) == 64, f"ID should be 64 characters: {doc_id}"
        assert all(c in "0123456789abcdef" for c in doc_id), f"ID should be hex: {doc_id}"

    assert result.ids[0] != result.ids[1] != result.ids[2]

    expected_hash_1 = hashlib.sha256(
        f"First document content|{json.dumps({'category': 'research', 'source': 'test1'}, sort_keys=True)}".encode()
    ).hexdigest()
    assert result.ids[0] == expected_hash_1, "First document hash should match expected"

    expected_hash_3 = hashlib.sha256("Third document content".encode()).hexdigest()
    assert result.ids[2] == expected_hash_3, "Third document hash should match expected"

    duplicate_documents: list[BaseRecord] = [
        {"content": "Same content", "metadata": {"source": "test"}},
        {"content": "Same content", "metadata": {"source": "test"}},
        {"content": "Same content", "metadata": {"source": "test"}},
    ]
    duplicate_result = _prepare_documents_for_chromadb(duplicate_documents)
    # Duplicates should be deduplicated - only one ID should remain
    assert len(duplicate_result.ids) == 1, "Duplicate documents should be deduplicated"
    assert len(duplicate_result.ids[0]) == 64, "Deduplicated ID should be clean hash"
    expected_hash = hashlib.sha256(
        f"Same content|{json.dumps({'source': 'test'}, sort_keys=True)}".encode()
    ).hexdigest()
    assert duplicate_result.ids[0] == expected_hash, "Deduplicated ID should match expected hash"


def test_hash_based_id_generation_with_doc_id_in_metadata(mock_vector_db):
    """Test that documents with doc_id in metadata use the doc_id directly, not hash-based."""
    from crewai.rag.chromadb.utils import _prepare_documents_for_chromadb
    from crewai.rag.types import BaseRecord

    documents_with_doc_id: list[BaseRecord] = [
        {"content": "First document", "metadata": {"doc_id": "custom-id-1", "source": "test1"}},
        {"content": "Second document", "metadata": {"doc_id": "custom-id-2"}},
    ]

    documents_without_doc_id: list[BaseRecord] = [
        {"content": "First document", "metadata": {"source": "test1"}},
        {"content": "Second document"},
    ]

    result_with_doc_id = _prepare_documents_for_chromadb(documents_with_doc_id)
    result_without_doc_id = _prepare_documents_for_chromadb(documents_without_doc_id)

    assert result_with_doc_id.ids == ["custom-id-1", "custom-id-2"]

    assert len(result_without_doc_id.ids) == 2
    # Unique documents get 64-character hashes
    for doc_id in result_without_doc_id.ids:
        assert len(doc_id) == 64, "ID should be 64 characters"
        assert all(c in "0123456789abcdef" for c in doc_id), "ID should be hex"
