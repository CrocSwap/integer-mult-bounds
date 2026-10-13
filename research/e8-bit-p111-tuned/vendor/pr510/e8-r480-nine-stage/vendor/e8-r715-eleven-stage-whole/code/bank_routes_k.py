"""Exact residual bank routes, generalised to bank width m (default 64 = PR #443).

Derived from PR #443's bank_routes.py by chafreaky (OpenAI Codex); `placement` takes the bank width m and the number of
replicas explicitly.  validate_isometries is unchanged and does not depend on the stage count.
Generalised by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
"""
import os, sys
from collections import deque
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../e8-r740-replica32/code'))
from tile_m import tile
from bank_routes import validate_isometries   # unchanged upstream function


def placement(widths, replicas=32, m=64):
    assert replicas > 0 and replicas % 8 == 0
    by_width = {}
    for rep in range(replicas):
        for helper, width in enumerate(widths):
            assert 0 < width <= 8
            by_width.setdefault(width, deque()).append((rep, helper))
    patterns = tile({w: len(q) for w, q in by_width.items()}, m)
    result = {}
    bank = 0
    for widths_in_bank, count in patterns:
        for _ in range(count):
            offset = 0
            for width in widths_in_bank:
                key = by_width[width].popleft()
                result[key] = (bank, offset, width)
                offset += width
            assert offset == m
            bank += 1
    assert all(not q for q in by_width.values())
    assert len(result) == replicas * len(widths)
    return result, bank
