import logging
import os

from flask import Flask
from flask_migrate import upgrade

from config import FLASK_APP
from reviveme import create_app
from reviveme.db import db
from reviveme.models import Comment, Thread, User

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_fake_user_data(app: Flask):
    with app.app_context():
        FAKE_USER_DATA = (
            {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "123john",
                "salt": "test",
            },
            {
                "username": "jane_doe",
                "email": "jane@example.com",
                "password": "123john",
                "salt": "test",
            },
        )
        try:
            for user_data in FAKE_USER_DATA:
                if User.query.filter_by(username=user_data["username"]).first():
                    continue
                db.session.add(User(**user_data))
            db.session.commit()
            logger.info("Fake User data was added to the db")
        except Exception as e:
            logger.info(
                f"There was an error adding fake User data to the database: {e}"
            )


def create_fake_thread_data(app: Flask):
    with app.app_context():
        FAKE_THREAD_DATA = (
            {
                "author_id": User.query.filter_by(username="john_doe").first().id,
                "title": "Johns Thread",
                "content": "Lorem Ipsum...",
            },
            {
                "author_id": User.query.filter_by(username="john_doe").first().id,
                "title": "Johns Thread 2",
                "content": "Lorem Ipsum...",
            },
            {
                "author_id": User.query.filter_by(username="jane_doe").first().id,
                "title": "Janes Thread",
                "content": "Lorem Ipsum...",
            },
        )
        try:
            for thread_data in FAKE_THREAD_DATA:
                if Thread.query.filter_by(title=thread_data["title"]).first():
                    continue
                db.session.add(Thread(**thread_data))
            db.session.commit()
            logger.info("Fake Thread data was added to the db")
        except Exception as e:
            logger.info(
                f"There was an error adding fake Thread data to the database: {e}"
            )


def create_fake_comment_data(app: Flask):
    with app.app_context():
        FAKE_COMMENT_DATA = [
            Comment(
                author_id = User.query.filter_by(username="jane_doe").first().id,
                thread_id = Thread.query.filter_by(title="Johns Thread").first().id,
                content = "This is a comment made by Jane",
            ),
            Comment(
                author_id = User.query.filter_by(username="jane_doe").first().id,
                thread_id = Thread.query.filter_by(title="Johns Thread").first().id,
                content = "This is another comment made by Jane",
            ),
        ]

        try:
            for comment in FAKE_COMMENT_DATA:
                comment_from_db = Comment.query.filter_by(author_id=comment.author_id, content=comment.content, depth=1).first()
                if comment_from_db:
                    FAKE_COMMENT_DATA[0] = comment_from_db
                    continue
                db.session.add(comment)
            db.session.commit()

            FAKE_REPLY_DATA = (
                Comment(
                    author_id = User.query.filter_by(username="john_doe").first().id,
                    thread_id = FAKE_COMMENT_DATA[0].thread_id,
                    content = "This is a reply made by John",
                    parent_id = FAKE_COMMENT_DATA[0].id,
                ),
            )

            for reply in FAKE_REPLY_DATA:
                if Comment.query.filter_by(author_id=reply.author_id, depth=2).first():
                    continue
                db.session.add(reply)
            db.session.commit()
            logger.info("Fake Comment data was added to the db")
        except Exception as e:
            logger.info(
                f"There was an error adding fake Comment data to the database: {e}"
            )


def create_fake_database_data():
    app = create_app()
    model_dir_path = os.getcwd() + "/" + FLASK_APP + "/models/"
    models = set(os.listdir(model_dir_path))
    all_tables_exist = False
    tables_in_db = db.metadata.tables.keys()

    with app.app_context():
        for table in tables_in_db:
            all_tables_exist = True if table in models else False
        if not all_tables_exist:
            db.create_all()

        # Order matters here, comments require a thread, threads require an author(User)
        create_fake_user_data(app)
        create_fake_thread_data(app)
        create_fake_comment_data(app)
        # Update the database schema
        upgrade()
        print("Data added successfully.")


if __name__ == "__main__":
    create_fake_database_data()
