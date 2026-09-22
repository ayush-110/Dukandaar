from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Store
from auth import CurrentMerchant
from models import Product

def get_owned_store(
    store_id: int,
    current_merchant: CurrentMerchant,
    db: Annotated[Session, Depends(get_db)]
) -> Store:
    store = db.query(Store).filter(Store.id == store_id).first()
    if store is None or store.merchant_id != current_merchant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store 

CurrentStore = Annotated[Store, Depends(get_owned_store)]

def get_owned_product(
    product_id: int,
    store: CurrentStore,
    db: Annotated[Session, Depends(get_db)]
) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None or product.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

CurrentProduct = Annotated[Product, Depends(get_owned_product)]