"""
Classification service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Classification domain.
"""
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPInternalServerError
from api_utils.mongo_utils import execute_infinite_scroll_query
import logging

logger = logging.getLogger(__name__)

# Allowed sort fields for Classification domain
ALLOWED_SORT_FIELDS = ['name', 'description']


class ClassificationService:
    """
    Service class for Classification domain operations.
    
    Handles:
    - RBAC authorization checks (placeholder for future implementation)
    - MongoDB operations via MongoIO singleton
    - Business logic for Classification domain (read-only)
    """
    
    @staticmethod
    def _check_permission(token, operation):
        """
        Check if the user has permission to perform an operation.
        
        Args:
            token: Token dictionary with user_id and roles
            operation: The operation being performed (e.g., 'read')
        
        Raises:
            HTTPForbidden: If user doesn't have required permission
            
        Note: This is a placeholder for future RBAC implementation.
        For now, all operations require a valid token (authentication only).
        
        Example RBAC implementation:
            if operation == 'read':
                # Read requires any authenticated user (no additional check needed)
                # For stricter requirements, you could require specific roles:
                # if not any(role in token.get('roles', []) for role in ['staff', 'admin', 'viewer']):
                #     raise HTTPForbidden("Insufficient permissions to read classification documents")
                pass
        """
        pass
    
    @staticmethod
    def get_classifications(token, breadcrumb, name=None, after_id=None, limit=10, sort_by='name', order='asc'):
        """
        Get infinite scroll batch of sorted, filtered classification documents.
        
        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            name: Optional name filter (simple search)
            after_id: Cursor (ID of last item from previous batch, None for first request)
            limit: Items per batch
            sort_by: Field to sort by
            order: Sort order ('asc' or 'desc')
        
        Returns:
            dict: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None  # ID of last item, or None if no more
            }
        
        Raises:
            HTTPBadRequest: If invalid parameters provided
        """
        try:
            ClassificationService._check_permission(token, 'read')
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            collection = mongo.get_collection(config.CLASSIFICATION_COLLECTION_NAME)
            result = execute_infinite_scroll_query(
                collection,
                name=name,
                after_id=after_id,
                limit=limit,
                sort_by=sort_by,
                order=order,
                allowed_sort_fields=ALLOWED_SORT_FIELDS,
            )
            logger.info(
                f"Retrieved {len(result['items'])} classifications (has_more={result['has_more']}) "
                f"for user {token.get('user_id')}"
            )
            return result
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving classifications: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve classifications")
    
    @staticmethod
    def get_classification(classification_id, token, breadcrumb):
        """
        Retrieve a specific classification document by ID.
        
        Args:
            classification_id: The classification ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging
            
        Returns:
            dict: The classification document
            
        Raises:
            HTTPNotFound: If classification is not found
        """
        try:
            ClassificationService._check_permission(token, 'read')
            
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            classification = mongo.get_document(config.CLASSIFICATION_COLLECTION_NAME, classification_id)
            if classification is None:
                raise HTTPNotFound(f"Classification { classification_id} not found")
            
            logger.info(f"Retrieved classification { classification_id} for user {token.get('user_id')}")
            return classification
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving classification { classification_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve classification { classification_id}")