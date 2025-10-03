"""
QR Code Generator for Certificate Verification
Standalone QR code generation utility
"""

import qrcode
import json
import os
from PIL import Image
from typing import Dict, Optional

class QRCodeGenerator:
    """Dedicated QR code generator for certificates"""
    
    def __init__(self, output_dir: str = "qr_codes"):
        """Initialize QR code generator"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_certificate_qr(self, certificate_data: Dict, 
                               size: tuple = (300, 300),
                               error_correction: str = 'M') -> str:
        """Generate QR code for certificate verification"""
        
        # Prepare QR data
        qr_data = {
            "type": "certificate_verification",
            "certificate_id": certificate_data.get("certificate_id", ""),
            "recipient": certificate_data.get("recipient_name", ""),
            "course": certificate_data.get("course_name", ""),
            "completion_date": certificate_data.get("completion_date", ""),
            "verification_url": f"https://verify.certificates.com/{certificate_data.get('certificate_id', '')}"
        }
        
        # Convert to JSON
        qr_string = json.dumps(qr_data, separators=(',', ':'))
        
        # Set error correction level
        error_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=10,
            border=4,
        )
        
        qr.add_data(qr_string)
        qr.make(fit=True)
        
        # Create image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Resize if needed
        if size != (300, 300):
            qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
        
        # Save QR code
        filename = f"qr_{certificate_data.get('certificate_id', 'unknown')}.png"
        filepath = os.path.join(self.output_dir, filename)
        qr_image.save(filepath)
        
        return filepath
    
    def generate_custom_qr(self, data: str, filename: str = "custom_qr.png",
                          size: tuple = (300, 300)) -> str:
        """Generate custom QR code with any data"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
        
        filepath = os.path.join(self.output_dir, filename)
        qr_image.save(filepath)
        
        return filepath
    
    def generate_styled_qr(self, data: str, filename: str = "styled_qr.png",
                          fill_color: str = "black", back_color: str = "white",
                          size: tuple = (300, 300)) -> str:
        """Generate styled QR code with custom colors"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
        qr_image = qr_image.resize(size, Image.Resampling.LANCZOS)
        
        filepath = os.path.join(self.output_dir, filename)
        qr_image.save(filepath)
        
        return filepath

# Example usage
if __name__ == "__main__":
    # Initialize QR generator
    qr_gen = QRCodeGenerator()
    
    # Sample certificate data
    sample_cert = {
        "certificate_id": "CERT_12345ABC",
        "recipient_name": "Alice Johnson",
        "course_name": "Data Science Fundamentals",
        "completion_date": "2025-10-03"
    }
    
    # Generate certificate QR code
    print("Generating certificate QR code...")
    qr_path = qr_gen.generate_certificate_qr(sample_cert)
    print(f"QR code saved: {qr_path}")
    
    # Generate custom QR code
    print("\nGenerating custom QR code...")
    custom_qr = qr_gen.generate_custom_qr("https://example.com", "example_qr.png")
    print(f"Custom QR code saved: {custom_qr}")
    
    # Generate styled QR code
    print("\nGenerating styled QR code...")
    styled_qr = qr_gen.generate_styled_qr(
        "Certificate Verification System", 
        "styled_qr.png",
        fill_color="darkblue",
        back_color="lightgray"
    )
    print(f"Styled QR code saved: {styled_qr}")