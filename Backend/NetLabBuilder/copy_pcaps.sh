#!/bin/bash

# Create target folder in current directory
mkdir -p ./pcaps

# Run the Docker command to copy .pcap files
docker run --rm \
  -v pcap_data:/data \
  -v "$PWD/pcaps":/host \
  alpine sh -c "cp /data/*.pcap /host/"

echo "PCAP files copied to: $PWD/pcaps"

