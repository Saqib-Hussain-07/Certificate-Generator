"""
Simple Certificate Generator Demo
Basic version without external dependencies for testing
"""

import sqlite3
import hashlib
import json
import os
from datetime import datetime

class SimpleCertificateGenerator:
    """Simplified certificate generator for demonstration"""
    
    def __init__(self, database_path="certificates.db"):
        self.database_path = database_path
        self.setup_database()
    
    def setup_database(self):
        """Create database to store certificate records"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificate_id TEXT UNIQUE,
                recipient_name TEXT,
                course_name TEXT,
                completion_date TEXT,
                issue_date TEXT,
                instructor_name TEXT,
                organization TEXT,
                grade TEXT,
                certificate_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Add is_active column to existing tables if it doesn't exist
        cursor.execute("PRAGMA table_info(certificates)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'is_active' not in columns:
            cursor.execute('ALTER TABLE certificates ADD COLUMN is_active BOOLEAN DEFAULT 1')
        
        conn.commit()
        conn.close()
    
    def generate_certificate_id(self, recipient_name, course_name):
        """Generate unique certificate ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data = f"{recipient_name}_{course_name}_{timestamp}"
        hash_object = hashlib.md5(data.encode())
        return f"CERT_{hash_object.hexdigest()[:8].upper()}"
    
    def create_certificate_record(self, recipient_data):
        """Create certificate record in database"""
        cert_id = self.generate_certificate_id(
            recipient_data["recipient_name"], 
            recipient_data["course_name"]
        )
        
        certificate_data = {
            "certificate_id": cert_id,
            "recipient_name": recipient_data["recipient_name"],
            "course_name": recipient_data["course_name"],
            "completion_date": recipient_data["completion_date"],
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "instructor_name": recipient_data.get("instructor_name", ""),
            "organization": recipient_data.get("organization", "Certificate Authority"),
            "grade": recipient_data.get("grade", ""),
        }
        
        # Generate certificate hash
        hash_string = f"{cert_id}{certificate_data['recipient_name']}{certificate_data['course_name']}{certificate_data['completion_date']}"
        certificate_data["certificate_hash"] = hashlib.sha256(hash_string.encode()).hexdigest()
        
        # Save to database
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO certificates 
            (certificate_id, recipient_name, course_name, completion_date, 
             issue_date, instructor_name, organization, grade, certificate_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            certificate_data["certificate_id"],
            certificate_data["recipient_name"],
            certificate_data["course_name"],
            certificate_data["completion_date"],
            certificate_data["issue_date"],
            certificate_data["instructor_name"],
            certificate_data["organization"],
            certificate_data["grade"],
            certificate_data["certificate_hash"]
        ))
        
        conn.commit()
        conn.close()
        
        # Create text-based certificate
        self.create_text_certificate(certificate_data)
        
        return cert_id
    
    def create_text_certificate(self, cert_data):
        """Create a text-based certificate file"""
        certificate_text = f"""
{'='*80}
                        CERTIFICATE OF COMPLETION
{'='*80}

                            This is to certify that

                        {cert_data['recipient_name'].upper()}

                    has successfully completed the course

                            {cert_data['course_name']}

Completion Date: {cert_data['completion_date']}
Issue Date: {cert_data['issue_date']}
Organization: {cert_data['organization']}
{f"Grade: {cert_data['grade']}" if cert_data['grade'] else ""}
{f"Instructor: {cert_data['instructor_name']}" if cert_data['instructor_name'] else ""}

Certificate ID: {cert_data['certificate_id']}
Security Hash: {cert_data['certificate_hash'][:16]}...

{'='*80}
        """
        
        # Save text certificate
        filename = f"certificate_{cert_data['certificate_id']}.txt"
        filepath = os.path.join("certificates", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(certificate_text)
        
        return filepath
    
    def verify_certificate(self, certificate_id):
        """Verify certificate by ID (only active certificates)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM certificates WHERE certificate_id = ? AND is_active = 1', (certificate_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [description[0] for description in cursor.description]
            conn.close()
            return dict(zip(columns, result))
        
        conn.close()
        return None
    
    def list_certificates(self):
        """List all active certificates (excluding deleted ones)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM certificates WHERE is_active = 1 ORDER BY created_at DESC')
        results = cursor.fetchall()
        
        if results:
            columns = [description[0] for description in cursor.description]
            certificates = [dict(zip(columns, row)) for row in results]
        else:
            certificates = []
        
        conn.close()
        return certificates

    def soft_delete_certificate(self, certificate_id):
        """Mark certificate as deleted (soft delete)"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE certificates SET is_active = 0 WHERE certificate_id = ?', (certificate_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0

    def restore_certificate(self, certificate_id):
        """Restore a soft-deleted certificate"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE certificates SET is_active = 1 WHERE certificate_id = ?', (certificate_id,))
        affected_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return affected_rows > 0

def demo_certificate_generation():
    """Demonstrate certificate generation"""
    print("🎓 Certificate Generation System Demo")
    print("=" * 50)
    
    # Initialize generator
    cert_gen = SimpleCertificateGenerator()
    
    # Sample certificate data
    sample_certificates = [
        {
            "recipient_name": "John Doe",
            "course_name": "Python Programming Fundamentals",
            "completion_date": "2025-10-01",
            "instructor_name": "Dr. Sarah Smith",
            "organization": "Tech Learning Academy",
            "grade": "A+"
        },
        {
            "recipient_name": "Jane Smith",
            "course_name": "Data Science Introduction",
            "completion_date": "2025-10-02",
            "instructor_name": "Prof. Michael Johnson",
            "organization": "Data Science Institute",
            "grade": "B+"
        },
        {
            "recipient_name": "Mike Wilson",
            "course_name": "Web Development Bootcamp",
            "completion_date": "2025-10-03",
            "organization": "Online Code Academy",
            "grade": "Pass"
        }
    ]
    
    # Generate certificates
    print("Generating sample certificates...")
    generated_ids = []
    
    for cert_data in sample_certificates:
        try:
            cert_id = cert_gen.create_certificate_record(cert_data)
            generated_ids.append(cert_id)
            print(f"✓ Generated certificate for {cert_data['recipient_name']} - ID: {cert_id}")
        except Exception as e:
            print(f"✗ Failed to generate certificate for {cert_data['recipient_name']}: {e}")
    
    # List all certificates
    print(f"\n📋 All Certificates:")
    certificates = cert_gen.list_certificates()
    
    if certificates:
        print("-" * 100)
        print(f"{'ID':<15} {'Recipient':<20} {'Course':<30} {'Date':<12} {'Grade':<8}")
        print("-" * 100)
        
        for cert in certificates:
            print(f"{cert['certificate_id']:<15} {cert['recipient_name']:<20} {cert['course_name']:<30} {cert['completion_date']:<12} {cert['grade'] or 'N/A':<8}")
    else:
        print("No certificates found.")
    
    # Test verification
    if generated_ids:
        print(f"\n🔍 Testing Certificate Verification:")
        test_id = generated_ids[0]
        verified_cert = cert_gen.verify_certificate(test_id)
        
        if verified_cert:
            print(f"✓ Certificate {test_id} is VALID")
            print(f"  Recipient: {verified_cert['recipient_name']}")
            print(f"  Course: {verified_cert['course_name']}")
        else:
            print(f"✗ Certificate {test_id} is INVALID")
    
    print(f"\n📁 Files created:")
    print(f"  - Database: {cert_gen.database_path}")
    print(f"  - Text certificates: certificates/ directory")
    
    return cert_gen

if __name__ == "__main__":
    demo_certificate_generation()