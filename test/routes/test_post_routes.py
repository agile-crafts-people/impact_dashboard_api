"""
Unit tests for Post routes (create-style with POST and GET).
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.post_routes import create_post_routes


class TestPostRoutes(unittest.TestCase):
    """Test cases for Post routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_post_routes(),
            url_prefix="/api/post",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.post_routes.create_flask_token")
    @patch("src.routes.post_routes.create_flask_breadcrumb")
    @patch("src.routes.post_routes.PostService.create_post")
    @patch("src.routes.post_routes.PostService.get_post")
    def test_create_post_success(
        self,
        mock_get_post,
        mock_create_post,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/post for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_post.return_value = "123"
        mock_get_post.return_value = {
            "_id": "123",
            "name": "test-post",
            "status": "active",
        }

        response = self.client.post(
            "/api/post",
            json={"name": "test-post", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_post.assert_called_once()
        mock_get_post.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.post_routes.create_flask_token")
    @patch("src.routes.post_routes.create_flask_breadcrumb")
    @patch("src.routes.post_routes.PostService.get_posts")
    def test_get_posts_success(
        self,
        mock_get_posts,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/post for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_posts.return_value = {
            "items": [
                {"_id": "123", "name": "post1"},
                {"_id": "456", "name": "post2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/post")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_posts.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.post_routes.create_flask_token")
    @patch("src.routes.post_routes.create_flask_breadcrumb")
    @patch("src.routes.post_routes.PostService.get_post")
    def test_get_post_success(
        self,
        mock_get_post,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/post/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_post.return_value = {
            "_id": "123",
            "name": "post1",
        }

        response = self.client.get("/api/post/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_post.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.post_routes.create_flask_token")
    @patch("src.routes.post_routes.create_flask_breadcrumb")
    @patch("src.routes.post_routes.PostService.get_post")
    def test_get_post_not_found(
        self,
        mock_get_post,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/post/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_post.side_effect = HTTPNotFound(
            "Post 999 not found"
        )

        response = self.client.get("/api/post/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Post 999 not found")

    @patch("src.routes.post_routes.create_flask_token")
    def test_create_post_unauthorized(self, mock_create_token):
        """Test POST /api/post when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/post",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
