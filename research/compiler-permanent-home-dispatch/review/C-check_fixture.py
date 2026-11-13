#!/usr/bin/env python3
"""Tiny independent control for the permanent-home fixture ABI and tariff."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

if not __debug__:
    raise SystemExit("optimized Python is unsupported: assertions are required")

TARGET = Path(__file__).resolve().parents[1] / 'tape_graph.py'
EXPECTED_SHA256 = "7d3cee3e79ba5fe410e1a6b5f4cf6a2fbe5e274f838b798cd8860344ff258b54"
actual_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
if actual_hash != EXPECTED_SHA256:
    raise SystemExit(f"tape_graph.py changed: {actual_hash}")

spec = importlib.util.spec_from_file_location("review_target_tape_graph", TARGET)
if spec is None or spec.loader is None:
    raise SystemExit("cannot load pinned tape_graph.py")
tg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tg)


def event(kind: str, service: str, owners: tuple[str, ...] = ()) -> SimpleNamespace:
    return SimpleNamespace(kind=kind, service=service, owners=owners, context=())


base = [
    event("allocate", "ZERO", ("O",)),
    event("native", "NOT", ("O",)),
    event("native", "XOR", ("A", "B")),
    event("release", "ZERO", ("O",)),
]
with_call_receipts = [event("call", "", ("A", "B", "O")), *base,
                      event("return", "", ("A", "B", "O"))]
owners = ("A", "B", "O")
reports = []

for events in (base, with_call_receipts):
    graph = tg.compile_graph(events, owners, productive_count=2)
    tapes = tg.initial_tapes(["010", "101"], home_count=3)
    initial_peaks = tuple(t.peak for t in tapes)

    first_steps = graph.run(tapes, limit=1_000_000)
    first = tg.decoded(tapes, 3)
    first_peaks = tuple(t.peak for t in tapes)

    second_steps = graph.run(tapes, limit=1_000_000, start=graph.execution_start)
    second = tg.decoded(tapes, 3)
    second_peaks = tuple(t.peak for t in tapes)

    assert first == ("010", "111", "000"), first
    assert second == ("010", "101", "000"), second
    assert first_peaks == second_peaks
    assert first_peaks[0] == 3 * (3 + 1) + 2
    assert first_peaks[1:] == (3 + 2, 3 + 2, 3 + 2)

    # R=4 services, B=2, O=1, K=3, b=2, F=3. The fixture's total
    # literal transition count (including its synthetic primitive graphs)
    # is below the claimed nonprimitive allowance alone.
    R, B, O, b, F = 4, 2, 1, 2, 3
    K = B + O
    nonprimitive_allowance = 16 * (R + 1) * (K + b + 1) * (F + 2)
    assert first_steps <= nonprimitive_allowance, (first_steps, nonprimitive_allowance)

    reports.append({
        "first_steps": first_steps,
        "second_steps": second_steps,
        "initial_peaks": initial_peaks,
        "retained_peaks": first_peaks,
        "nonprimitive_allowance": nonprimitive_allowance,
        "states": len(graph.rules),
    })

assert reports[0]["first_steps"] == reports[1]["first_steps"]
assert reports[0]["second_steps"] == reports[1]["second_steps"]

# ABI boundary: origin is the '^' cell at relative zero, data starts to its
# right, and the Tape implementation rejects relative origin-1 access.
packet = tg.initial_tapes(["010"], home_count=1)[0]
assert packet.contents() == "^010|$"
try:
    tg.Tape().move(-1)
except ValueError as exc:
    assert "crossed permanent origin" in str(exc)
else:
    raise AssertionError("relative origin-1 movement unexpectedly allowed")

print("PASS_COMPILER_DISPATCH_FIXTURE", reports)
print("ABI_PACKET=^010|$; origin_minus_one=rejected")
