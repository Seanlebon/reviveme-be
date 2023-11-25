from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    def serialize(self):
        raise NotImplementedError

db = SQLAlchemy(model_class=BaseModel)
