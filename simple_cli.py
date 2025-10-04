"""
Simple CLI for Certificate Generation System
Works with the basic system without external dependencies
"""

import argparse
import sys
import os
from datetime import datetime
from simple_demo import SimpleCertificateGenerator

def main():
    parser = argparse.ArgumentParser(description='Certificate Generation System CLI')
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate single certificate
    gen_parser = subparsers.add_parser('generate', help='Generate a single certificate')
    gen_parser.add_argument('--name', required=True, help='Recipient name')
    gen_parser.add_argument('--course', required=True, help='Course name')
    gen_parser.add_argument('--date', help='Completion date (YYYY-MM-DD), defaults to today')
    gen_parser.add_argument('--instructor', help='Instructor name')
    gen_parser.add_argument('--organization', default='Certificate Authority', help='Organization name')
    gen_parser.add_argument('--grade', help='Grade or score')
    
    # Verify certificate
    verify_parser = subparsers.add_parser('verify', help='Verify a certificate')
    verify_parser.add_argument('certificate_id', help='Certificate ID to verify')
    
    # List certificates
    list_parser = subparsers.add_parser('list', help='List all certificates')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of certificates to show')
    
    # Bulk generate
    bulk_parser = subparsers.add_parser('bulk', help='Generate certificates from CSV file')
    bulk_parser.add_argument('csv_file', help='Path to CSV file with certificate data')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize certificate generator
    cert_gen = SimpleCertificateGenerator()
    
    try:
        if args.command == 'generate':
            generate_certificate(cert_gen, args)
        elif args.command == 'verify':
            verify_certificate(cert_gen, args.certificate_id)
        elif args.command == 'list':
            list_certificates(cert_gen, args.limit)
        elif args.command == 'bulk':
            bulk_generate(cert_gen, args.csv_file)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def generate_certificate(cert_gen, args):
    """Generate a single certificate"""
    print("🎓 Generating certificate...")
    
    # Prepare certificate data
    cert_data = {
        'recipient_name': args.name,
        'course_name': args.course,
        'completion_date': args.date or datetime.now().strftime('%Y-%m-%d'),
        'instructor_name': args.instructor or '',
        'organization': args.organization,
        'grade': args.grade or ''
    }
    
    # Generate certificate
    cert_id = cert_gen.create_certificate_record(cert_data)
    
    print(f"✅ Certificate generated successfully!")
    print(f"   Certificate ID: {cert_id}")
    print(f"   Text file: certificates/certificate_{cert_id}.txt")
    print(f"   Verification: http://localhost:5000/verify/{cert_id}")

def verify_certificate(cert_gen, certificate_id):
    """Verify a certificate"""
    print(f"🔍 Verifying certificate: {certificate_id}")
    
    certificate = cert_gen.verify_certificate(certificate_id)
    
    if certificate:
        print("✅ Certificate is VALID")
        print("\n📋 Certificate Details:")
        print(f"   Recipient: {certificate['recipient_name']}")
        print(f"   Course: {certificate['course_name']}")
        print(f"   Completion Date: {certificate['completion_date']}")
        print(f"   Issue Date: {certificate['issue_date']}")
        print(f"   Organization: {certificate['organization']}")
        if certificate['grade']:
            print(f"   Grade: {certificate['grade']}")
        if certificate['instructor_name']:
            print(f"   Instructor: {certificate['instructor_name']}")
        print(f"   Security Hash: {certificate['certificate_hash'][:16]}...")
    else:
        print("❌ Certificate is INVALID or NOT FOUND")

def list_certificates(cert_gen, limit):
    """List certificates"""
    certificates = cert_gen.list_certificates()
    
    if not certificates:
        print("📭 No certificates found.")
        print("💡 Generate your first certificate with: python simple_cli.py generate --name 'Your Name' --course 'Your Course'")
        return
    
    print(f"📋 Showing {min(limit, len(certificates))} of {len(certificates)} certificates:")
    print("-" * 100)
    print(f"{'ID':<15} {'Recipient':<20} {'Course':<35} {'Date':<12} {'Grade':<8}")
    print("-" * 100)
    
    for i, cert in enumerate(certificates[:limit]):
        print(f"{cert['certificate_id']:<15} {cert['recipient_name']:<20} {cert['course_name']:<35} {cert['completion_date']:<12} {cert['grade'] or 'N/A':<8}")
    
    if len(certificates) > limit:
        print(f"\n... and {len(certificates) - limit} more certificates")
        print(f"💡 Use --limit {len(certificates)} to see all certificates")

def bulk_generate(cert_gen, csv_file):
    """Generate certificates from CSV file"""
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' not found.")
        return
    
    print(f"📂 Reading CSV file: {csv_file}")
    
    recipients = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
            # Skip header if present
            if lines and 'recipient_name' in lines[0].lower():
                lines = lines[1:]
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 3:
                    print(f"⚠️  Warning: Line {line_num} has insufficient data, skipping.")
                    continue
                
                recipient = {
                    'recipient_name': parts[0],
                    'course_name': parts[1],
                    'completion_date': parts[2],
                    'instructor_name': parts[3] if len(parts) > 3 else '',
                    'organization': parts[4] if len(parts) > 4 else 'Certificate Authority',
                    'grade': parts[5] if len(parts) > 5 else ''
                }
                recipients.append(recipient)
        
        if not recipients:
            print("❌ No valid recipient data found in CSV file.")
            return
        
        print(f"👥 Found {len(recipients)} recipients. Generating certificates...")
        print("-" * 60)
        
        generated_ids = []
        for i, recipient_data in enumerate(recipients, 1):
            try:
                cert_id = cert_gen.create_certificate_record(recipient_data)
                generated_ids.append(cert_id)
                print(f"✅ {i:2d}. {recipient_data['recipient_name']} → {cert_id}")
            except Exception as e:
                print(f"❌ {i:2d}. {recipient_data.get('recipient_name', 'Unknown')} → Error: {str(e)}")
        
        print("-" * 60)
        print(f"🎉 Successfully generated {len(generated_ids)} certificates!")
        print(f"📁 Text files saved in: certificates/ directory")
        print(f"🌐 View online: http://localhost:5000/certificates")
    
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")

if __name__ == '__main__':
    print("🎓 Certificate Generation System CLI")
    print("=" * 50)
    main()