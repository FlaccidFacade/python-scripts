# Quick Start Guide

Get started with the merge script in 3 steps:

## 1. Basic Usage (No Installation Required)

The script uses only Python standard library, so you can run it directly:

```bash
python3 merge.py /path/to/target /path/to/repo1 /path/to/repo2 /path/to/repo3
```

## 2. Quick Test

Test the script with sample repositories:

```bash
# Create 3 test repos
cd /tmp
for i in 1 2 3; do
  mkdir -p test_repos/repo$i && cd test_repos/repo$i
  git init
  git config user.email "test@example.com"
  git config user.name "Test User"
  echo "Content $i" > file$i.txt
  git add . && git commit -m "Initial commit"
  cd ../..
done

# Merge them
python3 merge.py /tmp/merged_repo /tmp/test_repos/repo1 /tmp/test_repos/repo2 /tmp/test_repos/repo3

# View results
cd /tmp/merged_repo
git log --graph --oneline --all
ls -R
```

## 3. Real-World Example

Merge three separate projects into a monorepo:

```bash
python3 merge.py ~/monorepo ~/projects/frontend ~/projects/backend ~/projects/docs
```

This creates a merged repository with all files from frontend, backend, and docs, along with their complete git history.

## Docker Quick Start

```bash
# Build
docker build -t merge-script .

# Run tests
docker run --rm merge-script pytest -v tests/

# Use with your repos (mount as volumes)
docker run --rm \
  -v /path/to/repo1:/repos/repo1:ro \
  -v /path/to/repo2:/repos/repo2:ro \
  -v /path/to/target:/repos/target \
  merge-script \
  python3 merge.py /repos/target /repos/repo1 /repos/repo2
```

## Common Options

- **Verbose output**: Add `-v` flag
  ```bash
  python3 merge.py -v /path/to/target /path/to/repo1 /path/to/repo2
  ```

- **Choose conflict resolution strategy**:
  ```bash
  # Accept all changes from source repos (no conflicts)
  python3 merge.py --strategy theirs /path/to/target /path/to/repo1 /path/to/repo2
  
  # Keep conflicts unresolved (default)
  python3 merge.py --strategy ours /path/to/target /path/to/repo1 /path/to/repo2
  
  # Favor current state in conflicts
  python3 merge.py --strategy recursive-ours /path/to/target /path/to/repo1 /path/to/repo2
  
  # Use custom git merge options
  python3 merge.py --custom-strategy ignore-space-change /path/to/target /path/to/repo1 /path/to/repo2
  ```
  
  See [MERGE_STRATEGIES.md](MERGE_STRATEGIES.md) for all strategies and detailed explanations.

## Next Steps

- See [README.md](README.md) for detailed documentation
- Run tests: `pytest tests/ -v` (after `pip install -r requirements.txt`)
- Get help: `python3 merge.py --help`
