from fastapi import APIRouter, Query
from app.services.github import list_issues, create_issue
from app.models.schemas import CreateIssueRequest, IssueResponse

router = APIRouter()


@router.get(
    "/list-issues/{owner}/{repo}",
    response_model=list[IssueResponse],
    summary="List issues in a repository",
)
def get_issues(
    owner: str,
    repo: str,
    state: str = Query("open", pattern="^(open|closed|all)$", description="Issue state"),
    per_page: int = Query(30, ge=1, le=100),
):
    """List issues (excluding pull requests) for a given repository."""
    return list_issues(owner, repo, state=state, per_page=per_page)


@router.post(
    "/create-issue/{owner}/{repo}",
    response_model=IssueResponse,
    status_code=201,
    summary="Create a new issue in a repository",
)
def post_issue(owner: str, repo: str, body: CreateIssueRequest):
    """Create a GitHub issue with a title, optional body, and optional labels."""
    return create_issue(owner, repo, title=body.title, body=body.body, labels=body.labels)