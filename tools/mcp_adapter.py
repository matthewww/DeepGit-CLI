import httpx
import logging
import os

logger = logging.getLogger(__name__)

def _ssl_verify():
    """Return the CA bundle path from env, or True (default verify) if not set."""
    return os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE") or True

class MCPAdapter:
    def __init__(self):
        self.adapter_name = "GitHub MCP Adapter"

    async def fetch(self, url: str, headers: dict = None, params: dict = None, client: httpx.AsyncClient = None):
        try:
            if client is None:
                async with httpx.AsyncClient(verify=_ssl_verify()) as temp_client:
                    response = await temp_client.get(url, headers=headers, params=params)
            else:
                response = await client.get(url, headers=headers, params=params)
            logger.info(f"[{self.adapter_name}] Fetched URL: {url} with status {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"[{self.adapter_name}] Error fetching {url}: {e}")
            raise e

mcp_adapter = MCPAdapter()
