#!/usr/bin/env python3
"""Offline PR99 source-retention proof and saved-profile reconciliation.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
This checks source identity and recorded accounting, not physical execution.
"""
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
PARENT = "56b66d58297deca1d7dd130247d720e960f77a37"
PR99 = "0622dcce6a897567e4eb6bdfedc7def66ab21346"
PR103 = "75ab1f70d146c21c7611ce0df9eb5f645f51ac0e"
ARCHIVE = "b91de239a64d24d8aee409a0f4ac3e00710ae5c1"
ORIGINAL = "research/nondegenerate-readout-saturation"
RETAINED = "research/saturated-balanced/vendor/pr99"
COMMON_TREE = "6bebd79406bb2453ada2b7761aece13d3e53b694"
INPUTS = (
    "research/community-reconciliation92-audit/ARCHIVE.json",
    "research/community-reconciliation92-audit/REVIEW.json",
)
BLOBS = {
    "baseline": (PR99, ORIGINAL + "/experiments/round7-review/qualification.json"),
    "candidate": (PR99, ORIGINAL + "/experiments/round7-review/saturation-results.json"),
    "prior_review": (PR99, ORIGINAL + "/historical/results.json"),
    "bit_ledger": (PR103, "research/saturated-balanced/bit-ledger.json"),
    "original_notice": (PR99, ORIGINAL + "/NOTICE"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def loads(raw):
    return json.loads(raw, object_pairs_hook=no_duplicate_keys)


def git_id(kind, raw):
    return hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class Proof:
    def __init__(self, document):
        require(document["schema_version"] == 1, "unsupported proof schema")
        self.objects = document["objects"]
        self.used = set()

    def raw(self, oid, kind):
        require(re.fullmatch(r"[0-9a-f]{40}", oid) is not None, "invalid Git id")
        require(oid in self.objects, "missing Git object: " + oid)
        obj = self.objects[oid]
        require(obj["type"] == kind, "Git object type mismatch")
        raw = base64.b64decode(obj["base64"], validate=True)
        require(git_id(kind, raw) == oid, "Git object digest mismatch: " + oid)
        self.used.add(oid)
        return raw

    def commit(self, oid):
        header = self.raw(oid, "commit").split(b"\n\n", 1)[0].decode("utf-8").splitlines()
        trees = [line[5:] for line in header if line.startswith("tree ")]
        require(len(trees) == 1, "commit needs one tree")
        return trees[0], [line[7:] for line in header if line.startswith("parent ")]

    def tree(self, oid):
        raw, offset, entries = self.raw(oid, "tree"), 0, {}
        while offset < len(raw):
            space = raw.find(b" ", offset)
            zero = raw.find(b"\0", space + 1)
            require(space > offset and zero > space + 1 and zero + 21 <= len(raw),
                    "malformed Git tree")
            mode = raw[offset:space].decode("ascii")
            name = raw[space + 1:zero].decode("utf-8")
            require(mode in ("40000", "100644", "100755", "120000"), "unsupported tree mode")
            require(name not in (".", "..") and "/" not in name and name not in entries,
                    "invalid or duplicate tree path")
            entries[name] = (mode, raw[zero + 1:zero + 21].hex())
            offset = zero + 21
        return entries

    def resolve(self, commit, path, expected_mode=None):
        parts = path.split("/")
        require(all(p and p not in (".", "..") for p in parts), "invalid requested path")
        oid, _ = self.commit(commit)
        mode = "40000"
        for part in parts:
            require(mode == "40000", "path traverses a non-directory")
            entries = self.tree(oid)
            require(part in entries, "missing path component: " + part)
            mode, oid = entries[part]
        if expected_mode is not None:
            require(mode == expected_mode, "path mode mismatch: " + path)
        return mode, oid

    def inventory(self, tree, prefix=""):
        result = {}
        for name, (mode, oid) in self.tree(tree).items():
            path = prefix + name
            if mode == "40000":
                result.update(self.inventory(oid, path + "/"))
            else:
                result[path] = {"mode": mode, "blob": oid}
        return result

    def difference(self, before, after, prefix=""):
        """Walk every changed subtree; equal Git trees are skipped exactly."""
        if before == after:
            return {}
        left, right = self.tree(before), self.tree(after)
        changed = {}
        for name in sorted(set(left) | set(right)):
            a, b = left.get(name), right.get(name)
            path = prefix + name
            if a == b:
                continue
            if a is None and b[0] == "40000":
                changed.update({p: {"before": None, "after": row}
                                for p, row in self.inventory(b[1], path + "/").items()})
            elif a is not None and b is not None and a[0] == b[0] == "40000":
                changed.update(self.difference(a[1], b[1], path + "/"))
            else:
                changed[path] = {
                    "before": None if a is None else {"mode": a[0], "blob": a[1]},
                    "after": None if b is None else {"mode": b[0], "blob": b[1]},
                }
        return changed

    def blob(self, role):
        commit, path = BLOBS[role]
        _, oid = self.resolve(commit, path, "100644")
        return self.raw(oid, "blob")


def histogram(pairs, width):
    out = {}
    for rank, count in pairs:
        require(type(rank) is int and type(count) is int and 0 < rank <= width and count > 0,
                "invalid histogram entry")
        require(rank not in out, "duplicate histogram rank")
        out[rank] = count
    require(bool(out), "empty histogram")
    return out


def nonzero(counter):
    return {str(k): v for k, v in sorted(counter.items()) if v}


def check_accounting(baseline, candidate, prior_review, bit_ledger):
    """Reconcile authenticated saved reports; do not call their producer code."""
    old, candidate = baseline["histogram"], candidate["Z"]
    new = candidate["histogram"]
    for key in ("h", "m", "v", "N", "W", "L", "s", "R"):
        require(type(old[key]) is int and old[key] == new[key], "changed common parameter: " + key)
    require((old["h"], old["m"], old["v"]) == (23, 529, 1771), "wrong historical instance")
    before, after = histogram(old["hist"], old["m"]), histogram(new["hist"], new["m"])
    changes = candidate["changes"]
    require(len({c["slot"] for c in changes}) == len(changes), "duplicate changed slot")
    require(len(changes) == candidate["changed_slots"] == 22, "changed-slot count mismatch")
    steps, expected, types = 0, Counter(), Counter()
    for c in changes:
        a, b = c["old_dim"], c["new_dim"]
        require(type(a) is int and type(b) is int and 0 <= a < b <= old["h"],
                "invalid frame extension")
        steps += b - a
        types[a, b] += 1
        r0, r1 = old["m"] - 2 * (old["h"] - a), old["m"] - 2 * (old["h"] - b)
        multiplicity = 2 * old["v"]
        expected[r0] -= multiplicity
        expected[r1] += multiplicity
        expected[1] -= multiplicity * (r1 - r0)
    require(steps == candidate["dimension_increase"] == 25, "dimension increase mismatch")
    delta = Counter(after)
    delta.subtract(before)
    require(nonzero(delta) == nonzero(expected), "saved delta differs from the 22 recorded mergers")
    require(nonzero(delta) == prior_review["total_histogram_delta"], "prior delta receipt mismatch")
    require(prior_review["changed_count"] == 22 and prior_review["dimension_increase"] == 25,
            "prior frame count mismatch")
    recorded_components = Counter()
    for component in prior_review["independently_recomputed_component_deltas"].values():
        recorded_components.update({int(k): v for k, v in component.items()})
    require(nonzero(recorded_components) == nonzero(delta), "prior component accounting mismatch")
    for hist in (before, after):
        require(sum(rank * count for rank, count in hist.items()) == old["s"], "recursive mass mismatch")
    retained = histogram([(int(k), v) for k, v in bit_ledger["histogram"].items()], new["m"])
    require(retained == after, "PR103 does not retain the exact candidate histogram")
    require(bit_ledger["recursive_rank"] == old["s"], "PR103 recursive mass mismatch")
    require(bit_ledger["roles"] == old["R"], "PR103 auxiliary role mismatch")
    return {
        "changed_frames": len(changes), "dimension_increase": steps,
        "frame_extension_counts": {f"{a}->{b}": n for (a, b), n in sorted(types.items())},
        "histogram_delta": nonzero(delta), "rank_mass_delta": sum(k * v for k, v in delta.items()),
        "recursive_rank": old["s"], "width": old["W"], "auxiliary_roles": old["R"],
        "pr103_saved_histogram_matches": True,
    }


def external_inputs():
    pins = loads((HERE / "SOURCES.json").read_bytes())
    require(pins["base_commit"] == BASE, "wrong research base")
    rows = {row["path"]: row for row in pins["files"] if row["usage"] == "input"}
    require(set(rows) == set(INPUTS), "external input coverage changed")
    result = []
    for path in INPUTS:
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == rows[path]["sha256"], "external source drift: " + path)
        require(git_id("blob", raw) == rows[path]["git_blob"], "external blob drift: " + path)
        result.append(loads(raw))
    return result


def verify(document, archive, reviews):
    proof = Proof(document)
    original_tree, original_parents = proof.commit(PR99)
    require(original_parents == [PARENT], "PR99 comparison parent changed")
    parent_tree, _ = proof.commit(PARENT)
    _, source = proof.resolve(PR99, ORIGINAL, "40000")
    _, retained = proof.resolve(PR103, RETAINED, "40000")
    require(source == retained == COMMON_TREE, "complete package trees differ")
    files = proof.inventory(source)
    require(len(files) == 46 and files == document["files"], "incomplete or changed package inventory")
    difference = proof.difference(parent_tree, original_tree)
    expected = {ORIGINAL + "/" + path: {"before": None, "after": row} for path, row in files.items()}
    require(difference == expected, "PR99 has changes outside the retained package")
    archive_tree, archive_parents = proof.commit(ARCHIVE)
    require(archive["commit"] == ARCHIVE and archive["tree"] == archive_tree
            and archive["parents"] == archive_parents, "archive receipt does not match its Git commit")
    require(PR103 in archive_parents, "PR103 is absent from the retained archive parents")
    require(reviews["103"]["head"] == PR103, "historical review refers to a different head")
    require(reviews["103"]["contributor"]["login"] == "rohanarun", "historical integration credit mismatch")
    data = {role: loads(proof.blob(role)) for role in BLOBS if role != "original_notice"}
    require(proof.blob("original_notice") == (HERE / "UPSTREAM-NOTICE").read_bytes(),
            "original notice was not retained exactly")
    accounting = check_accounting(**data)
    require(proof.used == set(proof.objects), "unused evidence objects")
    return {
        "status": "PASS_PR99_RETENTION_AND_SAVED_ACCOUNTING",
        "base_commit": BASE, "original_head": PR99, "retained_head": PR103,
        "archive_commit": ARCHIVE, "common_package_tree": COMMON_TREE,
        "retained_files": len(files), "original_changes": {"added": len(difference), "modified": 0, "deleted": 0},
        "authenticated_git_objects": len(proof.used), "accounting": accounting,
        "fresh_physical_replay": False, "new_kappa_claim": False,
        "scope": "Complete historical source retention and saved-report accounting; no new construction acceptance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=HERE / "SOURCE-PROOF.json")
    parser.add_argument("--write-result", type=Path, help="write a newly recomputed receipt instead of comparing RESULT.json")
    args = parser.parse_args()
    result = verify(loads(args.proof.read_bytes()), *external_inputs())
    if args.write_result:
        args.write_result.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == loads((HERE / "RESULT.json").read_bytes()), "saved result differs from recomputation")
    print(result["status"] + f" files={result['retained_files']} singleton_delta={result['accounting']['histogram_delta']['1']} mass_delta=0")


if __name__ == "__main__":
    main()
