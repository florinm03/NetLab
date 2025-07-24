#!/bin/bash
# Testing purposes
mkdir -p ./pcaps

docker run --rm \
  -v pcap_data:/data \
  -v "$PWD/pcaps":/host \
  alpine sh -c "cp /data/*.pcap /host/"

echo "PCAP files copied to: $PWD/pcaps"

