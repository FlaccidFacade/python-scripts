# Git Repository Merger

A Python script to merge multiple git repositories into a single repository, preserving all content, commits, and git history.

## Features

- Merges multiple git repositories into one target repository
- Preserves complete git history from all source repositories
- Three conflict resolution strategies: automatic (theirs), unresolved (ours), or manual
- Handles unrelated histories properly
- No external dependencies (uses standard library)

## Usage

### Basic Usage

```bash
python3 merge.py <target_repo> <source_repo1> <source_repo2> [source_repo3 ...]
```

### Example

Merge three repositories into a new merged repository:

```bash
python3 merge.py /path/to/merged-repo /path/to/repo1 /path/to/repo2 /path/to/repo3
```

This will:
1. Create the target repository if it doesn't exist
2. Merge each source repository using git merge (conflicts resolved automatically with 'ours' strategy by default)
3. Preserve all git history from each repository

### Options

- `--strategy {ours,theirs,manual}`: Choose conflict resolution strategy (default: ours)
  - `ours`: Keep all changes, commit with conflict markers in files
  - `theirs`: Automatically accept all changes from source repositories
  - `manual`: Prompt user to manually resolve conflicts as they occur
- `-v, --verbose`: Enable verbose output to see all git commands
- `-h, --help`: Show help message

### Conflict Resolution Strategies

When merging repositories with conflicting files (e.g., both have a README.md), you can choose how to handle conflicts:

**Strategy A (ours)** - Default:
```bash
python3 merge.py /path/to/merged-repo /path/to/repo1 /path/to/repo2
```
Commits all changes with conflict markers preserved in files. You can resolve conflicts later.

**Strategy B (theirs)**:
```bash
python3 merge.py --strategy theirs /path/to/merged-repo /path/to/repo1 /path/to/repo2
```
Automatically resolves conflicts by accepting changes from source repositories.

**Strategy C (manual)**:
```bash
python3 merge.py --strategy manual /path/to/merged-repo /path/to/repo1 /path/to/repo2
```
Pauses when conflicts occur and prompts you to resolve them interactively.

## Requirements

- Python 3.7+
- Git

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
pytest tests/ -v --cov=merge --cov-report=term-missing
```

## Docker

### Build the Docker Image

```bash
docker build -t merge-script .
```

### Run Tests in Docker

```bash
docker run --rm merge-script
```

### Use the Script in Docker

To use the script with your own repositories, mount them as volumes:

```bash
docker run --rm -v /path/to/source1:/repos/source1:ro \
                -v /path/to/source2:/repos/source2:ro \
                -v /path/to/source3:/repos/source3:ro \
                -v /path/to/target:/repos/target \
                merge-script \
                python3 merge.py /repos/target /repos/source1 /repos/source2 /repos/source3
```

## How It Works

1. **Validation**: Validates that all source repositories exist and are git repositories
2. **Initialization**: Creates the target repository if it doesn't exist
3. **For each source repository**:
   - Adds the source as a git remote
   - Fetches all branches and history
   - Checks out the source content
   - Merges into the target repository using `--allow-unrelated-histories`
   - Applies the selected conflict resolution strategy
4. **Result**: A single repository containing all files and complete git history

## Example Scenario

You have three separate projects:

```
/projects/
├── frontend/       (React app)
├── backend/        (Python API)
└── infrastructure/ (Terraform configs)
```

Merge them into a monorepo:

```bash
python3 merge.py /projects/monorepo /projects/frontend /projects/backend /projects/infrastructure
```

Result:

```
/projects/monorepo/
├── .git/            (contains full history)
├── (all files from frontend, backend, and infrastructure merged)
```

You can now run `git log --graph --oneline --all` to see the complete history from all three repositories.

**Note**: If the repositories have conflicting files, use the `--strategy` option to control how conflicts are resolved.

## Notes

- The script uses `git merge --allow-unrelated-histories` to merge repositories with no common ancestor
- All commits from source repositories are preserved with their original timestamps and authors
- The target repository can be a new or existing git repository
- Source repositories are not modified
