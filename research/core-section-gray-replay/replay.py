#!/usr/bin/env python3
"""Complete PR3773 replay with an isolated Gray-code section enumerator.

Produced by Nick Petalas. Apache-2.0. James Reed / PR3773 supplies the
unchanged scientific consumer. Gray-code subset enumeration is classical.
"""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/core-section-capacity/verify.py"
OLD = "sections = Counter(sum(1 << index for index, coordinate in zip(members, local) if not ((mask & coordinate).bit_count() % 2)).bit_count() for mask in range(1, 128))"
NEW = "sections = gray_sections(local, dimension)"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gray_counts(coordinates, dimension):
    """Return every kernel-section size, indexed by its binary mask."""
    require(type(dimension) is int and 0 <= dimension <= 10,
            "dimension must be an integer in 0..10")
    require(type(coordinates) in (list, tuple) and len(coordinates) <= 256,
            "at most 256 coordinates are supported")
    require(all(type(value) is int and 0 <= value < 1 << dimension
                for value in coordinates), "coordinate outside binary space")
    columns = [sum(((value >> bit) & 1) << index
                   for index, value in enumerate(coordinates))
               for bit in range(dimension)]
    counts = [len(coordinates)] * (1 << dimension)
    odd = 0
    for step in range(1, 1 << dimension):
        bit = (step & -step).bit_length() - 1
        odd ^= columns[bit]
        mask = step ^ (step >> 1)
        counts[mask] = len(coordinates) - odd.bit_count()
    return tuple(counts)


def gray_sections(coordinates, dimension):
    return Counter(gray_counts(coordinates, dimension)[1:])


def authenticate(root=ROOT):
    """Authenticate every declared live input before executing any source."""
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = tuple(row for row in manifest["files"] if row["usage"] == "input")
    require(len(inputs) == 3, "the complete three-input binding is required")
    payloads = {}
    for row in inputs:
        path = root / row["path"]
        payload = path.read_bytes()
        require(sha256(payload).hexdigest() == row["sha256"],
                "source drift: " + row["path"])
        payloads[row["path"]] = payload
    return payloads


def load_consumer(engine="gray", root=ROOT):
    require(engine in ("original", "gray"), "unknown engine")
    payloads = authenticate(root)
    path = root / SOURCE
    text = payloads[SOURCE].decode("utf-8")
    require(text.count(OLD) == 1 and "gray_sections" not in text,
            "the isolated source adapter no longer matches")
    if engine == "gray":
        text = text.replace(OLD, NEW)
    module = ModuleType("_core_section_consumer")
    module.__file__ = str(path)
    module.gray_sections = gray_sections
    # Only authenticated predecessor source is compiled. Its __main__ guard
    # remains false; main() below still executes its full scientific consumer.
    exec(compile(text, str(path), "exec"), module.__dict__)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("original", "gray"), default="gray")
    args = parser.parse_args()
    load_consumer(args.engine).main()


if __name__ == "__main__":
    main()
