import httpx
from fastapi import HTTPException
from app.config import settings

GITHUB_API_BASE = "https://api.github.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.github_pat}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _raise_for_status(response: httpx.Response, context: str = "") -> None:
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="GitHub authentication failed. Check your PAT.")
    if response.status_code == 403:
        raise HTTPException(status_code=403, detail="GitHub forbidden. Token may lack required scopes.")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"GitHub resource not found. {context}")
    if response.status_code == 422:
        raise HTTPException(status_code=422, detail=f"Validation error from GitHub: {response.text}")
    if not response.is_success:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"GitHub API error: {response.text}",
        )


# ── Repositories ──────────────────────────────────────────────────────────────

def fetch_repos(username: str, per_page: int = 30, page: int = 1) -> list[dict]:
    url = f"{GITHUB_API_BASE}/users/{username}/repos"
    params = {"per_page": per_page, "page": page, "sort": "updated"}
    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), params=params)
    _raise_for_status(response, f"User '{username}' not found.")
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "full_name": r["full_name"],
            "description": r["description"],
            "private": r["private"],
            "html_url": r["html_url"],
            "language": r["language"],
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "open_issues": r["open_issues_count"],
            "updated_at": r["updated_at"],
        }
        for r in response.json()
    ]


# ── Issues ────────────────────────────────────────────────────────────────────

def list_issues(owner: str, repo: str, state: str = "open", per_page: int = 30) -> list[dict]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    params = {"state": state, "per_page": per_page}
    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), params=params)
    _raise_for_status(response, f"Repo '{owner}/{repo}' not found.")
    return [
        {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "user": i["user"]["login"],
            "body": i.get("body", ""),
            "html_url": i["html_url"],
            "created_at": i["created_at"],
            "updated_at": i["updated_at"],
            "labels": [lbl["name"] for lbl in i.get("labels", [])],
        }
        for i in response.json()
        if "pull_request" not in i  # exclude PRs from issue list
    ]


def create_issue(owner: str, repo: str, title: str, body: str = "", labels: list[str] | None = None) -> dict:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues"
    payload: dict = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    with httpx.Client() as client:
        response = client.post(url, headers=_headers(), json=payload)
    _raise_for_status(response, f"Could not create issue in '{owner}/{repo}'.")
    i = response.json()
    return {
        "number": i["number"],
        "title": i["title"],
        "html_url": i["html_url"],
        "state": i["state"],
        "created_at": i["created_at"],
    }


# ── Commits ───────────────────────────────────────────────────────────────────

def fetch_commits(owner: str, repo: str, branch: str = "main", per_page: int = 20) -> list[dict]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits"
    params = {"sha": branch, "per_page": per_page}
    with httpx.Client() as client:
        response = client.get(url, headers=_headers(), params=params)
    _raise_for_status(response, f"Repo '{owner}/{repo}' or branch '{branch}' not found.")
    return [
        {
            "sha": c["sha"][:7],
            "message": c["commit"]["message"].split("\n")[0],
            "author": c["commit"]["author"]["name"],
            "date": c["commit"]["author"]["date"],
            "html_url": c["html_url"],
        }
        for c in response.json()
    ]