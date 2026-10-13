"""Replay these three research subtrees without modifying checkout receipts.

All generators run in an isolated copy of the package. Coordinate NPZ inputs
are regenerated, JSON is compared structurally, and the saved factor NPZ is
compared by array contents. Timing metadata is deliberately not certified.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

PACKAGE = Path(__file__).resolve().parents[2]

# Dependency order is intentional. hybrid_sections imports hybrid and therefore
# regenerates HYBRID.json too. clique_rank completes the leading-search receipt.
REPLAYS = (
    ('bit-routes/mod4_rank.py', ('MOD4-RANK.json',)),
    ('bit-routes/d16_rank.py', ('D16-RANK.json',)),
    ('bit-routes/mixed_rank.py', ('MIXED-ORBIT-RANKS.json',)),
    ('bit-routes/section_ranks.py', ('D16-SECTIONS.json',)),
    ('bit-routes/neighbor_cubics.py', ('NEIGHBOR-CUBICS.json',)),
    ('bit-routes/cubic_relations.py', ('CUBIC-RELATIONS.json',)),
    ('bit-routes/spinor_operator.py', ('SPINOR-OPERATOR.json',)),
    ('bit-routes/clique_residual.py', ('CLIQUE-RESIDUAL.json',)),
    ('bit-routes/clique_residual_support.py', ('CLIQUE-RESIDUAL-SUPPORT.json',)),
    ('continuation/section-search/sections.py', ('SECTIONS.json',)),
    ('continuation/section-search/hybrid_sections.py', ('HYBRID.json', 'HYBRID-SECTIONS.json')),
    ('continuation/spinor-routes/frame_bounds.py', ('FRAME-BOUNDS.json',)),
    ('continuation/spinor-routes/cross_rank.py', ('CROSS-RANK.json',)),
    ('continuation/spinor-routes/cross_factor.py', ('CROSS-FACTOR.json', 'CROSS-FACTOR.npz')),
    ('continuation/spinor-routes/clique_leading.py', ()),
    ('continuation/spinor-routes/clique_rank.py', ('CLIQUE-LEADING.json',)),
    ('continuation/spinor-routes/clique_small.py', ('CLIQUE-SMALL.json',)),
    ('continuation/spinor-routes/clique_half.py', ('CLIQUE-HALF.json',)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare_receipt(expected, actual):
    require(actual.is_file(), f'Missing regenerated receipt: {actual.name}')
    if expected.suffix == '.npz':
        with np.load(expected, allow_pickle=False) as left, np.load(actual, allow_pickle=False) as right:
            require(set(left.files) == set(right.files), f'NPZ keys differ: {expected.name}')
            for key in left.files:
                require(np.array_equal(left[key], right[key]), f'NPZ array differs: {expected.name}:{key}')
        return
    left = json.loads(expected.read_text())
    right = json.loads(actual.read_text())
    if expected.name == 'MOD4-RANK.json':
        left.pop('seconds', None)
        right.pop('seconds', None)
    require(left == right, f'Regenerated receipt differs: {expected}')


def replay(isolated_package, frozen_package=PACKAGE, optimized=False):
    """Replay in an already isolated package copy and return checked paths.

    The caller must supply distinct directories. This hook permits a top-level
    package verifier to reuse its own temporary workspace.
    """
    isolated_package = Path(isolated_package).resolve()
    frozen_package = Path(frozen_package).resolve()
    require(isolated_package != frozen_package, 'Replay must use an isolated package copy')
    checked = []
    for relative, outputs in REPLAYS:
        script = isolated_package / 'workbench' / relative
        command = [sys.executable, '-I']
        if optimized:
            command.append('-O')
        command.append(str(script))
        start = time.monotonic()
        completed = subprocess.run(command, cwd=isolated_package, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        require(completed.returncode == 0,
                f'{relative} failed:\n{completed.stdout[-6000:]}')
        directory = Path(relative).parent
        for name in outputs:
            path = Path('workbench') / directory / name
            compare_receipt(frozen_package / path, isolated_package / path)
            checked.append(str(path))
        print(f'PASS {relative} ({time.monotonic()-start:.1f}s)', flush=True)
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimized', action='store_true',
                        help='Run generators with -I -O (also inherited from this interpreter)')
    args = parser.parse_args()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='niemeier-bit-replay-') as temporary:
        isolated = Path(temporary) / 'niemeier-lattices'
        shutil.copytree(PACKAGE, isolated,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        checked = replay(isolated, optimized=args.optimized or bool(sys.flags.optimize))
    print(json.dumps({'status': 'PASS', 'compared_receipts': len(checked),
                      'coordinate_inputs': 'regenerated',
                      'elapsed_seconds': round(time.monotonic()-started, 2),
                      'frozen_checkout_modified': False}, indent=2))


if __name__ == '__main__':
    main()
