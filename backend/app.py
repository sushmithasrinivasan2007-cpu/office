from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

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

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ])

    # Register Blueprints
    app.register_blueprint(auth_bp,        url_prefix='/api/auth')
    app.register_blueprint(task_bp,        url_prefix='/api/tasks')
    app.register_blueprint(geo_bp,         url_prefix='/api/geo')

    app.register_blueprint(ai_bp,          url_prefix='/api/ai')
    app.register_blueprint(analytics_bp,   url_prefix='/api/analytics')
    app.register_blueprint(email_bp,       url_prefix='/api/email')
    app.register_blueprint(integration_bp, url_prefix='/api/integrations')

    app.register_blueprint(report_bp,      url_prefix='/api/reports')
    app.register_blueprint(user_bp,        url_prefix='/api/users')
    app.register_blueprint(company_bp,     url_prefix='/api/company')
    app.register_blueprint(client_bp,      url_prefix='/api/clients')
    app.register_blueprint(hr_bp,          url_prefix='/api/hr')
    app.register_blueprint(invoice_bp,     url_prefix='/api/invoices')

    @app.route('/', methods=['GET'])
    def health_check():
        return jsonify({"status": "success", "message": "Smart Office API is running"}), 200

    # Global error handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
