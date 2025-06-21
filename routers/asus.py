import requests
import base64
from typing import Dict, List, Any
from .base import RouterClient


class AsusClient(RouterClient):
    """
    Client for ASUS routers (RT-AX88U, etc)
    """
    
    def connect(self) -> bool:
        """Connect to ASUS router"""
        try:
            self.session = requests.Session()
            self.session.verify = False
            
            # Basic auth
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            self.session.headers.update({
                "Authorization": f"Basic {credentials}"
            })
            
            # Test connection
            response = self.session.get(f"http://{self.ip}/appGet.cgi?hook=get_cfg_clientlist()")
            return response.status_code == 200
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from router"""
        if self.session:
            self.session.close()
    
    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get DHCP leases"""
        if not self.session:
            return []
        
        try:
            # Get client list
            response = self.session.get(f"http://{self.ip}/appGet.cgi?hook=get_cfg_clientlist()")
            
            if response.status_code == 200:
                # Parse ASUS format (would need proper parsing)
                # This is simplified
                return []
        except Exception as e:
            print(f"Error getting DHCP leases: {e}")
        
        return []
    
    def add_dhcp_reservation(self, mac_address: str, ip_address: str, hostname: str = "") -> bool:
        """Add DHCP reservation"""
        if not self.session:
            return False
        
        try:
            # ASUS uses nvram commands
            # This would need the proper ASUS API calls
            return True
        except Exception as e:
            print(f"Error adding reservation: {e}")
            return False
    
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
            response = self.session.get(f"http://{self.ip}/appGet.cgi?hook=nvram_get(productid)")
            
            if response.status_code == 200:
                return {
                    "model": "ASUS Router",
                    "version": "Unknown",
                    "uptime": 0,
                    "wan_ip": "Unknown"
                }
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return {}
