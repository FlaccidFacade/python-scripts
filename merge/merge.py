#!/usr/bin/env python3
"""
Merge multiple git repositories into a single repository.

This script merges the content and git history of multiple source repositories
into a single target repository, preserving all commits and history.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


class RepoMerger:
    """Handles merging of multiple git repositories into one."""

    def __init__(self, target_repo: str, source_repos: List[str], verbose: bool = False):
        """
        Initialize the RepoMerger.

        Args:
            target_repo: Path to the target repository (can be new or existing)
            source_repos: List of paths to source repositories to merge
            verbose: Enable verbose output
        """
        self.target_repo = Path(target_repo).resolve()
        self.source_repos = [Path(repo).resolve() for repo in source_repos]
        self.verbose = verbose

    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and handle errors."""
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
            if cwd:
                print(f"  in: {cwd}")

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            print(f"Error running command: {' '.join(cmd)}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)

        return result

    def _validate_repos(self):
        """Validate that all source repositories exist and are git repositories."""
        for repo in self.source_repos:
            if not repo.exists():
                raise ValueError(f"Source repository does not exist: {repo}")
            if not (repo / ".git").exists():
                raise ValueError(f"Not a git repository: {repo}")

    def _initialize_target_repo(self):
        """Initialize target repository if it doesn't exist."""
        if not self.target_repo.exists():
            print(f"Creating target repository: {self.target_repo}")
            self.target_repo.mkdir(parents=True, exist_ok=True)
            self._run_command(["git", "init"], cwd=self.target_repo)
            self._run_command(["git", "config", "user.email", "merge@example.com"], cwd=self.target_repo)
            self._run_command(["git", "config", "user.name", "Repo Merger"], cwd=self.target_repo)
        elif not (self.target_repo / ".git").exists():
            raise ValueError(f"Target path exists but is not a git repository: {self.target_repo}")

    def _merge_repo(self, source_repo: Path, strategy: str = "ours"):
        """
        Merge a single repository into the target.

        Args:
            source_repo: Path to source repository
            strategy: Conflict resolution strategy ('ours', 'theirs', or 'manual')
        """
        repo_name = source_repo.name
        print(f"\nMerging repository: {source_repo.name}")

        # Add the source repository as a remote
        remote_name = f"source_{repo_name}"
        self._run_command(
            ["git", "remote", "add", remote_name, str(source_repo)],
            cwd=self.target_repo,
            check=False  # Don't fail if remote already exists
        )

        # Fetch the source repository
        print(f"  Fetching from {source_repo.name}...")
        self._run_command(
            ["git", "fetch", remote_name],
            cwd=self.target_repo
        )

        # Get the default branch of the source repo
        result = self._run_command(
            ["git", "symbolic-ref", "refs/remotes/" + remote_name + "/HEAD"],
            cwd=self.target_repo,
            check=False
        )

        if result.returncode == 0:
            default_branch = result.stdout.strip().split("/")[-1]
        else:
            # Fallback to main/master
            result = self._run_command(
                ["git", "branch", "-r"],
                cwd=self.target_repo
            )
            branches = result.stdout.strip().split("\n")
            if any("main" in b for b in branches):
                default_branch = "main"
            elif any("master" in b for b in branches):
                default_branch = "master"
            else:
                # Use the first branch found
                default_branch = branches[0].strip().split("/")[-1] if branches else "master"

        print(f"  Using branch: {default_branch}")

        # Create a temporary branch for merging
        merge_branch = f"merge_{repo_name}"

        # Check out the remote branch to a local branch
        self._run_command(
            ["git", "checkout", "-b", merge_branch, f"{remote_name}/{default_branch}"],
            cwd=self.target_repo,
            check=False
        )

        # Switch back to main branch
        result = self._run_command(
            ["git", "rev-parse", "--verify", "main"],
            cwd=self.target_repo,
            check=False
        )

        if result.returncode != 0:
            # Create main branch if it doesn't exist
            self._run_command(
                ["git", "checkout", "-b", "main"],
                cwd=self.target_repo
            )
        else:
            self._run_command(
                ["git", "checkout", "main"],
                cwd=self.target_repo
            )

        # Merge the temporary branch with allow-unrelated-histories
        print(f"  Merging history with strategy: {strategy}...")
        
        merge_cmd = ["git", "merge", "--allow-unrelated-histories"]
        
        if strategy == "ours":
            # Strategy A: Keep all changes, leave conflicts unresolved
            merge_cmd.extend(["-m", f"Merge {repo_name} repository", merge_branch])
            result = self._run_command(merge_cmd, cwd=self.target_repo, check=False)
            
            if result.returncode != 0:
                # Check if there are conflicts
                status_result = self._run_command(
                    ["git", "status", "--porcelain"],
                    cwd=self.target_repo
                )
                if any(line.startswith("UU") or line.startswith("AA") or line.startswith("DD") for line in status_result.stdout.split("\n")):
                    print(f"  ⚠ Merge conflicts detected. Adding all changes and committing with conflicts.")
                    # Add all files (both conflicted and non-conflicted)
                    self._run_command(["git", "add", "-A"], cwd=self.target_repo)
                    # Commit with conflicts marked
                    self._run_command(
                        ["git", "commit", "--no-edit", "-m", f"Merge {repo_name} repository with conflicts"],
                        cwd=self.target_repo,
                        check=False
                    )
                else:
                    # If it's not a conflict, re-raise the error
                    raise subprocess.CalledProcessError(result.returncode, merge_cmd)
        
        elif strategy == "theirs":
            # Strategy B: Keep all latest changes (from source repo)
            merge_cmd.extend(["-X", "theirs", "-m", f"Merge {repo_name} repository", merge_branch])
            self._run_command(merge_cmd, cwd=self.target_repo)
        
        elif strategy == "manual":
            # Strategy C: Open prompt for user to resolve conflicts
            merge_cmd.extend(["-m", f"Merge {repo_name} repository", merge_branch])
            result = self._run_command(merge_cmd, cwd=self.target_repo, check=False)
            
            if result.returncode != 0:
                # Check if there are conflicts
                status_result = self._run_command(
                    ["git", "status", "--porcelain"],
                    cwd=self.target_repo
                )
                if any(line.startswith("UU") or line.startswith("AA") or line.startswith("DD") for line in status_result.stdout.split("\n")):
                    print(f"\n  ⚠ Merge conflicts detected!")
                    print(f"  Please resolve the conflicts manually.")
                    print(f"  After resolving, run:")
                    print(f"    cd {self.target_repo}")
                    print(f"    git add <resolved-files>")
                    print(f"    git merge --continue")
                    print(f"\n  Or to abort the merge:")
                    print(f"    git merge --abort")
                    
                    # Wait for user input
                    input("\n  Press Enter after you've resolved the conflicts and completed the merge...")
                    
                    # Verify the merge was completed
                    merge_head = self.target_repo / ".git" / "MERGE_HEAD"
                    if merge_head.exists():
                        raise RuntimeError("Merge was not completed. Please complete or abort the merge before continuing.")
                else:
                    # If it's not a conflict, re-raise the error
                    raise subprocess.CalledProcessError(result.returncode, merge_cmd)

        # Clean up
        self._run_command(
            ["git", "branch", "-d", merge_branch],
            cwd=self.target_repo,
            check=False
        )

        print(f"  ✓ Successfully merged {repo_name}")

    def merge(self, strategy: str = "ours"):
        """
        Perform the merge operation.

        Args:
            strategy: Conflict resolution strategy ('ours', 'theirs', or 'manual')
        """
        print(f"Merging {len(self.source_repos)} repositories into {self.target_repo}")
        print(f"Conflict resolution strategy: {strategy}")

        # Validate all source repositories
        self._validate_repos()

        # Initialize target repository
        self._initialize_target_repo()

        # Merge each source repository
        for source_repo in self.source_repos:
            self._merge_repo(source_repo, strategy)

        print(f"\n✓ Successfully merged all repositories into {self.target_repo}")
        print(f"\nTo view the result:")
        print(f"  cd {self.target_repo}")
        print(f"  git log --oneline --graph --all")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Merge multiple git repositories into a single repository, preserving history."
    )
    parser.add_argument(
        "target_repo",
        help="Path to the target repository (will be created if it doesn't exist)"
    )
    parser.add_argument(
        "source_repos",
        nargs="+",
        help="Paths to source repositories to merge (minimum 1)"
    )
    parser.add_argument(
        "--strategy",
        choices=["ours", "theirs", "manual"],
        default="ours",
        help="Conflict resolution strategy: 'ours' (keep all changes, leave conflicts unresolved), "
             "'theirs' (accept all changes from source repos), 'manual' (prompt user to resolve conflicts)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if len(args.source_repos) < 1:
        print("Error: At least one source repository is required")
        sys.exit(1)

    try:
        merger = RepoMerger(args.target_repo, args.source_repos, verbose=args.verbose)
        merger.merge(strategy=args.strategy)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
