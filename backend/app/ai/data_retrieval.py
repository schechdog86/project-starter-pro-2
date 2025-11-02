"""
Data Retrieval System
---------------------
Unified interface for research data scraping and crawling.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class DataRetrieval:
    """Unified interface for research data scraping and crawling."""

    def __init__(self, base_path="data/research_cache"):
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)

        # Try to import optional dependencies
        self.scrapegraph = None
        self.firecrawl = None

        # Import settings
        try:
            from backend.app.core.config import settings
            self.settings = settings
        except ImportError:
            self.settings = None

        # Initialize ScrapeGraphAI
        try:
            from scrapegraphai.graphs import SmartScraperGraph

            # Check for API key
            api_key = ""
            if self.settings and hasattr(self.settings, 'SCRAPEGRAPH_API_KEY'):
                api_key = self.settings.SCRAPEGRAPH_API_KEY

            if api_key:
                self.scrapegraph = SmartScraperGraph
                print(f"✅ ScrapeGraphAI available (API key: {api_key[:10]}...)")
            else:
                self.scrapegraph = SmartScraperGraph  # May work without key for some features
                print("⚠️  ScrapeGraphAI available but no API key set")
        except ImportError as e:
            print(f"❌ ScrapeGraphAI import failed: {e}")
            self.scrapegraph = None
        except Exception as e:
            print(f"❌ ScrapeGraphAI initialization error: {e}")
            self.scrapegraph = None

        # Initialize Firecrawl
        try:
            from firecrawl import Firecrawl

            # Get API key from settings
            api_key = ""
            if self.settings and hasattr(self.settings, 'FIRECRAWL_API_KEY'):
                api_key = self.settings.FIRECRAWL_API_KEY

            if api_key:
                self.firecrawl = Firecrawl(api_key=api_key)
                print(f"✅ Firecrawl available (API key: {api_key[:10]}...)")
            else:
                self.firecrawl = None
                print("⚠️  Firecrawl API key not set (optional)")
        except (ImportError, ValueError) as e:
            self.firecrawl = None
            print(f"⚠️  Firecrawl not available (optional): {e}")

    def scrape(self, query: str, url: str, out_name: str = "scrape.json") -> Dict[str, Any]:
        """
        Scrape a URL with a specific query using ScrapeGraphAI.
        
        Args:
            query: What to extract from the page
            url: URL to scrape
            out_name: Output filename
            
        Returns:
            Scraped data
        """
        if not self.scrapegraph:
            print("❌ ScrapeGraphAI not available")
            return {"error": "ScrapeGraphAI not installed"}
        
        try:
            graph = self.scrapegraph(
                prompt=query,
                source=url,
                graph_output="json"
            )
            result = graph.run()
            
            # Save to cache
            out = self.base / out_name
            out.write_text(json.dumps(result, indent=2))
            
            print(f"✅ Scraped {url} → {out_name}")
            return result
            
        except Exception as e:
            print(f"❌ Scrape error: {e}")
            return {"error": str(e)}

    def crawl(self, domain: str, depth: int = 1, out_name: str = "crawl.json") -> Dict[str, Any]:
        """
        Crawl a domain using Firecrawl.
        
        Args:
            domain: Domain to crawl
            depth: Crawl depth
            out_name: Output filename
            
        Returns:
            Crawled data
        """
        if not self.firecrawl:
            print("❌ Firecrawl not available")
            return {"error": "Firecrawl not installed"}
        
        try:
            data = self.firecrawl.crawl(domain, depth=depth)
            
            # Save to cache
            out = self.base / out_name
            out.write_text(json.dumps(data, indent=2))
            
            print(f"✅ Crawled {domain} → {out_name}")
            return data
            
        except Exception as e:
            print(f"❌ Crawl error: {e}")
            return {"error": str(e)}

    def search_and_cache(self, topic: str, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Search multiple URLs and cache results.
        
        Args:
            topic: Search topic
            urls: List of URLs to scrape
            
        Returns:
            List of scraped results
        """
        results = []
        for i, u in enumerate(urls):
            res = self.scrape(topic, u, f"{topic}_{i}.json")
            results.append(res)
        return results

