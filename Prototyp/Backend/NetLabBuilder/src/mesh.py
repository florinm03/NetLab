from net_lab_builder.network_controller import NetworkController


def mesh_topology():
    try:
        network_controller = NetworkController()
        node1 = network_controller.create_node(base_name="node")
        node2 = network_controller.create_node(base_name="node")
        node3 = network_controller.create_node(base_name="node")
        node4 = network_controller.create_node(base_name="node")
        node5 = network_controller.create_node(base_name="node")

        network1 = network_controller.create_network()
        network2 = network_controller.create_network()
        network3 = network_controller.create_network()
        network4 = network_controller.create_network()
        network5 = network_controller.create_network()

        network_controller.connect_node_to_network(
            network1, node1, node2, node3, node4, node5
        )
        network_controller.connect_node_to_network(
            network2, node2, node3, node4, node5, node1
        )
        network_controller.connect_node_to_network(
            network3, node3, node4, node5, node1, node2
        )
        network_controller.connect_node_to_network(
            network4, node4, node5, node1, node2, node3
        )
        network_controller.connect_node_to_network(
            network5, node5, node1, node2, node3, node4
        )
    finally:
        if network_controller:
            network_controller.stop_all_nodes()
            network_controller.prune_all()


if __name__ == "__main__":
    mesh_topology()
