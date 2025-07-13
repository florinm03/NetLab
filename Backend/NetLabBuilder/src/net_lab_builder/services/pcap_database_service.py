import mysql.connector
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class PcapDatabaseService:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 3307,
            'user': 'pcap_user',
            'password': 'pcap_user_password',
            'database': 'pcap_db',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection = None

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
        Save PCAP file information to database
        
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
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Insert into single pcap_files table with all data
            insert_query = """
                INSERT INTO pcap_files 
                (creator, filename, file_path, file_size, topology_name, topology_type, 
                 node_count, capture_duration, metadata_json, connections_json, connection_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                creator,
                os.path.basename(file_path),
                file_path,
                file_size,
                topology_info.get('name', 'Unknown'),
                topology_info.get('type', 'unknown'),
                topology_info.get('node_count', 0),
                topology_info.get('capture_duration', 0),
                json.dumps(metadata),
                json.dumps(connections),
                len(connections)
            ))
            
            pcap_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Saved PCAP file with ID: {pcap_id}")
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
            List of PCAP file dictionaries
        """
        try:
            if not self.connect():
                return []

            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT * FROM pcap_files 
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

    def get_pcap_file_by_id(self, pcap_id: int) -> Optional[Dict]:
        """
        Get specific PCAP file by ID
        
        Args:
            pcap_id: PCAP file ID
            
        Returns:
            PCAP file dictionary or None
        """
        try:
            if not self.connect():
                return None

            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM pcap_files WHERE id = %s"
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
        Delete PCAP file from database
        
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
            
            # First get the file path
            select_query = "SELECT file_path FROM pcap_files WHERE id = %s AND creator = %s"
            cursor.execute(select_query, (pcap_id, creator))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"PCAP file {pcap_id} not found or not owned by {creator}")
                return False
            
            file_path = result[0]
            
            # Delete from database (cascade will handle related tables)
            delete_query = "DELETE FROM pcap_files WHERE id = %s AND creator = %s"
            cursor.execute(delete_query, (pcap_id, creator))
            
            # Delete actual file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            
            cursor.close()
            logger.info(f"Deleted PCAP file with ID: {pcap_id}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting PCAP file: {e}")
            return False
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
            
            # Get basic statistics
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
            
            # Get topology breakdown
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