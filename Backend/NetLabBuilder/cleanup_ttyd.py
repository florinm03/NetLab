"""
Script to cleanup orphaned ttyd processes
Run this script to kill all ttyd processes that may be consuming ports
"""

import subprocess
import psutil
import os
import signal

def find_ttyd_processes():
    """Find all ttyd processes"""
    ttyd_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'ttyd':
                ttyd_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return ttyd_processes

def kill_ttyd_processes():
    """Kill all ttyd processes"""
    ttyd_processes = find_ttyd_processes()
    
    if not ttyd_processes:
        print("No ttyd processes found")
        return
    
    print(f"Found {len(ttyd_processes)} ttyd processes:")
    for proc in ttyd_processes:
        print(f"  PID {proc.pid}: {' '.join(proc.cmdline())}")
    
    killed_count = 0
    for proc in ttyd_processes:
        try:
            os.killpg(proc.pid, signal.SIGKILL) # Process Group
            killed_count += 1
            print(f"Killed ttyd process {proc.pid}")
        except (OSError, psutil.NoSuchProcess):
            print(f"Process {proc.pid} already dead")
        except Exception as e:
            print(f"Failed to kill process {proc.pid}: {e}")
    
    print(f"Killed {killed_count} ttyd processes")

def check_ports():
    """Check which ports in 8000-9000 range are in use"""
    import socket
    used_ports = []
    
    for port in range(8000, 9001):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                s.close()
            except OSError:
                used_ports.append(port)
    
    if used_ports:
        print(f"Ports in use in range 8000-9000: {used_ports}")
    else:
        print("No ports in use in range 8000-9000")

if __name__ == "__main__":
    print("=== TTYD Cleanup Script ===")
    print()
    
    print("1. Checking for ttyd processes...")
    ttyd_processes = find_ttyd_processes()
    print(f"Found {len(ttyd_processes)} ttyd processes")
    
    print("\n2. Checking port usage...")
    check_ports()
    
    if ttyd_processes:
        print("\n3. Killing ttyd processes...")
        kill_ttyd_processes()
        
        print("\n4. Re-checking port usage...")
        check_ports()
    else:
        print("\nNo ttyd processes to kill")
    
    print("\nCleanup complete!") 