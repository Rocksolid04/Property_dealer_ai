from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
    
class UserUpdate(BaseModel):
    name: str
    email: str
    
class UserStatusUpdate(BaseModel):
    is_active: bool