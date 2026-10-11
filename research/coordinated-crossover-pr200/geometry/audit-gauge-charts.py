"""Reuse PR197's exact gauge chart factors on unchanged PR200 entrances.
Checks both inverse matrix identities, literal elementary factor replay,
all factor/unit denominators, and a conservative fully charged routing bound.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from math import gcd
import sys,json,hashlib,importlib.util
sys.set_int_max_str_digits(0);sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_bank',HERE/'pack-pr200.py');G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
packing=HERE/'retained-packing.py'
sp=importlib.util.spec_from_file_location('retained_exact_chart_factorizer',packing);P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
word=G.proof.Candidate();C=word.C
selected={s:z for s,z in word.gauge.items() if s not in word.donor};inventory=Counter(z['frame'] for z in selected.values())
G.need(len(selected)==2200 and len(inventory)==220,'actual unchanged220gauge frames')
records=[];maxops=maxnum=maxden=maxC=maxB=0
for f,count in sorted(inventory.items()):
 A=C.A[f];sigma=C.B[f];G.need(len(A)==4 and len(sigma)==20,'actual rank4 residual')
 residual=[]
 for a in A:
  r=[15*x-sum(a) for x in a];d0=gcd(*r);residual.append([x//d0 for x in r])
 G.need(all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in residual for b in sigma),'literal Gorthogonal residual basis')
 B=list(map(list,zip(*(residual+sigma))));inv,d,ops=P.inverse_integer(B)
 for left,right in [(B,inv),(inv,B)]:
  G.need(all(sum(x*y for x,y in zip(row,col))==d*int(i==j) for i,row in enumerate(left) for j,col in enumerate(zip(*right))),'two exact inverse identities')
 replay=[list(map(Q,r)) for r in B]
 for op,i,j,n,den in ops:
  if op=='swap':replay[i],replay[j]=replay[j],replay[i]
  elif op=='scale':replay[i]=[Q(n,den)*x for x in replay[i]]
  else:
   G.need(op=='add','retained elementary factor type');replay[i]=[x+Q(n,den)*y for x,y in zip(replay[i],replay[j])]
 G.need(all(x==int(i==j) for i,row in enumerate(replay) for j,x in enumerate(row)),'independent factor replay')
 maxops=max(maxops,len(ops));maxnum=max(maxnum,max(abs(o[3]) for o in ops));maxden=max(maxden,d,max(o[4] for o in ops));maxC=max(maxC,max(abs(x) for r in inv for x in r));maxB=max(maxB,max(abs(x) for r in B for x in r))
 records.append(dict(frame=f,count=count,basis=B,inverse_numerators=inv,inverse_denominator=d,factors=ops))
G.need(max(maxnum,maxden,maxC,maxB,18)<2**80,'all literal inverse and chart units below inherited prime bound')
# t in1..18 supplies18 distinct fixed scalar choices per selected bank. At most
# one scalar per earlier normalizer is forbidden; conjugation stays unchanged.
# Rational distinctness survives q>2^80 by this bound on cleared differences.
cleared_difference_bound=2*18*max(maxC,1)*max(maxden,1)
G.need(cleared_difference_bound<2**80,'distinct normalizers remain distinct modulo every allowed prime')
factor_bound=maxops+71+72
physicalstock=169206;physicalchains=17114;full_core_stage_occurrences=27
calls=2*full_core_stage_occurrences*((physicalstock-1)+physicalchains*72*factor_bound)
G.need(calls<2**40,'fully literal replicated extra selector bound')
raw=json.dumps(records,sort_keys=True,separators=(',',':')).encode()
import gzip
(HERE/'pr200-gauge-charts.json.gz').write_bytes(gzip.compress(raw,mtime=0))
out=dict(status='PASS_ALL_ACTUAL_GAUGE_CHARTS_AND_ROUTING_BILL',source_pin='a1175449f34d39ff933d9d8ab23ced1f32b290ec',retained_factorizer_sha256=hashlib.sha256(packing.read_bytes()).hexdigest(),gauges=2200,distinct_gauge_frames=220,max_chart_factors=maxops,max_factor_numerator=maxnum,max_denominator_or_inverse_denominator=maxden,max_inverse_numerator=maxC,max_basis_numerator=maxB,chart_witness_sha256=hashlib.sha256((HERE/'pr200-gauge-charts.json.gz').read_bytes()).hexdigest(),greedy_distinct_scalars=list(range(1,19)),cleared_normalizer_difference_bound=cleared_difference_bound,permutation_transpositions_bound=71,extra_distinct_scalar_coordinate_scales_bound=72,combined_chart_factor_bound=factor_bound,nine_full_replicas=True,total_stage_core_occurrences=27,literal_persistent_stock=physicalstock,conservative_extra_selector_calls=calls,selector_calls_below_2pow40=True,prime_guard='Every nonzero factor/inverse denominator and fixed scalar is smaller than2^80; all actual changes are invertible for every inherited primeq>2^80. Distinct normalizers remain distinct by cleared entry bounds.',routing_payment='These finite extra calls use inherited completed old ordinary selector; they are O(K V w^(1-a_old)), absorbed by strict finite-leaf atom/row toll as in PR197 PROOF5. No extra positive-rank children and no new external row reserve.',scope='Exact finite address chart, inverse, unit and replicated routing bill on same220gauge frames; allsize weighted/restored selector guarantee stays inherited.')
(HERE/'PR200-GAUGE-CHART-AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2))