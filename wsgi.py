"""
Production WSGI Server Configuration for Certificate Generation System
"""
from enhanced_web import app
import os

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

# Production settings
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Database configuration
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///certificates.db')

# File upload limits (adjust as needed)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)