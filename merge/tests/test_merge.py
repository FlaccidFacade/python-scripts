#!/usr/bin/env python3
"""
Tests for merge.py script.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from merge import RepoMerger


class TestRepoMerger:
    """Test suite for RepoMerger class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_repos(self, temp_dir):
        """Create sample git repositories for testing."""
        repos = []
        for i in range(3):
            repo_path = temp_dir / f"repo{i+1}"
            repo_path.mkdir()

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)

            # Create some files
            (repo_path / f"file{i+1}.txt").write_text(f"Content from repo {i+1}\n")
            (repo_path / "README.md").write_text(f"# Repository {i+1}\n")

            # Commit the files
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"Initial commit for repo{i+1}"],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            # Create another commit
            (repo_path / f"file{i+1}_v2.txt").write_text(f"Second file from repo {i+1}\n")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"Second commit for repo{i+1}"],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            repos.append(repo_path)

        return repos

    def test_merger_initialization(self, temp_dir, sample_repos):
        """Test that RepoMerger initializes correctly."""
        target = temp_dir / "target"
        merger = RepoMerger(str(target), [str(r) for r in sample_repos])

        assert merger.target_repo == target
        assert len(merger.source_repos) == 3

    def test_validate_repos_success(self, temp_dir, sample_repos):
        """Test that validation passes for valid repositories."""
        target = temp_dir / "target"
        merger = RepoMerger(str(target), [str(r) for r in sample_repos])

        # Should not raise any exception
        merger._validate_repos()

    def test_validate_repos_nonexistent(self, temp_dir):
        """Test that validation fails for non-existent repositories."""
        target = temp_dir / "target"
        non_existent = temp_dir / "nonexistent"

        merger = RepoMerger(str(target), [str(non_existent)])

        with pytest.raises(ValueError, match="does not exist"):
            merger._validate_repos()

    def test_validate_repos_not_git(self, temp_dir):
        """Test that validation fails for non-git directories."""
        target = temp_dir / "target"
        not_git = temp_dir / "not_git"
        not_git.mkdir()

        merger = RepoMerger(str(target), [str(not_git)])

        with pytest.raises(ValueError, match="Not a git repository"):
            merger._validate_repos()

    def test_initialize_target_repo_new(self, temp_dir):
        """Test initialization of a new target repository."""
        target = temp_dir / "new_target"
        merger = RepoMerger(str(target), [])

        merger._initialize_target_repo()

        assert target.exists()
        assert (target / ".git").exists()

    def test_initialize_target_repo_existing(self, temp_dir):
        """Test initialization with existing target repository."""
        target = temp_dir / "existing_target"
        target.mkdir()
        subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)

        merger = RepoMerger(str(target), [])

        # Should not raise any exception
        merger._initialize_target_repo()

        assert target.exists()
        assert (target / ".git").exists()

    def test_merge_with_subdirectories(self, temp_dir, sample_repos):
        """Test merging repositories with subdirectories."""
        target = temp_dir / "merged"
        merger = RepoMerger(str(target), [str(r) for r in sample_repos], verbose=True)

        merger.merge(use_subdirectories=True)

        # Verify target repository exists
        assert target.exists()
        assert (target / ".git").exists()

        # Verify subdirectories were created
        for repo in sample_repos:
            assert (target / repo.name).exists()

        # Verify files exist in subdirectories
        assert (target / "repo1" / "file1.txt").exists()
        assert (target / "repo2" / "file2.txt").exists()
        assert (target / "repo3" / "file3.txt").exists()

        # Verify git history
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True
        )
        # Should have commits from all repos
        assert "repo1" in result.stdout or "Initial commit" in result.stdout
        assert len(result.stdout.split("\n")) > 3  # At least multiple commits

    def test_merge_without_subdirectories(self, temp_dir, sample_repos):
        """Test merging repositories without subdirectories can cause conflicts."""
        target = temp_dir / "merged_flat"
        merger = RepoMerger(str(target), [str(r) for r in sample_repos], verbose=True)

        # This should fail due to file conflicts (README.md exists in all repos)
        # This is expected behavior and demonstrates why subdirectories are recommended
        with pytest.raises(subprocess.CalledProcessError):
            merger.merge(use_subdirectories=False)

    def test_merge_preserves_history(self, temp_dir, sample_repos):
        """Test that merge preserves git history from all repos."""
        target = temp_dir / "merged_history"
        merger = RepoMerger(str(target), [str(r) for r in sample_repos])

        merger.merge(use_subdirectories=True)

        # Get full git log
        result = subprocess.run(
            ["git", "log", "--all", "--oneline"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True
        )

        log_output = result.stdout
        # Each repo had 2 commits, plus merge commits
        # We should see evidence of the original commits
        assert len(log_output.split("\n")) >= 6  # At least 6 commits total

    def test_merge_single_repo(self, temp_dir, sample_repos):
        """Test merging a single repository."""
        target = temp_dir / "merged_single"
        merger = RepoMerger(str(target), [str(sample_repos[0])])

        merger.merge(use_subdirectories=True)

        # Verify target repository exists
        assert target.exists()
        assert (target / ".git").exists()
        assert (target / sample_repos[0].name / "file1.txt").exists()

    def test_run_command_success(self, temp_dir):
        """Test _run_command with successful command."""
        merger = RepoMerger(str(temp_dir / "target"), [])
        result = merger._run_command(["echo", "test"])

        assert result.returncode == 0
        assert "test" in result.stdout

    def test_run_command_failure(self, temp_dir):
        """Test _run_command with failing command."""
        merger = RepoMerger(str(temp_dir / "target"), [])

        with pytest.raises(subprocess.CalledProcessError):
            merger._run_command(["false"], check=True)


def test_main_module_import():
    """Test that the module can be imported."""
    import merge
    assert hasattr(merge, "RepoMerger")
    assert hasattr(merge, "main")
