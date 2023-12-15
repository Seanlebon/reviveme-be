import pytest

from reviveme.db import db
from reviveme.models import Thread

class TestThreadController():
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
    
    def test_create_thread_400(self, client, user):
        invalid_inputs = [
            {"title": "Test Thread"},
            {"content": "Test Content"},
            {"title": "Test Thread", "content": "Test Content", "invalid": "invalid"},
            {"title": "", "content": "Test Content"},
        ]

        for inp in invalid_inputs:
            response = client.post('/api/v1/threads', json=inp)
            assert response.status_code == 400

    def test_update_thread(self, client, thread):
        response = client.put(f'/api/v1/threads/{thread.id}', json={
            "title": "Updated Title",
            "content": "Updated Content",
        })
        assert response.status_code == 200

        thread = db.session.get(Thread, thread.id)
        assert thread.title == "Updated Title"
        assert thread.content == "Updated Content"
    
    def test_update_thread_title(self, client, thread):
        response = client.put(f'/api/v1/threads/{thread.id}', json={
            "title": "Updated Title",
        })
        assert response.status_code == 200

        thread = db.session.get(Thread, thread.id)
        assert thread.title == "Updated Title"
        assert thread.content == "Test Content"
    
    def test_update_thread_content(self, client, thread):
        response = client.put(f'/api/v1/threads/{thread.id}', json={
            "content": "Updated Content",
        })
        assert response.status_code == 200

        thread = db.session.get(Thread, thread.id)
        assert thread.title == "Test Thread"
        assert thread.content == "Updated Content"

    def test_update_thread_404(self, client):
        response = client.put('/api/v1/threads/1', json={
            "title": "Updated Title",
            "content": "Updated Content",
        })
        assert response.status_code == 404
    
    def test_update_thread_400(self, client, thread):
        invalid_inputs = [
            {"title": ""},
        ]
        for inp in invalid_inputs:
            response = client.put(f'/api/v1/threads/{thread.id}', json=inp)
            assert response.status_code == 400
            assert thread.title != inp["title"]

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
