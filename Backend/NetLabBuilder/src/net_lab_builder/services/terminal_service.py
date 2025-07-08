import logging
import uuid
import socket
from contextlib import closing
import subprocess
import docker
from collections import defaultdict

logger = logging.getLogger(__name__)

class TerminalService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_sessions = defaultdict(dict)

    def get_own_nodes(self, user_id, host):
        containers = self.client.containers.list(
            filters={'name': f'{user_id}'}
        )
        if not containers:
            return {
                'status': 'success',
                'message': 'No containers found for this user',
                'terminals': []
            }
        terminal_urls = []
        used_ports = set()
        min_port = 8000
        max_port = 9000
        for container in containers:
            try:
                port = None
                for _ in range(50):
                    candidate_port = self.find_free_port(min_port, max_port)
                    if candidate_port not in used_ports and not self.is_port_in_use(candidate_port):
                        port = candidate_port
                        min_port = candidate_port + 1
                        max_port = candidate_port + 10
                        break
                if port is None:
                    raise RuntimeError("Could not find available port")
                used_ports.add(port)
                self.start_ttyd_process(container.name, port)
                terminal_urls.append({
                    'container_name': container.name,
                    'url': f'http://{host.split(":")[0]}:{port}',
                    'port': port,
                    'status': container.status
                })
            except Exception as e:
                logger.error(f"Failed to start ttyd for {container.name}: {str(e)}")
                terminal_urls.append({
                    'container_name': container.name,
                    'error': str(e),
                    'status': 'failed'
                })
        return {
            'status': 'success',
            'user_id': user_id,
            'terminals': terminal_urls
        }

    def start_ttyd(self, container_name, session_id, host):
        try:
            container = self.client.containers.get(container_name)
            if container.status != 'running':
                container.start()
                logger.info(f"Started container: {container_name}")
        except Exception as e:
            logger.error(f"Container {container_name} not found: {str(e)}")
            return {
                'status': 'error',
                'message': f'Container {container_name} not found'
            }
        if session_id in self.active_sessions.get(container_name, {}):
            port = self.active_sessions[container_name][session_id]
            if self.is_port_in_use(port):
                return {
                    'status': 'success',
                    'url': f'http://{host.split(":")[0]}:{port}',
                    'port': port,
                    'session_id': session_id
                }
            del self.active_sessions[container_name][session_id]
        port = self.find_free_port()
        self.start_ttyd_process(container_name, port)
        self.active_sessions[container_name][session_id] = port
        return {
            'status': 'success',
            'url': f'http://{host.split(":")[0]}:{port}',
            'port': port,
            'session_id': session_id
        }

    def generate_session_id(self):
        return str(uuid.uuid4())

    def find_free_port(self, min=None, max=None):
        for port in range(min or 8000, max or 9000):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No free ports in range")

    def is_port_in_use(self, port):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_ttyd_process(self, container_name, port):
        cmd = [
            'ttyd',
            '--writable',
            '-p', str(port),
            'docker', 'exec', '-it', container_name, '/bin/bash'
        ]
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 