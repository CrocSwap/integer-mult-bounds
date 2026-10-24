"""Reconstruct the selected 92-pivot partial-own complex word.
Apache-2.0. Prepared with OpenAI Codex assistance; retain PR507/484 notices.
Usage: python -B build_kernel92.py GK_CODE PARTIAL_BASE KERNEL84_SELECTION
       RETIME_MAP KERNEL92_SELECTION NEW_OUTPUT_DIR
No discovery search runs. Actual physical allocation is independently checked.
"""
from pathlib import Path
import json,gzip,sys,copy,hashlib
from collections import Counter
if not __debug__:raise RuntimeError('Assertions must remain enabled')
code,basefile,s84file,mapfile,s92file,out=map(Path,sys.argv[1:]);assert not out.exists();sys.dont_write_bytecode=True;sys.path.insert(0,str(code));import gk_word as g
read=lambda p:json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
base=read(basefile);s84=read(s84file);s92=read(s92file);fm=read(mapfile)
assert base['report']['R']==560 and len(base['A'])==2680 and len(base['B'])==840
assert sum(len(c['pivots'])for c in s84['kernel'])==84
assert sum(len(c['pivots'])for c in s92['kernel'])==92
wanted=copy.deepcopy(s84['gauge'])
for h in ['540','541','542','543']:wanted[h]=[408,102]
assert s92['gauge']==wanted
w84=g.build(base,s84);r=copy.deepcopy(w84)
for part in ['A','B']:
 seen=set()
 for i,old,new in fm[part]:
  assert i not in seen and r[part][i][-1]==old,(part,i);seen.add(i);r[part][i][-1]=new
 assert [e[:-1]for e in r[part]]==[e[:-1]for e in w84[part]]
assert r['A'][:671]==w84['A'][:671]
assert g.profile(r)==Counter({int(k):v for k,v in fm['expected_local_profile'].items()})
ret=copy.deepcopy(base)
for part in ['A','B']:
 tail=r[part][-len(base[part]):];assert [e[:-1]for e in tail]==[e[:-1]for e in base[part]];ret[part]=copy.deepcopy(tail)
ret['cleanup']=[g.inverse(e,g.FULL)for e in reversed(ret['A']+ret['B'])if not 120<=e[1]<240]
w=g.build(ret,s92);H=g.profile(w);widths=g.widths_of(w)
assert H=={1:2539,2:160,3:530,4:88,5:298,6:68,7:1,8:17}
assert Counter(widths)=={7:18,8:154,9:388}
# Normalize only the established inherited floating display fields and redundant R.
norm=copy.deepcopy(w);assert norm.get('R',norm['report']['R'])==norm['report']['R']==560;norm.pop('R',None)
for k in ['complex_coarse_float','gain_percent_float']:norm['report'].pop(k,None)
semantic=hashlib.sha256(json.dumps(norm,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert semantic=='c6e758b324d3566e8443b3fd3d739c4d01e1928eadbee40f5c36973404b0640b'
out.mkdir(parents=True);(out/'FULL-WORD.json.gz').write_bytes(g.dump(w));(out/'SELECTION.json').write_text(json.dumps(s92,indent=2)+'\n');(out/'RETIMED-BASE.json.gz').write_bytes(g.dump(ret))
receipt=dict(status='PASS_EXACT_SOURCE_BOUND_KERNEL92_RECONSTRUCTION',sources={label:hashlib.sha256(path.read_bytes()).hexdigest()for label,path in [('partial_base',basefile),('kernel84_selection',s84file),('frame_map',mapfile),('kernel92_selection',s92file),('gk_word.py',code/'gk_word.py'),('gk_common.py',code/'gk_common.py')]},normalized_word_sha256=semantic,word_sha256=hashlib.sha256((out/'FULL-WORD.json.gz').read_bytes()).hexdigest(),profile=dict(H),widths=dict(Counter(widths)),widths_ordered=widths,pivots=92,entrance_rank=sum(9-x for x in widths),scope='Exact local source construction; arbitrary-dirt scalar, physical phases/owners and final outer assembly checked separately.')
(out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'])
