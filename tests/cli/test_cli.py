from __future__ import annotations
import subprocess
import sys
from unittest.mock import patch, MagicMock

from sciresearch_cli.main import main

def test_help_message():
    """Check that the --help message is printed and contains expected text."""
    result = subprocess.run(
        [sys.executable, "-m", "sciresearch_ai.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage: sciresearch-ai" in result.stdout
    assert "new" in result.stdout
    assert "run" in result.stdout
    assert "test-openai" in result.stdout

def test_run_mocked():
    """Test the 'run' command with mocks to ensure correct components are called."""
    with patch("sciresearch_cli.main.Project") as mock_project_class, \
         patch("sciresearch_cli.main.build_provider") as mock_build_provider, \
         patch("sciresearch_cli.main.Orchestrator") as mock_orchestrator_class, \
         patch("sciresearch_cli.main.RunConfig") as mock_run_config_class:

        # Arrange
        mock_project_instance = MagicMock()
        mock_project_class.return_value = mock_project_instance

        mock_provider_instance = MagicMock()
        mock_build_provider.return_value = mock_provider_instance

        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_class.return_value = mock_orchestrator_instance

        mock_run_config_instance = MagicMock()
        mock_run_config_class.return_value = mock_run_config_instance

        # Act
        main([
            "run",
            "--project", "test_project",
            "--provider", "mock",
            "--max-iterations", "3",
            "--budget-usd", "1.23",
        ])

        # Assert
        mock_project_class.assert_called_once_with("test_project")
        mock_build_provider.assert_called_once()

        # Check that args from CLI are passed to RunConfig
        mock_run_config_class.assert_called_once()
        _, kwargs = mock_run_config_class.call_args
        assert kwargs["max_iterations"] == 3
        assert kwargs["budget_usd"] == 1.23

        # Check that instances are passed to Orchestrator
        mock_orchestrator_class.assert_called_once_with(
            mock_project_instance,
            mock_provider_instance,
            mock_run_config_instance,
        )

        # Check that the run method is called
        mock_orchestrator_instance.run.assert_called_once()
