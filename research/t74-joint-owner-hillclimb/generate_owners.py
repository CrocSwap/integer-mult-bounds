"""Regenerate the complete changed owner map from pinned source plus moves.

Coordinates are (stage, replica, new compact helper); physical addresses and
offsets are explicit certificate data. The separate verifier checks them all.
"""
from pathlib import Path
import argparse,gzip,hashlib,json

P=Path(__file__).resolve().parent
DROP={384,386,387,388}
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    src=a.source_root/'research/gmx-t74-borrow43-width-exchange';f=src/'OWNERS.json.gz';pins=read(P/'UPSTREAM-2312.json')['files'];wanted=next(x['sha256']for x in pins if x['path']=='research/gmx-t74-borrow43-width-exchange/OWNERS.json.gz')
    if hashlib.sha256(f.read_bytes()).hexdigest()!=wanted:raise ValueError('immutable owner input changed')
    plan=read(src/'new/PLAN.json');order=read(P/'CALL-ORDER.json');at={tuple(x):i for i,x in enumerate(order)}
    patch=read(P/'OWNER-MOVES.json.gz');cols=patch['columns'];moves={tuple(z[:3]):dict(zip(cols,z))for z in patch['rows']};seen=set();rows=[]
    for old in read(f):
        h=old['helper']
        if h in DROP:continue
        z=dict(old);z['helper']=h-sum(k<h for k in DROP);key=z['stage'],z['replica'],z['helper']
        if key in moves:
            seen.add(key)
            for k in('owner_replica','child','port','offset'):z[k]=moves[key][k]
        z['time']=at[z['stage'],z['replica']];r,c,v=z['owner_replica'],z['child'],z['port'];z['copy']=r*112+v;z['family']=r*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+v;rows.append(z)
    if seen!=set(moves):raise ValueError('unknown/duplicate role move')
    rows.sort(key=lambda z:(z['time'],z['helper']));expected=read(P/'data/OWNERS.json.gz')
    if rows!=expected:raise ValueError('regenerated owner map differs')
    a.out.parent.mkdir(parents=True,exist_ok=True);data=gzip.compress(canonical(rows),mtime=0);a.out.write_bytes(data)
    print('PASS_REGENERATED_COMPLETE_OWNER_MAP',len(rows),'semantic_sha256',hashlib.sha256(canonical(rows)).hexdigest(),flush=True)

if __name__=='__main__':main()
