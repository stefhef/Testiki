from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, backref

from core.db import Base


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="refresh_token")
