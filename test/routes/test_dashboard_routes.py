"""
Unit tests for Dashboard routes.

These tests validate the Flask route layer for the Dashboard domain, using the
generated blueprint factory and mocking out the underlying service and
token/breadcrumb helpers from api_utils.
"""
import unittest
from unittest.mock import patch
from flask import Flask
from src.routes.dashboard_routes import create_dashboard_routes


class TestDashboardRoutes(unittest.TestCase):
    """Test cases for Dashboard routes."""

    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(
            create_dashboard_routes(),
            url_prefix="/api/dashboard",
        )
        self.client = self.app.test_client()

        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {"at_time": "sometime", "correlation_id": "correlation_ID"}

    @patch("src.routes.dashboard_routes.create_flask_token")
    @patch("src.routes.dashboard_routes.create_flask_breadcrumb")
    @patch("src.routes.dashboard_routes.DashboardService.create_dashboard")
    @patch("src.routes.dashboard_routes.DashboardService.get_dashboard")
    def test_create_dashboard_success(
        self,
        mock_get_dashboard,
        mock_create_dashboard,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test POST /api/dashboard for successful creation."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_create_dashboard.return_value = "123"
        mock_get_dashboard.return_value = {
            "_id": "123",
            "name": "test-dashboard",
            "status": "active",
        }

        response = self.client.post(
            "/api/dashboard",
            json={"name": "test-dashboard", "status": "active"},
        )

        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_create_dashboard.assert_called_once()
        mock_get_dashboard.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.dashboard_routes.create_flask_token")
    @patch("src.routes.dashboard_routes.create_flask_breadcrumb")
    @patch("src.routes.dashboard_routes.DashboardService.get_dashboards")
    def test_get_dashboards_no_filter(
        self,
        mock_get_dashboards,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/dashboard without name filter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_dashboards.return_value = {
            "items": [
                {"_id": "123", "name": "dashboard1"},
                {"_id": "456", "name": "dashboard2"},
            ],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/dashboard")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 2)
        mock_get_dashboards.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name=None,
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.dashboard_routes.create_flask_token")
    @patch("src.routes.dashboard_routes.create_flask_breadcrumb")
    @patch("src.routes.dashboard_routes.DashboardService.get_dashboards")
    def test_get_dashboards_with_name_filter(
        self,
        mock_get_dashboards,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/dashboard with name query parameter."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_dashboards.return_value = {
            "items": [{"_id": "123", "name": "test-dashboard"}],
            "limit": 10,
            "has_more": False,
            "next_cursor": None,
        }

        response = self.client.get("/api/dashboard?name=test")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        mock_get_dashboards.assert_called_once_with(
            self.mock_token,
            self.mock_breadcrumb,
            name="test",
            after_id=None,
            limit=10,
            sort_by="name",
            order="asc",
        )

    @patch("src.routes.dashboard_routes.create_flask_token")
    @patch("src.routes.dashboard_routes.create_flask_breadcrumb")
    @patch("src.routes.dashboard_routes.DashboardService.get_dashboard")
    def test_get_dashboard_success(
        self,
        mock_get_dashboard,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/dashboard/<id> for successful response."""
        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_dashboard.return_value = {
            "_id": "123",
            "name": "dashboard1",
        }

        response = self.client.get("/api/dashboard/123")

        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data["_id"], "123")
        mock_get_dashboard.assert_called_once_with(
            "123", self.mock_token, self.mock_breadcrumb
        )

    @patch("src.routes.dashboard_routes.create_flask_token")
    @patch("src.routes.dashboard_routes.create_flask_breadcrumb")
    @patch("src.routes.dashboard_routes.DashboardService.get_dashboard")
    def test_get_dashboard_not_found(
        self,
        mock_get_dashboard,
        mock_create_breadcrumb,
        mock_create_token,
    ):
        """Test GET /api/dashboard/<id> when document is not found."""
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_create_token.return_value = self.mock_token
        mock_create_breadcrumb.return_value = self.mock_breadcrumb

        mock_get_dashboard.side_effect = HTTPNotFound(
            "Dashboard 999 not found"
        )

        response = self.client.get("/api/dashboard/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error"], "Dashboard 999 not found")

    @patch("src.routes.dashboard_routes.create_flask_token")
    def test_create_dashboard_unauthorized(self, mock_create_token):
        """Test POST /api/dashboard when token is invalid."""
        from api_utils.flask_utils.exceptions import HTTPUnauthorized

        mock_create_token.side_effect = HTTPUnauthorized("Invalid token")

        response = self.client.post(
            "/api/dashboard",
            json={"name": "test"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
