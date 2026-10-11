"""Greedy packing of collective-kernel families (disjoint pivots, donors shareable along nested chronological chains),
phi-ledger kappa projection with #276's moment.py, selection JSON in kernel-selection.json schema + receipt in kernel500.json schema."""
import pickle, json, math, itertools, collections, sys, time, os, struct, importlib.util, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Q
from linalg import *
ap=argparse.ArgumentParser(); ap.add_argument('--helpers'); ap.add_argument('--families',nargs='+'); ap.add_argument('--dump'); ap.add_argument('--pkg'); ap.add_argument('--out')
ap.add_argument('--exclude',default='',help='JSON with key all: helper streams that must not appear in any accepted family'); ap.add_argument('--ledger283',default='',help='PR283 expected/PRICE.json: also price on its 120-replica ledger (cohort_candidate + 120*one-stage delta, W=510316-sum e)'); ap.add_argument('--preload',type=int,default=0,help='preload the first K census2 twin pairs (gen4_kernel.py order)'); ap.add_argument('--kinds',default='pair,tri,quad,quint'); ap.add_argument('--sweep',default='') ; ap.add_argument('--maxfam',type=int,default=10**9)
args=ap.parse_args()
d=pickle.load(open(args.helpers,'rb')); ff=d['firstframe']; ftab=d['ftab']; v=d['v']; lastread=d['lastread']; touch=d['touch']
phi=lambda r: 0.0 if r<=0 else r*math.log(100/r)
rec=open(args.dump+'/records.bin','rb').read()
def cut_read(i):
    op,a,b,c,f,z=struct.unpack_from('<6i',rec,24*i); assert op==1; return [a,b,c]
fams=[]
for p in args.families:
    fams+= [f for f in json.load(open(p))['families'] if f['kind'] in args.kinds.split(',')]
fams=fams[:args.maxfam]
if args.exclude:
    EX=set(json.load(open(args.exclude))['all']); before=len(fams); fams=[f for f in fams if not (set(f['members'])&EX)]; print('excluded families touching PR283 helpers:', before-len(fams), 'remaining', len(fams), flush=True)
print('candidate families', collections.Counter(f['kind'] for f in fams), flush=True)
# ---- model
def load(name):
    s=importlib.util.spec_from_file_location('m_'+name, args.pkg+'/'+name+'.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
cost=load('moment'); raw=json.load(open(args.dump+'/raw.json'))
H5=collections.Counter({int(k):n for k,n in raw['five_stage_profile']['histogram'].items()})
for a,n in {int(k):c for k,c in raw.get('completion_rank_histogram',raw['auxiliary_entrance_rank_histogram']).items()}.items(): H5[5*a]-=n
H5={k:n for k,n in H5.items() if n}
def kappa(H5p):
    # p = 10 deficit-fixed ledger (m = 100, deficit 4v-5h(h-2) = 2040 per replica, normalized = 12 x one-invocation five-stage)
    norm={k:12*n for k,n in H5p.items() if n}; mass=sum(k*n for k,n in norm.items()); m=100
    Wq=Q(mass+12*2040,m); W=int(Wq) if Wq.denominator==1 else int(Wq)+1
    root=cost.certify(norm,m,W,True); c=Q(int(Q(root['lower'])*10**18),10**18)
    chain=[Q(384599,10**10)]
    for _ in range(3): chain.append((1-c)*c+c*chain[-1])
    bit=chain[-1]; eta=Q(1,10**12); q=bit*(1-2*eta); mn=(1-eta)*q/(1+q); t=mn*10**18; return Q((t.numerator-1)//t.denominator,10**18), 5*W, c
# ---- packing state
pivots={}            # pivot -> entry
donors=collections.defaultdict(list)   # donor -> [(cut,e,basis,entry_idx)]
entries=[]
def chain_cost(dn, chain):
    r=ftab[ff[dn]]['dim']; ch=sorted(chain,key=lambda x:(x[0],x[1]))
    c=phi(ch[0][1]); 
    for a,b in zip(ch,ch[1:]): c+=phi(b[1]-a[1])
    return c+phi(r-ch[-1][1])-phi(r)
def chain_ok(chain):
    ch=sorted(chain,key=lambda x:(x[0],x[1]))
    for a,b in zip(ch,ch[1:]):
        if not contains(b[2],a[2]): return False
    return True
def marginal(p,ds,cut,e,basis):
    if p in pivots or p in donors: return None
    g=phi(ftab[ff[p]]['dim']-e)-phi(ftab[ff[p]]['dim'])
    for dn in ds:
        if dn in pivots: return None
        old=donors[dn]; new=old+[(cut,e,basis,None)]
        if not chain_ok(new): return None
        g+=chain_cost(dn,new)-(chain_cost(dn,old) if old else 0.0)
    return g
def accept(p,ds,cut,e,basis,kind,gain,members_dims):
    idx=len(entries)
    entries.append(dict(kind=kind,pivot=p,donors=list(ds),cut=cut,cut_read=cut_read(cut),rank=e,basis=basis,first_frame_dims=dict((str(s),ftab[ff[s]]['dim']) for s in [p]+list(ds)),phi_gain=round(gain,6),gram_det=det(gram(basis))))
    pivots[p]=idx
    for dn in ds: donors[dn].append((cut,e,basis,idx))
# preload census2 twin pairs in gen4_kernel.py order
if args.preload:
    cen=json.load(open(args.dump+'/census2.json'))['pairs']
    g2=lambda p: phi(p['dima']-1)-phi(p['dima'])+phi(1)+phi(p['dimb']-1)-phi(p['dimb'])
    cen.sort(key=g2)
    for p in cen[:args.preload]:
        if p['line'][0]=='e_i-e_j':
            u=[0]*24; u[p['line'][1]]=1; u[p['line'][2]]=-1
        else:
            q=[Q(x) for x in p['line'][1]]; u=integerize(q)
        mg=marginal(p['a'],[p['b']],p['cut'],1,[u]); assert mg is not None
        accept(p['a'],[p['b']],p['cut'],1,[u],'pair500',mg,None)
    print('preloaded', len(entries), 'pairs; phi', sum(e['phi_gain'] for e in entries), flush=True)
base=len(entries)
# greedy: families by best standalone gain; optional randomized restarts keep the order with the best total phi
import random
def greedy_total(order_f):
    global pivots,donors,entries
    sp,sd,se=pivots,donors,entries
    pivots={};donors=collections.defaultdict(list);entries=[]
    tot=0.0
    for f in order_f:
        best=None
        for o in f['options']:
            for pv in f['members']:
                ds=[s for s in f['members'] if s!=pv]
                mg=marginal(pv,ds,f['cut'],o['e'],o['basis'])
                if mg is not None and (best is None or mg<best[0]): best=(mg,pv,ds,o)
        if best is None or best[0]>=-1e-9: continue
        mg,pv,ds,o=best; accept(pv,ds,f['cut'],o['e'],o['basis'],f['kind'],mg,None); tot+=mg
    out=(tot,len(entries)); pivots,donors,entries=sp,sd,se; return out
fams.sort(key=lambda f:f['options'][0]['gain'])
RESTARTS=int(os.environ.get('PACK_RESTARTS','0')); best_order=list(fams)
if RESTARTS:
    base0=greedy_total(list(fams)); print('greedy order phi',base0,flush=True); bestphi=base0[0]
    rng=random.Random(int(os.environ.get('PACK_SEED','1')))
    for it in range(RESTARTS):
        noise=float(os.environ.get('PACK_NOISE','0.3'))
        cand=sorted(fams,key=lambda f:f['options'][0]['gain']*(1+noise*rng.random())-noise*rng.random())
        tot,cnt=greedy_total(cand)
        if tot<bestphi-1e-9: bestphi=tot; best_order=cand; print('restart',it,'better phi',tot,'count',cnt,flush=True)
    print('best phi after restarts',bestphi,flush=True)
    # iterated greedy: keep the accepted families of the best order first (minus a random ruin set pushed to the end)
    IG=int(os.environ.get('PACK_IG','0'))
    def accepted_of(order_f):
        global pivots,donors,entries
        sp,sd,se=pivots,donors,entries;pivots={};donors=collections.defaultdict(list);entries=[]
        acc=[]
        for f in order_f:
            best=None
            for o in f['options']:
                for pv in f['members']:
                    ds=[s for s in f['members'] if s!=pv]
                    mg=marginal(pv,ds,f['cut'],o['e'],o['basis'])
                    if mg is not None and (best is None or mg<best[0]): best=(mg,pv,ds,o)
            if best is None or best[0]>=-1e-9: continue
            mg,pv,ds,o=best; accept(pv,ds,f['cut'],o['e'],o['basis'],f['kind'],mg,None); acc.append(f)
        pivots,donors,entries=sp,sd,se; return acc
    cur_order=best_order; cur_acc=accepted_of(cur_order); cur_phi=bestphi
    ids={id(f):i for i,f in enumerate(fams)}
    for it in range(IG):
        ruin=set(rng.sample(range(len(cur_acc)),max(1,int(float(os.environ.get('PACK_RUIN','0.12'))*len(cur_acc)))))
        keep=[f for i,f in enumerate(cur_acc) if i not in ruin];out=[f for i,f in enumerate(cur_acc) if i in ruin]
        keepset=set(map(id,cur_acc));rest=sorted((f for f in fams if id(f) not in keepset),key=lambda f:f['options'][0]['gain']*(1+0.2*rng.random()))
        cand=keep+rest+out
        tot,cnt=greedy_total(cand)
        if tot<cur_phi-1e-9:
            cur_phi=tot;cur_order=cand;cur_acc=accepted_of(cand);print('ig',it,'better phi',tot,'count',cnt,flush=True)
    if cur_phi<bestphi: bestphi=cur_phi;best_order=cur_order
    print('best phi after iterated greedy',bestphi,flush=True)
fams=best_order
acc=collections.Counter(); rej=collections.Counter(); order=[]
for f in fams:
    best=None
    for o in f['options']:
        p=o['pivot']; ds=[s for s in f['members'] if s!=p]
        # also try other pivots for this e (shared-donor state can change the best pivot)
        for pv in f['members']:
            ds=[s for s in f['members'] if s!=pv]
            mg=marginal(pv,ds,f['cut'],o['e'],o['basis'])
            if mg is not None and (best is None or mg<best[0]): best=(mg,pv,ds,o)
    if best is None: rej[f['kind']]+=1; continue
    mg,pv,ds,o=best
    if mg>=-1e-9: rej[(f['kind'],'nonnegative marginal')]+=1; continue
    accept(pv,ds,f['cut'],o['e'],o['basis'],f['kind'],mg,None); acc[(f['kind'],o['e'])]+=1
print('accepted', sorted(acc.items()), 'rejected', dict(rej), flush=True)
print('total phi gain (new families)', sum(e['phi_gain'] for e in entries[base:]), 'count', len(entries)-base, flush=True)
# ---- histogram delta + kappa for prefixes of the acceptance order
def histogram(upto):
    H=collections.Counter(H5); ch=collections.defaultdict(list)
    for e in entries[:upto]:
        r=ftab[ff[e['pivot']]]['dim']; H[r]-=5
        if r-e['rank']>0: H[r-e['rank']]+=5
        for dn in e['donors']: ch[dn].append((e['cut'],e['rank']))
    for dn,c in ch.items():
        r=ftab[ff[dn]]['dim']; c.sort(); H[r]-=5; H[c[0][1]]+=5
        for a,b in zip(c,c[1:]):
            if b[1]-a[1]>0: H[b[1]-a[1]]+=5
        if r-c[-1][1]>0: H[r-c[-1][1]]+=5
    assert min(H.values())>=0
    return {k:n for k,n in H.items() if n}
k0,W0,c0=kappa(H5); print('baseline kappa %.15e W_lit %d' % (float(k0),W0), flush=True)
if args.ledger283:
    PR=json.load(open(args.ledger283)); CH=collections.Counter({int(k):n for k,n in PR['cohort_candidate']['histogram'].items()}); W283=510316
    massC=sum(r*n for r,n in CH.items()); assert 120*W283-massC==PR['cohort_candidate']['deficit']==105600, (120*W283-massC)
    ratio=Q(PR['cohort_candidate']['kappa_decimal'])/Q(PR['cohort_candidate']['coarse_decimal'])
    def kappa283(upto):
        Hh=histogram(upto); d=collections.Counter({r:(n-H5.get(r,0))//5 for r,n in Hh.items()}); d.update({r:-H5[r]//5 for r in H5 if r not in Hh})
        H=collections.Counter(CH)
        for r,n in d.items(): H[r]+=120*n
        H={r:n for r,n in H.items() if n}; assert min(H.values())>0
        W=W283-sum(e['rank'] for e in entries[:upto]); assert 120*W-sum(r*n for r,n in H.items())==105600
        root=cost.certify(H,120,W,True); c=Q(int(Q(root['lower'])*10**18),10**18)
        chain=[Q(384599,10**10)]
        for _ in range(3): chain.append((1-c)*c+c*chain[-1])
        bit=chain[-1]; eta=Q(1,10**12); q=bit*(1-2*eta); mn=(1-eta)*q/(1+q); t=mn*10**18; k=Q((t.numerator-1)//t.denominator,10**18)
        return float(c), float(k), W
    c283,k283,_=kappa283(0); print('PR283 cohort ledger reproduced: coarse %.15e (PRICE.json %s) -> PR276-chain kappa %.15e (PRICE.json %s)' % (c283, PR['cohort_candidate']['coarse_decimal'], k283, PR['cohort_candidate']['kappa_decimal']), flush=True)
results=[]
sweep=[int(x) for x in args.sweep.split(',') if x] if args.sweep else []
def even_prefix(upto):
    # the ledger model is exact only when the total entrance rank is even (W_lit = mass/2+2200 integer and divisible by 5 keeps the 52800 deficit); trim to the longest even prefix
    while upto>0 and sum(e['rank'] for e in entries[:upto])%5: upto-=1
    return upto
pts=sorted(set(even_prefix(u) for u in [base,len(entries)]+[base+s for s in sweep if base+s<=len(entries)]))
for upto in pts:
    Hh=histogram(upto); k,W,c=kappa(Hh); results.append((upto,float(k),W)); print('prefix %d (new %d): kappa %.15e W_lit %d' % (upto,upto-base,float(k),W), flush=True)
    if args.ledger283: c3,k3,W3=kappa283(upto); print('   on PR283 ledger: coarse %.15e kappa_est %.15e W %d phi_sum %.3f' % (c3,k3,W3,sum(e['phi_gain'] for e in entries[:upto])), flush=True); results[-1]=(upto,float(k),W,c3,k3,W3)
best=max(results,key=lambda x:(x[4] if args.ledger283 else x[1])); upto=best[0]
Hh=histogram(upto); k,W,c=kappa(Hh)
delta=collections.Counter({r:n//5 for r,n in Hh.items()}); delta.subtract({r:n//5 for r,n in H5.items()}); delta={str(r):n for r,n in sorted(delta.items()) if n}
sel=entries[:upto]
pairs=[dict(a=e['pivot'],b=e['donors'][0],cut=e['cut'],cut_read=e['cut_read'],rank=e['rank'],basis=e['basis'],first_frame_dims=list(e['first_frame_dims'].values()),phi_gain=e['phi_gain']) for e in sel if len(e['donors'])==1]
families=[dict(pivot=e['pivot'],donors=e['donors'],cut=e['cut'],cut_read=e['cut_read'],rank=e['rank'],basis=e['basis'],first_frame_dims=e['first_frame_dims'],phi_gain=e['phi_gain'],kind=e['kind'],gram_det=e['gram_det']) for e in sel if len(e['donors'])>1]
shared=collections.Counter(len([1 for e in sel if dn in e['donors']]) for dn in {dn for e in sel for dn in e['donors']})
selection=dict(status='GEN4_COLLECTIVE_KERNEL_FAMILIES_PER_FAMILY_CUTS',provenance='gen4coll/families.py + pack.py on the gen4 dump (scratch research; not a package)',n=d['n'],v=v,
    input_raw_sha256='60830cb24fbdd5a26942c4aa897d0ae30738ca5772ab83d6c57be666ddc95f7a',input_scalar_sha256='c0f4da07311f1998e0813b39098da9015969c180fa55d72f281e45cdd50aaba8',
    selected_pairs=len(pairs),selected_families=len(families),expected_local_delta=delta,pairs=pairs,families=families,
    donor_sharing_histogram={str(k):n for k,n in sorted(shared.items())},entrance_rank_histogram={str(k):n for k,n in sorted(collections.Counter(e['rank'] for e in sel).items())})
json.dump(selection,open(args.out+'.selection.json','w'))
receipt=dict(pairs=len(pairs),families=len(families),family_shapes={str(k):n for k,n in sorted(collections.Counter((e['kind'],len(e['donors'])+1,e['rank']) for e in sel).items())},delta=delta,W_lit=W,kappa=str(k),kappa_float=float(k),coarse=str(c),baseline_kappa_float=float(k0),phi_gain_total=sum(e['phi_gain'] for e in sel),sweep=results)
json.dump(receipt,open(args.out+'.json','w'),indent=1)
print('BEST prefix', upto, 'coarse %.15e (complex cap 7.47454944651775e-4)' % float(c), 'kappa %.15e' % float(k), 'W_lit', W, 'pairs', len(pairs), 'families', len(families), 'shapes', receipt['family_shapes'])
