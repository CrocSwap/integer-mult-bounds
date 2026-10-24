#!/usr/bin/env python3
"""Endpoint-frame audit of PR #4596 (DaysSky): the quotient of PR4470's word by span{511}.

#4596 (head 406aae34; QUOTIENT-WORD.json.gz vendored, blob 5bc2bdaf, sha256-pinned) applies
phi(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0), kernel span{511}, to every frame of PR4470's word, pads one helper's
final frame by the ninth axis, and prices the result as a block-8 supplier (complex kappa 0.0121, outer 0.0034).

This verifier compares the submitted word's main-field output frames with PR4470's, from main's pinned #4470
constructor (research/joint-helper-lattice/native_joint.py, run isolated), and records how the shipped literal replay
treats final frames:
  * PR4470: the 112 main roles 0-111 end in the full nine-axis frame F2^9; roles 112-223 end in 112 distinct
    hyperplanes, none containing 511;
  * #4596: all 224 main roles end in one and the same frame, the low-8-bit space F2^8; no main role reaches F2^9;
    the only role whose final frame is F2^9 is helper 224 (the pad_ambient extension); every main final frame differs
    from PR4470's;
  * phi maps every dimension-8 subspace avoiding 511 onto F2^8 and maps F2^9 onto F2^8 as well, which is why the 224
    distinct output charts collapse to one;
  * the pinned verify_buffers.py compares a replay's final frames with the submitted word's own canonical["final"]
    (its line 207) and its expected() rows carry no frame argument (logical scalar endpoints only), so the literal
    replay is satisfied by a word that changes every main field's output chart.
If the native supplier must deliver each main field in PR4470's required chart (the kernel on every live array), the
quotient word does not, and its smaller paid profile does not price the same operator. No kappa is claimed here.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = HERE / "PR4596-QUOTIENT-WORD.json.gz"
WORD_SHA256 = "42bd7fb0c27d859a8731ef3d6f5f1d05daff77f3cc0dcae8ef16f0670b1815f6"
REPLAY = ROOT / "research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def span(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    return frozenset(s)


def phi(v):
    return (v & 0xFF) ^ (0xFF if v & 0x100 else 0)


def main():
    raw = WORD.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "vendored #4596 QUOTIENT-WORD")
    q = json.loads(gzip.decompress(raw))
    with tempfile.TemporaryDirectory(prefix="audit-cache-") as cache:
        code = ("import json,sys;sys.path.insert(0,sys.argv[1]);import native_joint;"
                "c,p,b,o,n=native_joint.construct();print(json.dumps({'c':c}))")
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache, "-c", code,
                              str(ROOT / "research/joint-helper-lattice")], capture_output=True, check=True, timeout=120)
    c = json.loads(run.stdout)["c"]
    full, low8 = frozenset(range(512)), frozenset(range(256))
    orig = [span(c["frames"][c["final"][r]]) for r in range(224)]
    quot = [span(q["frames"][q["final"][r]]) for r in range(224)]
    need(all(orig[r] == full for r in range(112)), "PR4470: mains 0-111 end in F2^9")
    hyper = orig[112:]
    need(all(len(f) == 256 and 511 not in f for f in hyper) and len(set(hyper)) == 112,
         "PR4470: mains 112-223 end in 112 distinct hyperplanes avoiding 511")
    need(all(f == low8 for f in quot), "#4596: all 224 mains end in the same low-8-bit frame F2^8")
    need(all(orig[r] != quot[r] for r in range(224)), "#4596: every main output frame differs from PR4470's")
    at_full = [r for r in range(len(q["final"])) if span(q["frames"][q["final"][r]]) == full]
    need(at_full == [224], "#4596: only helper 224 (the padded one) ends in F2^9")
    need(phi(511) == 0 and {phi(v) for v in full} == set(range(256)), "phi has kernel span{511}, image F2^8")
    need(all({phi(v) for v in f} == set(range(256)) for f in hyper), "phi maps every 511-free hyperplane onto F2^8")
    src = REPLAY.read_text(encoding="utf-8").splitlines()
    need('[current["L", i] for i in range(n)] == canonical["final"]' in src[206], "replay checks the word's own finals")
    need(any(line.startswith("def expected(role, R, backward, clean):") for line in src), "expected() has no frame input")
    print(json.dumps({"status": "PASS_PR4596_ENDPOINT_FRAME_AUDIT",
                      "pr4470_main_finals": {"full_F2^9": 112, "distinct_hyperplanes": 112},
                      "pr4596_main_finals": {"single_frame_low8": 224, "full_F2^9": 0},
                      "main_output_frames_changed": 224, "roles_at_full_ambient_in_4596": at_full,
                      "replay_checks_own_finals_only": True, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
