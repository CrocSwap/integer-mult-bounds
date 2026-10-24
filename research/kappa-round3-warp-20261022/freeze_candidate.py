"""Deterministically normalize the discovery and emit a guarded solver-free patch."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz'


def span(B):
    s={0}
    for x in B:s|={y^x for y in tuple(s)}
    return s


def mv(cols,x):
    y=0
    for j,v in enumerate(cols):
        if x>>j&1:y^=v
    return y


def normalize():
    discovery=(HERE/'CANDIDATE-WORD.json.gz').read_bytes();d=json.loads(gzip.decompress(discovery))
    old=json.loads(gzip.decompress(BASE.read_bytes()));c=d['canonical'];b=old['canonical'];p=d['programs']['forward']
    oldG={w['op']:w['G_columns'] for w in b['warps']}
    for w in c['warps']:
        op=w['op'];classes=[e for e in p if e[0]=='warp' and abs(e[2])==op]
        def fits(e):
            a,z=e[3:5]
            if e[2]<0:a,z=z,a
            return {mv(oldG[op],x) for x in span(c['frames'][a])}==span(c['frames'][z])
        if all(fits(e) for e in classes):w['G_columns']=oldG[op]
        chosen=max((e for e in classes if e[2]>0),key=lambda e:len(c['frames'][e[3]]))
        w['from_frame'],w['to_frame']=chosen[3:5]
    used=set(c['start']+c['final'])
    for word in d['programs'].values():
        for e in word:
            if e[0] in ('climb','warp'):used.update(e[3:5])
            elif e[0]=='scalar':used.add(e[2])
            elif e[0]=='center':used.update(e[2:4])
    for w in c['warps']:used.update((w['from_frame'],w['to_frame']))
    n=len(b['frames']);keep=list(range(n))+sorted(x for x in used if x>=n);remap={x:i for i,x in enumerate(keep)}
    c['frames']=[c['frames'][i] for i in keep]
    for field in ('start','final'):c[field]=[remap[x] for x in c[field]]
    for word in d['programs'].values():
        for e in word:
            if e[0] in ('climb','warp'):e[3:5]=[remap[x] for x in e[3:5]]
            elif e[0]=='scalar':e[2]=remap[e[2]]
            elif e[0]=='center':e[2:4]=[remap[x] for x in e[2:4]]
    for w in c['warps']:
        for field in ('from_frame','to_frame'):w[field]=remap[w[field]]
    c['local_profile']=dict(Counter(e[5] for e in p if e[0]=='climb')+Counter(e[4] for e in p if e[0]=='center'))
    c['warp_edges']=sorted({(1 if e[2]>0 else -1,abs(e[2]),e[3],e[4]) for e in p if e[0]=='warp'})
    d['discovery_word_sha256']=sha256(discovery).hexdigest()
    d['scope']='Actual complete helper/map/contact word; unused appended discovery frames removed; unchanged native maps retained when every actual class admits them.'
    return d,old


def main():
    d,old=normalize();c=d['canonical'];b=old['canonical'];scalar=[];warps=[]
    A=[e for e in old['programs']['forward'] if e[0]!='climb'];B=[e for e in d['programs']['forward'] if e[0]!='climb']
    assert len(A)==len(B)
    for i,(a,z) in enumerate(zip(A,B)):
        assert a[0]==z[0]
        if a[0]=='scalar':
            assert a[1]==z[1]
            if a[2]!=z[2]:scalar.append([i,a[2],z[2]])
        elif a[0]=='warp':
            assert a[:3]==z[:3]
            if a[3:]!=z[3:]:warps.append([i,a[2],a[3],a[4],z[3],z[4]])
        else:assert a==z
    boundary={f:[[r,a,z] for r,(a,z) in enumerate(zip(b[f],c[f])) if a!=z] for f in ('start','final')}
    patch={'schema':'joint-helper-map-contacts/1','base_path':str(BASE.relative_to(ROOT)).replace('\\','/'),'base_sha256':sha256(BASE.read_bytes()).hexdigest(),
           'base_frame_count':len(b['frames']),'additional_frames':c['frames'][len(b['frames']):],
           'boundary_changes':boundary,'scalar_frame_changes':scalar,'warp_frame_changes':warps,'actual_operator_bindings':c['warps'],
           'discovery_word_sha256':d['discovery_word_sha256'],'scope':d['scope']}
    raw=json.dumps(d,sort_keys=True,separators=(',',':')).encode();compressed=gzip.compress(raw,mtime=0)
    frozen=HERE/'ACTUAL-WORD-FREEZE.json';receipt={'canonical_payload_sha256':sha256(raw).hexdigest(),'compressed_sha256':sha256(compressed).hexdigest(),
        'status':'FROZEN_PENDING_NATIVE_PHASE_ADMISSION','base_sha256':patch['base_sha256']}
    if frozen.exists():assert json.loads(frozen.read_text(encoding='utf-8'))==receipt,'Frozen witness changed'
    (HERE/'ACTUAL-WORD.json.gz').write_bytes(compressed)
    (HERE/'PATCH.json').write_text(json.dumps(patch,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    frozen.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(receipt,frames=len(c['frames']),boundary_changes={f:len(x) for f,x in boundary.items()},scalar_contacts=len(scalar),warp_pairs=len(warps)),sort_keys=True))


if __name__=='__main__':main()
