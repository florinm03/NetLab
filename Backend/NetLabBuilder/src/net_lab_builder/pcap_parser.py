import json
import os
import logging
import warnings
from typing import List, Dict, Optional

# Suppress scapy warnings about network interfaces
warnings.filterwarnings("ignore", category=UserWarning, module="scapy.runtime")
warnings.filterwarnings("ignore", message="No IPv4 address found")

# Suppress scapy logging
import logging
scapy_logger = logging.getLogger("scapy.runtime")
scapy_logger.setLevel(logging.ERROR)

from scapy.all import rdpcap

logger = logging.getLogger(__name__)

def parse_pcap_connections(file_path: str) -> List[Dict]:
    """
    Parse PCAP file and extract connection data with packet counts
    
    Args:
        file_path: Path to the PCAP file
        
    Returns:
        List of connection dictionaries with source, destination, and packet count
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"PCAP file not found: {file_path}")
            return []
            
        packets = rdpcap(file_path)
        connections = {}

        for pkt in packets:
            if pkt.haslayer('IP'):
                src = pkt['IP'].src
                dst = pkt['IP'].dst
                key = (src, dst)
                if key not in connections:
                    connections[key] = 0
                connections[key] += 1

        result = []
        for (src, dst), count in connections.items():
            result.append({
                "source": src,
                "destination": dst,
                "packets": count
            })

        logger.info(f"Parsed {len(result)} connections from PCAP file")
        return result
        
    except Exception as e:
        logger.error(f"Error parsing PCAP file {file_path}: {str(e)}")
        return []

def parse_pcap_connections_from_data(pcap_data: bytes) -> List[Dict]:
    """
    Parse PCAP data from bytes and extract connection data
    
    Args:
        pcap_data: Binary PCAP data
        
    Returns:
        List of connection dictionaries with source, destination, and packet count
    """
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as temp_pcap:
            temp_pcap.write(pcap_data)
            temp_pcap_path = temp_pcap.name
        
        try:
            return parse_pcap_connections(temp_pcap_path)
        finally:
            if os.path.exists(temp_pcap_path):
                try:
                    os.unlink(temp_pcap_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary PCAP file: {e}")
                    
    except Exception as e:
        logger.error(f"Error parsing PCAP data: {str(e)}")
        return []

def convert_connections_to_graph_format(connections: List[Dict]) -> List[Dict]:
    """
    Convert parsed connections to the format expected by the graph visualization
    
    Args:
        connections: List of connection dictionaries from parse_pcap_connections
        
    Returns:
        List of connection dictionaries in graph format
    """
    return [
        {
            "source": conn.get("source", ""),
            "destination": conn.get("destination", ""),
            "packets": conn.get("packets", 0)
        }
        for conn in connections
    ] 