"""
E2E tests for Comment endpoints (create-style with POST and GET).

These tests verify that Comment endpoints work correctly by making
actual HTTP requests to a running server.

To run these tests:
1. Start the server: pipenv run dev (or pipenv run api for containerized)
2. Run E2E tests: pipenv run e2e

API runs on port 9100 (same for dev and api).
"""
import pytest
import requests

BASE_URL = "http://localhost:9100"


def _err(response, expected):
    """Format assertion error with response body for debugging."""
    body = response.text[:300] if response.text else "(empty)"
    return f"Expected {expected}, got {response.status_code}. Response: {body}"


def get_auth_token():
    """Helper function to get an authentication token from dev-login."""
    response = requests.post(
        f"{BASE_URL}/dev-login",
        json={"subject": "e2e-test-user", "roles": ["admin", "developer"]},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@pytest.mark.e2e
def test_create_comment_endpoint():
    """Test POST /api/comment endpoint and basic retrieval by ID and search."""
    token = get_auth_token()
    assert token is not None, "Failed to get auth token"

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "e2e-test-comment",
        "description": "E2E test comment document",
    }

    response = requests.post(f"{BASE_URL}/api/comment", headers=headers, json=data)
    assert response.status_code == 201, _err(response, 201)

    response_data = response.json()
    assert "_id" in response_data, "Response missing '_id' key"
    assert response_data["name"] == "e2e-test-comment"
    assert "created" in response_data


@pytest.mark.e2e
def test_get_comments_endpoint():
    """Test GET /api/comment endpoint."""
    token = get_auth_token()
    assert token is not None, "Failed to get auth token"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/comment", headers=headers)
    assert response.status_code == 200, _err(response, 200)

    response_data = response.json()
    assert isinstance(response_data, dict), "Response should be a dict (infinite scroll format)"
    assert "items" in response_data, "Response should have 'items' key"
    assert "limit" in response_data, "Response should have 'limit' key"
    assert "has_more" in response_data, "Response should have 'has_more' key"
    assert "next_cursor" in response_data, "Response should have 'next_cursor' key"
    assert isinstance(response_data["items"], list), "Items should be a list"


@pytest.mark.e2e
def test_get_comment_not_found():
    """Test GET /api/comment/<id> with non-existent ID."""
    token = get_auth_token()
    assert token is not None, "Failed to get auth token"

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/comment/000000000000000000000000",
        headers=headers,
    )
    assert response.status_code == 404, _err(response, 404)


@pytest.mark.e2e
def test_comment_endpoints_require_auth():
    """Test that comment endpoints require authentication."""
    response = requests.get(f"{BASE_URL}/api/comment")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
