from routes.auth_routes import auth_bp
from routes.task_routes import task_bp
from routes.geo_routes import geo_bp

from routes.ai_routes import ai_bp
from routes.analytics_routes import analytics_bp
from routes.email_routes import email_bp
from routes.integration_routes import integration_bp
from routes.company_routes import company_bp
from routes.report_routes import report_bp
from routes.user_routes import user_bp
from routes.client_routes import client_bp
from routes.hr_routes import hr_bp
from routes.invoice_routes import invoice_bp

__all__ = [
    'auth_bp', 'task_bp', 'geo_bp', 'ai_bp',
    'analytics_bp', 'email_bp', 'integration_bp', 'company_bp',
    'report_bp', 'user_bp', 'client_bp', 'hr_bp', 'invoice_bp'
]