"""
Vercel-compatible Certificate Generator
Handles file storage limitations and serverless environment
"""
import os
import tempfile
from certificate_generator import CertificateGenerator as OriginalGenerator

class VercelCertificateGenerator(OriginalGenerator):
    """Modified certificate generator for Vercel deployment"""
    
    def __init__(self):
        # Use temporary directory for file storage on Vercel
        self.base_dir = '/tmp'
        self.certificates_dir = '/tmp/certificates'
        self.qr_codes_dir = '/tmp/qr_codes'
        
        # Ensure directories exist
        os.makedirs(self.certificates_dir, exist_ok=True)
        os.makedirs(self.qr_codes_dir, exist_ok=True)
        
        # Initialize parent with temp directory
        super().__init__()
        
    def setup_database(self):
        """Setup database with Vercel considerations"""
        import sqlite3
        
        # Use in-memory database for Vercel (stateless)
        # Or connect to external database via environment variable
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:
            # Use external database (PostgreSQL, etc.)
            # This would require additional configuration
            print(f"Using external database: {database_url}")
            # Implement external database connection here
        else:
            # Use SQLite in /tmp for temporary storage
            db_path = '/tmp/certificates.db'
            print(f"Using temporary SQLite database: {db_path}")
            
            conn = sqlite3.connect(db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS certificates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    certificate_id TEXT UNIQUE NOT NULL,
                    recipient_name TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    generated_date TEXT NOT NULL,
                    pdf_path TEXT,
                    qr_path TEXT,
                    email TEXT,
                    phone TEXT
                )
            ''')
            conn.commit()
            conn.close()
            return db_path