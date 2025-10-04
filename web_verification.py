"""
Certificate Verification System
Web-based verification using Flask
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
import os
from datetime import datetime
from certificate_generator import CertificateGenerator

app = Flask(__name__)
app.secret_key = 'certificate_verification_key_2025'

# Initialize certificate generator
cert_gen = CertificateGenerator()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    """Verify certificate by ID"""
    certificate = cert_gen.verify_certificate(certificate_id)
    
    if certificate:
        return render_template('verification_result.html', 
                             certificate=certificate, 
                             status='valid')
    else:
        return render_template('verification_result.html', 
                             certificate=None, 
                             status='invalid')

@app.route('/api/verify', methods=['POST'])
def api_verify():
    """API endpoint for certificate verification"""
    data = request.get_json()
    certificate_id = data.get('certificate_id', '').strip()
    
    if not certificate_id:
        return jsonify({'error': 'Certificate ID is required'}), 400
    
    certificate = cert_gen.verify_certificate(certificate_id)
    
    if certificate:
        return jsonify({
            'status': 'valid',
            'certificate': {
                'id': certificate['certificate_id'],
                'recipient': certificate['recipient_name'],
                'course': certificate['course_name'],
                'completion_date': certificate['completion_date'],
                'issue_date': certificate['issue_date'],
                'organization': certificate['organization'],
                'grade': certificate['grade'] if certificate['grade'] else None
            }
        })
    else:
        return jsonify({'status': 'invalid', 'message': 'Certificate not found'})

@app.route('/generate', methods=['GET', 'POST'])
def generate_certificate():
    """Generate new certificate"""
    if request.method == 'POST':
        try:
            # Get form data
            recipient_data = {
                'recipient_name': request.form['recipient_name'],
                'course_name': request.form['course_name'],
                'completion_date': request.form['completion_date'],
                'instructor_name': request.form.get('instructor_name', ''),
                'organization': request.form.get('organization', 'Certificate Authority'),
                'grade': request.form.get('grade', '')
            }
            
            # Generate certificate
            pdf_path = cert_gen.create_certificate_pdf(recipient_data)
            
            # Get certificate ID from the database
            certificates = cert_gen.list_certificates()
            latest_cert = certificates[0] if certificates else None
            
            return render_template('generation_result.html', 
                                 success=True, 
                                 certificate=latest_cert,
                                 pdf_path=pdf_path)
        
        except Exception as e:
            return render_template('generation_result.html', 
                                 success=False, 
                                 error=str(e))
    
    return render_template('generate.html')

@app.route('/certificates')
def list_certificates():
    """List all certificates"""
    certificates = cert_gen.list_certificates()
    return render_template('certificates_list.html', certificates=certificates)

@app.route('/bulk_generate', methods=['GET', 'POST'])
def bulk_generate():
    """Bulk certificate generation"""
    if request.method == 'POST':
        try:
            # Get uploaded file or form data
            csv_data = request.form.get('csv_data', '')
            
            if csv_data:
                recipients = []
                lines = csv_data.strip().split('\n')
                
                # Skip header if present
                if lines and 'recipient_name' in lines[0].lower():
                    lines = lines[1:]
                
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 3:
                            recipient = {
                                'recipient_name': parts[0],
                                'course_name': parts[1],
                                'completion_date': parts[2],
                                'instructor_name': parts[3] if len(parts) > 3 else '',
                                'organization': parts[4] if len(parts) > 4 else 'Certificate Authority',
                                'grade': parts[5] if len(parts) > 5 else ''
                            }
                            recipients.append(recipient)
                
                # Generate certificates
                generated_files = cert_gen.generate_bulk_certificates(recipients)
                
                return render_template('bulk_result.html', 
                                     success=True, 
                                     count=len(generated_files),
                                     files=generated_files)
            else:
                return render_template('bulk_result.html', 
                                     success=False, 
                                     error="No data provided")
        
        except Exception as e:
            return render_template('bulk_result.html', 
                                 success=False, 
                                 error=str(e))
    
    return render_template('bulk_generate.html')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("Certificate Generation System Starting...")
    print("Access the system at: http://localhost:5000")
    print("Available endpoints:")
    print("  - / : Main page")
    print("  - /generate : Generate single certificate")
    print("  - /bulk_generate : Generate multiple certificates")
    print("  - /certificates : List all certificates")
    print("  - /verify/<certificate_id> : Verify certificate")
    print("  - /api/verify : API verification endpoint")
    
    app.run(debug=True, host='0.0.0.0', port=5000)