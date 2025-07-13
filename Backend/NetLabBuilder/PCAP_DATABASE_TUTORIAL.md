# PCAP Database Tutorial

## Start Database

```bash
cd Backend/NetLabBuilder
./start_pcap_database.sh
```

## Connect to Database

```bash
# Inside container
docker exec -it pcap-database mysql -u pcap_user -ppcap_user_password pcap_db

# From outside
mysql -h 127.0.0.1 -P 3307 -u pcap_user -ppcap_user_password pcap_db
```

## Database Schema

```sql
CREATE TABLE pcap_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    creator VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    topology_name VARCHAR(255),
    topology_type VARCHAR(100),
    node_count INT,
    capture_duration INT,
    metadata_json JSON,
    connections_json JSON,
    connection_count INT
);
```

## Basic Queries

```sql
-- Show all PCAP files
SELECT * FROM pcap_files;

-- Files by user
SELECT * FROM pcap_files WHERE creator = 'guest_rnlqkm';

-- Extract metadata
SELECT id, filename, JSON_EXTRACT(metadata_json, '$.total_packets') as packets 
FROM pcap_files;

-- Count connections
SELECT id, filename, connection_count FROM pcap_files;

-- Topology statistics
SELECT topology_type, COUNT(*) as count 
FROM pcap_files 
GROUP BY topology_type;
```

## Python Usage

```python
from services.pcap_database_service import PcapDatabaseService

# Initialize service
pcap_service = PcapDatabaseService()

# Save PCAP file
pcap_id = pcap_service.save_pcap_file(
    creator="guest_rnlqkm",
    file_path="/path/to/file.pcap",
    topology_info={"name": "Ring", "type": "ring", "node_count": 4},
    metadata={"total_packets": 15000, "protocols": ["TCP", "UDP"]},
    connections=[{"source": "node1", "target": "node2", "type": "ethernet"}]
)

# Get user's PCAP files
files = pcap_service.get_pcap_files_by_creator("guest_rnlqkm")

# Get specific file
file_data = pcap_service.get_pcap_file_by_id(1)

# Delete file
success = pcap_service.delete_pcap_file(1, "guest_rnlqkm")
```

## Stop Database

```bash
docker-compose -f docker-compose.pcap.yml down
```

## Reset Database

```bash
docker-compose -f docker-compose.pcap.yml down -v
docker-compose -f docker-compose.pcap.yml up -d --build
``` 