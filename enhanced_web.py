"""
Enhanced Web Interface for Certificate Generation System
Supports both simple text certificates and full PDF+QR certificates
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
from mailer import send_email, send_whatsapp_via_twilio
import os
from datetime import datetime
import traceback

# Try to import full-featured generator, fall back to simple
try:
    from certificate_generator import CertificateGenerator
    FULL_FEATURES = True
    print("✅ Full-featured PDF+QR system available")
except ImportError as e:
    from simple_demo import SimpleCertificateGenerator as CertificateGenerator
    FULL_FEATURES = False
    print(f"⚠️  Using basic text system (PDF features unavailable: {e})")

app = Flask(__name__)
app.secret_key = 'certificate_verification_key_2025'

# Initialize certificate generator
cert_gen = CertificateGenerator()

@app.route('/')
def index():
    """Main page with system status"""
    certificates = cert_gen.list_certificates()
    return render_template('index.html', full_features=FULL_FEATURES, certificates=certificates)

@app.route('/system_status')
def system_status():
    """API endpoint for system status"""
    certificates = cert_gen.list_certificates()
    
    status = {
        'full_features': FULL_FEATURES,
        'total_certificates': len(certificates),
        'features': {
            'pdf_generation': FULL_FEATURES,
            'qr_codes': FULL_FEATURES,
            'text_certificates': True,
            'web_interface': True,
            'verification': True,
            'bulk_generation': True
        }
    }
    
    return jsonify(status)

@app.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    """Verify certificate by ID"""
    certificate = cert_gen.verify_certificate(certificate_id)
    
    if certificate:
        return render_template('verification_result.html', 
                             certificate=certificate, 
                             status='valid',
                             full_features=FULL_FEATURES)
    else:
        return render_template('verification_result.html', 
                             certificate=None, 
                             status='invalid',
                             full_features=FULL_FEATURES)

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
                'grade': request.form.get('grade', ''),
                'email': request.form.get('email', ''),
                'phone': request.form.get('phone', '')
            }
            
            # Generate certificate
            if FULL_FEATURES:
                pdf_path = cert_gen.create_certificate_pdf(recipient_data)
                # Get the latest certificate
                certificates = cert_gen.list_certificates()
                certificate = certificates[0] if certificates else None
            else:
                cert_id = cert_gen.create_certificate_record(recipient_data)
                certificate = cert_gen.verify_certificate(cert_id)
                pdf_path = None
            
            return render_template('generation_result.html', 
                                 success=True, 
                                 certificate=certificate,
                                 pdf_path=pdf_path,
                                 full_features=FULL_FEATURES)
        
        except Exception as e:
            print(f"Error generating certificate: {e}")
            traceback.print_exc()
            return render_template('generation_result.html', 
                                 success=False, 
                                 error=str(e),
                                 full_features=FULL_FEATURES)
    
    return render_template('generate.html', full_features=FULL_FEATURES)

@app.route('/certificates')
def list_certificates():
    """List all certificates"""
    certificates = cert_gen.list_certificates()
    return render_template('certificates_list.html', 
                         certificates=certificates,
                         full_features=FULL_FEATURES)

@app.route('/bulk_generate', methods=['GET', 'POST'])
def bulk_generate():
    """Bulk certificate generation"""
    if request.method == 'POST':
        try:
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
                            # CSV columns: name, course, completion_date, instructor?, organization?, grade?, email?, phone?
                            recipient = {
                                'recipient_name': parts[0],
                                'course_name': parts[1],
                                'completion_date': parts[2],
                                'instructor_name': parts[3] if len(parts) > 3 else '',
                                'organization': parts[4] if len(parts) > 4 else 'Certificate Authority',
                                'grade': parts[5] if len(parts) > 5 else '',
                                'email': parts[6] if len(parts) > 6 else '',
                                'phone': parts[7] if len(parts) > 7 else ''
                            }
                            recipients.append(recipient)
                
                # Generate certificates
                if FULL_FEATURES:
                    generated_items = cert_gen.generate_bulk_certificates(recipients)
                    return render_template('bulk_result.html', 
                                         success=True, 
                                         count=len(generated_items),
                                         files=generated_items,
                                         full_features=FULL_FEATURES)
                else:
                    generated_ids = []
                    for recipient_data in recipients:
                        try:
                            cert_id = cert_gen.create_certificate_record(recipient_data)
                            generated_ids.append(cert_id)
                        except Exception as e:
                            print(f"Error generating certificate: {e}")
                    
                    return render_template('bulk_result.html', 
                                         success=True, 
                                         count=len(generated_ids),
                                         certificate_ids=generated_ids,
                                         full_features=FULL_FEATURES)
            else:
                return render_template('bulk_result.html', 
                                     success=False, 
                                     error="No data provided",
                                     full_features=FULL_FEATURES)
        
        except Exception as e:
            return render_template('bulk_result.html', 
                                 success=False, 
                                 error=str(e),
                                 full_features=FULL_FEATURES)
    
    return render_template('bulk_generate.html', full_features=FULL_FEATURES)


@app.route('/bulk_send', methods=['POST'])
def bulk_send():
    """Send generated certificates via email or WhatsApp. Expects JSON payload with items and send options."""
    data = request.get_json() or {}
    items = data.get('items', [])  # list of {file, certificate_id, recipient_name, email, phone}
    method = data.get('method', 'email')
    message = data.get('message', 'Please find your certificate attached.')

    results = []

    # Email config from environment (recommended) or request (fallback)
    smtp_server = os.environ.get('SMTP_SERVER', data.get('smtp_server'))
    smtp_port = int(os.environ.get('SMTP_PORT', data.get('smtp_port', 587)))
    smtp_user = os.environ.get('SMTP_USER', data.get('smtp_user'))
    smtp_pass = os.environ.get('SMTP_PASS', data.get('smtp_pass'))

    twilio_sid = os.environ.get('TWILIO_SID', data.get('twilio_sid'))
    twilio_token = os.environ.get('TWILIO_TOKEN', data.get('twilio_token'))
    twilio_from = os.environ.get('TWILIO_FROM', data.get('twilio_from'))

    for item in items:
        recipient = item.get('recipient_name')
        file_path = item.get('file')
        email = item.get('email')
        phone = item.get('phone')

        if method == 'email' and email:
            to_list = [email]
            # Send email with attachment
            try:
                res = send_email(smtp_server, smtp_port, smtp_user, smtp_pass,
                                 subject=f"Your Certificate - {item.get('certificate_id')}",
                                 body=message,
                                 to_addresses=to_list,
                                 attachments=[file_path])
            except Exception as e:
                res = {'status': 'error', 'message': str(e)}

            results.append({'certificate_id': item.get('certificate_id'), 'method': 'email', 'recipient': recipient, 'result': res})

        elif method == 'whatsapp' and phone:
            # Send via Twilio WhatsApp (requires Twilio account)
            try:
                media_url = None
                # If file is accessible via HTTP you'd supply the media_url; for local files, Twilio requires a public URL.
                res = send_whatsapp_via_twilio(twilio_sid, twilio_token, twilio_from, phone, message, media_url)
            except Exception as e:
                res = {'status': 'error', 'message': str(e)}

            results.append({'certificate_id': item.get('certificate_id'), 'method': 'whatsapp', 'recipient': recipient, 'result': res})

        else:
            results.append({'certificate_id': item.get('certificate_id'), 'method': method, 'recipient': recipient, 'result': {'status': 'skipped', 'message': 'No contact info'}})

    return jsonify({'status': 'done', 'results': results})

@app.route('/download/<certificate_id>')
def download_certificate(certificate_id):
    """Download certificate file"""
    try:
        if FULL_FEATURES:
            # Try PDF first
            pdf_filename = f"certificate_{certificate_id}.pdf"
            pdf_path = os.path.join("certificates", pdf_filename)
            
            if os.path.exists(pdf_path):
                return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
        
        # Fall back to text file
        txt_filename = f"certificate_{certificate_id}.txt"
        txt_path = os.path.join("certificates", txt_filename)
        
        if os.path.exists(txt_path):
            return send_file(txt_path, as_attachment=True, download_name=txt_filename)
        else:
            return "Certificate file not found", 404
            
    except Exception as e:
        return f"Error accessing certificate: {str(e)}", 500

@app.route('/qr/<certificate_id>')
def download_qr_code(certificate_id):
    """Download QR code image"""
    if not FULL_FEATURES:
        return "QR codes not available in basic mode", 404
    
    try:
        qr_filename = f"qr_{certificate_id}.png"
        qr_path = os.path.join("qr_codes", qr_filename)
        
        if os.path.exists(qr_path):
            return send_file(qr_path, as_attachment=True, download_name=qr_filename)
        else:
            return "QR code not found", 404
            
    except Exception as e:
        return f"Error accessing QR code: {str(e)}", 500

@app.route('/api/delete_certificate', methods=['POST'])
def delete_certificate():
    """Soft delete a certificate"""
    data = request.get_json()
    certificate_id = data.get('certificate_id', '').strip()
    
    if not certificate_id:
        return jsonify({'error': 'Certificate ID is required'}), 400
    
    success = cert_gen.soft_delete_certificate(certificate_id)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Certificate deleted successfully'})
    else:
        return jsonify({'error': 'Certificate not found or already deleted'}), 404

@app.route('/api/restore_certificate', methods=['POST'])
def restore_certificate():
    """Restore a soft-deleted certificate"""
    data = request.get_json()
    certificate_id = data.get('certificate_id', '').strip()
    
    if not certificate_id:
        return jsonify({'error': 'Certificate ID is required'}), 400
    
    success = cert_gen.restore_certificate(certificate_id)
    
    if success:
        return jsonify({'status': 'success', 'message': 'Certificate restored successfully'})
    else:
        return jsonify({'error': 'Certificate not found'}), 404

if __name__ == '__main__':
    # Create directories
    os.makedirs('certificates', exist_ok=True)
    os.makedirs('qr_codes', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n🎓 Enhanced Certificate Generation System")
    print("=" * 60)
    print(f"🔧 System Mode: {'Full PDF+QR Features' if FULL_FEATURES else 'Basic Text Mode'}")
    print(f"🌐 Web Interface: http://localhost:5000")
    print(f"📊 Total Certificates: {len(cert_gen.list_certificates())}")
    
    if FULL_FEATURES:
        print("✅ Available Features:")
        print("   - Professional PDF certificates")
        print("   - QR code generation and verification")
        print("   - Text certificate fallback")
        print("   - Bulk generation")
        print("   - Web interface")
        print("   - Certificate verification")
    else:
        print("📝 Available Features:")
        print("   - Text-based certificates")
        print("   - Bulk generation")
        print("   - Web interface")
        print("   - Certificate verification")
        print("   - Install pillow, qrcode, reportlab for PDF features")
    
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)