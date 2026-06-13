#!/usr/bin/env python3
"""
Kickbacks.ai MCP Server

MCP server exposing Kickbacks.ai tools for AI agents.
Provides tools to check balance, earnings, status, ad history, and enable/disable ads.

Usage:
    uvx kickbacks-mcp
    # or
    python -m kickbacks_mcp.server

Environment Variables:
    KICKBACKS_API_KEY - API key from Kickbacks.ai (required)
    KICKBACKS_USER_ID - User ID (optional)
    KICKBACKS_API_BASE - Custom API base URL (optional)
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from .client import KickbacksClient, KickbacksConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Global client instance
_client: KickbacksClient | None = None


def get_client() -> KickbacksClient:
    """Get or create the global Kickbacks client."""
    global _client
    if _client is None:
        config = KickbacksConfig.from_env()
        _client = KickbacksClient(config)
    return _client


@asynccontextmanager
async def lifespan(server: Server):
    """Application lifespan manager."""
    logger.info("Kickbacks MCP server starting...")
    # Client is initialized lazily via get_client()
    yield
    logger.info("Kickbacks MCP server shutting down...")
    if _client:
        await _client.close()


# Create the MCP server
server = Server("kickbacks-mcp", lifespan=lifespan)


# =============================================================================
# Tool Definitions
# =============================================================================

TOOLS = [
    Tool(
        name="kickbacks_balance",
        description=(
            "Get current Kickbacks.ai balance. Shows total earnings available for withdrawal. "
            "Requires KICKBACKS_API_KEY environment variable. "
            "Contact support@kickbacks.ai for API access."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="kickbacks_earnings",
        description=(
            "Get Kickbacks.ai earnings breakdown by time period: today, this week, this month, and all-time total. "
            "Requires KICKBACKS_API_KEY environment variable."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="kickbacks_status",
        description=(
            "Get Kickbacks.ai connection status and earning state. Shows whether connected, authenticated, "
            "enabled, and if hourly/daily earning caps have been hit. "
            "Requires KICKBACKS_API_KEY environment variable."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="kickbacks_ads_history",
        description=(
            "Get recent ad impression and click history. Shows each ad shown, campaign name, surface (spinner/statusbar), "
            "event type, revenue earned, and whether it was clicked. Supports pagination. "
            "Requires KICKBACKS_API_KEY environment variable."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of items to return (1-100, default 20)",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
                "offset": {
                    "type": "integer",
                    "description": "Number of items to skip for pagination (default 0)",
                    "default": 0,
                    "minimum": 0,
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="kickbacks_set_enabled",
        description=(
            "Enable or disable Kickbacks.ai ads. When disabled, no ads are shown and no earnings accrue. "
            "When enabled, ads appear in supported AI agent spinners and status bars. "
            "Requires KICKBACKS_API_KEY environment variable."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "enabled": {
                    "type": "boolean",
                    "description": "True to enable ads, False to disable",
                },
            },
            "required": ["enabled"],
        },
    ),
    Tool(
        name="kickbacks_config",
        description=(
            "Check Kickbacks.ai configuration status. Shows whether API key is set and provides setup instructions if not. "
            "Safe to call - never exposes secrets."
        ),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]


# =============================================================================
# Tool Handlers
# =============================================================================

async def _handle_balance() -> CallToolResult:
    client = get_client()
    if not client.config.is_configured():
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    "Kickbacks not configured. Set KICKBACKS_API_KEY in environment. "
                    "Contact support@kickbacks.ai for API access."
                )
            )],
            isError=True,
        )
    try:
        result = await client.get_balance()
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Balance: {result.currency} {result.balance:.2f}\nUpdated: {result.updated_at}"
            )]
        )
    except Exception as e:
        logger.exception("Failed to get balance")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to get balance: {e}")],
            isError=True,
        )


async def _handle_earnings() -> CallToolResult:
    client = get_client()
    if not client.config.is_configured():
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    "Kickbacks not configured. Set KICKBACKS_API_KEY in environment. "
                    "Contact support@kickbacks.ai for API access."
                )
            )],
            isError=True,
        )
    try:
        result = await client.get_earnings()
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    f"Earnings Breakdown:\n"
                    f"  Today: ${result.today:.2f}\n"
                    f"  This Week: ${result.this_week:.2f}\n"
                    f"  This Month: ${result.this_month:.2f}\n"
                    f"  Total: ${result.total:.2f}\n"
                    f"  Currency: {result.currency}"
                )
            )]
        )
    except Exception as e:
        logger.exception("Failed to get earnings")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to get earnings: {e}")],
            isError=True,
        )


async def _handle_status() -> CallToolResult:
    client = get_client()
    if not client.config.is_configured():
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    "Kickbacks not configured. Set KICKBACKS_API_KEY in environment. "
                    "Contact support@kickbacks.ai for API access."
                )
            )],
            isError=True,
        )
    try:
        result = await client.get_status()
        status_parts = [
            f"Connected: {'✅' if result.connected else '❌'}",
            f"Authenticated: {'✅' if result.authenticated else '❌'}",
            f"Enabled: {'✅' if result.enabled else '❌'}",
        ]
        if result.hourly_cap:
            reset = f" (resets {result.hourly_cap_resets_at})" if result.hourly_cap_resets_at else ""
            status_parts.append(f"⚠ Hourly cap hit{reset}")
        if result.daily_cap:
            reset = f" (resets {result.daily_cap_resets_at})" if result.daily_cap_resets_at else ""
            status_parts.append(f"⚠ Daily cap hit{reset}")
        if result.last_sync:
            status_parts.append(f"Last sync: {result.last_sync}")
        status_parts.append(
            f"Session: {result.current_session_impressions} impressions, "
            f"{result.current_session_clicks} clicks"
        )
        return CallToolResult(
            content=[TextContent(type="text", text=" | ".join(status_parts))]
        )
    except Exception as e:
        logger.exception("Failed to get status")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to get status: {e}")],
            isError=True,
        )


async def _handle_ads_history(limit: int = 20, offset: int = 0) -> CallToolResult:
    client = get_client()
    if not client.config.is_configured():
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    "Kickbacks not configured. Set KICKBACKS_API_KEY in environment. "
                    "Contact support@kickbacks.ai for API access."
                )
            )],
            isError=True,
        )
    # Clamp limits
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    try:
        result = await client.get_ads_history(limit=limit, offset=offset)
        if not result.items:
            return CallToolResult(
                content=[TextContent(type="text", text="No ad events found.")]
            )
        lines = [f"Ad History (showing {len(result.items)} of {result.total}):"]
        for event in result.items:
            event_icon = "👆" if event.clicked else "👁"
            lines.append(
                f"  {event_icon} [{event.timestamp}] {event.campaign} "
                f"({event.surface}) - ${event.revenue:.4f}"
            )
        return CallToolResult(
            content=[TextContent(type="text", text="\n".join(lines))]
        )
    except Exception as e:
        logger.exception("Failed to get ads history")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to get ads history: {e}")],
            isError=True,
        )


async def _handle_set_enabled(enabled: bool) -> CallToolResult:
    client = get_client()
    if not client.config.is_configured():
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=(
                    "Kickbacks not configured. Set KICKBACKS_API_KEY in environment. "
                    "Contact support@kickbacks.ai for API access."
                )
            )],
            isError=True,
        )
    try:
        result = await client.set_enabled(enabled)
        action = "enabled" if result.enabled else "disabled"
        return CallToolResult(
            content=[TextContent(type="text", text=f"Kickbacks ads {action}")]
        )
    except Exception as e:
        logger.exception("Failed to set enabled state")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to {'enable' if enabled else 'disable'} Kickbacks: {e}")],
            isError=True,
        )


async def _handle_config() -> CallToolResult:
    client = get_client()
    try:
        result = await client.get_config()
        lines = [
            f"Configured: {'✅' if result.configured else '❌'}",
            f"API Key: {'✅' if result.has_api_key else '❌'}",
            f"User ID: {'✅' if result.has_user_id else '❌'}",
            f"API Base: {result.api_base}",
        ]
        if result.setup_help:
            lines.append("\nSetup:")
            lines.append(result.setup_help)
        return CallToolResult(
            content=[TextContent(type="text", text="\n".join(lines))]
        )
    except Exception as e:
        logger.exception("Failed to get config")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Failed to get config: {e}")],
            isError=True,
        )


# =============================================================================
# MCP Protocol Handlers
# =============================================================================

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(tools=TOOLS)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Call a tool by name with arguments."""
    handlers = {
        "kickbacks_balance": _handle_balance,
        "kickbacks_earnings": _handle_earnings,
        "kickbacks_status": _handle_status,
        "kickbacks_ads_history": _handle_ads_history,
        "kickbacks_set_enabled": _handle_set_enabled,
        "kickbacks_config": _handle_config,
    }
    handler = handlers.get(name)
    if not handler:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Unknown tool: {name}")],
            isError=True,
        )
    return await handler(**arguments)


# =============================================================================
# Entry Point
# =============================================================================

async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())


def cli_main():
    """Sync entry point for console script."""
    asyncio.run(main())