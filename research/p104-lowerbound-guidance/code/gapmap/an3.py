import pickle,sys
from collections import Counter
d=pickle.load(open('code/gapmap/lifes.pkl','rb'))
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
F=W['frames']; ports=W['ports']; dim=[len(b) for b in F]
dot=lambda a,b: bin(a&b).count('1')&1
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
pidx={q:i for i,q in enumerate(ports)}
def desc(f):
    S=span(F[f]); inn=[i for i,q in enumerate(ports) if q in S]
    perp=[i for i,q in enumerate(ports) if all(dot(b,q)==0 for b in F[f])]
    return (dim[f], 'ports-in',inn[:6],len(inn),'perp-of',perp[:6],len(perp))
for lid,L in d['lifes'].items():
    mv=[e for e in L['evs'] if e[0]=='move']
    if not mv: continue
    typ='D' if dim[mv[0][2]]<dim[mv[0][1]] else 'R'
    print(typ,L['reg'],'start',desc(mv[0][1]),'| end',desc(mv[-1][2]))
