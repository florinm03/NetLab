from typing import Any
import docker
import docker.errors
from docker.models.containers import ExecResult, Container
from docker.models.networks import Network as DockerNetwork

from net_lab_builder.components.frr_conf import FrrConfig
from net_lab_builder import utils


class NodeNetworkInterface:
    def __init__(self, interface_name, subnet, node_ip_address):
        self.interface_name = interface_name
        self.subnet = subnet
        self.node_ip_address = node_ip_address


class Node:
    """
    A class to represent a Node for a Docker Container.

    Attributes
    ----------
    container : Container
        The Docker Container instance associated with the Node.
    id : str
        The unique identifier of the Docker Container.
    name : str
        The name of the Docker Container.
    image : str
        The image used by the Docker Container.
    status : str
        The status of the Docker Container.
    count : int
        The count extracted from the Docker Container's name.
    interfaces : list
        List of interfaces associated with the Node.

    Methods
    -------
    start():
        Starts the Docker Container.

    stop():
        Stops the Docker Container.

    exec(command: str) -> ExecResult:
        Executes a specified command in the Docker Container.

    add_network(network: Network):
        Adds a specified network to the Docker Container.

    start_tcpdump():
        Starts the tcpdump command for capturing network traffic.

    get_logs() -> str:
        Fetches the logs associated with the Docker Container.

    __get_container_status() -> str:
        Fetches the status of the Docker Container.

    _update_frr_conf(network: Network):
        Updates the FRR (Free Range Routing) configuration of the Docker Container.
    """

    def __init__(self, docker_container: Container) -> None:
        self.container = docker_container
        self.id = self.container.id
        self.name = self.container.name
        self.image = self.container.image
        self._status = self.get_container_status()
        # self.networks = self.get_node_networks()
        self.count = utils.extract_number(self.name)
        self.container.reload()
        self.__logger = utils.LoggerFactory.get_logger(self.name, log_level="INFO")
        self.interfaces = []
        self.frr_config = self._update_frr_conf()

    def start(self) -> None:
        try:
            self.container.start()
            self.container.reload()
            # self.ip_address = self._container.attrs["NetworkSettings"]["IPAddress"]
        except docker.errors.APIError as e:
            raise ValueError("Server error while starting node")

    def stop(self) -> None:
        try:
            self.container.stop()
        except docker.errors.APIError as e:
            raise ValueError("Server error while stopping node")

    def exec(self, command: str) -> ExecResult:
        try:
            return self.container.exec_run(command, stream=True)
        except docker.errors.APIError as e:
            raise ValueError("Server error while executing command")

    def add_network(self, network) -> None:
        self.container.reload()

        self._add_subnet_to_frr_conf(network.subnet)
        # update frr.conf
        # run tcpdump command

    def start_tcpdump(self) -> None:
        self.__logger.info(f"Starting tcpdump for {self.name}")
        self.container.exec_run(
            f"tcpdump -i any -w /pcap/{self.name}.pcap", detach=True
        )

    def get_logs(self) -> Any:
        try:
            return self.container.logs()
        except docker.errors.APIError as e:
            raise ValueError("Server error while getting logs")

    # def get_node_networks(self):
    #     node_networks = []
    #     networks = self.__adapter.get_networks()
    #     if networks is not None:
    #         for network in networks:
    #             network.reload()
    #             for container_values in network.attrs["Containers"].values():
    #                 if container_values["Name"] == self.name:
    #                     container_ip_address = container_values["IPv4Address"].split(
    #                         "/"
    #                     )[0]
    #                     subnet = network.attrs["IPAM"]["Config"][0]["Subnet"]
    #                     node_networks.append(
    #                         NodeNetwork(network.name, subnet, container_ip_address)
    #                     )
    #     return node_networks

    def get_container_status(self):
        self.container.reload()
        return self.container.status

    def _update_frr_conf(self) -> None:
        frr_conf_path = "/etc/frr/frr.conf"
        exec_output = self.container.exec_run(f"cat {frr_conf_path}")[1]
        result = exec_output.decode()
        self.frr_config = FrrConfig(result)

    def _add_subnet_to_frr_conf(self, subnet: str) -> None:
        self._update_frr_conf()
        interface = self.frr_config.add_ospf_network(subnet=subnet)
        self.interfaces.append(interface)
        modified_config = self.frr_config.get_config()
        exec_instance = self.container.exec_run(
            cmd=["sh", "-c", "cat > /etc/frr/frr.conf"],
            stdin=True,
            socket=True,
        )
        socket = exec_instance.output
        socket._sock.sendall(modified_config.encode())
        socket.close()
