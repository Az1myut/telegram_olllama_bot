import httpx
import re


async def fetch_web_page(url: str) -> str:
    """
    Fetches the text content of a web page.
    Used by the agent automatically when it needs up-to-date information
    (e.g. when creating a Notion page about a current topic).
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Bot/1.0)"}
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text[:8000]
        except httpx.HTTPStatusError as e:
            return f"HTTP error fetching {url}: {e.response.status_code}"
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"


async def web_search_via_ddg(query: str) -> str:
    """
    Performs a DuckDuckGo HTML search and returns the top result snippets.
    No API key required.
    """
    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Bot/1.0)"}

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            response = await client.post(search_url, data=params, headers=headers)
            response.raise_for_status()
            text = response.text
            results = []
            parts = text.split('class="result__snippet"')
            for part in parts[1:6]:
                snippet_end = part.find("</a>")
                snippet = part[:snippet_end]
                clean = re.sub(r"<[^>]+>", "", snippet).strip()
                if clean:
                    results.append(clean)
            if results:
                return "\n\n".join(results)
            return "No results found."
        except Exception as e:
            return f"Search error: {str(e)}"