import subprocess
import json
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

def convert_pcap_to_json(pcap_file_path):
    """
    Convert PCAP file to JSON format using tshark
    
    Args:
        pcap_file_path: Path to the PCAP file
        
    Returns:
        JSON string representation of the PCAP data or None if conversion fails
    """
    try:
        subprocess.run(['tshark', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("tshark is not available. Please install Wireshark/tshark.")
        return None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_json:
            temp_json_path = temp_json.name
        
        cmd = [
            'tshark', '-r', pcap_file_path, '-T', 'fields',
            '-e', 'frame.number',
            '-e', 'frame.time_relative',
            '-e', 'ip.src',
            '-e', 'ip.dst',
            '-e', 'ipv6.src',
            '-e', 'ipv6.dst',
            '-e', 'frame.protocols',
            '-e', 'frame.len',
            '-e', '_ws.col.Info',
            '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d'
        ]
        
        tshark_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Python script to convert CSV to JSON
        python_script = '''
import csv, json, sys
try:
    reader = csv.DictReader(sys.stdin)
    data = list(reader)
    print(json.dumps(data, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}), file=sys.stderr)
    sys.exit(1)
'''
        
        python_process = subprocess.Popen(
            ['python3', '-c', python_script],
            stdin=tshark_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = python_process.communicate()
        tshark_process.wait()
        
        if python_process.returncode != 0:
            logger.error(f"Error converting PCAP to JSON: {stderr}")
            return None
        
        try:
            json_data = json.loads(stdout)
            return json.dumps(json_data, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON output: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error during PCAP conversion: {str(e)}")
        return None
    finally:
        if 'temp_json_path' in locals() and os.path.exists(temp_json_path):
            try:
                os.unlink(temp_json_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

def convert_pcap_data_to_json(pcap_data):
    """
    Convert PCAP binary data to JSON format
    
    Args:
        pcap_data: Binary PCAP data
        
    Returns:
        JSON string representation of the PCAP data or None if conversion fails
    """
    try:
        with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as temp_pcap:
            temp_pcap.write(pcap_data)
            temp_pcap_path = temp_pcap.name
        
        return convert_pcap_to_json(temp_pcap_path)
        
    except Exception as e:
        logger.error(f"Error converting PCAP data to JSON: {str(e)}")
        return None
    finally:
        if 'temp_pcap_path' in locals() and os.path.exists(temp_pcap_path):
            try:
                os.unlink(temp_pcap_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary PCAP file: {e}") 