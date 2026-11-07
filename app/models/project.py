import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(255), nullable=False, default="Untitled Wireframe")
    thumbnail_url = Column(Text, nullable=True, default="")
    ast_json = Column(JSON, nullable=True)
    jsx_code = Column(Text, nullable=True, default="")
    tailwind_code = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title}, user_id={self.user_id})>"
