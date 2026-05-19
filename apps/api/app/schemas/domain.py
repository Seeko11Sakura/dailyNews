from pydantic import BaseModel


class Domain(BaseModel):
    id: str
    name: str
    emoji: str
