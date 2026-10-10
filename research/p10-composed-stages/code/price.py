#!/usr/bin/env python3
"""Price the actual p10 composed word with PR315's two engines and complete fallback.
Prepared with OpenAI Codex assistance; Apache-2.0. PR315 math interfaces are inherited.
"""
import sys
if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,hashlib,json,struct,importlib.util
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'vendor/pr315';sys.path.insert(0,str(SRC))
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def run(candidate,bank_path,complex_path,output):
 candidate=Path(candidate);read=lambda p:json.loads(Path(p).read_text());bank=read(bank_path);st=read(candidate/'249-states.json');fs=read(candidate/'frames.json')['frames'];raw=(candidate/'COHORT249-RECORDS.bin').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert st['record_sha256']==digest
 H=Counter();adds=units=copies=0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',raw):
  if op==0 and f:H[f]+=1
  elif op==2:H[z]+=1;copies+=1
  elif op==1:adds+=1;units+=abs(c)
 assert copies==20 and adds>0
 residual=sum(fs[str(st['final'][str(i)])]['dim']-fs[str(st['initial'][str(i)])]['dim'] for i in range(1920,10150))
 stock=bank['normalized_stock'];assert bank['literal_stock']==5*stock and 100*bank['banks_per_stage']==60*residual
 assert bank['literal_stock']==4*960*60+5*bank['banks_per_stage']
 hist={r:60*n for r,n in H.items()}
 for r in (4,19,38,42):hist[r]=hist.get(r,0)+23040
 calls=sum(hist.values());mass=sum(r*n for r,n in hist.items());assert 100*stock-mass==24480 and max(hist)==42
 cost=load('composition_cost',SRC/'moment.py');other=load('composition_other',SRC/'base_two_moment.py');outer=load('composition_outer',SRC/'outer.py');upmath=load('composition_upmath',SRC/'math_check.py')
 root=cost.certify(hist,100,stock,True);coarse=Q(int(Q(root['lower'])*10**18),10**18);step=Q(1,10**18)
 first=cost.moment(hist,100,stock,coarse,True);first_next=cost.moment(hist,100,stock,coarse+step,True);assert first[1]<1<first_next[0]
 fallback=32*100*100*calls
 f0=other.moment(100,stock,list(hist.items()),coarse);b0=other.moment(100,stock,[(1,fallback)],coarse);fn=other.moment(100,stock,list(hist.items()),coarse+step);bn=other.moment(100,stock,[(1,fallback)],coarse+step)
 second=(f0[0]+Q(1,10**16)*b0[0],f0[1]+Q(1,10**16)*b0[1]);second_next=(fn[0]+Q(1,10**16)*bn[0],fn[1]+Q(1,10**16)*bn[1]);assert second[1]<1<second_next[0]
 complex_result=read(complex_path);supplier=upmath.complex_supplier(cost,other,complex_result['five_stage_histogram']);b=supplier['coarse'];eta=Q(1,10**12);beta=Q(1,10**9);s=min(coarse,Q(((1-beta)*b-step)*10**18//1,10**18));chain=[Q(384599,10**10)];gaps=[]
 for j in range(3):
  old=chain[-1];new=(1-s)*s+s*old;row=dict(atom=s-new,borrowing=1-new-s,remainder=1-new-s*(1-old),stock=1-s);assert old<new<s and min(row.values())>0;chain.append(new);gaps.append(row)
 leaf=chain[-1];bridge=dict(proof='vendor/pr315/PROOF.md',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
 q=leaf*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18);assembly=outer.assembly(leaf,b,bridge,k,eta=eta,beta=beta)
 assert len(assembly['strict_constraints'])==47 and min(assembly['strict_constraints'].values())>0
 try:outer.assembly(leaf,b,bridge,k+step,eta=eta,beta=beta)
 except AssertionError:pass
 else:raise AssertionError('adjacent kappa admitted')
 result=dict(status='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS',source_word_sha256=digest,adds=adds,unit_adds=units,local_histogram=dict(H),local_rank_mass=sum(r*n for r,n in H.items()),residual=residual,cohort_candidate=dict(stock=stock,histogram=hist,calls=calls,rank_mass=mass,deficit=24480,coarse=s,moment_upper=first[1] if s==coarse else cost.moment(hist,100,stock,s,True)[1],kappa=k),first_interval=first,first_next=first_next,second_interval=second,second_next=second_next,ordinary_chain=chain,ordinary_gaps=gaps,assembly=assembly,kappa=k,bit_root=coarse,complex_saving=b,complex_supplier=supplier,complex_binds=s<coarse,full_fallback_retained=True,fallback_density=Q(1,10**16),adjacent_rejected=True)
 Path(output).write_text(json.dumps(upmath.serial(result),sort_keys=True,indent=2)+'\n');print('PASS exact p10 price',k,float(k),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('candidate');ap.add_argument('--bank',required=True);ap.add_argument('--complex',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();run(a.candidate,a.bank,a.complex,a.output)
