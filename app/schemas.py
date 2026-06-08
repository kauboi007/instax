from pydantic import BaseModel
from fastapi_users import schemas
import uuid
class postcreate(BaseModel):
    title:str
    content:str

class user_read(schemas.BaseUser[uuid.UUID]):
    pass

class user_create(schemas.BaseUserCreate):
    pass

class user_update(schemas.BaseUserUpdate):
    pass