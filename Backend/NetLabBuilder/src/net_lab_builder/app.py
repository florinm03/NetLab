import logging
import sys
import atexit
from flask import Flask
from flask_cors import CORS


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Import and register blueprints
from routes.topology import topology_bp
from routes.container import container_bp
from routes.terminal import terminal_bp
from routes.validation import validation_bp

app.register_blueprint(topology_bp)
app.register_blueprint(container_bp)
app.register_blueprint(terminal_bp)
app.register_blueprint(validation_bp)

# Import terminal service to set up cleanup
from services.terminal_service import TerminalService

# Create global terminal service instance
terminal_service = TerminalService()

# Make terminal service available in app context
app.terminal_service = terminal_service

@app.route('/')
def home():
    return "NetLabBuilder API is running! Use /api/start-container to begin."

def cleanup_on_exit():
    """Cleanup function called when the application exits"""
    try:
        logger.info("Cleaning up terminal service...")
        terminal_service.stop_event_listener()
        terminal_service.cleanup_all_sessions()
        logger.info("Terminal service cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# Register cleanup function
atexit.register(cleanup_on_exit)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
