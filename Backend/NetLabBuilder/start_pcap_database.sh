#!/bin/bash

# Start PCAP Database Container
echo "Starting PCAP Database..."

# Check if network exists, create if not
if ! docker network ls | grep -q "netlab-network"; then
    echo "Creating netlab-network..."
    docker network create netlab-network
fi

# Build and start the PCAP database
cd "$(dirname "$0")"
docker-compose -f docker-compose.pcap.yml up -d --build

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 30

# Check if database is running
if docker ps | grep -q "pcap-database"; then
    echo "✅ PCAP Database is running on port 3307"
    echo "📊 Database: pcap_db"
    echo "👤 User: pcap_user"
    echo "🔑 Password: pcap_user_password"
    echo "🌐 Access: localhost:3307"
else
    echo "❌ Failed to start PCAP Database"
    exit 1
fi

echo ""
echo "To connect to the database:"
echo "mysql -h localhost -P 3307 -u pcap_user -ppcap_user_password pcap_db"
echo ""
echo "To stop the database:"
echo "docker-compose -f docker-compose.pcap.yml down" 