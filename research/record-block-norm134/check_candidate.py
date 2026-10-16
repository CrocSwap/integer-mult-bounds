# SPDX-License-Identifier: Apache-2.0
"""Replay the literal T134 allocation and exact paid moment, without a solver."""
import argparse
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
from verify_sources import HERE, ROOT, check, need, read, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    pins = check()
    claim = read(HERE/'CLAIM.json')
    previous = read(HERE/'PR2843-CLAIM.json')
    work = args.work.resolve() if args.work else Path(tempfile.mkdtemp(prefix='t134-independent-'))
    need(not work.is_relative_to(ROOT), 'external independent output')
    if args.work:
        need(not work.exists(), 'fresh output')
        work.mkdir(parents=True)
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1')
    env.pop('PYTHONOPTIMIZE',None)
    owner, moment = work/'OWNERS.json', work/'MOMENT.json'
    subprocess.run([sys.executable,'-B',str(HERE/'independent/owners.py'),
        '--replicas','134','--order',str(HERE/'data/ORDER.json'),'--fill',str(HERE/'data/FILL.json.gz'),
        '--dispatch',str(HERE/'data/DISPATCH.json'),'--profile',str(HERE/'data/PROFILE.json'),
        '--out',str(owner)],env=env,check=True)
    subprocess.run([sys.executable,'-B',str(HERE/'independent/moment.py'),
        '--owner-receipt',str(owner),'--best-claim',str(HERE/'PR2843-CLAIM.json'),
        '--out',str(moment)],env=env,check=True)
    o,m = read(owner),read(moment)
    need(o['status']=='PASS_INDEPENDENT_T_OWNER_CHRONOLOGY_MASKS' and len(o['controls'])==7,
         'independent owner coverage and faults')
    need((o['replicas'],o['roles'],o['live'],o['physical'])==(134,492048,120064,120554), 'literal complete stock')
    need(m['status']=='PASS_INDEPENDENT_EXACT_CANDIDATE_MOMENT' and len(m['controls'])==5,
         'exact moment and fault controls')
    need(Q(m['proposed_outer_target'])==Q(claim['kappa'])>Q(previous['kappa']), 'exact new headline')
    need(m['profile']==read(HERE/'data/PROFILE.json') and claim['replicas']==134, 'actual paid profile')
    need(check()==pins,'input/source drift during replay')
    result={'status':'PASS_INDEPENDENT_T134_ALLOCATION_AND_MOMENT','replicas':134,
            'kappa':claim['kappa'],'comparison_pr':2843,
            'owners_sha256':sha(owner),'moment_sha256':sha(moment),
            'geometry_faults':7,'moment_faults':5,
            'scope':'Finite independent allocation and exact moment. Full native/global/norm/outer release is separate.'}
    (work/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(result['status'])


if __name__=='__main__':
    main()
