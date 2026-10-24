"""Reconstruct the rank-sector coordinate-total supplier from frozen sources.
Apache-2.0. Prepared with OpenAI Codex assistance; retain inherited PR507/484 notices.
Usage: python -B build_ranksector.py HAMMING GK_CODE OLD_PAIR_BASE
       RETIMED_PAIR_BASE PAIR_SPEC KERNEL_SELECTION NEW_OUT
The adjacent construct_ranksector.py is a pinned source file, not an optimizer.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import sys,json,gzip,copy,hashlib,difflib,subprocess
if not __debug__:raise RuntimeError('Assertions must remain enabled')
hamming,code,oldfile,retfile,specfile,selfile,out=map(Path,sys.argv[1:]);assert not out.exists()
source=Path(__file__).resolve().with_name('construct_ranksector.py')
rawsha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
lf=lambda f:f.read_bytes().replace(b'\r\n',b'\n').replace(b'\r',b'\n')
textsha=lambda f:hashlib.sha256(lf(f)).hexdigest()
assert textsha(source)=='0b535b717ea3d15cf7e86b096a9a95fc92d71748cd5f937d1989001a3d2ec996'
assert textsha(specfile)=='751fad3214c819635216df2dab77b682c6a1798d1d71a959ba4e7392aab9b8c0'
assert textsha(selfile)=='e818377083be1b581da718ae4cdb0741f074df313c0813e4239377b3754f25a5'
read=lambda f:json.loads(gzip.decompress(f.read_bytes())if f.suffix=='.gz'else f.read_bytes())
old=read(oldfile);ret=read(retfile);selection=read(selfile)
assert old['report']['R']==ret['report']['R']==560
out.mkdir(parents=True)
with(out/'factory-construction.log').open('w')as log:
 subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('run_portable.py')),str(source),str(hamming),str(out/'factory'),str(specfile)],stdout=log,stderr=subprocess.STDOUT,check=True)
sys.dont_write_bytecode=True;sys.path.insert(0,str(code));import gk_word as g
b=read(out/'factory/FULL-WORD.json.gz');assert b['report']['R']==560
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
assert profile=={1:2474,2:182,3:516,4:88,5:242,6:124,7:1,8:17}
assert Counter(widths)=={7:18,8:161,9:381}
assert sum(len(c['pivots'])for c in selection['kernel'])==99
counts={}
for part in ['A','B','cut','cleanup','precondition']:
 counts[part]=len(w.get(part,[]))
 for e in w.get(part,[]):
  assert e[0]in['add','scale']
  q=Fraction(e[3],e[4])if e[0]=='add'else Fraction(e[2],e[3]);n=abs(q.numerator);d=q.denominator
  assert not d&(d-1),(part,e)
  if e[0]=='scale':assert n>0 and not n&(n-1),(part,e)
norm=copy.deepcopy(w);assert norm.get('R',560)==norm['report']['R']==560;norm.pop('R',None)
for k in ['complex_coarse_float','gain_percent_float']:norm['report'].pop(k,None)
semantic=hashlib.sha256(json.dumps(norm,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert semantic=='d966e1481e0c09e4b7a0607429411046c6b3663ee83e6b8833958a745b82e337'
(out/'FULL-WORD.json.gz').write_bytes(g.dump(w));(out/'RETIMED-BASE.json.gz').write_bytes(g.dump(b));(out/'SELECTION.json').write_bytes(lf(selfile))
receipt=dict(status='PASS_SOURCE_BOUND_RANKSECTOR_AND_DYADIC_GATE',sources={label:rawsha(f)for label,f in [('prototype',hamming/'PROTOTYPE.json'),('packet_programs',hamming/'PACKET-PROGRAMS.json.gz'),('old_pair_base',oldfile),('retimed_pair_base',retfile)]},lf_source_hashes={label:textsha(f)for label,f in [('ranksector_constructor',source),('pair_spec',specfile),('selection',selfile),('gk_word.py',code/'gk_word.py'),('gk_common.py',code/'gk_common.py')]},normalized_word_sha256=semantic,word_sha256=rawsha(out/'FULL-WORD.json.gz'),profile=dict(profile),widths=dict(Counter(widths)),widths_ordered=widths,pivots=99,transferred_frames=transferred,dyadic_event_counts=counts,scope='Exact local source, rank-factor decoder, response relations, frame chains and dyadic contract; independent all-column, physical and outer replay remain separate.')
(out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
