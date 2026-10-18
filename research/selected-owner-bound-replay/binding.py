"""The additional owner-map postcondition; no supplier proof is inferred here.

Guard idea: Josie Elliston PR1959; accepted mutants: Aaron Wang PR2301.
Implementation: Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STAGE = Path("research/complex-t16-rare-pattern-exchanges")
OWNER = STAGE / "data/OWNERS.json.gz"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def decode(raw):
    def reject(value):
        raise ValueError("nonfinite JSON: " + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject)


def canonical(value):
    # Encoding preserves the JSON type distinction true / 1 / 1.0 and all keys.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def pins(root=ROOT, package=HERE):
    expected = {}
    for row in decode((package / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] != "input":
            continue
        path = Path(row["path"])
        need(not path.is_absolute() and ".." not in path.parts, "relative source path")
        need(sha((root / path).read_bytes()) == row["sha256"], "source drift: " + str(path))
        expected[str(path)] = row["sha256"]
    return expected


def check(template_gzip, owner_gzip, expected_owner_sha):
    """Check the exact bytes parsed, with the owner source independently pinned.

    This returns ONLY the new postcondition. The runner separately requires the
    unchanged strict replay subprocess to complete successfully.
    """
    need(sha(owner_gzip) == expected_owner_sha, "owner source drift")
    raw = gzip.decompress(template_gzip)
    template = decode(raw)
    owners = decode(gzip.decompress(owner_gzip))
    need(isinstance(template, dict) and isinstance(template.get("hosting"), dict), "hosting object")
    hosting = template["hosting"]
    need(isinstance(owners, list) and isinstance(hosting.get("pooled_slots"), list), "owner lists")
    need(canonical(hosting["pooled_slots"]) == canonical(owners), "pooled slots differ from pinned owners")
    need(hosting.get("owner_map_sha256") == expected_owner_sha, "owner-map digest link differs")
    return {
        "schema": "selected-owner-postcondition/1",
        "status": "PASS_EXACT_SELECTED_OWNER_BINDING",
        "roles": len(owners),
        "template_payload_sha256": sha(raw),
        "template_gzip_sha256": sha(template_gzip),
        "owner_gzip_sha256": expected_owner_sha,
        "owner_typed_content_sha256": sha(canonical(owners)),
        "pooled_slots_equal_including_time": True,
        "owner_digest_link_equal": True,
    }
