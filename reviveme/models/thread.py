from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Boolean, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from reviveme.db import db
from .thread_vote import ThreadVote
class Thread(db.Model):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(String(10000))
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="thread")
    author: Mapped["User"] = relationship("User", back_populates="threads")

    @property
    def score(self) -> int:
        upvotes = db.session.execute(
            select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == self.id, ThreadVote.upvote == True)
        ).scalar()
        downvotes = db.session.execute(
            select(func.count("*")).select_from(ThreadVote).where(ThreadVote.thread_id == self.id, ThreadVote.upvote == False)
        ).scalar()
        return upvotes - downvotes

    def __init__(self, author_id: int, title: str, content: str):
        self.author_id = author_id
        self.title = title
        self.content = content

    def __repr__(self):
        return f"<Thread id={self.id!r}, title={self.title!r}, author_id={self.author_id!r}>"
