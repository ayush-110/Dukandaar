from fastapi import FastAPI
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import Merchant, Store, Product, ProductVariant
from schemas import MerchantCreate, MerchantOut, StoreCreate, StoreOut, SlugAvailability, ProductCreate, ProductOut
from auth import hash_password, verify_password, create_access_token, CurrentMerchant
from utils import generate_unique_slug
from dependencies import CurrentStore, CurrentProduct



app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/signup", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def signup(merchant_in: MerchantCreate, db: Annotated[Session, Depends(get_db)]):
    existing = db.query(Merchant).filter(Merchant.email == merchant_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    merchant = Merchant(
        email = merchant_in.email,
        hashed_password = hash_password(merchant_in.password)
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    merchant = db.query(Merchant).filter(Merchant.email == form_data.username).first()
    if not merchant or not verify_password(form_data.password, merchant.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    token = create_access_token(data={"sub": merchant.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/stores", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
def create_store(
    store_in: StoreCreate,
    current_merchant: CurrentMerchant,
    db: Annotated[Session, Depends(get_db)]
):

    slug = generate_unique_slug(db, store_in.name)
    store = Store(name=store_in.name, slug=slug, merchant_id=current_merchant.id)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store

@app.get("/stores/check-slug", response_model=SlugAvailability)
def check_slug(slug: str, db: Annotated[Session, Depends(get_db)]):
    exists = db.query(Store).filter(Store.slug == slug).first() is not None
    return SlugAvailability(slug=slug, available=not exists)

@app.get("/stores", response_model=list[StoreOut])
def list_my_store(
    current_merchant: CurrentMerchant,
    db: Annotated[Session, Depends(get_db)]
):
    return db.query(Store).filter(Store.merchant_id == current_merchant.id).all()

@app.post("/stores/{store_id}/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    store: CurrentStore,
    product_in: ProductCreate,
    db: Annotated[Session, Depends(get_db)]
):
    product = Product(
        store_id = store.id,
        name = product_in.name,
        description=product_in.description,
        category=product_in.category,
        visible_online=product_in.visible_online,
        visible_whatsapp=product_in.visible_whatsapp,
        visible_wholesale=product_in.visible_wholesale,   
    )

    product.variants = [
        ProductVariant(
            label = v.label,
            mrp = v.mrp,
            selling_price = v.selling_price,
            wholesale_price = v.wholesale_price,
            stock = v.stock
        )
        for v in product_in.variants
    ]

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/stores/{store_id}/products", response_model=list[ProductOut])
def list_products(store: CurrentStore,db: Annotated[Session, Depends(get_db)]):
    return db.query(Product).filter(Product.store_id == store.id).all()


@app.get("/stores/{store_id}/products/{product_id}", response_model=ProductOut)
def get_product(product: CurrentProduct):
    return product

@app.put("/stores/{store_id}/products/{product_id}", response_model=ProductOut)
def update_product(
    product: CurrentProduct,
    product_in: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
):
    product.name = product_in.name
    product.description = product_in.description
    product.category = product_in.category
    product.visible_online = product_in.visible_online
    product.visible_whatsapp = product_in.visible_whatsapp
    product.visible_wholesale = product_in.visible_wholesale

    product.variants.clear()
    product.variants = [
        ProductVariant(
            label=v.label, mrp=v.mrp, selling_price=v.selling_price,
            wholesale_price=v.wholesale_price, stock=v.stock,
        )
        for v in product_in.variants
    ]

    db.commit()
    db.refresh(product)
    return product

@app.delete("/stores/{store_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product: CurrentProduct, db: Annotated[Session, Depends(get_db)]):
    db.delete(product)
    db.commit()