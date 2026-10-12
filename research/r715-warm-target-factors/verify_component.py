"""Frozen reconstruction and arithmetic only; global physical admission remains pending."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import argparse,json,sys,subprocess,hashlib
ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);ap.add_argument('--research-root',type=Path,default=ROOT.parent);a=ap.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
read=lambda p:json.loads(p.read_text())
sys.path[:0]=[str(ROOT/'code'),str(a.research_root/'e8-r740-replica32/code')]
import e8core as E
from hosted_kernel import kernel
import hosting_core as HC
pin=read(ROOT/'SOURCE.json');assert hashlib.sha256((ROOT/'data/base.json.gz').read_bytes()).hexdigest()==pin['base_sha256']
base=E.load_word(str(ROOT/'data/base.json.gz'))
parent_entries=read(ROOT/'data/parent-kernel-selection.json')['entries']
word,ne,nr,nd=kernel(base,parent_entries);assert (ne,nr)==(99,118)
(out/'parent-kernel.json').write_text(json.dumps(word))
subprocess.run([sys.executable,'-B',str(ROOT/'code/mix_target.py'),str(out/'parent-kernel.json'),str(out/'parent-mixed.json')],check=True)
word=read(out/'parent-mixed.json')
for ph in ('D','A','B','C'):word[ph]=[[f,d,[s]] for f,d,ss in word[ph] for s in ss]
for batch in read(ROOT/'data/parent-retiming.json')['changes']:
 for ph,i,old,new in batch['changes']:
  assert word[ph][i][0]==old;word[ph][i][0]=new
assert word==read(ROOT/'data/parent-word.json')
assert hashlib.sha256((ROOT/'data/parent-word.json').read_bytes()).hexdigest()==pin['parent_word_sha256']
parent_audit=E.replay(word,span_mode='z');assert not parent_audit['viol']
# Strip precisely the old kernel corrections; preserve target mixing and retimed source gates.
n=sum(len(ds) for frame,h,ds in parent_entries)
assert all(g[1]>=2*word['v'] for g in word['A'][:n]+word['C'][-n:])
word['A']=word['A'][n:];word['C']=word['C'][:-n]
for frame,h,ds in parent_entries:word['start'][h]=0
v=word['v'];word['D']=[[f,d,[s]] for f,d,ss in base['D'] for s in ss]+[g for g in word['D'] if any(v<=s<2*v for s in g[2])]
precursor_audit=E.replay(word,span_mode='z');assert not precursor_audit['viol']
restored,_,_,_=kernel(word,parent_entries);restored_audit=E.replay(restored,span_mode='z');assert not restored_audit['viol'] and restored_audit['H']==parent_audit['H']
word,ne,nr,nd=kernel(word,read(ROOT/'data/delivery-parent-kernel.json')['entries']);assert (ne,nr,nd)==(105,113,104)
for ph in ('D','A','B','C'):word[ph]=[[f,d,[s]] for f,d,ss in word[ph] for s in ss]
for batch in read(ROOT/'data/retiming.json')['changes']:
 for ph,i,old,new in batch['changes']:
  assert word[ph][i][0]==old;word[ph][i][0]=new
canonical=lambda w:json.dumps(w,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(canonical(word)).hexdigest()==pin['pre_delivery_word_sha256']
frame_lattice=E.Lat(word['lines']);frame_masks=E.to_masks(word,frame_lattice);frame_dims=[frame_lattice.dim(x) for x in frame_masks]
for step in read(ROOT/'data/delivery-transformations.json'):
 witness=step['witness'];assert hashlib.sha256(canonical(word)).hexdigest()==witness['source_sha256']
 if step['kind']=='reorder':
  gates=word['B'];assert all(word['v']<=d<2*word['v'] and len(ss)==1 and ss[0]>=word['v'] for f,d,ss in gates)
  dependencies=[(i,j) for i,(_,d,ss) in enumerate(gates) for j,(_,e,tt) in enumerate(gates) if i<j and (d in tt or e in ss)]
  assert len(dependencies)==witness['noncommuting_pairs']
  for move in witness['changes']:
   i,old,new=move['gate'],move['old'],move['new'];assert gates[i][0]==old;gates[i][0]=new
  order=sorted(range(len(gates)),key=lambda i:(frame_dims[gates[i][0]],i));position={i:j for j,i in enumerate(order)}
  assert all(position[i]<position[j] for i,j in dependencies)
  word['B']=[gates[i] for i in order]
 elif step['kind']=='retime':
  for ph in ('D','A','B','C'):word[ph]=[[f,d,[s]] for f,d,ss in word[ph] for s in ss]
  for batch in witness['changes']:
   for ph,i,old,new in batch['changes']:
    assert word[ph][i][0]==old;word[ph][i][0]=new
 else:raise AssertionError(step['kind'])
 assert hashlib.sha256(canonical(word)).hexdigest()==witness['word_sha256']
assert word==read(ROOT/'data/delivery-parent-word.json')
assert hashlib.sha256((ROOT/'data/delivery-parent-word.json').read_bytes()).hexdigest()==pin['delivery_parent_word_sha256']
# Undo exactly the known donor corrections while preserving every target mix and delivery move.
entries=read(ROOT/'data/delivery-parent-kernel.json')['entries'];n=sum(len(ds) for e,h,ds in entries)
assert all(g[1]>=2*word['v'] for g in word['A'][:n]+word['C'][-n:])
old_audit=E.replay(word,span_mode='z');assert not old_audit['viol']
word['A']=word['A'][n:];word['C']=word['C'][:-n]
for e,h,ds in entries:word['start'][h]=0
v=word['v'];word['D']=[[f,d,[s]] for f,d,ss in base['D'] for s in ss]+[g for g in word['D'] if any(v<=s<2*v for s in g[2])]
pa=E.replay(word,span_mode='z');assert not pa['viol']
back,_,_,_=kernel(word,entries);ba=E.replay(back,span_mode='z');assert not ba['viol'] and ba['H']==old_audit['H']
word,ne,nr,nd=kernel(word,read(ROOT/'data/kernel-selection.json')['entries']);assert (ne,nr,nd)==(110,119,102)
assert word==read(ROOT/'data/kernel-word.json')
assert hashlib.sha256((ROOT/'data/kernel-word.json').read_bytes()).hexdigest()==pin['kernel_word_sha256']
subprocess.run([sys.executable,'-B',str(ROOT/'code/schur_constructor.py'),str(ROOT/'data/kernel-word.json'),str(ROOT/'data/target-factor-selection.json'),str(out/'target-factors')],check=True)
word=read(out/'target-factors/word.json')
assert word==read(ROOT/'data/word.json')
assert hashlib.sha256((ROOT/'data/word.json').read_bytes()).hexdigest()==pin['word_sha256']
L=E.Lat(word['lines']);masks=E.to_masks(word,L);dims=[L.dim(f) for f in masks];audit=E.replay(word,L=L,masks=masks,span_mode='z');assert not audit['viol'],audit['viol'][:5]
K=5;T=8;m=78;R=word['R'];W=240*K*T;stages=2*K+1
es=[dict(kind='local',stage=0,pair=0)]
for j in range(K):
 es.append(dict(kind='local',stage=2*j+1,pair=j))
 if j<K-1:es.append(dict(kind='bridge',dst=j,src=j+1))
 es.append(dict(kind='local',stage=2*j+2,pair=j))
 if j<K-1:es.append(dict(kind='bridge',dst=j,src=j+1))
for j in reversed(range(K-1)):es.append(dict(kind='bridge',dst=j+1,src=j))
levels=[-1]*K;sc=[];idx=0
for e in es:
 sc.append(e)
 if e['kind']!='local':continue
 s,p=e['stage'],e['pair'];assert levels[p]==s-1;levels[p]=s;changes=[]
 if 0<s<2*K-1:changes=[((s+1)//2 if s%2 else s//2,s)]
 elif s==2*K:changes=[(j,s) for j in range(K)]
 for j,to in changes:
  rank=7*(to-levels[j]);levels[j]=to;sc.append(dict(kind='idle',idx=idx,pair=j,rank=rank));idx+=1
win={i:x for i,x in HC.windows(sc).items() if x[1] and x[2]};widths=[8-dims[f] for f in word['start'][240:]]
y,z,_=HC.load_selection(ROOT/'data/pooling.json','bit');slots,rem=HC.expand(win,y,z,{s:[(i,widths[i%R]) for i in range(R*T)] for s in range(stages)},240*T)
assert len(slots)==R*T*stages and len({(s,h) for i,cp,off,width,s,h in slots})==len(slots)
assert all(s in win[i][2] and 0<=off and off+width<=win[i][1] for i,cp,off,width,s,h in slots)
P=Counter({k:n*stages*T for k,n in audit['H'].items()})
for e in sc:
 if e['kind']=='idle':
  for cp in range(240*T):
   rank=rem[e['idx'],cp] if e['idx'] in win else e['rank']
   if rank:P[rank]+=1
assert m*W-sum(k*n for k,n in P.items())==408*T
expected=read(ROOT/'evidence/AGGREGATE.json');assert dict(P)=={int(k):n for k,n in expected['profile'].items()}
cert=E.moment.certify(P,m,W,True);lo,hi=Q(cert['lower']),Q(cert['upper']);assert lo==Q(expected['bit_lower'])
for x,below in [(lo,True),(hi,False)]:
 l,u=E.other.moment(m,W,list(P.items()),x);b,bu=E.other.moment(m,W,[(1,32*m*m*sum(P.values()))],x);assert u+bu/10**16<1 if below else l+b/10**16>1
result=dict(status='PASS_R715_WARM_FACTORS_RECONSTRUCTION_AND_MOMENTS_GLOBAL_PENDING',bit_lower=str(lo),projected_kappa=float(lo/(1+lo)),columns=audit['n'],whole_occurrences=len(slots),scope='Global emitted physical operators, prefix/invoice, final assembly and complete replay not established.')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
