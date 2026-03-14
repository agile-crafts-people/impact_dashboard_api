"""
Classification routes for Flask API.

Provides endpoints for Classification domain:
- GET /api/classification - Get all classification documents
- GET /api/classification/<id> - Get a specific classification document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.classification_service import ClassificationService

import logging
logger = logging.getLogger(__name__)


def create_classification_routes():
    """
    Create a Flask Blueprint exposing classification endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with classification routes
    """
    classification_routes = Blueprint('classification_routes', __name__)
    
    @classification_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_classifications():
        """
        GET /api/classification - Retrieve infinite scroll batch of sorted, filtered classification documents.
        
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
        result = ClassificationService.get_classifications(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_classifications Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @classification_routes.route('/<classification_id>', methods=['GET'])
    @handle_route_exceptions
    def get_classification(classification_id):
        """
        GET /api/classification/<id> - Retrieve a specific classification document by ID.
        
        Args:
            classification_id: The classification ID to retrieve
            
        Returns:
            JSON response with the classification document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        classification = ClassificationService.get_classification(classification_id, token, breadcrumb)
        logger.info(f"get_classification Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(classification), 200
    
    logger.info("Classification Flask Routes Registered")
    return classification_routes