"""
Certificate Generation System with PDF and QR Code Integration
Author: Certificate Generator
Date: October 2025
"""

import os
import json
import qrcode
import hashlib
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white, gold
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sqlite3
from typing import Dict, List, Optional

class CertificateGenerator:
    """Main class for generating PDF certificates with QR codes"""
    
    def __init__(self, database_path: str = "certificates.db"):
        """Initialize the certificate generator"""
        self.database_path = database_path
        self.setup_database()
        self.certificate_template_path = "certificate_template.png"
        self.qr_code_size = (100, 100)  # QR code size in pixels
        
    def setup_database(self):
        """Create database to store certificate records"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT UNIQUE,
                recipient_name TEXT,
                email TEXT,
                course_name TEXT,
                completion_date TEXT,
                issue_date TEXT,
                instructor_name TEXT,
                organization TEXT,
                grade TEXT,
                certificate_hash TEXT,
                qr_code_data TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Add is_active column to existing tables if it doesn't exist
        cursor.execute("PRAGMA table_info(certificates)")
        columns = [column[1] for column in cursor.fetchall()]
        # Add optional columns if missing
        if 'is_active' not in columns:
            cursor.execute('ALTER TABLE certificates ADD COLUMN is_active BOOLEAN DEFAULT 1')
            columns.append('is_active')
        if 'email' not in columns:
            cursor.execute('ALTER TABLE certificates ADD COLUMN email TEXT')
            columns.append('email')
        if 'phone' not in columns:
            cursor.execute('ALTER TABLE certificates ADD COLUMN phone TEXT')
            columns.append('phone')
        if 'is_active' not in columns:
            cursor.execute('ALTER TABLE certificates ADD COLUMN is_active BOOLEAN DEFAULT 1')
        
        conn.commit()
        conn.close()
    
    def generate_certificate_id(self, recipient_name: str, course_name: str) -> str:
        """Generate unique certificate ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data = f"{recipient_name}_{course_name}_{timestamp}"
        hash_object = hashlib.md5(data.encode())
        return f"CERT_{hash_object.hexdigest()[:8].upper()}"
    
    def generate_qr_code(self, certificate_data: Dict) -> str:
        """Generate QR code with certificate verification data"""
        # Create QR code data
        qr_data = {
            "certificate_id": certificate_data["certificate_id"],
            "recipient": certificate_data["recipient_name"],
            "course": certificate_data["course_name"],
            "completion_date": certificate_data["completion_date"],
            "verification_url": f"https://verify.certificates.com/{certificate_data['certificate_id']}"
        }
        
        # Convert to JSON string
        qr_string = json.dumps(qr_data, separators=(',', ':'))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        qr_filename = f"qr_{certificate_data['certificate_id']}.png"
        qr_path = os.path.join("qr_codes", qr_filename)
        os.makedirs("qr_codes", exist_ok=True)
        qr_img.save(qr_path)
        
        return qr_path, qr_string
    
    def create_certificate_pdf(self, recipient_data: Dict) -> str:
        """Create PDF certificate with QR code"""
        # Generate certificate ID
        cert_id = self.generate_certificate_id(
            recipient_data["recipient_name"], 
            recipient_data["course_name"]
        )
        
        # Prepare certificate data
        certificate_data = {
            "certificate_id": cert_id,
            "recipient_name": recipient_data["recipient_name"],
            "course_name": recipient_data["course_name"],
            "completion_date": recipient_data["completion_date"],
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "instructor_name": recipient_data.get("instructor_name", ""),
            "organization": recipient_data.get("organization", "Certificate Authority"),
            "grade": recipient_data.get("grade", ""),
            "email": recipient_data.get("email", ""),
            "phone": recipient_data.get("phone", ""),
        }
        
        # Generate QR code
        qr_path, qr_data = self.generate_qr_code(certificate_data)
        
        # Create PDF
        pdf_filename = f"certificate_{cert_id}.pdf"
        pdf_path = os.path.join("certificates", pdf_filename)
        os.makedirs("certificates", exist_ok=True)
        
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Certificate design
        self.draw_certificate_design(c, width, height, certificate_data, qr_path)
        
        c.save()
        
        # Generate certificate hash
        cert_hash = self.generate_certificate_hash(certificate_data)
        
        # Save to database
        self.save_certificate_record(certificate_data, cert_hash, qr_data, pdf_path)
        
        return pdf_path
    
    def draw_certificate_design(self, c: canvas.Canvas, width: float, height: float, 
                               cert_data: Dict, qr_path: str):
        """Draw the certificate design on PDF canvas"""
        
        # Background and border
        c.setFillColor(Color(0.95, 0.95, 0.98))  # Light blue background
        c.rect(0, 0, width, height, fill=1)
        
        # Main border
        c.setStrokeColor(Color(0.2, 0.3, 0.6))  # Dark blue
        c.setLineWidth(8)
        c.rect(30, 30, width-60, height-60, fill=0)
        
        # Inner border
        c.setStrokeColor(gold)
        c.setLineWidth(4)
        c.rect(50, 50, width-100, height-100, fill=0)
        
        # Header
        c.setFillColor(Color(0.2, 0.3, 0.6))
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(width/2, height-120, "CERTIFICATE OF COMPLETION")
        
        # Decorative line
        c.setStrokeColor(gold)
        c.setLineWidth(3)
        c.line(width/2-150, height-140, width/2+150, height-140)
        
        # Recipient name
        c.setFillColor(Color(0.1, 0.1, 0.4))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-200, "This is to certify that")
        
        c.setFillColor(Color(0.6, 0.1, 0.1))  # Dark red
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width/2, height-250, cert_data["recipient_name"].upper())
        
        # Course information
        c.setFillColor(black)
        c.setFont("Helvetica", 18)
        c.drawCentredString(width/2, height-300, "has successfully completed the course")
        
        c.setFillColor(Color(0.2, 0.3, 0.6))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height-340, cert_data["course_name"])
        
        # Date and details
        c.setFillColor(black)
        c.setFont("Helvetica", 14)
        
        # Completion date
        c.drawCentredString(width/2, height-400, f"Completed on: {cert_data['completion_date']}")
        
        # Issue date
        c.drawCentredString(width/2, height-420, f"Issued on: {cert_data['issue_date']}")
        
        # Grade (if provided)
        if cert_data.get("grade"):
            c.drawCentredString(width/2, height-440, f"Grade: {cert_data['grade']}")
        
        # Organization
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height-480, cert_data["organization"])
        
        # Instructor signature area
        if cert_data.get("instructor_name"):
            c.setFont("Helvetica", 12)
            c.drawString(100, 150, "Instructor:")
            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, 130, cert_data["instructor_name"])
            
            # Signature line
            c.setStrokeColor(black)
            c.setLineWidth(1)
            c.line(100, 120, 250, 120)
        
        # Certificate ID
        c.setFont("Helvetica", 10)
        c.drawString(50, 100, f"Certificate ID: {cert_data['certificate_id']}")
        
        # QR Code
        if os.path.exists(qr_path):
            c.drawImage(qr_path, width-180, 80, 100, 100)
            c.setFont("Helvetica", 8)
            c.drawCentredString(width-130, 70, "Scan to verify")
    
    def generate_certificate_hash(self, cert_data: Dict) -> str:
        """Generate hash for certificate integrity"""
        hash_string = f"{cert_data['certificate_id']}{cert_data['recipient_name']}{cert_data['course_name']}{cert_data['completion_date']}"
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def save_certificate_record(self, cert_data: Dict, cert_hash: str, 
                               qr_data: str, file_path: str):
        """Save certificate record to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO certificates 
            (certificate_id, recipient_name, email, course_name, completion_date, 
             issue_date, instructor_name, organization, grade, certificate_hash, 
             qr_code_data, file_path, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cert_data["certificate_id"],
            cert_data["recipient_name"],
            cert_data.get("email", ""),
            cert_data["course_name"],
            cert_data["completion_date"],
            cert_data["issue_date"],
            cert_data.get("instructor_name", ""),
            cert_data["organization"],
            cert_data.get("grade", ""),
            cert_hash,
            qr_data,
            file_path,
            cert_data.get("phone", "")
        ))
        
        conn.commit()
        conn.close()
    
    def verify_certificate(self, certificate_id: str) -> Optional[Dict]:
        """Verify certificate by ID (only active certificates)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM certificates WHERE certificate_id = ? AND is_active = 1
        ''', (certificate_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def list_certificates(self) -> List[Dict]:
        """List all active certificates (excluding deleted ones)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM certificates WHERE is_active = 1 ORDER BY created_at DESC')
        results = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        certificates = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return certificates

    def list_all_certificates(self) -> List[Dict]:
        """List all certificates including deleted ones"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM certificates ORDER BY created_at DESC')
        results = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        certificates = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return certificates

    def soft_delete_certificate(self, certificate_id: str) -> bool:
        """Mark certificate as deleted (soft delete)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE certificates SET is_active = 0 WHERE certificate_id = ?', (certificate_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0

    def restore_certificate(self, certificate_id: str) -> bool:
        """Restore a soft-deleted certificate"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE certificates SET is_active = 1 WHERE certificate_id = ?', (certificate_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0

    def generate_bulk_certificates(self, recipients_data: List[Dict]) -> List[str]:
        """Generate multiple certificates at once"""
        generated_items = []
        
        for recipient_data in recipients_data:
            try:
                pdf_path = self.create_certificate_pdf(recipient_data)
                # get last generated certificate id from the cert path
                cert_id = os.path.splitext(os.path.basename(pdf_path))[0].replace('certificate_', '')
                generated_items.append({
                    'file': pdf_path,
                    'certificate_id': cert_id,
                    'recipient_name': recipient_data.get('recipient_name', ''),
                    'email': recipient_data.get('email', ''),
                    'phone': recipient_data.get('phone', '')
                })
                print(f"✓ Generated certificate for {recipient_data['recipient_name']}")
            except Exception as e:
                print(f"✗ Failed to generate certificate for {recipient_data.get('recipient_name', 'Unknown')}: {str(e)}")
        
        return generated_items

# Example usage and testing
if __name__ == "__main__":
    # Initialize certificate generator
    cert_gen = CertificateGenerator()
    
    # Sample certificate data
    sample_data = {
        "recipient_name": "John Doe",
        "course_name": "Advanced Python Programming",
        "completion_date": "2025-10-01",
        "instructor_name": "Dr. Jane Smith",
        "organization": "Tech Learning Academy",
        "grade": "A+"
    }
    
    # Generate certificate
    print("Generating sample certificate...")
    pdf_path = cert_gen.create_certificate_pdf(sample_data)
    print(f"Certificate generated: {pdf_path}")
    
    # List all certificates
    certificates = cert_gen.list_certificates()
    print(f"\nTotal certificates generated: {len(certificates)}")
    
    for cert in certificates:
        print(f"- {cert['recipient_name']} - {cert['course_name']} ({cert['certificate_id']})")