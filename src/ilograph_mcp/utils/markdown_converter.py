"""
HTML to Markdown conversion utility for Ilograph documentation.

This module provides functionality to convert HTML documentation pages from
Ilograph into clean, LLM-optimized markdown format with proper formatting,
link resolution, and content sanitization.
"""

import logging
import re
from typing import Optional, List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from bs4.element import Comment

logger = logging.getLogger(__name__)


class IlographMarkdownConverter:
    """Converts Ilograph HTML documentation to clean markdown format."""

    def __init__(self, base_url: str = "https://www.ilograph.com/"):
        """
        Initialize the markdown converter.

        Args:
            base_url: Base URL for resolving relative links
        """
        self.base_url = base_url

        # Elements to remove completely
        self.remove_selectors = [
            "nav",
            "header",
            "footer",
            ".navigation",
            "#navigation",
            ".sidebar",
            "#sidebar",
            ".menu",
            ".breadcrumb",
            ".search-container",
            ".cookie-notice",
            ".banner",
            ".ad",
            ".advertisement",
            "script",
            "style",
            "noscript",
        ]

        # Content selectors to look for (in order of preference)
        self.content_selectors = [
            "main",
            ".content",
            "#content",
            ".main-content",
            "#main-content",
            ".documentation",
            ".docs-content",
            "article",
            ".post-content",
        ]

    def remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """
        Remove navigation, ads, and other unwanted elements.

        Args:
            soup: BeautifulSoup object to clean
        """
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove unwanted elements
        for selector in self.remove_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Remove elements with common unwanted classes
        unwanted_classes = ["skip-link", "screen-reader-text", "sr-only", "visually-hidden"]
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=class_name):
                element.decompose()

    def find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """
        Find the main content area of the page.

        Args:
            soup: BeautifulSoup object to search

        Returns:
            Tag containing main content, or None if not found
        """
        # Try content selectors in order
        for selector in self.content_selectors:
            content = soup.select_one(selector)
            if content:
                logger.debug(f"Found main content using selector: {selector}")
                return content

        # Fallback: look for the body content
        body = soup.find("body")
        if body:
            logger.debug("Using body as main content")
            return body

        logger.warning("Could not find main content area")
        return None

    def resolve_links(self, soup: BeautifulSoup) -> None:
        """
        Convert relative links to absolute URLs.

        Args:
            soup: BeautifulSoup object to process
        """
        # Process all links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.startswith("#"):
                # Keep anchor links as-is
                continue
            elif href.startswith(("http://", "https://")):
                # Already absolute
                continue
            else:
                # Convert relative to absolute
                absolute_url = urljoin(self.base_url, href)
                link["href"] = absolute_url
                logger.debug(f"Converted relative link: {href} -> {absolute_url}")

        # Process all images
        for img in soup.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://", "data:")):
                absolute_url = urljoin(self.base_url, src)
                img["src"] = absolute_url
                logger.debug(f"Converted relative image: {src} -> {absolute_url}")

    def extract_code_blocks(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Extract code blocks with their language information.

        Args:
            soup: BeautifulSoup object to search

        Returns:
            List of (language, code) tuples
        """
        code_blocks = []

        # Look for pre > code combinations
        for pre in soup.find_all("pre"):
            code = pre.find("code")
            if code:
                # Try to determine language from class
                language = "yaml"  # Default for Ilograph
                if code.get("class"):
                    for class_name in code["class"]:
                        if class_name.startswith("language-"):
                            language = class_name[9:]  # Remove "language-"
                            break
                        elif class_name in [
                            "yaml",
                            "json",
                            "javascript",
                            "python",
                            "bash",
                            "shell",
                        ]:
                            language = class_name
                            break

                code_text = code.get_text().strip()
                if code_text:
                    code_blocks.append((language, code_text))

        return code_blocks

    def convert_headers(self, soup: BeautifulSoup) -> None:
        """
        Ensure proper header hierarchy and formatting.

        Args:
            soup: BeautifulSoup object to process
        """
        # Convert headers to maintain hierarchy
        for level in range(1, 7):  # h1 to h6
            for header in soup.find_all(f"h{level}"):
                # Clean header text
                header_text = header.get_text().strip()
                if header_text:
                    # Create markdown header
                    markdown_header = "#" * level + " " + header_text
                    header.string = markdown_header
                    header.name = "p"  # Convert to paragraph for markdown processing

    def process_lists(self, soup: BeautifulSoup) -> None:
        """
        Process and format lists for markdown conversion.

        Args:
            soup: BeautifulSoup object to process
        """
        # Process unordered lists
        for ul in soup.find_all("ul"):
            for li in ul.find_all("li", recursive=False):
                li_text = li.get_text().strip()
                if li_text:
                    li.string = f"- {li_text}"
                    li.name = "p"

        # Process ordered lists
        for ol in soup.find_all("ol"):
            for i, li in enumerate(ol.find_all("li", recursive=False), 1):
                li_text = li.get_text().strip()
                if li_text:
                    li.string = f"{i}. {li_text}"
                    li.name = "p"

    def format_tables(self, soup: BeautifulSoup) -> None:
        """
        Convert HTML tables to markdown format.

        Args:
            soup: BeautifulSoup object to process
        """
        for table in soup.find_all("table"):
            markdown_table = []

            # Process headers
            thead = table.find("thead")
            if thead:
                header_row = thead.find("tr")
                if header_row:
                    headers = [th.get_text().strip() for th in header_row.find_all(["th", "td"])]
                    if headers:
                        # Create markdown header
                        markdown_table.append("| " + " | ".join(headers) + " |")
                        markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

            # Process body rows
            tbody = table.find("tbody") or table
            for row in tbody.find_all("tr"):
                cells = [td.get_text().strip() for td in row.find_all(["td", "th"])]
                if cells:
                    markdown_table.append("| " + " | ".join(cells) + " |")

            if markdown_table:
                # Replace table with markdown
                table_text = "\n".join(markdown_table)
                new_tag = soup.new_tag("div")
                new_tag.string = "\n" + table_text + "\n"
                table.replace_with(new_tag)

    def clean_and_format_text(self, text: str) -> str:
        """
        Clean and format extracted text for LLM consumption.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned and formatted text
        """
        # Remove excessive whitespace
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)  # Max 2 consecutive newlines
        text = re.sub(r"[ \t]+", " ", text)  # Normalize spaces and tabs
        text = re.sub(r"\n[ \t]+", "\n", text)  # Remove leading whitespace on lines

        # Clean up common formatting issues
        text = text.replace("\u00a0", " ")  # Replace non-breaking spaces
        text = text.replace("\u2019", "'")  # Replace fancy apostrophes
        text = text.replace("\u201c", '"').replace("\u201d", '"')  # Replace fancy quotes

        return text.strip()

    def convert_html_to_markdown(self, html: str, source_url: str = None) -> str:
        """
        Convert HTML content to clean markdown format.

        Args:
            html: HTML content to convert
            source_url: Source URL for link resolution

        Returns:
            Clean markdown content optimized for LLM consumption
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, "lxml")

            # Update base URL if source URL provided
            if source_url:
                self.base_url = source_url

            # Remove unwanted elements
            self.remove_unwanted_elements(soup)

            # Find main content
            main_content = self.find_main_content(soup)
            if main_content is None:
                logger.warning("No main content found, using entire document")
                main_content = soup

            # Resolve relative links
            self.resolve_links(main_content)

            # Process content structure
            self.convert_headers(main_content)
            self.process_lists(main_content)
            self.format_tables(main_content)

            # Extract and preserve code blocks
            code_blocks = self.extract_code_blocks(main_content)

            # Get clean text
            content_text = main_content.get_text()

            # Clean and format
            markdown_content = self.clean_and_format_text(content_text)

            # Add code blocks back if they were found
            if code_blocks:
                markdown_content += "\n\n## Code Examples\n\n"
                for language, code in code_blocks:
                    markdown_content += f"```{language}\n{code}\n```\n\n"

            logger.info(
                f"Successfully converted HTML to markdown ({len(markdown_content)} characters)"
            )
            return markdown_content

        except Exception as e:
            logger.error(f"Error converting HTML to markdown: {e}")
            # Return a safe fallback
            try:
                soup = BeautifulSoup(html, "lxml")
                return self.clean_and_format_text(soup.get_text())
            except:
                return "Error: Unable to process HTML content"


# Global converter instance
_converter: Optional[IlographMarkdownConverter] = None


def get_markdown_converter() -> IlographMarkdownConverter:
    """Get the global markdown converter instance."""
    global _converter
    if _converter is None:
        _converter = IlographMarkdownConverter()
    return _converter
