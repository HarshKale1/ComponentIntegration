
import asyncio
import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from gnews_decoder import decode


MAX_CONTENT_LENGTH = 12000
MAX_REDIRECTS = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def validate_article_url(url: str) -> str:
    """Validate a URL and reject local or private destinations."""

    if not url or not url.strip():
        raise ValueError("Article URL cannot be empty")

    url = url.strip()
    parsed = urlparse(url)

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
                ipaddress.ip_address(result[4][0].split("%")[0])
                for result in socket.getaddrinfo(
                    hostname,
                    parsed.port or (443 if parsed.scheme == "https" else 80),
                    type=socket.SOCK_STREAM,
                )
            ]
        except socket.gaierror as exc:
            raise ValueError(
                "Article hostname could not be resolved"
            ) from exc

    if not addresses:
        raise ValueError("Article hostname has no valid IP addresses")

    if any(not address.is_global for address in addresses):
        raise ValueError("Private or non-public destinations are not allowed")

    return url


async def fetch_article_content(url: str) -> str:
    """
    Fetch readable article text.

    Returns an empty string when the publisher blocks access,
    the page is unavailable, or the content cannot be extracted.
    """

    current_url = url

    try:
        # Resolve Google News RSS URLs to publisher URLs.
        parsed = urlparse(current_url)

        if (
            parsed.hostname
            and parsed.hostname.lower() == "news.google.com"
        ):
            current_url = await asyncio.wait_for(
                asyncio.to_thread(decode, current_url),
                timeout=8.0,
            )

            if not current_url:
                print(
                    "Article extraction failed: "
                    "Google News URL could not be resolved"
                )
                return ""

        timeout = httpx.Timeout(8.0, connect=4.0)

        async with httpx.AsyncClient(
            timeout=timeout,
            headers=HEADERS,
            follow_redirects=False,
            trust_env=False,
        ) as client:

            # Validate every URL and follow only a bounded number
            # of redirects.
            for _ in range(MAX_REDIRECTS + 1):
                current_url = validate_article_url(current_url)

                response = await client.get(current_url)

                if response.status_code in {
                    301, 302, 303, 307, 308
                }:
                    location = response.headers.get("location")

                    if not location:
                        print(
                            "Article extraction failed: "
                            "redirect has no destination"
                        )
                        return ""

                    current_url = urljoin(
                        str(response.url),
                        location,
                    )
                    continue

                if response.status_code in {401, 403, 404, 410, 429}:
                    print(
                        "Article unavailable for extraction: "
                        f"HTTP {response.status_code} "
                        f"at {response.url}"
                    )
                    return ""

                response.raise_for_status()

                content_type = response.headers.get(
                    "content-type", ""
                ).lower()

                if "html" not in content_type:
                    print(
                        "Article extraction failed: "
                        "response is not HTML"
                    )
                    return ""

                soup = BeautifulSoup(
                    response.text,
                    "html.parser",
                )

                # Remove elements that generally do not contain
                # article content.
                for element in soup(
                    [
                        "script",
                        "style",
                        "nav",
                        "footer",
                        "header",
                        "aside",
                        "form",
                        "noscript",
                        "svg",
                    ]
                ):
                    element.decompose()

                # Prefer article-specific content when available.
                article = soup.find("article")

                if article:
                    text = article.get_text(
                        separator=" ",
                        strip=True,
                    )
                else:
                    main = soup.find("main")

                    if main:
                        text = main.get_text(
                            separator=" ",
                            strip=True,
                        )
                    else:
                        text = soup.get_text(
                            separator=" ",
                            strip=True,
                        )

                text = " ".join(text.split())

                if not text:
                    print(
                        "Article extraction failed: "
                        "page contains no readable text"
                    )
                    return ""

                return text[:MAX_CONTENT_LENGTH]

            print(
                "Article extraction failed: "
                "redirect limit exceeded"
            )
            return ""

    except (
        httpx.HTTPError,
        ValueError,
        TimeoutError,
        OSError,
    ) as exc:
        print(
            f"Article extraction failed: "
            f"{type(exc).__name__}: {exc}"
        )
        return ""
