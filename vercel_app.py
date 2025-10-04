"""
Vercel-compatible entry point for Certificate Generation System
"""
import os
from enhanced_web import app

# Vercel requires the Flask app to be wrapped for serverless deployment
# Configure for production
app.config['DEBUG'] = False

# Vercel environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-production-key')

# Database configuration - Use environment variable or default
# Note: Vercel is stateless, so consider using external database for production
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['DATABASE_URL'] = database_url

# File storage configuration for Vercel
# Vercel has read-only filesystem except for /tmp directory
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['CERTIFICATE_FOLDER'] = '/tmp/certificates'
app.config['QR_FOLDER'] = '/tmp/qr_codes'

# Ensure temp directories exist
os.makedirs('/tmp/certificates', exist_ok=True)
os.makedirs('/tmp/qr_codes', exist_ok=True)

# For Vercel, we need to export the app as 'app'
# This is the entry point that Vercel will use
def handler(request):
    """Vercel serverless function handler"""
    return app(request.environ, lambda *args: None)

# Also provide direct app access
if __name__ == "__main__":
    app.run()