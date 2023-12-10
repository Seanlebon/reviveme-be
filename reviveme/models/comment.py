from sqlalchemy import ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Union

from reviveme.db import db


class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    content: Mapped[str] = mapped_column(Text)
    parent_id: Mapped[Union[int, None]] = mapped_column(ForeignKey("comments.id"))
    depth: Mapped[int] = mapped_column(Integer, default=1)

    thread: Mapped["Thread"] = relationship("Thread", back_populates="comments")

    def __init__(self, author_id: int, thread_id: int, content: str, parent_id: Union[int, None] = None):
        self.author_id = author_id
        self.thread_id = thread_id
        self.content = content
        self.parent_id = parent_id

        if parent_id is not None:
            parent = db.session.get(Comment, parent_id)
            if parent is None:
                raise ValueError(f"Comment with id {parent_id} does not exist")
            self.depth = parent.depth + 1
        else:
            self.depth = 1

    def __repr__(self):
        return f"<Comment id={self.id!r}, author_id={self.author_id!r}, thread_id={self.thread_id!r} content={self.content!r}>"

    def serialize(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "thread_id": self.thread_id,
            "content": self.content,
        }
