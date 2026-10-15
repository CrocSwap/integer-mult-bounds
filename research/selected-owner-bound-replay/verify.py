"""Bounded new-gate replay; does not execute the inherited strict stages.

Use full_check.py for the separate real strict-replay integration test.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import copy
import gzip
import json
import sys
import tarfile
import tempfile
import subprocess

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as b


ARCHIVE = Path("research/community-frontier1094-audit/selected-replay.tar.gz")
MEMBER = "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"


def predecessor():
    spec = b.decode((HERE / "PREDECESSOR.json").read_bytes())
    for name, item in spec["files"].items():
        b.need(b.sha((HERE / name).read_bytes()) == item["sha256"], "predecessor source drift")
    return spec


def fixture():
    with tarfile.open(b.ROOT / ARCHIVE) as archive:
        members = [m for m in archive.getmembers() if m.name == MEMBER]
        b.need(len(members) == 1 and members[0].isfile(), "unique regular template member")
        return archive.extractfile(members[0]).read()


def replay():
    source_pins = b.pins()
    predecessor()
    owner_raw = (b.ROOT / b.OWNER).read_bytes()
    expected = source_pins[str(b.OWNER)]
    raw = fixture()
    original = b.decode(gzip.decompress(raw))
    good = b.check(raw, owner_raw, expected)
    b.need(good["roles"] == 69120, "selected role count")
    def compressed(value):
        return gzip.compress(b.canonical(value), mtime=0)
    def check(value):
        return b.check(compressed(value), owner_raw, expected)
    def slot(value):
        return value["hosting"]["pooled_slots"]
    def swap(value):
        a, c = slot(value)[0], slot(value)[480]
        b.need(a["width"] == c["width"] == 9 and (a["time"], c["time"]) == (0, 1), "PR2301 witness")
        a["time"], c["time"] = c["time"], a["time"]
    mutations = {
        "PR2301_time_swap": (swap, "pooled slots differ"),
        "PR2301_digest": (lambda t: t["hosting"].__setitem__("owner_map_sha256", "0" * 64), "digest link"),
        "changed_time": (lambda t: slot(t)[0].__setitem__("time", 9), "pooled slots differ"),
        "boolean_time": (lambda t: slot(t)[0].__setitem__("time", False), "pooled slots differ"),
        "float_time": (lambda t: slot(t)[0].__setitem__("time", 0.0), "pooled slots differ"),
        "missing_time": (lambda t: slot(t)[0].pop("time"), "pooled slots differ"),
        "unknown_role_field": (lambda t: slot(t)[0].__setitem__("unvalidated", 1), "pooled slots differ"),
        "changed_port": (lambda t: slot(t)[0].__setitem__("port", 15), "pooled slots differ"),
        "omitted_role": (lambda t: slot(t).pop(), "pooled slots differ"),
        "duplicated_role": (lambda t: slot(t).__setitem__(1, dict(slot(t)[0])), "pooled slots differ"),
        "reordered_roles": (lambda t: slot(t).reverse(), "pooled slots differ"),
        "nonlist_roles": (lambda t: t["hosting"].__setitem__("pooled_slots", {}), "owner lists"),
    }
    rejected = []
    for name, (mutate, message) in mutations.items():
        changed = copy.deepcopy(original)
        mutate(changed)
        try:
            check(changed)
        except ValueError as exc:
            b.need(message in str(exc), "wrong rejection: " + name)
            rejected.append(name)
        else:
            raise ValueError("accepted mutant: " + name)
    payload = gzip.decompress(raw)
    duplicate = b'{"hosting":null,' + payload[1:]
    extra = {
        "duplicate_JSON_key": (gzip.compress(duplicate, mtime=0), owner_raw, "duplicate JSON key"),
        "wrong_owner_bytes": (raw, owner_raw + b"\x00", "owner source drift"),
        "nonfinite_JSON": (gzip.compress(b'{"hosting":NaN}', mtime=0), owner_raw, "nonfinite JSON"),
    }
    for name, (template, owners, message) in extra.items():
        try:
            b.check(template, owners, expected)
        except ValueError as exc:
            b.need(message in str(exc), "wrong rejection: " + name)
            rejected.append(name)
        else:
            raise ValueError("accepted malformed input: " + name)
    # Generated containers/JSON whitespace are not immutable input identities.
    for template in (gzip.compress(payload, compresslevel=1, mtime=123),
                     gzip.compress(json.dumps(original, indent=1).encode(), mtime=0)):
        alt = b.check(template, owner_raw, expected)
        b.need(alt["owner_typed_content_sha256"] == good["owner_typed_content_sha256"], "valid re-encoding")
    # The inherited JSON == relation would miss these two typed changes.
    for value in (False, 0.0):
        a, c = {"time": 0}, {"time": value}
        b.need(a == c and b.canonical(a) != b.canonical(c), "typed comparison witness")
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary) / "existing"
        work.mkdir()
        keep = work / "BOUND-REPLAY.json"
        keep.write_bytes(b"prior evidence\n")
        result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "run_bound.py"),
                                 "--local", temporary, "--work", str(work)],
                                capture_output=True, text=True, timeout=20)
        b.need(result.returncode != 0 and "fresh output" in result.stderr, "existing output must reject")
        b.need(keep.read_bytes() == b"prior evidence\n" and list(work.iterdir()) == [keep], "existing evidence changed")
    return {"schema": "selected-owner-bound-gate-tests/1", "strict_replay_executed": False,
            "positive": good, "role_fields": sorted(original["hosting"]["pooled_slots"][0]),
            "negative_controls": rejected, "valid_reencodings": 2,
            "typed_equality_counterexamples": 2, "existing_output_preserved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    b.need(args.out is None or not args.out.exists(), "output already exists")
    result = replay()
    if args.out:
        with args.out.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        b.need(b.canonical(result) == b.canonical(b.decode((HERE / "RESULT.json").read_bytes())), "gate receipt drift")
    print("PASS_SELECTED_OWNER_BOUND_GATE", "roles=69120", "controls=15", "strict_replay_executed=false")


if __name__ == "__main__":
    main()
