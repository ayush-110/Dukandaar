from pydantic import BaseModel, EmailStr

class MerchantCreate(BaseModel):
    email: EmailStr
    password: str

class MerchantOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True