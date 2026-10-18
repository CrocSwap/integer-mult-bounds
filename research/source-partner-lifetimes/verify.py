#!/usr/bin/env python3
"""Bounded exact word/owner replay with semantic and physical rejecting controls."""
import contextlib,copy,gzip,io,json,subprocess,sys,tempfile
from pathlib import Path
from build import HERE,build,read,write,need,sha
from generate import mod

def verify(work):
 p=build(work/'build');al=mod('independent_local',p/'new/borrow/audit_local.py');wp=mod('cleanup',p/'new/borrow/word_patch.py');rejected=[]
 for tag in ['base','extra']:
  w=read(p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz')
  for label,target in [('restored-partner-49',49),('early-partner-31',31),('early-partner-68',68)]:
   m=copy.deepcopy(w)
   event=next(g for g in m['B'] if g[0]=='add' and g[1]==target and g[2] in [33,12,4])
   event[3]=-event[3]
   temp=copy.deepcopy(m);temp['A']=temp['A'][m['prelude_events']:];m['cleanup']=wp.derive_cleanup(temp,wp.restored_of(w))
   f=work/'bad-word.json.gz';write(f,m)
   try:
    with contextlib.redirect_stdout(io.StringIO()):al.run(f,work/'bad-audit.json')
   except RuntimeError as e:rejected.append(dict(control=tag+'-'+label,reason=str(e)))
   else:raise ValueError('accepted semantic mutation '+label)
  m=copy.deepcopy(w);g=next(g for g in m['A'][:m['prelude_events']] if g[0]=='add');g[3]*=2;write(work/'bad-word.json.gz',m)
  try:
   with contextlib.redirect_stdout(io.StringIO()):al.run(work/'bad-word.json.gz',work/'bad-audit.json')
  except RuntimeError as e:rejected.append(dict(control=tag+'-wrong-prelude-coefficient',reason=str(e)))
  else:raise ValueError('accepted prelude mutation')
 fillpath=p/'new/borrow-fill/FILL.json.gz';fill=read(fillpath)
 for label in ['missing-role','outside-window','duplicate-family']:
  bad=copy.deepcopy(fill)
  if label=='missing-role':bad['rows'].pop()
  elif label=='outside-window':
   row=bad['rows'][0];windows=read(work/'build/parent-data/PLAN.json')['windows'];allowed=windows[f'{row[2]},{row[3]}'][1];row[0]=next(t for t in range(666) if t not in allowed)
  else:
   a,b=next((a,b) for a,b in zip(bad['rows'],bad['rows'][1:]) if a[0]==b[0]);b[2:]=a[2:]
  write(fillpath,bad);out=work/('bad-'+label)
  r=subprocess.run([sys.executable,'-B',str(p/'reconstruct.py'),'--out',str(out)],capture_output=True,text=True)
  need(r.returncode!=0,'accepted physical mutation '+label);rejected.append(dict(control=label,reason=r.stderr[-300:]))
 write(fillpath,fill)
 need(read(work/'build/owners/PROFILE.json')==read(HERE/'PROFILE.json'),'exact global profile')
 need(len(rejected)==11,'all rejecting controls')
 from fractions import Fraction as Q
 claim=read(HERE/'CLAIM.json');pin=read(HERE/'LATEST-COMPARISON.json');latest=HERE/'evidence/PR2474-OUTER-CLAIM.json'
 need(sha(latest)==pin['sha256'],'comparison source pin')
 k=Q(claim['kappa']);old=Q(read(latest)['kappa']);ledger=read(HERE/'evidence/OUTER-LEDGER.json')
 need(k==Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational']),'exact outer claim binding')
 need(k-old==Q(claim['latest_claim_gain']) and k>old,'latest-claim comparison')
 need(ledger['profile']==read(HERE/'PROFILE.json') and ledger['W']==66304,'outer profile binding')
 need(sum(int(r)*n for r,n in ledger['profile'].items())==73*66304-23680,'rank mass')

 receipt=dict(status='PASS_SOURCE_PARTNER_WORDS_AND_LITERAL_OWNERS',scope='Exact all-column words and literal physical owners; full native/global/outer replay is separate.',controls_rejected=rejected,roles=281052,helpers_per_call=422)
 write(work/'RESULT.json',receipt);print(receipt['status'],flush=True)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path);a=ap.parse_args()
 if a.work:a.work.mkdir(parents=True,exist_ok=False);verify(a.work.resolve())
 else:
  with tempfile.TemporaryDirectory(prefix='source-partners-') as tmp:verify(Path(tmp))
