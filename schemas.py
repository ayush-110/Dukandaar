from pydantic import BaseModel, EmailStr, Field
from decimal import Decimal
from typing import Optional

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

class ProductVariantCreate(BaseModel):
    label: str
    mrp: Decimal
    selling_price: Decimal
    wholesale_price: Optional[Decimal] = None
    stock: int = 0

class ProductVariantOut(BaseModel):
    id: int
    label: str
    mrp: Decimal
    selling_price: Decimal
    wholesale_price: Optional[Decimal]
    stock: int

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    visible_online: bool = True
    visible_whatsapp: bool = True
    visible_wholesale: bool = False
    variants: list[ProductVariantCreate] = Field(min_length=1)

class ProductOut(BaseModel):
    id: int
    store_id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    visible_online: bool = True
    visible_whatsapp: bool = True
    visible_wholesale: bool = False
    variants: list[ProductVariantOut]

    class Config:
        from_attributes = True