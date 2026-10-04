#!/usr/bin/env python3
"""Dependency-free checks for the public, translated SpeakLog website."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

SITE_ORIGIN = "https://speak.erzhiqian.cc"
LANGUAGES = {"zh-CN": "", "en": "en/", "ja": "ja/"}
TOPICS = ("", "guides/getting-started/", "guides/speaking-practice/", "guides/export/", "privacy/")
PUBLIC_ROUTES = tuple("/" + prefix + topic for prefix in LANGUAGES.values() for topic in TOPICS)
ROOT_FILES = {"404.html", "robots.txt", "sitemap.xml", "site.webmanifest", "_headers", "_redirects"}
ASSET_MEDIA_SUFFIXES = {".png", ".svg", ".jpg", ".jpeg", ".webp", ".avif", ".ico", ".woff", ".woff2", ".ttf", ".mp4", ".webm", ".vtt"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list = field(default_factory=list)

    def all(self, tag=None):
        for child in self.children:
            if isinstance(child, Node):
                if tag is None or child.tag == tag:
                    yield child
                yield from child.all(tag)

    def text(self, exclude=()):
        return "".join(child if isinstance(child, str) else child.text(exclude)
                       for child in self.children
                       if not isinstance(child, Node) or child.tag not in exclude)


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def nodes(self, tag=None):
        return list(self.root.all(tag))

    def metadata(self, key):
        return [node.attrs.get("content", "") for node in self.nodes("meta")
                if node.attrs.get("name") == key or node.attrs.get("property") == key]

    def links(self, rel):
        return [node for node in self.nodes("link") if rel in node.attrs.get("rel", "").split()]


def normalize(text):
    return re.sub(r"\s+", " ", unescape(text)).strip()


def plain_html(text):
    return normalize(Document(text).root.text())


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def has_type(node, expected):
    value = node.get("@type", [])
    return expected in (value if isinstance(value, list) else [value])


def page_route(path, root):
    relative = path.relative_to(root).as_posix()
    return "/" + relative.removesuffix("index.html") if relative.endswith("index.html") else "/" + relative


def route_file(route):
    return route.lstrip("/") + "index.html"


def route_context(route):
    for language, prefix in LANGUAGES.items():
        if prefix and route.startswith("/" + prefix):
            return language, route[len(prefix) + 1:]
    return "zh-CN", route.lstrip("/")


def equivalents(route):
    _, topic = route_context(route)
    result = {language: SITE_ORIGIN + "/" + prefix + topic for language, prefix in LANGUAGES.items()}
    return {**result, "x-default": result["en"]}


def is_public_file(relative):
    """Positive allowlist: docs, credentials, generators and source maps never ship."""
    if any(part.startswith(".") for part in relative.parts):
        return False
    name = relative.as_posix()
    if name in ROOT_FILES or name in {route_file(route) for route in PUBLIC_ROUTES}:
        return True
    if relative.parts[0] == "assets":
        return (name in {"assets/site.css", "assets/site.js", "assets/analytics.js"}
                or relative.suffix.lower() in ASSET_MEDIA_SUFFIXES)
    return False


def validate(root):
    root = Path(root).resolve()
    errors = []
    pages = {}
    schemas = {}

    def require(ok, message):
        if not ok:
            errors.append(message)

    for path in sorted(root.rglob("*.html")):
        route = page_route(path, root)
        try:
            pages[route] = Document(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{route}: cannot parse HTML: {exc}")
    indexed = {route for route, doc in pages.items()
               if not any("noindex" in value.lower() for value in doc.metadata("robots"))}
    require(indexed == set(PUBLIC_ROUTES), f"indexable routes differ: missing={sorted(set(PUBLIC_ROUTES) - indexed)}, extra={sorted(indexed - set(PUBLIC_ROUTES))}")
    require("/404.html" in pages, "404.html is required")
    if "/404.html" in pages:
        require(any("noindex" in value.lower() for value in pages["/404.html"].metadata("robots")), "404.html must be noindex")

    versions = {}
    for route, doc in pages.items():
        canonical = SITE_ORIGIN + route
        ids = [node.attrs["id"] for node in doc.nodes() if node.attrs.get("id")]
        require(len(ids) == len(set(ids)), f"{route}: duplicate HTML ids")
        scripts = [node for node in doc.nodes("script") if node.attrs.get("type") == "application/ld+json"]
        structured = []
        for script in scripts:
            try:
                structured.extend(walk_json(json.loads(script.text())))
            except (ValueError, TypeError) as exc:
                errors.append(f"{route}: invalid JSON-LD: {exc}")
        schemas[route] = structured
        if route in indexed:
            language, _ = route_context(route)
            require([node.attrs.get("lang") for node in doc.nodes("html")] == [language], f"{route}: incorrect html lang")
            require(len(doc.nodes("title")) == 1 and bool(normalize(doc.nodes("title")[0].text())), f"{route}: one nonempty title required")
            descriptions = doc.metadata("description")
            require(len(descriptions) == 1 and bool(normalize(descriptions[0])), f"{route}: one nonempty meta description required")
            require([node.attrs.get("href") for node in doc.links("canonical")] == [canonical], f"{route}: canonical must equal {canonical}")
            alternates = doc.links("alternate")
            alternate_pairs = [(node.attrs.get("hreflang"), node.attrs.get("href")) for node in alternates if node.attrs.get("hreflang")]
            require(len(alternate_pairs) == 4 and dict(alternate_pairs) == equivalents(route), f"{route}: hreflang must reciprocate same-topic zh-CN/en/ja/x-default pages")
            require(doc.metadata("og:url") == [canonical], f"{route}: og:url must match canonical")
            for node in doc.nodes("a"):
                lang = node.attrs.get("hreflang")
                if lang in LANGUAGES:
                    require(urljoin(canonical, node.attrs.get("href", "")) == equivalents(route)[lang], f"{route}: language switch {lang} must link to the equivalent topic")
            require(bool(doc.nodes("h1")), f"{route}: h1 required")

        # Every local reference must remain inside the publishable website and resolve.
        for node in doc.nodes():
            for attribute in ("href", "src", "poster"):
                value = node.attrs.get(attribute)
                if value is None:
                    continue
                parsed = urlsplit(urljoin(canonical, value))
                if parsed.scheme not in {"http", "https"} or parsed.netloc != urlsplit(SITE_ORIGIN).netloc:
                    continue
                local_path = unquote(parsed.path)
                target = root / local_path.lstrip("/")
                if local_path.endswith("/") or target.is_dir():
                    target /= "index.html"
                require(target.resolve().is_relative_to(root), f"{route}: local link escapes website: {value}")
                if not target.resolve().is_relative_to(root):
                    continue
                require(target.is_file(), f"{route}: broken local {attribute}: {value}")
                if target.is_file():
                    require(is_public_file(target.relative_to(root)), f"{route}: reference is excluded from public build: {value}")
                if parsed.fragment and target.suffix == ".html" and target.is_file():
                    target_doc = pages.get(page_route(target, root))
                    fragment = unquote(parsed.fragment)
                    target_ids = {item.attrs.get("id") for item in target_doc.nodes()} if target_doc else set()
                    require(fragment in target_ids, f"{route}: missing fragment #{fragment} in {parsed.path}")

        faqs = []
        for container in doc.nodes():
            if "faq" in container.attrs.get("class", "").split():
                for detail in container.all("details"):
                    summaries = list(detail.all("summary"))
                    if summaries:
                        faqs.append((normalize(summaries[0].text()), normalize(detail.text(exclude=("summary",)))))
        faq_schemas = [node for node in structured if has_type(node, "FAQPage")]
        schema_faqs = []
        for schema in faq_schemas:
            for question in schema.get("mainEntity", []):
                answer = question.get("acceptedAnswer", {})
                schema_faqs.append((plain_html(question.get("name", "")), plain_html(answer.get("text", ""))))
        require(Counter(faqs) == Counter(schema_faqs), f"{route}: FAQ schema must match every visible FAQ question and answer")
        og_images = set(doc.metadata("og:image"))
        for schema in structured:
            if "screenshot" in schema:
                screenshots = schema["screenshot"] if isinstance(schema["screenshot"], list) else [schema["screenshot"]]
                for screenshot in screenshots:
                    url = screenshot.get("url", screenshot.get("contentUrl", "")) if isinstance(screenshot, dict) else screenshot
                    require(url not in og_images and not re.search(r"/og(?:[-.]|$)", str(url)), f"{route}: social OG artwork must not be labeled an app screenshot")
        for node in doc.nodes("a"):
            href = node.attrs.get("href", "")
            parsed = urlsplit(href)
            if parsed.netloc == "github.com" and parsed.path.startswith("/erzhiqianyi/SpeakLog-releases/releases"):
                expected = "package_download_click" if "/download/" in parsed.path and parsed.path.endswith(".pkg") else "release_page_click"
                require(node.attrs.get("data-track") == expected, f"{route}: {href} must track {expected}")
            require(node.attrs.get("data-track") != "download_click", f"{route}: ambiguous download_click event must be replaced")
        if route in {"/", "/en/", "/ja/"}:
            apps = [node for node in structured if has_type(node, "SoftwareApplication")]
            require(len(apps) == 1, f"{route}: one SoftwareApplication schema required")
            if apps:
                version = apps[0].get("softwareVersion", "")
                require(bool(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][\w.-]+)?", version)), f"{route}: valid softwareVersion required")
                versions[route] = version
    require(len(set(versions.values())) <= 1, f"homepage softwareVersion values disagree: {versions}")
    reference_version = versions.get("/")
    if reference_version:
        for route, doc in pages.items():
            version_nodes = [node for node in doc.nodes() if "data-version" in node.attrs or "data-software-version" in node.attrs]
            if route in {"/", "/en/", "/ja/"} or "/guides/" in route:
                require(bool(version_nodes), f"{route}: visible data-version marker required")
            for node in version_nodes:
                visible_version = node.attrs.get("data-software-version", node.attrs.get("data-version"))
                require(visible_version.lstrip("v") == reference_version, f"{route}: visible version disagrees with softwareVersion")
                require(normalize(node.text()).lstrip("v") == reference_version, f"{route}: displayed version text disagrees with softwareVersion")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
    try:
        sitemap = ET.parse(root / "sitemap.xml").getroot()
        entries = sitemap.findall("s:url", ns)
        locations = [entry.findtext("s:loc", namespaces=ns) for entry in entries]
        require(len(locations) == len(set(locations)), "sitemap contains duplicate URLs")
        require(set(locations) == {SITE_ORIGIN + route for route in indexed}, "sitemap coverage must equal all indexable canonical pages")
        for entry in entries:
            location = entry.findtext("s:loc", default="", namespaces=ns)
            alternates = [(link.get("hreflang"), link.get("href")) for link in entry.findall("x:link", ns) if link.get("rel") == "alternate"]
            require(len(alternates) == 4 and dict(alternates) == equivalents(urlsplit(location).path), f"sitemap {location}: same-topic hreflang alternates required")
            try:
                date.fromisoformat(entry.findtext("s:lastmod", default="", namespaces=ns))
            except ValueError:
                errors.append(f"sitemap {location}: valid lastmod date required")
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap cannot be read: {exc}")
    try:
        robots = (root / "robots.txt").read_text(encoding="utf-8")
        require(f"Sitemap: {SITE_ORIGIN}/sitemap.xml" in robots, "robots.txt must advertise the canonical sitemap")
        require(not re.search(r"^Disallow:\s*/\s*$", robots, re.M | re.I), "robots.txt must not block the entire public site")
    except OSError as exc:
        errors.append(f"robots.txt cannot be read: {exc}")
    try:
        manifest = json.loads((root / "site.webmanifest").read_text(encoding="utf-8"))
        for icon in manifest.get("icons", []):
            require((root / icon["src"].lstrip("/")).is_file(), f"manifest icon missing: {icon['src']}")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f"manifest invalid: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1] / "website")
    args = parser.parse_args()
    errors = validate(args.site_dir)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"Website validation failed: {len(errors)} error(s)")
        return 1
    print(f"Website validation passed: {len(PUBLIC_ROUTES)} translated canonical pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
