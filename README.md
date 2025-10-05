# python-scripts

[![CI](https://github.com/FlaccidFacade/python-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/FlaccidFacade/python-scripts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/FlaccidFacade/python-scripts/branch/main/graph/badge.svg)](https://codecov.io/gh/FlaccidFacade/python-scripts)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)

Repository for individual Python scripts with independent package management per script/folder.

## Structure

Each script lives in its own directory with:
- Independent `requirements.txt` for package management
- Its own tests using pytest
- A Dockerfile to prove working case
- Script-specific README with usage instructions

## Available Scripts

### merge/

Merges multiple git repositories into one, preserving all content and git history.

**Quick Start:**
```bash
cd merge/
pip install -r requirements.txt
python3 merge.py /path/to/target /path/to/repo1 /path/to/repo2 /path/to/repo3
```

**Docker:**
```bash
cd merge/
docker build -t merge-script .
docker run --rm merge-script  # Runs tests
```

See [merge/README.md](merge/README.md) for detailed documentation.

## Development

Each script directory is self-contained:

1. **Install dependencies**: `pip install -r <script>/requirements.txt`
2. **Run tests**: `pytest <script>/tests/ -v`
3. **Build Docker**: `docker build -t <script-name> <script>/`
4. **Run in Docker**: `docker run --rm <script-name>` 
