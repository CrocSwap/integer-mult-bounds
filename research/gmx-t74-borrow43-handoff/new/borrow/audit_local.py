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


def run(path,out,main=None,base=None):
    begin=time.monotonic();data=gzip.decompress(path.read_bytes());w=json.loads(data)
    if w.get('kind')=='BORROW-WORD':return run_borrow(path,out,main,base,w,data,begin)
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

# ---------------------------------------------------------------------------------------------
# BORROW-WORD extension (anticipatory dirty borrowing, #2226 construction on the T74 words).
# Everything below is new; run() above is unchanged except for the dispatch on w['kind'].
# ---------------------------------------------------------------------------------------------
def dot(a,b):return (a&b).bit_count()&1

def gmul(cols,x):
    # G given by its columns: cols[i] = G(e_i) as a bit mask; returns G(x)
    y=0;i=0
    while x:
        if x&1:y^=cols[i]
        x>>=1;i+=1
    return y

def ginv(cols,h):
    # inverse columns over F2 (None if singular), Gauss-Jordan on (G | I) column-wise
    piv={};
    for i in range(h):
        a=cols[i];b=1<<i
        while a:
            t=a.bit_length()-1
            if t in piv:a^=piv[t][0];b^=piv[t][1]
            else:piv[t]=(a,b);break
    if len(piv)<h:return None
    # reduce: for each unit vector e_t find preimage
    pre=[]
    for t in range(h):
        a=1<<t;b=0
        for s in sorted(piv,reverse=True):
            if a>>s&1:a^=piv[s][0];b^=piv[s][1]
        if a:return None
        pre.append(b)
    return pre   # pre[t] = G^{-1}(e_t)

def gtrans(cols,h):
    # transpose: column j of G^T = row j of G
    return [sum(((cols[i]>>j)&1)<<i for i in range(h)) for j in range(h)]

def perp(U,h):
    # orthogonal complement of span(U) under the standard dot product on F2^h
    return basis([x for x in range(1,1<<h) if all(dot(x,u)==0 for u in U)]) if h<=12 else None

def lagrangian(U,h):
    # L_U={(x,z):x in U,z in x+U^perp}; vector = x | z<<h ; spanned by (u,u) and (0,p)
    P=perp(U,h)
    return basis([u|(u<<h) for u in U]+[p<<h for p in P])

def check_warp(op,rec,h):
    """Exact static checks of one K_G warp; raises RuntimeError. Returns dict."""
    require(isinstance(rec,list) and len(rec)==5,'warp record shape')
    pos,lender,cols,U,E=rec
    require(len(cols)==h and all(isinstance(c,int) and 0<=c<(1<<h) for c in cols),'G column shape')
    check_G_frames(cols,U,E,h)
    return dict(position=pos,lender=lender,dim=len(U))

def check_G_frames(cols,U,E,h):
    """static K_G checks of the operator `cols` for the frame pair U -> E (used for B-phase warps and for A-phase prelude warps)"""
    inv=ginv(cols,h);require(inv is not None,'G not invertible')
    require(all(gmul(cols,inv[t])==1<<t for t in range(h)),'G inverse witness')
    U=list(U);E=list(E)
    require(len(basis(U))==len(U) and len(basis(E))==len(E),'warp frames are not bases')
    require(len(U)==len(E),'dim(from)!=dim(to)')
    require(all(0<=x<(1<<h) for x in U+E),'frame out of range')
    require(basis([gmul(cols,x) for x in U])==basis(E),'G(from)!=to')
    # symplectic form of K_G on F2^{2h}, vector = x | z<<h, columns of M: (x,z)->(Gx, (G+G^-T)x + G^-T z)
    GiT=gtrans(inv,h)        # G^{-T}: columns j = row j of G^{-1}
    # G^{-T}(z): via columns GiT
    def M(vec):
        x=vec&((1<<h)-1);z=vec>>h
        gx=gmul(cols,x);S=gx^gmul(GiT,x)   # (G + G^{-T}) x
        return gx|((S^gmul(GiT,z))<<h)
    sw=lambda vec:(vec>>h)|((vec&((1<<h)-1))<<h)
    sym=lambda a,b:dot(a,sw(b))             # omega((x,z),(x',z'))=x.z'+z.x'
    gens=[1<<k for k in range(2*h)]
    img=[M(g) for g in gens]
    require(all(sym(img[a],img[b])==sym(gens[a],gens[b]) for a in range(2*h) for b in range(a+1,2*h)),'K_G not symplectic')
    require(all(M(1<<k)==M(1<<k) for k in range(2*h)),'unreachable')
    L0=basis([1<<k for k in range(h,2*h)]);LF=basis([(1<<k)|(1<<(k+h)) for k in range(h)])
    require(basis([M(x) for x in [1<<k for k in range(h,2*h)]])==L0,'K_G does not fix L_0')
    require(basis([M(x) for x in [(1<<k)|(1<<(k+h)) for k in range(h)]])==LF,'K_G does not fix L_FULL')
    LU=lagrangian(U,h);LE=lagrangian(E,h)
    require(len(LU)==h==len(LE),'frame Lagrangian dimension')
    require(basis([M(x) for x in LU])==LE,'K_G(L_from)!=L_to')
    # dual orientation uses G^{-T}: it must map from^perp to to^perp
    require(basis([gmul(GiT,x) for x in perp(U,h)])==perp(E,h),'dual frame map')

def fraction_row(e):
    return F(e[3],e[4]) if e[0]=='add' else F(e[2],e[3])

def walg_add(dst,src,c):
    for k,x in src.items():
        a=dst.get(k,F(0))+c*x
        if a:dst[k]=a
        else:dst.pop(k,None)

def walg_warp(row,op):
    # K_op acts on every stored operator word: left multiply by op, cancelling an adjacent inverse
    out={}
    for (var,word),x in row.items():
        out[var,word[1:] if word and word[0]==-op else (op,)+word]=x
    return out

def walg_apply(e,rows,dual,dsym):
    """e: scalar gate list (add/scale) or ['warp',reg,signed_op,...]; free-algebra action."""
    if e[0]=='corr':
        _,t,src,word,c=e
        if not dual:
            row=rows[src]
            for op in reversed(word):row=walg_warp(row,op)
            walg_add(rows[t],row,c)
        else:
            row=rows[t]
            # transpose of the gate t+=c K s is s-=c K^T t, and K^T=(K^{-T})^{-1}=D^{-1}: a word K_o1..K_ok becomes D_ok^-1..D_o1^-1
            for op in word:row=walg_warp(row,-((op>0)-(op<0))*(abs(op)+dsym))
            walg_add(rows[src],row,-c)
        return
    if e[0]=='warp':
        op=e[2];s=(op>0)-(op<0)
        if dual:op=s*(abs(op)+dsym)     # dual orientation: K_G^{-T} is a distinct free symbol
        rows[e[1]]=walg_warp(rows[e[1]],op);return
    if e[0]=='add':
        t,s=e[1:3];q=F(e[3],e[4]);require(t!=s,'self add')
        if dual:t,s,q=s,t,-q
        walg_add(rows[t],rows[s],q)
    else:
        t=e[1];q=F(e[2],e[3]);require(q!=0,'zero scale')
        if dual:q=1/q
        rows[t]={k:q*x for k,x in rows[t].items()}

def invert_item(e,full):
    if e[0]=='warp':return ['warp',e[1],-e[2]]
    r=list(e)
    if r[0]=='add':r[3]=-r[3]
    else:r[2],r[3]=r[3],r[2]
    return r

def run_borrow(path,out,main,base,w,data,begin):
    v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
    require((v,h)==(112,9),'wrong source geometry')
    require(main is None,'--main parent interface is not available for coordinate-changed BORROW-WORD; use --base')
    full=basis([1<<i for i in range(h)]);FULLB=list(full)
    removed=set(w['removed']);require(all(2*v<=r<n for r in removed) and len(removed)==len(w['removed']),'removed must be distinct helpers')
    live=[r for r in range(n) if r not in removed];liveset=set(live)
    istarget=lambda r:v<=r<2*v
    warps=w['warps'];K=len(warps)
    # --- 1. warp records (static exact checks) ------------------------------------------------
    for op,rec in enumerate(warps,1):
        check_warp(op,rec,h)
        require(rec[1] in liveset and not istarget(rec[1]),'lender must be a remaining non-target register')
        require(0<=rec[0]<=len(w['B']),'warp position')
    print('warps',K,'PASS static K_G checks',flush=True)
    # --- 2. gate hygiene ----------------------------------------------------------------------
    sections={k:w[k] for k in ('precondition','compensation','A','cut','B','restore')}
    cleanup_given=w.get('cleanup')
    for name,sec in list(sections.items())+([('cleanup',cleanup_given)] if cleanup_given is not None else []):
        for e in sec:
            if e[0]=='warp':
                require(name in('cleanup','A','B'),'warp item outside cleanup list/prelude')
                require(len(e)==(5 if name in('A','B') else 4),'warp item shape')
                require(abs(e[2])<=K and e[2]!=0,'warp operator id')
                require((e[1] in liveset or (name=='cleanup' and e[1]-n in liveset)),'warp register');continue
            require(e[0] in('add','scale'),'unknown scalar primitive')
            regs=registers(e)
            if name=='cleanup':require(all((r in liveset) or (n<=r<2*n and r-n in liveset) for r in regs),'register out of range/removed')
            else:require(all(r in liveset for r in regs),'register out of range or removed helper referenced')
            q=fraction_row(e)
            require(q.denominator&(q.denominator-1)==0,'non-dyadic scalar')
            if e[0]=='scale':require(abs(q.numerator)&(abs(q.numerator)-1)==0,'non-unit scale')
            if e[0]=='add':require(e[1]!=e[2],'self add')
    require(all(not(v<=e[2]<2*v) for e in w['A']+w['B']+w['restore'] if e[0]=='add' and not(v<=e[1]<2*v)),'non-target reads target')
    # wrapper / compensation sections only write targets at the zero frame
    for e in w['precondition']+w['compensation']:
        require(e[-1]==[] and istarget(e[1]),'wrapper gate must be a zero-frame target write')
    require(all(e[-1] is None and istarget(e[1]) for e in w['cut']),'cut gates must be unframed target writes')
    require(all(not istarget(e[1]) for e in w['restore']),'restoration writes only non-targets')
    entering=set(map(int,w.get('start_extra',{})));restored=set(map(int,w.get('helper_final',{})))
    require(all(2*v<=q<n and q in liveset for q in entering|restored),'start_extra/helper_final must name remaining helpers')
    require(not any(e[2] in entering for e in w['compensation'] if e[0]=='add'),'nonzero entrance response')
    require(not any(r in entering|restored for e in w['precondition']+w['compensation'] for r in registers(e)),'pre-wrapper touch of residual helper')
    # --- 3. initial anticipatory corrections (the relaxed compensation rule) ---------------
    corr=w['initial_corrections']
    for t in corr:
        word=tuple(t['operator_word']);c=F(t['coefficient'])
        require(istarget(t['target']),'correction target')
        s=t['source'];require(s in liveset and s>=2*v,'correction source must be a remaining helper')
        require(s not in entering,'correction source has nonzero entrance frame')
        require(len(word)>=1 and all(1<=abs(o)<=K for o in word),'correction operator word')
        require(c!=0 and c.denominator&(c.denominator-1)==0,'correction coefficient')
        # the source is the lender of the operator it is read through
        require(all(warps[abs(o)-1][1]==s for o in word),'correction source is not the lender of its operator')
    # --- 4. frames: literal chain, monotone, paid profile ---------------------------------------
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w.get('helper_final',{}).items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w.get('start_extra',{}).items():start[int(q)]=basis(U)
    cur=start.copy();paid=Counter()
    def climb(q,U):
        U=basis(U);require(contained(cur[q],U),'frame not monotone '+str((q,cur[q],U)))
        d=len(U)-len(cur[q])
        if d:paid[d]+=1
        cur[q]=U
    npre=w.get('prelude_events',0);prelude=w['A'][:npre];Aord=w['A'][npre:]
    require(all(e[0]=='warp' or (istarget(e[1]) and e[0] in('add','scale')) for e in prelude),'prelude items must be warps or target writes')
    require(all(e[0]!='warp' for e in Aord),'warp item after the prelude')
    for e in prelude:
        if e[0]=='warp':
            _,r_,op_,fr_,to_=e;rec_=warps[abs(op_)-1]
            require(rec_[1]==r_ and op_!=0 and abs(op_)<=K,'prelude warp operator/lender')
            check_G_frames(rec_[2],list(fr_) if op_>0 else list(to_),list(to_) if op_>0 else list(fr_),h)
            require(cur[r_]==basis(fr_),'prelude warp frame mismatch '+str((r_,op_)))
            cur[r_]=basis(to_)
        else:
            for q in registers(e):climb(q,e[-1])
    for e in Aord:
        for q in registers(e):climb(q,e[-1])
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    require(all(cur[v+t]==lev.get(t,()) for t in range(v)),'target centre levels')
    for q,U in zip(w['centers'],w['center_frames']):
        U=basis(U);require(cur[q]==U,'center frame')
        served={lev.get(e[1]-v,()) for e in w['cut'] if e[2]==q}
        for T in sorted(served,key=lambda x:-len(x)):
            require(contained(T,U),'center path not nested')
            if T!=U:paid[len(U)-len(T)]+=1
            U=T
    byposition={}
    for op,rec in enumerate(warps,1):byposition.setdefault(rec[0],[]).append(op)
    B=w['B'];forward=[]    # chronological program of the (recorded) non-target word
    for e in Aord:forward.append(e)
    for p in range(len(B)+1):
        for op in byposition.get(p,[]):
            _,lender,cols,U,E=warps[op-1]
            require(cur[lender]==basis(U),'warp frame mismatch '+str((op,lender,cur[lender],basis(U))))
            cur[lender]=basis(E);forward.append(['warp',lender,op])
        if p<len(B):
            e=B[p];forward.append(e)
            if e[0]=='warp':
                _,r_,op_,fr_,to_=e;rec_=warps[abs(op_)-1]
                require(rec_[1]==r_ and op_!=0 and abs(op_)<=K,'B warp operator/lender')   # same lender binding as the prelude warps
                check_G_frames(rec_[2],list(fr_) if op_>0 else list(to_),list(to_) if op_>0 else list(fr_),h)
                require(cur[r_]==basis(fr_),'B warp frame mismatch '+str((r_,op_,cur[r_],fr_)));cur[r_]=basis(to_);continue
            for q in registers(e):climb(q,e[-1])
    endB=cur.copy()
    for e in w['restore']:
        for q in registers(e):climb(q,e[-1])
        forward.append(e)
    for q in live:climb(q,end[q])
    require(all(cur[q]==end[q] for q in live),'end frames')
    recorded=[e for e in forward if e[0]=='warp' or not istarget(e[1])]
    # --- 5. derived cleanup: inverse-reverse at FULL, private zero buffers for restored inputs --------
    buf=lambda r:r+n if r in restored else r
    def conv(e):
        e=invert_item(e,full)
        if e[0]=='warp':return [e[0],buf(e[1]),e[2],FULLB]
        if e[0]=='add':return ['add',buf(e[1]),buf(e[2]),e[3],e[4],FULLB]
        return ['scale',buf(e[1]),e[2],e[3],FULLB]
    derived=[conv(e) for e in reversed(recorded)]
    if cleanup_given is not None:
        norm=lambda c:[(list(g[:-1]),basis(g[-1])) for g in c]
        require(norm(cleanup_given)==norm(derived),'explicit cleanup differs from derived inverse-reverse at FULL')
    cleanup=derived if cleanup_given is None else cleanup_given
    import os
    if os.environ.get('DUMPCLEAN'): open(os.environ['DUMPCLEAN'],'w').write(json.dumps(derived))
    require(all(basis(g[-1])==full for g in cleanup),'cleanup not at FULL')
    for g in cleanup:
        for r in (registers(g) if g[0]!='warp' else (g[1],)):
            require(r not in restored,'cleanup touches a restored cold input directly')
            require(r<n or r-n in restored,'buffer for a non-restored register')
    require(all(end[q]==full for q in live if q not in restored and not istarget(q)),'cleanup reads a low end')
    print('frames/profile PASS',flush=True)
    require(dict(paid)=={int(k):a for k,a in w['report']['local_profile'].items()},'paid profile mismatch '+str(dict(sorted(paid.items()))))
    inventory=Counter(len(end[q])-len(start[q]) for q in range(2*v,n) if q in liveset)
    require(dict(inventory)=={int(k):a for k,a in w['report']['width_inventory'].items()},'width inventory mismatch '+str(dict(sorted(inventory.items()))))
    # --- 6. exact free-operator-algebra replay (both orientations) -----------------------------------
    DS=10**6
    status={}
    corr_items=[['corr',t['target'],t['source'],tuple(t['operator_word']),F(t['coefficient'])] for t in corr]
    program=corr_items+w['precondition']+w['compensation']+w['A']+w['cut']+[e for e in forward[len(Aord):]]
    for dual in (False,True):
        rows={r:{(r,()):F(1)} for r in live}
        for c in restored:rows[c+n]={}
        for e in program:walg_apply(e,rows,dual,DS)
        if not dual:
            for t in range(v):
                require(rows[v+t]=={(v+t,()):F(1),(t,()):F(1)},'target map failed '+str(t)+' '+str({k:str(x) for k,x in rows[v+t].items()}))
            for c in restored:
                require(rows[c]=={(c,()):F(1)},'restored cold row is not its own input '+str(c))
                require(all(not any(var==c for var,word in rows[r]) for r in live if r!=c),'restored cold input still read by '+str(c))
            require(all(rows[c+n]=={} for c in restored),'buffer polluted before cleanup')
        for e in cleanup:walg_apply(e,rows,dual,DS)
        exp={}
        for r in live:exp[r]={(r,()):F(1)}
        for t in range(v):
            if dual:exp[t]={(t,()):F(1),(v+t,()):F(-1)}
            else:exp[v+t]={(v+t,()):F(1),(t,()):F(1)}
        bad=[r for r in live if rows[r]!=exp[r]]
        require(not bad,'all-column endpoint failure '+str((dual,bad[:8])))
        require(all(rows[c+n]=={} for c in restored),'zero buffer not returned to zero '+('dual' if dual else 'forward'))
        status['dual' if dual else 'forward']='PASS'
        print('free-algebra','dual' if dual else 'forward','PASS',len(live),'independent inputs',flush=True)
    # --- 7. optional pinned-base comparison ---------------------------------------------------------------------
    base_report=None
    if base is not None:base_report=check_base(w,base,removed)
    report=dict(status='PASS_INDEPENDENT_EXACT_BORROWING_WORD',input_file=path.name,content_sha256=hashlib.sha256(data).hexdigest(),
                compressed_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),v=v,h=h,R=R,
                removed_helpers=len(removed),independent_inputs=len(live),warps=K,corrections=len(corr),
                restored_cold=len(restored),zero_buffers=len(restored),entering=len(entering),
                local_profile=dict(sorted(paid.items())),local_mass=sum(r*c for r,c in paid.items()),
                width_inventory=dict(sorted(inventory.items())),
                orientations=status,base=base_report,checked_columns=len(live),
                elapsed_seconds=time.monotonic()-begin,
                scope='Exact free-operator-algebra replay (every remaining input is an independent column): K_G warps with G invertible, G(from)=to, symplectic form fixing L_0/L_FULL and sending L_from to L_to (rank 0), literal frame chain with warps, relaxed fixed initial compensation, derived inverse-reverse cleanup at FULL with inverse warps and private zero buffers. No Clifford phase/Gaussian product, no owner admission, no repricing.')
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
    return report

def check_base(w,basepath,removed):
    """Pin every unchanged section/anchor of the borrowed word to the (separately audited) canonical base word."""
    b=json.loads(gzip.decompress(Path(basepath).read_bytes()));v=w['report']['v'];n=2*v+w['report']['R']
    fr=lambda i:basis(b['frames'][i])
    touch=lambda e:any(r in removed for r in registers(e))
    nrm=lambda e:(e[0],tuple(registers(e)),fraction_row(e))
    lit=lambda e:(nrm(e),None if e[-1] is None else basis(e[-1]))
    litb=lambda e:(nrm(e),None if e[-1] is None else fr(e[-1]))
    require(w['ports']==b['ports'] and w['centers']==b['centers'],'ports/centers differ from base')
    require([basis(f) for f in w['center_frames']]==[fr(i) for i in b['center_frames']],'center frames differ from base')
    for k in ('precondition','compensation','A','cut'):
        exp=[litb(e) for e in b[k] if not touch(e) and not (k=='compensation' and e[0]=='add' and e[2] in removed)]
        wk=w[k][w.get('prelude_events',0):] if k=='A' else w[k]
        require([lit(e) for e in wk]==exp,'section differs from base minus removed-helper gates: '+k)
    require({int(q):basis(U) for q,U in w['start_extra'].items()}=={r:fr(b['start'][r]) for r in range(2*v,n) if r not in removed and b['frames'][b['start'][r]]},'start frames differ from base')
    for q,U in w['helper_final'].items():require(basis(U)==fr(b['final'][int(q)]),'cold end frame differs from base '+q)
    full=basis([1<<i for i in range(w['report']['h'])])
    require(all(fr(b['final'][r])==full for r in range(v)),'base source ends')
    require(all(fr(b['final'][v+t])==basis([x for x in range(1,1<<w['report']['h']) if (x&w['ports'][t]).bit_count()%2==0]) for t in range(v)),'base target ends vs ports')
    return dict(base_sha256=hashlib.sha256(Path(basepath).read_bytes()).hexdigest(),sections_match_minus_removed=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word',type=Path,required=True,help='FULL-WORD.json.gz to check')
    parser.add_argument('--output',type=Path,required=True,help='JSON receipt output path')
    parser.add_argument('--main',type=Path,help='Optional pinned main checkout: also verify the transported centre/port interface')
    parser.add_argument('--base',type=Path,help='BORROW-WORD only: canonical base word whose unchanged sections/anchors are pinned')
    args=parser.parse_args()
    run(args.word,args.output,args.main,args.base)
