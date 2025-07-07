import sys
import os
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from net_lab_builder.network_controller import NetworkController


def mesh_topology(user_id = None):
    nc = None
    if user_id is None:
        try:
            user_id = sys.argv[1]
        except IndexError:
            user_id = "guest-user"
    try:
        nc = NetworkController(user_id=user_id)
        
        node1 = nc.create_node(base_name=f"node-{user_id}")
        node2 = nc.create_node(base_name=f"node-{user_id}")
        node3 = nc.create_node(base_name=f"node-{user_id}")
        node4 = nc.create_node(base_name=f"node-{user_id}")
        node5 = nc.create_node(base_name=f"node-{user_id}")

        network1 = nc.create_network(name=f"net-{user_id}-1")
        network2 = nc.create_network(name=f"net-{user_id}-2")
        network3 = nc.create_network(name=f"net-{user_id}-3")
        network4 = nc.create_network(name=f"net-{user_id}-4")
        network5 = nc.create_network(name=f"net-{user_id}-5")

        nc.connect_node_to_network(
            network1, node1, node2, node3, node4, node5
        )
        nc.connect_node_to_network(
            network2, node2, node3, node4, node5, node1
        )
        nc.connect_node_to_network(
            network3, node3, node4, node5, node1, node2
        )
        nc.connect_node_to_network(
            network4, node4, node5, node1, node2, node3
        )
        nc.connect_node_to_network(
            network5, node5, node1, node2, node3, node4
        )

        for node in [node1, node2, node3, node4, node5]:
            node.start_tcpdump()

        print("Mesh topology running... Press Ctrl+C to stop.")
        nc.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if nc:
            nc.stop_user_topology()


if __name__ == "__main__":
    mesh_topology() 