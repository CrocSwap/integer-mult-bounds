#!/usr/bin/env python3
"""Reuse a parsed selected record when its source hash matches.

The cached pass skips JSON parsing and still hashes the bytes. A one-digit
change misses. Restoring the bytes hits. This is not the frontier replay.
"""

import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
RECORD = ROOT / "certificates/selected-result.json"
COVERAGE = ROOT / "scripts/verify_replay_coverage.py"
FRONTIER = ROOT / "scripts/verify_frontier1094.py"
MARKER = "PASS_SELECTED_RECORD_PARSE_CACHE cached_faster=true no_new_kappa"
ITERATIONS = 4000


def fail(message):
    raise SystemExit("FAIL_SELECTED_RECORD_PARSE_CACHE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "scripts/verify_replay_coverage.py",
        "scripts/verify_frontier1094.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


class ParseCache:
    def __init__(self):
        self.digest = None
        self.value = None
        self.hits = 0
        self.misses = 0

    def load(self, raw):
        digest = hashlib.sha256(raw).hexdigest()
        if digest == self.digest:
            self.hits += 1
            return self.value, True
        self.misses += 1
        self.digest = digest
        self.value = json.loads(raw)
        return self.value, False


def cold_seconds(raw):
    started = time.perf_counter()
    for _ in range(ITERATIONS):
        ParseCache().load(raw)
    return time.perf_counter() - started


def cached_seconds(raw):
    cache = ParseCache()
    started = time.perf_counter()
    for _ in range(ITERATIONS):
        cache.load(raw)
    return time.perf_counter() - started, cache


def mutate(raw):
    text = raw.decode()
    value = json.loads(raw)["decimal"]
    changed = value[:-1] + str((int(value[-1]) + 1) % 10)
    old = '"decimal": "%s"' % value
    require(text.count(old) == 1, "the decimal field moved")
    return text.replace(old, '"decimal": "%s"' % changed, 1).encode(), changed


def evaluate():
    authenticate()
    coverage = COVERAGE.read_text(encoding="utf-8")
    frontier = FRONTIER.read_text(encoding="utf-8")
    require("without reuse guesses" in coverage, "the reuse rule moved")
    require("Reuse requires the published reviewed receipt" in frontier, "the baseline reuse rule moved")
    raw = RECORD.read_bytes()
    fresh = json.loads(raw)
    # The live record is the payload; its bytes are a provenance pin, checked at base_commit by scripts/research_package.py.
    cache = ParseCache()
    first, hit = cache.load(raw)
    require(hit is False and first == fresh, "the first load did not parse")
    second, hit = cache.load(raw)
    require(hit is True and second == fresh, "the second load missed")
    changed, digit = mutate(raw)
    third, hit = cache.load(changed)
    require(hit is False and third["decimal"] == digit, "the changed record hit")
    restored, hit = cache.load(raw)
    require(hit is False and restored == fresh, "the restored record reused the changed parse")
    cold = cold_seconds(raw)
    warm, timed = cached_seconds(raw)
    require(timed.hits == ITERATIONS - 1 and timed.misses == 1, "the timed cache dropped a load")
    require(timed.value == fresh, "the timed cache value drifted")
    require(warm * 2 < cold, "the cached pass was not faster: cold %.4f cached %.4f" % (cold, warm))
    print("cold_seconds %.4f cached_seconds %.4f iterations %d" % (cold, warm, ITERATIONS))
    return {
        "iterations": ITERATIONS,
        "cached_faster": True,
        "hit_equals_fresh_parse": True,
        "changed_bytes_miss": True,
        "restored_bytes_reparsed": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
