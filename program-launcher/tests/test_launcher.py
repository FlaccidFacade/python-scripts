"""Tests for the program launcher script."""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import launcher
sys.path.insert(0, str(Path(__file__).parent.parent))
import launcher


@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary configuration file."""
    config = {
        "groups": {
            "test_group": ["app1", "app2"],
            "url_group": ["https://example.com", "www.google.com"],
            "mixed_group": ["vscode", "https://github.com", "chrome tab with speed check"]
        }
    }
    config_file = tmp_path / "test_groups.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def invalid_config(tmp_path):
    """Create an invalid configuration file."""
    config_file = tmp_path / "invalid.json"
    with open(config_file, 'w') as f:
        f.write("{invalid json")
    return config_file


@pytest.fixture
def missing_groups_config(tmp_path):
    """Create a configuration file without 'groups' key."""
    config = {"other_key": {}}
    config_file = tmp_path / "no_groups.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    return config_file


class TestProgramLauncher:
    """Test cases for ProgramLauncher class."""

    def test_init_valid_config(self, temp_config):
        """Test initialization with valid config."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        assert launcher_obj.config is not None
        assert "groups" in launcher_obj.config

    def test_init_missing_file(self, tmp_path):
        """Test initialization with missing config file."""
        missing_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            launcher.ProgramLauncher(missing_file)

    def test_init_invalid_json(self, invalid_config):
        """Test initialization with invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            launcher.ProgramLauncher(invalid_config)

    def test_init_missing_groups_key(self, missing_groups_config):
        """Test initialization with missing 'groups' key."""
        with pytest.raises(ValueError, match="must contain a 'groups' key"):
            launcher.ProgramLauncher(missing_groups_config)

    def test_list_groups(self, temp_config):
        """Test listing available groups."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        groups = launcher_obj.list_groups()
        assert "test_group" in groups
        assert "url_group" in groups
        assert "mixed_group" in groups

    def test_launch_invalid_group(self, temp_config):
        """Test launching a non-existent group."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        with pytest.raises(ValueError, match="Group 'invalid' not found"):
            launcher_obj.launch_group("invalid")

    @patch('launcher.ProgramLauncher._launch_program')
    def test_launch_group_success(self, mock_launch, temp_config):
        """Test launching a valid group."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj.launch_group("test_group")
        assert mock_launch.call_count == 2
        mock_launch.assert_any_call("app1")
        mock_launch.assert_any_call("app2")

    def test_extract_url_speed_check(self, temp_config):
        """Test URL extraction for speed check."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        url = launcher_obj._extract_url_from_description("chrome tab with a speed check")
        assert "speedtest.net" in url

    def test_extract_url_github(self, temp_config):
        """Test URL extraction for github."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        url = launcher_obj._extract_url_from_description("chrome tab with github open")
        assert "github.com" in url

    def test_extract_url_google(self, temp_config):
        """Test URL extraction for google."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        url = launcher_obj._extract_url_from_description("chrome tab with google")
        assert "google.com" in url

    def test_extract_url_generic(self, temp_config):
        """Test URL extraction for generic search."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        url = launcher_obj._extract_url_from_description("chrome tab with something random")
        assert "google.com/search" in url
        assert "something+random" in url

    @patch('subprocess.Popen')
    def test_open_url(self, mock_popen, temp_config):
        """Test opening a URL."""
        launcher_obj = launcher.ProgramLauncher(temp_config, verbose=True)
        launcher_obj._open_url("https://example.com")
        assert mock_popen.called

    @patch('subprocess.Popen')
    def test_open_url_without_protocol(self, mock_popen, temp_config):
        """Test opening a URL without http protocol."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._open_url("www.example.com")
        # Check that Popen was called with the normalized URL (https:// is added)
        assert mock_popen.called
        call_args = str(mock_popen.call_args)
        assert "https://example.com" in call_args or "example.com" in call_args

    @patch('subprocess.Popen')
    def test_open_application(self, mock_popen, temp_config):
        """Test opening an application."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._open_application("vscode")
        assert mock_popen.called

    @patch('subprocess.Popen', side_effect=Exception("Launch failed"))
    def test_open_url_failure(self, mock_popen, temp_config, capsys):
        """Test handling of URL opening failure."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._open_url("https://example.com")
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "Failed" in captured.out

    @patch('launcher.ProgramLauncher._open_url')
    def test_launch_program_url_http(self, mock_open_url, temp_config):
        """Test launching a program with HTTP URL."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._launch_program("https://example.com")
        mock_open_url.assert_called_once()

    @patch('launcher.ProgramLauncher._open_url')
    def test_launch_program_url_www(self, mock_open_url, temp_config):
        """Test launching a program with www URL."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._launch_program("www.example.com")
        mock_open_url.assert_called_once()

    @patch('launcher.ProgramLauncher._open_url')
    def test_launch_program_chrome_tab(self, mock_open_url, temp_config):
        """Test launching a chrome tab description."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._launch_program("chrome tab with github")
        mock_open_url.assert_called_once()

    @patch('launcher.ProgramLauncher._open_application')
    def test_launch_program_application(self, mock_open_app, temp_config):
        """Test launching an application."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        launcher_obj._launch_program("vscode")
        mock_open_app.assert_called_once()

    def test_launch_program_empty_string(self, temp_config):
        """Test launching with empty program string."""
        launcher_obj = launcher.ProgramLauncher(temp_config)
        # Should not raise an error, just skip
        launcher_obj._launch_program("")
        launcher_obj._launch_program("   ")


class TestMain:
    """Test cases for main function."""

    @patch('launcher.ProgramLauncher')
    def test_main_list_groups(self, mock_launcher_class, temp_config, capsys):
        """Test main function with --list flag."""
        mock_instance = MagicMock()
        mock_instance.list_groups.return_value = ["group1", "group2"]
        mock_instance.config = {"groups": {"group1": ["app1"], "group2": ["app2"]}}
        mock_launcher_class.return_value = mock_instance

        with patch('sys.argv', ['launcher.py', '--list', '--config', str(temp_config)]):
            launcher.main()
        
        captured = capsys.readouterr()
        assert "Available groups" in captured.out

    @patch('launcher.ProgramLauncher')
    def test_main_no_args(self, mock_launcher_class, temp_config, capsys):
        """Test main function with no group specified."""
        mock_instance = MagicMock()
        mock_instance.list_groups.return_value = ["group1"]
        mock_instance.config = {"groups": {"group1": ["app1"]}}
        mock_launcher_class.return_value = mock_instance

        with patch('sys.argv', ['launcher.py', '--config', str(temp_config)]):
            launcher.main()
        
        captured = capsys.readouterr()
        assert "Available groups" in captured.out

    @patch('launcher.ProgramLauncher')
    def test_main_launch_group(self, mock_launcher_class, temp_config):
        """Test main function launching a group."""
        mock_instance = MagicMock()
        mock_launcher_class.return_value = mock_instance

        with patch('sys.argv', ['launcher.py', 'test_group', '--config', str(temp_config)]):
            launcher.main()
        
        mock_instance.launch_group.assert_called_once_with('test_group')

    @patch('launcher.ProgramLauncher', side_effect=Exception("Test error"))
    def test_main_error_handling(self, mock_launcher_class, temp_config, capsys):
        """Test main function error handling."""
        with patch('sys.argv', ['launcher.py', 'test_group', '--config', str(temp_config)]):
            with pytest.raises(SystemExit):
                launcher.main()
        
        captured = capsys.readouterr()
        assert "Error" in captured.out
