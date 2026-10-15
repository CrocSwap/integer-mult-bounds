#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Reprice the retained carried-cutoff bootstrap; arithmetic screen only.

Adapted literally from PR2269 code/assemble.py's _outer_witness_raw;
the cutoff carry repair is PR1956 (Josie Elliston). The retained47-row
outer implementation credits eumemic, icekylinx, Zhihao Chen and hipotures.
This is the supplier's strict balanced assembly, not the newer final outer.
"""
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
from check_endpoints import NATIVE,CONSERVATIVE,RESEARCH

HERE=Path(__file__).resolve().parent
OPTIONS=dict(grid_digits=19,margin_digits=29,bootstrap_steps=12,endpoint_digits=24)
ENGINE=RESEARCH/'face-hoist-evidence/budget/inherited/vendor/outer.py'
ENGINE_PIN='c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c'


def main():
 assert __debug__,'Assertions required'
 assert hashlib.sha256(ENGINE.read_bytes()).hexdigest()==ENGINE_PIN
 spec=importlib.util.spec_from_file_location('retained_balanced_outer',ENGINE)
 A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
 c=Q('0.001733427039589844234749');PAYLOAD=2048
 def one(bb):
  grid=10**OPTIONS['grid_digits'];mg=10**OPTIONS['margin_digits']
  eta=beta=Q(1,mg);s=min(c,(1-beta)*bb)-Q(1,1000*mg)
  assert 0<s<c and s<(1-beta)*bb
  KB=int(3.6*OPTIONS['margin_digits'])+64;ONE=1<<KB
  S=(s.numerator<<KB)//s.denominator
  assert 0<S<ONE and Q(S,ONE)<=s
  O=384599*ONE//10**10;N1=36*ONE**4;ONE2=ONE*ONE
  ell=PAYLOAD;cuts=[];unc_prev=None;unc_failed=[]
  for step in range(OPTIONS['bootstrap_steps']):
   a=(S*(ONE-S)+S*O)>>KB
   g=min((S-a)*ONE,(ONE-a-S)*ONE,ONE*ONE-a*ONE-S*(ONE-O),(ONE-S)*ONE)
   assert O<a<S<ONE-a and g>0
   N2=2*(4+ell)*ONE2
   e=max(N1.bit_length()-(2*g.bit_length()-1)+2,N2.bit_length()-g.bit_length()+2,0)
   cut=1<<e
   assert cut*g*g>=N1 and cut*g>=N2
   carry=-((-(cut*(a-O)))>>KB)
   if step<7:
    Lu=max(-(-N1//(g*g)),-(-2*(4+PAYLOAD)*ONE2//g))
    if unc_prev is not None:
     cu=-((-(unc_prev[0]*unc_prev[1]))>>KB)
     unc_failed.append(Lu*g<2*(4+cu)*ONE2)
     assert unc_failed[-1]
    unc_prev=(Lu,a-O)
   cuts.append(dict(step=step,cutoff_log2_power_of_two_exponent=e,carry_bit_length=carry.bit_length(),strict_gap=str(Q(g,ONE2))))
   ell=max(PAYLOAD,ell+carry)+1;O=a
  effective=Q(O,ONE);q=effective*(1-2*eta)
  margin=(1-eta)*q/(1+q);ticks=margin*grid
  k=Q((ticks.numerator-1)//ticks.denominator,grid)
  bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
  row=A.assembly(effective,bb,bridge,k,eta=eta,beta=beta)
  assert len(row['strict_constraints'])==47 and all(x>0 for x in row['strict_constraints'].values())
  controls=[]
  for name,kk,ee,be in [('next_grid',k+Q(1,grid),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
   try:A.assembly(effective,bb,bridge,kk,eta=ee,beta=be)
   except AssertionError:controls.append(name)
   else:raise AssertionError('accepted control '+name)
  return dict(endpoint=str(bb),strict_balanced_assembly_kappa=str(k),effective_bit_saving=str(effective),strict_constraints={n:str(v) for n,v in row['strict_constraints'].items()},cuts=cuts,uncarried_controls_rejected=unc_failed,controls=controls)
 out=dict(status='PASS_CARRIED_BOOTSTRAP_PARAMETER_SCREEN_NOT_SUPPLIER_ADMISSION',options=OPTIONS,
          native=one(NATIVE),conservative=one(CONSERVATIVE),engine_sha256=ENGINE_PIN,
          scope='Same exact bootstrap formulas and47-row supplier assembly as the pinned parent, repriced at proposed endpoints. Does not bind a global controller, finite invoice, or final capped-phase outer theorem.')
 (HERE/'BOOTSTRAP-SCREEN.json').write_text(json.dumps(out,indent=2)+'\n')
 print(out['status']);print(out['native']['strict_balanced_assembly_kappa']);print(out['conservative']['strict_balanced_assembly_kappa'])


if __name__=='__main__':main()
