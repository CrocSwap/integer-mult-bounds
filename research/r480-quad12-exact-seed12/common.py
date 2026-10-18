"""Pinned inputs for the R480 quad12 experiment; Apache-2.0.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
"""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
BIT = "research/e8-bit-carrier-skeleton/code/bit"
REGS = [307, 355, 415, 439, 494, 518]
START, STOP, FRAME = 849, 872, 314


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def check_sources():
    pins = load(HERE / "SOURCES.json")
    for name, expected in {**pins["execution_inputs"], **pins.get("comparison_inputs", {})}.items():
        data = (ROOT / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == expected["sha256"], "source SHA256 mismatch: " + name)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == expected["git_blob"], "source Git blob mismatch: " + name)
    return pins


def original_word():
    check_sources()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    need((word["v"], word["R"], word["h"]) == (120, 480, 8), "wrong historical word")
    block = word["A"][START:STOP]
    need(len(block) == 23 and all(f == FRAME and len(ss) == 1 for f, _, ss in block), "source slice")
    need(sorted({r for _, d, ss in block for r in [d, *ss]}) == REGS, "source registers")
    return word
