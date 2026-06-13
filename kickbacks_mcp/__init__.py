"""
Kickbacks.ai MCP Server

MCP server for Kickbacks.ai - Earn ad revenue from AI coding agent spinners
(Claude Code, Codex). Provides tools to check balance, earnings, status,
ad history, and enable/disable ads.
"""

__version__ = "0.1.0"
__author__ = "Hermes Agent"

from .server import main

__all__ = ["main"]