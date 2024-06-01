import pytest
from reviveme.api.v1.thread_controller import ThreadResponseSchema

from reviveme.db import db
from reviveme.models.thread import Thread
from reviveme.models.thread_vote import ThreadVote

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
            ),
            Thread(
                author_id=user.id,
                title="Test Thread 3",
                content="Test Content 3"
            ),
        ]

        db.session.add_all(threads)
        db.session.commit()
        return threads

    @pytest.fixture()
    def threads_with_votes(self, user, threads):
        votes = [
            ThreadVote(user_id=user.id, item_id=threads[0].id, upvote=False),
            ThreadVote(user_id=user.id, item_id=threads[1].id, upvote=True),
        ]
        db.session.add_all(votes)
        db.session.commit()

        return threads

    @pytest.fixture()
    def spaced_out_threads(self, user, threads):
        threads[2].created_at = threads[2].created_at.replace(year=2022)
        threads[1].created_at = threads[1].created_at.replace(year=2021)
        threads[0].created_at = threads[0].created_at.replace(year=2020)
        db.session.commit()
        return threads

    def test_get_threads(self, user, client, threads):
        response = client.get('/api/v1/threads')
        assert response.status_code == 200
        
        schema = ThreadResponseSchema(context={'user_id': user.id})
        for thread, response_thread in zip(threads, response.json):
            assert response_thread == schema.dump(thread)
            assert response_thread['title'] == thread.title
            assert response_thread['content'] == thread.content

    def test_get_threads_sortby_top(self, user, client, threads_with_votes):
        response = client.get('/api/v1/threads?sortby=top')
        assert response.status_code == 200
        
        schema = ThreadResponseSchema(context={'user_id': user.id})
        assert response.json[0] == schema.dump(threads_with_votes[1])
        assert response.json[1] == schema.dump(threads_with_votes[2])
        assert response.json[2] == schema.dump(threads_with_votes[0])

    def test_get_threads_sortby_newest(self, user, client, spaced_out_threads):
        response = client.get('/api/v1/threads?sortby=newest')
        assert response.status_code == 200
        
        schema = ThreadResponseSchema(context={'user_id': user.id})
        assert response.json[0] == schema.dump(spaced_out_threads[2])
        assert response.json[1] == schema.dump(spaced_out_threads[1])
        assert response.json[2] == schema.dump(spaced_out_threads[0])

    def test_get_thread(self, user, client, thread):
        response = client.get(f'/api/v1/threads/{thread.id}')
        assert response.status_code == 200

        schema = ThreadResponseSchema(context={'user_id': user.id})
        assert response.json == schema.dump(thread)
        assert response.json['title'] == thread.title
        assert response.json['content'] == thread.content
        
    def test_get_thread_404(self, client):
        response = client.get('/api/v1/threads/1')
        assert response.status_code == 404

    def test_create_thread(self, client, user):
        response = client.post('/api/v1/threads', json={
            "title": "Test Thread",
            "content": "Test Content",
            "author_id": user.id
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
        assert response.json["author_username"] == None
        assert response.json["title"] == None
        assert response.json["content"] == None

    def test_delete_thread_404(self, client):
        response = client.delete('/api/v1/threads/1')
        assert response.status_code == 404
