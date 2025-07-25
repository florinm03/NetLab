-- PCAP Database Schema
CREATE DATABASE IF NOT EXISTS pcap_db;
USE pcap_db;

-- Single PCAP files table with all data
CREATE TABLE IF NOT EXISTS pcap_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator VARCHAR(255) NOT NULL COMMENT 'User ID of the creator',
    filename VARCHAR(255) NOT NULL COMMENT 'Original filename',
    file_path VARCHAR(500) NOT NULL COMMENT 'Path to the .pcap file',
    pcap_data LONGBLOB COMMENT 'Binary PCAP file data',
    pcap_json JSON COMMENT 'JSON representation of PCAP data for analysis',
    file_size BIGINT COMMENT 'Size of the file in bytes',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    topology_name VARCHAR(255) COMMENT 'Name of the topology',
    topology_type VARCHAR(100) COMMENT 'Type of topology (ring, mesh, star, etc.)',
    node_count INT COMMENT 'Number of nodes in the topology',
    capture_duration INT COMMENT 'Duration of capture in seconds',
    metadata_json JSON COMMENT 'Complete metadata JSON',
    connections_json JSON COMMENT 'Connections data JSON',
    connection_count INT COMMENT 'Number of connections',
    INDEX idx_creator (creator),
    INDEX idx_created_at (created_at),
    INDEX idx_topology_type (topology_type)
);

-- Insert some sample data for testing
INSERT INTO pcap_files (
    creator, 
    filename, 
    file_path, 
    file_size, 
    topology_name, 
    topology_type, 
    node_count, 
    capture_duration,
    metadata_json,
    connections_json,
    connection_count
) VALUES
(
    'guest_rnlqkm', 
    'sample_ring.pcap', 
    '/pcap_storage/sample_ring.pcap', 
    1024000, 
    'Ring Topology', 
    'ring', 
    4, 
    300,
    '{"topology": "ring", "nodes": 4, "capture_start": "2024-01-01T10:00:00Z", "capture_end": "2024-01-01T10:05:00Z", "total_packets": 15000, "protocols": ["TCP", "UDP", "ICMP"]}',
    '{"connections": [{"source": "node1", "target": "node2", "type": "ethernet"}, {"source": "node2", "target": "node3", "type": "ethernet"}, {"source": "node3", "target": "node4", "type": "ethernet"}, {"source": "node4", "target": "node1", "type": "ethernet"}]}',
    4
),
(
    'guest_rnlqkm', 
    'sample_mesh.pcap', 
    '/pcap_storage/sample_mesh.pcap', 
    2048000, 
    'Mesh Topology', 
    'mesh', 
    6, 
    600,
    '{"topology": "mesh", "nodes": 6, "capture_start": "2024-01-01T11:00:00Z", "capture_end": "2024-01-01T11:10:00Z", "total_packets": 25000, "protocols": ["TCP", "UDP", "ICMP", "ARP"]}',
    '{"connections": [{"source": "node1", "target": "node2", "type": "ethernet"}, {"source": "node1", "target": "node3", "type": "ethernet"}, {"source": "node2", "target": "node4", "type": "ethernet"}, {"source": "node3", "target": "node5", "type": "ethernet"}, {"source": "node4", "target": "node6", "type": "ethernet"}, {"source": "node5", "target": "node6", "type": "ethernet"}]}',
    6
); 