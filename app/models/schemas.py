from pydantic import BaseModel, Field


class CreateIssueRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="Issue title")
    body: str = Field("", description="Issue body / description")
    labels: list[str] = Field(default_factory=list, description="Labels to attach")


class IssueResponse(BaseModel):
    number: int
    title: str
    html_url: str
    state: str
    created_at: str


class RepoResponse(BaseModel):
    id: int
    name: str
    full_name: str
    description: str | None
    private: bool
    html_url: str
    language: str | None
    stars: int
    forks: int
    open_issues: int
    updated_at: str


class CommitResponse(BaseModel):
    sha: str
    message: str
    author: str
    date: str
    html_url: str


class CreatePullRequestRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=256, description="PR title")
    head: str = Field(..., description="The branch containing changes (e.g. 'feature/my-branch')")
    base: str = Field(..., description="The branch you want to merge into (e.g. 'main')")
    body: str = Field("", description="PR description / body")
    draft: bool = Field(False, description="Open as a draft PR")


class PullRequestResponse(BaseModel):
    number: int
    title: str
    state: str
    draft: bool
    html_url: str
    head: str
    base: str
    created_at: str
    user: str