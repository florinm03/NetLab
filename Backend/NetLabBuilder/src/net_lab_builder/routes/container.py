from flask import Blueprint, request, jsonify
import logging
from services.container_service import ContainerService

logger = logging.getLogger(__name__)
container_bp = Blueprint('container', __name__, url_prefix='/api')
container_service = ContainerService()

@container_bp.route('/start-container', methods=['POST'])
def start_container():
    """Start a new container for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')

        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        result = container_service.start_container(user_id, session_id)
        return jsonify(result), 201

    except Exception as e:
        logger.error(f"Container start failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500 