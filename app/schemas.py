from pydantic import BaseModel

class postcreate(BaseModel):
    title:str
    content:str