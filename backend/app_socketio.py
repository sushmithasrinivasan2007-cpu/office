from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime
import os

# Import routes
from routes.auth_routes        import auth_bp
from routes.task_routes        import task_bp
from routes.geo_routes         import geo_bp

from routes.ai_routes          import ai_bp
from routes.analytics_routes   import analytics_bp
from routes.email_routes       import email_bp
from routes.integration_routes import integration_bp
from routes.company_routes     import company_bp
from routes.report_routes      import report_bp
from routes.user_routes        import user_bp
from routes.client_routes      import client_bp
from routes.hr_routes          import hr_bp
from routes.invoice_routes     import invoice_bp

# Import services
from services.websocket_service import socketio

def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Load configuration
    app.config.from_object(config_class)

    # Setup CORS
    frontend_url = os.getenv('FRONTEND_URL', '*')
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        frontend_url
    ])

    # Initialize SocketIO with threading (compatible with Python 3.13)
    # For production with gunicorn, use eventlet: pip install eventlet
    async_mode = 'eventlet' if os.getenv('USE_EVENTLET', 'false').lower() == 'true' else 'threading'
    socketio.init_app(app, cors_allowed_origins=[
        "http://localhost:3000", "http://localhost:5173", 
        "http://127.0.0.1:3000", "http://127.0.0.1:5173",
        frontend_url
    ], async_mode=async_mode)

    # Register blueprints
    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(task_bp,        url_prefix='/api/tasks')
    app.register_blueprint(geo_bp,         url_prefix='/api/geo')

    app.register_blueprint(ai_bp,          url_prefix='/api/ai')
    app.register_blueprint(analytics_bp,   url_prefix='/api/analytics')
    app.register_blueprint(email_bp,       url_prefix='/api/email')
    app.register_blueprint(integration_bp, url_prefix='/api/integrations')
    app.register_blueprint(company_bp,     url_prefix='/api/company')
    app.register_blueprint(report_bp,      url_prefix='/api/reports')
    app.register_blueprint(user_bp,        url_prefix='/api/users')
    app.register_blueprint(client_bp,      url_prefix='/api/clients')
    app.register_blueprint(hr_bp,          url_prefix='/api/hr')
    app.register_blueprint(invoice_bp,     url_prefix='/api/invoices')

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Resource not found'}, 404

    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500

    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'services': {
                'websocket': 'active',
                'database': 'connected',
                'ai': 'available'
            }
        }, 200

    # API info
    @app.route('/api', methods=['GET'])
    def api_info():
        return {
            'name': 'SmartOS API',
            'version': '1.0.0',
            'endpoints': {
                'auth': ['/api/auth/register', '/api/auth/login'],
                'tasks': ['/api/tasks/create-task', '/api/tasks/', '/api/tasks/<id>'],
                'geo': ['/api/geo/verify', '/api/geo/geocode'],
                'payments': ['/api/payments/create-order', '/api/payments/verify'],
                'ai': ['/api/ai/parse-task', '/api/ai/summarize', '/api/ai/predict-risk', '/api/ai/smart-plan', '/api/ai/ask'],
                'analytics': ['/api/analytics/dashboard', '/api/analytics/employee', '/api/analytics/benchmark'],
                'email': ['/api/email/daily-summary', '/api/email/weekly-report'],
                'company': ['/api/company/create', '/api/company/<id>/team'],
                'users': ['/api/users/profile/<id>', '/api/users/checkin', '/api/users/checkout'],
                'clients': ['/api/clients', '/api/clients/<id>'],
                'hr': ['/api/hr/leave-requests', '/api/hr/attendance'],
                'invoices': ['/api/invoices', '/api/invoices/<id>/send']
            }
        }, 200

    return app

# For running withSocketIO
if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)