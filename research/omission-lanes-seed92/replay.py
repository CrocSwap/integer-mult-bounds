#!/usr/bin/env python3
"""Opt-in exact acceleration of PR1017's complete literal omission replay.

Apache-2.0. Sagar Thakrar, with substantial OpenAI Codex assistance.
The frozen checker certificate remains unchanged.

Production note: research/omission-lanes-production/ wires packed lanes into
production research/r439-omission-atlas-seed81/verify.py. This opt-in package
keeps a vendored literal baseline.py for reference-engine comparisons.
"""

from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ATLAS = ROOT / "research/r439-omission-atlas-seed81"
PRODUCTION = ATLAS / "verify.py"
BASELINE = HERE / "baseline.py"
SOURCE = "research/r439-omission-atlas-seed81/verify.py"
BATCH_SIZE = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packed_replays(gates, width, batch_size=BATCH_SIZE):
    """Yield every one-gate-omission map in chronological gate order."""
    require(type(width) is int and width > 0, "positive width required")
    require(type(batch_size) is int and batch_size > 0, "positive batch size required")
    mask = (1 << width) - 1
    for start in range(0, len(gates), batch_size):
        stop = min(start + batch_size, len(gates))
        repeated = ((1 << (width * (stop - start))) - 1) // mask
        rows = [repeated << i for i in range(width)]
        for k, (destination, source, _, __) in enumerate(gates):
            value = rows[source]
            if start <= k < stop:
                # XOR cannot carry across lanes; suppress just this lane's gate.
                value &= ~(mask << (width * (k - start)))
            rows[destination] ^= value
        for lane in range(stop - start):
            yield [(row >> (width * lane)) & mask for row in rows]


def load_checker(packed=True):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for pin in pins["files"]:
        usage = pin.get("usage", "input")
        if usage == "provenance":
            continue
        relative = pin["path"]
        raw = (ROOT / relative).read_bytes()
        require(sha256(raw).hexdigest() == pin["sha256"], "source pin mismatch: " + relative)
    require(sha256(BASELINE.read_bytes()).hexdigest() ==
            "127d7679fb26e264018548a1301b2f0f437d834eb1f0ffa215556243077ff866",
            "vendored baseline drift")

    if packed:
        # Keep this predecessor adapter bound to its hash-checked literal baseline.
        # Production equivalence is checked separately by omission-lanes-production;
        # never execute live production bytes under a provenance-only source pin.
        source = BASELINE.read_text(encoding="utf-8")
        replacements = (
            ("    atlas=factors(gates)\n",
             "    atlas=factors(gates)\n    mutants=packed_replays(gates,N)\n"),
            ("        changed=replay(gates,k)\n",
             "        changed=next(mutants,None)\n"
             "        need(changed is not None,\"missing literal omission replay\")\n"
             "        need(len(changed)==N,\"literal omission row coverage\")\n"),
            ("    # A singleton input in v's support activates exactly u.",
             "    need(next(mutants,None) is None,\"extra literal omission replay\")\n"
             "    # A singleton input in v's support activates exactly u."),
        )
        for before, after in replacements:
            require(source.count(before) == 1, "pinned replay integration changed")
            source = source.replace(before, after)
        module = ModuleType("omission_atlas")
        module.__file__ = str(PRODUCTION)
        module.packed_replays = packed_replays
        exec(compile(source, module.__file__, "exec"), module.__dict__)
        return module

    module = ModuleType("omission_atlas")
    module.__file__ = str(PRODUCTION)
    module.packed_replays = packed_replays
    exec(compile(BASELINE.read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def audit(packed=True):
    checker = load_checker(packed)
    result = checker.run()
    expected = (ATLAS / "CERTIFICATE.json").read_bytes()
    require(checker.canonical(result) == checker.canonical(checker.load(expected)),
            "complete predecessor certificate mismatch")
    return result


if __name__ == "__main__":
    audit()
    print("PASS_PACKED_OMISSION_REPLAY gates=5563 columns=661 lanes=16 controls=7 no_new_kappa")
