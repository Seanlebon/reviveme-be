from reviveme import create_app
from reviveme.extensions import db
from reviveme.models import Comment, Thread, User

FAKE_USER_DATA = (
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "password": "123john",
        "salt": "test",
    },
    {
        "id": 2,
        "username": "jane_doe",
        "email": "jane@example.com",
        "password": "123john",
        "salt": "test",
    },
)

FAKE_THREAD_DATA = (
    {
        "id": 3,
        "author_id": 1,
        "title": "Johns Thread",
        "content": "Lorem Ipsum...",
    },
)

FAKE_COMMENT_DATA = (
    {
        "id": 4,
        "author_id": 2,
        "thread_id": 3,
        "content": "This is a comment made by Jane",
    },
)


def create_fake_database_data():
    app = create_app()
    with app.app_context():
        # Create or update the database schema
        db.drop_all()
        db.create_all()

        # Add data to the User model
        for user_data in FAKE_USER_DATA:
            if User.query.filter_by(username=user_data["username"]).first():
                continue
            db.session.add(User(**user_data))
        for thread_data in FAKE_THREAD_DATA:
            if Thread.query.filter_by(author_id=thread_data["author_id"]).first():
                continue
            db.session.add(Thread(**thread_data))
        for comment_data in FAKE_COMMENT_DATA:
            if Comment.query.filter_by(author_id=thread_data["author_id"]).first():
                continue
            db.session.add(Comment(**comment_data))
        db.session.commit()
        print("Data added successfully.")


if __name__ == "__main__":
    create_fake_database_data()
