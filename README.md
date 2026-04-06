# GitHub Cloud Connector

A lightweight REST API connector to GitHub, built with **FastAPI** and **Python 3.12**.

Authenticate once with a Personal Access Token and interact with repositories, issues, and commits through clean, documented endpoints.

---

## Features

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/repos/{username}` | GET | List repos for a GitHub user |
| `/list-issues/{owner}/{repo}` | GET | List issues in a repo |
| `/create-issue/{owner}/{repo}` | POST | Create a new issue |
| `/commits/{owner}/{repo}` | GET | Fetch recent commits |
| `/create-pr/{owner}/{repo}` | POST | **[Bonus]** Create a pull request |

---

## Setup

### 1. Clone & enter the project

```bash
git clone https://github.com/SagarDNG/github-connector
cd github-connector
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows
source venv\Scripts\activate  # Liux/Git bash
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your GitHub PAT

Copy the example env file and add your token:

```bash
cp .env.example .env
```

Edit `.env`:

```
GITHUB_PAT=ghp_your_actual_token_here
```

> **Required scopes:** `repo` (or `public_repo` for public repos only)  
> Generate at: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Running with Docker

```bash
docker build -t github-connector .
docker run -p 8000:8000 --env-file .env github-connector
```

---

## Running Tests

```bash
GITHUB_PAT=test_token pytest
```

Tests use mocked HTTP responses — no real GitHub calls or token required.

To see coverage:

```bash
GITHUB_PAT=test_token pytest --cov=app --cov-report=term-missing
```

---

## Example Requests

### List repositories
```bash
curl http://localhost:8000/repos/torvalds
```

### List issues
```bash
curl "http://localhost:8000/list-issues/facebook/react?state=open"
```

### Create an issue
```bash
curl -X POST http://localhost:8000/create-issue/your-username/your-repo \
  -H "Content-Type: application/json" \
  -d '{"title": "Found a bug", "body": "Steps to reproduce...", "labels": ["bug"]}'
```

### Fetch commits
```bash
curl "http://localhost:8000/commits/your-username/your-repo?branch=main"
```

### Create a pull request
```bash
curl -X POST http://localhost:8000/create-pr/your-username/your-repo \
  -H "Content-Type: application/json" \
  -d '{"title": "feat: add login", "head": "feature/login", "base": "main", "body": "Closes #5", "draft": false}'
```

---

## Project Structure

```
github-connector/
├── app/
│   ├── main.py                 # FastAPI app + router registration
│   ├── config.py               # Pydantic settings (reads .env)
│   ├── models/
│   │   └── schemas.py          # Request/response Pydantic models
│   ├── routers/
│   │   ├── repos.py            # /repos endpoints
│   │   ├── issues.py           # /list-issues, /create-issue endpoints
│   │   └── commits.py          # /commits endpoints
│   │   └── pull_requests.py    # /create-pr endpoints
│   └── services/
│       └── github.py           # All GitHub API calls + error handling
├── tests/
│   └── test_connector.py       # Full test suite (25 tests)
├── .gitignore
├── .env
├── .env.example
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **Python 3.12**
- **FastAPI** — REST framework with auto-generated OpenAPI docs
- **httpx** — HTTP client for GitHub API calls
- **Pydantic v2** — request/response validation
- **pytest** — test runner with coverage reporting