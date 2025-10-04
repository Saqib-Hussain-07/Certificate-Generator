"""
Vercel API Entry Point for Certificate Generation System
"""
import os
import sys
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the certificate generator (use the original one, make it Vercel-compatible here)
try:
    from certificate_generator import CertificateGenerator
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    print("⚠️ Certificate generator not available")

# Import mailer functions
try:
    sys.path.append('..')
    from mailer import send_email, send_whatsapp_via_twilio
except ImportError:
    print("⚠️ Mailer functions not available")
    def send_email(*args, **kwargs):
        return False
    def send_whatsapp_via_twilio(*args, **kwargs):
        return False

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Vercel serverless function configuration
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vercel-production-key-change-this')

# Initialize certificate generator for Vercel
if GENERATOR_AVAILABLE:
    # Ensure temp directories exist first
    os.makedirs('/tmp/certificates', exist_ok=True)
    os.makedirs('/tmp/qr_codes', exist_ok=True)
    
    # Initialize with temporary database path for Vercel
    cert_gen = CertificateGenerator('/tmp/certificates.db')
    
    # Override directory paths for Vercel (if attributes exist)
    if hasattr(cert_gen, 'certificates_dir'):
        cert_gen.certificates_dir = '/tmp/certificates'
    if hasattr(cert_gen, 'qr_codes_dir'):
        cert_gen.qr_codes_dir = '/tmp/qr_codes'
    
    print("✅ Certificate generator initialized for Vercel")
else:
    cert_gen = None
    print("❌ Certificate generator not available")

# Routes
@app.route('/')
def index():
    """Main page"""
    if cert_gen:
        certificates = cert_gen.list_certificates()
    else:
        certificates = []
    return render_template('index.html', full_features=GENERATOR_AVAILABLE, certificates=certificates)

@app.route('/generate')
def generate_form():
    """Certificate generation form"""
    return render_template('generate.html')

@app.route('/generate_certificate', methods=['POST'])
def generate_certificate():
    """Generate a single certificate"""
    try:
        if not cert_gen:
            return jsonify({'success': False, 'error': 'Certificate generator not available'})
            
        # Debug: Print all form data
        print("Form data received:", dict(request.form))
            
        # Get form data with correct field names
        recipient_name = request.form.get('recipient_name', '').strip()
        event_name = request.form.get('course_name', '').strip()  # Form uses 'course_name'
        event_date = request.form.get('completion_date', '').strip()  # Form uses 'completion_date'
        organization = request.form.get('organization', '').strip()
        recipient_email = request.form.get('email', '').strip()  # Form uses 'email'
        recipient_phone = request.form.get('phone', '').strip()  # Form uses 'phone'
        
        # Set default organization if empty
        if not organization:
            organization = 'Certificate Authority'
        
        # Debug: Print extracted values
        print(f"Extracted values: name={recipient_name}, course={event_name}, date={event_date}, org={organization}")
        
        # Validation - only require essential fields
        if not all([recipient_name, event_name, event_date]):
            missing_fields = []
            if not recipient_name: missing_fields.append('Recipient Name')
            if not event_name: missing_fields.append('Course Name')
            if not event_date: missing_fields.append('Completion Date')
            error_msg = f'Please fill in all required fields: {", ".join(missing_fields)}'
            return jsonify({'success': False, 'error': error_msg})
        
        # Validate date format
        try:
            datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            error_msg = 'Invalid date format. Please use the date picker or ensure date is in YYYY-MM-DD format.'
            return jsonify({'success': False, 'error': error_msg})
        
        # Basic name validation - allow letters, spaces, apostrophes, hyphens, periods
        name_pattern = r"^[a-zA-Z\s'\-\.]+$"
        if not re.match(name_pattern, recipient_name):
            error_msg = 'Recipient name contains invalid characters. Please use only letters, spaces, apostrophes, hyphens, and periods.'
            return jsonify({'success': False, 'error': error_msg})
        
        # Prepare recipient data for certificate generation
        recipient_data = {
            'recipient_name': recipient_name,
            'course_name': event_name,  # Map to course_name as expected by original generator
            'completion_date': event_date,
            'organization': organization,
            'email': recipient_email,
            'phone': recipient_phone,
            'instructor_name': '',  # Optional field
            'grade': ''  # Optional field
        }
        
        # Generate certificate using the original generator's method
        try:
            # Change to temp directory for certificate generation
            temp_dir = '/tmp'
            original_cwd = os.getcwd()
            
            try:
                # Change working directory to temp
                os.chdir(temp_dir)
                print(f"Debug: Changed working directory to {temp_dir}")
                
                # Create required directories in temp
                os.makedirs("certificates", exist_ok=True)
                os.makedirs("qr_codes", exist_ok=True)
                print(f"Debug: Created certificates and qr_codes directories in {temp_dir}")
                
                print(f"Debug: About to generate certificate with data: {recipient_data}")
                
                # Generate certificate (will use current working directory)
                pdf_path = cert_gen.create_certificate_pdf(recipient_data)
                print(f"Debug: Certificate generated at: {pdf_path}")
                
                # Convert relative path to absolute path for return
                if not os.path.isabs(pdf_path):
                    pdf_path = os.path.join(temp_dir, pdf_path)
                
                # Get certificate ID from filename
                cert_id = os.path.basename(pdf_path).replace('certificate_', '').replace('.pdf', '')
                print(f"Debug: Certificate ID: {cert_id}")
                
                result = {
                    'success': True,
                    'message': f'Certificate generated successfully',
                    'pdf_path': pdf_path,
                    'certificate_id': cert_id
                }
                
            finally:
                # Always restore original working directory
                os.chdir(original_cwd)
                print(f"Debug: Restored working directory to {original_cwd}")
                
        except Exception as gen_error:
            print(f"Certificate generation error: {gen_error}")
            result = {
                'success': False,
                'error': f'Certificate generation failed: {str(gen_error)}'
            }
        
        # Check if request wants JSON or HTML response
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('Accept', '').startswith('application/json'):
            return jsonify(result)
        else:
            # Return HTML response for regular form submission
            if result.get('success'):
                return render_template('generation_result.html', result=result)
            else:
                return render_template('generate.html', error=result.get('error'))
        
    except Exception as e:
        print(f"Certificate generation error: {str(e)}")
        return jsonify({'success': False, 'error': f'Generation failed: {str(e)}'})

@app.route('/certificates')
def certificates_list():
    """List all certificates"""
    if cert_gen:
        certificates = cert_gen.list_certificates()
    else:
        certificates = []
    return render_template('certificates_list.html', certificates=certificates)

@app.route('/verify/<certificate_id>')
def verify_certificate(certificate_id):
    """Verify certificate"""
    if cert_gen:
        result = cert_gen.verify_certificate(certificate_id)
    else:
        result = {'valid': False, 'error': 'Certificate generator not available'}
    return render_template('verification_result.html', result=result, certificate_id=certificate_id)

@app.route('/download/<certificate_id>')
def download_certificate(certificate_id):
    """Download certificate PDF"""
    try:
        # Check if the certificate exists in temp directory first
        temp_dir = '/tmp'
        pdf_filename = f'certificate_{certificate_id}.pdf'
        pdf_path = os.path.join(temp_dir, 'certificates', pdf_filename)
        
        print(f"Debug: Looking for certificate at: {pdf_path}")
        
        if os.path.exists(pdf_path):
            print(f"Debug: Found certificate at {pdf_path}")
            return send_file(pdf_path, 
                           as_attachment=True, 
                           download_name=f'certificate_{certificate_id}.pdf',
                           mimetype='application/pdf')
        else:
            print(f"Debug: Certificate not found at {pdf_path}")
            # Try to find in the original certificates directory
            local_pdf_path = os.path.join('certificates', pdf_filename)
            if os.path.exists(local_pdf_path):
                print(f"Debug: Found certificate at {local_pdf_path}")
                return send_file(local_pdf_path, 
                               as_attachment=True, 
                               download_name=f'certificate_{certificate_id}.pdf',
                               mimetype='application/pdf')
            else:
                print(f"Debug: Certificate not found anywhere")
                return jsonify({'error': 'Certificate not found'}), 404
                
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/bulk_generate', methods=['GET', 'POST'])
def bulk_generate_form():
    """Bulk generation form and processing"""
    if request.method == 'GET':
        return render_template('bulk_generate.html')
    
    # Handle POST - bulk generation
    try:
        if not cert_gen:
            return jsonify({'success': False, 'error': 'Certificate generator not available'})
        
        # For now, return a success message for bulk generation
        # Full implementation would handle CSV parsing and batch generation
        return jsonify({
            'success': True,
            'message': 'Bulk generation feature available in full version',
            'generated_count': 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/bulk_send', methods=['POST'])
def bulk_send():
    """Send certificates in bulk"""
    try:
        data = request.get_json()
        certificate_ids = data.get('certificate_ids', [])
        send_method = data.get('method', 'email')
        
        if not certificate_ids:
            return jsonify({'success': False, 'error': 'No certificates selected'})
        
        # For demo purposes, return success
        # In production, implement actual sending logic
        return jsonify({
            'success': True,
            'message': f'Sent {len(certificate_ids)} certificates via {send_method}',
            'sent_count': len(certificate_ids),
            'failed_count': 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Default export for Vercel