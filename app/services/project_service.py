from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.project import Project, Task
from app.models.user import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.utils.logger import logger

class ProjectService:

    @staticmethod
    def create_project(project_data: ProjectCreate, client_id: int, db: Session) -> Project:
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
        logger.info(f"Project created: {new_project.title}")
        return new_project

    @staticmethod
    def get_project_by_id(project_id: int, db: Session) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def update_project(project_id: int, update_data: ProjectUpdate, db: Session) -> Project:
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
        logger.info(f"Project updated: {project.title}")
        return project

    @staticmethod
    def delete_project(project_id: int, db: Session) -> bool:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(project)
        db.commit()
        logger.info(f"Project deleted: {project.title}")
        return True

    @staticmethod
    def assign_task(
        project_id: int,
        title: str,
        assigned_to: int,
        db: Session
    ) -> Task:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        task = Task(
            title=title,
            project_id=project_id,
            assigned_to=assigned_to
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task