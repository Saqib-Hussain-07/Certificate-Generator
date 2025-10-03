"""
Web Interface Status and Diagnostic Tool
Tests all components of the certificate generation web interface
"""

import os
import sys
import sqlite3
import requests
from datetime import datetime

def check_system_status():
    """Check overall system status"""
    print("🔍 Certificate Generation System Diagnostic")
    print("=" * 60)
    
    # Check files
    files_to_check = [
        'enhanced_web.py',
        'certificate_generator.py',
        'certificates.db',
        'templates/base.html',
        'templates/index.html',
        'templates/certificates_list.html',
        'templates/generate.html',
        'templates/verification_result.html'
    ]
    
    print("📁 File System Check:")
    for file_path in files_to_check:
        exists = os.path.exists(file_path)
        print(f"   {'✅' if exists else '❌'} {file_path}")
    
    # Check directories
    directories = ['certificates', 'qr_codes', 'templates']
    print("\n📂 Directory Check:")
    for directory in directories:
        exists = os.path.exists(directory)
        count = len(os.listdir(directory)) if exists else 0
        print(f"   {'✅' if exists else '❌'} {directory}/ ({count} files)")
    
    # Check database
    print("\n🗄️ Database Check:")
    try:
        conn = sqlite3.connect('certificates.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM certificates")
        cert_count = cursor.fetchone()[0]
        print(f"   ✅ Database accessible with {cert_count} certificates")
        
        # Get sample certificate
        cursor.execute("SELECT certificate_id, recipient_name, course_name FROM certificates LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"   📋 Sample: {sample[0]} - {sample[1]} - {sample[2]}")
        
        conn.close()
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # Check Python packages
    print("\n📦 Package Check:")
    packages = ['flask', 'PIL', 'qrcode', 'reportlab']
    for package in packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
    
    print("\n" + "=" * 60)

def test_web_endpoints():
    """Test web interface endpoints"""
    print("🌐 Web Interface Test")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    endpoints_to_test = [
        ('/', 'Home Page'),
        ('/system_status', 'System Status API'),
        ('/certificates', 'Certificates List'),
        ('/generate', 'Generate Form'),
        ('/bulk_generate', 'Bulk Generate Form')
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = f"✅ {response.status_code}" if response.status_code == 200 else f"⚠️ {response.status_code}"
            print(f"   {status} {endpoint} - {description}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {endpoint} - {description} (Error: {str(e)[:50]})")
    
    print("\n" + "=" * 60)

def show_usage_instructions():
    """Show how to use the system"""
    print("📖 Usage Instructions")
    print("=" * 60)
    print("1. 🌐 Web Interface:")
    print("   - Main interface: http://localhost:5000")
    print("   - Generate certificates, verify, and manage")
    print()
    print("2. 💻 Command Line:")
    print("   - Generate: python cli.py generate --name 'Name' --course 'Course'")
    print("   - Verify: python cli.py verify CERT_ID")
    print("   - List: python cli.py list")
    print()
    print("3. 📱 Features:")
    print("   - PDF certificates with professional design")
    print("   - QR codes for instant verification")
    print("   - Bulk generation from CSV data")
    print("   - Secure database storage")
    print()
    print("4. 🔧 Troubleshooting:")
    print("   - Restart web server: python enhanced_web.py")
    print("   - Check this diagnostic: python web_diagnostic.py")
    print("   - View server logs in terminal")
    print("\n" + "=" * 60)

def main():
    print(f"🎓 Certificate Generation System Diagnostic")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_system_status()
    print()
    test_web_endpoints()
    print()
    show_usage_instructions()
    
    print("🎉 Diagnostic Complete!")
    print("If web interface is not working:")
    print("1. Check if enhanced_web.py is running")
    print("2. Verify http://localhost:5000 in browser")
    print("3. Check terminal output for errors")

if __name__ == "__main__":
    main()