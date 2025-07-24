import logging
import uuid
import docker

logger = logging.getLogger(__name__)

class ContainerService:
    def __init__(self):
        self.client = docker.from_env()

    def start_container(self, user_id, session_id=None):
        """Start a new container for a user"""
        try:
            container_name = f"frr-NODE-{user_id}-{str(uuid.uuid4())[:8]}"
            logger.info(f"Creating container: {container_name}")

            container = self.client.containers.run(
                'frrouting/frr:latest',
                name=container_name,
                detach=True,
                tty=True,
                stdin_open=True,
                network_mode='bridge'
            )

            return {
                'status': 'success',
                'container_id': container.id,
                'container_name': container_name,
                'session_id': session_id,
                'details': {
                    'image': 'frrouting/frr:latest',
                    'status': container.status,
                }
            }

        except Exception as e:
            logger.error(f"Container start failed: {str(e)}")
            raise 