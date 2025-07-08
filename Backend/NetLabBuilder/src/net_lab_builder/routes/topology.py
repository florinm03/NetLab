from flask import Blueprint, request, jsonify
import logging
import subprocess
import os
from services.topology_service import TopologyService

logger = logging.getLogger(__name__)
topology_bp = Blueprint('topology', __name__, url_prefix='/api')
topology_service = TopologyService()

@topology_bp.route('/user-topologies/<user_id>', methods=['GET'])
def get_user_topologies(user_id):
    """Get all topologies for a specific user"""
    try:
        result = topology_service.get_user_topologies(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get topologies: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@topology_bp.route('/start-topology', methods=['POST'])
def start_topology():
    """Start a new topology for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topology_name = data.get('topology')
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        result = topology_service.start_topology(user_id, topology_name)
        return jsonify(result), 202

    except Exception as e:
        logger.error(f"Topology start failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': 'Check server logs for more information'
        }), 500 