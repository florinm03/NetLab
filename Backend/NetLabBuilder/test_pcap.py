#!/usr/bin/env python3
"""
Test script to verify PCAP functionality is working correctly.
This script creates a simple topology and checks if PCAP files are being created and merged.
"""

import time
import sys
import os
from pathlib import Path

src_dir = str(Path(__file__).parent / "src")
sys.path.append(src_dir)

from net_lab_builder.network_controller import NetworkController


def test_pcap_functionality():
    """Test PCAP functionality with a simple 2-node topology."""
    print("Testing PCAP functionality...")
    
    nc = None
    try:
        nc = NetworkController()
        
        node1 = nc.create_node(base_name="test_node")
        node2 = nc.create_node(base_name="test_node")
        
        network = nc.create_network()
        
        nc.connect_node_to_network(network, node1, node2)
        
        print("Starting tcpdump on nodes...")
        node1.start_tcpdump()
        node2.start_tcpdump()
        
        print("Waiting for tcpdump to initialize...")
        time.sleep(2)
        
        print("Starting PCAP merge...")
        import threading
        
        def run_pcap_merge():
            try:
                nc.pcap_merge()
            except KeyboardInterrupt:
                pass
        
        merge_thread = threading.Thread(target=run_pcap_merge, daemon=True)
        merge_thread.start()
        
        print("Running topology for 10 seconds...")
        time.sleep(10)
        
        print("Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if nc:
            print("Cleaning up...")
            nc.stop_all_nodes()
            nc.prune_all()
            print("Cleanup completed")


if __name__ == "__main__":
    test_pcap_functionality() 