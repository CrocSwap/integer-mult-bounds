import pickle,sys
from collections import Counter
d=pickle.load(open('code/gapmap/lifes.pkl','rb'))
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
F=W['frames']; ports=W['ports']; dim=[len(b) for b in F]
dot=lambda a,b: bin(a&b).count('1')&1
lab=d['lab']
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
SPc={}
def sp(f):
    if f not in SPc: SPc[f]=span(F[f])
    return SPc[f]
def coldat(f,k): # chart f subset of q_k^perp
    kind,p=lab[k]; q=ports[p]
    return all(dot(b,q)==0 for b in F[f])
def hotat(f,k): return ports[lab[k][1]] in sp(f)
out=[]
for lid,L in d['lifes'].items():
    evs=L['evs']; mv=[e for e in evs if e[0]=='move']
    if not mv: continue
    ds=[dim[e[2]]-dim[e[1]] for e in mv]
    typ='D' if ds[0]<0 else 'R'
    kinds=[e[0] for e in evs if e[0] in('in','out')]
    # GTD: all 'in' before all 'out'
    seq=''.join('i' if k=='in' else 'o' for k in kinds)
    gtd = ('o' not in seq) or ('i' not in seq[seq.index('o'):])
    # intake coldness
    cold=True; hotin=Counter(); intakes=0
    for e in evs:
        if e[0]=='in':
            f=e[3]; intakes+=1
            for k,v in e[5].items():
                if k in lab and lab[k][0] in('Y','Y2'):
                    if not coldat(f,k): cold=False; hotin['Y-hot']+=1
                elif k in lab and lab[k][0] in ('X','X2'):
                    hotin['X-sym']+=1
    # charts at intake/outputs
    shape=[dim[e[1]] for e in mv[:1]]+[dim[e[2]] for e in mv]
    out.append((typ,L['reg'],shape,seq,gtd,cold,dict(hotin),intakes))
for o in sorted(out): print(o)
print(Counter((o[0],o[4],o[5]) for o in out))
