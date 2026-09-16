import re
from sqlalchemy.orm import Session
from models import Store

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def generate_unique_slug(db: Session, name: str) -> str:
    base_slug = slugify(name)
    slug = base_slug
    counter = 2
    while db.query(Store).filter(Store.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


