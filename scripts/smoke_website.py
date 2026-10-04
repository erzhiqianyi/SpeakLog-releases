#!/usr/bin/env python3
"""Read-only post-deploy check: compare public bytes and require a real HTTP 404."""
import argparse
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import uuid

sys.dont_write_bytecode = True
from validate_website import is_public_file, validate


def fetch(url, timeout):
    request = Request(url, headers={"User-Agent": "SpeakLog-release-smoke/1.0", "Cache-Control": "no-cache"})
    try:
        response = urlopen(request, timeout=timeout)
    except HTTPError as error:
        response = error
    with response:
        return response.status, response.headers, response.read(20 * 1024 * 1024 + 1)


def smoke(base_url, site_dir, timeout=15):
    parsed = urlsplit(base_url)
    if (parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.username or parsed.password
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
        raise ValueError("Use an explicit origin URL, without credentials, path, query or fragment")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Remote deployment checks require HTTPS")
    errors = validate(site_dir)
    if errors:
        return ["Local expected website must pass validation before comparing deployment", *errors]
    base_url = base_url.rstrip("/")
    for path in sorted(site_dir.rglob("*")):
        relative = path.relative_to(site_dir)
        if not path.is_file() or not is_public_file(relative) or relative.as_posix() in {"_headers", "_redirects"}:
            continue
        route = "/" + relative.as_posix()
        if route.endswith("index.html"):
            route = route.removesuffix("index.html")
        try:
            status, headers, body = fetch(base_url + route, timeout)
            if status not in ({200, 404} if route == "/404.html" else {200}):
                errors.append(f"{route}: expected HTTP 200, got {status}")
            if body != path.read_bytes():
                errors.append(f"{route}: deployed bytes differ from this checkout (wrong release or stale cache)")
            expected_type = {".html": "text/html", ".css": "text/css", ".js": "javascript", ".png": "image/png"}.get(path.suffix)
            if expected_type and expected_type not in headers.get("Content-Type", ""):
                errors.append(f"{route}: unexpected Content-Type {headers.get('Content-Type')}")
        except (OSError, URLError) as exc:
            errors.append(f"{route}: request failed: {exc}")
    for prefix in ("/", "/en/guides/", "/ja/guides/"):
        route = prefix + "speaklog-smoke-missing-" + uuid.uuid4().hex + "/"
        try:
            status, _, _ = fetch(base_url + route, timeout)
            if status != 404:
                errors.append(f"{route}: unknown route must return HTTP 404, got {status}")
        except (OSError, URLError) as exc:
            errors.append(f"{route}: request failed: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="The deployment URL or production origin to check; never publishes")
    parser.add_argument("--site-dir", type=Path, default=Path(__file__).resolve().parents[1] / "website")
    parser.add_argument("--timeout", type=float, default=15)
    args = parser.parse_args()
    try:
        errors = smoke(args.base_url, args.site_dir.resolve(), args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print("Post-deploy smoke passed: public file bytes, content types and real 404 responses match expectations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
