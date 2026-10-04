import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
import subprocess
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.links.append(value)

class ArchiveHealthTests(unittest.TestCase):
    def test_local_links_resolve(self):
        hold = json.loads((ROOT / "tests" / "publication_holds.json").read_text(encoding="utf-8"))
        expected_holds = {(item["file"], item["unresolved_link"]) for item in hold["holds"]}
        observed_holds = []
        for page in ROOT.glob("*.html"):
            parser = LinkParser()
            parser.feed(page.read_text(encoding="utf-8-sig"))
            for value in parser.links:
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (ROOT if url.path.startswith("/") else page.parent) / unquote(url.path).lstrip("/")
                with self.subTest(page=page.name, link=value):
                    if (page.name, value) in expected_holds:
                        self.assertFalse(target.exists(), "Resolved link must be removed from the explicit hold")
                        observed_holds.append((page.name, value))
                    else:
                        self.assertTrue(target.exists(), str(target))
        self.assertEqual(set(observed_holds), expected_holds, "Only the exact declared publication holds may remain unresolved")
        self.assertEqual(len(observed_holds), 2)

    def test_publication_hold_preserves_original_git_blob(self):
        hold = json.loads((ROOT / "tests" / "publication_holds.json").read_text(encoding="utf-8"))
        self.assertEqual(hold["status"], "PUBLICATION_REVIEW_HOLD")
        expected = {
            "athenasglobalplan.html": ("downloads/Athena_Plan_Healing_the_Planet.pdf", "4270762800197a77e36d7215c8f2056b8c3830bc"),
            "avatarandgenius.html": ("downloads/The_Avatar_and_the_Great_Genius.pdf", "cf7e1c7f0f2676cbd2325248a5fe049d33c744d0"),
        }
        self.assertEqual(len(hold["holds"]), 2)
        self.assertEqual({item["file"] for item in hold["holds"]}, set(expected))
        for item in hold["holds"]:
            with self.subTest(file=item["file"]):
                self.assertEqual((item["unresolved_link"], item["original_git_blob"]), expected[item["file"]])
                actual = subprocess.check_output(["git", "-C", str(ROOT), "hash-object", "--no-filters", str(ROOT / item["file"])], text=True).strip()
                self.assertEqual(actual, item["original_git_blob"])

    def test_json_downloads_parse(self):
        for path in ROOT.glob("*.json"):
            with self.subTest(path=path.name):
                json.loads(path.read_bytes())

    def test_archived_source_bytes_match_original_manifest(self):
        manifest_path = ROOT / "tests" / "original-source-sha256.json"
        if not manifest_path.exists():
            self.skipTest("This static HTML library has no JSON carriers")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), {p.name for p in ROOT.glob("*.json")})
        for name, expected in manifest.items():
            with self.subTest(path=name):
                record = json.loads((ROOT / name).read_bytes())
                self.assertEqual(record["format"], "athenachka.narrative-archive.v1")
                self.assertEqual(record["source_file"], name)
                self.assertEqual(record["source_encoding"], "utf-8")
                self.assertIs(record["source_instructions_executable"], False)
                self.assertEqual(record["source_sha256"], expected)
                self.assertEqual(hashlib.sha256(record["source_text"].encode("utf-8")).hexdigest(), expected)

if __name__ == "__main__":
    unittest.main()
