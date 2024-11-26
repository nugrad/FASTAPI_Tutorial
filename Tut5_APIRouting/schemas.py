from pydantic import BaseModel
from typing import List

class Blogs(BaseModel):
    id: int
    name: str
    description: str
    author_id: int

    class Config:
        orm_mode = True

class AuthorCreate(BaseModel):
    name: str
    email: str
    password: str

class AuthorResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True
