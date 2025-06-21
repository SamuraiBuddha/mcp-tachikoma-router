"""Tachikoma Router Management MCP

Natural language router control for Claude.
Supports multiple router types with unified interface.
"""

__version__ = "0.1.0"
__author__ = "SamuraiBuddha"

from .server import main

__all__ = ["main"]
