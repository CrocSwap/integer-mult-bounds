#!/usr/bin/env python3
"""Replay the source-bound T530 outer arithmetic on the retimed profile.
Retains the PR1673/1786/2180 and T530 source notices. Arithmetic is separate
from global controller admission and all-size/physical hypotheses.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,subprocess,sys

def need(x,m):
 if not x:raise ValueError(m)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--t530',type=Path,required=True);p.add_argument('--moment',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();need(not a.out.exists(),'fresh output');a.out.mkdir();(a.out/'outer').mkdir();(a.out/'new').mkdir()
 raw=a.repo/'research/gmx-t74-borrow43-handoff/outer/check_ledger.py'
 patch=next(x for x in read(a.t530/'evidence/RESULT.json')['patches'] if x['path']=='outer/check_ledger.py')
 need(sha(raw)==patch['before_sha256'],'retained checker source')
 text=raw.read_text()
 for before,after in patch['replacements']:
  need(text.count(before)==1,'unique authorized T530 dimension generalization');text=text.replace(before,after)
 need(hashlib.sha256(text.encode()).hexdigest()==patch['after_sha256'],'same T530 checker')
 (a.out/'outer/check_ledger.py').write_text(text)
 inp=a.repo/'research/gmx-t74-borrow43-handoff/outer/independent_check.py';(a.out/'outer/independent_check.py').write_bytes(inp.read_bytes())
 m=read(a.moment);C=Q(m['root_interval'][0]);K=Q(m['candidate_modern_kappa']);old=read(a.t530/'EXPECTED.json')['candidate_endpoint']
 save(a.out/'new/SPEC.json',dict(geometry=dict(dimension=73,replicas=m['replicas']),expected=dict(complex_lower=str(C),kappa=old,global_profile=m['new_profile'],live=m['live']),outer_refinement=dict(endpoint_digits=24)))
 save(a.out/'CLAIM.json',dict(kappa=str(K),scope='Conditional retimed candidate; global controller admission separate'))
 save(a.out/'outer/B.json',dict(b=str(C-Q(1,10**104)),b_above_endpoint=m['root_interval'][1],profile=m['new_profile'],live=m['live']))
 for name in ('check_ledger.py','independent_check.py'):
  with (a.out/(name+'.log')).open('w') as f:subprocess.run([sys.executable,'-B',str(a.out/'outer'/name)],stdout=f,stderr=subprocess.STDOUT,check=True)
 ledger=read(a.out/'outer/LEDGER.json');row=ledger['rows']['struct_boundary_radix_union'];controls=ledger['rejecting_controls']['struct_boundary_radix_union']
 need(Q(row['kappa']['rational'])==K,'derived kappa')
 need(len(row['strict_checks'])==63 and all(Q(x['rational'])>0 for x in row['strict_checks'].values()),'63 positive inequalities')
 need(len(controls)==17 and all(x and all(Q(v['rational'])<=0 for v in x.values()) for x in controls.values()),'17 controls')
 independent=read(a.out/'outer/INDEPENDENT.json');need(Q(independent['rows']['struct_boundary_radix_union']['kappa'])==K,'independent derivation')
 result=dict(status='PASS_RETIMED_MODERN_OUTER_ARITHMETIC',kappa=str(K),strict_inequalities=63,rejected_controls=17,independent=independent['status'],ledger_sha256=sha(a.out/'outer/LEDGER.json'),checker_sha256=sha(a.out/'outer/check_ledger.py'),independent_checker_sha256=sha(inp),scope='Fresh source-bound exact arithmetic. Global changed-word controller/invoice release not inferred; inherited supplier and all-size premises remain.')
 save(a.out/'RESULT.json',result);print(result['status'])
if __name__=='__main__':main()
