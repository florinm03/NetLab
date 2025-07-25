from flask import Blueprint, request, jsonify, send_file
import logging
import os
import subprocess
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

@container_bp.route('/download-pcap/<user_id>', methods=['GET'])
def download_pcap(user_id):
    """Download merged PCAP file for a specific user"""
    try:
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        container_name = f"prototype-{user_id}-pcap-merger"
    
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                check=True
            )
            print(result)

            if container_name not in result.stdout:
                return jsonify({
                    'status': 'error', 
                    'message': f'PCAP merger container for user {user_id} not found or not running'
                }), 404
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking container status: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to check container status'}), 500

        temp_file_path = f"/tmp/merged_pcap_{user_id}.pcap"
        
        try:
            copy_result = subprocess.run([
                'docker', 'cp', f'{container_name}:/pcap/merged.pcap', temp_file_path
            ], capture_output=True, text=True, check=True)
            
            if not os.path.exists(temp_file_path):
                return jsonify({
                    'status': 'error', 
                    'message': 'PCAP file not found in container or failed to copy'
                }), 404
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Error copying PCAP file: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to copy PCAP file from container'}), 500

        try:
            return send_file(
                temp_file_path,
                as_attachment=True,
                download_name=f'merged_pcap_{user_id}.pcap',
                mimetype='application/vnd.tcpdump.pcap'
            )
        except Exception as e:
            logger.error(f"Error sending file: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Failed to send PCAP file'}), 500
        finally:
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")

    except Exception as e:
        logger.error(f"PCAP download failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500 