import logging
import uuid
import socket
from contextlib import closing
import subprocess
import docker
from collections import defaultdict
import psutil
import os

logger = logging.getLogger(__name__)

class TerminalService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_sessions = defaultdict(dict)
        self.container_ports = {}  # Maps container_name to port
        self.ttyd_processes = {}  # Maps container_name to process info

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
        
        # Clean up any orphaned ttyd processes
        self._cleanup_orphaned_processes()
        
        terminal_urls = []
        for container in containers:
            try:
                # Check if we already have a ttyd process for this container
                if container.name in self.container_ports:
                    port = self.container_ports[container.name]
                    # Verify the process is still running
                    if self._is_ttyd_process_running(container.name, port):
                        terminal_urls.append({
                            'container_name': container.name,
                            'url': f'http://{host.split(":")[0]}:{port}',
                            'port': port,
                            'status': container.status
                        })
                        continue
                    else:
                        # Process is dead, remove from tracking
                        self._cleanup_container_session(container.name)
                
                # Start new ttyd process for this container
                port = self._start_ttyd_for_container(container.name)
                if port:
                    terminal_urls.append({
                        'container_name': container.name,
                        'url': f'http://{host.split(":")[0]}:{port}',
                        'port': port,
                        'status': container.status
                    })
                else:
                    terminal_urls.append({
                        'container_name': container.name,
                        'error': 'Failed to start ttyd process',
                        'status': 'failed'
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
        
        # Check if we already have a session for this container
        if session_id in self.active_sessions.get(container_name, {}):
            port = self.active_sessions[container_name][session_id]
            if self._is_ttyd_process_running(container_name, port):
                return {
                    'status': 'success',
                    'url': f'http://{host.split(":")[0]}:{port}',
                    'port': port,
                    'session_id': session_id
                }
            else:
                # Process is dead, remove from tracking
                del self.active_sessions[container_name][session_id]
        
        # Check if container already has a ttyd process
        if container_name in self.container_ports:
            port = self.container_ports[container_name]
            if self._is_ttyd_process_running(container_name, port):
                # Reuse existing port for this session
                self.active_sessions[container_name][session_id] = port
                return {
                    'status': 'success',
                    'url': f'http://{host.split(":")[0]}:{port}',
                    'port': port,
                    'session_id': session_id
                }
        
        # Start new ttyd process
        port = self._start_ttyd_for_container(container_name)
        if port:
            self.active_sessions[container_name][session_id] = port
            return {
                'status': 'success',
                'url': f'http://{host.split(":")[0]}:{port}',
                'port': port,
                'session_id': session_id
            }
        else:
            return {
                'status': 'error',
                'message': 'Failed to start ttyd process'
            }

    def _start_ttyd_for_container(self, container_name):
        """Start a ttyd process for a container and return the port"""
        try:
            # Find an available port
            port = self.find_free_port()
            if not port:
                logger.error(f"No available ports for container {container_name}")
                return None
            
            # Start ttyd process
            cmd = [
                'ttyd',
                '--writable',
                '-p', str(port),
                'docker', 'exec', '-it', container_name, '/bin/bash'
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Store process info
            self.ttyd_processes[container_name] = {
                'pid': process.pid,
                'port': port,
                'cmd': cmd
            }
            self.container_ports[container_name] = port
            
            logger.info(f"Started ttyd process for {container_name} on port {port} (PID: {process.pid})")
            return port
            
        except Exception as e:
            logger.error(f"Failed to start ttyd for {container_name}: {str(e)}")
            return None

    def _is_ttyd_process_running(self, container_name, port):
        """Check if ttyd process is still running for a container"""
        if container_name not in self.ttyd_processes:
            return False
        
        process_info = self.ttyd_processes[container_name]
        pid = process_info['pid']
        
        try:
            # Check if process is still running
            process = psutil.Process(pid)
            if process.is_running():
                # Also verify the port is still in use
                return self.is_port_in_use(port)
            else:
                return False
        except psutil.NoSuchProcess:
            return False

    def _cleanup_container_session(self, container_name):
        """Clean up ttyd process for a specific container"""
        if container_name in self.ttyd_processes:
            process_info = self.ttyd_processes[container_name]
            pid = process_info['pid']
            
            try:
                # Kill the process group
                os.killpg(pid, 9)  # SIGKILL
                logger.info(f"Killed ttyd process for {container_name} (PID: {pid})")
            except (OSError, psutil.NoSuchProcess):
                pass  # Process already dead
            
            # Remove from tracking
            del self.ttyd_processes[container_name]
            if container_name in self.container_ports:
                del self.container_ports[container_name]
            
            # Clean up sessions
            if container_name in self.active_sessions:
                del self.active_sessions[container_name]

    def _cleanup_orphaned_processes(self):
        """Clean up any ttyd processes that are no longer associated with running containers"""
        try:
            # Get all running containers
            running_containers = set()
            for container in self.client.containers.list():
                running_containers.add(container.name)
            
            # Check each tracked ttyd process
            containers_to_cleanup = []
            for container_name in list(self.ttyd_processes.keys()):
                if container_name not in running_containers:
                    containers_to_cleanup.append(container_name)
            
            # Clean up orphaned processes
            for container_name in containers_to_cleanup:
                logger.info(f"Cleaning up orphaned ttyd process for {container_name}")
                self._cleanup_container_session(container_name)
                
        except Exception as e:
            logger.error(f"Error during orphaned process cleanup: {str(e)}")

    def cleanup_all_sessions(self, user_id=None):
        """Clean up all ttyd sessions, optionally for a specific user"""
        containers_to_cleanup = []
        
        if user_id:
            # Clean up sessions for specific user
            for container_name in list(self.ttyd_processes.keys()):
                if user_id in container_name:
                    containers_to_cleanup.append(container_name)
        else:
            # Clean up all sessions
            containers_to_cleanup = list(self.ttyd_processes.keys())
        
        for container_name in containers_to_cleanup:
            self._cleanup_container_session(container_name)

    def generate_session_id(self):
        return str(uuid.uuid4())

    def find_free_port(self, min_port=8000, max_port=9000):
        """Find a free port in the specified range"""
        for port in range(min_port, max_port):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    continue
        logger.error(f"No free ports available in range {min_port}-{max_port}")
        return None

    def is_port_in_use(self, port):
        """Check if a port is currently in use"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_ttyd_process(self, container_name, port):
        """Legacy method - kept for compatibility"""
        return self._start_ttyd_for_container(container_name) 