from sqlalchemy import Column, Integer, String

from reviveme.db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    # Temporarily using a string for password
    password = Column(
        String(120),
    )

    def __init__(self, name=None, email=None, password=None):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User {self.name!r}>"
