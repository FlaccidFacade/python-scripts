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

    def _merge_repo(self, source_repo: Path, subdirectory: Optional[str] = None):
        """
        Merge a single repository into the target.

        Args:
            source_repo: Path to source repository
            subdirectory: Optional subdirectory name in target repo
        """
        repo_name = subdirectory or source_repo.name
        print(f"\nMerging repository: {source_repo.name} -> {repo_name}")

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

        # Move all files to subdirectory if specified
        if subdirectory:
            print(f"  Moving files to subdirectory: {subdirectory}")
            # Create the subdirectory
            (self.target_repo / subdirectory).mkdir(parents=True, exist_ok=True)

            # Move all files except .git to subdirectory
            for item in self.target_repo.iterdir():
                if item.name not in [".git", subdirectory]:
                    dest = self.target_repo / subdirectory / item.name
                    shutil.move(str(item), str(dest))

            # Commit the move
            self._run_command(["git", "add", "-A"], cwd=self.target_repo)
            self._run_command(
                ["git", "commit", "-m", f"Move {repo_name} files to {subdirectory}/ subdirectory"],
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
        print(f"  Merging history...")
        self._run_command(
            ["git", "merge", "--allow-unrelated-histories", "-m", f"Merge {repo_name} repository", merge_branch],
            cwd=self.target_repo
        )

        # Clean up
        self._run_command(
            ["git", "branch", "-d", merge_branch],
            cwd=self.target_repo,
            check=False
        )

        print(f"  ✓ Successfully merged {repo_name}")

    def merge(self, use_subdirectories: bool = True):
        """
        Perform the merge operation.

        Args:
            use_subdirectories: If True, place each repo in its own subdirectory
        """
        print(f"Merging {len(self.source_repos)} repositories into {self.target_repo}")

        # Validate all source repositories
        self._validate_repos()

        # Initialize target repository
        self._initialize_target_repo()

        # Merge each source repository
        for source_repo in self.source_repos:
            subdirectory = source_repo.name if use_subdirectories else None
            self._merge_repo(source_repo, subdirectory)

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
        "--no-subdirectories",
        action="store_true",
        help="Don't place each repository in its own subdirectory (may cause conflicts)"
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
        merger.merge(use_subdirectories=not args.no_subdirectories)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
