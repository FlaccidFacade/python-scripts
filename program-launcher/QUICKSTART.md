# Quick Start Guide

Get started with the program launcher in 3 steps:

## 1. Basic Usage (No Installation Required)

The script uses only Python standard library, so you can run it directly:

```bash
python3 launcher.py <group_name>
```

## 2. Quick Test

List available groups:
```bash
python3 launcher.py --list
# Output:
# Available groups:
#   - lol (3 program(s))
#   - code (2 program(s))
#   - work (4 program(s))
#   - browse (3 program(s))
```

Launch a group:
```bash
python3 launcher.py code
```

## 3. Create Your Own Groups

Edit `groups.json` or create a new configuration file:

```json
{
  "groups": {
    "morning": [
      "https://mail.google.com",
      "slack",
      "spotify"
    ],
    "gaming": [
      "discord",
      "https://www.twitch.tv"
    ]
  }
}
```

Then launch:
```bash
python3 launcher.py morning
```

## Docker Quick Start

```bash
# Build
docker build -t program-launcher .

# Run help
docker run --rm program-launcher

# List groups
docker run --rm program-launcher python3 launcher.py --list

# Run tests
docker run --rm program-launcher pytest -v tests/
```

## Common Options

- **List groups**: `python3 launcher.py --list`
- **Verbose output**: Add `-v` flag
  ```bash
  python3 launcher.py -v code
  ```
- **Custom config file**: Use `-c` flag
  ```bash
  python3 launcher.py -c my-groups.json work
  ```

## Supported Program Types

1. **Application names**: `vscode`, `chrome`, `slack`, `discord`, `spotify`
2. **Direct URLs**: `https://github.com`, `www.google.com`
3. **Chrome tab descriptions**: `chrome tab with speed check`, `chrome tab with github`

## Next Steps

- See [README.md](README.md) for detailed documentation
- Run tests: `pytest tests/ -v` (after `pip install -r requirements.txt`)
- Get help: `python3 launcher.py --help`
