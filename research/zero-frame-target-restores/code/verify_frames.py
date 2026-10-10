#!/usr/bin/env python3
"""Independently validate exact bases and annihilators of every candidate frame."""
import argparse
import hashlib
import json
from pathlib import Path
from sympy import Matrix, eye, ones, zeros

if not __debug__:
    raise SystemExit("assertions are required")


def validate(frame):
    d = frame["dim"]
    assert type(d) is int and 0 <= d <= 24
    b, a = frame["B"], frame["A"]
    assert len(b) == d and len(a) == 24-d
    assert all(len(row) == 24 and all(type(x) is int for x in row) for row in b+a)
    B = Matrix(b) if b else zeros(0, 24)
    A = Matrix(a) if a else zeros(0, 24)
    assert B.rank() == d and A.rank() == 24-d
    assert B*A.T == zeros(d, 24-d)
    assert (B*(9*eye(24)-ones(24))*B.T).det() != 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    raw = args.frames.read_bytes()
    frames = json.loads(raw)
    seen = set()
    for frame in frames.values():
        key = json.dumps(frame, sort_keys=True)
        if key not in seen:
            validate(frame)
            seen.add(key)
    result = dict(status="PASS_EXACT_BASES_ANNIHILATORS_AND_GRAM",
                  frames_checked=len(frames), distinct_frames_checked=len(seen),
                  frames_sha256=hashlib.sha256(raw).hexdigest())
    assert not args.output.exists()
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
