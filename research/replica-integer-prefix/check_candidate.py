#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent literal-owner and directed-rational moment replay (no solver)."""
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from verify_sources import HERE, ROOT, check, need, read, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertions enabled')
    pins = check()
    claim = read(HERE/'CLAIM.json')
    if args.work:
        work = args.work.resolve()
        need(not work.exists() and not work.is_relative_to(ROOT), 'fresh external output')
        work.mkdir(parents=True)
    else:
        work = Path(tempfile.mkdtemp(prefix='replica-integer-prefix-independent-'))
        need(not work.is_relative_to(ROOT), 'external temporary output')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE', None)
    owner, moment = work/'INDEPENDENT-OWNERS.json', work/'INDEPENDENT-MOMENT.json'
    subprocess.run([sys.executable, '-B', str(HERE/'independent/owners.py'),
        '--replicas', str(claim['replicas']), '--order', str(HERE/'data/ORDER.json'),
        '--fill', str(HERE/'data/FILL.json.gz'), '--dispatch', str(HERE/'data/DISPATCH.json'),
        '--profile', str(HERE/'data/PROFILE.json'), '--out', str(owner)], env=env, check=True)
    subprocess.run([sys.executable, '-B', str(HERE/'independent/moment.py'),
        '--owner-receipt', str(owner), '--out', str(moment)], env=env, check=True)
    o, m = read(owner), read(moment)
    need(o['status'] == 'PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS' and len(o['controls']) == 7,
         'complete independent geometry controls')
    need(m['status'] == 'PASS_INDEPENDENT_EXACT_CANDIDATE_MOMENT' and len(m['controls']) == 5,
         'complete independent exact moment controls')
    need(o['roles'] == 455328 and o['live'] == 111104 and o['physical'] == 111594,
         'literal stock and complete role coverage')
    need(Fraction(m['proposed_outer_target']) == Fraction(claim['kappa']) and
         m['profile'] == read(HERE/'data/PROFILE.json'), 'exact package target and paid profile')
    cap = work/'P33-PACKING-CAP.json'
    subprocess.run([sys.executable, '-I', '-S', '-B', str(HERE/'packing/verify.py'),
        '--owner', str(owner), '--moment', str(moment), '--out', str(cap)], env=env, check=True)
    need(read(cap) == read(HERE/'evidence/P33-PACKING-CAP.json'), 'exact independent packing cap')
    need(check() == pins, 'no source or package drift')
    result = dict(status='PASS_INDEPENDENT_INTEGER_PREFIX_CANDIDATE',
        owners_sha256=sha(owner), moment_sha256=sha(moment),
        geometry_controls=7, moment_controls=5, packing_cap_sha256=sha(cap), source_bindings=pins,
        scope='Finite actual-word algebra, complete literal geometry and exact moment only. Full native/global/outer release is reproduce.py.')
    (work/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    print(result['status'], str(work), flush=True)


if __name__ == '__main__':
    main()
