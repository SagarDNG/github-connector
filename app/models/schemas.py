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