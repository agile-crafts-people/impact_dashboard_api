"""
Unit tests for Comment routes (create-style with POST and GET).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.comment_routes import create_comment_routes


class TestCommentRoutes(unittest.TestCase):
    """Test cases for Comment routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_comment_routes(),
            url_prefix="/api/comment",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.comment_routes.create_flask_token")
    @patch("src.routes.comment_routes.create_flask_breadcrumb")
    @patch("src.routes.comment_routes.CommentService.create_comment")
    @patch("src.routes.comment_routes.CommentService.get_comment")
    def test_create_comment_success(
        self,
        mock_get_comment,
        mock_create_comment,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/comment for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_comment.return_value = "123"
        mock_get_comment.return_value = {
            "_id": "123",
            "name": "test-comment",
            "status": "active",
        }

        response = self.client.post(
            "/api/comment",
            json={"name": "test-comment", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_comment.assert_called_once()
        mock_get_comment.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.comment_routes.create_flask_token")
    @patch("src.routes.comment_routes.create_flask_breadcrumb")
    @patch("src.routes.comment_routes.CommentService.get_comments")
    def test_get_comments_success(
        self,
        mock_get_comments,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/comment for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_comments.return_value = {
            "items": [
                {"_id": "123", "name": "comment1"},
                {"_id": "456", "name": "comment2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/comment")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_comments.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.comment_routes.create_flask_token")
    @patch("src.routes.comment_routes.create_flask_breadcrumb")
    @patch("src.routes.comment_routes.CommentService.get_comment")
    def test_get_comment_success(
        self,
        mock_get_comment,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/comment/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_comment.return_value = {
            "_id": "123",
            "name": "comment1",
        }

        response = self.client.get("/api/comment/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_comment.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.comment_routes.create_flask_token")
    @patch("src.routes.comment_routes.create_flask_breadcrumb")
    @patch("src.routes.comment_routes.CommentService.get_comment")
    def test_get_comment_not_found(
        self,
        mock_get_comment,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/comment/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_comment.side_effect = HTTPNotFound(
            "Comment 999 not found"
        )

        response = self.client.get("/api/comment/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Comment 999 not found")

    @patch("src.routes.comment_routes.create_flask_token")
    def test_create_comment_unauthorized(self, mock_create_token):
        """Test POST /api/comment when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/comment",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
