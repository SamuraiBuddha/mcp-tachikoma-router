import requests
from typing import Dict, List, Any
from .base import RouterClient


class UbiquitiClient(RouterClient):
    """
    Client for Ubiquiti routers (UniFi, EdgeRouter)
    """
    
    def connect(self) -> bool:
        """Connect to Ubiquiti router"""
        try:
            self.session = requests.Session()
            self.session.verify = False  # Self-signed certs
            
            # Login to UniFi controller
            login_url = f"https://{self.ip}:8443/api/login"
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(login_url, json=login_data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from router"""
        if self.session:
            try:
                logout_url = f"https://{self.ip}:8443/api/logout"
                self.session.post(logout_url)
            except:
                pass
            self.session.close()
    
    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get DHCP leases from UniFi"""
        if not self.session:
            return []
        
        try:
            # Get active clients
            url = f"https://{self.ip}:8443/api/s/default/stat/sta"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                leases = []
                
                for client in data.get("data", []):
                    lease = {
                        "mac": client.get("mac", ""),
                        "ip": client.get("ip", ""),
                        "hostname": client.get("hostname", client.get("name", "")),
                        "vendor": client.get("oui", "")
                    }
                    leases.append(lease)
                
                return leases
        except Exception as e:
            print(f"Error getting DHCP leases: {e}")
        
        return []
    
    def add_dhcp_reservation(self, mac_address: str, ip_address: str, hostname: str = "") -> bool:
        """Add DHCP reservation in UniFi"""
        if not self.session:
            return False
        
        try:
            # Create fixed IP assignment
            url = f"https://{self.ip}:8443/api/s/default/rest/user"
            data = {
                "mac": mac_address.lower(),
                "use_fixedip": True,
                "fixed_ip": ip_address,
                "name": hostname or f"Device-{mac_address[-5:].replace(':', '')}"
            }
            
            response = self.session.post(url, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error adding reservation: {e}")
            return False
    
    def get_port_forwards(self) -> List[Dict[str, Any]]:
        """Get port forwarding rules"""
        if not self.session:
            return []
        
        try:
            # Get port forward rules
            url = f"https://{self.ip}:8443/api/s/default/rest/portforward"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                forwards = []
                
                for rule in data.get("data", []):
                    forward = {
                        "name": rule.get("name", ""),
                        "enabled": rule.get("enabled", False),
                        "external_port": rule.get("dst_port", ""),
                        "internal_ip": rule.get("fwd", ""),
                        "internal_port": rule.get("fwd_port", ""),
                        "protocol": rule.get("proto", "tcp")
                    }
                    forwards.append(forward)
                
                return forwards
        except Exception as e:
            print(f"Error getting port forwards: {e}")
        
        return []
    
    def add_port_forward(self, name: str, external_port: int, internal_ip: str, 
                        internal_port: int, protocol: str = "tcp") -> bool:
        """Add port forwarding rule"""
        if not self.session:
            return False
        
        try:
            url = f"https://{self.ip}:8443/api/s/default/rest/portforward"
            data = {
                "name": name,
                "enabled": True,
                "dst_port": str(external_port),
                "fwd": internal_ip,
                "fwd_port": str(internal_port),
                "proto": protocol.lower()
            }
            
            response = self.session.post(url, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error adding port forward: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        if not self.session:
            return {}
        
        try:
            # Get system info
            url = f"https://{self.ip}:8443/api/s/default/stat/sysinfo"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json().get("data", [{}])[0]
                return {
                    "model": data.get("model_name", "Unknown"),
                    "version": data.get("version", "Unknown"),
                    "uptime": data.get("uptime", 0),
                    "wan_ip": data.get("wan_ip", "Unknown")
                }
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return {}
