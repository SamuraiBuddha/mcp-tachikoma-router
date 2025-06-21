# Tachikoma Router Management MCP 🦖

A Model Context Protocol (MCP) server for natural language router management. Control your network infrastructure through Claude with support for multiple router types. Named after the AI tanks from Ghost in the Shell - because your router deserves to be sentient!

## Features

🌐 **Multi-Router Support**
- Ubiquiti UniFi / EdgeRouter
- ASUS (Merlin & Stock)
- Netgear
- pfSense
- OpenWRT/DD-WRT
- TP-Link

🛠️ **Core Capabilities**
- DHCP reservation management
- Port forwarding automation
- Network status monitoring
- Firewall rule configuration
- Bandwidth monitoring
- Configuration backup/restore

🤖 **Natural Language Interface**
- "Set up static IP for my NAS"
- "Forward port 9000 to Lilith"
- "Show me all DHCP reservations"
- "Backup router configuration"

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SamuraiBuddha/mcp-tachikoma-router.git
cd mcp-tachikoma-router
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure your router credentials:
```bash
cp .env.example .env
# Edit .env with your router details
```

4. Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "tachikoma-router": {
      "command": "python",
      "args": ["-m", "mcp_router_manager"],
      "cwd": "/path/to/mcp-tachikoma-router"
    }
  }
}
```

## Quick Start

### Detect Your Router
```bash
python scripts/detect_router.py 192.168.1.1
```

### EVA Network Quick Setup
For the EVA Network infrastructure:
```python
# In Claude:
"Connect to router at 192.168.50.1"
"Setup EVA network with static IPs for all nodes"
```

This automatically configures:
- Lilith: 192.168.50.10
- Adam: 192.168.50.11  
- Balthazar: 192.168.50.20
- Caspar: 192.168.50.21
- Melchior: 192.168.50.30

## Usage Examples

### Basic Commands
```
# Connect to router
"Connect to my router at 192.168.1.1"

# List devices
"Show all connected devices"
"List DHCP reservations"

# Add static IP
"Give my NAS a static IP at 192.168.1.100"
"Reserve 192.168.50.10 for device with MAC aa:bb:cc:dd:ee:ff"

# Port forwarding
"Forward port 9000 to my Portainer server"
"Open port 22 to 192.168.1.50 for SSH"

# Backup
"Backup router configuration"
"Restore configuration from backup"
```

### Advanced Usage
```
# Firewall rules
"Block all traffic from 192.168.1.99"
"Allow only port 80 and 443 from guest network"

# Network monitoring
"Show bandwidth usage for all devices"
"Which device is using the most bandwidth?"

# Bulk operations
"Set up static IPs for all my IoT devices"
"Forward ports 8000-8010 to my development server"
```

## Router-Specific Notes

### Ubiquiti UniFi
- Requires UniFi Controller (self-hosted or cloud)
- Uses API token authentication
- Full support for Dream Machine, USG, EdgeRouter

### ASUS Routers
- Best with Merlin firmware
- Stock firmware has limited API
- SSH access recommended for advanced features

### pfSense
- Full API support
- Requires API key generation
- Most comprehensive feature set

### OpenWRT
- Uses LuCI RPC API
- Excellent customization options
- Supports custom scripts

## Architecture

```
Claude Desktop
    ↓
 MCP Protocol
    ↓
Tachikoma Router MCP
    ↓
Router Abstraction Layer
    ↓
┌────────┬───────┬─────────┬─────────┐
│UniFi API│ASUS SSH│pfSense API│OpenWRT RPC│
└────────┴───────┴─────────┴─────────┘
```

## Environment Variables

```env
# Router connection
ROUTER_IP=192.168.50.1
ROUTER_TYPE=auto  # auto, unifi, asus, netgear, pfsense, openwrt

# Authentication
ROUTER_USERNAME=admin
ROUTER_PASSWORD=your_password

# UniFi specific
UNIFI_SITE=default
UNIFI_CONTROLLER=https://192.168.1.1:8443

# SSH (for ASUS/OpenWRT)
SSH_PORT=22
SSH_KEY_PATH=~/.ssh/id_rsa

# API Keys (if applicable)
API_KEY=your_api_key
```

## Security

🔒 **Best Practices:**
- Never commit .env files
- Use SSH keys when possible
- Enable HTTPS for API access
- Rotate credentials regularly
- Use read-only access when applicable

🛡️ **Built-in Protections:**
- Credentials never logged
- Encrypted credential storage
- Audit logging for all changes
- Automatic backup before changes
- Rate limiting on API calls

## Troubleshooting

### Connection Issues
```bash
# Test router connectivity
python scripts/test_connection.py

# Debug mode
ROUTER_DEBUG=true python -m mcp_router_manager
```

### Common Problems

**"Router type not detected"**
- Manually specify ROUTER_TYPE in .env
- Check if router web interface is accessible
- Verify correct IP address

**"Authentication failed"**
- Check username/password
- Some routers need admin privileges enabled
- Try SSH if web API fails

**"Operation not supported"**
- Not all routers support all features
- Check router-specific documentation
- Consider firmware upgrade

## Contributing

Contributions welcome! Especially for:
- Additional router support
- Enhanced security features
- Performance optimizations
- Documentation improvements

## Ghost in the Shell References 🌌

This MCP is themed after Ghost in the Shell's Section 9:

- **Tachikoma** - The main router interface (loyal, intelligent)
- **Motoko** - Firewall operations (the Major handles security)
- **Batou** - Network monitoring (always watching)
- **Aramaki** - Configuration management (the chief oversees all)

Future MCPs in the Section 9 suite:
- `mcp-motoko-firewall` - Advanced firewall management
- `mcp-batou-monitor` - Network monitoring and alerts
- `mcp-aramaki-orchestrator` - Multi-device orchestration

## License

MIT License - See LICENSE file

## Acknowledgments

- Built with the [Model Context Protocol](https://github.com/anthropics/mcp)
- Inspired by Ghost in the Shell: Stand Alone Complex
- Part of the EVA Network infrastructure suite

---

*"A router without natural language control is like a Tachikoma without oil - technically functional but missing its soul!"* 🦖
