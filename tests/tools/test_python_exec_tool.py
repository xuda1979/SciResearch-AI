import pytest
from unittest.mock import patch, MagicMock
from packages.sciresearch_tools.python_exec_tool import PythonExecTool

@pytest.mark.asyncio
async def test_python_exec_tool_simple_script():
    """Test that the tool can execute a simple python script."""
    tool = PythonExecTool()
    code = "print('hello world')"
    with patch.object(tool, '_get_docker_client') as mock_get_client:
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            output=b"hello world\n"
        )
        mock_client = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_get_client.return_value = mock_client

        output = await tool(code)
        assert output == "hello world\n"

@pytest.mark.asyncio
async def test_python_exec_tool_error():
    """Test that the tool handles errors in the script."""
    tool = PythonExecTool()
    code = "print(1/0)"
    with patch.object(tool, '_get_docker_client') as mock_get_client:
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            output=b"Traceback (most recent call last):\n  File \"/tmp/script.py\", line 1, in <module>\n    print(1/0)\nZeroDivisionError: division by zero\n"
        )
        mock_client = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_get_client.return_value = mock_client

        output = await tool(code)
        assert "ZeroDivisionError: division by zero" in output

@pytest.mark.asyncio
async def test_python_exec_tool_timeout():
    """Test that the tool times out when the script runs for too long."""
    tool = PythonExecTool(timeout=1)
    code = "import time; time.sleep(5)"

    with patch.object(tool, '_get_docker_client') as mock_get_client:
        mock_container = MagicMock()
        # The following import is correct
        from docker.errors import APIError
        mock_container.exec_run.side_effect = APIError("Read timed out")

        mock_client = MagicMock()
        mock_client.containers.create.return_value = mock_container
        mock_get_client.return_value = mock_client

        output = await tool(code)
        assert "An error occurred" in output
        assert "Read timed out" in output
