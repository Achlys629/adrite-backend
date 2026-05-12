from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.blog import Blog
from app.models.user import User
from app.schemas.blog_schema import BlogCreate, BlogUpdate, BlogResponse

router = APIRouter()

# Admin : Create blog
@router.post("/", response_model=BlogResponse)
def create_blog(
    blog_data: BlogCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check slug is unique
    existing = db.query(Blog).filter(Blog.slug == blog_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    new_blog = Blog(
        title=blog_data.title,
        content=blog_data.content,
        slug=blog_data.slug,
        is_published=blog_data.is_published,
        author_id=current_user.id
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# Public: Get all published blogs
@router.get("/", response_model=List[BlogResponse])
def get_published_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_published == True).all()
    return blogs

# Admin: Get all blogs including unpublished
@router.get("/all", response_model=List[BlogResponse])
def get_all_blogs(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    blogs = db.query(Blog).all()
    return blogs

# Public: Get single blog by slug
@router.get("/slug/{slug}", response_model=BlogResponse)
def get_blog_by_slug(slug: str, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(
        Blog.slug == slug,
        Blog.is_published == True
    ).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

# Get single blog by id
@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

# Admin: Update blog
@router.put("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    update_data: BlogUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if update_data.title:
        blog.title = update_data.title
    if update_data.content:
        blog.content = update_data.content
    if update_data.slug:
        blog.slug = update_data.slug
    if update_data.is_published is not None:
        blog.is_published = update_data.is_published

    db.commit()
    db.refresh(blog)
    return blog

# Admin: Delete blog
@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully"}