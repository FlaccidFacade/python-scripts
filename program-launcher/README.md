# Program Launcher

[![CI](https://github.com/FlaccidFacade/python-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/FlaccidFacade/python-scripts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/FlaccidFacade/python-scripts/branch/main/graph/badge.svg)](https://codecov.io/gh/FlaccidFacade/python-scripts)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)

A Python script to open multiple programs based on group definitions in a JSON configuration file. Perfect for quickly launching your favorite sets of applications for different workflows (gaming, coding, work, etc.).

## Features

- Launch multiple programs with a single command
- Group programs by workflow or activity
- Support for applications and URLs
- Cross-platform (Windows, macOS, Linux)
- No external dependencies (uses standard library)
- Smart URL detection for opening browser tabs

## Usage

### Basic Usage

```bash
python3 launcher.py <group_name>
```

### Examples

List all available groups:
```bash
python3 launcher.py --list
# Or simply:
python3 launcher.py
```

Launch the "lol" group (League of Legends setup):
```bash
python3 launcher.py lol
```

Launch the "code" group (development setup):
```bash
python3 launcher.py code
```

Use a custom configuration file:
```bash
python3 launcher.py -c my-groups.json work
```

Enable verbose output:
```bash
python3 launcher.py -v code
```

### Configuration File

Create a `groups.json` file in the same directory as the script:

```json
{
  "groups": {
    "lol": [
      "league",
      "professor",
      "chrome tab with a speed check"
    ],
    "code": [
      "vscode",
      "chrome tab with github open"
    ],
    "work": [
      "vscode",
      "slack",
      "https://mail.google.com",
      "spotify"
    ]
  }
}
```

**Group Structure:**
- Each group is a key in the "groups" dictionary
- Each group contains a list of programs to launch
- Programs can be:
  - Application names (e.g., "vscode", "slack", "spotify")
  - URLs (e.g., "https://github.com", "www.google.com")
  - Chrome tab descriptions (e.g., "chrome tab with a speed check")

### Supported Program Types

**1. Application Names:**
The script recognizes common applications:
- `vscode`, `vs code` - Visual Studio Code
- `chrome` - Google Chrome
- `firefox` - Firefox
- `spotify` - Spotify
- `discord` - Discord
- `slack` - Slack
- `league` - League of Legends

**2. URLs:**
Any string starting with `http://`, `https://`, or `www.` will be opened in the default browser.

**3. Chrome Tab Descriptions:**
Descriptions like "chrome tab with X" will:
- Extract common patterns (e.g., "speed check" → speedtest.net)
- Open GitHub if "github" is mentioned
- Search Google for other queries

### Options

- `group` - Name of the group to launch (optional, omit to list groups)
- `-c, --config` - Path to configuration file (default: groups.json)
- `-l, --list` - List all available groups
- `-v, --verbose` - Enable verbose output
- `-h, --help` - Show help message

## Requirements

- Python 3.7+

For testing:
- pytest
- pytest-cov

Install testing dependencies:

```bash
pip install -r requirements.txt
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ -v --cov=launcher --cov-report=term-missing
```

## Platform-Specific Notes

### macOS
- Applications are launched using the `open` command
- Works with apps in `/Applications` or user applications

### Windows
- Applications are launched using the `start` command
- Recognizes installed applications by name

### Linux
- Applications are launched by executable name
- Checks common locations: `/usr/bin`, `/usr/local/bin`, `/snap/bin`
- Works with snap and flatpak applications

## Examples

### Gaming Setup
```json
{
  "groups": {
    "gaming": [
      "discord",
      "spotify",
      "https://www.twitch.tv"
    ]
  }
}
```

### Development Setup
```json
{
  "groups": {
    "dev": [
      "vscode",
      "chrome tab with github",
      "https://stackoverflow.com",
      "spotify"
    ]
  }
}
```

### Morning Routine
```json
{
  "groups": {
    "morning": [
      "https://mail.google.com",
      "https://calendar.google.com",
      "slack",
      "chrome tab with weather"
    ]
  }
}
```

## Docker

Build the Docker image:

```bash
docker build -t program-launcher .
```

Run tests in Docker:

```bash
docker run --rm program-launcher pytest -v tests/
```

## Troubleshooting

**Application not launching?**
- Check if the application is installed
- Try using the full application name
- Use verbose mode (`-v`) to see what the script is trying

**URL not opening?**
- Ensure you have a default browser set
- Check if the URL is properly formatted

**Configuration errors?**
- Validate your JSON using a JSON validator
- Ensure "groups" key exists at the top level
- Each group must be a list of strings

## License

This is free and unencumbered software released into the public domain. See LICENSE file for details.
