from sqlalchemy.orm import DeclarativeBase

class BaseModel(DeclarativeBase):
    def serialize(self):
        raise NotImplementedError
    
    @classmethod
    def deserialize(obj):
        raise NotImplementedError
