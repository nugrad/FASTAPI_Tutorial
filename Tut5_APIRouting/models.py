from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class DBBlog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    description = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'))

    writer = relationship("DBAuthor", back_populates="writings")

class DBAuthor(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String, unique=True)
    password = Column(String)

    writings = relationship("DBBlog", back_populates="writer")
