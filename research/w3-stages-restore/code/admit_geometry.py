#!/usr/bin/env python3
"""Bind exact new-frame and changed-projector audits to the complete word."""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
from fractions import Fraction as Q
import argparse,json,hashlib,struct

def read(p):return json.loads(Path(p).read_text())
def rank_mod(rows):
 if not rows:return 0
 p=2147483647;M=[[x%p for x in r] for r in rows];r=0
 for c in range(24):
  pivot=next((i for i in range(r,len(M)) if M[i][c]),None)
  if pivot is None:continue
  M[r],M[pivot]=M[pivot],M[r];iv=pow(M[r][c],-1,p);M[r]=[(x*iv)%p for x in M[r]]
  for i in range(r+1,len(M)):
   if M[i][c]:
    k=M[i][c];M[i]=[(a-k*b)%p for a,b in zip(M[i],M[r])]
  r+=1
  if r==len(M):break
 return r

def frame(f):
 d=f['dim'];B=f['B'];A=f['A'];assert len(B)==d and len(A)==24-d
 assert all(len(r)==24 and all(isinstance(x,int) for x in r) for r in B+A)
 # Full rank modulo a prime proves full rank over Q; exact orthogonality then proves A=B-perp.
 assert rank_mod(B)==d and rank_mod(A)==24-d
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)

def run(base,candidate,bank_dir,charts_dir,output):
 base,candidate,bank_dir,charts_dir=map(Path,(base,candidate,bank_dir,charts_dir));nf=read(candidate/'COHORT249-FRAMES.json')
 for f in nf.values():frame(f)
 assert len(nf)==4703
 negative=[]
 f=json.loads(json.dumps(next(iter(nf.values()))));f['A'][0]=[0]*24
 try:frame(f)
 except AssertionError:negative.append('zero annihilator row rejected')
 else:raise AssertionError('Bad annihilator accepted')
 old=read(base/'249-states.json');ini=read(candidate/'COHORT249-INITIAL.json');fin=read(candidate/'COHORT249-FINAL.json');fs=read(base/'frames.json')['frames'];fs.update(nf)
 def pairs(path):return {(b,c,r) for op,a,b,c,r,z in struct.iter_unpack('<6i',path.read_bytes()) if op==0 and r}
 required=pairs(candidate/'COHORT249-RECORDS.bin')-pairs(base/'249-records.bin')
 endpoints=0
 for i in range(3520,20107):
  role=str(i)
  if ini[role]!=old['initial'][role] or fin[role]!=old['final'][role]:
   before,after=ini[role],fin[role];required.add((before,after,fs[str(after)]['dim']-fs[str(before)]['dim']));endpoints+=1
 audit=read(charts_dir/'COMBINED-CHART-AUDIT.json');charts=read(charts_dir/'COMBINED-CHARTS.json');bank=read(bank_dir/'BANK-REVIEW.json');full=read(bank_dir/'BANK-CHARTS.json')
 assert {(x['before'],x['after'],x['rank']) for x in charts}==required and len(charts)==len(required)==23870
 assert audit['retired_endpoints']==endpoints==3221 and audit['unique_projectors_checked']==len(required)
 assert audit['all_entries_below_two_to_80'] and audit['max_factors']==342
 assert int(audit['max_numerator'])<2**80 and int(audit['max_denominator'])<2**80
 assert {x['frame'] for x in full}=={int(k) for k in nf} and len(full)==4703
 assert bank['new_exact_charts']==4703 and bank['max_new_chart_factors']==320
 assert bank['actual_role_replica_stage_assignments']==3026400 and bank['actual_helper_roles']==15132
 assert bank['literal_stock']==808485 and bank['normalized_stock']==161697
 bank['new_frame_chart_max']=bank['max_new_chart_factors'];bank['max_new_chart_factors']=max(bank['max_new_chart_factors'],audit['max_factors'])
 assert bank['max_new_chart_factors']+119+120<=bank['normalizer_factor_ceiling']==787
 bank.update(changed_projector_charts=23870,changed_helper_endpoints=3221,all_new_ordinary_annihilators_full_rank=True,geometry_controls=negative)
 bank['geometry_input_hashes']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in [candidate/'COHORT249-RECORDS.bin',candidate/'COHORT249-FRAMES.json',charts_dir/'COMBINED-CHART-AUDIT.json',charts_dir/'COMBINED-CHARTS.json',bank_dir/'BANK-REVIEW.json',bank_dir/'BANK-CHARTS.json']}
 Path(output).write_text(json.dumps(bank,sort_keys=True,indent=2)+'\n');print('PASS all new frame ranks, exact annihilators and 22118 changed charts',flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--base',required=True);ap.add_argument('--candidate',required=True);ap.add_argument('--bank',required=True);ap.add_argument('--charts',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();run(a.base,a.candidate,a.bank,a.charts,a.output)
