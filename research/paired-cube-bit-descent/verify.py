#!/usr/bin/env python3
"""Independent finite frame-word, formal-column, prime and paid-moment audit.

Search reproduction is optional: the exported basis plan is checked directly.
Apache-2.0; prepared with OpenAI Codex.
"""
import argparse
import copy
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import word
from moment import certify,paid_moment,js
from prime_check import certificate as primes

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

def digest(path):return sha256(path.read_bytes()).hexdigest()

def build(root):
    word.BASE=root/'research/paired-cube-bit'
    plan=json.loads((HERE/'frames.json').read_text())
    initial=json.loads((HERE/'initial.json').read_text())
    assert plan['provenance']['initial_sha256']==digest(HERE/'initial.json')
    print('Checking exact operation frames and every physical and target chain.',file=sys.stderr,flush=True)
    c=word.Candidate(plan=plan);c.exact_frames();row=c.row()
    assert row['changed_operation_frames']==len(plan['frames']) and row['reused_registers']==0
    # Recount the initial plan in the same checked source word. The generalized
    # loader intentionally permits ascent, but every actual local chain must pass.
    base=word.Candidate(plan=initial);base.exact_frames();before=base.row()
    prior=certify(before)
    print('Checking every F2 and integer source, target and dirty-register column.',file=sys.stderr,flush=True)
    formal=[c.formal(r) for r in (2,0)];controls=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError):controls.append(name)
        else:raise ValueError('Adverse control accepted: '+name)
    for tamper in ('omit_compensation','missing_partner'):
        reject(tamper,lambda t=tamper:c.formal(2,t))
    i=c.changed_frames[0];saved=c.opframe[i]
    c.opframe[i]=c.register([]);reject('zero_operation_frame',c.exact_frames);c.opframe[i]=saved
    # A full frame at a point with a proper successor must violate nesting.
    target=next(j for j in c.changed_frames if any(k>j and
        (c.ops[k][0] in c.ops[j][:2] or c.ops[k][1] in c.ops[j][:2]) and
        c.C.dimf[c.opframe[k]]<c.h for k in range(j+1,min(len(c.ops),j+100))))
    saved=c.opframe[target];c.opframe[target]=c.w['full_frame']
    reject('past_successor_frame',c.row);c.opframe[target]=saved
    duplicate=copy.deepcopy(plan);duplicate['frames'].append(duplicate['frames'][0])
    reject('duplicate_operation_record',lambda:word.Candidate(plan=duplicate))
    bad_index=copy.deepcopy(plan);bad_index['frames'][0][0]=-1
    reject('negative_operation_index',lambda:word.Candidate(plan=bad_index))
    malformed=copy.deepcopy(plan);malformed['frames'][0][1][0][0]=True
    reject('boolean_basis_coefficient',lambda:word.Candidate(plan=malformed))
    print('Factoring all new Gram determinants and certifying the complete paid moment.',file=sys.stderr,flush=True)
    prime=primes(HERE/'frames.json');moment=certify(row)
    assert prime['total_operation_frames']==len(plan['frames'])
    assert moment['coarse_saving']>prior['coarse_saving']
    assert moment['ordinary_saving']>prior['ordinary_saving']
    p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,
        total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
    assert paid_moment(p,prior['coarse_saving'])['upper']<prior['accepted']['lower']
    return js(dict(status='PASS conditional finite frame improvement',profile=row,initial_profile=before,
        formal=formal,controls=controls,prime_witnesses=prime,paid_moment=moment,initial_paid_moment=prior,
        scope='Finite physical frames, exact source/target/dirty-column replay, determinant factors, full fallback and atom toll. All inherited all-size and assembly contracts remain assumptions. No final kappa is claimed by this module.'))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,default=HERE.parents[1])
    ap.add_argument('--write',action='store_true');ap.add_argument('--reproduce-search',action='store_true');args=ap.parse_args()
    assert not sys.flags.optimize
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    check=lambda:{p:digest(args.source/p) for p in manifest['files']}
    before=check();assert before==manifest['files'],'Pinned source drift'
    if args.reproduce_search:
        subprocess.run([sys.executable,'-B',str(HERE/'search.py'),'--source',str(args.source)],check=True)
    record=build(args.source);target=HERE/'certificate.json'
    if args.write:target.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:assert record==json.loads(target.read_text()),'Canonical frame certificate changed'
    assert check()==before,'Pinned source changed during verification'
    print('PASS finite frame improvement; coarse='+str(record['paid_moment']['coarse_saving'])+
          '; ordinary='+str(float(Q(record['paid_moment']['ordinary_saving']))))

if __name__=='__main__':main()
