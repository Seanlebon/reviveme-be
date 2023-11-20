from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from reviveme.extensions import db


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password: Mapped[str] = mapped_column(String(120))
    salt: Mapped[str] = mapped_column(
        String(22)
    )  # 22 characters is the exact length of a bcrypt salt

    def __repr__(self):
        return f"<User id={self.id!r}, email={self.email!r}>"
