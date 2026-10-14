# FileEditTool Documentation

## Description
The `FileEditTool` is a component of the crewai_tools package that edits an existing text file by replacing an exact string. Instead of rewriting a whole file, the agent names the snippet to change and the text to put in its place, which makes small, targeted edits to code, configuration, and documents cheap and safe. The snippet must match exactly once unless `replace_all` is set, so an ambiguous match never edits the wrong place. Line endings are kept as they are on disk.

## Installation
Install the crewai_tools package to use the `FileEditTool` in your projects:

```shell
pip install 'crewai[tools]'
```

## Example
To get started with the `FileEditTool`:

```python
from crewai_tools import FileEditTool

# Initialize the tool
file_edit_tool = FileEditTool()

# Replace a single, unique snippet
result = file_edit_tool.run(
    file_path='config.yaml',
    old_string='debug: false',
    new_string='debug: true',
)
print(result)

# Rename every occurrence of an identifier
result = file_edit_tool.run(
    file_path='app.py',
    old_string='old_name',
    new_string='new_name',
    replace_all=True,
)
```

## Arguments
The agent supplies these at runtime:

- `file_path`: The path of the existing file to edit. A relative path resolves inside the tool's allowed directory.
- `old_string`: The exact text to replace, including whitespace and indentation. It must appear exactly once unless `replace_all` is true; include surrounding lines to make it unique.
- `new_string`: The replacement text. Must differ from `old_string`. Pass an empty string to delete `old_string`.
- `replace_all` (optional): Whether to replace every occurrence. Accepts `true`/`false` (also `yes`/`no`, `on`/`off`, `1`/`0`). Defaults to `false`, which reports an error when `old_string` appears more than once.

You set these when constructing the tool:

- `base_dir` (optional): The directory that edits must stay inside. Defaults to the current working directory.
- `encoding` (optional): Text encoding used to read and write the file. Defaults to `utf-8`.

The tool edits existing files only. Use `FileWriterTool` to create a file or replace its whole content.

## Allowed paths
Because the file path is usually chosen by an LLM at runtime, edits are confined to a sandbox: the resolved `file_path` must be inside `base_dir` (the current working directory by default). `..` segments, absolute paths, and symlinks are resolved before the check, so they cannot be used to escape.

To let an agent edit outside the working directory, point `base_dir` at the target tree:

```python
# The agent may edit anywhere under /srv/app, and nowhere outside it
file_edit_tool = FileEditTool(base_dir='/srv/app')
```

Setting `CREWAI_TOOLS_ALLOW_UNSAFE_PATHS=true` disables path validation, but it applies process-wide to every crewai-tools tool, including the SSRF protections on URL-fetching tools, so prefer `base_dir`.
