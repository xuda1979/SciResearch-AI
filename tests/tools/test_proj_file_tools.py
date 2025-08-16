import os

import pytest

from packages.sciresearch_tools.proj_file_tools import (
    ListProjectFilesTool,
    WriteProjectFileTool,
)


@pytest.mark.asyncio
async def test_write_and_list_project_files(tmpdir):
    """Test that we can write and list project files."""
    base_dir = str(tmpdir)
    write_tool = WriteProjectFileTool(base_dir=base_dir)
    list_tool = ListProjectFilesTool(base_dir=base_dir)

    # List files in an empty directory
    files = await list_tool()
    assert files == []

    # Write a file
    filepath = "test_file.txt"
    content = "hello world"
    result = await write_tool(filepath, content)
    assert result == f"Successfully wrote to {filepath}"

    # Verify the file was written
    with open(os.path.join(base_dir, filepath), "r") as f:
        assert f.read() == content

    # List files again
    files = await list_tool()
    assert files == ["test_file.txt"]

    # Write a file in a subdirectory
    filepath2 = "subdir/test_file2.txt"
    os.makedirs(os.path.join(base_dir, "subdir"))
    content2 = "hello again"
    result2 = await write_tool(filepath2, content2)
    assert result2 == f"Successfully wrote to {filepath2}"

    # List files again
    files = await list_tool()
    assert set(files) == {"test_file.txt", "subdir/test_file2.txt"}


@pytest.mark.asyncio
async def test_write_project_file_traversal(tmpdir):
    """Test that writing outside the base directory is not allowed."""
    base_dir = str(tmpdir)
    write_tool = WriteProjectFileTool(base_dir=base_dir)

    # Attempt to write outside the directory
    filepath = "../test_file.txt"
    content = "hello world"
    result = await write_tool(filepath, content)
    assert "cannot contain '..'" in result


@pytest.mark.asyncio
async def test_write_project_file_error(tmpdir):
    """Test that write errors are handled gracefully."""
    base_dir = str(tmpdir)
    write_tool = WriteProjectFileTool(base_dir=base_dir)

    if os.geteuid() == 0:
        pytest.skip("Skipping permission test when running as root")

    # Make the directory read-only
    os.chmod(base_dir, 0o555)

    filepath = "test_file.txt"
    content = "hello world"
    result = await write_tool(filepath, content)
    assert "Error writing to file" in result

    # Restore permissions so cleanup can happen
    os.chmod(base_dir, 0o755)
