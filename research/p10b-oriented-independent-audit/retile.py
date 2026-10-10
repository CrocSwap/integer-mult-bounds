"""Independent exact width-100 tiling from actual endpoint ranks at T=300.
OpenAI Codex assistance; Apache-2.0. No construction-bank imports.
"""
import argparse,json
from collections import Counter
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--proof',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
c=a.proof/'candidate';st=json.loads((c/'249-states.json').read_text());frames=json.loads((c/'frames.json').read_text())['frames'];assert json.loads((c/'frames.json').read_text())['h']==20
census=Counter(frames[str(st['final'][str(i)])]['dim']-frames[str(st['initial'][str(i)])]['dim']for i in range(2*st['v'],st['n']))
assert all(0<w<=20 for w in census)
rem=Counter({w:300*n for w,n in census.items()});patterns=[]
def use(widths,count):
    assert count>0 and sum(widths)==100
    for w,n in Counter(widths).items():rem[w]-=count*n;assert rem[w]>=0,(w,rem[w])
    patterns.append(dict(count=count,widths=widths))
# A mixed anchor makes this tiling intentionally different from the producer.
if rem[19]>=900 and rem[3]>=300 and rem[20]>=600:use([19,19,19,3,20,20],300)
for w in sorted(set(census)-{4,20},reverse=True):
    if not rem[w]:continue
    groups=[g for g in range(1,101//w+1)if 300%g==0 and g*w<=100 and (100-g*w)%4==0]
    assert groups,(w,'no independent pattern')
    g=max(groups);assert rem[w]%g==0
    left=100-g*w;twenties=left//20;fours=(left-20*twenties)//4
    use([w]*g+[20]*twenties+[4]*fours,rem[w]//g)
# Complete the remaining 20/4 inventory, including a non-pure bridge if needed.
r=rem[20]%5
if r:use([20]*r+[4]*(25-5*r),1)
if rem[20]:use([20]*5,rem[20]//5)
assert rem[4]%25==0
if rem[4]:use([4]*25,rem[4]//25)
assert all(n==0 for n in rem.values())
assert 100*sum(p['count']for p in patterns)==300*sum(w*n for w,n in census.items())
r=dict(census=dict(sorted(census.items())),physical_replicas=300,patterns=patterns,scope='Independent deterministic exact packing built only from actual endpoint ranks; optional mixed19/3 anchor and20/4 completion.')
a.output.parent.mkdir(parents=True,exist_ok=True);assert not a.output.exists();a.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS independent generic endpoint tiling',sum(p['count']for p in patterns),dict(census))
