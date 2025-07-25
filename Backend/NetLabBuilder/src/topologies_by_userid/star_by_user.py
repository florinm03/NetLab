import sys
import os
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from net_lab_builder.network_controller import NetworkController


def star_topology(user_id = None):
    nc = None
    if user_id is None:
        try:
            user_id = sys.argv[1]
        except IndexError:
            user_id = "guest-user"
    try:
        nc = NetworkController(user_id=user_id)
        
        central_node = nc.create_node(base_name=f"central-{user_id}")
        node1 = nc.create_node(base_name=f"node-{user_id}")
        node2 = nc.create_node(base_name=f"node-{user_id}")
        node3 = nc.create_node(base_name=f"node-{user_id}")
        node4 = nc.create_node(base_name=f"node-{user_id}")

        network1 = nc.create_network(name=f"net-{user_id}-1")
        network2 = nc.create_network(name=f"net-{user_id}-2")
        network3 = nc.create_network(name=f"net-{user_id}-3")
        network4 = nc.create_network(name=f"net-{user_id}-4")

        nc.connect_node_to_network(network1, central_node, node1)
        nc.connect_node_to_network(network2, central_node, node2)
        nc.connect_node_to_network(network3, central_node, node3)
        nc.connect_node_to_network(network4, central_node, node4)

        for node in [central_node, node1, node2, node3, node4]:
            node.start_tcpdump()

        print("Star topology running... Press Ctrl+C to stop.")
        nc.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if nc:
            nc.stop_user_topology()


if __name__ == "__main__":
    star_topology() 