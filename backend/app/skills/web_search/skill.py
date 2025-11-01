"""
Web Search Skill
----------------
Search the web using DuckDuckGo.
"""

import requests
from bs4 import BeautifulSoup
from backend.app.skills.base import BaseSkill
from typing import List, Dict, Any


class WebSearchSkill(BaseSkill):
    """Simple web search using DuckDuckGo."""
    
    def execute(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title and snippet
        """
        # Validate parameters
        self.validate_params({"query": query, "num_results": num_results})
        
        try:
            # Perform search
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse results
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            for result in soup.select(".result")[:num_results]:
                title_elem = result.select_one(".result__title")
                snippet_elem = result.select_one(".result__snippet")
                link_elem = result.select_one(".result__url")
                
                if title_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                        "url": link_elem.get_text(strip=True) if link_elem else ""
                    })
            
            return results
            
        except requests.RequestException as e:
            print(f"❌ Web search error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error in web search: {e}")
            return []

