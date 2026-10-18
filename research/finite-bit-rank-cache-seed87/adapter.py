"""Opt-in repeated-transition cache for the pinned finite-bit checker.

Sagar Thakrar, with substantial OpenAI Codex assistance. Apache-2.0.
The loaded checker and its mathematics are Douglas R. Colkitt's retained work.
"""
from hashlib import sha256
from pathlib import Path
import sys
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'scripts/finite_bit_contract.py'
SOURCE_SHA256 = '3cff26a332cb6056f656b824e3a523fb8937d15206ddcc4118b911ac8df1b2a7'
BEFORE = '    costs = tuple(rank(sub(frames[v],frames[u])) for u,v,_ in edges)'
AFTER = '''    frame_ids = {}
    ids = [frame_ids.setdefault(frame, len(frame_ids)) for frame in frames]
    ranks = {}
    costs = []
    for u,v,_ in edges:
        key = (ids[u],ids[v])
        if key not in ranks:
            ranks[key] = rank(sub(frames[v],frames[u]))
        costs.append(ranks[key])'''


def checked_source(source, cached):
    if sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError('finite-bit checker source drift')
    text = source.decode('utf-8')
    if text.count(BEFORE) != 1:
        raise ValueError('expected exactly one edge-rank expression')
    return text.replace(BEFORE, AFTER) if cached else text


def load_checker(cached):
    """Load a separate module; leave files and other imported modules unchanged."""
    sys.path.insert(0, str(ROOT / 'scripts'))
    module = ModuleType('finite_bit_contract')
    module.__file__ = str(SOURCE)
    exec(compile(checked_source(SOURCE.read_bytes(), cached), str(SOURCE), 'exec'),
         module.__dict__)
    return module
