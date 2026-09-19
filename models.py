from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stores = relationship("Store", back_populates="merchant")

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    merchant = relationship("Merchant", back_populates="stores")
    products = relationship("Product", back_populates="store")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    visible_online = Column(Boolean, default=True, nullable=False)
    visible_whatsapp = Column(Boolean, default=True, nullable=False)
    visible_wholesale = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    store = relationship("Store", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    label = Column(String, nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    wholesale_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="variants")
