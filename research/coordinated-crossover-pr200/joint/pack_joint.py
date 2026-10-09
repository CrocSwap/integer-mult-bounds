"""Literal 4/5/6/11/12/24 completed banks and actual charts for joint gauge word."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
from math import gcd
import importlib.util,json,hashlib,sys
sys.dont_write_bytecode=True
from joint_word import Candidate,D,P
PACKAGE=D.parent;ROOT=PACKAGE.parents[1]
spec=importlib.util.spec_from_file_location('retained_chart',PACKAGE/'geometry/retained-packing.py');chart=importlib.util.module_from_spec(spec);spec.loader.exec_module(chart)
W=Candidate();C=W.C
removed={W.w['rootroles'][e['root']]for e in json.loads((P/'selected/bit/sinks.json').read_text())}
borrowed={r['role']for r in json.loads((PACKAGE/'borrow/selection.json').read_text())}
assert len(borrowed)==440 and not borrowed&(set(W.gauge)|set(W.source.values())|set(W.donor)|removed)
gauge_borrowed={r['role']for r in json.loads((PACKAGE/'gaugeb/selection.json').read_text())}
assert len(gauge_borrowed)==3 and gauge_borrowed<=set(W.gauge) and not gauge_borrowed&(borrowed|set(W.donor)|removed)
physical=set(range(W.R))-set(W.donor)-removed-borrowed-gauge_borrowed
selected={s for s in W.gauge if s in physical}
assert Counter(W.gauge[s]['dim']for s in selected)=={20:2200,18:13,12:18,13:48}
families={r:sorted(s for s in selected if 24-W.gauge[s]['dim']==r)for r in [4,5,6,11,12]}
families[24]=sorted(physical-selected)
assert {r:len(xs)for r,xs in families.items()}=={4:2200,6:13,5:0,11:48,12:18,24:14392}
assert set().union(*map(set,families.values()))==physical and len(physical)==16671
# Every actual gauge chart and its two-sided inverse.
charts=[];maxops=maxnum=maxden=0
for f,count in sorted(Counter(W.gauge[s]['frame']for s in selected).items()):
 residual=[]
 for a in C.A[f]:
  row=[15*x-sum(a)for x in a];d=gcd(*row);residual.append([x//d for x in row])
 source=C.B[f]
 assert len(residual)+len(source)==24
 assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in residual for b in source)
 B=list(map(list,zip(*(residual+list(source)))));inverse,den,ops=chart.inverse_integer(B)
 for left,right in ((B,inverse),(inverse,B)):
  assert all(sum(x*y for x,y in zip(row,col))==den*int(i==j)for i,row in enumerate(left)for j,col in enumerate(zip(*right)))
 replay=[list(map(Q,row))for row in B]
 for op,i,j,num,d in ops:
  if op=='swap':replay[i],replay[j]=replay[j],replay[i]
  elif op=='scale':replay[i]=[Q(num,d)*x for x in replay[i]]
  else:replay[i]=[x+Q(num,d)*y for x,y in zip(replay[i],replay[j])]
 assert all(x==int(i==j)for i,row in enumerate(replay)for j,x in enumerate(row))
 maxops=max(maxops,len(ops));maxnum=max(maxnum,max(abs(o[3])for o in ops));maxden=max(maxden,den,max(o[4]for o in ops))
 charts.append(dict(frame=f,count=count,residual_rank=len(residual),basis=B,inverse_numerator=inverse,inverse_denominator=den,factors=ops))
assert max(maxnum,maxden)<2**80
print('PASS charts',len(charts),'max factors',maxops,flush=True)

T=72;patterns=[([11]*4+[4]*7,864),([4]*18,8464),([6]*12,78),([12]*6,216),([24]*3,345408)]
assert all(sum(blocks)==72 for blocks,_ in patterns)
incidence=hashlib.sha256();assignments=0;normalizers=[];controls=[]
for stage in range(3):
 used=Counter();bank=0
 for widths,count in patterns:
  j=next(i for i in range(72)if not 24*stage<=i<24*(stage+1));witness=[];offset=0
  for block,rank in enumerate(widths):
   original=list(range(24*stage,24*stage+rank));target=list(range(offset,offset+rank));src=original+[i for i in range(72)if i not in original];dst=target+[i for i in range(72)if i not in target];pi=dict(zip(src,dst));assert set(pi)==set(pi.values())==set(range(72));witness.append((pi[j],block+1));offset+=rank
  assert len(set(witness))==len(widths)
  normalizers.append(dict(stage=stage,widths=widths,outside_stage_column=j,scaled_column_witness=witness))
  for _ in range(count):
   offset=0
   for block,rank in enumerate(widths):
    q=used[rank];role=families[rank][q//T];replica=q%T;used[rank]+=1
    incidence.update(f'{stage},{rank},{role},{replica},{bank},{offset}\n'.encode());assignments+=1;offset+=rank
   assert offset==72;bank+=1
 assert bank==355030 and used=={r:T*len(rs)for r,rs in families.items()if rs}
 if stage==0:
  for widths,_ in patterns:
   def endpoint(indices):
    state=list(range(144));offsets=[sum(widths[:b])for b in range(len(widths))]
    for b in indices:
     for j in range(offsets[b],offsets[b]+widths[b]):state[j],state[72+j]=state[72+j],state[j]
    return state
   blocks=len(widths);full=list(range(72,144))+list(range(72))
   assert endpoint(range(blocks))==full
   assert endpoint(list(range(blocks))+list(reversed(range(blocks))))==list(range(144))
   assert endpoint(range(blocks-1))!=full;controls.append(dict(widths=widths,mutation='omitted last block',status='REJECTED'))
   assert endpoint(list(range(blocks))+[0])!=full;controls.append(dict(widths=widths,mutation='repeated first block',status='REJECTED'))
assert assignments==3*T*16671==3600936
banks=3*355030;literal_stock=banks+T*2*W.v;assert literal_stock==1318530
K=2*3*T*((literal_stock-1)+16671*72*(maxops+71+72));assert 0<K<2**40
out=dict(status='PASS_ACTUAL_JOINT_GAUGE_CHARTS_AND_COMPLETE_BANKS',families={r:len(rs)for r,rs in families.items()},physical_replicas=T,bank_patterns=[dict(widths=widths,banks_per_stage=n)for widths,n in patterns],banks_total=banks,assignments=assignments,literal_stock=literal_stock,integer_normalization=24,W=439510,deficit=46464,m=72,charts=len(charts),max_chart_factors=maxops,max_factor_numerator=maxnum,max_denominator=maxden,incidence_sha256=incidence.hexdigest(),normalizers=normalizers,controls=controls,conservative_extra_selector_calls=K,chart_sha256=hashlib.sha256(json.dumps(charts,sort_keys=True,separators=(',',':')).encode()).hexdigest())
(D/'joint-charts.json').write_text(json.dumps(charts,separators=(',',':'))+'\n');(D/'joint-banks.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS complete banks',patterns,'stock',literal_stock,'routing',K,flush=True)
