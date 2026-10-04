import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, field_validator

from crewai_tools.security.safe_path import (
    format_error_for_display,
    format_path_for_display,
    format_sandbox_error,
    validate_file_path,
)
from crewai_tools.tools.file_writer_tool.file_writer_tool import strtobool


class FileEditToolInput(BaseModel):
    """Input for FileEditTool."""

    file_path: str = Field(
        ...,
        description=(
            "Path of the existing file to edit. A relative path resolves inside "
            "the tool's allowed directory."
        ),
    )
    old_string: str = Field(
        ...,
        description=(
            "The exact text to replace, including whitespace and indentation. "
            "It must appear in the file exactly once unless 'replace_all' is "
            "true; include surrounding lines to make it unique."
        ),
    )
    new_string: str = Field(
        ...,
        description=(
            "The text to replace 'old_string' with. Must differ from "
            "'old_string'. Pass an empty string to delete 'old_string'."
        ),
    )
    replace_all: str | bool = Field(
        False,
        description=(
            "Whether to replace every occurrence of 'old_string'. Accepts "
            "true/false (also yes/no, on/off, 1/0). Defaults to false, which "
            "reports an error when 'old_string' appears more than once."
        ),
    )


class FileEditTool(BaseTool):
    """A tool for editing a text file by exact string replacement.

    The agent names a snippet of the file and the text to put in its place,
    so it can change part of a file without rewriting the whole of it. The
    snippet must match exactly once unless ``replace_all`` is set, which keeps
    an ambiguous match from editing the wrong place. Line endings are kept as
    they are on disk.

    Edits are confined to ``base_dir`` (the current working directory by
    default), because the target path is typically chosen by an LLM at
    runtime. Set ``base_dir`` to widen that sandbox deliberately.

    Args:
        base_dir (Optional[str]): Directory that edits must stay inside.
            Defaults to the current working directory.
        encoding (str): Text encoding used to read and write the file.
            Defaults to UTF-8.

    Example:
        >>> tool = FileEditTool()
        >>> tool.run(
        ...     file_path="config.yaml",
        ...     old_string="debug: false",
        ...     new_string="debug: true",
        ... )
        >>> # Allow the agent to edit anywhere under /srv/app:
        >>> tool = FileEditTool(base_dir="/srv/app")
    """

    name: str = "File Edit Tool"
    description: str = "A tool to edit an existing text file by replacing an exact string. Accepts file_path, old_string, new_string, and optionally a replace_all flag. 'old_string' must match the file's text exactly, including whitespace, and appear exactly once unless replace_all is true. Edits are confined to the tool's allowed directory; a path that resolves outside it is rejected."
    args_schema: type[BaseModel] = FileEditToolInput
    base_dir: str | None = None
    encoding: str = "utf-8"

    @field_validator("base_dir")
    @classmethod
    def _anchor_base_dir(cls, value: str | None) -> str | None:
        """Resolve base_dir once so a later chdir cannot move the sandbox."""
        return os.path.realpath(value) if value is not None else None

    def _run(
        self,
        file_path: str,
        old_string: str,
        new_string: str,
        replace_all: str | bool = False,
    ) -> str:
        """Replace *old_string* with *new_string* in *file_path*."""
        try:
            replace_every = strtobool(replace_all)
        except ValueError as e:
            return f"Error: {e!s}"

        if not old_string:
            return "Error: 'old_string' must not be empty. Use FileWriterTool to create or overwrite a file."
        if old_string == new_string:
            return "Error: 'old_string' and 'new_string' are identical, so there is nothing to change."

        try:
            resolved_path = validate_file_path(file_path, self.base_dir)
        except ValueError as e:
            return "Error: Invalid file path: " + format_sandbox_error(
                e,
                "Pass base_dir to FileEditTool to allow editing another "
                "directory tree.",
            )

        display_path = format_path_for_display(resolved_path, self.base_dir)
        try:
            # newline="" keeps "\r\n" intact, so editing a CRLF file does not
            # rewrite every line ending.
            with open(resolved_path, "r", encoding=self.encoding, newline="") as file:
                content = file.read()
        except FileNotFoundError:
            return f"Error: File not found at path: {display_path}"
        except IsADirectoryError:
            return f"Error: {display_path} is a directory, not a file."
        except PermissionError:
            return f"Error: Permission denied when trying to read file: {display_path}"
        except UnicodeDecodeError:
            return (
                f"Error: Failed to decode file {display_path} as {self.encoding}. "
                f"Pass a different 'encoding' to FileEditTool if the file uses "
                f"another text encoding."
            )
        except Exception as e:
            return (
                f"Error: Failed to read file {display_path}. "
                f"{format_error_for_display(e)}"
            )

        occurrences = content.count(old_string)
        if occurrences == 0:
            return (
                f"Error: 'old_string' was not found in {display_path}. It must "
                f"match the file's text exactly, including whitespace and "
                f"indentation."
            )
        if occurrences > 1 and not replace_every:
            return (
                f"Error: 'old_string' appears {occurrences} times in "
                f"{display_path}. Include more surrounding text to make it "
                f"unique, or set replace_all to true to replace every occurrence."
            )

        updated = content.replace(old_string, new_string)
        try:
            with open(resolved_path, "w", encoding=self.encoding, newline="") as file:
                file.write(updated)
        except PermissionError:
            return f"Error: Permission denied when trying to write file: {display_path}"
        except Exception as e:
            return (
                f"Error: Failed to write file {display_path}. "
                f"{format_error_for_display(e)}"
            )

        noun = "occurrence" if occurrences == 1 else "occurrences"
        return f"Successfully replaced {occurrences} {noun} in {display_path}"
