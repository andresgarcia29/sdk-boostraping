"""
GitHub Service - Client for interacting with GitHub API.

This service provides a Python interface to interact with GitHub repositories,
pull requests, webhooks, branch protection, labels, and comments using PyGithub.
"""

from typing import Optional, List, Dict, Any
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Branch import Branch
from github.Label import Label
from github.IssueComment import IssueComment
from github.Hook import Hook
from github.GithubException import GithubException


class GitHubService:
    """
    Service class for interacting with the GitHub API using PyGithub.

    PyGithub documentation: https://pygithub.readthedocs.io/
    """

    def __init__(
        self,
        token: str,
        base_url: Optional[str] = None,
        verify: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize the GitHub Service.

        Args:
            token: GitHub personal access token or OAuth token
            base_url: Base URL for GitHub Enterprise (optional, defaults to github.com)
            verify: Whether to verify SSL certificates (default: True)
            timeout: Request timeout in seconds (default: 30)

        Raises:
            ValueError: If token is not provided
        """
        if not token:
            raise ValueError("token is required")

        self.token = token
        self.timeout = timeout
        self.verify = verify

        # Initialize PyGithub client
        if base_url:
            self.github = Github(
                base_url=base_url,
                login_or_token=token,
                verify=verify,
                timeout=timeout,
            )
        else:
            self.github = Github(
                login_or_token=token,
                verify=verify,
                timeout=timeout,
            )

    def get_repository(self, owner: str, repo: str) -> Repository:
        """
        Get a repository object.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name

        Returns:
            Repository object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> repo = service.get_repository(owner="octocat", repo="Hello-World")
        """
        return self.github.get_repo(f"{owner}/{repo}")

    def create_webhook(
        self,
        owner: str,
        repo: str,
        url: str,
        content_type: str = "json",
        secret: Optional[str] = None,
        events: Optional[List[str]] = None,
        active: bool = True,
    ) -> Hook:
        """
        Create a webhook for a repository.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            url: Webhook URL to receive events
            content_type: Content type for webhook payloads (default: "json")
            secret: Secret token for webhook (optional)
            events: List of events to subscribe to (optional, defaults to all events)
                    Examples: ["push", "pull_request", "issues", "create"]
            active: Whether the webhook is active (default: True)

        Returns:
            Hook object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> webhook = service.create_webhook(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     url="https://example.com/webhook",
            ...     events=["push", "pull_request"]
            ... )
        """
        repository = self.get_repository(owner, repo)

        config = {
            "url": url,
            "content_type": content_type,
        }

        if secret:
            config["secret"] = secret

        if events is None:
            events = ["*"]

        return repository.create_hook(
            name="web",
            config=config,
            events=events,
            active=active,
        )

    def get_webhooks(self, owner: str, repo: str) -> List[Hook]:
        """
        Get all webhooks for a repository.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name

        Returns:
            List of Hook objects

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> webhooks = service.get_webhooks(owner="octocat", repo="Hello-World")
        """
        repository = self.get_repository(owner, repo)
        return list(repository.get_hooks())

    def delete_webhook(self, owner: str, repo: str, hook_id: int) -> bool:
        """
        Delete a webhook by ID.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            hook_id: Webhook ID to delete

        Returns:
            True if successful

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> service.delete_webhook(owner="octocat", repo="Hello-World", hook_id=123456)
        """
        repository = self.get_repository(owner, repo)
        hook = repository.get_hook(hook_id)
        hook.delete()
        return True

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False,
    ) -> PullRequest:
        """
        Create a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            title: Pull request title
            head: Branch name containing the changes (source branch)
            base: Branch name to merge into (target branch)
            body: Pull request description (optional)
            draft: Whether to create as a draft PR (default: False)

        Returns:
            PullRequest object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> pr = service.create_pull_request(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     title="Add new feature",
            ...     head="feature-branch",
            ...     base="main",
            ...     body="This PR adds a new feature"
            ... )
        """
        repository = self.get_repository(owner, repo)
        return repository.create_pull(
            title=title,
            body=body or "",
            head=head,
            base=base,
            draft=draft,
        )

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> PullRequest:
        """
        Get a pull request by number.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number

        Returns:
            PullRequest object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> pr = service.get_pull_request(owner="octocat", repo="Hello-World", pr_number=1)
        """
        repository = self.get_repository(owner, repo)
        return repository.get_pull(pr_number)

    def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        base: Optional[str] = None,
        head: Optional[str] = None,
    ) -> List[PullRequest]:
        """
        Get pull requests for a repository.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            state: PR state - "open", "closed", or "all" (default: "open")
            base: Filter by base branch (optional)
            head: Filter by head branch (optional)

        Returns:
            List of PullRequest objects

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> prs = service.get_pull_requests(owner="octocat", repo="Hello-World", state="open")
        """
        repository = self.get_repository(owner, repo)
        return list(repository.get_pulls(state=state, base=base, head=head))

    def push_to_pull_request(
        self,
        owner: str,
        repo: str,
        branch: str,
        file_path: str,
        content: str,
        message: str,
        pr_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Push a file to a branch (which may be associated with a pull request).

        This creates or updates a file in the repository branch.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name to push to (should be the PR's head branch)
            file_path: Path to the file in the repository
            content: File content (will be base64 encoded)
            message: Commit message
            pr_number: Optional PR number for reference (not required, but useful for logging)

        Returns:
            Dictionary with commit information

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> result = service.push_to_pull_request(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     branch="feature-branch",
            ...     file_path="src/new_file.py",
            ...     content="# New file content",
            ...     message="Add new file",
            ...     pr_number=1
            ... )
        """
        repository = self.get_repository(owner, repo)

        # Get the branch reference
        ref = repository.get_git_ref(f"heads/{branch}")

        # Get the current commit
        commit = repository.get_git_commit(ref.object.sha)

        # Get the tree
        tree = repository.get_git_tree(commit.tree.sha, recursive=True)

        # Create blob for the new file
        blob = repository.create_git_blob(content, "utf-8")

        # Create new tree entry
        from github import InputGitTreeElement

        tree_elements = []
        for element in tree.tree:
            if element.path != file_path:
                tree_elements.append(
                    InputGitTreeElement(
                        element.path, element.mode, element.type, element.sha
                    )
                )

        tree_elements.append(InputGitTreeElement(file_path, "100644", "blob", blob.sha))

        # Create new tree
        new_tree = repository.create_git_tree(tree_elements, base_tree=tree)

        # Create new commit
        new_commit = repository.create_git_commit(message, new_tree, [commit])

        # Update branch reference
        ref.edit(new_commit.sha)

        return {
            "commit_sha": new_commit.sha,
            "branch": branch,
            "file_path": file_path,
            "message": message,
        }

    def create_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        base_branch: str,
    ) -> Dict[str, Any]:
        """
        Create a new branch from a base branch.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Name of the new branch to create
            base_branch: Name of the base branch to create from (e.g., "main", "master")

        Returns:
            Dictionary with branch information

        Raises:
            ValueError: If base branch is not found or branch already exists

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> result = service.create_branch(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     branch="feature/new-branch",
            ...     base_branch="main"
            ... )
        """
        repository = self.get_repository(owner, repo)

        # Check if branch already exists
        try:
            repository.get_git_ref(f"heads/{branch}")
            raise ValueError(f"Branch '{branch}' already exists")
        except GithubException as e:
            # Branch doesn't exist (404 or similar), which is what we want
            if e.status != 404:
                raise
        except ValueError:
            # Re-raise ValueError if branch exists
            raise

        # Get the base branch reference
        try:
            base_ref = repository.get_git_ref(f"heads/{base_branch}")
        except Exception as e:
            raise ValueError(f"Base branch '{base_branch}' not found: {e}")

        # Create new branch from base branch
        repository.create_git_ref(f"refs/heads/{branch}", base_ref.object.sha)

        return {
            "branch": branch,
            "base_branch": base_branch,
            "commit_sha": base_ref.object.sha,
        }

    def push_files_to_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: Dict[str, str],
        message: str,
    ) -> Dict[str, Any]:
        """
        Push multiple files to a branch.

        This method commits multiple files to an existing branch in a single commit.
        The branch must already exist.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Name of the branch to push files to
            files: Dictionary mapping file paths to file contents
                   Example: {"src/file1.py": "content1", "src/file2.py": "content2"}
            message: Commit message

        Returns:
            Dictionary with commit information

        Raises:
            ValueError: If branch is not found

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> result = service.push_files_to_branch(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     branch="feature/new-branch",
            ...     files={
            ...         "src/file1.py": "# File 1 content",
            ...         "src/file2.py": "# File 2 content",
            ...         "docs/README.md": "# Documentation"
            ...     },
            ...     message="Add new files"
            ... )
        """
        repository = self.get_repository(owner, repo)

        # Get the branch reference
        try:
            branch_ref = repository.get_git_ref(f"heads/{branch}")
        except Exception as e:
            raise ValueError(f"Branch '{branch}' not found: {e}")

        # Get the current commit
        commit = repository.get_git_commit(branch_ref.object.sha)

        # Get the current tree
        tree = repository.get_git_tree(commit.tree.sha, recursive=True)

        # Create blobs for all files
        from github import InputGitTreeElement

        file_paths = set(files.keys())
        tree_elements = []

        # Keep existing tree elements that are not being updated
        for element in tree.tree:
            if element.path not in file_paths:
                tree_elements.append(
                    InputGitTreeElement(
                        element.path, element.mode, element.type, element.sha
                    )
                )

        # Create blobs and add new/updated files to tree
        for file_path, content in files.items():
            blob = repository.create_git_blob(content, "utf-8")
            tree_elements.append(
                InputGitTreeElement(file_path, "100644", "blob", blob.sha)
            )

        # Create new tree
        new_tree = repository.create_git_tree(tree_elements, base_tree=tree)

        # Create new commit
        new_commit = repository.create_git_commit(message, new_tree, [commit])

        # Update branch reference
        branch_ref.edit(new_commit.sha)

        return {
            "commit_sha": new_commit.sha,
            "branch": branch,
            "files": list(files.keys()),
            "message": message,
        }

    def update_branch_protection(
        self,
        owner: str,
        repo: str,
        branch: str,
        required_status_checks: Optional[Dict[str, Any]] = None,
        enforce_admins: bool = False,
        required_pull_request_reviews: Optional[Dict[str, Any]] = None,
        restrictions: Optional[Dict[str, Any]] = None,
        allow_force_pushes: bool = False,
        allow_deletions: bool = False,
    ) -> Branch:
        """
        Update branch protection rules.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name to protect
            required_status_checks: Status checks configuration (optional)
                Example: {"strict": True, "contexts": ["ci/tests"]}
            enforce_admins: Enforce protection rules for admins (default: False)
            required_pull_request_reviews: PR review requirements (optional)
                Example: {
                    "required_approving_review_count": 1,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True
                }
            restrictions: Branch restrictions (optional)
                Example: {"users": ["user1"], "teams": ["team1"]}
            allow_force_pushes: Allow force pushes (default: False)
            allow_deletions: Allow branch deletion (default: False)

        Returns:
            Branch object with updated protection

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> branch = service.update_branch_protection(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     branch="main",
            ...     required_pull_request_reviews={
            ...         "required_approving_review_count": 1,
            ...         "dismiss_stale_reviews": True
            ...     },
            ...     enforce_admins=True
            ... )
        """
        repository = self.get_repository(owner, repo)
        branch_obj = repository.get_branch(branch)

        branch_obj.protect(
            user_push_restrictions=restrictions.get("users", [])
            if restrictions
            else None,
            team_push_restrictions=restrictions.get("teams", [])
            if restrictions
            else None,
            required_status_checks=required_status_checks,
            enforce_admins=enforce_admins,
            required_pull_request_reviews=required_pull_request_reviews,
            allow_force_pushes=allow_force_pushes,
            allow_deletions=allow_deletions,
        )

        return branch_obj

    def get_branch_protection(
        self, owner: str, repo: str, branch: str
    ) -> Dict[str, Any]:
        """
        Get branch protection rules.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name

        Returns:
            Dictionary with protection rules

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> protection = service.get_branch_protection(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     branch="main"
            ... )
        """
        repository = self.get_repository(owner, repo)
        branch_obj = repository.get_branch(branch)

        protection = branch_obj.get_protection()

        return {
            "required_status_checks": protection.required_status_checks,
            "enforce_admins": protection.enforce_admins,
            "required_pull_request_reviews": protection.required_pull_request_reviews,
            "restrictions": protection.restrictions,
        }

    def create_label(
        self,
        owner: str,
        repo: str,
        name: str,
        color: str,
        description: Optional[str] = None,
    ) -> Label:
        """
        Create a label in the repository.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            name: Label name
            color: Label color in hex format (e.g., "FF0000" for red)
            description: Label description (optional)

        Returns:
            Label object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> label = service.create_label(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     name="bug",
            ...     color="d73a4a",
            ...     description="Something isn't working"
            ... )
        """
        repository = self.get_repository(owner, repo)
        return repository.create_label(name=name, color=color, description=description)

    def get_labels(self, owner: str, repo: str) -> List[Label]:
        """
        Get all labels for a repository.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name

        Returns:
            List of Label objects

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> labels = service.get_labels(owner="octocat", repo="Hello-World")
        """
        repository = self.get_repository(owner, repo)
        return list(repository.get_labels())

    def add_label_to_pull_request(
        self, owner: str, repo: str, pr_number: int, label_name: str
    ) -> bool:
        """
        Add a label to a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            label_name: Label name to add

        Returns:
            True if successful

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> service.add_label_to_pull_request(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     pr_number=1,
            ...     label_name="bug"
            ... )
        """
        repository = self.get_repository(owner, repo)
        pr = repository.get_pull(pr_number)
        pr.add_to_labels(label_name)
        return True

    def remove_label_from_pull_request(
        self, owner: str, repo: str, pr_number: int, label_name: str
    ) -> bool:
        """
        Remove a label from a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            label_name: Label name to remove

        Returns:
            True if successful

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> service.remove_label_from_pull_request(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     pr_number=1,
            ...     label_name="bug"
            ... )
        """
        repository = self.get_repository(owner, repo)
        pr = repository.get_pull(pr_number)
        pr.remove_from_labels(label_name)
        return True

    def get_pull_request_labels(
        self, owner: str, repo: str, pr_number: int
    ) -> List[Label]:
        """
        Get all labels for a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of Label objects

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> labels = service.get_pull_request_labels(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     pr_number=1
            ... )
        """
        repository = self.get_repository(owner, repo)
        pr = repository.get_pull(pr_number)
        return list(pr.get_labels())

    def create_pull_request_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        body: str,
        commit_id: Optional[str] = None,
        path: Optional[str] = None,
        line: Optional[int] = None,
        side: Optional[str] = None,
    ) -> IssueComment:
        """
        Create a comment on a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            body: Comment body text
            commit_id: Commit SHA for line comments (optional)
            path: File path for line comments (optional)
            line: Line number for line comments (optional)
            side: Side of the diff for line comments - "LEFT" or "RIGHT" (optional)

        Returns:
            IssueComment object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> comment = service.create_pull_request_comment(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     pr_number=1,
            ...     body="This looks good!"
            ... )
        """
        repository = self.get_repository(owner, repo)
        pr = repository.get_pull(pr_number)

        # If commit_id, path, and line are provided, create a review comment
        if commit_id and path and line is not None:
            return pr.create_review_comment(
                body=body, commit_id=commit_id, path=path, line=line, side=side
            )
        else:
            # Otherwise, create a regular PR comment
            return pr.create_issue_comment(body)

    def get_pull_request_comments(
        self, owner: str, repo: str, pr_number: int
    ) -> List[IssueComment]:
        """
        Get all comments for a pull request.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number

        Returns:
            List of IssueComment objects

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> comments = service.get_pull_request_comments(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     pr_number=1
            ... )
        """
        repository = self.get_repository(owner, repo)
        pr = repository.get_pull(pr_number)
        return list(pr.get_issue_comments())

    def update_pull_request_comment(
        self,
        owner: str,
        repo: str,
        comment_id: int,
        body: str,
    ) -> IssueComment:
        """
        Update a pull request comment.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            comment_id: Comment ID to update
            body: New comment body text

        Returns:
            Updated IssueComment object

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> comment = service.update_pull_request_comment(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     comment_id=123456,
            ...     body="Updated comment"
            ... )
        """
        repository = self.get_repository(owner, repo)
        comment = repository.get_issue_comment(comment_id)
        return comment.edit(body)

    def delete_pull_request_comment(
        self, owner: str, repo: str, comment_id: int
    ) -> bool:
        """
        Delete a pull request comment.

        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            comment_id: Comment ID to delete

        Returns:
            True if successful

        Example:
            >>> service = GitHubService(token="ghp_xxx")
            >>> service.delete_pull_request_comment(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     comment_id=123456
            ... )
        """
        repository = self.get_repository(owner, repo)
        comment = repository.get_issue_comment(comment_id)
        comment.delete()
        return True
