import logging
import sys
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from collections import defaultdict
from contextlib import closing
import subprocess
import uuid
import socket
import docker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
active_sessions = defaultdict(dict)  # {container_name: {session_id: port}}
client = docker.from_env()

# CORS Configuration
CORS(app,
    supports_credentials=True)

# @app.before_request
# def handle_options():
#     if request.method == "OPTIONS":
#         response = make_response()
#         response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
#         response.headers.add("Access-Control-Allow-Credentials", "true")
#         response.headers.add("Access-Control-Allow-Headers", "Content-Type,X-Session-ID")
#         response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
#         return response

@app.route('/')
def home():
    return "NetLabBuilder API is running! Use /api/start-container to begin."

# Return the user's nodes
@app.route('/api/user-topologies/<user_id>', methods=['GET'])
def get_user_topologies(user_id):
    try:
        # Get all containers for this user
        containers = client.containers.list(
            filters={'name': f'{user_id}'}
        )

        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'nodes': [c.name for c in containers],
            'running': [c.status == 'running' for c in containers],
        }), 200

    except Exception as e:
        logger.error(f"Failed to get topologies: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/start-topology', methods=['POST'])
# TODOs check if the docker container for this userid exists and kill it if called again,
# or at least warn the user that the topology is already running
# a check if the container successfully has been started and return the status
def start_topology():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        topology_name = data.get('topology')
        print("data:", data)
        print("user_id:", user_id)
        print("topology_name:", topology_name)

        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        # Construct the file path
        topology_script = f"../topologies_by_userid/{topology_name}_by_user.py"
        print("topology_script:", topology_script)

        # Execute the topology script in background
        process = subprocess.Popen([
            'python3',
            topology_script,
            user_id
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Immediately return success while the topology runs in background
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'topology': topology_name,
            'pid': process.pid,
            'message': f'Topology {topology_name} started for user {user_id}'
        }), 202  # 202 Accepted status code for async operations

    except Exception as e:
        logger.error(f"Topology start failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': 'Check server logs for more information'
        }), 500

# @app.route('/api/stop-topology/<user_id>', methods=['POST'])
# def stop_topology(user_id):
#     try:
#         # Get all containers for this user
#         containers = client.containers.list(
#             filters={'name': f'node-{user_id}'}
#         )

#         stopped_containers = []
#         for container in containers:
#             container.stop()
#             stopped_containers.append(container.name)

#         # Get all networks for this user
#         networks = client.networks.list(
#             names=[f'net-{user_id}-1', f'net-{user_id}-2', f'net-{user_id}-3']
#         )

#         removed_networks = []
#         for network in networks:
#             network.remove()
#             removed_networks.append(network.name)

#         return jsonify({
#             'status': 'success',
#             'user_id': user_id,
#             'stopped_containers': stopped_containers,
#             'removed_networks': removed_networks
#         }), 200

#     except Exception as e:
#         logger.error(f"Failed to stop topology: {str(e)}")
#         return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/start-container', methods=['POST'])
def start_container():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id') # noch wird keine session id erstellt

        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id required'}), 400

        container_name = f"frr-NODE-{user_id}-{str(uuid.uuid4())[:8]}"
        logger.info(f"Creating container: {container_name}")

        # Create the container
        container = client.containers.run(
            'frrouting/frr:latest',
            name=container_name,
            detach=True,
            tty=True,
            stdin_open=True,
            network_mode='bridge'
        )

        # Link container to session if provided
        if session_id:
            active_sessions[container_name][session_id] = None

        return jsonify({
            'status': 'success',
            'container_id': container.id,
            'container_name': container_name,
            'session_id': session_id,
            'details': {
                'image': 'frrouting/frr:latest',
                'status': container.status,
            }
        }), 201

    except Exception as e:
            logger.error(f"ttyd failed: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ttyd/getOwnNodes', methods=['GET'])
def get_own_nodes():
    try:
        user_id = request.args.get('user_id')
        print(f"user_id: {user_id}")
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

        # Get all containers for this user
        containers = client.containers.list(
            filters={'name': f'{user_id}'}
        )
        print(f"containers: {containers}")

        if not containers:
            return jsonify({
                'status': 'success',
                'message': 'No containers found for this user',
                'terminals': []
            }), 200

        terminal_urls = []
        used_ports = set()  # Track ports we've already assigned
        min_port = 8000
        max_port = 9000

        for container in containers:
            try:
                # Keep trying ports until we find an available one
                port = None
                for _ in range(50):
                    candidate_port = find_free_port(min_port, max_port)
                    if candidate_port not in used_ports and not is_port_in_use(candidate_port):
                        port = candidate_port
                        min_port = candidate_port + 1
                        max_port = candidate_port + 10
                        break
                if port is None:
                    raise RuntimeError("Could not find available port")

                used_ports.add(port)
                start_ttyd_process(container.name, port)

                terminal_urls.append({
                    'container_name': container.name,
                    'url': f'http://{request.host.split(":")[0]}:{port}',
                    'port': port,
                    'status': container.status
                })

            except Exception as e:
                logger.error(f"Failed to start ttyd for {container.name}: {str(e)}")
                terminal_urls.append({
                    'container_name': container.name,
                    'error': str(e),
                    'status': 'failed'
                })
        print(f"terminal_urls: {terminal_urls}")
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'terminals': terminal_urls
        }), 200

    except Exception as e:
        logger.error(f"Failed to retrieve containers: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/ttyd/<container_name>')
def start_ttyd(container_name):
    try:
        # Check container exists and is running
        try:
            container = client.containers.get(container_name)
            if container.status != 'running':
                container.start()
                logger.info(f"Started container: {container_name}")
        except Exception as e:
            logger.error(f"Container {container_name} not found: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Container {container_name} not found'
            }), 404

        # Session management
        session_id = request.headers.get('X-Session-ID') or \
                    request.cookies.get('ttyd_session') or \
                    str(uuid.uuid4())

        # Reuse existing session if valid
        if session_id in active_sessions.get(container_name, {}):
            port = active_sessions[container_name][session_id]
            if is_port_in_use(port):
                return make_session_response(session_id, port)
            del active_sessions[container_name][session_id]

        # Create new session
        port = find_free_port()
        start_ttyd_process(container_name, port)
        active_sessions[container_name][session_id] = port

        return make_session_response(session_id, port)

    except Exception as e:
        logger.error(f"ttyd failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/ttyd/temporary_session')
def init_ttyd_session():
    try:
        session_id = request.cookies.get('ttyd_session') or str(uuid.uuid4())
        response = jsonify({
            'status': 'success',
            'session_id': session_id
        })
        response.set_cookie(
            'ttyd_session',
            value=session_id,
            max_age=86400,
            httponly=True,
            secure=False,  # True in production with HTTPS
            samesite='Lax'
        )
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def make_session_response(session_id, port):
    response = jsonify({
        'status': 'success',
        'url': f'http://{request.host.split(":")[0]}:{port}',
        'port': port,
        'session_id': session_id
    })
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.set_cookie(
        'ttyd_session',
        value=session_id,
        max_age=86400,
        httponly=True,
        secure=False,
        samesite='Lax'
    )
    return response

def start_ttyd_process(container_name, port):
    subprocess.Popen([
        'ttyd', '--writable', '-p', str(port),
        '-t', 'enableTrzsz=true',
        '-t', 'enableZmodem=true',
        '-t', 'termType=xterm-256color',
        'docker', 'exec', '-it', container_name, 'bash', '--login'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port(min = None, max = None):
    for port in range(min or 8000, max or 9000):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free ports in range")

@app.route('/api/validate-python', methods=['POST'])
def validate_python():
    data = request.get_json()
    code = data.get('code')
    # Syntax check only
    try:
        compile(code, '<string>', 'exec')
        return jsonify({"success": True})
    except SyntaxError as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
