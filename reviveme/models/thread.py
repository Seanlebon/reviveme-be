from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reviveme.extensions import db


class Thread(db.Model):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(String(10000))

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="thread")

    def __repr__(self):
        return f"<Thread id={self.id!r}, title={self.title!r}, author_id={self.author_id!r}>"