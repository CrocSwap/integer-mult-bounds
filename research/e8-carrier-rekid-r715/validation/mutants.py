"""independent mutation suite for the mixed R715 word. Detector = mix_check.check (e8core.replay + defining identity + strict span), unchanged s11x code.
Mutants: the 4 stock controls (re-implemented here, with the failure reason recorded), plus per-receiver families:
 X1 mix at a NON-COMMON frame (same-dim incomparable frame substituted for G),  X2 one dropped preconditioner (single D gate removed),
 X3 one scatter correction undone, X4 one mix addition dropped.  Also write the first X1/X2 mutants as words for the C++ pipeline."""
import sys,gzip,json,copy,traceback
sys.path.insert(0,sys.argv[1]); import mix_check as MC
ld=lambda p: json.load(gzip.open(p,'rt') if p.endswith('.gz') else open(p))
w=ld('copy/R715_mixed.json'); base=ld('copy/R715_k3.json.gz'); frames=json.load(open('chain/mixed/records/frames.json'))['frames']
v=w['v']; nD=len(base['D'])
def test(m):
    try: MC.check(m,frames); return 'ACCEPTED',''
    except BaseException as e: return 'REJECTED','%s: %s'%(type(e).__name__,str(e)[:90])
print('control (unmutated mixed word):',test(w)[0])
# --- stock four, with reasons
res={}
m=copy.deepcopy(w); m['D']=m['D'][:nD]; res['stock1 omit all frame-0 preconditioners']=test(m)
m=copy.deepcopy(w); m['scatter']=base['scatter']; res['stock2 omit scatter correction']=test(m)
mixed=[k for k,g in enumerate(w['B']) if v<=g[2][0]<2*v]
full=next(i for i,f in enumerate(w['frames']) if len(f)==len(w['lines']))
m=copy.deepcopy(w); g=m['B'][mixed[0]]; m['B'][mixed[0]]=[full,g[1],g[2]]; res['stock3 mix at the full frame']=test(m)
m=copy.deepcopy(w); m['B']=[g for g in m['B'] if not (v<=g[2][0]<2*v)]; res['stock4 omit mix additions']=test(m)
for k,(s,why) in res.items(): print('%-42s %s   [%s]'%(k,s,why))
print('number of mix additions in B:',len(mixed),'; preconditioners:',len(w['D'])-nD)
# --- per-receiver families
F=[frozenset(f) for f in w['frames']]
from collections import Counter
rejX1=rejX2=rejX3=rejX4=0; acc=[]; reasons=Counter()
pre=list(range(nD,len(w['D'])))
for j,k in enumerate(mixed):
    G,u,(wd,)=w['B'][k]
    cands=[i for i,f in enumerate(F) if len(f)==len(F[G]) and not (f<=F[G] or F[G]<=f)]
    # prefer a frame inside the receiver's FINAL frame cap so the substitution is not trivially an outside frame
    F1=cands[(7*j)%len(cands)]
    m=copy.deepcopy(w); m['B'][k]=[F1,u,[wd]]; s,why=test(m); rejX1+=(s=='REJECTED'); reasons['X1 '+why[:30]]+=1
    if s!='REJECTED': acc.append(('X1',j))
    if j==0: json.dump(m,open('work/mut_X1_noncommon.json','w'))
for j,p in enumerate(pre):
    m=copy.deepcopy(w); del m['D'][p]; s,why=test(m); rejX2+=(s=='REJECTED'); reasons['X2 '+why[:30]]+=1
    if s!='REJECTED': acc.append(('X2',j))
    if j==0: json.dump(m,open('work/mut_X2_droppre.json','w'))
    if j==len(pre)-1: json.dump(m,open('work/mut_X2_droppre_last.json','w'))
recv=[g[1] for g in w['B'] if False]
for j,k in enumerate(mixed):
    G,u,(wd,)=w['B'][k]
    m=copy.deepcopy(w); m['scatter'][u-v]=base['scatter'][u-v]; s,why=test(m); rejX3+=(s=='REJECTED'); reasons['X3 '+why[:30]]+=1
    if s!='REJECTED': acc.append(('X3',j))
    m=copy.deepcopy(w); del m['B'][k]; s,why=test(m); rejX4+=(s=='REJECTED'); reasons['X4 '+why[:30]]+=1
    if s!='REJECTED': acc.append(('X4',j))
n=len(mixed)
print('X1 mix at non-common (incomparable same-dim) frame : %d/%d rejected'%(rejX1,n))
print('X2 single dropped preconditioner                    : %d/%d rejected'%(rejX2,len(pre)))
print('X3 single scatter correction undone                 : %d/%d rejected'%(rejX3,n))
print('X4 single mix addition dropped                      : %d/%d rejected'%(rejX4,n))
print('accepted mutants:',acc); print(dict(reasons))
