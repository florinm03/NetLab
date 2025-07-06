import unittest
from unittest.mock import Mock, patch

from src.net_lab_builder.network_controller import NetworkController
from src.net_lab_builder.components.node import Node
from src.net_lab_builder.components.network import Network


class TestNetworkController(unittest.TestCase):
    @patch("src.net_lab_builder.docker_adapter.DockerAdapter")
    @patch("src.net_lab_builder.utils.LoggerFactory.get_logger")
    def setUp(self, mock_logger, mock_adapter):
        self.controller = NetworkController()
        self.controller.adapter = mock_adapter
        self.controller.__logger = mock_logger

    def test_create_node(self):
        node_name = "mock_node_name"
        self.controller._NetworkController__generate_container_name = Mock(
            return_value=node_name
        )
        self.controller.create_node()
        self.controller.adapter.create_node.assert_called_with(name=node_name)

    def test_get_node_by_name_or_id(self):
        node_id = "mock_node_id"
        self.controller.get_node_by_name_or_id(node_id=node_id)
        self.controller.adapter.get_container.assert_called_with(node_id)

    def test_get_nodes(self):
        self.controller.get_nodes()
        self.controller.adapter.get_containers.assert_called_once()

    def test_create_network(self):
        network_name = "mock_network_name"
        self.controller._NetworkController__generate_network_name = Mock(
            return_value=network_name
        )
        self.controller.create_network()
        self.controller.adapter.create_network.assert_called_with(name=network_name)

    def test_get_networks(self):
        self.controller.get_networks()
        self.controller.adapter.get_networks.assert_called_once()

    def test_connect_node_to_network(self):
        network = Mock(spec=Network)
        node = Mock(spec=Node)
        node.name = "mock_node_name"
        self.controller.connect_node_to_network(network, node)
        network.connect_node.assert_called_with(node)

    def test_pcap_merge(self):
        self.controller.pcap_merge()
        self.controller.adapter.pcap_merge.assert_called_once()

    def test_restart_all_nodes(self):
        self.controller.restart_all_nodes()
        self.controller.adapter.restart_all_nodes.assert_called_once()

    def test_stop_all_nodes(self):
        self.controller.stop_all_nodes()
        self.controller.adapter.stop_all_nodes.assert_called_once()

    def test_prune_all(self):
        self.controller.prune_all()
        self.controller.adapter.prune.assert_called_once()


if __name__ == "__main__":
    unittest.main()
