#!/usr/bin/env python3
"""Create isolated pinned source closures; never copy caches or private records."""
from common import *
import shutil


def prepare(complex_root, bit_root, output):
    check_sources(complex_root, bit_root)
    prepared = output / 'sources'
    prepared.mkdir()
    roots = []
    for kind, source in [('complex', complex_root), ('bit', bit_root)]:
        target = prepared / kind
        target.mkdir()
        for name, expected in source_pins(kind).items():
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)
            assert sha(destination) == expected
        check_source(target, kind)
        roots.append(target)
    return tuple(roots)
