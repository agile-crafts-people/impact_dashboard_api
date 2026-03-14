"""
Dashboard routes for Flask API.

Provides endpoints for Dashboard domain:
- POST /api/dashboard - Create a new dashboard document
- GET /api/dashboard - Get all dashboard documents (with optional ?name= query parameter)
- GET /api/dashboard/<id> - Get a specific dashboard document by ID
- PATCH /api/dashboard/<id> - Update a dashboard document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.dashboard_service import DashboardService

import logging
logger = logging.getLogger(__name__)


def create_dashboard_routes():
    """
    Create a Flask Blueprint exposing dashboard endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with dashboard routes
    """
    dashboard_routes = Blueprint('dashboard_routes', __name__)
    
    @dashboard_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_dashboard():
        """
        POST /api/dashboard - Create a new dashboard document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created dashboard document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        dashboard_id = DashboardService.create_dashboard(data, token, breadcrumb)
        dashboard = DashboardService.get_dashboard(dashboard_id, token, breadcrumb)
        
        logger.info(f"create_dashboard Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(dashboard), 201
    
    @dashboard_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_dashboards():
        """
        GET /api/dashboard - Retrieve infinite scroll batch of sorted, filtered dashboard documents.
        
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
        result = DashboardService.get_dashboards(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_dashboards Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @dashboard_routes.route('/<dashboard_id>', methods=['GET'])
    @handle_route_exceptions
    def get_dashboard(dashboard_id):
        """
        GET /api/dashboard/<id> - Retrieve a specific dashboard document by ID.
        
        Args:
            dashboard_id: The dashboard ID to retrieve
            
        Returns:
            JSON response with the dashboard document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        dashboard = DashboardService.get_dashboard(dashboard_id, token, breadcrumb)
        logger.info(f"get_dashboard Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(dashboard), 200
    
    @dashboard_routes.route('/<dashboard_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_dashboard(dashboard_id):
        """
        PATCH /api/dashboard/<id> - Update a dashboard document.
        
        Args:
            dashboard_id: The dashboard ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated dashboard document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        dashboard = DashboardService.update_dashboard(dashboard_id, data, token, breadcrumb)
        
        logger.info(f"update_dashboard Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(dashboard), 200
    
    logger.info("Dashboard Flask Routes Registered")
    return dashboard_routes