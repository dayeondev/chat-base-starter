import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False, default="새 커리어 대화")
    aegra_thread_id = Column(String(128), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
