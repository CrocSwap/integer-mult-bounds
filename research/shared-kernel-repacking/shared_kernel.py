# SPDX-License-Identifier: Apache-2.0
"""Staged four-helper compensation kernels for pinned PR2833 supplier words.

Prepared for Yiyang (@Lyy-iiis) with substantial OpenAI Codex assistance,
including separate construction and review agents. Builds on Jeremy Kothe's
PR2833 dirt-entry supplier and its credited PR2802/earlier lineage. Frame and
inverse-cleanup conventions follow that supplier's Apache-2.0 word_patch.py and
audit_local.py; the CLI authenticates and calls the inherited implementation.
No source files, imports, processes, or outputs are touched by apply().
"""
import copy, hashlib, json
from collections import Counter
from fractions import Fraction as F

CANONICAL_INPUTS={
 'aaf1d752501a30fdf7305be9515617698d0b4753411844d28f005aab1b67f3df':'base',
 '1b02e1ea0214b45071f9d93ad074cc392fd7e59f6fb83a7c4e8cd99c36150a3c':'extra',
}
COMPRESSED_INPUTS={
 'dda9878455b3a3bec64ca16b1ac7789bbf5ffb603d5713b8df8644485e85b1b7':'base',
 'bbe6bcba59e45e827a8e932ee4b23650d56ed4a0b8e0875c14f23c36b9e47eac':'extra',
}
DEPENDENCIES={
 'word_patch.py':'9b3287f189c4f29c1a8bdb1ba01fdcfe14a57d87b50fa4f2f646fb2346ab01ce',
 'audit_local.py':'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90',
}
GROUPS={460:(460,461,468,469),462:(462,463,470,471),478:(478,479,490,491),480:(480,481,492,493)}

def require(ok, reason):
 if not ok:raise ValueError(str(reason))

def basis(vs):
 piv={}
 for a in vs:
  while a:
   bit=a.bit_length()-1
   if bit in piv:a^=piv[bit]
   else:piv[bit]=a;break
 for k in sorted(piv):
  for j in piv:
   if j>k and piv[j]>>k&1:piv[j]^=piv[k]
 return tuple(piv[k] for k in sorted(piv,reverse=True))

def contained(a,b):return basis(a+b)==b

def _restored_of(w):
 n=2*w['report']['v']+w['report']['R']
 return {g[1]-n for g in w['cleanup'] if g[1]>=n}|{g[2]-n for g in w['cleanup'] if g[0]=='add' and g[2]>=n}

def _derive_cleanup(w,restored):
 # Literal inverse-reverse, excluding target writes; caller removes the prelude.
 v=w['report']['v'];n=2*v+w['report']['R'];full=list(basis([1<<i for i in range(w['report']['h'])]))
 byp={}
 for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append((op,rec))
 fw=list(w['A'])
 for p in range(len(w['B'])+1):
  for op,rec in byp.get(p,[]):fw.append(['warp',rec[1],op])
  if p<len(w['B']):fw.append(w['B'][p])
 fw+=w['restore'];buf=lambda r:r+n if r in restored else r;out=[]
 for g in reversed([g for g in fw if g[0]=='warp' or not(v<=g[1]<2*v)]):
  if g[0]=='warp':out.append(['warp',buf(g[1]),-g[2],full])
  elif g[0]=='add':out.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],full])
  else:out.append(['scale',buf(g[1]),g[3],g[2],full])
 return out

def apply(word, chosen=(478,460,462,480)):
 """Return (changed word, ledger); authenticate the decoded pinned source first."""
 canonical=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
 digest=hashlib.sha256(canonical).hexdigest()
 require(digest in CANONICAL_INPUTS, 'unauthorized decoded source SHA256')
 variant=CANONICAL_INPUTS[digest]
 chosen=list(chosen)
 require(chosen and len(chosen)==len(set(chosen)) and all(q in GROUPS for q in chosen), 'invalid or duplicate kernel selection')
 w=word;x=copy.deepcopy(w);byp={};ledger=[]
 for leader in chosen:
  q0,q1,q2,q3=GROUPS[leader];info={}
  for q in(q0,q1,q2,q3):
   use=[(i,g) for i,g in enumerate(w['A']) if q in(g[1:3] if g[0]=='add' else g[1:2])]
   require(len(use)==1, ('unexpected A uses',q,use))
   i,g=use[0];require(g[0]=='add' and g[1]==q, 'partner gate shape')
   s=g[2];require(all(e[1]!=s for e in w['A']), 'partner not A-constant')
   info[q]=(i,s,F(g[3],g[4]),basis(g[-1]))
  i0,s0,c0,E=info[q0];i1,s1,c1,E1=info[q1];i2,s2,c2,G=info[q2];i3,s3,c3,G1=info[q3]
  require(E==E1 and G==G1 and len(E)==len(G)==2, 'paired frame interface')
  span=lambda U:{z for z in range(512) if basis(list(U)+[z])==U}
  L=basis(span(E)&span(G));require(len(L)==1, 'paired intersection dimension')
  def emit(p,t,s,c,fr):
   byp.setdefault(p,[]).append(['add',t,s,c.numerator,c.denominator,list(fr)])
  emit(min(i0,i2),q2,q0,F(-1),L)
  emit(max(i0,i1)+1,q1,q0,F(1),E);emit(max(i0,i1)+1,q1,s0,-c0,E)
  emit(max(i2,i3)+1,q3,q2,F(1),G);emit(max(i2,i3)+1,q3,s2,-c2,G)
  comp3=[g for g in w['compensation'] if g[0]=='add' and g[2]==q3]
  removed=[g for g in x['compensation'] if g[0]=='add' and g[2]==q0]
  x['compensation']=[g for g in x['compensation'] if g not in removed]
  x['compensation'] += [g[:2]+[q2]+g[3:] for g in comp3]
  x['start_extra'][str(q0)]=list(L)
  ledger.append(dict(group=[q0,q1,q2,q3],raised=q0,entry=list(L),source_width=9,new_width=8,compensation_removed=len(removed),compensation_added=len(comp3)))
 A=[]
 for p in range(len(w['A'])+1):
  A.extend(byp.get(p,[]))
  if p<len(w['A']):A.append(w['A'][p])
 x['A']=A
 full=basis([1<<i for i in range(9)]);end=[full]*112+[basis([z for z in range(1,512) if(z&p).bit_count()%2==0]) for p in x['ports']]+[full]*480
 for r,U in x['helper_final'].items():end[int(r)]=basis(U)
 start=[(p,) for p in x['ports']]+[()]*(112+480)
 for r,U in x['start_extra'].items():start[int(r)]=basis(U)
 cur=start.copy();paid=Counter()
 def climb(r,U):
  U=basis(U);require(contained(cur[r],U), ('nonmonotone frame',r,cur[r],U))
  d=len(U)-len(cur[r])
  if d:paid[d]+=1
  cur[r]=U
 def step(g):
  if g[0]=='warp':require(cur[g[1]]==basis(g[3]), 'A warp frame');cur[g[1]]=basis(g[4])
  else:
   for r in(g[1:3] if g[0]=='add' else g[1:2]):climb(r,g[-1])
 for g in x['A']:step(g)
 for r,U in zip(x['centers'],x['center_frames']):
  require(cur[r]==basis(U), 'centre frame')
  for T in sorted({basis(x['target_levels'].get(str(g[1]-112),[])) for g in x['cut'] if g[2]==r},key=lambda t:-len(t)):
   if basis(U)!=T:paid[len(U)-len(T)]+=1
   U=T
 bw={}
 for rec in x['warps']:bw.setdefault(rec[0],[]).append(rec)
 for p in range(len(x['B'])+1):
  for rec in bw.get(p,[]):require(cur[rec[1]]==basis(rec[3]), 'B warp frame');cur[rec[1]]=basis(rec[4])
  if p<len(x['B']):step(x['B'][p])
 for g in x['restore']:step(g)
 live=set(range(704))-set(x['removed'])
 for r in live:climb(r,end[r])
 inv=Counter(len(end[r])-len(start[r]) for r in live if r>=224)
 x['report']['local_profile']={str(k):v for k,v in sorted(paid.items())};x['report']['width_inventory']={str(k):v for k,v in sorted(inv.items())}
 oldprof=Counter({int(k):v for k,v in w['report']['local_profile'].items()});diff={k:paid[k]-oldprof[k] for k in paid.keys()|oldprof.keys() if paid[k]!=oldprof[k]}
 require(diff=={1:3*len(chosen),2:-2*len(chosen)}, ('unexpected paid profile',diff))
 t=copy.deepcopy(x);t['A']=t['A'][t['prelude_events']:];x['cleanup']=_derive_cleanup(t,_restored_of(x))
 ledger=dict(variant=variant,source_canonical_sha256=digest,chosen=chosen,local_profile=x['report']['local_profile'],width_inventory=x['report']['width_inventory'],delta=diff,groups=ledger,insertions=byp)
 return x,ledger

def main():
 import argparse,gzip,importlib.util,os,subprocess,sys
 from pathlib import Path
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source-word',required=True,type=Path)
 p.add_argument('--source-dir',required=True,type=Path,help='pinned PR2833 new/borrow directory')
 p.add_argument('--output',required=True,type=Path)
 p.add_argument('--ledger',type=Path)
 p.add_argument('--groups',nargs='+',type=int,default=[478,460,462,480])
 p.add_argument('--no-audit',action='store_true',help='skip the separate inherited auditor; input and cleanup pins remain mandatory')
 a=p.parse_args();sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
 raw=a.source_word.read_bytes();digest=hashlib.sha256(raw).hexdigest()
 require(digest in COMPRESSED_INPUTS,'unauthorized compressed source SHA256')
 for name,expected in DEPENDENCIES.items():
  require(hashlib.sha256((a.source_dir/name).read_bytes()).hexdigest()==expected,'unauthorized dependency SHA256: '+name)
 source=json.loads(gzip.decompress(raw));word,ledger=apply(source,a.groups)
 spec=importlib.util.spec_from_file_location('_pinned_shared_kernel_word_patch',a.source_dir/'word_patch.py')
 inherited=importlib.util.module_from_spec(spec);spec.loader.exec_module(inherited)
 stripped=copy.deepcopy(word);stripped['A']=stripped['A'][stripped.get('prelude_events',0):]
 clean=inherited.derive_cleanup(stripped,inherited.restored_of(word))
 require(clean==word['cleanup'],'pure and inherited cleanup disagree')
 word['cleanup']=clean
 a.output.parent.mkdir(parents=True,exist_ok=True)
 data=json.dumps(word,separators=(',',':')).encode();a.output.write_bytes(gzip.compress(data,mtime=0))
 ledger.update(source_compressed_sha256=digest,output_content_sha256=hashlib.sha256(data).hexdigest(),output_compressed_sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),dependencies=DEPENDENCIES,inherited_cleanup_matches=True)
 lp=a.ledger or a.output.with_name(a.output.name+'.ledger.json');lp.write_text(json.dumps(ledger,indent=2)+'\n')
 if not a.no_audit:
  receipt=a.output.with_name(a.output.name+'.audit.json')
  subprocess.run([sys.executable,'-B',str(a.source_dir/'audit_local.py'),'--word',str(a.output),'--output',str(receipt)],check=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 print(json.dumps({'word':str(a.output),'ledger':str(lp),'content_sha256':ledger['output_content_sha256'],'profile':ledger['local_profile']},sort_keys=True))

if __name__=='__main__':main()
