"""
ModelNorth Sovereign LinkedIn Agent - MCP Protocol Gateway
https://modelnorth.com

High-speed programmatic bridge to LinkedIn Model Context Protocol (MCP) server.
Enables instant extraction, graph querying, and structured lead ingestion.
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger("sovereign_linkedin.mcp")


class MCPLinkedInClient:
    """Protocol adapter for LinkedIn MCP toolset."""

    def __init__(self, mcp_server_name: str = "linkedin"):
        self.server_name = mcp_server_name

    def format_search_people_payload(
        self,
        keywords: Optional[str] = None,
        title: Optional[str] = None,
        company: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 20
    ) -> dict[str, Any]:
        """Constructs standardized parameters for people search."""
        params: dict[str, Any] = {"limit": limit}
        if keywords:
            params["keywords"] = keywords
        if title:
            params["title"] = title
        if company:
            params["company"] = company
        if location:
            params["location"] = location
        return params

    def format_connect_payload(
        self,
        profile_url: str,
        message: Optional[str] = None
    ) -> dict[str, Any]:
        """Constructs parameters for sending a connection invitation."""
        payload: dict[str, Any] = {"profile_url": profile_url}
        if message:
            payload["message"] = message[:300]  # LinkedIn 300 char invite note limit
        return payload

    def format_message_payload(
        self,
        recipient_id: str,
        message_body: str
    ) -> dict[str, Any]:
        """Constructs parameters for direct 1-on-1 messaging."""
        return {
            "recipient_id": recipient_id,
            "message": message_body
        }
