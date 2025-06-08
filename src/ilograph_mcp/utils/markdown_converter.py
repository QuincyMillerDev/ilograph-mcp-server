"""
HTML to Markdown conversion utility for Ilograph documentation.

This module provides functionality to convert HTML documentation pages from
Ilograph into clean, LLM-optimized markdown format with proper formatting,
link resolution, and content sanitization.
"""

import logging
import re
from typing import List, Optional, Tuple, Union
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
            for element in soup.find_all(class_=class_name):  # type: ignore
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
            if content and isinstance(content, Tag):
                logger.debug(f"Found main content using selector: {selector}")
                return content

        # Fallback: look for the body content
        body = soup.find("body")
        if body and isinstance(body, Tag):
            logger.debug("Using body as main content")
            return body

        logger.warning("Could not find main content area")
        return None

    def resolve_links(self, soup: Union[BeautifulSoup, Tag]) -> None:
        """
        Convert relative links to absolute URLs.

        Args:
            soup: BeautifulSoup object to process
        """
        # Process all links
        for link in soup.find_all("a", href=True):
            if not isinstance(link, Tag):
                continue
            href = link.get("href")
            if not isinstance(href, str):
                continue
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
            if not isinstance(img, Tag):
                continue
            src = img.get("src")
            if not isinstance(src, str):
                continue
            if not src.startswith(("http://", "https://", "data:")):
                absolute_url = urljoin(self.base_url, src)
                img["src"] = absolute_url
                logger.debug(f"Converted relative image: {src} -> {absolute_url}")

    def extract_code_blocks(self, soup: Union[BeautifulSoup, Tag]) -> List[Tuple[str, str]]:
        """
        Extract code blocks with their language information.

        Args:
            soup: BeautifulSoup object to search

        Returns:
            List of (language, code) tuples
        """
        code_blocks = []

        # Look for pre > code combinations
        pre_tags = soup.find_all("pre")
        for pre in pre_tags:
            if not isinstance(pre, Tag):
                continue

            code = pre.find("code")
            if code and isinstance(code, Tag):
                # Try to determine language from class
                language = "yaml"  # Default for Ilograph
                class_attr = code.get("class")
                if class_attr and isinstance(class_attr, list):
                    for class_name in class_attr:
                        if isinstance(class_name, str):
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

    def convert_headers(self, soup: Union[BeautifulSoup, Tag]) -> None:
        """
        Ensure proper header hierarchy and formatting.

        Args:
            soup: BeautifulSoup object to process
        """
        # Convert headers to maintain hierarchy
        for level in range(1, 7):  # h1 to h6
            headers = soup.find_all(f"h{level}")
            for header in headers:
                if isinstance(header, Tag):
                    # Clean header text
                    header_text = header.get_text().strip()
                    if header_text:
                        # Create markdown header
                        markdown_header = "#" * level + " " + header_text
                        header.string = markdown_header
                        header.name = "p"  # Convert to paragraph for markdown processing

    def process_lists(self, soup: Union[BeautifulSoup, Tag]) -> None:
        """
        Process and format lists for markdown conversion.

        Args:
            soup: BeautifulSoup object to process
        """
        # Process unordered lists
        unordered_lists = soup.find_all("ul")
        for ul in unordered_lists:
            if isinstance(ul, Tag):
                list_items = ul.find_all("li", recursive=False)
                for li in list_items:
                    if isinstance(li, Tag):
                        li_text = li.get_text().strip()
                        if li_text:
                            li.string = f"- {li_text}"
                            li.name = "p"

        # Process ordered lists
        ordered_lists = soup.find_all("ol")
        for ol in ordered_lists:
            if isinstance(ol, Tag):
                list_items = ol.find_all("li", recursive=False)
                for i, li in enumerate(list_items, 1):
                    if isinstance(li, Tag):
                        li_text = li.get_text().strip()
                        if li_text:
                            li.string = f"{i}. {li_text}"
                            li.name = "p"

    def format_tables(self, soup: Union[BeautifulSoup, Tag]) -> None:
        """
        Convert HTML tables to markdown format.

        Args:
            soup: BeautifulSoup object to process
        """
        tables = soup.find_all("table")
        for table in tables:
            if not isinstance(table, Tag):
                continue

            markdown_table = []

            # Process headers
            thead = table.find("thead")
            if thead and isinstance(thead, Tag):
                header_row = thead.find("tr")
                if header_row and isinstance(header_row, Tag):
                    header_cells = header_row.find_all(["th", "td"])
                    headers = [th.get_text().strip() for th in header_cells if isinstance(th, Tag)]
                    if headers:
                        # Create markdown header
                        markdown_table.append("| " + " | ".join(headers) + " |")
                        markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

            # Process body rows
            tbody = table.find("tbody") or table
            if isinstance(tbody, Tag):
                table_rows = tbody.find_all("tr")
                for row in table_rows:
                    if isinstance(row, Tag):
                        row_cells = row.find_all(["td", "th"])
                        cells = [td.get_text().strip() for td in row_cells if isinstance(td, Tag)]
                        if cells:
                            markdown_table.append("| " + " | ".join(cells) + " |")

            if markdown_table:
                # Replace table with markdown
                table_text = "\n".join(markdown_table)
                # Get a soup object that can create new tags
                root_soup: Optional[BeautifulSoup] = None
                if isinstance(soup, BeautifulSoup):
                    root_soup = soup
                else:
                    # Safely traverse up the parent hierarchy to find BeautifulSoup
                    current: Union[Tag, BeautifulSoup, None] = soup

                    while current is not None:
                        if isinstance(current, BeautifulSoup):
                            root_soup = current
                            break
                        current = current.find_parent() if hasattr(current, "find_parent") else None  # type: ignore

                if root_soup is not None and hasattr(root_soup, "new_tag"):
                    new_tag_method = getattr(root_soup, "new_tag")
                    if callable(new_tag_method):
                        new_tag = new_tag_method("div")
                        if hasattr(new_tag, "string"):
                            new_tag.string = "\n" + table_text + "\n"
                        table.replace_with(new_tag)
                    else:
                        # Fallback: create text node
                        from bs4 import NavigableString

                        text_node = NavigableString("\n" + table_text + "\n")
                        table.replace_with(text_node)
                else:
                    # Fallback: create text node
                    from bs4 import NavigableString

                    text_node = NavigableString("\n" + table_text + "\n")
                    table.replace_with(text_node)

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

    def convert_html_to_markdown(self, html: str, source_url: Optional[str] = None) -> str:
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
                # Use body as fallback, or create a wrapper
                body = soup.find("body")
                if isinstance(body, Tag):
                    main_content = body
                else:
                    # Create a temporary wrapper tag for processing
                    main_content = soup.new_tag("div")
                    # Move all body content into our wrapper
                    for child in list(soup.children):
                        if hasattr(child, "extract"):
                            child.extract()
                            main_content.append(child)

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
