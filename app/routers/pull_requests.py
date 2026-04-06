from fastapi import APIRouter
from app.services.github import create_pull_request
from app.models.schemas import CreatePullRequestRequest, PullRequestResponse

router = APIRouter()


@router.post(
    "/create-pr/{owner}/{repo}",
    response_model=PullRequestResponse,
    status_code=201,
    summary="Create a pull request (Bonus)",
)
def post_pull_request(owner: str, repo: str, body: CreatePullRequestRequest):
    """
    Create a GitHub pull request.

    - **head**: branch with your changes (e.g. `feature/login`)
    - **base**: branch to merge into (e.g. `main`)
    - **draft**: set `true` to open as a draft PR
    """
    return create_pull_request(
        owner,
        repo,
        title=body.title,
        head=body.head,
        base=body.base,
        body=body.body,
        draft=body.draft,
    )