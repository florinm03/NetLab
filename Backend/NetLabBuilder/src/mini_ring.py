from net_lab_builder.network_controller import NetworkController
# tests

def mini_ring_topology():
    nc = None
    try:
        nc = NetworkController()

        n1 = nc.create_node(base_name="node")
        n2 = nc.create_node(base_name="node")
        n3 = nc.create_node(base_name="node")

        net1 = nc.create_network()
        net2 = nc.create_network()
        net3 = nc.create_network()

        nc.connect_node_to_network(net1, n1, n2)
        nc.connect_node_to_network(net2, n2, n3)
        nc.connect_node_to_network(net3, n3, n1)

        for node in [n1, n2, n3]:
            node.start_tcpdump()

        print("Running... Press Ctrl+C to stop.")

        nc.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if nc:
            nc.stop_all_nodes()
            nc.prune_all()


if __name__ == "__main__":
    mini_ring_topology()
