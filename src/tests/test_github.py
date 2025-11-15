"""
Tests for GitHub Service.

Tests cover initialization, repository operations, pull requests, webhooks,
branch protection, labels, and comments.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Branch import Branch
from github.Label import Label
from github.IssueComment import IssueComment
from github.Hook import Hook
from github.GithubException import GithubException

from services.github.github import GitHubService


class TestGitHubServiceInit:
    """Test GitHubService initialization."""

    @patch("services.github.github.Github")
    def test_init_with_token(self, mock_github_class):
        """Test initialization with token."""
        mock_github_instance = Mock()
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        assert service.token == "ghp_test123"
        assert service.timeout == 30
        assert service.verify is True
        mock_github_class.assert_called_once_with(
            login_or_token="ghp_test123", verify=True, timeout=30
        )

    @patch("services.github.github.Github")
    def test_init_with_base_url(self, mock_github_class):
        """Test initialization with base_url (GitHub Enterprise)."""
        mock_github_instance = Mock()
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(
            token="ghp_test123", base_url="https://github.example.com/api/v3"
        )
        mock_github_class.assert_called_once_with(
            base_url="https://github.example.com/api/v3",
            login_or_token="ghp_test123",
            verify=True,
            timeout=30,
        )

    @patch("services.github.github.Github")
    def test_init_without_token(self, mock_github_class):
        """Test initialization without token raises ValueError."""
        with pytest.raises(ValueError, match="token is required"):
            GitHubService(token="")

    @patch("services.github.github.Github")
    def test_init_custom_timeout_and_verify(self, mock_github_class):
        """Test initialization with custom timeout and verify."""
        mock_github_instance = Mock()
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123", timeout=60, verify=False)
        assert service.timeout == 60
        assert service.verify is False


class TestGitHubServiceRepository:
    """Test repository-related methods."""

    @patch("services.github.github.Github")
    def test_get_repository(self, mock_github_class):
        """Test getting a repository."""
        mock_repo = Mock(spec=Repository)
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        repo = service.get_repository(owner="octocat", repo="Hello-World")

        assert repo == mock_repo
        mock_github_instance.get_repo.assert_called_once_with("octocat/Hello-World")


class TestGitHubServiceWebhooks:
    """Test webhook-related methods."""

    @patch("services.github.github.Github")
    def test_create_webhook(self, mock_github_class):
        """Test creating a webhook."""
        mock_hook = Mock(spec=Hook)
        mock_repo = Mock(spec=Repository)
        mock_repo.create_hook.return_value = mock_hook
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        webhook = service.create_webhook(
            owner="octocat",
            repo="Hello-World",
            url="https://example.com/webhook",
            events=["push", "pull_request"],
        )

        assert webhook == mock_hook
        mock_repo.create_hook.assert_called_once()
        call_kwargs = mock_repo.create_hook.call_args[1]
        assert call_kwargs["name"] == "web"
        assert call_kwargs["config"]["url"] == "https://example.com/webhook"
        assert call_kwargs["events"] == ["push", "pull_request"]

    @patch("services.github.github.Github")
    def test_create_webhook_with_secret(self, mock_github_class):
        """Test creating a webhook with secret."""
        mock_hook = Mock(spec=Hook)
        mock_repo = Mock(spec=Repository)
        mock_repo.create_hook.return_value = mock_hook
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        webhook = service.create_webhook(
            owner="octocat",
            repo="Hello-World",
            url="https://example.com/webhook",
            secret="secret123",
        )

        call_kwargs = mock_repo.create_hook.call_args[1]
        assert call_kwargs["config"]["secret"] == "secret123"

    @patch("services.github.github.Github")
    def test_get_webhooks(self, mock_github_class):
        """Test getting all webhooks."""
        mock_hooks = [Mock(spec=Hook), Mock(spec=Hook)]
        mock_repo = Mock(spec=Repository)
        mock_repo.get_hooks.return_value = mock_hooks
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        webhooks = service.get_webhooks(owner="octocat", repo="Hello-World")

        assert len(webhooks) == 2
        assert webhooks == mock_hooks

    @patch("services.github.github.Github")
    def test_delete_webhook(self, mock_github_class):
        """Test deleting a webhook."""
        mock_hook = Mock(spec=Hook)
        mock_repo = Mock(spec=Repository)
        mock_repo.get_hook.return_value = mock_hook
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.delete_webhook(owner="octocat", repo="Hello-World", hook_id=123)

        assert result is True
        mock_hook.delete.assert_called_once()


class TestGitHubServicePullRequests:
    """Test pull request-related methods."""

    @patch("services.github.github.Github")
    def test_create_pull_request(self, mock_github_class):
        """Test creating a pull request."""
        mock_pr = Mock(spec=PullRequest)
        mock_repo = Mock(spec=Repository)
        mock_repo.create_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        pr = service.create_pull_request(
            owner="octocat",
            repo="Hello-World",
            title="Test PR",
            head="feature-branch",
            base="main",
            body="PR description",
        )

        assert pr == mock_pr
        mock_repo.create_pull.assert_called_once_with(
            title="Test PR",
            body="PR description",
            head="feature-branch",
            base="main",
            draft=False,
        )

    @patch("services.github.github.Github")
    def test_create_pull_request_draft(self, mock_github_class):
        """Test creating a draft pull request."""
        mock_pr = Mock(spec=PullRequest)
        mock_repo = Mock(spec=Repository)
        mock_repo.create_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        pr = service.create_pull_request(
            owner="octocat",
            repo="Hello-World",
            title="Test PR",
            head="feature-branch",
            base="main",
            draft=True,
        )

        call_kwargs = mock_repo.create_pull.call_args[1]
        assert call_kwargs["draft"] is True

    @patch("services.github.github.Github")
    def test_get_pull_request(self, mock_github_class):
        """Test getting a pull request."""
        mock_pr = Mock(spec=PullRequest)
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        pr = service.get_pull_request(owner="octocat", repo="Hello-World", pr_number=1)

        assert pr == mock_pr
        mock_repo.get_pull.assert_called_once_with(1)

    @patch("services.github.github.Github")
    def test_get_pull_requests(self, mock_github_class):
        """Test getting pull requests."""
        mock_prs = [Mock(spec=PullRequest), Mock(spec=PullRequest)]
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pulls.return_value = mock_prs
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        prs = service.get_pull_requests(
            owner="octocat", repo="Hello-World", state="open"
        )

        assert len(prs) == 2
        mock_repo.get_pulls.assert_called_once_with(state="open", base=None, head=None)

    @patch("services.github.github.Github")
    def test_get_pull_requests_with_filters(self, mock_github_class):
        """Test getting pull requests with base and head filters."""
        mock_prs = [Mock(spec=PullRequest)]
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pulls.return_value = mock_prs
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        prs = service.get_pull_requests(
            owner="octocat",
            repo="Hello-World",
            state="open",
            base="main",
            head="feature-branch",
        )

        mock_repo.get_pulls.assert_called_once_with(
            state="open", base="main", head="feature-branch"
        )


class TestGitHubServiceBranchOperations:
    """Test branch-related operations."""

    @patch("services.github.github.Github")
    @patch("github.InputGitTreeElement")
    def test_push_to_pull_request(self, mock_tree_element, mock_github_class):
        """Test pushing a file to a branch."""
        # Setup mocks
        mock_blob = Mock()
        mock_blob.sha = "blob_sha"
        mock_tree_element_instance = Mock()
        mock_tree_element.return_value = mock_tree_element_instance

        mock_tree = Mock()
        mock_tree.tree = [Mock(path="other_file.py", mode="100644", type="blob", sha="old_sha")]

        mock_commit = Mock()
        mock_commit.tree.sha = "tree_sha"
        mock_commit.sha = "commit_sha"

        mock_ref = Mock()
        mock_ref.object.sha = "ref_sha"

        mock_new_tree = Mock()
        mock_new_commit = Mock()
        mock_new_commit.sha = "new_commit_sha"

        mock_repo = Mock(spec=Repository)
        mock_repo.get_git_ref.return_value = mock_ref
        mock_repo.get_git_commit.return_value = mock_commit
        mock_repo.get_git_tree.return_value = mock_tree
        mock_repo.create_git_blob.return_value = mock_blob
        mock_repo.create_git_tree.return_value = mock_new_tree
        mock_repo.create_git_commit.return_value = mock_new_commit

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.push_to_pull_request(
            owner="octocat",
            repo="Hello-World",
            branch="feature-branch",
            file_path="src/new_file.py",
            content="# New file",
            message="Add new file",
            pr_number=1,
        )

        assert result["commit_sha"] == "new_commit_sha"
        assert result["branch"] == "feature-branch"
        assert result["file_path"] == "src/new_file.py"
        mock_ref.edit.assert_called_once_with("new_commit_sha")

    @patch("services.github.github.Github")
    def test_create_branch(self, mock_github_class):
        """Test creating a new branch."""
        mock_base_ref = Mock()
        mock_base_ref.object.sha = "base_sha"

        mock_repo = Mock(spec=Repository)
        mock_repo.get_git_ref.side_effect = [
            GithubException(404, "Not found"),  # Branch doesn't exist
            mock_base_ref,  # Base branch exists
        ]
        mock_repo.create_git_ref = Mock()

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.create_branch(
            owner="octocat",
            repo="Hello-World",
            branch="feature/new-branch",
            base_branch="main",
        )

        assert result["branch"] == "feature/new-branch"
        assert result["base_branch"] == "main"
        assert result["commit_sha"] == "base_sha"
        mock_repo.create_git_ref.assert_called_once_with(
            "refs/heads/feature/new-branch", "base_sha"
        )

    @patch("services.github.github.Github")
    def test_create_branch_already_exists(self, mock_github_class):
        """Test creating a branch that already exists raises ValueError."""
        mock_ref = Mock()
        mock_repo = Mock(spec=Repository)
        # First call (checking if branch exists) returns the ref (branch exists)
        # This should raise ValueError
        mock_repo.get_git_ref.return_value = mock_ref

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        with pytest.raises(ValueError, match="already exists"):
            service.create_branch(
                owner="octocat",
                repo="Hello-World",
                branch="existing-branch",
                base_branch="main",
            )

    @patch("services.github.github.Github")
    def test_create_branch_base_not_found(self, mock_github_class):
        """Test creating a branch with non-existent base raises ValueError."""
        mock_repo = Mock(spec=Repository)
        mock_repo.get_git_ref.side_effect = [
            GithubException(404, "Not found"),  # Branch doesn't exist (good)
            GithubException(404, "Not found"),  # Base branch doesn't exist (bad)
        ]

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        with pytest.raises(ValueError, match="Base branch"):
            service.create_branch(
                owner="octocat",
                repo="Hello-World",
                branch="new-branch",
                base_branch="nonexistent",
            )

    @patch("services.github.github.Github")
    @patch("github.InputGitTreeElement")
    def test_push_files_to_branch(self, mock_tree_element, mock_github_class):
        """Test pushing multiple files to a branch."""
        mock_blob = Mock()
        mock_blob.sha = "blob_sha"
        mock_tree_element_instance = Mock()
        mock_tree_element.return_value = mock_tree_element_instance

        mock_tree = Mock()
        mock_tree.tree = [Mock(path="other_file.py", mode="100644", type="blob", sha="old_sha")]

        mock_commit = Mock()
        mock_commit.tree.sha = "tree_sha"

        mock_branch_ref = Mock()
        mock_branch_ref.object.sha = "ref_sha"

        mock_new_tree = Mock()
        mock_new_commit = Mock()
        mock_new_commit.sha = "new_commit_sha"

        mock_repo = Mock(spec=Repository)
        mock_repo.get_git_ref.return_value = mock_branch_ref
        mock_repo.get_git_commit.return_value = mock_commit
        mock_repo.get_git_tree.return_value = mock_tree
        mock_repo.create_git_blob.return_value = mock_blob
        mock_repo.create_git_tree.return_value = mock_new_tree
        mock_repo.create_git_commit.return_value = mock_new_commit

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.push_files_to_branch(
            owner="octocat",
            repo="Hello-World",
            branch="feature-branch",
            files={"file1.py": "content1", "file2.py": "content2"},
            message="Add files",
        )

        assert result["commit_sha"] == "new_commit_sha"
        assert result["branch"] == "feature-branch"
        assert len(result["files"]) == 2
        assert "file1.py" in result["files"]
        assert "file2.py" in result["files"]

    @patch("services.github.github.Github")
    def test_push_files_to_branch_not_found(self, mock_github_class):
        """Test pushing files to non-existent branch raises ValueError."""
        mock_repo = Mock(spec=Repository)
        mock_repo.get_git_ref.side_effect = GithubException(404, "Not found")

        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        with pytest.raises(ValueError, match="Branch"):
            service.push_files_to_branch(
                owner="octocat",
                repo="Hello-World",
                branch="nonexistent",
                files={"file.py": "content"},
                message="Add file",
            )


class TestGitHubServiceBranchProtection:
    """Test branch protection methods."""

    @patch("services.github.github.Github")
    def test_update_branch_protection(self, mock_github_class):
        """Test updating branch protection."""
        mock_branch = Mock(spec=Branch)
        mock_branch.protect = Mock()  # Add protect method explicitly
        mock_repo = Mock(spec=Repository)
        mock_repo.get_branch.return_value = mock_branch
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.update_branch_protection(
            owner="octocat",
            repo="Hello-World",
            branch="main",
            required_pull_request_reviews={"required_approving_review_count": 1},
            enforce_admins=True,
        )

        assert result == mock_branch
        mock_branch.protect.assert_called_once()

    @patch("services.github.github.Github")
    def test_get_branch_protection(self, mock_github_class):
        """Test getting branch protection."""
        mock_protection = Mock()
        mock_protection.required_status_checks = {"strict": True}
        mock_protection.enforce_admins = True
        mock_protection.required_pull_request_reviews = {"count": 1}
        mock_protection.restrictions = {"users": []}

        mock_branch = Mock(spec=Branch)
        mock_branch.get_protection.return_value = mock_protection
        mock_repo = Mock(spec=Repository)
        mock_repo.get_branch.return_value = mock_branch
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        protection = service.get_branch_protection(
            owner="octocat", repo="Hello-World", branch="main"
        )

        assert "required_status_checks" in protection
        assert "enforce_admins" in protection
        assert "required_pull_request_reviews" in protection
        assert "restrictions" in protection


class TestGitHubServiceLabels:
    """Test label-related methods."""

    @patch("services.github.github.Github")
    def test_create_label(self, mock_github_class):
        """Test creating a label."""
        mock_label = Mock(spec=Label)
        mock_repo = Mock(spec=Repository)
        mock_repo.create_label.return_value = mock_label
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        label = service.create_label(
            owner="octocat",
            repo="Hello-World",
            name="bug",
            color="d73a4a",
            description="Something isn't working",
        )

        assert label == mock_label
        mock_repo.create_label.assert_called_once_with(
            name="bug", color="d73a4a", description="Something isn't working"
        )

    @patch("services.github.github.Github")
    def test_get_labels(self, mock_github_class):
        """Test getting all labels."""
        mock_labels = [Mock(spec=Label), Mock(spec=Label)]
        mock_repo = Mock(spec=Repository)
        mock_repo.get_labels.return_value = mock_labels
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        labels = service.get_labels(owner="octocat", repo="Hello-World")

        assert len(labels) == 2
        assert labels == mock_labels

    @patch("services.github.github.Github")
    def test_add_label_to_pull_request(self, mock_github_class):
        """Test adding a label to a pull request."""
        mock_pr = Mock(spec=PullRequest)
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.add_label_to_pull_request(
            owner="octocat", repo="Hello-World", pr_number=1, label_name="bug"
        )

        assert result is True
        mock_pr.add_to_labels.assert_called_once_with("bug")

    @patch("services.github.github.Github")
    def test_remove_label_from_pull_request(self, mock_github_class):
        """Test removing a label from a pull request."""
        mock_pr = Mock(spec=PullRequest)
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.remove_label_from_pull_request(
            owner="octocat", repo="Hello-World", pr_number=1, label_name="bug"
        )

        assert result is True
        mock_pr.remove_from_labels.assert_called_once_with("bug")

    @patch("services.github.github.Github")
    def test_get_pull_request_labels(self, mock_github_class):
        """Test getting labels for a pull request."""
        mock_labels = [Mock(spec=Label), Mock(spec=Label)]
        mock_pr = Mock(spec=PullRequest)
        mock_pr.get_labels.return_value = mock_labels
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        labels = service.get_pull_request_labels(
            owner="octocat", repo="Hello-World", pr_number=1
        )

        assert len(labels) == 2
        assert labels == mock_labels


class TestGitHubServiceComments:
    """Test comment-related methods."""

    @patch("services.github.github.Github")
    def test_create_pull_request_comment(self, mock_github_class):
        """Test creating a regular PR comment."""
        mock_comment = Mock(spec=IssueComment)
        mock_pr = Mock(spec=PullRequest)
        mock_pr.create_issue_comment.return_value = mock_comment
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        comment = service.create_pull_request_comment(
            owner="octocat", repo="Hello-World", pr_number=1, body="Great work!"
        )

        assert comment == mock_comment
        mock_pr.create_issue_comment.assert_called_once_with("Great work!")

    @patch("services.github.github.Github")
    def test_create_pull_request_review_comment(self, mock_github_class):
        """Test creating a review comment (line comment)."""
        mock_comment = Mock(spec=IssueComment)
        mock_pr = Mock(spec=PullRequest)
        mock_pr.create_review_comment.return_value = mock_comment
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        comment = service.create_pull_request_comment(
            owner="octocat",
            repo="Hello-World",
            pr_number=1,
            body="Fix this line",
            commit_id="abc123",
            path="src/file.py",
            line=10,
            side="RIGHT",
        )

        assert comment == mock_comment
        mock_pr.create_review_comment.assert_called_once_with(
            body="Fix this line",
            commit_id="abc123",
            path="src/file.py",
            line=10,
            side="RIGHT",
        )

    @patch("services.github.github.Github")
    def test_get_pull_request_comments(self, mock_github_class):
        """Test getting all comments for a pull request."""
        mock_comments = [Mock(spec=IssueComment), Mock(spec=IssueComment)]
        mock_pr = Mock(spec=PullRequest)
        mock_pr.get_issue_comments.return_value = mock_comments
        mock_repo = Mock(spec=Repository)
        mock_repo.get_pull.return_value = mock_pr
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        comments = service.get_pull_request_comments(
            owner="octocat", repo="Hello-World", pr_number=1
        )

        assert len(comments) == 2
        assert comments == mock_comments

    @patch("services.github.github.Github")
    def test_update_pull_request_comment(self, mock_github_class):
        """Test updating a pull request comment."""
        mock_updated_comment = Mock(spec=IssueComment)
        mock_comment = Mock(spec=IssueComment)
        mock_comment.edit.return_value = mock_updated_comment
        mock_repo = Mock(spec=Repository)
        mock_repo.get_issue_comment = Mock(return_value=mock_comment)  # Add method explicitly
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.update_pull_request_comment(
            owner="octocat",
            repo="Hello-World",
            comment_id=123456,
            body="Updated comment",
        )

        assert result == mock_updated_comment
        mock_comment.edit.assert_called_once_with("Updated comment")

    @patch("services.github.github.Github")
    def test_delete_pull_request_comment(self, mock_github_class):
        """Test deleting a pull request comment."""
        mock_comment = Mock(spec=IssueComment)
        mock_repo = Mock(spec=Repository)
        mock_repo.get_issue_comment = Mock(return_value=mock_comment)  # Add method explicitly
        mock_github_instance = Mock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_github_instance

        service = GitHubService(token="ghp_test123")
        result = service.delete_pull_request_comment(
            owner="octocat", repo="Hello-World", comment_id=123456
        )

        assert result is True
        mock_comment.delete.assert_called_once()

