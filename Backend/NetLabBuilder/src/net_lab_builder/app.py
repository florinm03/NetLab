import logging
import sys
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

@app.route('/')
def home():
    return "NetLabBuilder API is running! Use /api/start-container to begin."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
