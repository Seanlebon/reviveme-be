import pytest

from . import client, app, app_context
from reviveme.db import db
from reviveme.models import Thread, User, Comment

@pytest.mark.usefixtures("client")
@pytest.mark.usefixtures("app_context")
class TestThreadController():
    @pytest.fixture()
    def user(self):
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
    def thread(self, user):
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

    def test_get_threads(self, client, threads):
        response = client.get('/api/v1/threads')
        assert response.status_code == 200
        assert response.json == [thread.serialize() for thread in threads]

    def test_get_thread(self, client, thread):
        response = client.get(f'/api/v1/threads/{thread.id}')
        assert response.status_code == 200
        assert response.json == thread.serialize()

    def test_get_thread_404(self, client):
        response = client.get('/api/v1/threads/1')
        assert response.status_code == 404

    def test_create_thread(self, client, user):
        response = client.post('/api/v1/threads', json={
            "title": "Test Thread",
            "content": "Test Content",
        })
        assert response.status_code == 201

    def test_delete_thread(self, client, thread):
        response = client.delete(f'/api/v1/threads/{thread.id}')
        assert response.status_code == 200

        assert thread.deleted == True
        
        response = client.get(f'/api/v1/threads/{thread.id}')
        assert response.status_code == 200
        assert response.json["deleted"] == True
        assert response.json["author_id"] == None
        assert response.json["author_name"] == None
        assert response.json["title"] == None
        assert response.json["content"] == None

    def test_delete_thread_404(self, client):
        response = client.delete('/api/v1/threads/1')
        assert response.status_code == 404
