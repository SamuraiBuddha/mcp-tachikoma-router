#!/usr/bin/env python3
"""
Router Detection Utility
Automatically detects router type based on web interface fingerprinting
"""

import sys
import requests
import argparse
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


class RouterDetector:
    """Detects router type by analyzing web interface responses"""
    
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False  # Many routers use self-signed certs
        
    def detect_unifi(self, base_url: str) -> bool:
        """Detect UniFi Controller"""
        try:
            # UniFi controllers typically have /api/s/default/stat/health
            resp = self.session.get(f"{base_url}/api/s/default/stat/health", 
                                   timeout=self.timeout)
            return 'unifi' in resp.headers.get('Server', '').lower()
        except:
            pass
            
        try:
            # Try the login page
            resp = self.session.get(f"{base_url}/manage/account/login", 
                                   timeout=self.timeout)
            return 'unifi' in resp.text.lower()
        except:
            return False
    
    def detect_asus(self, base_url: str) -> bool:
        """Detect ASUS routers"""
        try:
            resp = self.session.get(f"{base_url}/Main_Login.asp", 
                                   timeout=self.timeout)
            return 'asus' in resp.text.lower() or 'rt-' in resp.text.lower()
        except:
            pass
            
        try:
            # Check for ASUS specific endpoints
            resp = self.session.get(f"{base_url}/ajax_status.asp", 
                                   timeout=self.timeout)
            return resp.status_code == 200
        except:
            return False
    
    def detect_netgear(self, base_url: str) -> bool:
        """Detect Netgear routers"""
        try:
            resp = self.session.get(base_url, timeout=self.timeout)
            return 'netgear' in resp.text.lower()
        except:
            pass
            
        try:
            # Netgear often uses this endpoint
            resp = self.session.get(f"{base_url}/setup.cgi", 
                                   timeout=self.timeout)
            return 'netgear' in resp.headers.get('Server', '').lower()
        except:
            return False
    
    def detect_pfsense(self, base_url: str) -> bool:
        """Detect pfSense"""
        try:
            resp = self.session.get(base_url, timeout=self.timeout)
            return 'pfsense' in resp.text.lower()
        except:
            pass
            
        try:
            # pfSense login page
            resp = self.session.get(f"{base_url}/index.php", 
                                   timeout=self.timeout)
            return 'pfsense' in resp.text.lower()
        except:
            return False
    
    def detect_openwrt(self, base_url: str) -> bool:
        """Detect OpenWRT/DD-WRT"""
        try:
            # LuCI interface
            resp = self.session.get(f"{base_url}/cgi-bin/luci", 
                                   timeout=self.timeout)
            return resp.status_code in [200, 302]
        except:
            pass
            
        try:
            resp = self.session.get(base_url, timeout=self.timeout)
            text_lower = resp.text.lower()
            return 'openwrt' in text_lower or 'dd-wrt' in text_lower
        except:
            return False
    
    def detect_tplink(self, base_url: str) -> bool:
        """Detect TP-Link routers"""
        try:
            resp = self.session.get(base_url, timeout=self.timeout)
            return 'tp-link' in resp.text.lower() or 'tplink' in resp.text.lower()
        except:
            pass
            
        try:
            # TP-Link specific endpoint
            resp = self.session.get(f"{base_url}/userRpm/LoginRpm.htm", 
                                   timeout=self.timeout)
            return resp.status_code == 200
        except:
            return False
    
    def detect_router_type(self, ip: str) -> Tuple[Optional[str], Dict[str, bool]]:
        """
        Detect router type by trying various detection methods
        
        Returns:
            Tuple of (detected_type, results_dict)
        """
        # Try both HTTP and HTTPS
        results = {}
        
        for protocol in ['http', 'https']:
            base_url = f"{protocol}://{ip}"
            
            # Test each router type
            tests = [
                ('unifi', self.detect_unifi),
                ('asus', self.detect_asus),
                ('netgear', self.detect_netgear),
                ('pfsense', self.detect_pfsense),
                ('openwrt', self.detect_openwrt),
                ('tplink', self.detect_tplink),
            ]
            
            for router_type, detect_func in tests:
                key = f"{router_type}_{protocol}"
                try:
                    results[key] = detect_func(base_url)
                    if results[key]:
                        return router_type, results
                except Exception as e:
                    results[key] = False
        
        return None, results


def main():
    parser = argparse.ArgumentParser(description='Detect router type')
    parser.add_argument('ip', help='Router IP address')
    parser.add_argument('--timeout', type=int, default=5, 
                       help='Connection timeout in seconds')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed results')
    
    args = parser.parse_args()
    
    print(f"🔍 Detecting router type at {args.ip}...")
    
    detector = RouterDetector(timeout=args.timeout)
    router_type, results = detector.detect_router_type(args.ip)
    
    if args.verbose:
        print("\nDetection Results:")
        for test, result in results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test}")
    
    if router_type:
        print(f"\n✅ Router detected: {router_type.upper()}")
        print(f"\nAdd to your .env file:")
        print(f"ROUTER_TYPE={router_type}")
        print(f"ROUTER_IP={args.ip}")
        return 0
    else:
        print("\n❌ Could not detect router type")
        print("\nPossible reasons:")
        print("  - Router is not accessible at this IP")
        print("  - Router type is not supported")
        print("  - Web interface is disabled")
        print("\nTry manually setting ROUTER_TYPE in your .env file")
        return 1


if __name__ == "__main__":
    sys.exit(main())
