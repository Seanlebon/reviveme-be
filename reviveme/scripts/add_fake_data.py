from reviveme import create_app
from reviveme.extensions import db
from reviveme.models import Comment, Thread, User

app = create_app()
# TODO: create a migration instead of using create_all for this
with app.app_context():
    # Create or update the database schema
    db.create_all()

    # Add data to the User model
    user1 = User(
        username="john_doe", email="john@example.com", password="123john", salt="test"
    )
    user2 = User(
        username="jane_doe", email="jane@example.com", password="123john", salt="test"
    )

    db.session.add(user1)
    db.session.add(user2)

    db.session.commit()

    print("Data added successfully.")
