#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent original-bin DP and on-disk failure/relocation controls."""
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def load_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def independent_mixed_dp():
    """No PART/policy/Bellman import: enumerate original mixed-width bin fills."""
    source = ROOT / 'research/native-complex-moment552/engines/base_two_moment.py'
    source_rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    pin = next(r['sha256'] for r in source_rows if r['path'] == str(source.relative_to(ROOT)))
    require(hashlib.sha256(source.read_bytes()).hexdigest() == pin, 'independent engine pin')
    engine = load_file(source, 'independent_base_two')
    scale = 10**25
    g = {0: (0, 0)}
    for r in range(1, 43):
        l, h = engine.log_bounds(Q(64, r))
        lo = r * engine.exp_bounds(l / 1000)[0]
        hi = r * engine.exp_bounds(h / 1000)[1]
        g[r] = ((lo * scale).__floor__(), (hi * scale).__ceil__())
    # Three bins of each capacity. At most three width7 and 27 width8 roles.
    # Store every original-bin mixture, without a move-to-seven reduction.
    states = {(0, 0): (0, 0, (0,) * 43)}
    transitions = 0
    for c in (7, 14, 28, 42) * 3:
        next_states = {}
        for (used7, used8), (lo, hi, profile) in states.items():
            for a in range(min(c // 7, 3 - used7) + 1):
                for b in range(min((c - 7 * a) // 8, 27 - used8) + 1):
                    r = c - 7 * a - 8 * b
                    p = list(profile)
                    if r:
                        p[r] += 1
                    p = tuple(p)
                    item = (lo + g[r][0], hi + g[r][1], p)
                    key = (used7 + a, used8 + b)
                    old = next_states.get(key)
                    transitions += 1
                    if old is None or item[1] < old[0]:
                        next_states[key] = item
                    elif old[1] < item[0] or old[2] == item[2]:
                        pass
                    else:
                        raise ValueError('independent DP comparison inconclusive')
        states = next_states
    checked = 0
    # State s<=14 has at most two empty42 bins and one partial, so it fits.
    # Expected formula is written directly; the production policy is not imported.
    for n7 in range(4):
        for slack in range(15):
            q, rem = divmod(slack, 5)
            p = [0] * 43
            p[7] = 3 - n7
            p[6] = 3
            p[4] = 3
            p[2] = 3 - q
            p[42] = q
            if rem == 1:
                p[6] -= 1; p[14] += 1
            elif rem == 2:
                p[4] -= 1; p[20] += 1
            elif rem == 3:
                p[4] -= 1; p[28] += 1
            elif rem == 4:
                p[2] -= 1; p[34] += 1
            require(states[n7, 27 - slack][2] == tuple(p), 'independent mixed-bin optimum')
            checked += 1
    return {'mixed_states_compared': checked, 'transitions': transitions,
            'scope': 'three bins per capacity; 0..3 width7 roles, slack0..14; a=1/1000'}


def command(root, expected, marker, optimized=False):
    argv = [sys.executable, '-I'] + (['-O'] if optimized else [])
    argv += ['-B', str(root / 'research/bit-partial-width7-optimum/verify.py')]
    proc = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=120)
    require((proc.returncode == 0) == expected and marker in proc.stdout + proc.stderr,
            'subprocess control failed: ' + proc.stdout + proc.stderr)


def main():
    print(json.dumps(independent_mixed_dp(), sort_keys=True))
    with tempfile.TemporaryDirectory(prefix='partial width7 independent ') as directory:
        root = Path(directory)
        target = root / 'research/bit-partial-width7-optimum'
        shutil.copytree(HERE, target)
        rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
        for row in rows:
            if row['usage'] == 'input':
                dst = root / row['path']
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], dst)
        command(root, True, 'PASS_BIT_PARTIAL_WIDTH7_OPTIMUM', optimized=True)
        record = root / 'research/e8-bit-p111-tuned/tune/EXPECTED.json'
        saved = record.read_bytes()
        record.write_bytes(saved + b' ')
        command(root, False, 'source pin')
        record.write_bytes(saved)
        expected = target / 'EXPECTED.json'
        saved = expected.read_bytes()
        changed = json.loads(saved)
        changed['cases'][2]['idle']['28'] -= 1
        expected.write_text(json.dumps(changed))
        command(root, False, 'committed evidence mismatch')
        expected.write_bytes(saved)
        expected.unlink()
        command(root, False, 'FileNotFoundError')
    print('PASS_BIT_PARTIAL_WIDTH7_PACKAGE independent_mixed_states=60 disk_controls=3 relocated_optimized=1')


if __name__ == '__main__':
    main()
