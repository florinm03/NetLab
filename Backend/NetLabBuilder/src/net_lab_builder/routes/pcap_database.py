from flask import Blueprint, request, jsonify, send_file
import logging
import subprocess
import os
import json
import tempfile
from datetime import datetime
from services.pcap_database_service import PcapDatabaseService

logger = logging.getLogger(__name__)
pcap_db_bp = Blueprint('pcap_database', __name__, url_prefix='/api')
pcap_service = PcapDatabaseService()

@pcap_db_bp.route('/save-pcap/<user_id>', methods=['POST'])
def save_pcap_to_database(user_id):
    """Save PCAP file to database for a specific user"""
    try:
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        request_data = request.get_json() or {}
        creator_in_body = request_data.get('creator') or request_data.get('user_id')
        if creator_in_body and creator_in_body != user_id:
            return jsonify({'status': 'error', 'message': 'User ID mismatch: not allowed to save for another user.'}), 403

        container_name = f"prototype-{user_id}-pcap-merger"
    
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                check=True
            )

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

        topology_info = request_data.get('topology_info', {})
        
        metadata = generate_pcap_metadata(temp_file_path)
        
        connections = request_data.get('connections', [])
        
        pcap_id = pcap_service.save_pcap_file(
            creator=user_id,
            file_path=temp_file_path,
            topology_info=topology_info,
            metadata=metadata,
            connections=connections
        )
        
        if pcap_id:
            # Clean up temporary file after saving to database
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")
            
            return jsonify({
                'status': 'success',
                'message': 'PCAP file and metadata saved to database successfully',
                'pcap_id': pcap_id
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to save PCAP file to database'
            }), 500

    except Exception as e:
        logger.error(f"PCAP save failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcaps/<user_id>', methods=['GET'])
def get_user_pcaps(user_id):
    """Get all PCAP files for a specific user"""
    try:
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        pcaps = pcap_service.get_pcap_files_by_creator(user_id)
        
        # Convert datetime objects to strings for JSON serialization
        for pcap in pcaps:
            if 'created_at' in pcap and pcap['created_at']:
                pcap['created_at'] = pcap['created_at'].isoformat()
            if 'updated_at' in pcap and pcap['updated_at']:
                pcap['updated_at'] = pcap['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'pcaps': pcaps
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get PCAPs for user {user_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcap/<pcap_id>', methods=['GET'])
def get_pcap_details(pcap_id):
    """Get specific PCAP file details"""
    try:
        if not pcap_id:
            return jsonify({'status': 'error', 'message': 'pcap_id required'}), 400

        pcap = pcap_service.get_pcap_file_by_id(int(pcap_id), include_data=False)
        
        if not pcap:
            return jsonify({'status': 'error', 'message': 'PCAP file not found'}), 404
        
        # Convert datetime objects to strings
        if 'created_at' in pcap and pcap['created_at']:
            pcap['created_at'] = pcap['created_at'].isoformat()
        if 'updated_at' in pcap and pcap['updated_at']:
            pcap['updated_at'] = pcap['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'pcap': pcap
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get PCAP {pcap_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcap/<pcap_id>/download', methods=['GET'])
def download_pcap_from_db(pcap_id):
    """Download PCAP file from database storage"""
    try:
        if not pcap_id:
            return jsonify({'status': 'error', 'message': 'pcap_id required'}), 400

        pcap = pcap_service.get_pcap_file_by_id(int(pcap_id), include_data=True)
        
        if not pcap:
            return jsonify({'status': 'error', 'message': 'PCAP file not found'}), 404
        
        if not pcap.get('pcap_data'):
            return jsonify({'status': 'error', 'message': 'PCAP file data not found in database'}), 404
        
        # Create response with PCAP data
        from io import BytesIO
        pcap_data = pcap['pcap_data']
        if isinstance(pcap_data, str):
            pcap_data = pcap_data.encode('latin-1')
        
        return send_file(
            BytesIO(pcap_data),
            as_attachment=True,
            download_name=pcap['filename'],
            mimetype='application/vnd.tcpdump.pcap'
        )
        
    except Exception as e:
        logger.error(f"Failed to download PCAP {pcap_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcap/<pcap_id>/json', methods=['GET'])
def get_pcap_json(pcap_id):
    """Get PCAP data in JSON format for analysis"""
    try:
        if not pcap_id:
            return jsonify({'status': 'error', 'message': 'pcap_id required'}), 400

        pcap = pcap_service.get_pcap_file_by_id(int(pcap_id), include_data=False)
        
        if not pcap:
            return jsonify({'status': 'error', 'message': 'PCAP file not found'}), 404
        
        pcap_json = pcap_service.get_pcap_json_by_id(int(pcap_id))
        
        if not pcap_json:
            return jsonify({'status': 'error', 'message': 'PCAP JSON data not found in database'}), 404
        
        try:
            json_data = json.loads(pcap_json)
            return jsonify({
                'status': 'success',
                'pcap_id': pcap_id,
                'data': json_data
            }), 200
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PCAP JSON data: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Invalid JSON data in database'}), 500
        
    except Exception as e:
        logger.error(f"Failed to get PCAP JSON {pcap_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcap/<pcap_id>/connections', methods=['GET'])
def get_pcap_connections(pcap_id):
    """Get PCAP connections data for graph visualization"""
    try:
        if not pcap_id:
            return jsonify({'status': 'error', 'message': 'pcap_id required'}), 400

        pcap = pcap_service.get_pcap_file_by_id(int(pcap_id), include_data=False)
        
        if not pcap:
            return jsonify({'status': 'error', 'message': 'PCAP file not found'}), 404
        
        if not pcap.get('connections_json'):
            return jsonify({'status': 'error', 'message': 'PCAP connections data not found in database'}), 404
        
        try:
            connections_data = json.loads(pcap['connections_json'])
            return jsonify({
                'status': 'success',
                'pcap_id': pcap_id,
                'connections': connections_data
            }), 200
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PCAP connections data: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Invalid connections data in database'}), 500
        
    except Exception as e:
        logger.error(f"Failed to get PCAP connections {pcap_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@pcap_db_bp.route('/pcap/<pcap_id>', methods=['DELETE'])
def delete_pcap(pcap_id):
    """Delete PCAP metadata from database"""
    try:
        if not pcap_id:
            return jsonify({'status': 'error', 'message': 'pcap_id required'}), 400

        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        success = pcap_service.delete_pcap_file(int(pcap_id), user_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'PCAP metadata deleted successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to delete PCAP metadata'
            }), 500
        
    except Exception as e:
        logger.error(f"Failed to delete PCAP {pcap_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_pcap_metadata(file_path):
    """Generate metadata from PCAP file using tcpdump"""
    try:
        file_size = os.path.getsize(file_path)
        file_stats = os.stat(file_path)
        
        result = subprocess.run([
            'tcpdump', '-r', file_path, '-n', '-q', '-c', '1000'
        ], capture_output=True, text=True)
        
        packet_count = len(result.stdout.splitlines())
        
        protocols = set()
        for line in result.stdout.splitlines():
            if 'IP' in line:
                if 'TCP' in line:
                    protocols.add('TCP')
                elif 'UDP' in line:
                    protocols.add('UDP')
                elif 'ICMP' in line:
                    protocols.add('ICMP')
        
        return {
            'file_size': file_size,
            'created_time': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'estimated_packets': packet_count,
            'protocols': list(protocols),
            'analysis_method': 'tcpdump'
        }
        
    except Exception as e:
        logger.error(f"Error generating PCAP metadata: {str(e)}")
        return {
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'error': str(e)
        } 