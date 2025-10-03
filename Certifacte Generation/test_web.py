"""
Simple Web Interface Test
Minimal Flask app to test if templates are working
"""

from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = 'test_key'

# Test data
test_certificates = [
    {
        'certificate_id': 'CERT_TEST123',
        'recipient_name': 'Test User',
        'course_name': 'Test Course',
        'completion_date': '2025-10-03',
        'issue_date': '2025-10-03',
        'organization': 'Test Org',
        'grade': 'A+',
        'instructor_name': 'Test Instructor',
        'certificate_hash': 'testhash123'
    }
]

@app.route('/')
def index():
    """Test home page"""
    return "<h1>Certificate System Test</h1><p>Web server is working!</p><a href='/test-certificates'>Test Certificates List</a>"

@app.route('/test-certificates')
def test_certificates_list():
    """Test certificates list page"""
    try:
        return render_template('certificates_list.html', 
                             certificates=test_certificates,
                             full_features=True)
    except Exception as e:
        return f"Template Error: {str(e)}"

@app.route('/status')
def status():
    """Simple status check"""
    return {
        'status': 'running',
        'templates_dir': os.path.exists('templates'),
        'certificates_list_template': os.path.exists('templates/certificates_list.html'),
        'base_template': os.path.exists('templates/base.html')
    }

if __name__ == '__main__':
    print("🧪 Testing Web Interface...")
    print("🌐 URL: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)