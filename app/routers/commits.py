from fastapi import APIRouter, Query
from app.services.github import fetch_commits
from app.models.schemas import CommitResponse

router = APIRouter()


@router.get(
    "/commits/{owner}/{repo}",
    response_model=list[CommitResponse],
    summary="Fetch recent commits from a repository",
)
def get_commits(
    owner: str,
    repo: str,
    branch: str = Query("main", description="Branch name"),
    per_page: int = Query(20, ge=1, le=100),
):
    """Get the latest commits on a given branch of a repository."""
    return fetch_commits(owner, repo, branch=branch, per_page=per_page)