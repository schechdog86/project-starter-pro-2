"""
Data Formatter
--------------
Format scraped research data into various output formats.

Supports:
- Normalization of scraped data
- Markdown generation
- PDF generation (via markdown-pdf or weasyprint)
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class DataFormatter:
    """Format research data into various output formats."""
    
    def __init__(self, output_dir: str = "data/research_output"):
        """
        Initialize formatter.
        
        Args:
            output_dir: Base directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def normalize(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize scraped data into a consistent structure.
        
        Args:
            data: List of scraped results from different sources
            
        Returns:
            Normalized data structure
        """
        normalized = {
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "content": [],
            "metadata": {
                "total_sources": len(data),
                "successful_scrapes": 0,
                "failed_scrapes": 0
            }
        }
        
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                # Check if scrape was successful
                if "error" in item:
                    normalized["metadata"]["failed_scrapes"] += 1
                    normalized["sources"].append({
                        "index": idx,
                        "status": "failed",
                        "error": item.get("error", "Unknown error")
                    })
                else:
                    normalized["metadata"]["successful_scrapes"] += 1
                    
                    # Extract content
                    content_item = {
                        "index": idx,
                        "status": "success",
                        "data": item
                    }
                    
                    # Try to extract common fields
                    if "title" in item:
                        content_item["title"] = item["title"]
                    if "text" in item:
                        content_item["text"] = item["text"]
                    if "url" in item:
                        content_item["url"] = item["url"]
                    
                    normalized["content"].append(content_item)
                    normalized["sources"].append({
                        "index": idx,
                        "status": "success",
                        "has_title": "title" in item,
                        "has_text": "text" in item
                    })
        
        return normalized
    
    def to_markdown(self, topic: str, normalized_data: Dict[str, Any]) -> str:
        """
        Convert normalized data to Markdown format.
        
        Args:
            topic: Research topic
            normalized_data: Normalized data structure
            
        Returns:
            Path to generated Markdown file
        """
        # Generate filename
        safe_topic = topic.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # Build Markdown content
        md_lines = [
            f"# Research Report: {topic}",
            "",
            f"**Generated:** {normalized_data.get('timestamp', 'N/A')}",
            "",
            "## Summary",
            "",
            f"- **Total Sources:** {normalized_data['metadata']['total_sources']}",
            f"- **Successful Scrapes:** {normalized_data['metadata']['successful_scrapes']}",
            f"- **Failed Scrapes:** {normalized_data['metadata']['failed_scrapes']}",
            "",
            "---",
            ""
        ]
        
        # Add content sections
        if normalized_data.get("content"):
            md_lines.append("## Research Findings")
            md_lines.append("")
            
            for item in normalized_data["content"]:
                md_lines.append(f"### Source {item['index'] + 1}")
                md_lines.append("")
                
                if "title" in item:
                    md_lines.append(f"**Title:** {item['title']}")
                    md_lines.append("")
                
                if "url" in item:
                    md_lines.append(f"**URL:** {item['url']}")
                    md_lines.append("")
                
                if "text" in item:
                    md_lines.append("**Content:**")
                    md_lines.append("")
                    md_lines.append(item["text"])
                    md_lines.append("")
                elif "data" in item:
                    md_lines.append("**Data:**")
                    md_lines.append("")
                    md_lines.append("```json")
                    md_lines.append(json.dumps(item["data"], indent=2))
                    md_lines.append("```")
                    md_lines.append("")
                
                md_lines.append("---")
                md_lines.append("")
        
        # Add failed sources section
        failed_sources = [s for s in normalized_data.get("sources", []) if s.get("status") == "failed"]
        if failed_sources:
            md_lines.append("## Failed Sources")
            md_lines.append("")
            
            for source in failed_sources:
                md_lines.append(f"- **Source {source['index'] + 1}:** {source.get('error', 'Unknown error')}")
            
            md_lines.append("")
        
        # Write to file
        filepath.write_text("\n".join(md_lines))
        
        print(f"✅ Markdown generated: {filepath}")
        return str(filepath)
    
    def to_pdf(self, topic: str, normalized_data: Dict[str, Any]) -> str:
        """
        Convert normalized data to PDF format.
        
        Args:
            topic: Research topic
            normalized_data: Normalized data structure
            
        Returns:
            Path to generated PDF file
        """
        # First generate Markdown
        md_path = self.to_markdown(topic, normalized_data)
        
        # Generate PDF filename
        pdf_path = Path(md_path).with_suffix(".pdf")
        
        try:
            # Try using markdown-pdf (requires md-to-pdf npm package)
            import subprocess
            result = subprocess.run(
                ["md-to-pdf", md_path, "-o", str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and pdf_path.exists():
                print(f"✅ PDF generated: {pdf_path}")
                return str(pdf_path)
            else:
                print(f"⚠️  md-to-pdf failed: {result.stderr}")
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"⚠️  md-to-pdf not available: {e}")
        
        try:
            # Try using weasyprint (Python library)
            from weasyprint import HTML
            from markdown import markdown
            
            # Convert Markdown to HTML
            md_content = Path(md_path).read_text()
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
                    h3 {{ color: #888; }}
                    code {{ background: #f4f4f4; padding: 2px 5px; }}
                    pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                {markdown(md_content, extensions=['fenced_code', 'tables'])}
            </body>
            </html>
            """
            
            HTML(string=html_content).write_pdf(str(pdf_path))
            print(f"✅ PDF generated (weasyprint): {pdf_path}")
            return str(pdf_path)
            
        except ImportError:
            print("⚠️  weasyprint not available (optional)")
        except Exception as e:
            print(f"⚠️  PDF generation failed: {e}")
        
        # Fallback: return Markdown path
        print(f"⚠️  PDF generation not available, returning Markdown: {md_path}")
        return md_path
    
    def to_json(self, topic: str, normalized_data: Dict[str, Any]) -> str:
        """
        Save normalized data as JSON.
        
        Args:
            topic: Research topic
            normalized_data: Normalized data structure
            
        Returns:
            Path to generated JSON file
        """
        # Generate filename
        safe_topic = topic.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_topic}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Write to file
        filepath.write_text(json.dumps(normalized_data, indent=2))
        
        print(f"✅ JSON generated: {filepath}")
        return str(filepath)

