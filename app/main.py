from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import repos, issues, commits, pull_requests

app = FastAPI(
    title="GitHub Cloud Connector",
    description="A lightweight connector to interact with the GitHub API via PAT authentication.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repos.router, prefix="/repos", tags=["Repositories"])
app.include_router(issues.router, tags=["Issues"])
app.include_router(commits.router, tags=["Commits"])
app.include_router(pull_requests.router, tags=["Pull Requests"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "GitHub Cloud Connector"}