"""
Post routes for Flask API.

Provides endpoints for Create domain:
- POST /api/post - Create a new post document
- GET /api/post - Get all post documents
- GET /api/post/<id> - Get a specific post document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.post_service import PostService

import logging
logger = logging.getLogger(__name__)


def create_post_routes():
    """
    Create a Flask Blueprint exposing post endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with post routes
    """
    post_routes = Blueprint('post_routes', __name__)
    
    @post_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_post():
        """
        POST /api/post - Create a new post document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the postd post document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        post_id = PostService.create_post(data, token, breadcrumb)
        post = PostService.get_post(post_id, token, breadcrumb)
        
        logger.info(f"create_post Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(post), 201
    
    @post_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_posts():
        """
        GET /api/post - Retrieve infinite scroll batch of sorted, filtered post documents.
        
        Query Parameters:
            name: Optional name filter
            after_id: Cursor for infinite scroll (ID of last item from previous batch, omit for first request)
            limit: Items per batch (default: 10, max: 100)
            sort_by: Field to sort by (default: 'name')
            order: Sort order 'asc' or 'desc' (default: 'asc')
        
        Returns:
            JSON response with infinite scroll results: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None
            }
        
        Raises:
            400 Bad Request: If invalid parameters provided
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get query parameters
        name = request.args.get('name')
        after_id = request.args.get('after_id')
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        # Service layer validates parameters and raises HTTPBadRequest if invalid
        # @handle_route_exceptions decorator will catch and format the exception
        result = PostService.get_posts(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_posts Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @post_routes.route('/<post_id>', methods=['GET'])
    @handle_route_exceptions
    def get_post(post_id):
        """
        GET /api/post/<id> - Retrieve a specific post document by ID.
        
        Args:
            post_id: The post ID to retrieve
            
        Returns:
            JSON response with the post document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        post = PostService.get_post(post_id, token, breadcrumb)
        logger.info(f"get_post Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(post), 200
    
    logger.info("Create Flask Routes Registered")
    return post_routes