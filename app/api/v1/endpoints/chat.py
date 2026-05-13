from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.chat import ChatMessage
from app.models.user import User, UserRole
from app.utils.pagination import PaginationParams, paginate_query

from app.schemas.chat_schema import ChatMessageCreate, ChatMessageResponse

router = APIRouter()

# Client: Send message
@router.post("/", response_model=ChatMessageResponse)
def send_message(
    chat_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_message = ChatMessage(
        message=chat_data.message,
        response=None,  # AI will fill this later
        client_id=current_user.id
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

# Client: my chat history with pagination
@router.get("/")
def get_all_chats(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(ChatMessage)
    return paginate_query(query, pagination)

# my chat with pagination
@router.get("/my-chats")
def get_my_chats(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ChatMessage).filter(
        ChatMessage.client_id == current_user.id
    ).order_by(ChatMessage.created_at.asc())
    return paginate_query(query, pagination)

# Admin: Get chats of specific client
@router.get("/client/{client_id}", response_model=List[ChatMessageResponse])
def get_client_chats(
    client_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.client_id == client_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages

# Get single message
@router.get("/{message_id}", response_model=ChatMessageResponse)
def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Client can only see their own messages
    if current_user.role == UserRole.client and message.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return message

# Admin: Delete message
@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    message = db.query(ChatMessage).filter(
        ChatMessage.id == message_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()
    return {"message": "Message deleted successfully"}