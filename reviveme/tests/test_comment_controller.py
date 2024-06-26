from datetime import datetime
from typing import List
import pytest
from reviveme.api.v1.comment_controller import CommentResponseSchema

from reviveme.db import db
from reviveme.models.thread import Thread
from reviveme.models.comment import Comment
from reviveme.models.comment_vote import CommentVote

class TestCommentController:
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
    
    # Multiple non-nested comments on one thread
    @pytest.fixture()
    def comments(self, user, thread):
        comments = [
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 1"
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

    # several nested comments on one thread
    @pytest.fixture()
    def nested_comments(self, user, thread):
        top_level_comments = [
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 1"
            ),
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 2"
            )
        ]

        db.session.add_all(top_level_comments)
        db.session.commit()

        child_comments = [
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 1 Reply 1",
                parent_id=top_level_comments[0].id
            ),
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 1 Reply 2",
                parent_id=top_level_comments[0].id
            ),
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 2 Reply 1",
                parent_id=top_level_comments[1].id
            )
        ]
        db.session.add_all(child_comments)
        db.session.commit()

        grandchild_comments = [
            Comment(
                author_id=user.id,
                thread_id=thread.id,
                content="Test Comment 1 Reply 1 Grandchild",
                parent_id=child_comments[0].id
            )
        ]
        db.session.add_all(grandchild_comments)
        db.session.commit()

        # upvote/downvote comments
        votes = [
            CommentVote(user_id=user.id, item_id=top_level_comments[1].id, upvote=True),
            CommentVote(user_id=user.id, item_id=child_comments[1].id, upvote=True),
            CommentVote(user_id=user.id, item_id=child_comments[0].id, upvote=False),
            CommentVote(user_id=user.id, item_id=grandchild_comments[0].id, upvote=True)
        ]
        db.session.add_all(votes)
        db.session.commit()

        return (top_level_comments, child_comments, grandchild_comments)

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

    def test_list_comments(self, user, client, comments):
        response = client.get(f'/api/v1/threads/{comments[0].thread.id}/comments')
        assert response.status_code == 200

        schema = CommentResponseSchema(context={'user_id': user.id})
        for comment, response_comment in zip(comments, response.json):
            assert response_comment == {**schema.dump(comment), 'children': []}
            assert response_comment['content'] == comment.content

    def test_list_comments_multiple_threads(self, user, client, comments_on_multiple_threads):
        response = client.get(f'/api/v1/threads/{comments_on_multiple_threads[0].thread.id}/comments')
        assert response.status_code == 200

        schema = CommentResponseSchema(context={'user_id': user.id})
        assert response.json == [ 
            {**schema.dump(comments_on_multiple_threads[0]), "children": []}
        ]

        response = client.get(f'/api/v1/threads/{comments_on_multiple_threads[1].thread.id}/comments')
        assert response.status_code == 200
        assert response.json == [ 
            {**schema.dump(comment), "children": []} for comment in comments_on_multiple_threads[1:] 
        ]
    
    def test_list_comments_nested(self, user, client, nested_comments):
        top_level_comments, child_comments, grandchild_comments = nested_comments
        response = client.get(f'/api/v1/threads/{top_level_comments[0].thread_id}/comments')
        assert response.status_code == 200

        schema = CommentResponseSchema(context={'user_id': user.id})
        expected_response = [
            {
                **schema.dump(top_level_comments[0]),
                "children": [
                    {
                        **schema.dump(child_comments[0]),
                        "children": [
                            {
                                **schema.dump(grandchild_comments[0]),
                                "children": [],
                            }
                        ],
                    },
                    {
                        **schema.dump(child_comments[1]),
                        "children": [],
                    }
                ],
            },
            {
                **schema.dump(top_level_comments[1]),
                "children": [
                    { 
                        **schema.dump(child_comments[2]), 
                        "children": [], 
                    }
                ],
            }
        ]
        
        assert response.json == expected_response

    def test_list_comments_sort_by_newest(self, user, client, nested_comments):
        top_level_comments, child_comments, grandchild_comments = nested_comments
        response = client.get(f'/api/v1/threads/{top_level_comments[0].thread_id}/comments?sort_by=newest')
        assert response.status_code == 200

        self.verify_sorted_by_newest(response.json)

    def verify_sorted_by_newest(self, comments_json):
        for i in range(1, len(comments_json)):
            assert datetime.fromisoformat(comments_json[i]['created_at']) >= datetime.fromisoformat(comments_json[i - 1]['created_at'])
        
        for comment in comments_json:
            self.verify_sorted_by_newest(comment['children'])
        
    def test_list_comments_sort_by_top(self, user, client, nested_comments):
        top_level_comments, child_comments, grandchild_comments = nested_comments
        response = client.get(f'/api/v1/threads/{top_level_comments[0].thread_id}/comments?sort_by=top')
        assert response.status_code == 200

        self.verify_sorted_by_top(response.json)

    def verify_sorted_by_top(self, comments_json):
        for i in range(1, len(comments_json)):
            assert comments_json[i]['score'] >= comments_json[i - 1]['score']
        
        for comment in comments_json:
            self.verify_sorted_by_top(comment['children'])

    def test_list_comments_404(self, client):
        response = client.get('/api/v1/threads/1/comments')
        assert response.status_code == 404
    
    def test_get_comment(self, user, client, comment):
        response = client.get(f'/api/v1/comments/{comment.id}')
        assert response.status_code == 200
        schema = CommentResponseSchema(context={'user_id': user.id})
        assert response.json == schema.dump(comment)
        assert response.json['content'] == comment.content

    def test_get_comment_404(self, client):
        response = client.get('/api/v1/comments/1')
        assert response.status_code == 404

    def test_create_comment(self, client, thread):
        response = client.post(f'/api/v1/threads/{thread.id}/comments', json={
            "content": "Test Comment",
            "author_id": 1
        })
        assert response.status_code == 201

        comment = db.session.query(Comment).filter_by(thread_id=thread.id).first()
        assert comment is not None
        assert comment.content == "Test Comment"

    def test_create_comment_nested(self, client, thread, comment):
        response = client.post(f'/api/v1/threads/{thread.id}/comments', json={
            "content": "Test Comment",
            "parent_id": comment.id,
            "author_id": 1
        })
        assert response.status_code == 201

        comments = db.session.query(Comment).filter_by(thread_id=thread.id)
        assert comments.count() == 2

        child_comment = comments.filter_by(parent_id=comment.id).first()
        assert child_comment is not None
        assert child_comment.content == "Test Comment"
        assert child_comment.depth == 2

    def test_create_comment_404(self, client):
        response = client.post('/api/v1/threads/1/comments', json={
            "content": "Test Comment"
        })
        assert response.status_code == 404

    def test_create_comment_invalid_parent(self, client, thread):
        response = client.post(f'/api/v1/threads/{thread.id}/comments', json={
            "content": "Test Comment",
            "parent_id": 1
        })
        assert response.status_code == 400

    def test_create_comment_invalid_content(self, client, thread):
        response = client.post(f'/api/v1/threads/{thread.id}/comments', json={
            "content": ""
        })
        assert response.status_code == 400

    def test_update_comment(self, client, comment):
        response = client.put(f'/api/v1/comments/{comment.id}', json={
            "content": "Updated Comment",
            "author_id": 1
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

    def test_update_comment_invalid_content(self, client, comment):
        response = client.put(f'/api/v1/comments/{comment.id}', json={
            "content": ""
        })
        assert response.status_code == 400

    def test_delete_comment(self, client, comment):
        response = client.delete(f'/api/v1/comments/{comment.id}')
        assert response.status_code == 200

        assert comment.deleted == True

        resp = client.get(f'/api/v1/comments/{comment.id}')
        assert resp.status_code == 200
        assert resp.json["deleted"] == True
        assert resp.json["content"] == None
        assert resp.json["author_username"] == None
    
    def test_delete_comment_404(self, client):
        response = client.delete('/api/v1/comments/1')
        assert response.status_code == 404
