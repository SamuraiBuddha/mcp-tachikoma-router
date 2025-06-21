#!/usr/bin/env python3
"""
MCP Tachikoma Router Management Server
Ghost in the Shell themed network automation
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server import McpServer, Request, Response
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from scripts.detect_router import detect_router
from routers.base import RouterClient
from routers.ubiquiti import UbiquitiClient
from routers.asus import AsusClient
from routers.netgear import NetgearClient
from routers.pfsense import PfSenseClient
from routers.openwrt import OpenWrtClient


class TachikomaServer:
    """
    Tachikoma MCP Server - Your friendly neighborhood router management AI
    Named after the spider tanks from Ghost in the Shell
    """
    
    def __init__(self):
        self.server = McpServer("Tachikoma Router Manager")
        self.router_cache: Dict[str, RouterClient] = {}
        
        # Register tools
        self._register_tools()
        
    def _register_tools(self):
        """Register all router management tools"""
        
        @self.server.tool()
        async def detect_router_type(ip: str = "192.168.50.1") -> TextContent:
            """
            Detect the type of router at the given IP address
            """
            router_info = detect_router(ip)
            return TextContent(
                type="text",
                text=json.dumps(router_info, indent=2)
            )
        
        @self.server.tool()
        async def connect_to_router(
            ip: str = "192.168.50.1",
            username: str = "admin",
            password: str = "",
            router_type: Optional[str] = None
        ) -> TextContent:
            """
            Connect to a router and cache the connection
            """
            try:
                # Auto-detect if type not provided
                if not router_type:
                    detection = detect_router(ip)
                    router_type = detection.get("type", "unknown")
                
                # Create appropriate client
                client = self._create_router_client(router_type, ip, username, password)
                
                # Test connection
                if client.connect():
                    self.router_cache[ip] = client
                    return TextContent(
                        type="text",
                        text=f"Successfully connected to {router_type} router at {ip}"
                    )
                else:
                    return TextContent(
                        type="text",
                        text=f"Failed to connect to router at {ip}"
                    )
                    
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error connecting to router: {str(e)}"
                )
        
        @self.server.tool()
        async def list_dhcp_leases(ip: str = "192.168.50.1") -> TextContent:
            """
            List all current DHCP leases on the router
            """
            client = self.router_cache.get(ip)
            if not client:
                return TextContent(
                    type="text",
                    text="Not connected to router. Use connect_to_router first."
                )
            
            try:
                leases = client.get_dhcp_leases()
                return TextContent(
                    type="text",
                    text=json.dumps(leases, indent=2)
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error getting DHCP leases: {str(e)}"
                )
        
        @self.server.tool()
        async def add_dhcp_reservation(
            ip: str = "192.168.50.1",
            mac_address: str = "",
            reserved_ip: str = "",
            hostname: str = ""
        ) -> TextContent:
            """
            Add a DHCP reservation for a specific MAC address
            """
            client = self.router_cache.get(ip)
            if not client:
                return TextContent(
                    type="text",
                    text="Not connected to router. Use connect_to_router first."
                )
            
            try:
                result = client.add_dhcp_reservation(mac_address, reserved_ip, hostname)
                return TextContent(
                    type="text",
                    text="DHCP reservation added successfully" if result else "Failed to add reservation"
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error adding DHCP reservation: {str(e)}"
                )
        
        @self.server.tool()
        async def list_port_forwards(ip: str = "192.168.50.1") -> TextContent:
            """
            List all port forwarding rules on the router
            """
            client = self.router_cache.get(ip)
            if not client:
                return TextContent(
                    type="text",
                    text="Not connected to router. Use connect_to_router first."
                )
            
            try:
                forwards = client.get_port_forwards()
                return TextContent(
                    type="text",
                    text=json.dumps(forwards, indent=2)
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error getting port forwards: {str(e)}"
                )
        
        @self.server.tool()
        async def add_port_forward(
            ip: str = "192.168.50.1",
            name: str = "",
            external_port: int = 0,
            internal_ip: str = "",
            internal_port: int = 0,
            protocol: str = "tcp"
        ) -> TextContent:
            """
            Add a port forwarding rule
            """
            client = self.router_cache.get(ip)
            if not client:
                return TextContent(
                    type="text",
                    text="Not connected to router. Use connect_to_router first."
                )
            
            try:
                result = client.add_port_forward(
                    name, external_port, internal_ip, internal_port, protocol
                )
                return TextContent(
                    type="text",
                    text="Port forward added successfully" if result else "Failed to add port forward"
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error adding port forward: {str(e)}"
                )
        
        @self.server.tool()
        async def get_network_info(ip: str = "192.168.50.1") -> TextContent:
            """
            Get general network information from the router
            """
            client = self.router_cache.get(ip)
            if not client:
                return TextContent(
                    type="text",
                    text="Not connected to router. Use connect_to_router first."
                )
            
            try:
                info = client.get_system_info()
                return TextContent(
                    type="text",
                    text=json.dumps(info, indent=2)
                )
            except Exception as e:
                return TextContent(
                    type="text",
                    text=f"Error getting network info: {str(e)}"
                )
        
        @self.server.tool()
        async def setup_eva_network() -> TextContent:
            """
            Configure network settings for the entire EVA infrastructure
            """
            eva_nodes = {
                "lilith": {"ip": "192.168.50.100", "mac": "00:00:00:00:01:00"},
                "adam": {"ip": "192.168.50.101", "mac": "00:00:00:00:01:01"},
                "melchior": {"ip": "192.168.50.10", "mac": "00:00:00:00:00:10"},
                "balthasar": {"ip": "192.168.50.11", "mac": "00:00:00:00:00:11"},
                "caspar": {"ip": "192.168.50.12", "mac": "00:00:00:00:00:12"}
            }
            
            results = []
            
            # Connect to router if not already
            if "192.168.50.1" not in self.router_cache:
                results.append("Connecting to router...")
                # This would need actual credentials
                results.append("Please connect to router first with credentials")
                return TextContent(
                    type="text",
                    text="\n".join(results)
                )
            
            client = self.router_cache["192.168.50.1"]
            
            # Add DHCP reservations for all EVA nodes
            for node_name, node_info in eva_nodes.items():
                try:
                    client.add_dhcp_reservation(
                        node_info["mac"],
                        node_info["ip"],
                        node_name
                    )
                    results.append(f"✓ Added DHCP reservation for {node_name}")
                except Exception as e:
                    results.append(f"✗ Failed to add reservation for {node_name}: {e}")
            
            # Add common port forwards
            port_forwards = [
                {"name": "SSH-Lilith", "ext": 22100, "int_ip": "192.168.50.100", "int": 22},
                {"name": "SSH-Adam", "ext": 22101, "int_ip": "192.168.50.101", "int": 22},
                {"name": "Portainer-Lilith", "ext": 9100, "int_ip": "192.168.50.100", "int": 9000},
                {"name": "Portainer-Adam", "ext": 9101, "int_ip": "192.168.50.101", "int": 9000},
            ]
            
            for pf in port_forwards:
                try:
                    client.add_port_forward(
                        pf["name"], pf["ext"], pf["int_ip"], pf["int"], "tcp"
                    )
                    results.append(f"✓ Added port forward: {pf['name']}")
                except Exception as e:
                    results.append(f"✗ Failed to add port forward {pf['name']}: {e}")
            
            return TextContent(
                type="text",
                text="\n".join(results)
            )
    
    def _create_router_client(self, router_type: str, ip: str, username: str, password: str) -> RouterClient:
        """Create the appropriate router client based on type"""
        clients = {
            "ubiquiti": UbiquitiClient,
            "asus": AsusClient,
            "netgear": NetgearClient,
            "pfsense": PfSenseClient,
            "openwrt": OpenWrtClient
        }
        
        client_class = clients.get(router_type.lower())
        if not client_class:
            raise ValueError(f"Unsupported router type: {router_type}")
        
        return client_class(ip, username, password)
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = TachikomaServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
