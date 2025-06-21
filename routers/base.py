from abc import ABC, abstractmethod
from typing import Dict, List, Any


class RouterClient(ABC):
    """
    Base class for router client implementations
    """
    
    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.username = username
        self.password = password
        self.session = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to router"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close connection to router"""
        pass
    
    @abstractmethod
    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get current DHCP leases"""
        pass
    
    @abstractmethod
    def add_dhcp_reservation(self, mac_address: str, ip_address: str, hostname: str = "") -> bool:
        """Add a DHCP reservation"""
        pass
    
    @abstractmethod
    def get_port_forwards(self) -> List[Dict[str, Any]]:
        """Get port forwarding rules"""
        pass
    
    @abstractmethod
    def add_port_forward(self, name: str, external_port: int, internal_ip: str, 
                        internal_port: int, protocol: str = "tcp") -> bool:
        """Add a port forwarding rule"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Get system/network information"""
        pass
