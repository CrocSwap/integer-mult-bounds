"""Exact witnesses for the written factor-linear overcomplete decoder floor.

The universal statements are in PROOF.md, conditional on the explicitly
inherited real-flat classification. Finite examples are not that proof.
Prepared for woklerx with substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,importlib.util,json,random,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE='c0e3631dc24e3c24a861f7d3d79e0608481cccec'
OLD='research/complex-decoder-field-extension-seed44/'
PAIR='research/complex-frame-pair-decoders/'
PATHS={OLD+x for x in ('PROOF.md','verify.py','exact.py','replay_source.py','SOURCES.json')}|{
    PAIR+'PROOF.md', PAIR+'README.md',
    'research/frame-pair-enumeration-production/baseline.py'}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs(items):
    out={}
    for k,v in items:
        need(k not in out,'duplicate JSON key');out[k]=v
    return out
def read(p):
    return json.loads(p.read_text(),object_pairs_hook=pairs,
        parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def source():
    pins=read(HERE/'SOURCES.json');need(pins['base']==BASE and set(pins['files'])==PATHS,'mandatory source inventory')
    for p,h in pins['files'].items():need(sha((ROOT/p).read_bytes().replace(b'\r\n',b'\n'))==h,'source pin '+p)
    need(sha((HERE/'BASE-SELECTED.json').read_bytes().replace(b'\r\n',b'\n'))==pins['selected_sha256'],'selected context')
    need(read(HERE/'BASE-SELECTED.json')['kappa']=='836330098538459/500000000000000000','selected kappa')
    spec=importlib.util.spec_from_file_location('credited_exact',ROOT/(OLD+'exact.py'));ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
    return ex

def root_products(ex,roots,A):
    den,ints=ex.clear(A);m=len(A[0])
    return den,[[tuple(sum(r[j]*ints[j][k][q] for j in range(8)) for q in range(2)) for k in range(m)] for r in roots]

def all_pairs(ex,roots,A,B):
    ad,d=root_products(ex,roots,A);bd,t=root_products(ex,roots,B)
    for i,r in enumerate(roots):
        for j,s in enumerate(roots):
            a=sum(x[0]*y[0]-x[1]*y[1] for x,y in zip(d[i],t[j]));b=sum(x[0]*y[1]+x[1]*y[0] for x,y in zip(d[i],t[j]))
            if b or a!=2*ad*bd*sum(x*y for x,y in zip(r,s)):return False
    return True

def costs(ex,roots,N,A,B,live):
    _,D=root_products(ex,roots,A);_,T=root_products(ex,roots,B);m=len(A[0])
    left=[sum((D[i][k]!=(0,0))<<i for i in range(len(roots)))&live for k in range(m)]
    right=[sum((T[i][k]!=(0,0))<<i for i in range(len(roots)))&live for k in range(m)]
    need(all(left) and all(right),'nonzero active terms')
    return [ex.rank2([N[i]&y for i in range(len(roots)) if x>>i&1]) for x,y in zip(left,right)]

def inverseq(a):
    n=len(a);a=[[Q(x) for x in row]+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next((k for k in range(j,n) if a[k][j]),None);need(k is not None,'singular rational matrix')
        a[j],a[k]=a[k],a[j];q=a[j][j];a[j]=[x/q for x in a[j]]
        for k in range(n):
            if k!=j:
                q=a[k][j];a[k]=[x-q*y for x,y in zip(a[k],a[j])]
    return [row[n:] for row in a]

def compute():
    ex=source();G=ex.G
    # The pinned wrapper replays A/B/C/E with predecessor assertions enabled.
    old=subprocess.run([sys.executable,'-I','-B',str(ROOT/(OLD+'replay_source.py'))],capture_output=True,text=True)
    need(old.returncode==0,'inherited fact replay: '+old.stderr)
    inherited=json.loads(old.stdout);need(len(inherited['census'])==8 and inherited['d7_orbit']==1080,'finite premise coverage')
    roots=[tuple(r) for r in inherited['root_lines']];N=inherited['pairing_rows'];full=(1<<120)-1
    need(ex.rank2(N)==9,'label rank')
    # Each source root is twice a norm-two real root; coordinate scaling has
    # no effect on supports and is accounted for in every exact identity.
    f0=inherited['frame0'];A=ex.transpose([[G(x)/2 for x in roots[k]] for k in f0]);B=ex.dual(A)
    for i in range(8):
        phase=G(1,1+i%3)
        for j in range(8):A[j][i]=A[j][i]*phase;B[j][i]=B[j][i]/phase
    need(all_pairs(ex,roots,A,B),'ordinary-transpose baseline')
    examples=[]
    for m in (9,10,12,16):
        a=[row[:] for row in A];b=[row[:] for row in B]
        for k in range(m-8):
            lam=G(1,1+(k%2))
            for i in range(8):
                original=a[i][k];a[i][k]=lam*original;a[i].append((G(1)-lam)*original);b[i].append(b[i][k])
        need(all_pairs(ex,roots,a,b),'overcomplete all-pair identity')
        profiles=[]
        for p in range(25):
            removed=inherited['chain'][str(p)]['punctured'];live=full^sum(1<<x for x in removed)
            c=costs(ex,roots,N,a,b,live);need(sum(c)>=max(72-p,56),'overcomplete example floor')
            profiles.append({'p':p,'terms':c,'total':sum(c)})
        examples.append({'terms':m,'A':ex.encoded(a),'B':ex.encoded(b),'identity_entries':14400,'profiles':profiles})
    # Finite arithmetic checks supplement the monotone all-m proof. The only
    # missing coarse case is p=8,m=9, handled by the positive-diagonal proof.
    bound_cases=[]
    for p in range(25):
        for m in range(9,33):
            lower=7*m+16-2*p if p<=7 else (64 if p==8 and m==9 else 7*m)
            need(lower>=max(72-p,56),'case split arithmetic');bound_cases.append([p,m,lower])
    # Explicit independent rational Gram calculations on sixteen root bases.
    rng=random.Random(47);bases=[list(f0)]
    while len(bases)<16:
        order=list(range(120));rng.shuffle(order);chosen=[]
        for i in order:
            if ex.rankq([roots[j] for j in chosen+[i]])>len(chosen):chosen.append(i)
            if len(chosen)==8:break
        need(len(chosen)==8,'greedy real root basis');bases.append(chosen)
    grams=[];pair_checks=0
    for ids in bases:
        gram=[[Q(sum(x*y for x,y in zip(roots[i],roots[j])),4) for j in ids] for i in ids]
        inv=inverseq(gram);diag=[2*inv[i][i] for i in range(8)]
        need(all(x>0 for x in diag),'real positive inverse diagonal')
        live=full^sum(1<<i for i in ids)
        columns=ex.transpose([[G(x)/2 for x in roots[i]] for i in ids])
        for i in range(8):
            for j in range(8):
                c=costs(ex,roots,N,[[r[i]] for r in columns],[[r[j]] for r in columns],live)[0]
                odd=(sum(x*y for x,y in zip(roots[ids[i]],roots[ids[j]]))//4)%2
                need(c==8-int(bool(odd)) and (c!=7 or i!=j),'punctured-root pair classification')
                pair_checks+=1
        grams.append({'punctured_root_basis':ids,'required_diagonal':[str(x) for x in diag]})
    # Unrestricted overcomplete factors need not lie in col(R): split a normal
    # column using an outside-code vector, with exact cancellation on all pairs.
    liveids=[i for i in range(120) if i not in f0];R=[list(roots[i]) for i in liveids]
    z=[int(i==0) for i in range(len(R))]
    need(ex.rankq(R)==8 and ex.rankq([r+[v] for r,v in zip(R,z)])==9,'outside-code witness')
    D=[[r[0]+z[i]]+r[1:]+[-z[i]] for i,r in enumerate(R)]
    T=[[2*r[0]]+[2*x for x in r[1:]]+[2*r[0]] for r in R]
    for i,r in enumerate(R):
        for j,s in enumerate(R):need(sum(a*b for a,b in zip(D[i],T[j]))==2*sum(a*b for a,b in zip(r,s)),'outside-code exact identity')
    need(ex.rankq([r+[d[0]] for r,d in zip(R,D)])==9,'first column outside root code')
    controls=[]
    bad=[row[:] for row in B];bad[0][0]=bad[0][0]+G(1)
    need(not all_pairs(ex,roots,A,bad),'coefficient mutation');controls.append('changed_coefficient_rejected')
    conjugate=[[x.conjugate() for x in row] for row in B]
    need(not all_pairs(ex,roots,A,conjugate),'Hermitian substitution');controls.append('Hermitian_transpose_rejected')
    need(7*9==63<64,'exceptional crude-bound gap');controls.append('p8_m9_needs_diagonal_argument')
    need(any(D[i][0]*T[j][0]!=0 for i in range(len(R)) for j in range(len(R))),'active split terms')
    need(any(sum(a*b for a,b in zip(D[i][:-1],T[j][:-1]))!=2*sum(a*b for a,b in zip(R[i],R[j])) for i in range(len(R)) for j in range(len(R))),'deleted cancelling term');controls.append('missing_split_term_rejected')
    controls.append('rank9_outside_code_blocks_unrestricted_extension')
    return {'base':BASE,'seed':47,'theorem':'All-pairs complex factor-linear decoders with any active term count m have copy cost >= max(72-p,56), p<=24.',
        'inherited_scope':'PR968 real-flat classification and finite geometric lemmas; PR1077 complex support descent and eight-term theorem. No new proof of classification.',
        'premises':{'census':inherited['census'],'d7_orbit':1080,'attaining_chain':inherited['chain'],'finite_log':inherited['log']},
        'overcomplete_examples':examples,'arithmetic_case_checks':len(bound_cases),'root_basis_checks':grams,'root_pair_checks':pair_checks,
        'outside_code_countercontrol':{'live_rows':112,'terms':9,'identity_entries':12544,'root_code_rank':8,'augmented_rank':9,'z_nonzero_at_live_row':0},
        'controls':controls,'scope':{'requires_both_factors_in_root_code':True,'unrestricted_overcomplete_bound':False,'new_supplier':False,'new_kappa':False}}

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=compute()
    if a.write:(HERE/'EXPECTED.json').write_text(json.dumps(r,indent=2)+'\n')
    else:need(enc(r)==enc(read(HERE/'EXPECTED.json')),'typed complete receipt mismatch')
    print('PASS_FACTOR_LINEAR_OVERCOMPLETE examples=4 punctures=25 root_pairs=1024 outside_code_rank=9 controls='+str(len(r['controls'])))
if __name__=='__main__':main()
