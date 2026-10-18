"""Independent exact scalar/frame audit of the changed forward supplier.

This does not import a generator, builder, stored compensation, or price.
All claimed endpoint matrices are derived from the input word's gates.
Optional --main checks the transported boundary against the pinned parent.
Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0.
"""
import argparse,gzip,json,hashlib,time
from pathlib import Path
from fractions import Fraction as F
from collections import Counter

def require(x,label):
    if not x:raise RuntimeError(label)

def basis(vs):
    piv={}
    for a in vs:
        while a:
            bit=a.bit_length()-1
            if bit in piv:a^=piv[bit]
            else:
                piv[bit]=a;break
    for k in sorted(piv):
        for j in piv:
            if j>k and piv[j]>>k&1:piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))

def contained(a,b):return basis(a+b)==b

def registers(e):return e[1:3] if e[0]=='add' else e[1:2]

def apply(e,rows,dual=False):
    if e[0]=='add':
        t,s=e[1:3];q=F(e[3],e[4]);require(t!=s,'self add')
        if dual:t,s,q=s,t,-q
        dst=rows[t]
        for k,x in list(rows[s].items()):
            a=dst.get(k,F(0))+q*x
            if a:dst[k]=a
            else:dst.pop(k,None)
    elif e[0]=='scale':
        t=e[1];q=F(e[2],e[3]);require(q!=0,'zero scale')
        if dual:q=1/q
        rows[t]={k:q*x for k,x in rows[t].items()}
    else:raise RuntimeError('unknown scalar primitive')

def invert(e):
    r=list(e)
    if r[0]=='add':r[3]=-r[3]
    else:r[2],r[3]=r[3],r[2]
    return r

def check_parent_interface(word,main):
    # Read only the retained boundary data. No builder or local checker is imported.
    relative="research/community-k492-audit/pr622/replay/baseline558/complex-global/base/split-centres/CANONICAL-WORD.json.gz"
    path=main/relative;raw=path.read_bytes()
    require(hashlib.sha256(raw).hexdigest()=="66d3c3c70983224650643a0a05a21ac6c6959f84d0f4528650601016f5a76844",'parent canonical input pin')
    parent=json.loads(gzip.decompress(raw))
    tau=lambda x:x^(43 if (x&43).bit_count()%2 else 0)
    ports=parent['ports'];v=word['report']['v']
    require(len(ports)==len(set(ports))==v,'parent port count')
    require(set(map(tau,word['ports']))==set(ports),'transported source/target ports')
    moved={i:ports.index(tau(p)) for i,p in enumerate(word['ports'])}
    centers=[moved.get(r,r) for r in word['centers']]
    actual=[list(basis([tau(x) for x in frame])) for frame in word['center_frames']]
    expected=[parent['frames'][f] for f in parent['center_frames']]
    require(len(centers)==len(set(centers))==len(actual)==8,'eight distinct centre carriers')
    require(actual==expected and all(len(f)==8 for f in actual),'ordered centre frame interface')
    return dict(parent_path=relative,parent_file_sha256=hashlib.sha256(raw).hexdigest(),
                transport_tau=43,ordered_frame_bases_match=True,all_ports_match=True,
                transported_centers=centers,source_centers=[r for r in centers if r<v],
                ordered_frame_bases=actual)


def run(path,out,main=None):
    begin=time.monotonic();data=gzip.decompress(path.read_bytes());w=json.loads(data)
    v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
    require((v,h)==(112,9),'wrong source geometry')
    center_interface=check_parent_interface(w,main) if main is not None else None
    ident=lambda:[{k:F(1)} for k in range(n)]
    main=w['A']+w['cut']+w['B']
    for e in main+w['precondition']+w['cleanup']:
        require(all(0<=k<n for k in registers(e)),'register out of range')
        q=F(e[3],e[4]) if e[0]=='add' else F(e[2],e[3])
        require(q.denominator&(q.denominator-1)==0,'non-dyadic scalar')
        if e[0]=='scale':require(abs(q.numerator)&(abs(q.numerator)-1)==0,'non-unit scale')
    require(all(not(v<=e[2]<2*v) for e in w['A']+w['B'] if e[0]=='add' and not(v<=e[1]<2*v)), 'non-target reads target')
    raw=ident()
    for e in main:apply(e,raw)
    dirt=[{} for _ in range(n)]
    for y in range(v,2*v):dirt[y]={k:a for k,a in raw[y].items() if k>=2*v}
    for e in w['precondition']:apply(e,dirt)
    compensation=[['add',y,k,-a.numerator,a.denominator,[]] for y in range(v,2*v) for k,a in sorted(dirt[y].items())]
    entering=set(map(int,w.get('start_extra',{})));lowends=set(map(int,w.get('helper_final',{})))
    coldends=lowends-entering
    require(not any(e[2] in entering for e in compensation),'nonzero entrance response')
    require(not any(r in entering|coldends for e in w['precondition']+compensation for r in registers(e)), 'pre-wrapper touch of residual helper')
    require(all(e[-1]==[] for e in w['precondition']+compensation),'nonzero frame precondition')
    early=w.get('early_cleanup',[]);earlyids={i for i,U in early}
    require(len(earlyids)==len(early),'duplicate early cleanup gate')
    tail=[w['cleanup'][i][:-1]+[U] for i,U in early]
    cleanup=[e for i,e in enumerate(w['cleanup']) if i not in earlyids]
    prefix=w['precondition']+compensation+main
    program=prefix+tail+cleanup
    for dual in (False,True):
        actual=ident()
        for e in program:apply(e,actual,dual)
        expected=ident()
        for t in range(v):expected[t if dual else v+t][v+t if dual else t]=F(-1 if dual else 1)
        bad=[i for i in range(n) if actual[i]!=expected[i]]
        require(not bad,'all-column endpoint failure '+str((dual,bad[:8])))
        print('endpoint', 'dual' if dual else 'forward','PASS',flush=True)
    full=basis([1<<i for i in range(h)])
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w.get('helper_final',{}).items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w.get('start_extra',{}).items():
        require(2*v<=int(q)<n,'non-helper entrance');start[int(q)]=basis(U)
    cur=start.copy();paid=Counter()
    def climb(q,U):
        U=basis(U);require(contained(cur[q],U),'frame not monotone '+str((q,cur[q],U)))
        d=len(U)-len(cur[q])
        if d:paid[d]+=1
        cur[q]=U
    for section in ('A','B'):
        if section=='B':
            lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
            require(all(cur[v+t]==lev.get(t,()) for t in range(v)),'target centre levels')
            for q,U in zip(w['centers'],w['center_frames']):
                U=basis(U);require(cur[q]==U,'center frame')
                served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
                for T in sorted(served,key=lambda x:-len(x)):
                    require(contained(T,U),'center path not nested')
                    if T!=U:paid[len(U)-len(T)]+=1
                    U=T
        for e in w[section]:
            for q in registers(e):climb(q,e[-1])
    endB=cur.copy()
    for e in tail:
        for q in registers(e):climb(q,e[-1])
    for q,U in enumerate(end):climb(q,U)
    require(all(all(end[q]==full for q in registers(e)) for e in cleanup),'full cleanup reads a low end')
    require(dict(paid)=={int(k):a for k,a in w['report']['local_profile'].items()},'paid profile mismatch')
    inventory=Counter(len(end[q])-len(start[q]) for q in range(2*v,n))
    require(dict(inventory)=={int(k):a for k,a in w['report']['width_inventory'].items()},'width inventory mismatch')
    p=ident();pinv=ident()
    for e in prefix:apply(e,p)
    for e in reversed(prefix):apply(invert(e),pinv)
    for q in lowends:
        U=end[q]
        require(all(contained(endB[k],U) for k in pinv[q]),'inverse-row cone '+str(q))
        require(all(k==q or not p[k].get(q) or contained(endB[k],U) for k in range(n)),'dirt-column cone '+str(q))
    report=dict(status='PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES',
                input_file=path.name,content_sha256=hashlib.sha256(data).hexdigest(),
                compressed_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                parent_center_interface=center_interface,v=v,h=h,R=R,
                entering=len(entering),lowends=len(lowends),coldends=len(coldends),
                compensation_gates=len(compensation),local_profile=dict(sorted(paid.items())),
                width_inventory=dict(sorted(inventory.items())),checked_columns=n,
                elapsed_seconds=time.monotonic()-begin,
                scope='Exact rational full scalar map in both orientations; all literal native frame chains, center levels, dyadic units, entrance-zero response, wrapper exclusion and final helper row/column cones. No global owner admission or exponent repricing.')
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word',type=Path,required=True,help='FULL-WORD.json.gz to check')
    parser.add_argument('--output',type=Path,required=True,help='JSON receipt output path')
    parser.add_argument('--main',type=Path,help='Optional pinned main checkout: also verify the transported centre/port interface')
    args=parser.parse_args()
    run(args.word,args.output,args.main)
