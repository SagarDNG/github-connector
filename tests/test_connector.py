"""
Test suite for GitHub Cloud Connector.

All tests mock the GitHub API — no real network calls, no real PAT needed.
Set GITHUB_PAT=test_token in the environment (handled automatically via conftest).
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import os

# Ensure env var is set before app import
os.environ.setdefault("GITHUB_PAT", "test_pat_token")

from app.main import app  # noqa: E402

client = TestClient(app)


# ─────────────────────────────────────────────
# Fixtures — reusable mock payloads
# ─────────────────────────────────────────────

@pytest.fixture
def mock_repo():
    return {
        "id": 1,
        "name": "cool-project",
        "full_name": "octocat/cool-project",
        "description": "A cool project",
        "private": False,
        "html_url": "https://github.com/octocat/cool-project",
        "language": "Python",
        "stargazers_count": 42,
        "forks_count": 7,
        "open_issues_count": 3,
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_issue():
    return {
        "number": 99,
        "title": "Bug: something is broken",
        "state": "open",
        "user": {"login": "octocat"},
        "body": "Detailed description here",
        "html_url": "https://github.com/octocat/cool-project/issues/99",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "labels": [],
    }


@pytest.fixture
def mock_commit():
    return {
        "sha": "abc1234efgh",
        "commit": {
            "message": "fix: resolve null pointer\n\nDetailed body",
            "author": {"name": "Sagar", "date": "2024-01-01T00:00:00Z"},
        },
        "html_url": "https://github.com/octocat/cool-project/commit/abc1234efgh",
    }


def _mock_response(payload, status_code=200):
    mock = MagicMock()
    mock.status_code = status_code
    mock.is_success = status_code < 400
    mock.json.return_value = payload
    mock.text = str(payload)
    return mock


# ─────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────

class TestHealth:
    def test_health_check_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "GitHub Cloud Connector" in data["service"]


# ─────────────────────────────────────────────
# GET /repos/{username}
# ─────────────────────────────────────────────

class TestRepos:
    def test_fetch_repos_success(self, mock_repo):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([mock_repo])
            )
            response = client.get("/repos/octocat")

        assert response.status_code == 200
        repos = response.json()
        assert len(repos) == 1
        assert repos[0]["name"] == "cool-project"
        assert repos[0]["stars"] == 42
        assert repos[0]["language"] == "Python"

    def test_fetch_repos_user_not_found(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response({}, 404)
            )
            response = client.get("/repos/nonexistent_user_xyz")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_fetch_repos_unauthorized(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response({}, 401)
            )
            response = client.get("/repos/octocat")

        assert response.status_code == 401
        assert "authentication failed" in response.json()["detail"].lower()

    def test_fetch_repos_pagination_params(self, mock_repo):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_get = mock_client_cls.return_value.__enter__.return_value.get
            mock_get.return_value = _mock_response([mock_repo])
            client.get("/repos/octocat?per_page=10&page=2")
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["per_page"] == 10
            assert kwargs["params"]["page"] == 2

    def test_fetch_repos_invalid_per_page(self):
        response = client.get("/repos/octocat?per_page=0")
        assert response.status_code == 422  # FastAPI validation

    def test_fetch_repos_returns_empty_list(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([])
            )
            response = client.get("/repos/newuser")

        assert response.status_code == 200
        assert response.json() == []


# ─────────────────────────────────────────────
# GET /list-issues/{owner}/{repo}
# ─────────────────────────────────────────────

class TestListIssues:
    def test_list_issues_success(self, mock_issue):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([mock_issue])
            )
            response = client.get("/list-issues/octocat/cool-project")

        assert response.status_code == 200
        issues = response.json()
        assert len(issues) == 1
        assert issues[0]["number"] == 99
        assert issues[0]["title"] == "Bug: something is broken"

    def test_list_issues_filters_out_prs(self, mock_issue):
        pr = {**mock_issue, "pull_request": {"url": "https://api.github.com/repos/..."}}
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([mock_issue, pr])
            )
            response = client.get("/list-issues/octocat/cool-project")

        # PR should be excluded
        assert len(response.json()) == 1

    def test_list_issues_repo_not_found(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response({}, 404)
            )
            response = client.get("/list-issues/octocat/does-not-exist")

        assert response.status_code == 404

    def test_list_issues_invalid_state_param(self):
        response = client.get("/list-issues/octocat/repo?state=invalid")
        assert response.status_code == 422

    def test_list_issues_state_closed(self, mock_issue):
        closed_issue = {**mock_issue, "state": "closed"}
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_get = mock_client_cls.return_value.__enter__.return_value.get
            mock_get.return_value = _mock_response([closed_issue])
            response = client.get("/list-issues/octocat/cool-project?state=closed")
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["state"] == "closed"

        assert response.status_code == 200


# ─────────────────────────────────────────────
# POST /create-issue/{owner}/{repo}
# ─────────────────────────────────────────────

class TestCreateIssue:
    def test_create_issue_success(self, mock_issue):
        created = {**mock_issue, "number": 100, "title": "New bug found"}
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = (
                _mock_response(created, 201)
            )
            response = client.post(
                "/create-issue/octocat/cool-project",
                json={"title": "New bug found", "body": "Steps to reproduce..."},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New bug found"
        assert data["number"] == 100

    def test_create_issue_with_labels(self, mock_issue):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_post = mock_client_cls.return_value.__enter__.return_value.post
            mock_post.return_value = _mock_response(mock_issue, 201)
            client.post(
                "/create-issue/octocat/cool-project",
                json={"title": "Label test", "labels": ["bug", "help wanted"]},
            )
            _, kwargs = mock_post.call_args
            assert "bug" in kwargs["json"]["labels"]

    def test_create_issue_missing_title(self):
        response = client.post(
            "/create-issue/octocat/cool-project",
            json={"body": "No title here"},
        )
        assert response.status_code == 422

    def test_create_issue_empty_title(self):
        response = client.post(
            "/create-issue/octocat/cool-project",
            json={"title": ""},
        )
        assert response.status_code == 422

    def test_create_issue_forbidden(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = (
                _mock_response({}, 403)
            )
            response = client.post(
                "/create-issue/octocat/cool-project",
                json={"title": "Test issue"},
            )
        assert response.status_code == 403

    def test_create_issue_unprocessable_entity_from_github(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.post.return_value = (
                _mock_response({"message": "Validation Failed"}, 422)
            )
            response = client.post(
                "/create-issue/octocat/cool-project",
                json={"title": "Bad issue"},
            )
        assert response.status_code == 422


# ─────────────────────────────────────────────
# GET /commits/{owner}/{repo}
# ─────────────────────────────────────────────

class TestCommits:
    def test_fetch_commits_success(self, mock_commit):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([mock_commit])
            )
            response = client.get("/commits/octocat/cool-project")

        assert response.status_code == 200
        commits = response.json()
        assert len(commits) == 1
        assert commits[0]["sha"] == "abc1234"  # truncated to 7
        assert commits[0]["message"] == "fix: resolve null pointer"  # first line only
        assert commits[0]["author"] == "Sagar"

    def test_fetch_commits_custom_branch(self, mock_commit):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_get = mock_client_cls.return_value.__enter__.return_value.get
            mock_get.return_value = _mock_response([mock_commit])
            client.get("/commits/octocat/cool-project?branch=develop")
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["sha"] == "develop"

    def test_fetch_commits_repo_not_found(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response({}, 404)
            )
            response = client.get("/commits/octocat/missing-repo")

        assert response.status_code == 404

    def test_fetch_commits_empty(self):
        with patch("app.services.github.httpx.Client") as mock_client_cls:
            mock_client_cls.return_value.__enter__.return_value.get.return_value = (
                _mock_response([])
            )
            response = client.get("/commits/octocat/cool-project")

        assert response.status_code == 200
        assert response.json() == []