#!/usr/bin/env python3
"""Offline source and exact-moment reconciliation for PR225. No source code imports.

Ross Richardson, substantial OpenAI Codex assistance, Apache-2.0.
The capsule preserves Chafik Boukhalfa's original package and notices unchanged.
"""
import argparse
import base64
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
BASE = "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf"
OLD = "b8e829172fc92bbbd6b1eda560ab5d99aebee0df"
NEW = "830971b6b157374ebf941d0ca0b73fd2b956e3e0"
PACKAGE = "research/exact-dft-transfer"
WORKFLOW = ".github/workflows/exact-dft-transfer.yml"
NAMES = ("pr144", "pr200", "pr194", "pr233", "pr194-five", "pr233-five")
ENDPOINTS = (Fraction(607, 1250000), Fraction(3327, 5000000), Fraction(7009, 10**7),
             Fraction(7099, 10**7), Fraction(7474, 10**7), Fraction(7547, 10**7))
SCALE = 10**60
LOG_TERMS = 80
EXP_TERMS = 24


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ceildiv(n, d):
    require(n >= 0 and d > 0, "invalid nonnegative quotient")
    return (n + d - 1) // d


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def original_decimal(text):
    require(text.endswith("/10^30"), "original decimal certificate format")
    return Fraction(int(text[:-6]), 10**30)


class GitCapsule:
    """Read Git commit/tree/blob objects directly; no git, shell or network needed."""
    def __init__(self, data):
        require(data.get("format") == "pr225-git-capsule-v1", "capsule format")
        self.objects = {}
        self.used = set()
        for oid, record in data["objects"].items():
            kind = record["type"]
            require(kind in ("commit", "tree", "blob"), "object type")
            raw = base64.b64decode(record["data"], validate=True)
            actual = hashlib.sha1((kind + " " + str(len(raw))).encode() + b"\0" + raw).hexdigest()
            require(actual == oid, "Git object digest mismatch: " + oid)
            self.objects[oid] = (kind, raw)

    def get(self, oid, kind):
        require(oid in self.objects, "missing Git object: " + oid)
        self.used.add(oid)
        actual, raw = self.objects[oid]
        require(actual == kind, "wrong Git object type")
        return raw

    def tree(self, oid):
        raw = self.get(oid, "tree")
        entries, pos = {}, 0
        while pos < len(raw):
            end = raw.index(b"\0", pos)
            mode, name = raw[pos:end].split(b" ", 1)
            require(end + 21 <= len(raw), "truncated tree object")
            name = name.decode()
            require(name not in entries and name not in (".", "..") and "/" not in name, "invalid tree path")
            entries[name] = (mode.decode(), raw[end + 1:end + 21].hex())
            pos = end + 21
        return entries

    def resolve(self, commit, path):
        raw = self.get(commit, "commit")
        first = raw.split(b"\n", 1)[0]
        require(first.startswith(b"tree "), "commit root tree missing")
        oid, mode = first[5:].decode(), "40000"
        for part in path.split("/"):
            require(mode == "40000", "non-tree parent")
            entries = self.tree(oid)
            require(part in entries, "path absent: " + path)
            mode, oid = entries[part]
        return mode, oid

    def read(self, commit, path):
        mode, oid = self.resolve(commit, path)
        require(mode in ("100644", "100755"), "nonregular input")
        return self.get(oid, "blob")

    def json(self, commit, path):
        return json.loads(self.read(commit, path))

    def inventory(self, commit):
        mode, root = self.resolve(commit, PACKAGE)
        require(mode == "40000", "package is not a directory")
        result = {}

        def walk(oid, prefix):
            for name, (mode, child) in self.tree(oid).items():
                path = prefix + "/" + name
                if mode == "40000":
                    walk(child, path)
                else:
                    require(mode in ("100644", "100755"), "nonregular package file")
                    content = self.get(child, "blob")
                    result[path] = {"mode": mode, "blob": child, "sha256": sha256(content)}
        walk(root, PACKAGE)
        mode, oid = self.resolve(commit, WORKFLOW)
        result[WORKFLOW] = {"mode": mode, "blob": oid, "sha256": sha256(self.get(oid, "blob"))}
        return result


def small_log(n, d):
    """Outward integer interval for SCALE*log(n/d), with 1 <= n/d <= 2."""
    require(0 < d <= n <= 2 * d, "small-log domain")
    u, v = n - d, n + d  # y = u/v, at most 1/3
    low, high = SCALE * u // v, ceildiv(SCALE * u, v)
    sl, sh = 0, 0
    for j in range(LOG_TERMS):
        sl += low // (2 * j + 1)
        sh += ceildiv(high, 2 * j + 1)
        low = low * u * u // (v * v)
        high = ceildiv(high * u * u, v * v)
    # Omitted odd series <= y^(2N+1)/((2N+1)*(1-y^2)).
    tail = ceildiv(2 * high * v * v, (2 * LOG_TERMS + 1) * (v * v - u * u))
    return 2 * sl, 2 * sh + tail


@lru_cache(maxsize=None)
def log_interval(n, d):
    require(type(n) is int and type(d) is int and 0 < d <= n, "log domain")
    k = 0
    while n > 2 * d:
        d *= 2
        k += 1
    lo, hi = small_log(n, d)
    l2, h2 = small_log(2, 1)
    return lo + k * l2, hi + k * h2


def exp_interval(lo, hi):
    """Outward interval for SCALE*exp(x), lo <= SCALE*x <= hi <= SCALE/16."""
    require(0 <= lo <= hi <= SCALE // 16, "exp domain")
    tl = th = sl = sh = SCALE
    for k in range(1, EXP_TERMS + 1):
        tl = tl * lo // (SCALE * k)
        th = ceildiv(th * hi, SCALE * k)
        sl += tl
        sh += th
    first = ceildiv(th * hi, SCALE * (EXP_TERMS + 1))
    tail = ceildiv(first * SCALE * (EXP_TERMS + 2), SCALE * (EXP_TERMS + 2) - hi)
    return sl, sh + tail


def moment_interval(m, hist, a):
    require(type(m) is int and m > 1, "moment width")
    require(isinstance(a, Fraction) and 0 <= a < 1, "moment exponent")
    require(bool(hist), "empty histogram")
    low, high = 0, 0
    for r, n in sorted(hist.items()):
        require(type(r) is int and type(n) is int and 0 < r < m and n > 0, "invalid child")
        ll, lh = log_interval(m, r)
        el, eh = exp_interval(ll * a.numerator // a.denominator,
                             ceildiv(lh * a.numerator, a.denominator))
        low += n * r * el // m
        high += ceildiv(n * r * eh, m)
    return low, high


def histogram(p):
    result = {}
    for key, value in p["child_histogram"].items():
        r = int(key)
        require(str(r) == key and type(value) is int and value >= 0, "invalid histogram entry")
        if value:
            result[r] = value
    require(result and all(0 < r < p["m"] for r in result), "child outside width")
    return result


def five_stage(p):
    """Independent component invoice, restricted to the pinned h=22 words."""
    require(p["m"] == 66 and p["W_per_vertex"] == 12052, "five-stage source geometry")
    h3 = histogram(p)
    # Remove every three-stage data child before dividing the invocation count.
    inv = {}
    for r in sorted(set(h3) | {2}):
        n = h3.get(r, 0) - (2640 if r == 2 else 0)
        require(n >= 0 and n % 3 == 0, "nonintegral per-invocation ledger")
        if n:
            inv[r] = n // 3
    h5 = {r: n * 5 for r, n in inv.items()}
    for r in (4, 21, 42, 46):
        h5[r] = h5.get(r, 0) + 2640
    rank = sum(r * n for r, n in h5.items())
    require(rank == 1613040, "five-stage rank invoice")
    return {"m": 110, "h": 22, "v": 1320, "loss": 440, "R": 9412,
            "W_per_vertex": 14692, "rank_per_vertex": rank, "deficit_per_vertex": 3080,
            "child_histogram": {str(r): n for r, n in sorted(h5.items())}}


def check_profile(p, c):
    hist = histogram(p)
    fields = {"m": "m", "h": "h", "v": "v", "loss": "loss", "R": "R",
              "W_per_vertex": "roles_per_vertex", "rank_per_vertex": "rank_per_vertex",
              "deficit_per_vertex": "deficit_per_vertex"}
    require(all(p.get(k) == c[v] for k, v in fields.items()), "profile metadata mismatch")
    require(hist == histogram(c), "derived histogram mismatch")
    rank = sum(r * n for r, n in hist.items())
    require(rank == c["rank_per_vertex"], "rank mismatch")
    require(c["m"] * c["roles_per_vertex"] - rank == c["deficit_per_vertex"], "deficit mismatch")
    return hist


def run(cap):
    old, new = cap.inventory(OLD), cap.inventory(NEW)
    require(len(old) == 19 and len(new) == 23, "package inventory size")
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(p for p in old.keys() & new.keys() if old[p] != new[p])
    unchanged = sorted(p for p in old.keys() & new.keys() if old[p] == new[p])
    require(not removed and len(added) == 4 and len(changed) == 6 and len(unchanged) == 13,
            "unexpected source delta")
    oldsrc = cap.json(OLD, PACKAGE + "/SOURCE.json")
    src = cap.json(NEW, PACKAGE + "/SOURCE.json")
    require(oldsrc["suppliers"] == src["suppliers"], "supplier sources changed")
    require(oldsrc["references"] == src["references"] == {}, "unexpected local references")
    require(set(src["framework"]) - set(oldsrc["framework"]) == {"five_stage"}, "framework delta")
    require(all(src["framework"][k] == v for k, v in oldsrc["framework"].items()), "old framework changed")
    oldexp = cap.json(OLD, PACKAGE + "/expected.json")
    newexp = cap.json(NEW, PACKAGE + "/expected.json")
    require(set(oldexp["suppliers"]) == set(NAMES[:4]) and set(newexp["suppliers"]) == set(NAMES), "coverage rows")
    require(all(newexp["suppliers"][k] == v for k, v in oldexp["suppliers"].items()), "historical rows changed")
    require(newexp["best"] == "pr233-five" and newexp["theta"] == "9992453/10000000", "new best-row summary")
    require(newexp["framework"] == src["framework"], "framework receipt mismatch")
    ledger = cap.json(BASE, "docs/research/pr-ledger.json")
    # The ledger is a source snapshot, not a live approval or closure.
    row = next(r for r in ledger["pull_requests"] if r["number"] == 225)
    require(row["current_head"] == NEW and row["previously_reviewed_heads"] == [OLD]
            and row["disposition"] == "changed_since_review", "base review scope")
    round9 = cap.json(BASE, "research/community-round9-audit/review-ledger.json")
    historical = next(r for r in round9["prs"] if r["number"] == 225)
    require(historical["head"] == OLD and historical["disposition"] == "scoped-replay-passed", "historical review identity")
    require(set(historical["source_files"]) == set(old), "historical review file coverage")
    log = cap.read(BASE, "research/community-round9-audit/pr225-replay.log.txt").decode()
    require("theta = 1 - 7099/10000000 with the pr233 supplier" in log and "-five" not in log, "historical replay log")
    selected = cap.json(BASE, "certificates/selected-result.json")
    require(selected["kappa"] == "1661960547713947/1000000000000000000", "selected base context")

    records, source_pins = {}, {}
    for name, a in zip(NAMES, ENDPOINTS):
        parent = name.replace("-five", "")
        pin = src["suppliers"][parent]
        raw = cap.read(pin["commit"], pin["path"])
        require(sha256(raw) == pin["sha256"], "supplier SHA256 mismatch")
        if parent != "pr144":
            require(cap.read(NEW, pin["local_path"]) == raw, "vendored supplier mismatch")
        data = json.loads(raw)
        p = data if parent == "pr144" else data["complex"]["profile"] if parent == "pr200" else data["complex_profile"]
        if name.endswith("-five"):
            p = five_stage(p)
        cpath = PACKAGE + "/certificates/network-children-" + name + ".json"
        cbytes = cap.read(NEW, cpath)
        c = json.loads(cbytes)
        field = "child_histogram" if parent == "pr144" else "complex.profile" if parent == "pr200" else "complex_profile"
        require(c["source"] == {"repository": pin["repository"], "pr": pin["pr"], "commit": pin["commit"],
                "path": pin["path"], "sha256": pin["sha256"], "field": field}, "child provenance")
        hist = check_profile(p, c)
        if not name.endswith("-five") and c["v"] is not None and c["loss"] is not None:
            require(c["deficit_per_vertex"] == 2 * c["v"] - 3 * c["loss"], "three-stage identity")
        m, W = c["m"], c["roles_per_vertex"]
        mc = cap.json(NEW, PACKAGE + "/certificates/moment-" + name + ".json")
        require(mc["children_sha256"] == sha256(cbytes), "moment child binding")
        require(Fraction(mc["a"]) == a and Fraction(mc["theta"]) == 1 - a
                and Fraction(mc["next_grid_point"]) == a + Fraction(1, 10**7), "moment exponent binding")
        require(all(mc[k] == c[k] for k in ("m", "roles_per_vertex", "rank_per_vertex", "deficit_per_vertex"))
                and mc["max_child"] == max(hist), "moment invoice binding")
        low, high = moment_interval(m, hist, a)
        nextlow, nexthigh = moment_interval(m, hist, a + Fraction(1, 10**7))
        require(high < W * SCALE, "claimed endpoint not certified")
        require(nextlow > W * SCALE, "next endpoint not rigorously rejected")
        original_upper = original_decimal(mc["moment_upper_bound"])
        original_margin = original_decimal(mc["margin_lower_bound"])
        require(original_upper >= Fraction(high, SCALE) and original_margin == W - original_upper
                and original_margin > 0, "original conservative margin not supported")
        require(mc["passed"] is True and mc["next_grid_point_rejected"] is True, "original status flags")
        row = newexp["suppliers"][name]
        require(row["a"] == str(a) and row["theta"] == str(1-a) and row["m"] == m and row["W"] == W
                and row["deficit"] == c["deficit_per_vertex"] and row["max_child"] == max(hist)
                and row["commit"] == pin["commit"][:7], "original expected row metadata")
        records[name] = {"a": str(a), "theta": str(1 - a), "m": m, "W": W,
                         "rank": c["rank_per_vertex"], "deficit": c["deficit_per_vertex"],
                         "max_child": max(hist), "child_count": sum(hist.values()),
                         "histogram_sha256": sha256(canonical({str(r): n for r, n in hist.items()})),
                         "margin_interval_scaled": [W * SCALE - high, W * SCALE - low],
                         "next_grid": str(a + Fraction(1, 10**7)),
                         "next_excess_interval_scaled": [nextlow - W * SCALE, nexthigh - W * SCALE]}
        source_pins[parent] = {k: pin[k] for k in ("repository", "commit", "path", "sha256")}
    require(cap.used == set(cap.objects), "unconsumed capsule objects")
    return {"format": "pr225-five-stage-reconciliation-v1", "base": BASE, "reviewed_head": OLD,
            "current_head": NEW, "objects": len(cap.objects), "source_pins": source_pins,
            "scope": "Finite source/profile/moment reconciliation only; no external transfer proof or supplier rebuild.",
            "source_delta": {"added": added, "changed": changed, "unchanged": unchanged, "removed": removed},
            "inventories": {"reviewed": old, "current": new}, "framework_pins_not_reverified": src["framework"],
            "scale": SCALE, "log_terms": LOG_TERMS, "exp_terms": EXP_TERMS, "profiles": records}


def load(path=None):
    path = HERE / "sources.json.gz" if path is None else Path(path)
    return GitCapsule(json.loads(gzip.decompress(path.read_bytes())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = run(load())
    expected = HERE / "EXPECTED.json"
    if args.write_receipt:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    require(json.loads(expected.read_text()) == result, "complete receipt mismatch")
    print("PASS_PR225_FIVE_STAGE_RECONCILIATION profiles=6 added_profiles=2 next_points_rejected=6 source_files=19->23")


if __name__ == "__main__":
    main()
