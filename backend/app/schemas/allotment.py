from pydantic import BaseModel


class AllotmentRunResponse(BaseModel):
    scope: str
    allotted: int
    unallotted: list[str]
    results: list[dict]