from net_lab_builder.network_controller import NetworkController


def tree_topology():
    try:
        network_controller = NetworkController()

        # Star 1
        star1_central_node = network_controller.create_node(base_name="star1_central")
        star1_node1 = network_controller.create_node(base_name="star1")
        star1_node2 = network_controller.create_node(base_name="star1")
        star1_node3 = network_controller.create_node(base_name="star1")
        star1_node4 = network_controller.create_node(base_name="star1")

        star1_network1 = network_controller.create_network()
        star1_network2 = network_controller.create_network()
        star1_network3 = network_controller.create_network()
        star1_network4 = network_controller.create_network()

        network_controller.connect_node_to_network(
            star1_network1, star1_central_node, star1_node1
        )
        network_controller.connect_node_to_network(
            star1_network2, star1_central_node, star1_node2
        )
        network_controller.connect_node_to_network(
            star1_network3, star1_central_node, star1_node3
        )
        network_controller.connect_node_to_network(
            star1_network4, star1_central_node, star1_node4
        )

        star1_central_node.start_tcpdump()
        star1_node1.start_tcpdump()
        # star1_node2.start_tcpdump()
        # star1_node3.start_tcpdump()
        # star1_node4.start_tcpdump()

        # Star 2
        star2_central_node = network_controller.create_node(base_name="star2_central")
        star2_node1 = network_controller.create_node(base_name="star2")
        star2_node2 = network_controller.create_node(base_name="star2")
        star2_node3 = network_controller.create_node(base_name="star2")
        star2_node4 = network_controller.create_node(base_name="star2")

        star2_network1 = network_controller.create_network()
        star2_network2 = network_controller.create_network()
        star2_network3 = network_controller.create_network()
        star2_network4 = network_controller.create_network()

        network_controller.connect_node_to_network(
            star2_network1, star2_central_node, star2_node1
        )
        network_controller.connect_node_to_network(
            star2_network2, star2_central_node, star2_node2
        )
        network_controller.connect_node_to_network(
            star2_network3, star2_central_node, star2_node3
        )
        network_controller.connect_node_to_network(
            star2_network4, star2_central_node, star2_node4
        )

        star2_central_node.start_tcpdump()
        star2_node1.start_tcpdump()
        # star2_node2.start_tcpdump()
        # star2_node3.start_tcpdump()
        # star2_node4.start_tcpdump()

        # Tree
        tree_central_node = network_controller.create_node(base_name="tree_central")

        tree_network1 = network_controller.create_network()
        tree_network2 = network_controller.create_network()

        network_controller.connect_node_to_network(
            tree_network1, tree_central_node, star1_central_node
        )
        network_controller.connect_node_to_network(
            tree_network2, tree_central_node, star2_central_node
        )

        tree_central_node.start_tcpdump()

        print("Press Ctrl+C to stop.")
        network_controller.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if network_controller:
            network_controller.stop_all_nodes()
            network_controller.prune_all()


if __name__ == "__main__":
    tree_topology()
