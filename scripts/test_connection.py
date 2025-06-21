#!/usr/bin/env python3
"""
Router Connection Test Utility
Tests connectivity and authentication to various router types
"""

import os
import sys
import requests
import argparse
from typing import Dict, Optional
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


class ConnectionTester:
    """Test router connections and authentication"""
    
    def __init__(self):
        load_dotenv()
        self.router_ip = os.getenv('ROUTER_IP', '192.168.1.1')
        self.router_type = os.getenv('ROUTER_TYPE', 'auto')
        self.username = os.getenv('ROUTER_USERNAME', 'admin')
        self.password = os.getenv('ROUTER_PASSWORD', '')
        self.session = requests.Session()
        self.session.verify = False
        
    def test_basic_connectivity(self) -> bool:
        """Test if router is reachable"""
        print(f"🔌 Testing connectivity to {self.router_ip}...")
        
        for protocol in ['http', 'https']:
            try:
                url = f"{protocol}://{self.router_ip}"
                resp = self.session.get(url, timeout=5)
                print(f"  ✅ {protocol.upper()} connection successful (Status: {resp.status_code})")
                return True
            except requests.exceptions.Timeout:
                print(f"  ⏱️  {protocol.upper()} connection timed out")
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {protocol.upper()} connection failed")
            except Exception as e:
                print(f"  ❌ {protocol.upper()} error: {type(e).__name__}")
        
        return False
    
    def test_unifi_auth(self) -> bool:
        """Test UniFi authentication"""
        print("\n🔐 Testing UniFi authentication...")
        
        try:
            url = f"https://{self.router_ip}:8443/api/login"
            data = {
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(url, json=data, timeout=10)
            
            if resp.status_code == 200:
                print("  ✅ Authentication successful")
                return True
            else:
                print(f"  ❌ Authentication failed (Status: {resp.status_code})")
                return False
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}: {str(e)}")
            return False
    
    def test_asus_auth(self) -> bool:
        """Test ASUS authentication"""
        print("\n🔐 Testing ASUS authentication...")
        
        try:
            # ASUS uses basic auth
            self.session.auth = (self.username, self.password)
            url = f"http://{self.router_ip}/ajax_status.asp"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                print("  ✅ Authentication successful")
                return True
            else:
                print(f"  ❌ Authentication failed (Status: {resp.status_code})")
                return False
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}: {str(e)}")
            return False
    
    def test_pfsense_auth(self) -> bool:
        """Test pfSense authentication"""
        print("\n🔐 Testing pfSense authentication...")
        
        try:
            # Get CSRF token first
            url = f"https://{self.router_ip}/index.php"
            resp = self.session.get(url, timeout=10)
            
            # Extract CSRF token (simplified - real implementation needs parsing)
            csrf_token = "test"  # Would extract from response
            
            # Login
            data = {
                '__csrf_magic': csrf_token,
                'usernamefld': self.username,
                'passwordfld': self.password,
                'login': 'Sign In'
            }
            resp = self.session.post(url, data=data, timeout=10)
            
            if 'Dashboard' in resp.text:
                print("  ✅ Authentication successful")
                return True
            else:
                print("  ❌ Authentication failed")
                return False
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}: {str(e)}")
            return False
    
    def test_openwrt_auth(self) -> bool:
        """Test OpenWRT authentication"""
        print("\n🔐 Testing OpenWRT authentication...")
        
        try:
            # OpenWRT uses RPC authentication
            url = f"http://{self.router_ip}/cgi-bin/luci/rpc/auth"
            data = {
                'username': self.username,
                'password': self.password
            }
            resp = self.session.post(url, json=data, timeout=10)
            
            if resp.status_code == 200 and resp.json().get('result'):
                print("  ✅ Authentication successful")
                return True
            else:
                print("  ❌ Authentication failed")
                return False
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}: {str(e)}")
            return False
    
    def test_environment_vars(self) -> Dict[str, str]:
        """Test environment variable configuration"""
        print("🔧 Checking environment configuration...")
        
        env_vars = {
            'ROUTER_IP': self.router_ip,
            'ROUTER_TYPE': self.router_type,
            'ROUTER_USERNAME': self.username,
            'ROUTER_PASSWORD': '***' if self.password else 'NOT SET'
        }
        
        # Router-specific vars
        if self.router_type == 'unifi':
            env_vars['UNIFI_SITE'] = os.getenv('UNIFI_SITE', 'default')
            env_vars['UNIFI_CONTROLLER'] = os.getenv('UNIFI_CONTROLLER', f'https://{self.router_ip}:8443')
        
        for key, value in env_vars.items():
            status = "✅" if value and value != 'NOT SET' else "⚠️"
            print(f"  {status} {key}: {value}")
        
        return env_vars
    
    def run_tests(self) -> bool:
        """Run all appropriate tests"""
        print(f"🚀 Tachikoma Router Connection Test")
        print(f"{'='*50}\n")
        
        # Check environment
        env_vars = self.test_environment_vars()
        
        if not self.password:
            print("\n⚠️  Warning: No password set in environment")
            return False
        
        # Test basic connectivity
        print("")
        if not self.test_basic_connectivity():
            print("\n❌ Router is not reachable. Check:")
            print("  - Router IP address is correct")
            print("  - Router is powered on")
            print("  - Network connection is working")
            return False
        
        # Test authentication based on router type
        auth_tests = {
            'unifi': self.test_unifi_auth,
            'asus': self.test_asus_auth,
            'pfsense': self.test_pfsense_auth,
            'openwrt': self.test_openwrt_auth,
        }
        
        if self.router_type in auth_tests:
            success = auth_tests[self.router_type]()
        else:
            print(f"\n⚠️  No specific auth test for router type: {self.router_type}")
            success = True
        
        # Summary
        print(f"\n{'='*50}")
        if success:
            print("✅ Connection test PASSED")
            print("\nYou're ready to use the Tachikoma Router MCP!")
        else:
            print("❌ Connection test FAILED")
            print("\nTroubleshooting tips:")
            print("  - Verify credentials in .env file")
            print("  - Check router type detection")
            print("  - Ensure router API/SSH is enabled")
            print("  - Try running with ROUTER_DEBUG=true")
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description='Test router connection and authentication'
    )
    parser.add_argument('--router-ip', help='Override router IP')
    parser.add_argument('--router-type', help='Override router type')
    
    args = parser.parse_args()
    
    # Override environment if specified
    if args.router_ip:
        os.environ['ROUTER_IP'] = args.router_ip
    if args.router_type:
        os.environ['ROUTER_TYPE'] = args.router_type
    
    tester = ConnectionTester()
    success = tester.run_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
