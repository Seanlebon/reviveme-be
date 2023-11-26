from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from reviveme.db import db


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    content: Mapped[str] = mapped_column(Text)

    thread: Mapped["Thread"] = relationship("Thread", back_populates="comments")

    def __init__(self, author_id: int, thread_id: int, content: str):
        self.author_id = author_id
        self.thread_id = thread_id
        self.content = content

    def __repr__(self):
        return f"<Comment id={self.id!r}, author_id={self.author_id!r}, thread_id={self.thread_id!r} content={self.content!r}>"

    def serialize(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "thread_id": self.thread_id,
            "content": self.content,
        }
