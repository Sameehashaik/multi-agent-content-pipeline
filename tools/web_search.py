"""
Web Search Tool - Tavily-powered web search

Used by the pipeline to gather real search results
before the Researcher agent runs. Tavily is optimized
for AI agents with clean, structured results.

Requires: TAVILY_API_KEY in .env
"""

from typing import List, Dict
import os
import logging

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Real web search using Tavily (optimized for AI agents).

    Returns clean, structured results with proper source extraction.
    Requires TAVILY_API_KEY environment variable.
    """

    def __init__(self):
        self.search_count = 0
        self._client = None
        logger.info("WebSearch initialized (Tavily)")

    def _get_client(self):
        """Lazy-load TavilyClient so the app doesn't crash if the key isn't set yet."""
        if self._client is None:
            from tavily import TavilyClient
            api_key = os.environ.get('TAVILY_API_KEY', '')
            if not api_key:
                raise ValueError(
                    "TAVILY_API_KEY not set. Add it to your .env file. "
                    "Get a free key at https://tavily.com"
                )
            self._client = TavilyClient(api_key=api_key)
        return self._client

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using Tavily.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of dicts with title, snippet, url, source
        """
        self.search_count += 1
        logger.info(f"Web search #{self.search_count}: {query}")

        try:
            response = self._get_client().search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )

            raw_results = response.get('results', [])

            results = []
            for r in raw_results:
                url = r.get('url', '')
                # Extract domain from URL for source field
                try:
                    source = url.split('/')[2] if url else 'unknown'
                except IndexError:
                    source = 'unknown'

                results.append({
                    'title': r.get('title', ''),
                    'snippet': r.get('content', ''),
                    'url': url,
                    'source': source,
                })

            logger.info(f"Found {len(results)} results for: {query}")
            return results

        except Exception as e:
            logger.warning(f"Web search failed: {e}. Returning empty results.")
            return [{
                'title': 'Search unavailable',
                'snippet': f'Web search failed: {str(e)}. The researcher will use its training data.',
                'url': '',
                'source': 'error',
            }]


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    search = WebSearchTool()
    results = search.search("Recent advances in RAG systems")
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"\n  Title: {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  Snippet: {r['snippet'][:120]}...")
