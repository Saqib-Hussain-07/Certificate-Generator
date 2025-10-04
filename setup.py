"""
Setup and Test Script for Certificate Generation System
Run this script to install dependencies and test the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required!")
        return False
    
    print("✅ Python version is adequate")
    return True

def install_dependencies():
    """Install required Python packages"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def test_imports():
    """Test if all required modules can be imported"""
    print(f"\n{'='*50}")
    print("📦 Testing imports")
    print(f"{'='*50}")
    
    modules = [
        'flask',
        'PIL',
        'qrcode',
        'reportlab',
        'sqlite3'
    ]
    
    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            success = False
    
    return success

def create_directories():
    """Create necessary directories"""
    print(f"\n{'='*50}")
    print("📁 Creating directories")
    print(f"{'='*50}")
    
    directories = ['certificates', 'qr_codes', 'templates']
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        print(f"✅ Directory '{directory}' ready")
    
    return True

def test_certificate_generation():
    """Test basic certificate generation"""
    print(f"\n{'='*50}")
    print("🎓 Testing certificate generation")
    print(f"{'='*50}")
    
    try:
        from certificate_generator import CertificateGenerator
        
        cert_gen = CertificateGenerator()
        
        # Test data
        test_data = {
            "recipient_name": "Test User",
            "course_name": "System Test Course",
            "completion_date": "2025-10-03",
            "instructor_name": "Test Instructor",
            "organization": "Test Academy",
            "grade": "A+"
        }
        
        print("Generating test certificate...")
        pdf_path = cert_gen.create_certificate_pdf(test_data)
        
        if os.path.exists(pdf_path):
            print(f"✅ Test certificate generated: {pdf_path}")
            
            # Check if QR code was generated
            certificates = cert_gen.list_certificates()
            if certificates:
                cert_id = certificates[0]['certificate_id']
                qr_path = f"qr_codes/qr_{cert_id}.png"
                if os.path.exists(qr_path):
                    print(f"✅ QR code generated: {qr_path}")
                else:
                    print(f"⚠️  QR code not found: {qr_path}")
            
            return True
        else:
            print(f"❌ Test certificate not generated")
            return False
    
    except Exception as e:
        print(f"❌ Certificate generation test failed: {e}")
        return False

def test_qr_generation():
    """Test QR code generation"""
    print(f"\n{'='*50}")
    print("📱 Testing QR code generation")
    print(f"{'='*50}")
    
    try:
        # Import the QR generator from Generate QR Code.py
        sys.path.append('.')
        from importlib import import_module
        
        # Import the QR code module
        qr_module = import_module('Generate QR Code')
        qr_gen = qr_module.QRCodeGenerator()
        
        test_data = {
            "certificate_id": "TEST_12345",
            "recipient_name": "QR Test User",
            "course_name": "QR Test Course",
            "completion_date": "2025-10-03"
        }
        
        qr_path = qr_gen.generate_certificate_qr(test_data)
        
        if os.path.exists(qr_path):
            print(f"✅ QR code test successful: {qr_path}")
            return True
        else:
            print(f"❌ QR code test failed")
            return False
    
    except Exception as e:
        print(f"❌ QR code test failed: {e}")
        return False

def test_web_app():
    """Test if web app can start"""
    print(f"\n{'='*50}")
    print("🌐 Testing web application")
    print(f"{'='*50}")
    
    try:
        from web_verification import app
        
        # Test if Flask app can be created
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Web application test successful")
                return True
            else:
                print(f"❌ Web application returned status {response.status_code}")
                return False
    
    except Exception as e:
        print(f"❌ Web application test failed: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print(f"\n{'='*50}")
    print("📊 SETUP SUMMARY")
    print(f"{'='*50}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your Certificate Generation System is ready to use.")
        print("\nNext steps:")
        print("1. Run 'python web_verification.py' to start the web interface")
        print("2. Visit http://localhost:5000 in your browser")
        print("3. Try generating your first certificate!")
        print("4. Use 'python cli.py --help' for command line options")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the errors above.")
        print("Consider reinstalling dependencies or checking file permissions.")

def main():
    """Main setup function"""
    print("🎓 Certificate Generation System Setup")
    print("=" * 50)
    
    results = {}
    
    # Run all tests
    results["Python Version Check"] = check_python_version()
    results["Install Dependencies"] = install_dependencies()
    results["Test Imports"] = test_imports()
    results["Create Directories"] = create_directories()
    results["Certificate Generation"] = test_certificate_generation()
    results["QR Code Generation"] = test_qr_generation()
    results["Web Application"] = test_web_app()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    main()