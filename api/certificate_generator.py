"""
Vercel-compatible Certificate Generator
Handles temporary file system and serverless constraints
"""
import os
import sys
import tempfile
from datetime import datetime
import secrets
import string
import sqlite3

# Try to import full dependencies, fall back gracefully
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import qrcode
    from PIL import Image as PILImage
    FULL_FEATURES = True
except ImportError as e:
    FULL_FEATURES = False
    print(f"⚠️ Limited features available: {e}")

class VercelCertificateGenerator:
    """Certificate generator optimized for Vercel deployment"""
    
    def __init__(self, database_path: str = None):
        """Initialize generator with Vercel-friendly paths"""
        # Use temporary directory for Vercel
        self.temp_dir = '/tmp'
        self.database_path = database_path or '/tmp/certificates.db'
        
        # Create directories
        self.certificates_dir = os.path.join(self.temp_dir, 'certificates')
        self.qr_codes_dir = os.path.join(self.temp_dir, 'qr_codes')
        
        os.makedirs(self.certificates_dir, exist_ok=True)
        os.makedirs(self.qr_codes_dir, exist_ok=True)
        
        self.setup_database()
    
    def setup_database(self):
        """Setup SQLite database in temporary directory"""
        try:
            conn = sqlite3.connect(self.database_path)
            
            # Check if email and phone columns exist, add if missing
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(certificates)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Create table if not exists
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
            
            # Add email column if missing
            if 'email' not in columns:
                try:
                    conn.execute('ALTER TABLE certificates ADD COLUMN email TEXT')
                    print("✅ Added email column to database")
                except sqlite3.Error:
                    pass  # Column might already exist
            
            # Add phone column if missing
            if 'phone' not in columns:
                try:
                    conn.execute('ALTER TABLE certificates ADD COLUMN phone TEXT')
                    print("✅ Added phone column to database")
                except sqlite3.Error:
                    pass  # Column might already exist
            
            conn.commit()
            conn.close()
            print(f"✅ Database setup complete: {self.database_path}")
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
    
    def generate_certificate_id(self):
        """Generate unique certificate ID"""
        return f"CERT_{secrets.token_hex(4).upper()}"
    
    def generate_certificate(self, recipient_name, event_name, event_date, 
                           organization, recipient_email=None, recipient_phone=None):
        """Generate certificate with PDF and QR code"""
        try:
            certificate_id = self.generate_certificate_id()
            generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            pdf_path = None
            qr_path = None
            
            if FULL_FEATURES:
                # Generate PDF certificate
                pdf_filename = f"certificate_{certificate_id}.pdf"
                pdf_path = os.path.join(self.certificates_dir, pdf_filename)
                
                # Generate QR code
                qr_filename = f"qr_{certificate_id}.png"
                qr_path = os.path.join(self.qr_codes_dir, qr_filename)
                
                # Create PDF
                self._create_pdf_certificate(
                    pdf_path, certificate_id, recipient_name, 
                    event_name, event_date, organization, generated_date
                )
                
                # Create QR code
                verification_url = f"https://your-app.vercel.app/verify/{certificate_id}"
                self._create_qr_code(verification_url, qr_path)
            
            # Save to database
            self._save_to_database(
                certificate_id, recipient_name, event_name, event_date,
                organization, generated_date, pdf_path, qr_path,
                recipient_email, recipient_phone
            )
            
            return {
                'success': True,
                'certificate_id': certificate_id,
                'pdf_path': pdf_path,
                'qr_path': qr_path,
                'message': f"Certificate generated successfully: {certificate_id}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Certificate generation failed: {str(e)}"
            }
    
    def _create_pdf_certificate(self, pdf_path, cert_id, name, event, date, org, gen_date):
        """Create PDF certificate"""
        if not FULL_FEATURES:
            return
            
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Certificate title
        story.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        story.append(Spacer(1, 20))
        
        # Main content
        story.append(Paragraph("This is to certify that", styles['Normal']))
        story.append(Spacer(1, 10))
        
        name_style = ParagraphStyle('NameStyle', parent=styles['Heading2'], 
                                   fontSize=18, alignment=TA_CENTER)
        story.append(Paragraph(name, name_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph(f"has successfully completed", styles['Normal']))
        story.append(Spacer(1, 10))
        
        event_style = ParagraphStyle('EventStyle', parent=styles['Heading3'], 
                                    fontSize=14, alignment=TA_CENTER)
        story.append(Paragraph(event, event_style))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph(f"Event Date: {date}", styles['Normal']))
        story.append(Paragraph(f"Organization: {org}", styles['Normal']))
        story.append(Spacer(1, 30))
        
        story.append(Paragraph(f"Certificate ID: {cert_id}", styles['Normal']))
        story.append(Paragraph(f"Generated: {gen_date}", styles['Normal']))
        
        doc.build(story)
    
    def _create_qr_code(self, data, qr_path):
        """Create QR code"""
        if not FULL_FEATURES:
            return
            
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image.save(qr_path)
    
    def _save_to_database(self, cert_id, name, event, date, org, gen_date, 
                         pdf_path, qr_path, email, phone):
        """Save certificate data to database"""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.execute('''
                INSERT INTO certificates 
                (certificate_id, recipient_name, event_name, event_date, 
                 organization, generated_date, pdf_path, qr_path, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cert_id, name, event, date, org, gen_date, pdf_path, qr_path, email, phone))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database save error: {e}")
            raise
    
    def list_certificates(self):
        """List all certificates"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT certificate_id, recipient_name, event_name, event_date, 
                       organization, generated_date, email, phone
                FROM certificates 
                ORDER BY generated_date DESC
            ''')
            
            certificates = []
            for row in cursor.fetchall():
                certificates.append({
                    'certificate_id': row[0],
                    'recipient_name': row[1],
                    'event_name': row[2],
                    'event_date': row[3],
                    'organization': row[4],
                    'generated_date': row[5],
                    'email': row[6],
                    'phone': row[7]
                })
            
            conn.close()
            return certificates
            
        except Exception as e:
            print(f"List certificates error: {e}")
            return []
    
    def verify_certificate(self, certificate_id):
        """Verify certificate exists"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM certificates WHERE certificate_id = ?
            ''', (certificate_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'valid': True,
                    'certificate_id': result[1],
                    'recipient_name': result[2],
                    'event_name': result[3],
                    'event_date': result[4],
                    'organization': result[5],
                    'generated_date': result[6]
                }
            else:
                return {'valid': False}
                
        except Exception as e:
            print(f"Verify certificate error: {e}")
            return {'valid': False, 'error': str(e)}

# For backward compatibility
CertificateGenerator = VercelCertificateGenerator