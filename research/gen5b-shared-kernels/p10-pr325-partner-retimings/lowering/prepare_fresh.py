from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_frame_binding()
"""Fresh PR325 finite bank address and rational chart preparation.
Independent source-data consumer; upstream programs are never executed.
Prepared with OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from math import gcd,lcm
import json,gzip,hashlib,struct,os
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent
SOURCE=contract.SOURCE
OUT=contract.PREPARED
HEAD='0eca9340a3df6141b8e71a41638c3937b3522888'
# Source transport hash is of the actual compressed word bytes.
WORD='601da0e6a67715011a4bbc44f6977f13625c5833d4d40443c10b0d5a9da1896d'
FRAMES='fec07e983f81459c45747dfaa4eecabc3429e84d4685f385771904dee4c4fbc0'
sha=lambda b:hashlib.sha256(b).hexdigest()
def fs(p):return sha(Path(p).read_bytes())
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def dump(n,x):
 b=canon(contract.portable(x));(OUT/n).write_bytes(gzip.compress(b,mtime=0)if n.endswith('.gz')else b)
def primitive(row):
 den=lcm(*(x.denominator for x in row));a=[int(x*den)for x in row];d=gcd(*a);return[x//d for x in a]if d else a
def rref(rows):
 a=[list(map(F,r))for r in rows];piv=[];k=0
 for j in range(20):
  z=next((i for i in range(k,len(a))if a[i][j]),None)
  if z is None:continue
  a[k],a[z]=a[z],a[k];v=a[k][j];a[k]=[x/v for x in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
  piv.append(j);k+=1
 return a[:k],piv
def null(rows):
 a,piv=rref(rows);out=[]
 for j in range(20):
  if j in piv:continue
  v=[F(0)]*20;v[j]=F(1)
  for i,k in enumerate(piv):v[k]=-a[i][j]
  out.append(primitive(v))
 return out
def factor_inverse(columns):
 a=[list(map(F,row))for row in zip(*columns)];inv=[[F(i==j)for j in range(20)]for i in range(20)];ops=[]
 def swap(i,j):a[i],a[j]=a[j],a[i];inv[i],inv[j]=inv[j],inv[i];ops.append(['swap',i,j,'1'])
 def scale(i,c):a[i]=[c*x for x in a[i]];inv[i]=[c*x for x in inv[i]];ops.append(['scale',i,i,str(c)])
 def add(i,j,c):a[i]=[x+c*y for x,y in zip(a[i],a[j])];inv[i]=[x+c*y for x,y in zip(inv[i],inv[j])];ops.append(['add',i,j,str(c)])
 for j in range(20):
  i=next(i for i in range(j,20)if a[i][j])
  if i!=j:swap(i,j)
  if a[j][j]!=1:scale(j,1/a[j][j])
  for i in range(20):
   if i!=j and a[i][j]:add(i,j,-a[i][j])
 assert a==[[int(i==j)for j in range(20)]for i in range(20)]
 B=list(zip(*columns))
 for left,right in ((B,inv),(inv,B)):
  assert all(sum(x*y for x,y in zip(row,col))==int(i==j)for i,row in enumerate(left)for j,col in enumerate(zip(*right)))
 assert len(ops)+99+100<=349
 return [[str(x)for x in row]for row in inv],ops

def main():
 sources=read(SOURCE/'SOURCES.json');assert sources['head']==HEAD
 for z in sources['files']:assert fs(SOURCE/'inputs'/z['local'])==z['sha256']
 pre=SOURCE/'inputs/bitword__selected__bit__'
 wp=Path(str(pre)+'word_p10.json.gz');fp=Path(str(pre)+'frames_p10.json.gz')
 assert fs(wp)==WORD and fs(fp)==FRAMES
 w=read(wp);frames=read(fp)['frames'];aliases={b:a for a,b in w['pairs']}
 assert len(aliases)==960 and not set(aliases)&set(aliases.values())
 virtual=1+max(max(r[:2])for r in w['ops']);roles=sorted(set(range(virtual))-set(aliases))
 assert virtual==9060 and len(roles)==8100
 gauges={z['role']:z for z in w['gauges']if z['role']in roles}
 assert len(gauges)==1200 and Counter(z['dim']for z in gauges.values())=={16:1200}
 programs={};uses={};denominators=set();factor_lengths=[]
 for role,z in sorted(gauges.items()):
  f=z['frame'];uses[role]=f
  if f in programs:continue
  frm=frames[str(f)];A=frm.get('a');B=frm.get('b')
  if A is None:A=null(B)
  if B is None:B=null(A)
  assert len(rref(A)[0])==4 and len(rref(B)[0])==16
  assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)
  R=[[11*x-sum(a)for x in a]for a in A]
  assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in R for b in B)
  columns=R+B;inverse,ops=factor_inverse(columns)
  for row in inverse:
   for x in row:denominators.add(F(x).denominator)
  for op,i,j,c in ops:denominators.add(F(c).denominator)
  programs[f]={'source_frame':f,'rank':4,'entrance_rank':16,'final_rank':20,'basis_columns':columns,'inverse':inverse,'factors':ops,'factor_count':len(ops)}
  factor_lengths.append(len(ops))
 assert len(programs)==120
 raw=bytearray();coverage=bytearray(85680*100);bank=0
 for width in (4,20):
  selected=[r for r in roles if(4 if r in gauges else 20)==width]
  capacity=100//width;items=[(r,t)for r in selected for t in range(60)];assert len(items)%capacity==0
  for start in range(0,len(items),capacity):
   for slot,(r,t)in enumerate(items[start:start+capacity]):
    off=slot*width;scalar=slot+1;raw.extend(struct.pack('>6I',r,t,bank,off,width,scalar))
    sl=slice(bank*100+off,bank*100+off+width);assert not any(coverage[sl]);coverage[sl]=b'\1'*width
   bank+=1
 assert bank==85680 and all(coverage)and len(raw)==486000*24
 (OUT/'literal-bank-assignments.bin.gz').write_bytes(gzip.compress(raw,mtime=0))
 dump('fresh-role-index.json',{'roles':roles,'aliases':aliases,'source_word_gzip_sha256':WORD,'helper_offset':1920,'work':10020,'source_gauge_frames':uses})
 dump('fresh-endpoint-charts.json.gz',{'programs':programs,'uses':uses,'denominators':sorted(denominators),'all_actual_current_gauges':True})
 result={'status':'PASS_FRESH_PR325_BANK_PREPARATION_ONLY','source_head':HEAD,'word_gzip_sha256':WORD,'frames_gzip_sha256':FRAMES,
 'physical_roles':8100,'assignments':486000,'banks_per_stage':85680,'literal_stock':658800,'inventory':{4:1200,20:6900},'full_bank_coverage':True,
 'paid_completion_sweeps':0,'fresh_charts':120,'chart_uses':1200,'max_chart_factors':max(factor_lengths),'normalizer_factor_bound':349,
 'assignment_raw_sha256':sha(raw),'assignment_gzip_sha256':fs(OUT/'literal-bank-assignments.bin.gz'),'source_manifest_sha256':fs(SOURCE/'SOURCES.json'),
 'checker_sha256':fs(__file__),'no_old_role_frame_or_chart_data_imported':True,'scope':'Fresh roles, endpoint chart algebra and complete literal bank coverage only. Actual full local frame stream, chronology/matrix retiming proof and global phase binding remain required.'}
 dump('PREPARATION.json',result);dump('MANIFEST.json',{p.name:fs(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='MANIFEST.json'})
 print(json.dumps(contract.portable(result),indent=2))
if __name__=='__main__':main()
