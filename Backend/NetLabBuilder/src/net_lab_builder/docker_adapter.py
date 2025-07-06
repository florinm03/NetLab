import os
from pathlib import Path
import time
from typing import Dict, List

import docker
from docker.models.networks import Network as DockerNetwork
from docker.models.containers import Container as DockerContainer
from docker.models.images import Image as DockerImage

from .utils import LoggerFactory

from .config import _config


class DockerAdapter:
    """
    The DockerAdapter class is designed to interface directly with the Docker daemon for the management of Docker objects such as containers, networks, and more. The class serves as the primary point of contact with the Docker daemon and all other components of the package are designed to remain stateless, with the Docker daemon managing the state of objects.

    The class includes methods for creating nodes, setting up and managing Docker networks, checking the health of the Docker daemon, and interacting with Docker containers. It also includes internal methods for initialising Docker images and working with packet capture files.

    Attributes:
        __client: Instance of docker client for communication with Docker daemon.
        __label: Label to identify objects associated with the current project.
        images: Docker images used in the project.
        __pcap_merger: Docker container used for merging pcap files.
        __pcap_volume: Volume used for storing pcap files.
    """

    def __init__(self) -> None:
        self.__logger = LoggerFactory.get_logger(
            "NodeController", log_level=_config["log_level"]
        )
        self.__client = docker.from_env()
        self.__label = _config["label"]
        self.images = self.__init_docker_images()
        self.__pcap_merger = None
        self.__pcap_volume = self.__init_pcap()
        self.__logger.info("DockerAdapter initialized")

    def create_node(
        self,
        name: str,
    ) -> DockerContainer:
        """
        This method creates and starts a new Docker container with a given name using the 'frr-node' image.
        The container is created with specific properties such as 'network_mode' set to 'none', 'privileged' set to True, and 'pcap_data' volume mounted to '/pcap'. The container is also labeled with 'self.__label'.

        If the specified image is not found, an API error occurs, or an error occurs while creating the container, an error is logged and the corresponding exception is re-raised.

        Args:
            name (str): The name to be assigned to the new container.

        Returns:
            DockerContainer: The created Docker container instance.

        Raises:
            docker.errors.ImageNotFound: If the specified image does not exist.
            docker.errors.APIError: If there is an API error while creating the container.
            docker.errors.ContainerError: If there is a container-related error while creating the container.
        """
        image = self.images["frr-node"]
        try:
            self.__logger.debug(f"Creating container {name} from image {image}")
            docker_container = self.__client.containers.create(
                image=image,
                name=name,
                labels=[self.__label],
                network_mode="none",
                privileged=True,
                volumes=["pcap_data:/pcap"],
            )
            docker_container.start()
            return docker_container
        except docker.errors.ImageNotFound:
            self.__logger.error(f"Image {image} not found")
            raise
        except docker.errors.APIError as e:
            self.__logger.error(f"Error creating container: {e}")
            raise
        except docker.errors.ContainerError as e:
            self.__logger.error(f"Error creating container: {e}")
            raise

    def create_network(self, name: str) -> DockerNetwork:
        """
        This method creates a new Docker network with the specified name. The network is a bridge network with a subnet in the '172.100.0.0/16' to '172.254.0.0/16' range, automatically selecting the first unused subnet in that range.
        The method uses the IPAM (IP Address Management) system for subnet and gateway specification.

        The network is labeled with 'self.__label'.

        If no unused subnets are found in the specified range, a ValueError is raised. If an API error occurs while creating the network, an error is logged and the exception is re-raised.

        Args:
            name (str): The name to be assigned to the new network.

        Returns:
            DockerNetwork: The created Docker network instance.

        Raises:
            ValueError: If no unused subnet could be found in the specified range.
            docker.errors.APIError: If there is an API error while creating the network.
        """
        labels = {self.__label: ""}
        # Just iterate from 100 to 255 and find the first free subnet
        subnet_mask = None
        for i in range(101, 255):
            subnet_tmp = f"172.{i}"
            if self.get_network_by_subnet(f"{subnet_tmp}.0.0/16") is None:
                subnet_mask = subnet_tmp
                break
        if subnet_mask is None:
            raise ValueError("No free subnet found")
        ipam_pool = docker.types.IPAMPool(
            subnet=f"{subnet_mask}.0.0/16", gateway=f"{subnet_mask}.0.1"
        )
        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

        try:
            self.__logger.debug(
                f"Creating network {name} with subnet {subnet_mask} and gateway {subnet_mask}.0.1"
            )
            network = self.__client.networks.create(
                name=name,
                driver="bridge",
                ipam=ipam_config,
                labels=labels,
            )
            return network
        except docker.errors.APIError as e:
            self.__logger.error(f"Error creating network: {e}")
            raise

    def check_docker_daemon_health(self) -> bool:
        """
        This method checks the health of the Docker daemon by attempting to ping it. If the ping is successful, the method returns True. If the Docker API raises an error during the ping attempt, the method returns False.

        Returns:
            bool: True if the Docker daemon is healthy and reachable, False otherwise.
        """
        try:
            return self.__client.ping()
        except docker.errors.APIError:
            return False

    def get_containers(self) -> List[DockerContainer]:
        """
        This method retrieves a list of all Docker containers associated with the current project,
        identified by the project label. If an error occurs during the operation, it logs the error.

        Returns:
            list: List of Docker containers associated with the current project.

        Raises:
            docker.errors.APIError: If there is an error retrieving the containers.
        """
        try:
            return self.__client.containers.list(
                all=True, filters={"label": self.__label}
            )
        except docker.errors.APIError as e:
            self.__logger.error(f"Error getting containers: {e}")

    def get_container(self, container_id_or_name: str) -> DockerContainer:
        """
        This method retrieves a Docker container using its id or name. If the container is not found, it returns None. If an error occurs during the operation, it logs the error.

        Args:
            container_id_or_name (str): The id or name of the Docker container to retrieve.

        Returns:
            DockerContainer or None: The Docker container if found, None otherwise.

        Raises:
            docker.errors.APIError: If there is an error retrieving the container.
        """
        try:
            return self.__client.containers.get(container_id=container_id_or_name)
        except docker.errors.NotFound:
            return None
        except docker.errors.APIError as e:
            self.__logger.error(f"Error getting container: {e}")

    def get_networks(self) -> List[DockerNetwork]:
        """
        This method retrieves a list of all Docker networks associated with the current project,
        identified by the project label. If an error occurs during the operation, it logs the error.

        Returns:
            list: List of Docker networks associated with the current project.

        Raises:
            docker.errors.APIError: If there is an error retrieving the networks.
        """
        try:
            return self.__client.networks.list(filters={"label": self.__label})
        except docker.errors.APIError as e:
            self.__logger.error(f"Error getting networks: {e}")

    def get_network_by_id(self, id: str) -> DockerNetwork:
        """
        This method retrieves a Docker network by its id. It uses the Docker client's get method for networks, which
        returns a Docker network instance if a network with the given id exists.

        If no network with the given id is found, an error is logged and the NotFound exception from the Docker API
        is re-raised.

        Args:
            id (str): The id of the network to retrieve.

        Returns:
            DockerNetwork: The Docker network instance with the given id.

        Raises:
            docker.errors.NotFound: If no network with the given id could be found.
        """
        try:
            return self.__client.networks.get(id)
        except docker.error.NotFound:
            self.__logger.error(f"Network {id} not found")
            raise

    def get_network_by_name(self, name: str) -> DockerNetwork:
        """
        This method retrieves a Docker network by its name. It iterates over all networks known to the Docker client until it finds a network with a matching name. Note that this method is not restricted to networks labeled with the project label (self.__label), it considers all networks.

        If no matching network is found, the method now returns None. If an API error occurs while retrieving networks, an error is logged and the exception is re-raised.

        Args:
            name (str): The name of the network to retrieve.

        Returns:
            Optional[DockerNetwork]: The Docker network instance with the given name, or None if no matching network is found.

        Raises:
            docker.errors.APIError: If there is an API error while retrieving networks.
        """
        try:
            for network in self.__client.networks.list():
                if network.name == name:
                    return network
            return None
        except docker.errors.APIError as e:
            self.__logger.error(f"Error getting network: {e}")

    def get_network_by_subnet(self, subnet: str) -> DockerNetwork:
        """
        This method retrieves a Docker network associated with the current project by its subnet.
        If no network with the specified subnet is found, it returns None.

        Args:
            subnet (str): The subnet of the Docker network to retrieve.

        Returns:
            DockerNetwork or None: The Docker network if found, None otherwise.
        """
        for network in self.get_networks():
            if network.attrs["IPAM"]["Config"][0]["Subnet"] == subnet:
                return network
        return None

    def restart_all_nodes(self) -> None:
        for container in self.get_containers():
            container.restart()

    def stop_all_nodes(self) -> None:
        for container in self.get_containers():
            container.stop()

    def prune(self, containers=True, networks=True, volumes=False, images=False) -> None:
        """
        This method performs selective pruning of Docker resources associated with the label specified by 'self.__label'.
        It removes unused or dangling containers, networks, volumes, and images based on the provided boolean arguments.

        Args:
            containers (bool, optional): A flag indicating whether to prune containers. Defaults to True.
            networks (bool, optional): A flag indicating whether to prune networks. Defaults to True.
            volumes (bool, optional): A flag indicating whether to prune volumes. Defaults to True.
            images (bool, optional): A flag indicating whether to prune images. Defaults to True.
        """
        if containers:
            self.__logger.debug("Pruning containers...")
            self.__client.containers.prune(filters={"label": self.__label})
        if networks:
            self.__logger.debug("Pruning networks...")
            self.__client.networks.prune(filters={"label": self.__label})
        if volumes:
            self.__logger.debug("Pruning volumes...")
            self.__client.volumes.prune(filters={"label": self.__label})
        if images:
            self.__logger.debug("Pruning images...")
            self.__client.images.prune(filters={"label": self.__label})

    def pcap_merge(self) -> None:
        """
        This method continuously merges pcap files from all the containers managed by the current instance.
        It reloads the state of the pcap merger container and retrieves the paths of the pcap files from all containers.
        These files are then merged into a single file specified by the 'pcap_merge_target' config value.
        The merge operation repeats at intervals specified by the 'pcap_merge_interval' config value.

        Note:
            This is a continuous loop intended to be used with an exception interrupt. Without an interrupt, this method will keep running indefinitely.
        """
        while True:
            self.__pcap_merger.reload()
            pcap_files = self.__get_pcap_files()
            pcap_files_str = " ".join(pcap_files)
            command = f"mergecap -w {_config['pcap_merge_target']} {pcap_files_str}"
            self.__logger.info(
                f"Merge pcap files to {_config['pcap_merge_target']}: {pcap_files_str}"
            )
            try:
                self.__pcap_merger.exec_run(command)
            except docker.errors.APIError as e:
                self.__logger.error(f"Error while merging pcap files: {e.explanation}")
                raise
            time.sleep(_config["pcap_merge_interval"])

    def remove_container_from_none_network(self, container: DockerContainer) -> None:
        """
        This method removes a given Docker container from the 'none' network. The method first retrieves the 'none' network and reloads its state to ensure the latest status. It then checks if the provided Docker container is in the 'none' network. If so, it disconnects the container from the network.
        Finally, it reloads the state of the container to reflect any changes.

        Args:
            container (DockerContainer): The Docker container to be disconnected from the 'none' network.

        Note:
            DockerContainer is an alias for Container in docker.models.containers module.
        """
        none_network = self.get_network_by_name("none")
        none_network.reload()
        if container in none_network.containers:
            try:
                none_network.disconnect(container)
            except docker.errors.APIError as e:
                self.__logger.error(
                    f"Error disconnecting container {container.name} from none network: {e}"
                )
                raise
        container.reload()

    def __init_docker_images(self) -> Dict[str, DockerImage]:
        """
        This method initializes Docker images from Dockerfiles located in the 'dockerfiles' directory.
        It first fetches the Dockerfiles, then tries to get the corresponding Docker images.
        If an image does not exist, it triggers the image build process.
        Finally, it returns a dictionary mapping Dockerfiles to Docker images.

        Raises:
            ValueError: If no Dockerfiles were found in the specified directory.

        Returns:
            Dict[str, DockerImage]: A dictionary where keys are Dockerfile names and values are corresponding DockerImage objects.
        """
        dockerfiles = self.__get_dockerfiles()
        if len(dockerfiles) == 0:
            self.__logger.error("No dockerfiles found")
            raise ValueError("No dockerfiles found")
        self.__logger.debug(f"Found dockerfiles: {dockerfiles}")

        images = {}
        for dockerfile in dockerfiles:
            try:
                image = self.__client.images.get(f"{dockerfile}-image")
            except docker.errors.ImageNotFound:
                self.__logger.debug(
                    f"Image {dockerfile}-image not found. Building image..."
                )
                image = self.__build_docker_image(dockerfile)
            images[dockerfile] = image
        self.__logger.debug(f"Initialized docker images: {images}")
        return images

    def __get_dockerfiles(self) -> List[str]:
        """
        This method searches for Dockerfiles in the 'dockerfiles' directory. It checks each sub-directory for the presence of a 'Dockerfile' and appends the sub-directory name to a list if a Dockerfile is found.

        Returns:
            List[str]: A list of sub-directory names where Dockerfiles were found.
        """
        path = Path(__file__).parent.resolve().__str__() + "/dockerfiles/"
        dockerfiles = []
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Check if 'Dockerfile' exists in the sub-directory
                    if os.path.isfile(os.path.join(entry.path, "Dockerfile")):
                        dockerfiles.append(entry.name)
        return dockerfiles

    def __build_docker_image(self, dockerfile: str) -> DockerImage:
        """
        This method builds a Docker image from a specified Dockerfile. The Dockerfile is located based on the provided dockerfile name. The resulting Docker image is tagged with the dockerfile name appended by '-image'.

        Args:
            dockerfile (str): The name of the Dockerfile from which to build the Docker image.

        Raises:
            ValueError: If an error was encountered during the build process.

        Returns:
            DockerImage: The Docker image object built from the Dockerfile.
        """
        dict_path = (
            Path(__file__).parent.resolve().__str__() + "/dockerfiles/" + dockerfile
        )
        file_path = dict_path + "/Dockerfile"
        image_name = f"{dockerfile}-image"
        try:
            image = self.__client.images.build(
                path=dict_path,
                dockerfile=file_path,
                tag=image_name,
                labels={self.__label: ""},
            )[0]
            return image
        except docker.errors.BuildError as e:
            self.__logger.error(e)
            raise ValueError(f"BuildError while building image {image_name}")
        except docker.errors.APIError as e:
            self.__logger.error(e)
            raise ValueError(f"APIError while building image {image_name}")

    def __init_pcap(self) -> None:
        """
        This method initializes the 'pcap_data' volume if it does not exist and starts a new container
        using the 'linuxserver/wireshark' image if a container with the name '{self.__label}-pcap-merger'
        does not already exist. The new container is detached, labeled with 'self.__label',
        and the 'pcap_data' volume is mounted to '/pcap' in the container.
        """
        if "pcap_data" not in self.__client.volumes.list():
            self.__client.volumes.create(name="pcap_data", labels={self.__label: ""})

        if not self.get_container(f"{self.__label}-pcap-merger"):
            self.__pcap_merger = self.__client.containers.run(
                image="linuxserver/wireshark",
                name=f"{self.__label}-pcap-merger",
                detach=True,
                volumes=["pcap_data:/pcap"],
                labels=[self.__label],
            )
            self.__pcap_merger.reload()

    def __get_pcap_files(self) -> List[str]:
        """
        This method scans all the containers managed by the current instance, excluding the one named '{self.__label}-pcap-merger',
        and attempts to locate a pcap file in the '/pcap' directory of each container. The pcap file is expected to have the same name as the container with a '.pcap' extension.

        If a pcap file is found, its path is appended to the list of pcap file paths to be returned. If a pcap file is not found, a warning message is logged.

        Returns:
            List[str]: A list of paths to the pcap files found in the scanned containers.
        """
        pcap_files = []
        for container in self.get_containers():
            container.reload()
            if container.status == "running":
                if container.name != f"{self.__label}-pcap-merger":
                    pcap_file_path = f"/pcap/{container.name}.pcap"
                    pcap_file_ls = container.exec_run(f"ls {pcap_file_path}")
                    if pcap_file_ls[0] == 0 and pcap_file_path in pcap_file_ls[
                        1
                    ].decode("utf-8"):
                        pcap_files.append(f"/pcap/{container.name}.pcap")
                    else:
                        self.__logger.warning(
                            f"pcap file {pcap_file_path} not found in container {container.name}"
                        )
        return pcap_files
