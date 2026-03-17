from pydantic import BaseModel
from datetime import date
from typing import Optional

# User schema
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = {
        "from_attribute" : True 
    }       

# Inspections schema
class InspectionBase(BaseModel):
    date: date
    location: str
    item: str
    is_abnormal: bool
    description: Optional[str] = None
    inspection_number: str
    image_url: Optional[str] = None

class InspectionCreate(BaseModel):
    pass

class InspectionUpdate(BaseModel):
    location: Optional[str]
    item: Optional[str]
    is_abnormal: Optional[bool]
    description: Optional[str]

# 系統產生欄位
class InspectionOut(InspectionBase):
    id: int
    created_by: int
    inspection_number: str

    class Config:
        orm_mode = True