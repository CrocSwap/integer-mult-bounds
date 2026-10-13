#!/usr/bin/env python3
"""Verify terminal elimination on #144's bit word from the pinned sources (Python stdlib only; about 5 minutes).

  1. #144 control: scripts/paired_cube_network.py's own functions reproduce #144's coarse bit saving 4617656/10^10,
     stopped saving 4613422943/10^13 and kappa 4609169/10^10 exactly (largest grid points, next points rejected);
  2. exact frames rebuilt from the pinned PR97 witness (Swapnil Jain's check_lifted.py machinery; no cache);
  3. the elimination plan is regenerated (per target, the best exactly nested subset) and equals plan.json;
  4. the reduced bit row is regenerated (paired_cube_bit.reconstruct() arithmetic) and equals row-elim.json;
  5. literal scalar replay of the reduced word over Z (exact integer coefficients) and F2 with arbitrary scratch and
     data; tamper controls (missing redirected update, sign flip) rejected;
  6. #144's own assembly on the reduced row: kappa 4646633/10^10 with the next grid point rejected.
Usage: python3 research/bit-elim-144/verify.py"""
import gzip
import json
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
def log(*a): print('[%5.0fs]' % (time.time() - T0), *a, flush=True)


def run(*args):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=1800)
    if p.returncode: raise SystemExit('FAIL %s\n%s\n%s' % (args[0], p.stdout[-3000:], p.stderr[-3000:]))
    return p.stdout


def main():
    assert not sys.flags.optimize, 'run without -O'
    import price144
    from paired_cube_bit import reconstruct
    r0 = price144.price(reconstruct())
    assert (r0['coarse'], r0['stopped'], r0['kappa']) == (Q(4617656, 10**10), Q(4613422943, 10**13), Q(4609169, 10**10)), r0
    log('PASS #144 control: coarse 4617656/10^10, stopped 4613422943/10^13, kappa 4609169/10^10 (next rejected)')
    with tempfile.TemporaryDirectory(prefix='bit-elim-144-') as tmp:
        tmp = Path(tmp)
        log(run(HERE / 'frames144.py', tmp / 'frames.json.gz').strip())
        log(run(HERE / 'elim144.py', tmp / 'frames.json.gz', tmp / 'plan.json').strip())
        assert json.loads((tmp / 'plan.json').read_text()) == json.loads((HERE / 'plan.json').read_text()), 'plan differs'
        log('PASS regenerated plan equals plan.json (every accepted target chain nested exactly over Q)')
        run(HERE / 'row144.py', HERE / 'plan.json', tmp / 'row.json')
        assert json.loads((tmp / 'row.json').read_text()) == json.loads((HERE / 'row-elim.json').read_text()), 'row differs'
        log('PASS regenerated reduced row equals row-elim.json')
        log(run(HERE / 'replay144.py', HERE / 'plan.json').strip().replace('\n', ' | '))
    r = price144.price(json.loads((HERE / 'row-elim.json').read_text()))
    assert r['kappa'] == Q(4646633, 10**10) and r['coarse'] == Q(4655227, 10**10), r
    log('PASS kappa %s = %.10e (next %s rejected); coarse %s, stopped %s, R %d, W %d' % (
        r['kappa'], float(r['kappa']), r['kappa_next_rejected'], r['coarse'], r['stopped'], r['R'], r['W_per_vertex']))


if __name__ == '__main__':
    main()
