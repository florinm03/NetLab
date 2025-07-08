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

@topology_bp.route('/node-routing/<node_id>', methods=['GET'])
def get_node_routing(node_id):
    """Get routing table for a specific node"""
    try:
        result = topology_service.get_node_routing(node_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to get routing table for node {node_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@topology_bp.route('/delete-node/<user_id>/<node_id>', methods=['DELETE'])
def delete_node(user_id, node_id):
    """Delete a specific node from user's topology"""
    try:
        result = topology_service.delete_node(user_id, node_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to delete node {node_id} for user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@topology_bp.route('/clear-topology/<user_id>', methods=['DELETE'])
def clear_topology(user_id):
    """Clear all nodes for a user's topology"""
    try:
        result = topology_service.clear_topology(user_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Failed to clear topology for user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500 