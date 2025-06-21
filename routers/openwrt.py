import requests
import json
from typing import Dict, List, Any
from .base import RouterClient


class OpenWrtClient(RouterClient):
    """
    Client for OpenWrt routers using LuCI RPC
    """
    
    def __init__(self, ip: str, username: str, password: str):
        super().__init__(ip, username, password)
        self.auth_token = None
    
    def connect(self) -> bool:
        """Connect to OpenWrt router"""
        try:
            self.session = requests.Session()
            self.session.verify = False
            
            # Authenticate with LuCI
            auth_url = f"http://{self.ip}/cgi-bin/luci/rpc/auth"
            auth_data = {
                "id": 1,
                "method": "login",
                "params": [self.username, self.password]
            }
            
            response = self.session.post(auth_url, json=auth_data)
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get("result")
                return self.auth_token is not None
            
            return False
            
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from router"""
        if self.session:
            self.session.close()
        self.auth_token = None
    
    def _rpc_call(self, method: str, params: List[Any] = None) -> Any:
        """Make RPC call to OpenWrt"""
        if not self.auth_token:
            return None
        
        url = f"http://{self.ip}/cgi-bin/luci/rpc/sys?auth={self.auth_token}"
        data = {
            "id": 1,
            "method": method,
            "params": params or []
        }
        
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            return response.json().get("result")
        
        return None
    
    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get DHCP leases"""
        if not self.session or not self.auth_token:
            return []
        
        try:
            # Read dhcp.leases file
            leases_data = self._rpc_call("exec", ["cat", "/tmp/dhcp.leases"])
            
            if leases_data:
                leases = []
                # Parse lease file (simplified)
                return leases
        except Exception as e:
            print(f"Error getting DHCP leases: {e}")
        
        return []
    
    def add_dhcp_reservation(self, mac_address: str, ip_address: str, hostname: str = "") -> bool:
        """Add DHCP reservation"""
        if not self.session or not self.auth_token:
            return False
        
        try:
            # Use UCI to add reservation
            commands = [
                f"uci add dhcp host",
                f"uci set dhcp.@host[-1].mac='{mac_address}'",
                f"uci set dhcp.@host[-1].ip='{ip_address}'",
                f"uci set dhcp.@host[-1].name='{hostname or 'device'}'",
                f"uci commit dhcp",
                f"/etc/init.d/dnsmasq restart"
            ]
            
            for cmd in commands:
                self._rpc_call("exec", cmd.split())
            
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
        if not self.session or not self.auth_token:
            return False
        
        try:
            # Use UCI to add port forward
            commands = [
                f"uci add firewall redirect",
                f"uci set firewall.@redirect[-1].name='{name}'",
                f"uci set firewall.@redirect[-1].src='wan'",
                f"uci set firewall.@redirect[-1].dest='lan'",
                f"uci set firewall.@redirect[-1].proto='{protocol}'",
                f"uci set firewall.@redirect[-1].src_dport='{external_port}'",
                f"uci set firewall.@redirect[-1].dest_ip='{internal_ip}'",
                f"uci set firewall.@redirect[-1].dest_port='{internal_port}'",
                f"uci set firewall.@redirect[-1].target='DNAT'",
                f"uci commit firewall",
                f"/etc/init.d/firewall restart"
            ]
            
            for cmd in commands:
                self._rpc_call("exec", cmd.split())
            
            return True
            
        except Exception as e:
            print(f"Error adding port forward: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        if not self.session or not self.auth_token:
            return {}
        
        try:
            # Get system info
            info = self._rpc_call("exec", ["ubus", "call", "system", "board"])
            
            if info:
                data = json.loads(info)
                return {
                    "model": data.get("model", "OpenWrt Router"),
                    "version": data.get("release", {}).get("version", "Unknown"),
                    "uptime": 0,  # Would get from uptime command
                    "wan_ip": "Unknown"  # Would get from network info
                }
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return {}
