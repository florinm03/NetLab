import logging
import subprocess
import os
import docker
from collections import defaultdict
from .terminal_service import TerminalService

logger = logging.getLogger(__name__)

class TopologyService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_sessions = defaultdict(dict)
        self.terminal_service = TerminalService()

    def get_user_topologies(self, user_id):
        """Get all topologies for a specific user"""
        try:
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

            print(f"name:  {topology_name}")
            topology_script = f"../../topologies_by_userid/{topology_name}_by_user.py"
            
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
            
            cmd = ['python3', topology_script, user_id]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(__file__)
            )

            import time
            time.sleep(2)
            
            if process.poll() is not None:
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

    def get_node_routing(self, node_id):
        """Get routing table for a specific node"""
        try:
            containers = self.client.containers.list(
                filters={'name': node_id}
            )
            
            if not containers:
                logger.info(f"Exact match not found for {node_id}, trying partial match")
                all_containers = self.client.containers.list()
                matching_containers = [c for c in all_containers if node_id in c.name]
                
                if matching_containers:
                    containers = matching_containers
                    logger.info(f"Found {len(containers)} containers with partial match: {[c.name for c in containers]}")
                else:
                    logger.error(f"Node {node_id} not found (exact or partial match)")
                    return {
                        'status': 'error',
                        'message': f'Node {node_id} not found'
                    }
            
            container = containers[0]
            logger.info(f"Found container {container.name} for node {node_id}")
            
            result = container.exec_run('netstat -r')
            
            logger.info(f"netstat -r exit code: {result.exit_code}")
            logger.info(f"netstat -r output: {result.output.decode('utf-8')}")
            
            if result.exit_code != 0:
                error_msg = f'Failed to get routing table: {result.output.decode("utf-8")}'
                logger.error(error_msg)
                return {
                    'status': 'error',
                    'message': error_msg
                }
            
            routes = self.parse_netstat_output(result.output.decode('utf-8'))
            logger.info(f"Parsed routes: {routes}")
            
            return {
                'status': 'success',
                'node_id': node_id,
                'routes': routes
            }
            
        except Exception as e:
            logger.error(f"Failed to get routing table for node {node_id}: {str(e)}")
            raise

    def parse_netstat_output(self, output):
        """Parse netstat -r output into structured data"""
        routes = []
        lines = output.strip().split('\n')
        
        logger.info(f"Parsing netstat output with {len(lines)} lines")
        
        # Skip header lines
        for line in lines:
            if line.startswith('Kernel') or line.startswith('Destination') or not line.strip():
                logger.debug(f"Skipping header line: {line}")
                continue
            
            parts = line.split()
            logger.debug(f"Processing line: {line} -> {parts}")
            
            if len(parts) >= 6:
                route = {
                    'destination': parts[0],
                    'gateway': parts[1],
                    'genmask': parts[2],
                    'flags': parts[3],
                    'mss': parts[4],
                    'window': parts[5],
                    'irtt': parts[6] if len(parts) > 6 else '',
                    'iface': parts[7] if len(parts) > 7 else ''
                }
                routes.append(route)
                logger.debug(f"Added route: {route}")
            else:
                logger.warning(f"Line has insufficient parts: {line} -> {parts}")
        
        logger.info(f"Parsed {len(routes)} routes")
        return routes

    def delete_node(self, user_id, node_id):
        """Delete a specific node from user's topology"""
        try:
            containers = self.client.containers.list(
                filters={'name': node_id}
            )
            
            if not containers:
                return {
                    'status': 'error',
                    'message': f'Node {node_id} not found'
                }
            
            container = containers[0]
            
            self.terminal_service._cleanup_container_session(container.name)
            
            container.stop()
            container.remove()
            
            logger.info(f"Node {node_id} deleted for user {user_id}")
            
            return {
                'status': 'success',
                'message': f'Node {node_id} deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to delete node {node_id} for user {user_id}: {str(e)}")
            raise

    def clear_topology(self, user_id):
        """Clear all nodes for a user's topology"""
        try:
            containers = self.client.containers.list(
                filters={'name': f'{user_id}'}
            )
            
            deleted_count = 0
            for container in containers:
                try:
                    container.stop()
                    container.remove()
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete container {container.name}: {str(e)}")
            
            self.terminal_service.cleanup_all_sessions(user_id)
            
            logger.info(f"Cleared topology for user {user_id}, deleted {deleted_count} containers")
            
            return {
                'status': 'success',
                'message': f'Topology cleared successfully, deleted {deleted_count} nodes'
            }
            
        except Exception as e:
            logger.error(f"Failed to clear topology for user {user_id}: {str(e)}")
            raise 