#!/usr/bin/env python3
"""Bind each native warp event to its exact binary frame transport.

This is an additional prerequisite for a literal replay, not an endpoint,
Clifford-phase, chronology, or paid-profile verifier. Apache-2.0.
Prepared by 1337isnot1337 with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def span(basis):
    result = {0}
    for vector in basis:
        result |= {x ^ vector for x in tuple(result)}
    return frozenset(result)


def apply(columns, vector):
    result = 0
    for bit, column in enumerate(columns):
        if (vector >> bit) & 1:
            result ^= column
    return result


class WarpFrameAudit:
    """Nine-bit native frame prerequisite, independent of the legacy evaluator.

    For op > 0 require G_op(span(old)) = span(new). For op < 0
    require G_|op|(span(new)) = span(old), equivalent to the inverse
    transport because the constructor first checks that G is invertible.
    """

    def __init__(self, canonical):
        need(type(canonical.get("h")) is int and canonical["h"] == 9,
             "This audit requires the retained nine-bit native model")
        frames = canonical.get("frames")
        need(isinstance(frames, list) and frames, "Missing native frames")
        self.spaces = []
        for index, basis in enumerate(frames):
            need(isinstance(basis, list) and len(basis) <= 9,
                 f"Invalid frame basis {index}")
            need(all(type(x) is int and 0 <= x < 512 for x in basis),
                 f"Non-binary or out-of-range vector in frame {index}")
            space = span(basis)
            need(len(space) == 1 << len(basis), f"Dependent frame basis {index}")
            self.spaces.append(space)
        warps = canonical.get("warps")
        need(isinstance(warps, list), "Missing canonical warp table")
        self.maps = {}
        self.checked_classes = set()
        for warp in warps:
            op = warp["op"]
            need(type(op) is int and op > 0 and op not in self.maps,
                 "Warp operators must have distinct positive integer IDs")
            columns = warp["G_columns"]
            need(isinstance(columns, list) and len(columns) == 9 and
                 all(type(x) is int and 0 <= x < 512 for x in columns),
                 f"Invalid binary G columns for operator {op}")
            images = tuple(apply(columns, x) for x in range(512))
            need(len(set(images)) == 512, f"Singular G for operator {op}")
            self.maps[op] = images
        for warp in warps:
            self.check(warp["op"], warp["from_frame"], warp["to_frame"],
                       "canonical warp declaration")

    def check(self, operator, old, new, context="warp event"):
        need(type(operator) is int and operator != 0 and abs(operator) in self.maps,
             f"{context}: unknown or zero warp operator {operator!r}")
        for frame in (old, new):
            need(type(frame) is int and 0 <= frame < len(self.spaces),
                 f"{context}: invalid frame ID {frame!r}")
        key = (operator, old, new)
        if key in self.checked_classes:
            return
        source, target = (old, new) if operator > 0 else (new, old)
        images = self.maps[abs(operator)]
        actual = frozenset(images[x] for x in self.spaces[source])
        need(actual == self.spaces[target],
             f"{context}: G does not carry frame {old} to {new} "
             f"for signed operator {operator}")
        self.checked_classes.add(key)

    def program(self, program, direction="program"):
        count = 0
        for index, event in enumerate(program):
            need(isinstance(event, list) and event, f"{direction}[{index}]: invalid event")
            if event[0] == "warp":
                context = f"{direction}[{index}]"
                need(len(event) == 5, f"{context}: invalid warp event shape")
                _, role, operator, old, new = event
                self.check(operator, old, new, f"{context}, role {role!r}")
                count += 1
        return count


def audit(canonical, programs):
    checker = WarpFrameAudit(canonical)
    need(isinstance(programs, dict) and programs, "Missing native programs")
    counts = {direction: checker.program(program, direction)
              for direction, program in programs.items()}
    return {"operators": len(checker.maps), "warp_events": counts,
            "distinct_signed_frame_classes": len(checker.checked_classes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("canonical", type=Path)
    parser.add_argument("word", type=Path)
    args = parser.parse_args()
    result = audit(read_json(args.canonical), read_json(args.word))
    print(json.dumps({"status": "PASS_NATIVE_WARP_EVENT_FRAMES", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
