import time
from typing import List
from ..utils import create_ipv4_from_subnet
from .node import Node
from docker.models.networks import Network as DockerNetwork


class Network:
    """
    A class to represent a Network for a Docker Container.

    Attributes
    ----------
    __docker_network : DockerNetwork
        The Docker Network instance associated with the Network.
    id : str
        The unique identifier of the Docker Network.
    name : str
        The name of the Docker Network.
    containers : list
        List of Containers associated with the Network.
    subnet : str
        The subnet of the Docker Network.
    gateway : str
        The gateway of the Docker Network.

    Methods
    -------
    connect_node(node: Node):
        Connects a specified Node to the Docker Network.

    reload():
        Reloads the Docker Network.

    __get_network_containers() -> list:
        Fetches the list of Containers associated with the Docker Network.
    """

    def __init__(self, docker_network: DockerNetwork) -> None:
        self.__docker_network = docker_network
        self.id = self.__docker_network.id
        self.name = self.__docker_network.name
        self.nodes = self.__get_network_nodes()
        self.subnet = self.__docker_network.attrs["IPAM"]["Config"][0]["Subnet"]
        self.gateway = self.__docker_network.attrs["IPAM"]["Config"][0]["Gateway"]

    def connect_node(self, node: Node) -> None:
        self.__docker_network.reload()
        self.__docker_network.connect(
            node.container,
            ipv4_address=create_ipv4_from_subnet(self.subnet, node.count),
        )
        self.__docker_network.reload()
        # TODO node call should come from NetworkController
        node.add_network(self)

    def reload(self) -> None:
        self.__docker_network.reload()

    def __get_network_nodes(self) -> List[Node]:
        docker_containers = self.__docker_network.containers
        containers = []
        for docker_container in docker_containers:
            containers.append(Node(docker_container))
        return containers
