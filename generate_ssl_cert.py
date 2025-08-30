#!/usr/bin/env python3
"""
Generate SSL certificates for HTTPS development
This allows mobile camera access without HTTPS restrictions
"""

import os
import subprocess
import sys
from datetime import datetime, timedelta

def generate_self_signed_cert():
    """Generate self-signed SSL certificate for development"""
    
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ SSL certificates already exist")
        return True
    
    print("🔒 Generating self-signed SSL certificate for development...")
    
    try:
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa', '-out', key_file, '2048'
        ], check=True, capture_output=True)
        
        # Generate certificate
        subprocess.run([
            'openssl', 'req', '-new', '-x509', '-key', key_file, '-out', cert_file,
            '-days', '365', '-subj', '/C=US/ST=State/L=City/O=Organization/CN=localhost'
        ], check=True, capture_output=True)
        
        print("✅ SSL certificates generated successfully!")
        print(f"   Certificate: {cert_file}")
        print(f"   Private Key: {key_file}")
        print("   Valid for: 365 days")
        print()
        print("🚀 You can now start the app with HTTPS support:")
        print("   python3 app.py")
        print()
        print("📱 Mobile camera access will be available at:")
        print("   https://localhost:5001")
        print("   https://YOUR_IP:5001")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating SSL certificate: {e}")
        print("💡 Make sure OpenSSL is installed on your system")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL:")
        print("   macOS: brew install openssl")
        print("   Ubuntu: sudo apt-get install openssl")
        print("   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html")
        return False

def check_openssl():
    """Check if OpenSSL is available"""
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ OpenSSL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ OpenSSL not working properly")
            return False
    except FileNotFoundError:
        print("❌ OpenSSL not found")
        return False

def main():
    """Main function"""
    print("🔐 SSL Certificate Generator for Story Reader")
    print("=" * 50)
    
    # Check if OpenSSL is available
    if not check_openssl():
        print("\n💡 Alternative solutions:")
        print("1. Install OpenSSL and run this script again")
        print("2. Use localhost or local IP addresses (http://localhost:5001)")
        print("3. Use ngrok for HTTPS tunneling")
        print("4. Use a reverse proxy like nginx with SSL")
        return
    
    # Generate certificates
    if generate_self_signed_cert():
        print("\n🎉 Setup complete! Your app now supports HTTPS for mobile camera access.")
    else:
        print("\n❌ Failed to generate SSL certificates.")
        print("💡 You can still use the app with HTTP on localhost or local network IPs.")

if __name__ == "__main__":
    main()
