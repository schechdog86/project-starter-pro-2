"""
Web Search Skill
----------------
Search the web using DuckDuckGo.
"""

import requests
from bs4 import BeautifulSoup
from backend.app.skills.base import BaseSkill


class WebSearchSkill(BaseSkill):
    """Simple web search using DuckDuckGo."""

    def execute(self, query: str, num_results: int = 5):
        """
        Search the web for information.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            Dictionary with results list
        """
        # Validate parameters
        self.validate_params({"query": query, "num_results": num_results})

        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(
                "https://duckduckgo.com/html/",
                params={"q": query},
                headers=headers,
                timeout=20
            )
            soup = BeautifulSoup(r.text, "html.parser")
            titles = [
                a.get_text(strip=True)
                for a in soup.select(".result__a, .result__title a")
            ][:num_results]

            return {"results": titles}

        except requests.RequestException as e:
            print(f"❌ Web search error: {e}")
            return {"results": []}
        except Exception as e:
            print(f"❌ Unexpected error in web search: {e}")
            return {"results": []}

