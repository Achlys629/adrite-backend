from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, ProjectResponse
from app.utils.pagination import PaginationParams, paginate_query
from fastapi import UploadFile, File
from app.services.storage_service import StorageService

ALLOWED_DOC_TYPES = ["application/pdf", "image/jpeg", "image/png"]

router = APIRouter()

# Admin: Create project for a client
@router.post("/", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    client_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        budget=project_data.budget,
        deadline=project_data.deadline,
        client_id=client_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# Admin: Get all projects with pagination
@router.get("/")
def get_all_projects(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Project)
    if pagination.search:
        query = query.filter(Project.title.ilike(f"%{pagination.search}%"))
    return paginate_query(query, pagination)

# Client: Get my projects with pagination
@router.get("/my-projects")
def get_my_projects(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Project).filter(Project.client_id == current_user.id)
    if pagination.search:
        query = query.filter(Project.title.ilike(f"%{pagination.search}%"))
    return paginate_query(query, pagination)

# Get single project
@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == UserRole.client and project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return project

# Admin: Update project
@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if update_data.title:
        project.title = update_data.title
    if update_data.description:
        project.description = update_data.description
    if update_data.budget:
        project.budget = update_data.budget
    if update_data.deadline:
        project.deadline = update_data.deadline
    if update_data.status:
        project.status = update_data.status

    db.commit()
    db.refresh(project)
    return project

# Admin: Delete project
@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

# document upload
@router.post("/{project_id}/upload")
async def upload_project_document(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, JPEG, PNG allowed")

    url = StorageService.upload_file(file, folder="projects")
    return {"document_url": url}