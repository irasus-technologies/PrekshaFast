# app/models/schema.py
from pydantic import BaseModel


class Model(BaseModel):
    id: str
    name: str
    # add other fields here
