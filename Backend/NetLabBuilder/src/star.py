from net_lab_builder.network_controller import NetworkController


def star_topology():
    try:
        network_controller = NetworkController()
        central_node = network_controller.create_node(base_name="central")
        node1 = network_controller.create_node(base_name="node")
        node2 = network_controller.create_node(base_name="node")
        node3 = network_controller.create_node(base_name="node")
        node4 = network_controller.create_node(base_name="node")

        network1 = network_controller.create_network()
        network2 = network_controller.create_network()
        network3 = network_controller.create_network()
        network4 = network_controller.create_network()

        network_controller.connect_node_to_network(network1, central_node, node1)
        network_controller.connect_node_to_network(network2, central_node, node2)
        network_controller.connect_node_to_network(network3, central_node, node3)
        network_controller.connect_node_to_network(network4, central_node, node4)

        central_node.start_tcpdump()
        node1.start_tcpdump()
        node2.start_tcpdump()
        node3.start_tcpdump()
        node4.start_tcpdump()

        print("Press Ctrl+C to stop.")
        network_controller.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if network_controller:
            network_controller.stop_all_nodes()
            network_controller.prune_all()


if __name__ == "__main__":
    star_topology()
