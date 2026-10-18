"""Extract local destinations used by this repository's Markdown/HTML links."""

import re
from urllib.parse import unquote, urlsplit


def local_targets(text: str) -> list[str]:
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")
    html_link = re.compile(r'href=["\']([^"\'#]+)(?:#[^"\']*)?["\']')
    targets = []
    for pattern in (markdown_link, html_link):
        for match in pattern.finditer(text):
            target = match.group(1).strip().removeprefix("<").removesuffix(">")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            targets.append(unquote(parsed.path))
    return targets
