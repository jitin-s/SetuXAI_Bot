import requests
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup

class WebsiteScanner:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SetuXBotCrawler/1.0"
        }

    def clean_text(self, text: str) -> str:
        # Remove extra whitespace and line breaks
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Crawls a target website URL, extracts page title, headings, main text, and links.
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            res = requests.get(url, headers=self.headers, timeout=self.timeout)
            if res.status_code != 200:
                return {
                    "success": False,
                    "url": url,
                    "error": f"HTTP {res.status_code} response from website"
                }

            soup = BeautifulSoup(res.text, "html.parser")

            # Remove scripts, styles, and non-content elements
            for element in soup(["script", "style", "nav", "footer", "svg", "noscript"]):
                element.decompose()

            # Extract Title
            title = soup.title.string if soup.title else url

            # Extract Headings and Paragraphs
            content_blocks = []
            for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'td', 'th']):
                txt = self.clean_text(elem.get_text())
                if len(txt) > 20: # Filter short noise
                    if elem.name.startswith('h'):
                        content_blocks.append(f"\n### {txt}\n")
                    else:
                        content_blocks.append(txt)

            cleaned_markdown = "\n".join(content_blocks[:100]) # Cap to first 100 blocks

            return {
                "success": True,
                "url": url,
                "title": title.strip(),
                "content": cleaned_markdown,
                "character_count": len(cleaned_markdown)
            }

        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }

    def scan_page_payload(self, url: str, title: str, raw_text: str) -> Dict[str, Any]:
        """
        Processes live DOM text sent directly from an embedded JS widget on a host website.
        """
        cleaned = self.clean_text(raw_text)
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": cleaned[:8000],
            "character_count": len(cleaned)
        }
