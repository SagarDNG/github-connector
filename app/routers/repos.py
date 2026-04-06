from fastapi import APIRouter, Query
from app.services.github import fetch_repos
from app.models.schemas import RepoResponse

router = APIRouter()


@router.get(
    "/{username}",
    response_model=list[RepoResponse],
    summary="List repositories for a GitHub user",
)
def get_repos(
    username: str,
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    page: int = Query(1, ge=1, description="Page number"),
):
    """Fetch all public repositories for a given GitHub username, sorted by last updated."""
    return fetch_repos(username, per_page=per_page, page=page)