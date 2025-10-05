# Merge Strategies Guide

This document explains the merge strategies available in the merge script and how to understand the merge context when combining multiple repositories.

## Understanding Merge Context: "Ours" vs "Theirs"

When merging repositories, it's important to understand which side is which:

- **"ours"** = The current state in the **target repository** (HEAD)
- **"theirs"** = The incoming changes from the **source repository** being merged

### Example: Merging 3 Repositories

When you run:
```bash
python3 merge.py /target /repo1 /repo2 /repo3
```

The merge happens sequentially:

1. **First merge**: `repo1` → target
   - "ours" = empty target repository
   - "theirs" = repo1's content
   - Result: target now contains repo1

2. **Second merge**: `repo2` → target (which now has repo1)
   - "ours" = target + repo1
   - "theirs" = repo2's content
   - Result: target now contains repo1 + repo2

3. **Third merge**: `repo3` → target (which now has repo1 + repo2)
   - "ours" = target + repo1 + repo2
   - "theirs" = repo3's content
   - Result: target now contains repo1 + repo2 + repo3

**Key Point**: Each merge builds on the previous state. By the time you merge repo3, "ours" includes everything from repo1 and repo2.

## Built-in Strategies

### 1. `ours` (Default)
Commits with conflict markers preserved in files.

```bash
python3 merge.py /target /repo1 /repo2 /repo3
# or explicitly:
python3 merge.py --strategy ours /target /repo1 /repo2 /repo3
```

**Behavior**:
- Attempts to merge changes from both sides
- If conflicts occur, commits the files WITH conflict markers like:
  ```
  <<<<<<< HEAD
  Content from ours (target)
  =======
  Content from theirs (source)
  >>>>>>> merge_repo2
  ```
- You can resolve conflicts later at your convenience

**Best for**: When you want to review and manually resolve conflicts later.

### 2. `theirs`
Accepts all incoming changes from source repositories.

```bash
python3 merge.py --strategy theirs /target /repo1 /repo2 /repo3
```

**Behavior**:
- In case of conflicts, automatically chooses changes from the source repository
- No conflict markers in the final result
- Uses git merge option: `-X theirs`

**Best for**: When you trust the incoming changes and want automatic resolution.

**Example**: If both target and repo2 have a file `README.md`:
- Target's README.md: "Target documentation"
- repo2's README.md: "Repo2 documentation"
- Result: "Repo2 documentation" (theirs wins)

### 3. `ours-only`
Discards all incoming changes, keeping only the current state.

```bash
python3 merge.py --strategy ours-only /target /repo1 /repo2 /repo3
```

**Behavior**:
- Merges the git history but keeps the current file content
- Uses git merge strategy: `-s ours`
- Useful when you only want to record the merge in history

**Best for**: When you want to merge histories but not actual file content.

**Example**: If both target and repo2 have a file `README.md`:
- Target's README.md: "Target documentation"
- repo2's README.md: "Repo2 documentation"
- Result: "Target documentation" (ours wins, theirs discarded)

### 4. `recursive-ours`
Favors current state in conflicts while still merging non-conflicting changes.

```bash
python3 merge.py --strategy recursive-ours /target /repo1 /repo2 /repo3
```

**Behavior**:
- Merges non-conflicting changes from both sides
- For conflicts, automatically chooses current state (ours)
- Uses git merge option: `-X ours`
- Similar to `ours-only` but still merges non-conflicting changes

**Best for**: When you want to incorporate non-conflicting changes but prefer current state for conflicts.

**Example**: If both have different lines in `config.txt`:
- Target's config.txt:
  ```
  setting1=value1
  setting2=value2
  ```
- repo2's config.txt:
  ```
  setting1=value1_from_repo2
  setting3=value3
  ```
- Result (recursive-ours):
  ```
  setting1=value1
  setting2=value2
  setting3=value3
  ```
  (setting1 keeps target's value, setting3 is added from repo2)

### 5. `patience`
Uses patience diff algorithm for better conflict resolution.

```bash
python3 merge.py --strategy patience /target /repo1 /repo2 /repo3
```

**Behavior**:
- Uses a more sophisticated diff algorithm
- Better at detecting moved or reordered code blocks
- Uses git merge option: `-X patience`
- If conflicts still occur, commits with conflict markers

**Best for**: Code files that have been refactored or reorganized.

### 6. `manual`
Interactive resolution - pauses for user input when conflicts occur.

```bash
python3 merge.py --strategy manual /target /repo1 /repo2 /repo3
```

**Behavior**:
- Pauses when conflicts are detected
- Displays instructions for resolution
- Waits for user to resolve and commit
- Continues after user confirmation

**Best for**: When you want full control and immediate resolution.

## Custom Strategy Options

For advanced users, you can pass custom git merge options:

```bash
python3 merge.py --custom-strategy ignore-space-change /target /repo1 /repo2
python3 merge.py --custom-strategy rename-threshold=75 /target /repo1 /repo2
python3 merge.py --custom-strategy no-renames /target /repo1 /repo2
```

These options are passed to `git merge -X <OPTION>`.

Common custom options:
- `ignore-space-change`: Ignore whitespace changes when comparing
- `ignore-all-space`: Ignore all whitespace
- `ignore-space-at-eol`: Ignore whitespace at end of line
- `rename-threshold=<n>`: Threshold for detecting renames (0-100)
- `no-renames`: Disable rename detection
- `find-renames[=<n>]`: Enable rename detection with threshold

### Combining Strategies

The `--custom-strategy` option overrides `--strategy` if both are provided:

```bash
# This uses the custom strategy, ignoring --strategy theirs
python3 merge.py --strategy theirs --custom-strategy ignore-all-space /target /repo1 /repo2
```

## Practical Examples

### Example 1: Merging Frontend, Backend, and Docs

```bash
# Scenario: Three separate projects, might have conflicting README files
python3 merge.py --strategy theirs /monorepo ~/projects/frontend ~/projects/backend ~/projects/docs
```

**What happens**:
1. frontend merges into empty /monorepo
   - No conflicts (first merge)
2. backend merges into /monorepo (containing frontend)
   - Conflict on README.md: backend's version wins
3. docs merges into /monorepo (containing frontend + backend)
   - Conflict on README.md: docs' version wins
   
**Final result**: All three projects merged, with docs' README.md

### Example 2: Preserving All Conflicts for Review

```bash
python3 merge.py --strategy ours /monorepo ~/projects/frontend ~/projects/backend ~/projects/docs
```

**What happens**:
- All conflicts are preserved with markers
- You can review the merged repository and resolve conflicts later
- Run `git grep "<<<<<<< HEAD"` to find all conflict markers

### Example 3: Favor Current State for Conflicts

```bash
python3 merge.py --strategy recursive-ours /config-repo ~/team1-config ~/team2-config ~/team3-config
```

**What happens**:
- Non-conflicting entries from all repos are merged
- For conflicts, current state is kept
- Useful when you want new entries but prefer existing values

### Example 4: Ignore Whitespace Differences

```bash
python3 merge.py --custom-strategy ignore-all-space /target ~/repo1 ~/repo2
```

**What happens**:
- Conflicts caused only by whitespace differences are automatically resolved
- Useful when merging code with different formatting styles

## Troubleshooting

### Q: How do I know which repo "won" in a conflict?

Check the commit history:
```bash
cd /target
git log --oneline --graph
```

The most recent merge shows which repo was merged last.

### Q: Can I change strategy for different repos?

Currently, the strategy applies to all repos in a single run. To use different strategies:
```bash
# First merge with one strategy
python3 merge.py --strategy theirs /target ~/repo1 ~/repo2

# Then merge more repos with a different strategy
python3 merge.py --strategy ours /target ~/repo3 ~/repo4
```

### Q: What if I make a mistake?

You can always reset:
```bash
cd /target
git reset --hard <commit-before-merge>
```

Or start fresh by deleting the target directory and running the merge again.

## See Also

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [Git merge documentation](https://git-scm.com/docs/git-merge)
- [Git merge strategies](https://git-scm.com/docs/merge-strategies)
