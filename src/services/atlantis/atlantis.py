"""
Atlantis Service - Client for interacting with Atlantis API.

Atlantis is a tool for automating Terraform workflows via pull requests.
This service provides a Python interface to interact with the Atlantis API.
"""

import requests
from typing import Optional, Dict, Any, List
from requests.auth import HTTPBasicAuth


class AtlantisService:
    """
    Service class for interacting with the Atlantis API.

    Atlantis API documentation: https://www.runatlantis.io/docs/api.html
    """

    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        verify_ssl: bool = True,
        timeout: int = 30,
    ):
        """
        Initialize the Atlantis Service.

        Args:
            base_url: Base URL of the Atlantis server (e.g., 'https://atlantis.example.com')
            username: Username for basic authentication (optional if token is provided)
            password: Password for basic authentication (optional if token is provided)
            token: API token for authentication (optional if username/password are provided)
            verify_ssl: Whether to verify SSL certificates (default: True)
            timeout: Request timeout in seconds (default: 30)

        Raises:
            ValueError: If neither authentication method is provided
        """
        if not base_url:
            raise ValueError("base_url is required")

        if not username and not password and not token:
            raise ValueError(
                "Either username/password or token must be provided for authentication"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Set up authentication
        self.auth = None
        self.headers = {}

        if token:
            # For plan/apply endpoints, use X-Atlantis-Token header
            # For other endpoints, Bearer token may also work
            self.headers["X-Atlantis-Token"] = token
            self.headers["Authorization"] = f"Bearer {token}"
        elif username and password:
            self.auth = HTTPBasicAuth(username, password)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Atlantis API.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (e.g., '/api/projects')
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response JSON as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            auth=self.auth,
            headers=self.headers,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

        response.raise_for_status()

        # Handle empty responses
        if response.status_code == 204 or not response.text:
            return {}

        return response.json()

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects from Atlantis.

        Returns:
            List of project dictionaries

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> projects = service.get_projects()
        """
        response = self._make_request("GET", "/api/projects")
        return response.get("projects", [])

    def get_project(
        self, repo: str, project: Optional[str] = None, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a specific project from Atlantis.

        Args:
            repo: Repository identifier (e.g., 'owner/repo')
            project: Project name (optional)
            branch: Branch name (optional)

        Returns:
            Project dictionary

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> project = service.get_project(repo="owner/repo", project="default")
        """
        params = {"repo": repo}
        if project:
            params["project"] = project
        if branch:
            params["branch"] = branch

        response = self._make_request("GET", "/api/project", params=params)
        return response

    def get_project_status(
        self, repo: str, project: Optional[str] = None, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the status of a project (locks, plans, applies).

        Args:
            repo: Repository identifier (e.g., 'owner/repo')
            project: Project name (optional)
            branch: Branch name (optional)

        Returns:
            Status dictionary containing locks, plans, and applies
        """
        params = {"repo": repo}
        if project:
            params["project"] = project
        if branch:
            params["branch"] = branch

        response = self._make_request("GET", "/api/project/status", params=params)
        return response

    def get_locks(self, repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all locks or locks for a specific repository.

        Args:
            repo: Repository identifier (optional, if not provided returns all locks)

        Returns:
            List of lock dictionaries

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> locks = service.get_locks(repo="owner/repo")
        """
        params = {}
        if repo:
            params["repo"] = repo

        response = self._make_request("GET", "/api/locks", params=params)
        return response.get("locks", [])

    def delete_lock(
        self, lock_id: str, repo: Optional[str] = None, project: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a lock by ID.

        Args:
            lock_id: Lock ID to delete
            repo: Repository identifier (optional, for validation)
            project: Project name (optional, for validation)

        Returns:
            Response dictionary

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> service.delete_lock(lock_id="abc-123")
        """
        params = {"id": lock_id}
        if repo:
            params["repo"] = repo
        if project:
            params["project"] = project

        return self._make_request("DELETE", "/api/locks", params=params)

    def get_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent events from Atlantis.

        Args:
            limit: Maximum number of events to return (optional)

        Returns:
            List of event dictionaries

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> events = service.get_events(limit=10)
        """
        params = {}
        if limit:
            params["limit"] = limit

        response = self._make_request("GET", "/api/events", params=params)
        return response.get("events", [])

    def get_version(self) -> Dict[str, Any]:
        """
        Get Atlantis server version information.

        Returns:
            Version dictionary

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> version = service.get_version()
        """
        return self._make_request("GET", "/api/version")

    def get_health(self) -> Dict[str, Any]:
        """
        Get Atlantis server health status.

        Returns:
            Health status dictionary

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> health = service.get_health()
        """
        return self._make_request("GET", "/api/health")

    def plan(
        self,
        repository: str,
        ref: str,
        vcs_type: str,
        paths: List[Dict[str, str]],
        pr_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Terraform plan operation via Atlantis.

        Args:
            repository: Repository identifier (e.g., 'owner/repo')
            ref: Git reference (branch name or commit SHA)
            vcs_type: VCS provider type (e.g., 'Github', 'Gitlab', 'Bitbucket')
            paths: List of dictionaries specifying directories and workspaces.
                   Each dict should contain 'Directory' and/or 'Workspace' keys.
                   Example: [{"Directory": ".", "Workspace": "default"}]
            pr_number: Pull request number (optional)

        Returns:
            Response dictionary from Atlantis API

        Raises:
            requests.exceptions.RequestException: If the request fails

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> paths = [{"Directory": ".", "Workspace": "default"}]
            >>> response = service.plan(
            ...     repository="owner/repo",
            ...     ref="main",
            ...     vcs_type="Github",
            ...     paths=paths,
            ...     pr_number=1
            ... )

        Note:
            Requires Atlantis to be configured with an api-secret for authentication.
            The token parameter in __init__ should be set to the API secret.
        """
        payload = {
            "Repository": repository,
            "Ref": ref,
            "Type": vcs_type,
            "Paths": paths,
        }

        if pr_number is not None:
            payload["PR"] = pr_number

        return self._make_request("POST", "/api/plan", json_data=payload)

    def apply(
        self,
        repository: str,
        ref: str,
        vcs_type: str,
        paths: List[Dict[str, str]],
        pr_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Terraform apply operation via Atlantis.

        Args:
            repository: Repository identifier (e.g., 'owner/repo')
            ref: Git reference (branch name or commit SHA)
            vcs_type: VCS provider type (e.g., 'Github', 'Gitlab', 'Bitbucket')
            paths: List of dictionaries specifying directories and workspaces.
                   Each dict should contain 'Directory' and/or 'Workspace' keys.
                   Example: [{"Directory": ".", "Workspace": "default"}]
            pr_number: Pull request number (optional)

        Returns:
            Response dictionary from Atlantis API

        Raises:
            requests.exceptions.RequestException: If the request fails

        Example:
            >>> service = AtlantisService(base_url="https://atlantis.example.com", token="abc123")
            >>> paths = [{"Directory": ".", "Workspace": "default"}]
            >>> response = service.apply(
            ...     repository="owner/repo",
            ...     ref="main",
            ...     vcs_type="Github",
            ...     paths=paths,
            ...     pr_number=1
            ... )

        Note:
            Requires Atlantis to be configured with an api-secret for authentication.
            The token parameter in __init__ should be set to the API secret.
        """
        payload = {
            "Repository": repository,
            "Ref": ref,
            "Type": vcs_type,
            "Paths": paths,
        }

        if pr_number is not None:
            payload["PR"] = pr_number

        return self._make_request("POST", "/api/apply", json_data=payload)
