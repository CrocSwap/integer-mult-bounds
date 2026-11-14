"""Separate exact arithmetic, packing, and executed source-binding controls."""
from fractions import Fraction as Q
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pair(a, b):
    x = (*a, *b)
    rows = ((1, -1, 1, 1), (1, 1, -1, 1),
            (1, 1, 1, -1), (-1, 1, 1, 1))
    y = [sum(Q(c)*v for c, v in zip(row, x))/2 for row in rows]
    return (y[0], y[1]), (y[2], y[3])


def axis(values, bit):
    out = list(values)
    for j in range(len(values)):
        if not j & (1 << bit):
            out[j], out[j | (1 << bit)] = pair(values[j], values[j | (1 << bit)])
    return out


def main():
    entrance = [(Q(v), Q(0)) for v in (1, 0, 0, 1)]
    expected = [(Q(v), Q(0)) for v in (0, 1, 1, 0)]
    for order in ((0, 1), (1, 0)):
        middle = axis(entrance, order[0])
        need(any(v.denominator != 1 for z in middle for v in z),
             'endpoint-only admission must fail at first axis')
        need(axis(middle, order[1]) == expected, 'two-axis exact endpoint')
    overflow = pair((Q(3), Q(-3)), (Q(3), Q(3)))
    need(overflow == ((Q(6), Q(0)), (Q(0), Q(0))), 'exact width control')
    need(any(not -4 <= v <= 3 for z in overflow for v in z),
         'integrality alone must not imply signed width admission')
    packing_trials = 0
    for f, step, offset in ((1, 2, 0), (2, 2, 1), (3, 3, 1)):
        prefix = 2
        nbits = prefix + 9*f*step + 1
        selected = [prefix+(i*f+j)*step+offset for i in range(9) for j in range(f)]
        permutation = list(range(prefix))+selected+[
            k for k in range(prefix, nbits) if k not in selected]
        need(sorted(permutation) == list(range(nbits)), 'complete bijection')
        for seed in range(5):
            original = [(k*k+seed*k+seed//2) % 2 for k in range(nbits)]
            packed = [original[k] for k in permutation]
            restored = [None]*nbits
            for j, k in enumerate(permutation):
                restored[k] = packed[j]
            need(restored == original, 'inverse preserves every spectator bit')
            for i in range(9):
                chunk = packed[prefix+i*f:prefix+(i+1)*f]
                value = sum(x << (f-1-j) for j, x in enumerate(chunk))
                for bit in range(f):
                    need((value >> bit) & 1 == original[selected[i*f+f-1-bit]],
                         'uniform tensor-column reversal')
            packing_trials += 1
        for width in (2, 7, 40):
            old = 3*(1 << nbits)*6*2*(width+1)
            new = 2*3*(1 << nbits)*2*width
            need(Q(old, new) == Q(3*(width+1), width) and old > new,
                 'header-only cardinality mismatch')
    mutations = []
    with tempfile.TemporaryDirectory(prefix='selected-grid-controls-') as tmp:
        copied = Path(tmp)/'package'
        shutil.copytree(HERE, copied, ignore=shutil.ignore_patterns('__pycache__'))
        for relative in ('inputs/WORD.json.gz', 'inputs/literal-leaf-contract.md'):
            target = copied/relative
            original = target.read_bytes()
            changed = bytearray(original)
            changed[len(changed)//2] ^= 1
            target.chmod(0o600)
            target.write_bytes(changed)
            for optimized in (False, True):
                argv = [sys.executable, '-I', '-B']
                if optimized:
                    argv.append('-O')
                done = subprocess.run(argv+[str(copied/'verify.py')],
                                      capture_output=True, timeout=20)
                need(done.returncode != 0 and b'exact bundled SHA256' in done.stderr,
                     'actual source-binding verifier rejects changed bytes')
                need(b'PASS_' not in done.stdout, 'mutant cannot emit acceptance')
                mutations.append({'source': relative, 'optimized': optimized,
                                  'rejected_at_source_binding': True})
            target.write_bytes(original)
    print(json.dumps({'status': 'PASS_INDEPENDENT_SELECTED_GRID_CONTROLS',
                      'exact_axis_orders': 2, 'signed_width_rejection': True,
                      'packing_roundtrips': packing_trials,
                      'cardinality_cases': 9, 'source_mutations': mutations,
                      'scope': 'Independent finite controls, not a literal machine replay or universal proof.'},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
