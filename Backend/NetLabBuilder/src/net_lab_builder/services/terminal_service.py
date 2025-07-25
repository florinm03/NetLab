import logging
import uuid
import socket
from contextlib import closing
import subprocess
import docker
from collections import defaultdict
import psutil
import os
import threading
import time

logger = logging.getLogger(__name__)

class TerminalService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_sessions = defaultdict(dict)
        self.container_ports = {}  # Maps container_name to port
        self.ttyd_processes = {}  # Maps container_name to process info
        self.event_listener_thread = None
        self.should_stop_listener = False
        
        self._start_docker_event_listener()

    def get_own_nodes(self, user_id, host):
        try:
            containers = self.client.containers.list(
                filters={'name': f'{user_id}'}
            )
        except Exception as e:
            logger.error(f"Error getting containers for user {user_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Failed to get containers: {str(e)}',
                'terminals': []
            }
        
        if not containers:
            return {
                'status': 'success',
                'message': 'No containers found for this user',
                'terminals': []
            }
        
        self._cleanup_orphaned_processes()
        
        self.cleanup_orphaned_processes_by_name(user_id)
        
        terminal_urls = []
        for container in containers:
            try:
                if container.name in self.container_ports:
                    port = self.container_ports[container.name]
                    if self._is_ttyd_process_running(container.name, port):
                        terminal_urls.append({
                            'container_name': container.name,
                            'url': f'http://{host.split(":")[0]}:{port}',
                            'port': port,
                            'status': container.status
                        })
                        continue
                    else:
                        self._cleanup_container_session(container.name)
                
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
                del self.active_sessions[container_name][session_id]
        
        if container_name in self.container_ports:
            port = self.container_ports[container_name]
            if self._is_ttyd_process_running(container_name, port):
                self.active_sessions[container_name][session_id] = port
                return {
                    'status': 'success',
                    'url': f'http://{host.split(":")[0]}:{port}',
                    'port': port,
                    'session_id': session_id
                }
        
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
            port = self.find_free_port()
            if not port:
                logger.error(f"No available ports for container {container_name}")
                return None
            
            process_name = f"ttyd_{container_name.replace('-', '_')}"
            
            cmd = [
                'ttyd',
                '--writable',
                '-p', str(port),
                'docker', 'exec', '-it', container_name, '/bin/bash'
            ]
            
            wrapper_script = f"""#!/bin/bash
exec -a "{process_name}" ttyd --writable -p {port} docker exec -it {container_name} /bin/bash
"""
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(wrapper_script)
                wrapper_path = f.name
            
            os.chmod(wrapper_path, 0o755)
            
            process = subprocess.Popen(
                ['/bin/bash', wrapper_path],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid 
            )
            
            self.ttyd_processes[container_name] = {
                'pid': process.pid,
                'port': port,
                'cmd': cmd,
                'name': process_name,
                'wrapper_path': wrapper_path
            }
            self.container_ports[container_name] = port
            
            logger.info(f"Started ttyd process '{process_name}' for {container_name} on port {port} (PID: {process.pid})")
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
            process = psutil.Process(pid)
            if process.is_running():
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
            process_name = process_info.get('name', 'unknown')
            wrapper_path = process_info.get('wrapper_path')
            
            try:
                os.killpg(pid, 9)  # SIGKILL
                logger.info(f"Killed ttyd process '{process_name}' for {container_name} (PID: {pid})")
            except (OSError, psutil.NoSuchProcess):
                logger.debug(f"Process {pid} for {container_name} already dead")
            except Exception as e:
                logger.warning(f"Error killing process {pid} for {container_name}: {str(e)}")
            
            try:
                self._kill_processes_by_name(process_name)
            except Exception as e:
                logger.debug(f"Could not kill processes by name '{process_name}': {str(e)}")
            
            if wrapper_path and os.path.exists(wrapper_path):
                try:
                    os.unlink(wrapper_path)
                    logger.debug(f"Removed wrapper script: {wrapper_path}")
                except Exception as e:
                    logger.warning(f"Could not remove wrapper script {wrapper_path}: {str(e)}")
            
            del self.ttyd_processes[container_name]
            if container_name in self.container_ports:
                del self.container_ports[container_name]
            
            if container_name in self.active_sessions:
                del self.active_sessions[container_name]

    def _cleanup_orphaned_processes(self):
        """Clean up any ttyd processes that are no longer associated with running containers"""
        try:
            running_containers = set()
            try:
                for container in self.client.containers.list():
                    running_containers.add(container.name)
            except Exception as e:
                logger.warning(f"Could not get running containers list: {str(e)}")
                return
            
            containers_to_cleanup = []
            for container_name in list(self.ttyd_processes.keys()):
                if container_name not in running_containers:
                    containers_to_cleanup.append(container_name)
            
            for container_name in containers_to_cleanup:
                logger.info(f"Cleaning up orphaned ttyd process for {container_name}")
                self._cleanup_container_session(container_name)
                
        except Exception as e:
            logger.error(f"Error during orphaned process cleanup: {str(e)}")

    def cleanup_all_sessions(self, user_id=None):
        """Clean up all ttyd sessions, optionally for a specific user"""
        containers_to_cleanup = []
        
        if user_id:
            for container_name in list(self.ttyd_processes.keys()):
                if user_id in container_name:
                    containers_to_cleanup.append(container_name)
        else:
            containers_to_cleanup = list(self.ttyd_processes.keys())
        
        for container_name in containers_to_cleanup:
            self._cleanup_container_session(container_name)
        
        self.cleanup_orphaned_processes_by_name(user_id)

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

    def _kill_processes_by_name(self, process_name):
        """Kill all processes with a specific name"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == process_name or (proc.info['cmdline'] and process_name in ' '.join(proc.info['cmdline'])):
                        logger.info(f"Killing process by name '{process_name}' (PID: {proc.info['pid']})")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            logger.warning(f"Error killing processes by name '{process_name}': {str(e)}")

    def cleanup_orphaned_processes_by_name(self, user_id=None):
        """Clean up orphaned ttyd processes by searching for them by name"""
        try:
            ttyd_pattern = "ttyd_"
            if user_id:
                ttyd_pattern += user_id.replace('-', '_')
            
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and proc.info['name'].startswith(ttyd_pattern):
                        logger.info(f"Found orphaned ttyd process: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed_count > 0:
                logger.info(f"Cleaned up {killed_count} orphaned ttyd processes")
            
        except Exception as e:
            logger.error(f"Error during orphaned process cleanup by name: {str(e)}")

    def _start_docker_event_listener(self):
        """Start a background thread to listen for Docker container events"""
        try:
            self.event_listener_thread = threading.Thread(
                target=self._docker_event_listener_worker,
                daemon=True,
                name="DockerEventListener"
            )
            self.event_listener_thread.start()
            logger.info("Started Docker event listener thread")
        except Exception as e:
            logger.error(f"Failed to start Docker event listener: {str(e)}")

    def _docker_event_listener_worker(self):
        """Worker thread that listens for Docker container events"""
        try:
            for event in self.client.events(
                filters={'type': 'container'},
                decode=True
            ):
                if self.should_stop_listener:
                    break
                
                try:
                    self._handle_docker_event(event)
                except Exception as e:
                    logger.error(f"Error handling Docker event: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Docker event listener error: {str(e)}")
        finally:
            logger.info("Docker event listener thread stopped")

    def _handle_docker_event(self, event):
        """Handle a Docker container event"""
        try:
            event_type = event.get('Type')
            action = event.get('Action')
            container_id = event.get('Actor', {}).get('ID')
            container_name = event.get('Actor', {}).get('Attributes', {}).get('name')
            
            if not container_name:
                return
            
            logger.debug(f"Docker event: {event_type} - {action} - {container_name}")
            
            # Handle container stop/remove events
            if action in ['die', 'stop', 'destroy', 'kill']:
                if container_name in self.ttyd_processes:
                    logger.info(f"Container {container_name} stopped/removed, cleaning up ttyd process")
                    self._cleanup_container_session(container_name)
                else:
                    self._cleanup_orphaned_processes_by_container_name(container_name)
                    
        except Exception as e:
            logger.error(f"Error handling Docker event: {str(e)}")

    def _cleanup_orphaned_processes_by_container_name(self, container_name):
        """Clean up orphaned ttyd processes for a specific container name"""
        try:
            process_name = f"ttyd_{container_name.replace('-', '_')}"
            
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == process_name:
                        logger.info(f"Found orphaned ttyd process for container {container_name}: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed_count > 0:
                logger.info(f"Cleaned up {killed_count} orphaned ttyd processes for container {container_name}")
                
        except Exception as e:
            logger.error(f"Error cleaning up orphaned processes for container {container_name}: {str(e)}")

    def stop_event_listener(self):
        """Stop the Docker event listener thread"""
        self.should_stop_listener = True
        if self.event_listener_thread and self.event_listener_thread.is_alive():
            self.event_listener_thread.join(timeout=5)
            logger.info("Docker event listener stopped")

    def start_ttyd_process(self, container_name, port):
        """"""
        return self._start_ttyd_for_container(container_name) 