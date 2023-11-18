from reviveme.db import Base, Session, engine
from reviveme.db.models import User

Base.metadata.create_all(engine)

session = Session()

# Create fake users
test_user_1 = User("john doe", "johndoe@email.com", "password")
test_user_2 = User("john doe 2", "johndoe2@email.com", "password")

session.add(test_user_1)
session.add(test_user_2)

session.commit()
session.close()
