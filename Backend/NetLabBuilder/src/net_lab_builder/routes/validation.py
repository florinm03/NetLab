from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)
validation_bp = Blueprint('validation', __name__, url_prefix='/api')

@validation_bp.route('/validate-python', methods=['POST'])
def validate_python():
    """Validate Python code syntax"""
    try:
        data = request.get_json()
        code = data.get('code')
        
        # Syntax check only
        try:
            compile(code, '<string>', 'exec')
            return jsonify({"success": True})
        except SyntaxError as e:
            return jsonify({"error": str(e)})
            
    except Exception as e:
        logger.error(f"Python validation failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500 