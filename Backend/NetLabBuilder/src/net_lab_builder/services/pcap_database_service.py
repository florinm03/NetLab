import mysql.connector
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pcap_converter import convert_pcap_data_to_json
from .pcap_parsing_service import PcapParsingService

logger = logging.getLogger(__name__)

class PcapDatabaseService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 3307,
            'user': 'pcap_user',
            'password': 'pcap_user_password', # TODO env
            'database': 'pcap_db',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection = None
        self.pcap_parsing_service = PcapParsingService()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            logger.info("Connected to PCAP database")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Disconnected from PCAP database")

    def save_pcap_file(self, creator: str, file_path: str, topology_info: Dict, 
                       metadata: Dict, connections: List[Dict]) -> Optional[int]:
        """
        Save PCAP file and metadata to database
        
        Args:
            creator: User ID of the creator
            file_path: Path to the PCAP file
            topology_info: Dictionary with topology information
            metadata: Complete metadata JSON
            connections: List of connection dictionaries
            
        Returns:
            PCAP file ID if successful, None otherwise
        """
        try:
            if not self.connect():
                return None

            cursor = self.connection.cursor()
            
            pcap_data = None
            file_size = 0
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    pcap_data = f.read()
                file_size = len(pcap_data)
            else:
                file_size = metadata.get('file_size', 0)
            
            pcap_json = None
            if pcap_data:
                logger.info("Converting PCAP data to JSON format...")
                pcap_json = convert_pcap_data_to_json(pcap_data)
                if pcap_json:
                    logger.info("PCAP to JSON conversion successful")
                else:
                    logger.warning("PCAP to JSON conversion failed, continuing without JSON data")
            
            real_connections = []
            if pcap_data:
                logger.info("Extracting connections from PCAP data...")
                real_connections = self.pcap_parsing_service.get_connections_for_graph(pcap_data)
                if real_connections:
                    logger.info(f"Successfully extracted {len(real_connections)} connections from PCAP data")
                else:
                    logger.warning("No connections found in PCAP data, using topology connections")
                    real_connections = connections
            
            insert_query = """
                INSERT INTO pcap_files 
                (creator, filename, file_path, pcap_data, pcap_json, file_size, topology_name, topology_type, 
                 node_count, capture_duration, metadata_json, connections_json, connection_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                creator,
                os.path.basename(file_path) if file_path else f"pcap_{creator}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap",
                "database_stored", 
                pcap_data,
                pcap_json,
                file_size,
                topology_info.get('name', 'Unknown'),
                topology_info.get('type', 'unknown'),
                topology_info.get('node_count', 0),
                topology_info.get('capture_duration', 0),
                json.dumps(metadata),
                json.dumps(real_connections),
                len(real_connections)
            ))
            
            pcap_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Saved PCAP file and metadata with ID: {pcap_id}")
            return pcap_id
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error saving PCAP file: {e}")
            return None
        finally:
            self.disconnect()

    def get_pcap_files_by_creator(self, creator: str) -> List[Dict]:
        """
        Get all PCAP files for a specific creator
        
        Args:
            creator: User ID
            
        Returns:
            List of PCAP file dictionaries (without pcap_data for JSON serialization)
        """
        try:
            if not self.connect():
                return []

            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT id, creator, filename, file_path, file_size, topology_name, topology_type, 
                       node_count, capture_duration, metadata_json, connections_json, connection_count,
                       created_at, updated_at
                FROM pcap_files 
                WHERE creator = %s 
                ORDER BY created_at DESC
            """
            
            cursor.execute(query, (creator,))
            results = cursor.fetchall()
            
            cursor.close()
            return results
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return []
        finally:
            self.disconnect()

    def get_pcap_file_by_id(self, pcap_id: int, include_data: bool = False) -> Optional[Dict]:
        """
        Get specific PCAP file by ID
        
        Args:
            pcap_id: PCAP file ID
            include_data: Whether to include pcap_data (for downloads)
            
        Returns:
            PCAP file dictionary or None
        """
        try:
            if not self.connect():
                return None

            cursor = self.connection.cursor(dictionary=True)
            
            if include_data:
                query = "SELECT * FROM pcap_files WHERE id = %s"
            else:
                query = """
                    SELECT id, creator, filename, file_path, file_size, topology_name, topology_type, 
                           node_count, capture_duration, metadata_json, connections_json, connection_count,
                           created_at, updated_at
                    FROM pcap_files WHERE id = %s
                """
            
            cursor.execute(query, (pcap_id,))
            result = cursor.fetchone()
            
            cursor.close()
            return result
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return None
        finally:
            self.disconnect()

    def delete_pcap_file(self, pcap_id: int, creator: str) -> bool:
        """
        Delete PCAP metadata from database
        
        Args:
            pcap_id: PCAP file ID
            creator: User ID (for security)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.connect():
                return False

            cursor = self.connection.cursor()
            
            delete_query = "DELETE FROM pcap_files WHERE id = %s AND creator = %s"
            cursor.execute(delete_query, (pcap_id, creator))
            
            if cursor.rowcount == 0:
                logger.warning(f"PCAP file {pcap_id} not found or not owned by {creator}")
                return False
            
            cursor.close()
            logger.info(f"Deleted PCAP metadata with ID: {pcap_id}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting PCAP metadata: {e}")
            return False
        finally:
            self.disconnect()

    def get_pcap_json_by_id(self, pcap_id: int) -> Optional[str]:
        """
        Get PCAP JSON data by ID (separate method to avoid memory issues)
        
        Args:
            pcap_id: PCAP file ID
            
        Returns:
            JSON string or None
        """
        try:
            if not self.connect():
                return None

            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT pcap_json FROM pcap_files WHERE id = %s"
            cursor.execute(query, (pcap_id,))
            result = cursor.fetchone()
            
            cursor.close()
            return result['pcap_json'] if result else None
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return None
        finally:
            self.disconnect()

    def get_pcap_statistics(self, creator: str) -> Dict:
        """
        Get statistics for a creator's PCAP files
        
        Args:
            creator: User ID
            
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.connect():
                return {}

            cursor = self.connection.cursor(dictionary=True)
            
            stats_query = """
                SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    AVG(file_size) as avg_size,
                    COUNT(DISTINCT topology_type) as topology_types,
                    SUM(node_count) as total_nodes,
                    SUM(capture_duration) as total_duration
                FROM pcap_files 
                WHERE creator = %s
            """
            
            cursor.execute(stats_query, (creator,))
            stats = cursor.fetchone()
            
            topology_query = """
                SELECT topology_type, COUNT(*) as count
                FROM pcap_files 
                WHERE creator = %s 
                GROUP BY topology_type
            """
            
            cursor.execute(topology_query, (creator,))
            topology_stats = cursor.fetchall()
            
            cursor.close()
            
            return {
                'basic_stats': stats,
                'topology_breakdown': topology_stats
            }
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return {}
        finally:
            self.disconnect() 