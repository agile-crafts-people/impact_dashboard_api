"""
Flask MongoDB API Server

This is a Flask + MongoDB API that for the sample service in the Mentor Hub system.
"""
import sys
import os
import signal
from flask import Flask, send_from_directory

# Initialize Config Singleton (doesn't require external services)
from api_utils import Config
config = Config.get_instance()

# Initialize logging (Config constructor configures logging)
import logging
logger = logging.getLogger(__name__)
logger.info("============= Starting Server ===============")

# Initialize MongoIO Singleton and set enumerators and versions
from api_utils import MongoIO
mongo = MongoIO.get_instance()
config.set_enumerators(mongo.get_documents(config.ENUMERATORS_COLLECTION_NAME))
config.set_versions(mongo.get_documents(config.VERSIONS_COLLECTION_NAME))

# Initialize Flask App
from api_utils import MongoJSONEncoder
app = Flask(__name__)
app.json = MongoJSONEncoder(app)

# Route registration (all grouped together)
from api_utils import (
    create_metric_routes,
    create_dev_login_routes,
    create_config_routes,
    create_explorer_routes
)
from src.routes.dashboard_routes import create_dashboard_routes
from src.routes.post_routes import create_post_routes
from src.routes.comment_routes import create_comment_routes
from src.routes.classification_routes import create_classification_routes
from src.routes.profile_routes import create_profile_routes
# Register route blueprints
# Register explorer routes with template's docs directory
docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
app.register_blueprint(create_explorer_routes(docs_dir), url_prefix='/docs')
app.register_blueprint(create_config_routes(), url_prefix='/api/config')
app.register_blueprint(create_dev_login_routes(), url_prefix='/dev-login')
app.register_blueprint(create_dashboard_routes(), url_prefix='/api/dashboard')
app.register_blueprint(create_post_routes(), url_prefix='/api/post')
app.register_blueprint(create_comment_routes(), url_prefix='/api/comment')
app.register_blueprint(create_classification_routes(), url_prefix='/api/classification')
app.register_blueprint(create_profile_routes(), url_prefix='/api/profile')
metrics = create_metric_routes(app)  # This exposes /metrics endpoint

logger.info("============= Routes Registered ===============")
logger.info("  /api/config - Configuration endpoint")
logger.info("  /dev-login - Dev Login (returns 404 if disabled)")
logger.info("  /api/dashboard - Dashboard domain endpoints")
logger.info("  /api/post - Post domain endpoints")
logger.info("  /api/comment - Comment domain endpoints")
logger.info("  /api/classification - Classification domain endpoints")
logger.info("  /api/profile - Profile domain endpoints")
logger.info("  /docs - API Explorer")
logger.info("  /metrics - Prometheus metrics endpoint")

# Define a signal handler for SIGTERM and SIGINT
def handle_exit(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT."""
    global mongo
    logger.info(f"Received signal {signum}. Initiating shutdown...")
    
    # Disconnect from MongoDB if connected
    if mongo is not None:
        logger.info("Closing MongoDB connection.")
        try:
            mongo.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {e}")
    
    logger.info("Shutdown complete.")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Expose app for Gunicorn or direct execution
if __name__ == "__main__":
    api_port = config.DASHBOARD_API_PORT
    logger.info(f"Starting Flask server on port {api_port}")
    app.run(host="0.0.0.0", port=api_port, debug=False)