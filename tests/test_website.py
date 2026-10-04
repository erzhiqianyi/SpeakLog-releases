"""Regression checks use Python's standard library only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
from build_website import build
from smoke_website import smoke
from validate_website import Document, PUBLIC_ROUTES, equivalents, is_public_file, normalize, validate


class ContentTests(unittest.TestCase):
    def test_public_content_contract(self):
        self.assertEqual(validate(ROOT / "website"), [])

    def test_equivalents_preserve_each_topic(self):
        for route in PUBLIC_ROUTES:
            urls = equivalents(route)
            self.assertEqual(len(urls), 4)
            self.assertEqual(urls['x-default'], urls['en'])
            for translated in urls.values():
                self.assertEqual(equivalents(translated.removeprefix('https://speak.erzhiqian.cc')), urls)

    def test_parser_preserves_nested_faq_text(self):
        doc = Document('<div class="faq"><details><summary>A &amp; B?</summary><p>Use <strong>both</strong>.</p></details></div>')
        self.assertEqual(normalize(doc.nodes('details')[0].text(exclude=('summary',))), 'Use both.')

    def test_detects_bad_canonical(self):
        self.assert_mutation('href="https://speak.erzhiqian.cc/"', 'href="https://speak.erzhiqian.cc/wrong/"', 'canonical must equal')

    def test_detects_broken_fragment(self):
        self.assert_mutation('href="#main"', 'href="#missing-regression-target"', 'missing fragment')

    def test_detects_ambiguous_download_analytics(self):
        self.assert_mutation('data-track="package_download_click"', 'data-track="download_click"', 'ambiguous download_click')

    def test_detects_faq_schema_drift(self):
        self.assert_mutation('"@type": "FAQPage"', '"@type": "WebPage"', 'FAQ schema must match')

    def test_detects_social_artwork_as_screenshot(self):
        self.assert_mutation('"@type": "SoftwareApplication",', '"@type": "SoftwareApplication", "screenshot": "https://speak.erzhiqian.cc/assets/og.png",', 'must not be labeled an app screenshot')

    def test_detects_guide_version_drift(self):
        filename = 'en/guides/getting-started/index.html'
        version = self.visible_version(filename)
        self.assert_mutation(f'data-version="{version}"', f'data-version="{version}-regression"', 'visible version disagrees', filename)

    def test_detects_guide_displayed_version_drift(self):
        filename = 'ja/guides/export/index.html'
        version = self.visible_version(filename)
        self.assert_mutation(f'data-version="{version}">{version}</span>', f'data-version="{version}">{version}-regression</span>', 'displayed version text disagrees', filename)

    def test_detects_wrong_topic_hreflang(self):
        self.assert_mutation('hreflang="en" href="https://speak.erzhiqian.cc/en/guides/export/"', 'hreflang="en" href="https://speak.erzhiqian.cc/en/"', 'hreflang must reciprocate', 'guides/export/index.html')

    def test_detects_missing_sitemap_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / 'site'
            shutil.copytree(ROOT / 'website', site)
            sitemap = site / 'sitemap.xml'
            content = sitemap.read_text()
            start, end = content.index('  <url>'), content.index('  </url>') + len('  </url>')
            sitemap.write_text(content[:start] + content[end:])
            self.assertTrue(any('sitemap coverage' in e for e in validate(site)))

    def visible_version(self, filename):
        document = Document((ROOT / 'website' / filename).read_text())
        return next(node.attrs['data-version'] for node in document.nodes() if 'data-version' in node.attrs)

    def assert_mutation(self, old, new, error, filename='index.html'):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / 'site'
            shutil.copytree(ROOT / 'website', site)
            page = site / filename
            content = page.read_text()
            self.assertIn(old, content, f'Mutation fixture changed: {old}')
            page.write_text(content.replace(old, new, 1))
            self.assertTrue(any(error in e for e in validate(site)), f'Expected validator error: {error}')


class BuildTests(unittest.TestCase):
    def test_allowlist_excludes_internal_files(self):
        for file in ['README.md', 'deploy.sh', 'make-og.swift', '.env', '.git/config', 'scripts/secret.js', 'assets/internal.js', 'assets/site.js.map', 'assets/.private.png', 'guides/internal/index.html']:
            self.assertFalse(is_public_file(Path(file)), file)
        for file in ['index.html', 'en/privacy/index.html', 'ja/guides/export/index.html', 'assets/site.js', 'assets/icon-512.png', 'sitemap.xml']:
            self.assertTrue(is_public_file(Path(file)), file)

    def test_output_contains_only_publishable_files_and_still_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'build'
            files = build(ROOT / 'website', output)
            self.assertIn('index.html', files)
            self.assertNotIn('README.md', files)
            self.assertNotIn('deploy.sh', files)
            self.assertEqual(validate(output), [])

    def test_rejects_nonempty_destination_without_deleting_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'build'
            output.mkdir()
            marker = output / 'keep.txt'
            marker.write_text('keep')
            with self.assertRaises(ValueError):
                build(ROOT / 'website', output)
            self.assertEqual(marker.read_text(), 'keep')

    def test_rejects_overlapping_output(self):
        with self.assertRaises(ValueError):
            build(ROOT / 'website', ROOT / 'website' / 'out')

    def test_rejects_symlink_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'
            source.mkdir()
            (source / 'index.html').symlink_to(ROOT / 'website' / 'index.html')
            with self.assertRaises(ValueError):
                build(source, Path(tmp) / 'out')

    def test_rejects_symlink_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'target'
            target.mkdir()
            output = Path(tmp) / 'link'
            output.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                build(ROOT / 'website', output)
            self.assertEqual(list(target.iterdir()), [])


class SmokeTests(unittest.TestCase):
    def test_rejects_unsafe_or_ambiguous_origins(self):
        for url in ['http://example.com', 'https://name:password@example.com', 'https://example.com/a/', 'https://example.com?x=1', 'file:///tmp/index.html']:
            with self.assertRaises(ValueError, msg=url):
                smoke(url, ROOT / 'website')

    def test_smoke_on_local_build(self):
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'build'
            build(ROOT / 'website', output)
            server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(output)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                self.assertEqual(smoke(f'http://127.0.0.1:{server.server_port}', output), [])
            finally:
                server.shutdown()
                server.server_close()
                thread.join()


if __name__ == '__main__':
    unittest.main()
