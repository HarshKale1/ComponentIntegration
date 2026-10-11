import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup


def validate_article_url(url: str) -> str:
    """Validate an article URL and reject local/private destinations."""
    if not url or not url.strip():
        raise ValueError("Article URL cannot be empty")

    parsed = urlparse(url.strip())

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")

    if not parsed.hostname:
        raise ValueError("Invalid article URL")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed")

    hostname = parsed.hostname.lower()

    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Local URLs are not allowed")

    try:
        addresses = [ipaddress.ip_address(hostname)]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(result[4][0])
                for result in socket.getaddrinfo(
                    hostname,
                    parsed.port or (443 if parsed.scheme == "https" else 80),
                    type=socket.SOCK_STREAM,
                )
            ]
        except socket.gaierror as exc:
            raise ValueError("Article hostname could not be resolved") from exc

    if not addresses:
        raise ValueError("Article hostname has no valid IP addresses")

    for address in addresses:
        if not address.is_global:
            raise ValueError("Private or non-public destinations are not allowed")

    return url.strip()


async def fetch_article_content(url: str) -> str:
    """Fetch a webpage and extract its readable text."""
    validated_url = validate_article_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; FinFlowAI/1.0)"
    }

    try:
        async with httpx.AsyncClient(
            timeout=15.0,
            headers=headers,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            response = await client.get(validated_url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(
            ["script", "style", "nav", "footer", "header", "aside"]
        ):
            element.decompose()

        return soup.get_text(separator=" ", strip=True)[:12000]

    except (httpx.HTTPError, ValueError):
        return ""
