from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from typing import List

from reviveme_server import db

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password: Mapped[str] = mapped_column(String(120))
    salt: Mapped[str] = mapped_column(String(22)) # 22 characters is the exact length of a bcrypt salt

    def __repr__(self):
        return f"<User id={self.id!r}, email={self.email!r}>"
    
class Thread(db.Model):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(String(10000))
    
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="thread")

    def __repr__(self):
        return f"<Thread id={self.id!r}, title={self.title!r}, author_id={self.author_id!r}>"

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    content: Mapped[str] = mapped_column(Text)

    thread: Mapped["Thread"] = relationship("Thread", back_populates="comments")

    def __repr__(self):
        return f"<Comment id={self.id!r}, author_id={self.author_id!r}, thread_id={self.thread_id!r} content={self.content!r}>"
