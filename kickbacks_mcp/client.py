"""
Kickbacks.ai API Client

HTTP client for Kickbacks.ai API. Replace mock responses with real API calls
when Kickbacks provides API access (contact support@kickbacks.ai).
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_API_BASE = "https://api.kickbacks.ai/v1"
KICKBACKS_API_KEY_ENV = "KICKBACKS_API_KEY"
KICKBACKS_USER_ID_ENV = "KICKBACKS_USER_ID"


@dataclass
class KickbacksConfig:
    """Configuration for Kickbacks API client."""

    api_key: str = ""
    user_id: str = ""
    api_base: str = DEFAULT_API_BASE
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "KickbacksConfig":
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv(KICKBACKS_API_KEY_ENV, ""),
            user_id=os.getenv(KICKBACKS_USER_ID_ENV, ""),
            api_base=os.getenv("KICKBACKS_API_BASE", DEFAULT_API_BASE),
        )

    def is_configured(self) -> bool:
        """Check if minimum required credentials are present."""
        return bool(self.api_key)


# =============================================================================
# Data Models
# =============================================================================

class BalanceResponse(BaseModel):
    balance: float
    currency: str = "USD"
    updated_at: str


class EarningsResponse(BaseModel):
    today: float = 0.0
    this_week: float = 0.0
    this_month: float = 0.0
    total: float = 0.0
    currency: str = "USD"


class AdEvent(BaseModel):
    id: str
    timestamp: str
    ad_id: str
    campaign: str
    surface: str  # "spinner", "statusbar", "terminal"
    event_type: str  # "impression", "click"
    revenue: float = 0.0
    clicked: bool = False


class AdsHistoryResponse(BaseModel):
    items: List[AdEvent] = Field(default_factory=list)
    total: int = 0


class StatusResponse(BaseModel):
    connected: bool = False
    authenticated: bool = False
    enabled: bool = True
    hourly_cap: bool = False
    daily_cap: bool = False
    hourly_cap_resets_at: Optional[str] = None
    daily_cap_resets_at: Optional[str] = None
    last_sync: Optional[str] = None
    supported_surfaces: List[str] = Field(default_factory=lambda: ["spinner", "statusbar"])
    current_session_impressions: int = 0
    current_session_clicks: int = 0


class SetEnabledResponse(BaseModel):
    enabled: bool


class ConfigResponse(BaseModel):
    configured: bool
    has_api_key: bool
    has_user_id: bool
    api_base: str
    env_vars: Dict[str, str]
    setup_help: Optional[str] = None


# =============================================================================
# API Client
# =============================================================================

class KickbacksClient:
    """
    HTTP client for Kickbacks.ai API.

    NOTE: Currently uses mock responses for development.
    When Kickbacks provides API access, replace _mock_response with real HTTP calls.
    """

    def __init__(self, config: Optional[KickbacksConfig] = None):
        self.config = config or KickbacksConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Kickbacks-MCP/0.1.0",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=self._get_headers(),
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Kickbacks API."""
        # TODO: Replace with real HTTP when API is available
        # client = await self._get_client()
        # response = await client.request(
        #     method,
        #     f"{self.config.api_base}{endpoint}",
        #     **kwargs
        # )
        # response.raise_for_status()
        # return response.json()

        # Mock responses for development
        import logging
        logging.warning("Kickbacks API not implemented - returning mock data")
        return self._mock_response(method, endpoint)

    def _mock_response(self, method: str, endpoint: str) -> Dict[str, Any]:
        """Return mock data for development."""
        base_endpoint = endpoint.split("?")[0]

        if base_endpoint == "/balance":
            return {
                "balance": 42.50,
                "currency": "USD",
                "updated_at": datetime.now().isoformat(),
            }
        elif base_endpoint == "/earnings":
            return {
                "today": 0.42,
                "this_week": 7.11,
                "this_month": 42.50,
                "total": 156.78,
                "currency": "USD",
            }
        elif base_endpoint == "/status":
            return {
                "connected": True,
                "authenticated": True,
                "enabled": True,
                "hourly_cap": False,
                "daily_cap": False,
                "hourly_cap_resets_at": None,
                "daily_cap_resets_at": None,
                "last_sync": datetime.now().isoformat(),
                "supported_surfaces": ["spinner", "statusbar"],
                "current_session_impressions": 23,
                "current_session_clicks": 2,
            }
        elif base_endpoint == "/ads/history":
            return {
                "items": [
                    {
                        "id": "evt_1",
                        "timestamp": datetime.now().isoformat(),
                        "ad_id": "ad_abc123",
                        "campaign": "Ramp - save time and money",
                        "surface": "spinner",
                        "event_type": "impression",
                        "revenue": 0.001,
                        "clicked": False,
                    },
                    {
                        "id": "evt_2",
                        "timestamp": datetime.now().isoformat(),
                        "ad_id": "ad_xyz789",
                        "campaign": "Bitcoin Devs Takeover Toronto",
                        "surface": "statusbar",
                        "event_type": "click",
                        "revenue": 0.05,
                        "clicked": True,
                    },
                ],
                "total": 2,
            }
        elif base_endpoint == "/enable":
            return {"enabled": True}
        elif base_endpoint == "/disable":
            return {"enabled": False}
        elif base_endpoint == "/config":
            return {
                "configured": self.config.is_configured(),
                "has_api_key": bool(self.config.api_key),
                "has_user_id": bool(self.config.user_id),
                "api_base": self.config.api_base,
                "env_vars": {
                    KICKBACKS_API_KEY_ENV: "set" if self.config.api_key else "NOT SET",
                    KICKBACKS_USER_ID_ENV: "set" if self.config.user_id else "NOT SET",
                },
                "setup_help": (
                    "To configure Kickbacks:\n"
                    "1. Get API credentials from support@kickbacks.ai\n"
                    f"2. Set {KICKBACKS_API_KEY_ENV} environment variable\n"
                    f"3. Optional: Set {KICKBACKS_USER_ID_ENV}" if not self.config.is_configured() else None
                ),
            }
        return {"error": f"Unknown endpoint: {endpoint}"}

    # =========================================================================
    # Public API Methods
    # =========================================================================

    async def get_balance(self) -> BalanceResponse:
        """Get current balance."""
        data = await self._request("GET", "/balance")
        return BalanceResponse(**data)

    async def get_earnings(self) -> EarningsResponse:
        """Get earnings breakdown by time period."""
        data = await self._request("GET", "/earnings")
        return EarningsResponse(**data)

    async def get_status(self) -> StatusResponse:
        """Get connection and earning status."""
        data = await self._request("GET", "/status")
        return StatusResponse(**data)

    async def get_ads_history(self, limit: int = 50, offset: int = 0) -> AdsHistoryResponse:
        """Get ad impression/click history with pagination."""
        data = await self._request("GET", f"/ads/history?limit={limit}&offset={offset}")
        return AdsHistoryResponse(**data)

    async def set_enabled(self, enabled: bool) -> SetEnabledResponse:
        """Enable or disable Kickbacks ads."""
        endpoint = "/enable" if enabled else "/disable"
        data = await self._request("POST", endpoint)
        return SetEnabledResponse(**data)

    async def get_config(self) -> ConfigResponse:
        """Get configuration status."""
        data = await self._request("GET", "/config")
        return ConfigResponse(**data)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None