from flask import Blueprint, request, jsonify, make_response
import logging
from services.terminal_service import TerminalService

logger = logging.getLogger(__name__)
terminal_bp = Blueprint('terminal', __name__, url_prefix='/api/ttyd')
terminal_service = TerminalService()

@terminal_bp.route('/getOwnNodes', methods=['GET'])
def get_own_nodes():
    """Get terminal URLs for all user's nodes"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'user_id parameter is required'}), 400

        result = terminal_service.get_own_nodes(user_id, request.host)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Failed to retrieve containers: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@terminal_bp.route('/<container_name>')
def start_ttyd(container_name):
    """Start ttyd terminal for a specific container"""
    try:
        session_id = request.headers.get('X-Session-ID') or \
                    request.cookies.get('ttyd_session') or \
                    terminal_service.generate_session_id()

        result = terminal_service.start_ttyd(container_name, session_id, request.host)
        return make_session_response(result, session_id)

    except Exception as e:
        logger.error(f"ttyd failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@terminal_bp.route('/temporary_session')
def init_ttyd_session():
    """Initialize a temporary ttyd session"""
    try:
        session_id = request.cookies.get('ttyd_session') or terminal_service.generate_session_id()
        response = jsonify({
            'status': 'success',
            'session_id': session_id
        })
        response.set_cookie(
            'ttyd_session',
            value=session_id,
            max_age=86400,
            httponly=True,
            secure=False,  # TODO? True in production with HTTPS
            samesite='Lax'
        )
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def make_session_response(result, session_id):
    """Create a session response with proper headers and cookies"""
    response = jsonify(result)
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