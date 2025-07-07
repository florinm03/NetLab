import sys
import os
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

from net_lab_builder.network_controller import NetworkController


def tree_topology(user_id = None):
    nc = None
    if user_id is None:
        try:
            user_id = sys.argv[1]
        except IndexError:
            user_id = "guest-user"
    try:
        nc = NetworkController(user_id=user_id)

        star1_central_node = nc.create_node(base_name=f"star1_central-{user_id}")
        star1_node1 = nc.create_node(base_name=f"star1-{user_id}")
        star1_node2 = nc.create_node(base_name=f"star1-{user_id}")
        star1_node3 = nc.create_node(base_name=f"star1-{user_id}")
        star1_node4 = nc.create_node(base_name=f"star1-{user_id}")

        star1_network1 = nc.create_network(name=f"star1-net-{user_id}-1")
        star1_network2 = nc.create_network(name=f"star1-net-{user_id}-2")
        star1_network3 = nc.create_network(name=f"star1-net-{user_id}-3")
        star1_network4 = nc.create_network(name=f"star1-net-{user_id}-4")

        nc.connect_node_to_network(
            star1_network1, star1_central_node, star1_node1
        )
        nc.connect_node_to_network(
            star1_network2, star1_central_node, star1_node2
        )
        nc.connect_node_to_network(
            star1_network3, star1_central_node, star1_node3
        )
        nc.connect_node_to_network(
            star1_network4, star1_central_node, star1_node4
        )

        for node in [star1_central_node, star1_node1, star1_node2, star1_node3, star1_node4]:
            node.start_tcpdump()

        star2_central_node = nc.create_node(base_name=f"star2_central-{user_id}")
        star2_node1 = nc.create_node(base_name=f"star2-{user_id}")
        star2_node2 = nc.create_node(base_name=f"star2-{user_id}")
        star2_node3 = nc.create_node(base_name=f"star2-{user_id}")
        star2_node4 = nc.create_node(base_name=f"star2-{user_id}")

        star2_network1 = nc.create_network(name=f"star2-net-{user_id}-1")
        star2_network2 = nc.create_network(name=f"star2-net-{user_id}-2")
        star2_network3 = nc.create_network(name=f"star2-net-{user_id}-3")
        star2_network4 = nc.create_network(name=f"star2-net-{user_id}-4")

        nc.connect_node_to_network(
            star2_network1, star2_central_node, star2_node1
        )
        nc.connect_node_to_network(
            star2_network2, star2_central_node, star2_node2
        )
        nc.connect_node_to_network(
            star2_network3, star2_central_node, star2_node3
        )
        nc.connect_node_to_network(
            star2_network4, star2_central_node, star2_node4
        )

        for node in [star2_central_node, star2_node1, star2_node2, star2_node3, star2_node4]:
            node.start_tcpdump()

        tree_central_node = nc.create_node(base_name=f"tree_central-{user_id}")

        tree_network1 = nc.create_network(name=f"tree-net-{user_id}-1")
        tree_network2 = nc.create_network(name=f"tree-net-{user_id}-2")

        nc.connect_node_to_network(
            tree_network1, tree_central_node, star1_central_node
        )
        nc.connect_node_to_network(
            tree_network2, tree_central_node, star2_central_node
        )

        tree_central_node.start_tcpdump()

        print("Tree topology running... Press Ctrl+C to stop.")
        nc.pcap_merge()
    except KeyboardInterrupt:
        pass
    finally:
        if nc:
            nc.stop_user_topology()


if __name__ == "__main__":
    tree_topology() 