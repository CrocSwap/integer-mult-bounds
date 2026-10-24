#!/usr/bin/env python3
"""Exact source-bound coherent gauge checks. JoyboyBrian; Apache-2.0."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SHA = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source pin: ' + row['path'])
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(blob == row['git_blob'], 'source Git blob')
    raw = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SHA, 'literal word pin')
    return json.loads(gzip.decompress(raw))


def lam(frames, frame, t):
    return t if len(frames[frame]) == 9 else F(1)


def audit(src, orientation):
    c = src['canonical']; frames = c['frames']; program = src['programs'][orientation]
    need(c['h'] == 9 and c['v'] == 112, 'native dimension and main ports')
    need(len(c['start']) == len(c['final']) == 632, 'full role inventory')
    need(len(program) == 21449, 'complete event inventory')
    now = {('L', i): f for i, f in enumerate(c['start'])}
    paid = Counter(); warp = []; centers = []; blocks = []; block = None
    def frame(f):
        need(type(f) is int and 0 <= f < len(frames), 'frame id')
    def role(x):
        need(isinstance(x,list) and len(x)==2 and type(x[1]) is int, 'role syntax')
        need(x == ['C',0] or x[0]=='L' and 0<=x[1]<632, 'role extent')
        return tuple(x)
    for index,e in enumerate(program):
        kind=e[0]
        if kind=='scalar':
            _,g,f=e;frame(f);d=role(g[1]);op=g[0]
            if op=='clear':
                need(d==('C',0), 'only owned center cleared')
                if block is None:block=[]
                else:
                    block.append(index);blocks.append(block);block=None
                now[d]=f
            elif op=='copy':
                srcrole=role(g[2]);need(d==('C',0) and now.get(srcrole)==f, 'copy frame')
                now[d]=f
            elif op=='add':
                srcrole=role(g[2]);need(d!=srcrole and now.get(d)==now.get(srcrole)==f,'ADD common frame')
                need(F(g[3],g[4])!=0,'nonzero add')
            elif op=='scale':
                need(now.get(d)==f and F(g[2],g[3])!=0,'invertible SCALE')
            else:raise ValueError('unknown scalar')
        elif kind=='climb':
            _,tag,i,old,new,r=e;frame(old);frame(new)
            need(tag=='warp_retimed' and now.get(('L',i))==old,'paid source frame')
            need(type(r) is int and len(frames[new])-len(frames[old])==r>0,'paid rank')
            now['L',i]=new;paid[r]+=1
        elif kind=='center':
            _,i,old,new,r=e;frame(old);frame(new)
            need(block is not None and i==0 and now.get(('C',i))==old,'owned center frame')
            need({len(frames[old]),len(frames[new])}=={0,8} and r==8,'center rank pair')
            now['C',i]=new;paid[r]+=1;centers.append(index)
        elif kind=='warp':
            _,rr,w,old,new=e;d=role(rr);frame(old);frame(new)
            need(type(w) is int and 0<abs(w)<=len(c['warps']),'warp operator')
            need(now.get(d)==old and len(frames[old])==len(frames[new]),'warp rank/chronology')
            now[d]=new;warp.append(index)
        else:need(kind in ('adapter','phase'),'event type')
        if block is not None:block.append(index)
    need(block is None and len(blocks)==8 and len(centers)==8,'eight owned macros')
    for ids in blocks:
        need(len(ids)==26,'complete macro length')
        capture=set();fanout=set()
        for i in ids:
            e=program[i]
            if e[0]!='scalar' or e[1][0]=='clear':continue
            g=e[1]
            if g[1]==['C',0]:capture.add(tuple(g[2]))
            else:
                need(g[0]=='add' and g[2]==['C',0],'center fanout type');fanout.add(tuple(g[1]))
        need(capture and fanout and not capture&fanout,'unchanged disjoint captures')
    need([now['L',i] for i in range(632)]==c['final'],'all final frames')
    need(dict(paid)=={1:2201,2:412,3:510,4:127,5:40,8:8},'paid profile')
    need(len(warp)==240,'all warp count')
    pairs=[(len(frames[a]),len(frames[b])) for a,b in zip(c['start'],c['final'])]
    need(pairs[:112]==[(1,9)]*112 and pairs[112:224]==[(0,8)]*112,'main boundary ranks')
    need(all(a!=9 for a,b in pairs),'no rank nine inputs')
    helpers=Counter(pairs[224:])
    need(helpers=={(0,9):326,(1,9):41,(0,4):26,(1,8):6,(0,8):6,(5,9):2,(2,9):1},'all helper endpoints')
    return {'events':len(program),'warps':len(warp),'centers':len(centers),'persistent_roles':632,
            'paid_profile':{str(k):v for k,v in sorted(paid.items())},
            'helper_rank_pairs':{f'{a}->{b}':n for (a,b),n in sorted(helpers.items())},
            'scaled_helpers':sum(n for (a,b),n in helpers.items() if b==9),'unscaled_helpers':38}


def execute(src, orientation, initial, t):
    """Literal delta-zero source restriction; no predecessor executor imported."""
    c=src['canonical'];frames=c['frames']
    a={('L',i):F(x) for i,x in enumerate(initial)};a['C',0]=F(0)
    for e in src['programs'][orientation]:
        if e[0]=='scalar':
            g=e[1];op=g[0];d=tuple(g[1])
            if op=='clear':a[d]=F(0)
            elif op=='copy':a[d]=a[tuple(g[2])]
            elif op=='add':a[d]+=F(g[3],g[4])*a[tuple(g[2])]
            elif op=='scale':a[d]*=F(g[2],g[3])
            else:raise ValueError('scalar type')
        elif e[0] in ('climb','center'):
            if e[0]=='climb':_,_,i,old,new,_=e;d=('L',i)
            else:_,i,old,new,_=e;d=('C',i)
            a[d]*=lam(frames,new,t)/lam(frames,old,t)
        # Every homogeneous warp fixes delta_0 with phase one. Adapters are
        # source markers; their physical charts are retained in PROOF.md.
    need(a['C',0]==0,'owned center restored')
    return [a['L',i] for i in range(632)]


def ideal(orientation, x):
    y=x.copy()
    for i in range(112):
        if orientation=='forward':y[112+i]+=x[i]
        else:y[i]-=x[112+i]
    return y


def border(src,t,eps,x,y,helpers,second_helpers):
    # Formal Q=1 border specialization, not a physical Gaussian simulation.
    # Literal B followed by sign-conjugated source forward/backward.
    a=[x-y/eps]*112+[x]*112+helpers
    def signed(o,a):
        a=a.copy()
        for i in range(112,224):a[i]=-a[i]
        a=execute(src,o,a,t)
        for i in range(112,224):a[i]=-a[i]
        return a
    a=signed('forward',a)
    first_helper_outputs=a[224:]
    a=signed('backward',a[:224]+second_helpers)
    for i in range(112,224):a[i]*=eps
    return a,first_helper_outputs


def calculate(src):
    receipt={'scope':'additive coherent source countermodel; no admitted numerical caller','source_sha256':SHA,'orientations':{}}
    t=F(9,8);eps=F(1,16)
    for o in ('forward','backward'):
        receipt['orientations'][o]=audit(src,o)
        for seed in (17,23):
            x=[F((i*seed)%31-15,8) for i in range(632)]
            y=ideal(o,x)
            need(execute(src,o,x,F(1))==y,'ideal all-role endpoint')
            z=execute(src,o,x,t)
            need(z==[v*lam(src['canonical']['frames'],f,t) for v,f in zip(y,src['canonical']['final'])], 'gauge all-role endpoint')
    helpers=[F(i-204,16) for i in range(408)]
    second_helpers=[F(2*i-401,32) for i in range(408)]
    for tt in (F(1),t,F(257,256)):
        for x,y in ((F(0),F(1)),(F(2),F(-3))):
            a,first_outputs=border(src,tt,eps,x,y,helpers,second_helpers)
            expectedx=tt*tt*x-tt*(tt-1)*y/eps
            need(a[:112]==[expectedx]*112 and a[112:224]==[y]*112,'paired main endpoint')
            final=src['canonical']['final'][224:];frames=src['canonical']['frames']
            need(first_outputs==[h*lam(frames,f,tt) for h,f in zip(helpers,final)],'first independent helper bank endpoint')
            need(a[224:]==[h*lam(frames,f,tt) for h,f in zip(second_helpers,final)],'second independent helper bank endpoint')
    receipt['calibration']={'t':'9/8','epsilon':'1/16','upper_right':'-9/4','full_role_vectors_per_orientation':2,'paired_full_role_vectors':6,'paired_helper_banks':2,'paired_independent_helper_roles':816,'paired_replay_scope':'formal Q=1 specialization; arbitrary-Q claim proved in PROOF.md'}
    return receipt


def controls(src):
    mutations=[]
    bad=copy.deepcopy(src)
    w=next(e for e in bad['programs']['forward'] if e[0]=='warp');w[-1]=1
    mutations.append(('wrong warp endpoint',bad))
    bad=copy.deepcopy(src);bad['canonical']['final'][0]=0;mutations.append(('missing main full endpoint',bad))
    bad=copy.deepcopy(src);bad['canonical']['final'][224]=0;mutations.append(('lost helper endpoint',bad))
    bad=copy.deepcopy(src);bad['programs']['forward'].pop();mutations.append(('truncated source',bad))
    bad=copy.deepcopy(src)
    e=next(e for e in bad['programs']['forward'] if e[0]=='center');e[-1]=7
    mutations.append(('incorrect owned center',bad))
    for name,bad in mutations:
        try:audit(bad,'forward')
        except (ValueError,KeyError,IndexError):continue
        raise ValueError('accepted mutation: '+name)
    # A false conclusion that coherence eliminates the pole must fail.
    need(F(9,8)*(F(9,8)-1)/F(1,16)!=0,'pole-discarding control')
    return [name for name,_ in mutations]+['discarded nonzero pole']


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--regenerate',action='store_true');args=parser.parse_args()
    src=load();receipt=calculate(src);receipt['rejecting_controls']=controls(src)
    path=HERE/'RESULT.json'
    if args.regenerate:path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads(path.read_text()),sort_keys=True,separators=(',',':'))==json.dumps(receipt,sort_keys=True,separators=(',',':')),'frozen receipt mismatch')
    print('PASS_COHERENT_FRESH_D_BOUNDARY: both complete source words, all 632 endpoints, correlated pole; no supplier admission')

if __name__=='__main__':main()
