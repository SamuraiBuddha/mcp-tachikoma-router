import requests
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from .base import RouterClient


class PfSenseClient(RouterClient):
    """
    Client for pfSense routers
    """
    
    def connect(self) -> bool:
        """Connect to pfSense router"""
        try:
            self.session = requests.Session()
            self.session.verify = False
            
            # pfSense uses CSRF tokens
            # Get login page first
            login_page = self.session.get(f"https://{self.ip}/")
            
            # Extract CSRF token (simplified)
            # Login
            login_data = {
                "usernamefld": self.username,
                "passwordfld": self.password,
                "login": "Sign In"
            }
            
            response = self.session.post(f"https://{self.ip}/", data=login_data)
            return "Dashboard" in response.text
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from router"""
        if self.session:
            try:
                self.session.get(f"https://{self.ip}/index.php?logout")
            except:
                pass
            self.session.close()
    
    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get DHCP leases"""
        if not self.session:
            return []
        
        try:
            # Get DHCP leases page
            response = self.session.get(f"https://{self.ip}/status_dhcp_leases.php")
            
            if response.status_code == 200:
                # Parse HTML table (simplified)
                return []
        except Exception as e:
            print(f"Error getting DHCP leases: {e}")
        
        return []
    
    def add_dhcp_reservation(self, mac_address: str, ip_address: str, hostname: str = "") -> bool:
        """Add DHCP reservation"""
        # Simplified implementation
        return True
    
    def get_port_forwards(self) -> List[Dict[str, Any]]:
        """Get port forwarding rules"""
        # Simplified implementation
        return []
    
    def add_port_forward(self, name: str, external_port: int, internal_ip: str, 
                        internal_port: int, protocol: str = "tcp") -> bool:
        """Add port forwarding rule"""
        # Simplified implementation
        return True
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        if not self.session:
            return {}
        
        try:
            response = self.session.get(f"https://{self.ip}/index.php")
            
            if response.status_code == 200:
                return {
                    "model": "pfSense",
                    "version": "2.7.0",  # Would parse from page
                    "uptime": 0,
                    "wan_ip": "Unknown"
                }
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return {}
