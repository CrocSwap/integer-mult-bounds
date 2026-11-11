"""Rebuild the frozen blockwise evaluation-pair factory and 99-pivot word.
Apache-2.0. Adapted with OpenAI Codex assistance; retain PR507/484 notices.
Usage: python -B build_pair35.py PR507_CONSTRUCTOR HAMMING GK_CODE
       OLD_PARTIAL_BASE RETIMED_PARTIAL_BASE PAIR_SPEC KERNEL_SELECTION NEW_OUT
No optimizer or discovery search runs. Physical routing and outer price are separate.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import sys,json,gzip,hashlib,copy,difflib,subprocess
if not __debug__:raise RuntimeError('Assertions must remain enabled')
source,hamming,code,oldfile,retfile,specfile,selfile,out=map(Path,sys.argv[1:])
assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n') if p.suffix in {'.py','.json'} else p.read_bytes()).hexdigest()
assert sha(source)=='8b9a7f1bb69626d76fec9e915134cec7199a70b53656723ce49ecc47f4644afd'
assert sha(specfile)=='751fad3214c819635216df2dab77b682c6a1798d1d71a959ba4e7392aab9b8c0'
assert sha(selfile)=='e818377083be1b581da718ae4cdb0741f074df313c0813e4239377b3754f25a5'
read=lambda f:json.loads(gzip.decompress(f.read_bytes())if f.suffix=='.gz'else f.read_bytes())
spec=read(specfile);assert len(spec)==14
assert [k for k,v in sorted(spec.items())if v==[1,1]]==['0,2,4,6','0,3,4,7']
assert all(v==([1,1]if k in ['0,2,4,6','0,3,4,7']else[0,0])for k,v in spec.items())
s=source.read_text();old_token='[(1,1)[parity]]';assert s.count(old_token)==1
s=s.replace(old_token,"[json.loads(Path(sys.argv[3]).read_text())[','.join(map(str,c))][parity]]")
out.mkdir(parents=True);patched=out/'factory_constructor.py';patched.write_text(s,encoding='utf-8')
with(out/'factory-construction.log').open('w')as log:
 subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('run_portable.py')),str(patched),str(hamming),str(out/'factory'),str(specfile)],stdout=log,stderr=subprocess.STDOUT,check=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(code));import gk_word as g
b=read(out/'factory/FULL-WORD.json.gz');old=read(oldfile);ret=read(retfile);selection=read(selfile)
assert b['report']['R']==old['report']['R']==ret['report']['R']==560
transferred={}
for part in ['A','B']:
 assert [e[:-1]for e in old[part]]==[e[:-1]for e in ret[part]]
 aa=[tuple(e[:-1])for e in old[part]];bb=[tuple(e[:-1])for e in b[part]];count=0
 for ia,ib,n in difflib.SequenceMatcher(a=aa,b=bb,autojunk=False).get_matching_blocks():
  for d in range(n):
   assert old[part][ia+d][:-1]==b[part][ib+d][:-1]
   if old[part][ia+d][-1]!=ret[part][ia+d][-1]:b[part][ib+d][-1]=copy.deepcopy(ret[part][ia+d][-1]);count+=1
 transferred[part]=count
b['cleanup']=[g.inverse(e,g.FULL)for e in reversed(b['A']+b['B'])if not 120<=e[1]<240]
w=g.build(b,selection);profile=g.profile(w);widths=g.widths_of(w)
assert profile=={1:2530,2:182,3:516,4:88,5:298,6:68,7:1,8:17}
assert Counter(widths)=={7:18,8:161,9:381}
assert sum(len(c['pivots'])for c in selection['kernel'])==99
counts={}
for part in ['A','B','cut','cleanup','precondition']:
 counts[part]=len(w.get(part,[]))
 for e in w.get(part,[]):
  assert e[0]in['add','scale']
  q=Fraction(e[3],e[4])if e[0]=='add'else Fraction(e[2],e[3])
  assert q.denominator&(q.denominator-1)==0,(part,e)
  if e[0]=='scale':assert abs(q.numerator)>0 and abs(q.numerator)&(abs(q.numerator)-1)==0,(part,e)
norm=copy.deepcopy(w);assert norm.get('R',560)==norm['report']['R']==560;norm.pop('R',None)
for k in ['complex_coarse_float','gain_percent_float']:norm['report'].pop(k,None)
semantic=hashlib.sha256(json.dumps(norm,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert semantic=='bf26b8c3709039eb027430218f8b9bd3c369eb9c584e4ebfc2f9e350bab93f19'
(out/'FULL-WORD.json.gz').write_bytes(g.dump(w));(out/'RETIMED-BASE.json.gz').write_bytes(g.dump(b));(out/'SELECTION.json').write_bytes(selfile.read_bytes())
receipt=dict(status='PASS_SOURCE_BOUND_PAIR35_CONSTRUCTION_AND_DYADIC_GATE',sources={label:sha(f)for label,f in [('public_constructor',source),('prototype',hamming/'PROTOTYPE.json'),('packet_programs',hamming/'PACKET-PROGRAMS.json.gz'),('old_partial',oldfile),('retimed_partial',retfile),('pair_spec',specfile),('selection',selfile),('gk_word.py',code/'gk_word.py'),('gk_common.py',code/'gk_common.py')]},normalized_word_sha256=semantic,word_sha256=sha(out/'FULL-WORD.json.gz'),profile=dict(profile),widths=dict(Counter(widths)),widths_ordered=widths,pivots=99,transferred_frames=transferred,dyadic_event_counts=counts,scope='Exact local source, relation, frame and scalar compiler compatibility; complete arbitrary-dirt and physical provider replay remain separate.')
(out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
