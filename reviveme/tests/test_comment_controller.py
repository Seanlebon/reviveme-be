import pytest

from . import client, app, app_context
from reviveme.db import db
from reviveme.models import Thread, User, Comment

@pytest.mark.usefixtures("client")
@pytest.mark.usefixtures("app_context")
class TestCommentController:
    @pytest.fixture()
    def user(self) -> User:
        user = User(
            username="johndoe",
            email="john.doe@test.com",
            password="password",
            salt="salt"
        )

        db.session.add(user)
        db.session.commit()
        return user

    @pytest.fixture()
    def thread(self, user) -> Thread:
        thread = Thread(
            author_id=user.id,
            title="Test Thread",
            content="Test Content"
        )

        db.session.add(thread)
        db.session.commit()
        return thread
    
    @pytest.fixture()
    def threads(self, user):
        threads = [
            Thread(
                author_id=user.id,
                title="Test Thread",
                content="Test Content"
            ),
            Thread(
                author_id=user.id,
                title="Test Thread 2",
                content="Test Content 2"
            )
        ]

        db.session.add_all(threads)
        db.session.commit()
        return threads
    
    @pytest.fixture()
    def comment(self, user, thread):
        comment = Comment(
            author_id=user.id,
            thread_id=thread.id,
            content="Test Comment"
        )

        db.session.add(comment)
        db.session.commit()
        return comment
    
    # two comments on one thread
    @pytest.fixture()
    def comments(self, user, thread):
        comments = [
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment"
            ),
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 2"
            )
        ]

        db.session.add_all(comments)
        db.session.commit()
        return comments
    
    @pytest.fixture()
    def comments_on_multiple_threads(self, user, threads):
        comments = [
            Comment(
                author_id=user.id,
                thread_id=threads[0].id,
                content="Test Comment"
            ),
            Comment(
                author_id=user.id,
                thread_id=threads[1].id,
                content="Test Comment 2"
            ),
            Comment(
                author_id=user.id,
                thread_id=threads[1].id,
                content="Test Comment 3"
            )
        ]

        db.session.add_all(comments)
        db.session.commit()
        return comments

    def test_list_comments(self, client, comments):
        response = client.get(f'/api/v1/threads/{comments[0].thread.id}/comments')
        assert response.status_code == 200
        assert response.json == [ comment.serialize() for comment in comments ]

    def list_comments_multiple_threads(self, client, comments_on_multiple_threads):
        response = client.get(f'/api/v1/threads/{comments_on_multiple_threads[0].thread.id}/comments')
        assert response.status_code == 200
        assert response.json == [ comments_on_multiple_threads[0].serialize() ]

        response = client.get(f'/api/v1/threads/{comments_on_multiple_threads[1].thread.id}/comments')
        assert response.status_code == 200
        assert response.json == [ comment.serialize() for comment in comments_on_multiple_threads[1:] ]

    def test_list_comments_404(self, client):
        response = client.get('/api/v1/threads/1/comments')
        assert response.status_code == 404
    
    def test_get_comment(self, client, comment):
        response = client.get(f'/api/v1/comments/{comment.id}')
        assert response.status_code == 200
        assert response.json == comment.serialize()

    def test_get_comment_404(self, client):
        response = client.get('/api/v1/comments/1')
        assert response.status_code == 404

    def test_create_comment(self, client, thread):
        response = client.post(f'/api/v1/threads/{thread.id}/comments', json={
            "content": "Test Comment"
        })
        assert response.status_code == 201

        comment = db.session.query(Comment).filter_by(thread_id=thread.id).first()
        assert comment is not None
        assert comment.content == "Test Comment"

    def test_create_comment_404(self, client):
        response = client.post('/api/v1/threads/1/comments', json={
            "content": "Test Comment"
        })
        assert response.status_code == 404

    def test_update_comment(self, client, comment):
        response = client.put(f'/api/v1/comments/{comment.id}', json={
            "content": "Updated Comment"
        })
        assert response.status_code == 200

        comment = db.session.query(Comment).filter_by(id=comment.id).first()
        assert comment is not None
        assert comment.content == "Updated Comment"

    def test_update_comment_404(self, client):
        response = client.put('/api/v1/comments/1', json={
            "content": "Updated Comment"
        })
        assert response.status_code == 404

    def test_delete_comment(self, client, comment):
        response = client.delete(f'/api/v1/comments/{comment.id}')
        assert response.status_code == 200

        assert comment.deleted == True

        resp = client.get(f'/api/v1/comments/{comment.id}')
        assert resp.status_code == 200
        assert resp.json["deleted"] == True
        assert resp.json["content"] == None
        assert resp.json["author_id"] == None
    
    def test_delete_comment_404(self, client):
        response = client.delete('/api/v1/comments/1')
        assert response.status_code == 404
