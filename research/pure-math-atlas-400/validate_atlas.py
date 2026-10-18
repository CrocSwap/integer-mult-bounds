"""Validate atlas counts, cross-references and packaged bytes. This does not prove mathematics."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(root, check_local=False):
    root = root.resolve()
    catalog = json.loads((root / "CATALOG.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]
    assert len(entries) == 400
    by_id = {e["id"]: e for e in entries}
    assert len(by_id) == 400
    expected_ids = {f"{p}{i:03d}" for p in "ABCD" for i in range(1, 101)}
    assert set(by_id) == expected_ids
    proved = [e for e in entries if not e["conjectural"]]
    conjectures = [e for e in entries if e["conjectural"]]
    assert len(proved) == 379 and len(conjectures) == 21
    assert all(e["has_proof"] for e in proved)
    assert sum(e["status"] == "atlas_proposal_global_status_not_established" for e in conjectures) == 8
    for number, volume in enumerate(catalog["volumes"], 1):
        data = (root / volume["path"]).read_bytes()
        assert sha(data) == volume["exported_sha256"], volume["path"]
        text = data.decode("utf-8")
        assert "\r" not in text and "\ufffd" not in text
        assert not any(ord(c) < 32 and c not in "\n\t" for c in text)
        heads = list(re.finditer(r"^### ([ABCD]\d{3})[^\n]*\n", text, re.M))
        assert [m.group(1) for m in heads] == [f"{'ABCD'[number-1]}{i:03d}" for i in range(1, 101)]
        for i, match in enumerate(heads):
            entry = by_id[match.group(1)]
            body = text[match.end():heads[i+1].start() if i+1 < len(heads) else len(text)]
            assert entry["volume"] == number
            assert set(entry["referenced_entries"]) <= expected_ids
            assert f'<a id="{entry["anchor"]}"></a>' in text
            assert bool("**Proof.**" in body) == entry["has_proof"]
            if entry["conjectural"]:
                assert re.search(r"evidence|approach|not proved|status", body, re.I)
            else:
                assert "**Proof.**" in body, entry["id"]
        report = (root / "reviews" / f"{number:02d}-peer-review.md").read_text(encoding="utf-8-sig")
        assert volume["reviewed_draft_sha256"] in report
    links = 0
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8-sig")
        for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text):
            if re.match(r"(?:https?://|mailto:|[A-Za-z]:[/\\])", target):
                continue
            target = target.strip("<>")
            local, sep, fragment = target.partition("#")
            q = (p.parent / local).resolve() if local else p
            assert q.is_relative_to(root), (p, target, "link escapes bundle")
            assert q.is_file(), (p, target, "missing link target")
            if sep and fragment:
                assert f'<a id="{fragment}"></a>' in q.read_text(encoding="utf-8-sig"), (p, target, "missing anchor")
            links += 1
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and p.name != "MANIFEST.json"}
    assert actual == set(manifest["files"]), (actual - set(manifest["files"]), set(manifest["files"]) - actual)
    for rel, info in manifest["files"].items():
        p = root / rel
        assert p.resolve().is_relative_to(root)
        assert not p.is_symlink()
        data = p.read_bytes()
        assert len(data) == info["bytes"] and sha(data) == info["sha256"], rel
        assert len(data) < 25 * 1024 * 1024
        assert p.suffix in {".md", ".json", ".py"}, rel
    audit = json.loads((root / "sources/SOURCE-HASH-RECHECK.json").read_text(encoding="utf-8"))
    assert audit["all_match"] and len(audit["results"]) == 31
    assert all(v["match"] and v["expected"] == v["actual"] for v in audit["results"])
    if check_local:
        for item in audit["results"]:
            assert sha(Path(item["path"]).read_bytes()) == item["expected"], item["path"]
    return {"status": "PASS", "entries": 400, "proved": 379, "conjectural": 21,
            "volume_count": 4, "local_links_checked": links,
            "files_including_manifest": len(actual) + 1,
            "local_sources_rechecked": check_local,
            "scope": "Structural and SHA-256 validation; not mathematical or Lean proof verification."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-local-sources", action="store_true", help="also rehash the registered source paths on this machine")
    args = parser.parse_args()
    try:
        print(json.dumps(check(Path(__file__).parent, args.check_local_sources), indent=2))
    except (AssertionError, OSError, ValueError) as exc:
        print("FAIL: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
