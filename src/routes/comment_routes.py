"""
Comment routes for Flask API.

Provides endpoints for Create domain:
- POST /api/comment - Create a new comment document
- GET /api/comment - Get all comment documents
- GET /api/comment/<id> - Get a specific comment document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.comment_service import CommentService

import logging
logger = logging.getLogger(__name__)


def create_comment_routes():
    """
    Create a Flask Blueprint exposing comment endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with comment routes
    """
    comment_routes = Blueprint('comment_routes', __name__)
    
    @comment_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_comment():
        """
        POST /api/comment - Create a new comment document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the commentd comment document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        comment_id = CommentService.create_comment(data, token, breadcrumb)
        comment = CommentService.get_comment(comment_id, token, breadcrumb)
        
        logger.info(f"create_comment Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(comment), 201
    
    @comment_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_comments():
        """
        GET /api/comment - Retrieve infinite scroll batch of sorted, filtered comment documents.
        
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
        result = CommentService.get_comments(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_comments Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @comment_routes.route('/<comment_id>', methods=['GET'])
    @handle_route_exceptions
    def get_comment(comment_id):
        """
        GET /api/comment/<id> - Retrieve a specific comment document by ID.
        
        Args:
            comment_id: The comment ID to retrieve
            
        Returns:
            JSON response with the comment document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        comment = CommentService.get_comment(comment_id, token, breadcrumb)
        logger.info(f"get_comment Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(comment), 200
    
    logger.info("Create Flask Routes Registered")
    return comment_routes