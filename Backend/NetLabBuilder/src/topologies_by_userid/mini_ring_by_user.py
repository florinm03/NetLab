import sys
import os
from pathlib import Path

# Add parent directory to Python path
parent_dir = str(Path(__file__).parent.parent)  # Gets the parent directory of current file
sys.path.append(parent_dir)

from net_lab_builder.network_controller import NetworkController


def mini_ring_topology(user_id = None):
    nc = None
    if user_id is None:
        try:
            user_id = sys.argv[1]
        except IndexError:
            user_id = "guest-user"
    try:
        nc = NetworkController(user_id=user_id)

        n1 = nc.create_node(base_name=f"node-{user_id}")
        n2 = nc.create_node(base_name=f"node-{user_id}")
        n3 = nc.create_node(base_name=f"node-{user_id}")

        net1 = nc.create_network(name=f"net-{user_id}-1")
        net2 = nc.create_network(name=f"net-{user_id}-2")
        net3 = nc.create_network(name=f"net-{user_id}-3")

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
            nc.stop_user_topology()


if __name__ == "__main__":
    mini_ring_topology()
