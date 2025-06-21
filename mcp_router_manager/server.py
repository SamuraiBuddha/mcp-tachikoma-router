#!/usr/bin/env python3
"""MCP Server for Router Management"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any

from mcp import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .routers import RouterFactory, BaseRouter
from .models import DHCPReservation, PortForward, NetworkDevice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouterManagerServer:
    """MCP Server for router management"""
    
    def __init__(self):
        self.server = Server("tachikoma-router")
        self.router: Optional[BaseRouter] = None
        self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available router management tools"""
            return [
                Tool(
                    name="connect_router",
                    description="Connect to a router at specified IP address",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string", "description": "Router IP address"},
                            "username": {"type": "string", "description": "Router username"},
                            "password": {"type": "string", "description": "Router password"},
                            "router_type": {
                                "type": "string", 
                                "description": "Router type (auto, unifi, asus, netgear, pfsense, openwrt)",
                                "default": "auto"
                            }
                        },
                        "required": ["ip", "username", "password"]
                    }
                ),
                Tool(
                    name="list_dhcp_reservations",
                    description="List all DHCP reservations",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="add_dhcp_reservation",
                    description="Add a DHCP reservation for a device",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mac": {"type": "string", "description": "MAC address"},
                            "ip": {"type": "string", "description": "IP address to reserve"},
                            "hostname": {"type": "string", "description": "Device hostname"}
                        },
                        "required": ["mac", "ip"]
                    }
                ),
                Tool(
                    name="remove_dhcp_reservation",
                    description="Remove a DHCP reservation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "mac": {"type": "string", "description": "MAC address"}
                        },
                        "required": ["mac"]
                    }
                ),
                Tool(
                    name="list_port_forwards",
                    description="List all port forwarding rules",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="add_port_forward",
                    description="Add a port forwarding rule",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Rule name"},
                            "external_port": {"type": "integer", "description": "External port"},
                            "internal_ip": {"type": "string", "description": "Internal IP address"},
                            "internal_port": {"type": "integer", "description": "Internal port"},
                            "protocol": {
                                "type": "string", 
                                "description": "Protocol (tcp, udp, both)",
                                "default": "tcp"
                            }
                        },
                        "required": ["name", "external_port", "internal_ip", "internal_port"]
                    }
                ),
                Tool(
                    name="remove_port_forward",
                    description="Remove a port forwarding rule",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Rule name"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="list_connected_devices",
                    description="List all currently connected devices",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_network_status",
                    description="Get current network status and statistics",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="backup_configuration",
                    description="Backup router configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string", 
                                "description": "Backup filename (optional)"
                            }
                        }
                    }
                ),
                Tool(
                    name="setup_eva_network",
                    description="Quick setup for EVA Network infrastructure",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a router management tool"""
            
            try:
                if name == "connect_router":
                    return await self._connect_router(**arguments)
                
                # Ensure we're connected for other operations
                if not self.router:
                    return [TextContent(
                        type="text",
                        text="Error: Not connected to a router. Use 'connect_router' first."
                    )]
                
                # Route to appropriate handler
                handlers = {
                    "list_dhcp_reservations": self._list_dhcp_reservations,
                    "add_dhcp_reservation": self._add_dhcp_reservation,
                    "remove_dhcp_reservation": self._remove_dhcp_reservation,
                    "list_port_forwards": self._list_port_forwards,
                    "add_port_forward": self._add_port_forward,
                    "remove_port_forward": self._remove_port_forward,
                    "list_connected_devices": self._list_connected_devices,
                    "get_network_status": self._get_network_status,
                    "backup_configuration": self._backup_configuration,
                    "setup_eva_network": self._setup_eva_network
                }
                
                handler = handlers.get(name)
                if not handler:
                    return [TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )]
                
                return await handler(**arguments)
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def _connect_router(self, ip: str, username: str, password: str, 
                            router_type: str = "auto") -> List[TextContent]:
        """Connect to a router"""
        try:
            self.router = await RouterFactory.create_router(
                router_type=router_type,
                ip=ip,
                username=username,
                password=password
            )
            
            await self.router.connect()
            info = await self.router.get_system_info()
            
            return [TextContent(
                type="text",
                text=f"Successfully connected to {info.get('model', 'router')} at {ip}\n"
                     f"Firmware: {info.get('firmware', 'Unknown')}\n"
                     f"Router Type: {self.router.router_type}"
            )]
            
        except Exception as e:
            logger.error(f"Failed to connect to router: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to connect to router: {str(e)}"
            )]
    
    async def _list_dhcp_reservations(self) -> List[TextContent]:
        """List DHCP reservations"""
        reservations = await self.router.get_dhcp_reservations()
        
        if not reservations:
            return [TextContent(type="text", text="No DHCP reservations found.")]
        
        lines = ["DHCP Reservations:", "-" * 60]
        for res in reservations:
            lines.append(f"MAC: {res.mac_address} | IP: {res.ip_address} | "
                        f"Hostname: {res.hostname or 'N/A'}")
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _add_dhcp_reservation(self, mac: str, ip: str, 
                                   hostname: Optional[str] = None) -> List[TextContent]:
        """Add DHCP reservation"""
        reservation = DHCPReservation(
            mac_address=mac,
            ip_address=ip,
            hostname=hostname
        )
        
        success = await self.router.add_dhcp_reservation(reservation)
        
        if success:
            return [TextContent(
                type="text",
                text=f"Successfully added DHCP reservation: {mac} -> {ip}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to add DHCP reservation"
            )]
    
    async def _remove_dhcp_reservation(self, mac: str) -> List[TextContent]:
        """Remove DHCP reservation"""
        success = await self.router.remove_dhcp_reservation(mac)
        
        if success:
            return [TextContent(
                type="text",
                text=f"Successfully removed DHCP reservation for {mac}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to remove DHCP reservation"
            )]
    
    async def _list_port_forwards(self) -> List[TextContent]:
        """List port forwarding rules"""
        forwards = await self.router.get_port_forwards()
        
        if not forwards:
            return [TextContent(type="text", text="No port forwarding rules found.")]
        
        lines = ["Port Forwarding Rules:", "-" * 80]
        for fwd in forwards:
            lines.append(
                f"Name: {fwd.name} | External: {fwd.external_port} | "
                f"Internal: {fwd.internal_ip}:{fwd.internal_port} | "
                f"Protocol: {fwd.protocol}"
            )
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _add_port_forward(self, name: str, external_port: int,
                               internal_ip: str, internal_port: int,
                               protocol: str = "tcp") -> List[TextContent]:
        """Add port forwarding rule"""
        forward = PortForward(
            name=name,
            external_port=external_port,
            internal_ip=internal_ip,
            internal_port=internal_port,
            protocol=protocol
        )
        
        success = await self.router.add_port_forward(forward)
        
        if success:
            return [TextContent(
                type="text",
                text=f"Successfully added port forward: {name} "
                     f"({external_port} -> {internal_ip}:{internal_port})"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to add port forwarding rule"
            )]
    
    async def _remove_port_forward(self, name: str) -> List[TextContent]:
        """Remove port forwarding rule"""
        success = await self.router.remove_port_forward(name)
        
        if success:
            return [TextContent(
                type="text",
                text=f"Successfully removed port forward: {name}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Failed to remove port forwarding rule"
            )]
    
    async def _list_connected_devices(self) -> List[TextContent]:
        """List connected devices"""
        devices = await self.router.get_connected_devices()
        
        if not devices:
            return [TextContent(type="text", text="No connected devices found.")]
        
        lines = ["Connected Devices:", "-" * 80]
        for dev in devices:
            status = "Active" if dev.is_active else "Inactive"
            lines.append(
                f"MAC: {dev.mac_address} | IP: {dev.ip_address} | "
                f"Hostname: {dev.hostname or 'Unknown'} | Status: {status}"
            )
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _get_network_status(self) -> List[TextContent]:
        """Get network status"""
        status = await self.router.get_network_status()
        
        lines = [
            "Network Status:",
            "-" * 40,
            f"WAN IP: {status.get('wan_ip', 'Unknown')}",
            f"LAN Network: {status.get('lan_network', 'Unknown')}",
            f"DHCP Range: {status.get('dhcp_start', 'N/A')} - {status.get('dhcp_end', 'N/A')}",
            f"DNS Servers: {', '.join(status.get('dns_servers', []))}",
            f"Uptime: {status.get('uptime', 'Unknown')}"
        ]
        
        return [TextContent(type="text", text="\n".join(lines))]
    
    async def _backup_configuration(self, filename: Optional[str] = None) -> List[TextContent]:
        """Backup router configuration"""
        if not filename:
            from datetime import datetime
            filename = f"router_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.conf"
        
        filepath = await self.router.backup_configuration(filename)
        
        if filepath:
            return [TextContent(
                type="text",
                text=f"Configuration backed up to: {filepath}"
            )]
        else:
            return [TextContent(
                type="text",
                text="Failed to backup configuration"
            )]
    
    async def _setup_eva_network(self) -> List[TextContent]:
        """Quick setup for EVA Network"""
        # EVA Network node configuration
        eva_nodes = [
            DHCPReservation("aa:bb:cc:dd:ee:10", "192.168.50.10", "lilith"),
            DHCPReservation("aa:bb:cc:dd:ee:11", "192.168.50.11", "adam"),
            DHCPReservation("aa:bb:cc:dd:ee:20", "192.168.50.20", "balthazar"),
            DHCPReservation("aa:bb:cc:dd:ee:21", "192.168.50.21", "caspar"),
            DHCPReservation("aa:bb:cc:dd:ee:30", "192.168.50.30", "melchior")
        ]
        
        # Port forwards for services
        eva_forwards = [
            PortForward("portainer", 9000, "192.168.50.10", 9000, "tcp"),
            PortForward("neo4j", 7474, "192.168.50.10", 7474, "tcp"),
            PortForward("comfyui", 8188, "192.168.50.20", 8188, "tcp"),
            PortForward("ssh-caspar", 9222, "192.168.50.21", 9222, "tcp")
        ]
        
        results = ["EVA Network Setup Results:", "=" * 40]
        
        # Add DHCP reservations
        results.append("\nDHCP Reservations:")
        for node in eva_nodes:
            # Note: You'll need to update with actual MAC addresses
            results.append(f"  - {node.hostname}: {node.ip_address} (Configure MAC manually)")
        
        # Add port forwards
        results.append("\nPort Forwards:")
        for fwd in eva_forwards:
            success = await self.router.add_port_forward(fwd)
            status = "✓" if success else "✗"
            results.append(f"  {status} {fwd.name}: {fwd.external_port} -> "
                          f"{fwd.internal_ip}:{fwd.internal_port}")
        
        results.append("\nNote: Update DHCP reservations with actual MAC addresses")
        
        return [TextContent(type="text", text="\n".join(results))]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="tachikoma-router",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities()
                )
            )


def main():
    """Main entry point"""
    import asyncio
    server = RouterManagerServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
