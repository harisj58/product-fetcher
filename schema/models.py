from pydantic import BaseModel


class SearchRequest(BaseModel):
    country: str
    query: str
