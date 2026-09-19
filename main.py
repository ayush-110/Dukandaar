from fastapi import FastAPI
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import Merchant, Store
from schemas import MerchantCreate, MerchantOut, StoreCreate, StoreOut, SlugAvailability
from auth import hash_password, verify_password, create_access_token, CurrentMerchant
from utils import generate_unique_slug



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

