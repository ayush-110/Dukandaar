from pydantic import BaseModel, EmailStr

class MerchantCreate(BaseModel):
    email: EmailStr
    password: str

class MerchantOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class StoreCreate(BaseModel):
    name: str

class StoreOut(BaseModel):
    id: int
    name: str
    slug: str
    merchant_id: int

    class Config:
        from_attributes = True

class SlugAvailability(BaseModel):
    slug: str
    available: bool