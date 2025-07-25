import logging
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ..pcap_parser import parse_pcap_connections_from_data, convert_connections_to_graph_format
except ImportError:
    from pcap_parser import parse_pcap_connections_from_data, convert_connections_to_graph_format

logger = logging.getLogger(__name__)

class PcapParsingService:
    """
    Service for parsing PCAP files and extracting connection data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_connections_from_pcap_data(self, pcap_data: bytes) -> List[Dict]:
        """
        Extract connection data from PCAP binary data
        
        Args:
            pcap_data: Binary PCAP data
            
        Returns:
            List of connection dictionaries with source, destination, and packet count
        """
        try:
            self.logger.info("Extracting connections from PCAP data...")
            
            connections = parse_pcap_connections_from_data(pcap_data)
            
            if connections:
                self.logger.info(f"Successfully extracted {len(connections)} connections from PCAP data")
                return connections
            else:
                self.logger.warning("No connections found in PCAP data")
                return []
                
        except Exception as e:
            self.logger.error(f"Error extracting connections from PCAP data: {str(e)}")
            return []
    
    def extract_connections_from_file(self, file_path: str) -> List[Dict]:
        """
        Extract connection data from PCAP file
        
        Args:
            file_path: Path to the PCAP file
            
        Returns:
            List of connection dictionaries with source, destination, and packet count
        """
        try:
            self.logger.info(f"Extracting connections from PCAP file: {file_path}")
            
            with open(file_path, 'rb') as f:
                pcap_data = f.read()
            
            return self.extract_connections_from_pcap_data(pcap_data)
            
        except Exception as e:
            self.logger.error(f"Error extracting connections from PCAP file {file_path}: {str(e)}")
            return []
    
    def get_connections_for_graph(self, pcap_data: bytes) -> List[Dict]:
        """
        Get connections in the format expected by the graph visualization
        
        Args:
            pcap_data: Binary PCAP data
            
        Returns:
            List of connection dictionaries in graph format
        """
        try:
            connections = self.extract_connections_from_pcap_data(pcap_data)
            
            graph_connections = convert_connections_to_graph_format(connections)
            
            self.logger.info(f"Converted {len(graph_connections)} connections to graph format")
            return graph_connections
            
        except Exception as e:
            self.logger.error(f"Error getting connections for graph: {str(e)}")
            return []
    
    def get_connections_for_graph_from_file(self, file_path: str) -> List[Dict]:
        """
        Get connections from PCAP file in the format expected by the graph visualization
        
        Args:
            file_path: Path to the PCAP file
            
        Returns:
            List of connection dictionaries in graph format
        """
        try:
            connections = self.extract_connections_from_file(file_path)
            
            graph_connections = convert_connections_to_graph_format(connections)
            
            self.logger.info(f"Converted {len(graph_connections)} connections to graph format from file")
            return graph_connections
            
        except Exception as e:
            self.logger.error(f"Error getting connections for graph from file: {str(e)}")
            return []
    
    def convert_connections_to_graph_format(self, connections: List[Dict]) -> List[Dict]:
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