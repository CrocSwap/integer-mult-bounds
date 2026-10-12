"""Reconstruct the coordinated word from the pinned partial-own factory."""
from pathlib import Path
import json,gzip,sys,copy
GROOT,B,SEL,EXPECTED,OUT=map(Path,sys.argv[1:6]);sys.path.insert(0,str(GROOT/'code'));import gk_word as G
raw=json.load(gzip.open(B/'sc_base/FULL-WORD.json.gz'));full=json.load(gzip.open(B/'split-centres/FULL-WORD.json.gz'));sel=json.load(open(GROOT.parents[2]/'data/KERNEL-SELECTION.json'))
n=len(full['A'])-len(raw['A']);assert n>=0
assert [e[:-1]for e in raw['A']]==[e[:-1]for e in full['A'][n:]]
assert [e[:-1]for e in raw['B']]==[e[:-1]for e in full['B']]
raw['A']=full['A'][n:];raw['B']=full['B'];raw['cleanup']=[G.inverse(e,G.FULL)for e in reversed(raw['A']+raw['B'])if not 120<=e[1]<240]
baseline=G.build(raw,sel);assert baseline['A']==full['A']and baseline['B']==full['B']and G.profile(baseline)==G.profile(full)
newsel=json.load(open(SEL));expectedsel=copy.deepcopy(sel)
for h in [540,541,542,543]:expectedsel['gauge'][str(h)]=[408,102]
assert newsel==expectedsel
word=G.build(raw,newsel);assert word==json.load(gzip.open(EXPECTED));OUT.write_bytes(G.dump(word))
print('PASS_RECONSTRUCT_COORDINATED_PARTIAL_WORD',n)
