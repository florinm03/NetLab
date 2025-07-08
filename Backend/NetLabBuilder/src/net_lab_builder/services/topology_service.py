import logging
import subprocess
import os
import docker
from collections import defaultdict

logger = logging.getLogger(__name__)

class TopologyService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_sessions = defaultdict(dict)

    def get_user_topologies(self, user_id):
        """Get all topologies for a specific user"""
        try:
            # Get all containers for this user
            containers = self.client.containers.list(
                filters={'name': f'{user_id}'}
            )

            return {
                'status': 'success',
                'user_id': user_id,
                'nodes': [c.name for c in containers],
                'running': [c.status == 'running' for c in containers],
            }

        except Exception as e:
            logger.error(f"Failed to get topologies: {str(e)}")
            raise

    def start_topology(self, user_id, topology_name):
        """Start a new topology for a user"""
        try:
            # Check if user already has a running topology
            containers = self.client.containers.list(
                filters={'name': f'prototype-{user_id}'}
            )
            if containers:
                return {
                    'status': 'error',
                    'user_id': user_id,
                    'topology': topology_name,
                    'message': f'User {user_id} already has a running topology. Please stop it first.',
                    'details': f'Found {len(containers)} running containers for this user'
                }

            # Construct the file path
            topology_script = f"../../topologies_by_userid/{topology_name}_by_user.py"
            
            # Check if the topology script file exists
            script_path = os.path.join(os.path.dirname(__file__), topology_script)
            if not os.path.exists(script_path):
                error_msg = f"Topology script not found: {script_path}"
                logger.error(error_msg)
                return {
                    'status': 'error',
                    'user_id': user_id,
                    'topology': topology_name,
                    'message': error_msg,
                    'details': f'Available topologies: {[f.split("_by_user.py")[0] for f in os.listdir(os.path.join(os.path.dirname(__file__), "../topologies_by_userid")) if f.endswith("_by_user.py")]}'
                }
            
            # Execute the topology script in background
            cmd = ['python3', topology_script, user_id]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(__file__)
            )

            # Give the process a moment to start and check for immediate errors
            import time
            time.sleep(2)
            
            # Check if process has already terminated (indicating an error)
            if process.poll() is not None:
                # Process has terminated, get the error output
                stdout, stderr = process.communicate()
                error_output = stderr.decode('utf-8') if stderr else "Unknown error"
                logger.error(f"Topology script failed to start: {error_output}")
                return {
                    'status': 'error',
                    'user_id': user_id,
                    'topology': topology_name,
                    'message': f'Failed to start topology: {error_output}',
                    'details': 'Check server logs for more information'
                }
            
            # Process is running, return success
            logger.info(f"Topology script started successfully for user {user_id} with PID {process.pid}")
            return {
                'status': 'success',
                'user_id': user_id,
                'topology': topology_name,
                'pid': process.pid,
                'message': f'Topology {topology_name} started for user {user_id}'
            }

        except Exception as e:
            logger.error(f"Topology start failed: {str(e)}")
            raise 