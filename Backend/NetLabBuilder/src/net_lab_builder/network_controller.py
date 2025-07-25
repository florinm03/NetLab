import time
from typing import List

from .utils import LoggerFactory
from .components.network import Network
from .components.node import Node
from .docker_adapter import DockerAdapter
from .config import _config


class NetworkController:
    """
    The NetworkController class is responsible for managing Docker nodes and networks.
    It provides methods for creating, retrieving, connecting nodes to networks and managing system resources.
    """

    def __init__(self, user_id=None):
        """
        Initialize a new instance of the NetworkController class.
        
        Args:
            user_id (str, optional): User ID to create unique labels for isolation
        """
        self.__user_id = user_id
        # Create unique label per user to prevent conflicts
        if user_id:
            self.__label = f"{_config['label']}-{user_id}"
        else:
            self.__label = _config["label"]
            
        self.adapter = DockerAdapter(self.__label)
        self.__logger = LoggerFactory.get_logger(
            "NetworkController", log_level=_config["log_level"]
        )
        self.__logger.info(f"NetworkController initialized with label: {self.__label}")

    def create_node(self, base_name: str = "node") -> Node:
        """
        Create a new Docker node.

        Args:
            base_name (str): The base name of the node. Defaults to 'node'.

        Returns:
            Node: A Node object representing the newly created Docker node.
        """
        node_name = self.__generate_container_name(base_name)
        self.__logger.info(f"Creating node {node_name}")
        docker_container = self.adapter.create_node(name=node_name)
        return Node(docker_container)

    def get_node_by_name_or_id(
        self, node_id: str = None, node_name: str = None
    ) -> Node:
        """
        Retrieve a Docker node by its ID or name.

        Args:
            node_id (str): The ID of the node to retrieve.
            node_name (str): The name of the node to retrieve.

        Returns:
            Node: A Node object representing the Docker node.

        Raises:
            ValueError: If neither node_id nor node_name is set.
        """
        if node_id:
            docker_container = self.adapter.get_container(node_id)
        elif node_name:
            docker_container = self.adapter.get_container_by_name(node_name)
        else:
            raise ValueError("Either node_id or node_name must be set")
        return Node(docker_container)

    def get_nodes(self) -> List[Node]:
        """
        Retrieve all Docker nodes.

        Returns:
            List[Node]: A list of Node objects representing all Docker nodes.
        """
        containers = self.adapter.get_containers()
        nodes = []
        for container in containers:
            nodes.append(Node(container))
        return nodes

    def create_network(self, name: str = None) -> Network:
        """
        Create a new Docker network.

        Args:
            name (str, optional): Custom name for the network. If None, generates a random name.

        Returns:
            Network: A Network object representing the newly created Docker network.
        """
        network_name = name if name else self.__generate_network_name()
        self.__logger.info(f"Creating network {network_name}")
        docker_network = self.adapter.create_network(name=network_name)
        return Network(docker_network)


    def get_networks(self) -> List[Network]:
        """
        Retrieve all Docker networks.

        Returns:
            List[Network]: A list of Network objects representing all Docker networks.
        """
        networks = []
        for docker_network in self.adapter.get_networks():
            docker_network.reload()
            networks.append(Network(docker_network))
        return networks

    def connect_node_to_network(self, network: Network, *nodes: Node) -> None:
        """
        Connect Docker nodes to a network.

        Args:
            network (Network): The network to which nodes will be connected.
            *nodes (Node): Nodes to be connected to the network.
        """
        for node in nodes:
            self.__logger.info(f"Connecting {node.name} to {network.name}")
            self.adapter.remove_container_from_none_network(node.container)
            network.connect_node(node)
        # TODO sleep makes it slow. find a better way to wait for the network to be ready
        time.sleep(2)

        for node in nodes:
            node.container.restart()

    def pcap_merge(self) -> None:
        """
        Merge packet capture (pcap) files at intervals specified in the config.
        """
        self.__logger.info(
            f"Merging pcaps every {_config['pcap_merge_interval']} seconds..."
        )
        self.adapter.pcap_merge()

    def restart_all_nodes(self):
        self.adapter.restart_all_nodes()

    def stop_all_nodes(self):
        self.__logger.info("Stopping all nodes...")
        self.adapter.stop_all_nodes()
        self.__logger.info("All nodes stopped")

    def stop_user_topology(self):
        """
        Stop and clean up only the containers and networks for this specific user.
        """
        self.__logger.info(f"Stopping topology for user {self.__user_id}...")
        self.adapter.stop_all_nodes()
        self.adapter.prune(containers=True, networks=True, volumes=False, images=False)
        self.__logger.info(f"Topology for user {self.__user_id} stopped and cleaned up")

    def prune_all(self):
        """
        Prune all unused Docker objects: containers, networks, images, build cache.
        """
        self.__logger.info("Pruning all...")
        self.adapter.prune()
        self.__logger.info("All pruned")

    def __generate_container_name(self, base_name: str) -> str:
        """
        Generates a unique container name based on the label and the number of containers.

        Args:
            base_name (str): The base name of the container.

        Returns:
            str: A unique container name.
        """
        node_count = 100
        containers = self.adapter.get_containers()
        for node in containers:
            node_count += 1
        return f"{self.__label}_{base_name}_{node_count}"

    def __generate_network_name(self) -> str:
        """
        Generates a unique network name based on the label and the number of networks associated with that label.

        Returns:
            str: A unique network name.
        """
        network_count = 101
        for network in self.adapter.get_networks():
            if self.__label in network.name:
                network_count += 1
        return f"{self.__label}_network_{network_count}"
