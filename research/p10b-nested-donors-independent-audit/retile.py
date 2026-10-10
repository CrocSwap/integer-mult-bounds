"""Build a distinct exact tiling directly from literal endpoint ranks.
OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from pathlib import Path
import json
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--proof',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
proof=args.proof/'candidate'
st=json.loads((proof/'249-states.json').read_text());frames=json.loads((proof/'frames.json').read_text())['frames']
initial=json.loads((proof/'COHORT249-INITIAL.json').read_text());final=json.loads((proof/'COHORT249-FINAL.json').read_text())
# Recover endpoint dictionary representation without importing native tools.
assert isinstance(initial,dict) and isinstance(final,dict)

census=Counter(frames[str(st['final'][str(i)])]['dim']-frames[str(st['initial'][str(i)])]['dim'] for i in range(2*st['v'],st['n']))
assert 0 not in census
remaining=Counter({w:300*n for w,n in census.items()});patterns=[]
def use(widths,count):
    assert count>0 and sum(widths)==100
    for w,n in Counter(widths).items():
        remaining[w]-=count*n;assert remaining[w]>=0
    patterns.append(dict(count=count,widths=widths))
# Intentionally different from the native canonical packing.
use([19,19,19,3,20,20],300)
for w,group,filler in [(19,4,[20,4]),(18,4,[20,4,4]),(16,5,[20]),(15,4,[20,20]),(13,4,[20,20,4,4]),(12,5,[20,20]),(3,20,[20,20])]:
    assert remaining[w]%group==0
    if remaining[w]:use([w]*group+filler,remaining[w]//group)
for w in (20,4):
    assert remaining[w]%(100//w)==0
    if remaining[w]:use([w]*(100//w),remaining[w]//(100//w))
assert all(n==0 for n in remaining.values())
assert 100*sum(p['count']for p in patterns)==300*sum(w*n for w,n in census.items())
out=dict(census=dict(sorted(census.items())),physical_replicas=300,patterns=patterns,scope='Independent exact packing from current actual endpoint ranks, including an alternate mixed19/3 pattern.')
dest=args.output;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(out,indent=2)+'\n')
print('PASS distinct actual-endpoint tiling',sum(p['count']for p in patterns),census)
