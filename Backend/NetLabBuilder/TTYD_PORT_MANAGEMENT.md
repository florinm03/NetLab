# TTYD Port Management System

1. **Port Reuse**: The system tracks which containers have active ttyd sessions and reuses existing ports
2. **Process Management**: Uses `psutil` to track and manage ttyd processes
3. **Automatic Cleanup**: Orphaned processes are automatically detected and cleaned up
4. **Session Persistence**: Active sessions are maintained across API calls

### How It Works

#### Container Port Tracking
- `container_ports`: Maps container names to their assigned ports
- `ttyd_processes`: Maps container names to process information (PID, port, command)

#### Process Lifecycle
1. **Check Existing**: When `get_own_nodes` is called, it first checks if a container already has a ttyd process
2. **Verify Process**: Uses `psutil` to verify the process is still running and the port is still in use
3. **Reuse or Create**: If process exists and is healthy, reuse it. Otherwise, create a new one
4. **Cleanup Orphans**: Automatically removes processes for containers that no longer exist

#### Port Assignment
- Uses `find_free_port()` to find available ports in 8000-9000 range
- Tracks used ports to avoid conflicts
- Returns `None` if no ports are available (instead of throwing exception)

### API Endpoints

#### GET `/api/ttyd/status`
Returns status of all ttyd sessions:
```json
{
  "status": "success",
  "data": {
    "active_sessions": 5,
    "container_ports": 5,
    "ttyd_processes": 5,
    "containers": ["container1", "container2"],
    "processes": ["container1", "container2"]
  }
}
```

#### POST `/api/ttyd/cleanup`
Clean up ttyd sessions:
```json
{
  "user_id": "optional_user_id"  // If not provided, cleans all sessions
}
```

### Integration with Topology Service

The topology service automatically cleans up ttyd sessions when:
- A topology is cleared (`clear_topology`)
- Individual nodes are deleted (`delete_node`)

### Manual Cleanup

If you need to manually clean up orphaned ttyd processes:

```bash
# Run the cleanup script
cd Backend/NetLabBuilder
python3 cleanup_ttyd.py
```

This script will:
1. Find all ttyd processes
2. Check which ports are in use
3. Kill all ttyd processes
4. Re-check port usage

### Installation

Make sure to install the dependency:

```bash
pip install psutil==5.9.5
```

### Monitoring

You can monitor the system using the status endpoint:

```bash
curl http://localhost:5050/api/ttyd/status
```