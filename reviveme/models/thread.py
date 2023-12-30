from typing import List

from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reviveme.db import db


class Thread(db.Model):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(String(10000))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="thread")
    author: Mapped["User"] = relationship("User", back_populates="threads")

    def __init__(self, author_id: int, title: str, content: str):
        self.author_id = author_id
        self.title = title
        self.content = content

    def __repr__(self):
        return f"<Thread id={self.id!r}, title={self.title!r}, author_id={self.author_id!r}>"

    def serialize(self):
        return {
            "id": self.id,
            "author_username": self.author.username if not self.deleted else None,
            "title": self.title if not self.deleted else None,
            "content": self.content if not self.deleted else None,
            "author_name": self.author.username if not self.deleted else None,
            "deleted": self.deleted,
        }
