"""tamper controls for the six pre-life hostings (L<-h) on a stacked word: each mutant gets its cleanup RE-DERIVED
(word_patch.derive_cleanup, same restored set) so only the semantic content differs; audit_local must reject it.
usage: prelife_controls.py WORD.json.gz ORIG2526WORD.json.gz OUT.json   (run by new/rebuild_borrow.py on the shipped word and the PR2526 word)
Scope note: a warp operator G' with G'(U)=E that differs from G off U is NOT treated as a mutant: the audits bind only G(from)=to (the free
warp algebra is free in the operator), and such a G' also passes the native chain; only G(from)=to is a checked property of the warp record."""
import sys,json,gzip,copy,tempfile,io,contextlib
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_local as al, word_patch
from alias_build import make_G
ld=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()))
w0=ld(sys.argv[1]);orig=ld(sys.argv[2]);tmp=Path(tempfile.mkdtemp())
PL=[(482,273),(483,275),(494,289),(495,291),(507,305),(519,321)]
rs0=word_patch.restored_of(w0)
def rederive(w,rs):
    t=copy.deepcopy(w);t['A']=w['A'][w.get('prelude_events',0):];w['cleanup']=word_patch.derive_cleanup(t,rs);return w
def audit(w):
    p=tmp/'m.json.gz';p.write_bytes(gzip.compress(json.dumps(w).encode(),mtime=0))
    with contextlib.redirect_stdout(io.StringIO()):return al.run(p,tmp/'m.out.json',None,None)
res=[];good=True
r=audit(w0);print('unmutated',r['status']);res.append(dict(control='unmutated',status=r['status']))
def ctl(name,w,rs=rs0,why=()):
    global good
    try:w=rederive(w,rs)
    except Exception as e:res.append(dict(control=name,rejected=True,stage='derive_cleanup',reason=str(e)[:200]));print('rejected(derive)',name,str(e)[:80]);return
    try:audit(w);res.append(dict(control=name,rejected=False));print('NOT REJECTED',name);good=False
    except RuntimeError as e:
        ok=any(x in str(e) for x in why) if why else True;good&=ok
        res.append(dict(control=name,rejected=True,reason=str(e)[:200],expected_reason_match=ok));print('rejected' if ok else 'WRONG-REASON',name,'|',str(e)[:100])
v=112;n=2*v+w0['report']['R']
opof={rec[1]:i+1 for i,rec in enumerate(w0['warps'])}
TM=('target map failed',)
for k,(L,h) in enumerate(PL):
    op=opof[h];ci=[i for i,c in enumerate(w0['initial_corrections']) if c['source']==h];assert ci,(L,h)
    i0=ci[0];h2=PL[(k+1)%6][1]
    w=copy.deepcopy(w0);c=w['initial_corrections'][i0];c['coefficient']=str(-F(c['coefficient']));ctl(f'{L}<-{h}: correction sign flipped',w,why=TM)
    w=copy.deepcopy(w0);c=w['initial_corrections'][i0];c['coefficient']=str(2*F(c['coefficient']));ctl(f'{L}<-{h}: correction coefficient doubled',w,why=TM)
    w=copy.deepcopy(w0);del w['initial_corrections'][i0];ctl(f'{L}<-{h}: one correction dropped',w,why=TM)
    w=copy.deepcopy(w0);w['initial_corrections']=[c for c in w['initial_corrections'] if c['source']!=h];ctl(f'{L}<-{h}: all {len(ci)} corrections dropped',w,why=TM)
    w=copy.deepcopy(w0);c=w['initial_corrections'][i0];c['source']=h2;c['operator_word']=[opof[h2]];ctl(f'{L}<-{h}: correction read through neighbouring host {h2} (consistent lender/op)',w,why=TM)
    w=copy.deepcopy(w0);c=w['initial_corrections'][i0];c['operator_word']=[op,op];ctl(f'{L}<-{h}: correction operator word doubled [op,op]',w,why=TM)
    tg=sorted({c['target'] for c in w0['initial_corrections']}|{x for x in range(v,2*v)})
    w=copy.deepcopy(w0);c=w['initial_corrections'][i0];c['target']=next(t for t in range(v,2*v) if t!=c['target'] and all(not(d['target']==t and d['source']==h) for d in w['initial_corrections']));ctl(f'{L}<-{h}: correction moved to another target port',w,why=TM)
    # anticipatory corrections NOT pulled back through the precondition: raw compensation vector of L from #2526
    raw={}
    for e in orig['compensation']:
        if e[0]=='add' and e[2]==L:raw[e[1]]=raw.get(e[1],F(0))+F(e[3],e[4])
    cur={c['target']:F(c['coefficient']) for c in w0['initial_corrections'] if c['source']==h}
    if {t:x for t,x in raw.items() if x}!=cur:
        w=copy.deepcopy(w0);w['initial_corrections']=[c for c in w['initial_corrections'] if c['source']!=h]+[dict(target=t,source=h,operator_word=[op],coefficient=str(x)) for t,x in sorted(raw.items()) if x]
        ctl(f'{L}<-{h}: raw compensation (not pulled back through precondition)',w,why=TM)
    else:res.append(dict(control=f'{L}<-{h}: raw==pulled-back, control vacuous'));print('vacuous pullback',L,h)
    # warp G replaced by an invertible G' that does NOT send U to E (record otherwise unchanged).  NB: a G' with G'(U)=E that differs
    # off U is NOT a mutant: the audit algebra is free in the warp operator (only G(from)=to is bound), see gfree below.
    rec=w0['warps'][op-1];G=rec[2];U=al.basis(rec[3]);E=al.basis(rec[4])
    for j in range(9):
        G2=list(G);G2[j]^=1<<((j+1)%9)
        if al.ginv(G2,9) is not None and al.basis([al.gmul(G2,u) for u in U])!=E:break
    w=copy.deepcopy(w0);w['warps'][op-1][2]=G2;ctl(f'{L}<-{h}: warp G replaced by invertible G\' with G\'(U)!=E',w,why=('G(from)!=to',))
    # warp image E replaced by another frame of the same dimension (consistent G)
    Lfirst=rec[0];F1=al.basis(w0['B'][Lfirst][-1])
    alt=None
    for y in range(1,512):
        E2=al.basis(list(E[1:])+[y])
        if len(E2)==len(E) and E2!=E:alt=E2;break
    w=copy.deepcopy(w0);w['warps'][op-1][2]=make_G(U,alt);w['warps'][op-1][4]=list(alt);ctl(f'{L}<-{h}: warp image E replaced by another dim-{len(E)} frame',w,why=('frame not monotone','target map failed','warp frame mismatch','G(from)!=to'))
    # warp dropped (op ids renumbered; corrections of h dropped too -- no operator to read through)
    w=copy.deepcopy(w0);del w['warps'][op-1];w['initial_corrections']=[dict(c,operator_word=[o-1 if o>op else o for o in c['operator_word']]) for c in w['initial_corrections'] if c['source']!=h]
    ctl(f'{L}<-{h}: pre-life warp and its corrections dropped',w,why=('frame not monotone','target map failed','warp frame mismatch'))
    # warp moved one gate later (after h's first hosted gate)
    w=copy.deepcopy(w0);w['warps'][op-1][0]=rec[0]+1;ctl(f'{L}<-{h}: warp moved after host first gate',w,why=('frame not monotone','warp frame mismatch','target map failed'))
    # host claimed cold again (status lie): helper_final restored to its #2526 cold frame, restored set incl. h
    w=copy.deepcopy(w0);w['helper_final'][str(h)]=orig['helper_final'][str(h)];ctl(f'{L}<-{h}: host re-declared cold (helper_final restored)',w,rs=rs0|{h},why=('frame not monotone','restored cold','endpoint','target map','width inventory mismatch','paid profile mismatch'))
Path(sys.argv[3]).write_text(json.dumps(dict(all_rejected_for_expected_reason=good,controls=res),indent=1))
print('ALL PRELIFE CONTROLS OK' if good else 'CONTROL FAILURE',len(res)-1)
