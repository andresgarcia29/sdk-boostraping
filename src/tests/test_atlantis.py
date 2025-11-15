"""
Tests for Atlantis Service.

Tests cover initialization, authentication, and all API methods.
"""

import pytest
import responses
from unittest.mock import Mock, patch
from requests.exceptions import RequestException, HTTPError

from services.atlantis.atlantis import AtlantisService


class TestAtlantisServiceInit:
    """Test AtlantisService initialization."""

    def test_init_with_token(self):
        """Test initialization with token."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )
        assert service.base_url == "https://atlantis.example.com"
        assert service.timeout == 30
        assert service.verify_ssl is True
        assert service.headers["X-Atlantis-Token"] == "test-token"
        assert service.headers["Authorization"] == "Bearer test-token"
        assert service.auth is None

    def test_init_with_username_password(self):
        """Test initialization with username and password."""
        service = AtlantisService(
            base_url="https://atlantis.example.com",
            username="user",
            password="pass",
        )
        assert service.base_url == "https://atlantis.example.com"
        assert service.auth is not None
        assert "X-Atlantis-Token" not in service.headers

    def test_init_without_auth(self):
        """Test initialization without authentication raises ValueError."""
        with pytest.raises(ValueError, match="Either username/password or token"):
            AtlantisService(base_url="https://atlantis.example.com")

    def test_init_without_base_url(self):
        """Test initialization without base_url raises ValueError."""
        with pytest.raises(ValueError, match="base_url is required"):
            AtlantisService(base_url="", token="test-token")

    def test_init_strips_trailing_slash(self):
        """Test that base_url trailing slash is stripped."""
        service = AtlantisService(
            base_url="https://atlantis.example.com/", token="test-token"
        )
        assert service.base_url == "https://atlantis.example.com"

    def test_init_custom_timeout_and_verify(self):
        """Test initialization with custom timeout and verify_ssl."""
        service = AtlantisService(
            base_url="https://atlantis.example.com",
            token="test-token",
            timeout=60,
            verify_ssl=False,
        )
        assert service.timeout == 60
        assert service.verify_ssl is False


class TestAtlantisServiceMakeRequest:
    """Test _make_request method."""

    @responses.activate
    def test_make_request_success(self):
        """Test successful request."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/test",
            json={"status": "ok"},
            status=200,
        )

        result = service._make_request("GET", "/api/test")
        assert result == {"status": "ok"}

    @responses.activate
    def test_make_request_with_params(self):
        """Test request with query parameters."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/test",
            json={"param": "value"},
            status=200,
        )

        result = service._make_request("GET", "/api/test", params={"key": "value"})
        assert result == {"param": "value"}

    @responses.activate
    def test_make_request_with_json_data(self):
        """Test request with JSON body."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.POST,
            "https://atlantis.example.com/api/test",
            json={"created": True},
            status=200,
        )

        result = service._make_request("POST", "/api/test", json_data={"data": "value"})
        assert result == {"created": True}

    @responses.activate
    def test_make_request_empty_response(self):
        """Test request with empty response (204)."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.DELETE,
            "https://atlantis.example.com/api/test",
            status=204,
        )

        result = service._make_request("DELETE", "/api/test")
        assert result == {}

    @responses.activate
    def test_make_request_http_error(self):
        """Test request that raises HTTPError."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/test",
            status=404,
        )

        with pytest.raises(HTTPError):
            service._make_request("GET", "/api/test")


class TestAtlantisServiceProjects:
    """Test project-related methods."""

    @responses.activate
    def test_get_projects(self):
        """Test getting all projects."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/projects",
            json={"projects": [{"name": "project1"}, {"name": "project2"}]},
            status=200,
        )

        projects = service.get_projects()
        assert len(projects) == 2
        assert projects[0]["name"] == "project1"

    @responses.activate
    def test_get_projects_empty(self):
        """Test getting projects when none exist."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/projects",
            json={"projects": []},
            status=200,
        )

        projects = service.get_projects()
        assert projects == []

    @responses.activate
    def test_get_project(self):
        """Test getting a specific project."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/project?repo=owner%2Frepo",
            json={"name": "project1", "repo": "owner/repo"},
            status=200,
        )

        project = service.get_project(repo="owner/repo")
        assert project["name"] == "project1"

    @responses.activate
    def test_get_project_with_project_and_branch(self):
        """Test getting a project with project and branch parameters."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/project?repo=owner%2Frepo&project=default&branch=main",
            json={"name": "default", "branch": "main"},
            status=200,
        )

        project = service.get_project(
            repo="owner/repo", project="default", branch="main"
        )
        assert project["name"] == "default"

    @responses.activate
    def test_get_project_status(self):
        """Test getting project status."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/project/status?repo=owner%2Frepo",
            json={"locks": [], "plans": [], "applies": []},
            status=200,
        )

        status = service.get_project_status(repo="owner/repo")
        assert "locks" in status
        assert "plans" in status
        assert "applies" in status


class TestAtlantisServiceLocks:
    """Test lock-related methods."""

    @responses.activate
    def test_get_locks(self):
        """Test getting all locks."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/locks",
            json={"locks": [{"id": "lock1"}, {"id": "lock2"}]},
            status=200,
        )

        locks = service.get_locks()
        assert len(locks) == 2

    @responses.activate
    def test_get_locks_with_repo(self):
        """Test getting locks for a specific repository."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/locks?repo=owner%2Frepo",
            json={"locks": [{"id": "lock1"}]},
            status=200,
        )

        locks = service.get_locks(repo="owner/repo")
        assert len(locks) == 1

    @responses.activate
    def test_delete_lock(self):
        """Test deleting a lock."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.DELETE,
            "https://atlantis.example.com/api/locks?id=lock1",
            status=204,
        )

        result = service.delete_lock(lock_id="lock1")
        assert result == {}

    @responses.activate
    def test_delete_lock_with_repo_and_project(self):
        """Test deleting a lock with repo and project."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.DELETE,
            "https://atlantis.example.com/api/locks?id=lock1&repo=owner%2Frepo&project=default",
            status=204,
        )

        result = service.delete_lock(
            lock_id="lock1", repo="owner/repo", project="default"
        )
        assert result == {}


class TestAtlantisServiceEvents:
    """Test event-related methods."""

    @responses.activate
    def test_get_events(self):
        """Test getting events."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/events",
            json={"events": [{"id": "event1"}, {"id": "event2"}]},
            status=200,
        )

        events = service.get_events()
        assert len(events) == 2

    @responses.activate
    def test_get_events_with_limit(self):
        """Test getting events with limit."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/events?limit=5",
            json={"events": [{"id": "event1"}]},
            status=200,
        )

        events = service.get_events(limit=5)
        assert len(events) == 1


class TestAtlantisServiceInfo:
    """Test info-related methods (version, health)."""

    @responses.activate
    def test_get_version(self):
        """Test getting version."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/version",
            json={"version": "1.0.0"},
            status=200,
        )

        version = service.get_version()
        assert version["version"] == "1.0.0"

    @responses.activate
    def test_get_health(self):
        """Test getting health status."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.GET,
            "https://atlantis.example.com/api/health",
            json={"status": "healthy"},
            status=200,
        )

        health = service.get_health()
        assert health["status"] == "healthy"


class TestAtlantisServicePlan:
    """Test plan method."""

    @responses.activate
    def test_plan(self):
        """Test executing a plan."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.POST,
            "https://atlantis.example.com/api/plan",
            json={"status": "planned"},
            status=200,
        )

        paths = [{"Directory": ".", "Workspace": "default"}]
        result = service.plan(
            repository="owner/repo",
            ref="main",
            vcs_type="Github",
            paths=paths,
        )

        assert result["status"] == "planned"
        request_body = responses.calls[0].request.body
        assert "Repository" in request_body.decode()

    @responses.activate
    def test_plan_with_pr_number(self):
        """Test executing a plan with PR number."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.POST,
            "https://atlantis.example.com/api/plan",
            json={"status": "planned"},
            status=200,
        )

        paths = [{"Directory": ".", "Workspace": "default"}]
        result = service.plan(
            repository="owner/repo",
            ref="main",
            vcs_type="Github",
            paths=paths,
            pr_number=1,
        )

        assert result["status"] == "planned"


class TestAtlantisServiceApply:
    """Test apply method."""

    @responses.activate
    def test_apply(self):
        """Test executing an apply."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.POST,
            "https://atlantis.example.com/api/apply",
            json={"status": "applied"},
            status=200,
        )

        paths = [{"Directory": ".", "Workspace": "default"}]
        result = service.apply(
            repository="owner/repo",
            ref="main",
            vcs_type="Github",
            paths=paths,
        )

        assert result["status"] == "applied"

    @responses.activate
    def test_apply_with_pr_number(self):
        """Test executing an apply with PR number."""
        service = AtlantisService(
            base_url="https://atlantis.example.com", token="test-token"
        )

        responses.add(
            responses.POST,
            "https://atlantis.example.com/api/apply",
            json={"status": "applied"},
            status=200,
        )

        paths = [{"Directory": ".", "Workspace": "default"}]
        result = service.apply(
            repository="owner/repo",
            ref="main",
            vcs_type="Github",
            paths=paths,
            pr_number=1,
        )

        assert result["status"] == "applied"
