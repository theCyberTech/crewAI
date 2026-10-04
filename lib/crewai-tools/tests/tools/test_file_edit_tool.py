import os

import crewai_tools
from crewai_tools.tools.file_edit_tool.file_edit_tool import FileEditTool
import pytest


@pytest.fixture
def tool():
    return FileEditTool()


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    # Edits are confined to the working directory, so make the temp dir the cwd.
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def test_replaces_unique_match(tool, workdir):
    write(workdir / "app.py", "x = 1\ny = 2\n")

    result = tool._run(file_path="app.py", old_string="y = 2", new_string="y = 3")

    assert read(workdir / "app.py") == "x = 1\ny = 3\n"
    assert "Successfully replaced 1 occurrence in app.py" in result
    assert str(workdir) not in result


def test_empty_new_string_deletes_text(tool, workdir):
    write(workdir / "notes.txt", "keep\ndrop\nkeep\n")

    tool._run(file_path="notes.txt", old_string="drop\n", new_string="")

    assert read(workdir / "notes.txt") == "keep\nkeep\n"


def test_ambiguous_match_is_rejected_and_file_untouched(tool, workdir):
    write(workdir / "a.txt", "foo bar foo")

    result = tool._run(file_path="a.txt", old_string="foo", new_string="baz")

    assert "appears 2 times" in result
    assert read(workdir / "a.txt") == "foo bar foo"


@pytest.mark.parametrize("flag", [True, "true", "yes", "1"])
def test_replace_all_replaces_every_match(tool, workdir, flag):
    write(workdir / "a.txt", "foo bar foo")

    result = tool._run(
        file_path="a.txt", old_string="foo", new_string="baz", replace_all=flag
    )

    assert read(workdir / "a.txt") == "baz bar baz"
    assert "2 occurrences" in result


def test_invalid_replace_all_value(tool, workdir):
    write(workdir / "a.txt", "foo")

    result = tool._run(
        file_path="a.txt", old_string="foo", new_string="bar", replace_all="maybe"
    )

    assert result.startswith("Error:")
    assert read(workdir / "a.txt") == "foo"


def test_missing_old_string(tool, workdir):
    write(workdir / "a.txt", "hello")

    result = tool._run(file_path="a.txt", old_string="bye", new_string="hi")

    assert "was not found" in result
    assert read(workdir / "a.txt") == "hello"


def test_empty_or_identical_strings_are_rejected(tool, workdir):
    write(workdir / "a.txt", "hello")

    assert "must not be empty" in tool._run(
        file_path="a.txt", old_string="", new_string="x"
    )
    assert "identical" in tool._run(
        file_path="a.txt", old_string="hello", new_string="hello"
    )
    assert read(workdir / "a.txt") == "hello"


def test_preserves_crlf_line_endings(tool, workdir):
    write(workdir / "win.txt", "one\r\ntwo\r\n")

    tool._run(file_path="win.txt", old_string="two", new_string="three")

    assert read(workdir / "win.txt") == "one\r\nthree\r\n"


def test_nonexistent_file(tool, workdir):
    result = tool._run(file_path="missing.txt", old_string="a", new_string="b")

    assert "File not found" in result
    assert not (workdir / "missing.txt").exists()


def test_directory_target(tool, workdir):
    (workdir / "sub").mkdir()

    result = tool._run(file_path="sub", old_string="a", new_string="b")

    assert "is a directory" in result


def test_rejects_path_outside_base_dir(tool, workdir, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.txt"
    write(outside, "secret")

    for path in (str(outside), os.path.relpath(outside, workdir)):
        result = tool._run(file_path=path, old_string="secret", new_string="pwned")
        assert "outside the allowed directory" in result
        assert "base_dir" in result

    assert read(outside) == "secret"


def test_rejects_symlink_escape(tool, workdir, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside") / "secret.txt"
    write(outside, "secret")
    (workdir / "link.txt").symlink_to(outside)

    result = tool._run(file_path="link.txt", old_string="secret", new_string="pwned")

    assert "outside the allowed directory" in result
    assert read(outside) == "secret"


def test_base_dir_allows_editing_that_tree(workdir, tmp_path_factory):
    other = tmp_path_factory.mktemp("other")
    write(other / "a.txt", "old")
    tool = FileEditTool(base_dir=str(other))

    result = tool._run(file_path="a.txt", old_string="old", new_string="new")

    assert read(other / "a.txt") == "new"
    assert "Successfully replaced" in result


def test_custom_encoding(workdir):
    with open(workdir / "latin.txt", "w", encoding="latin-1") as f:
        f.write("café")
    tool = FileEditTool(encoding="latin-1")

    tool._run(file_path="latin.txt", old_string="café", new_string="thé")

    with open(workdir / "latin.txt", encoding="latin-1") as f:
        assert f.read() == "thé"


def test_undecodable_file(tool, workdir):
    (workdir / "bin.dat").write_bytes(b"\xff\xfe\x00bad")

    result = tool._run(file_path="bin.dat", old_string="bad", new_string="good")

    assert "Failed to decode" in result


def test_exported_from_package():
    assert crewai_tools.FileEditTool is FileEditTool
