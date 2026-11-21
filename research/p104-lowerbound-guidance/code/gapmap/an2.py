import pickle,sys
from collections import Counter
from fractions import Fraction as Q
d=pickle.load(open('code/gapmap/lifes.pkl','rb'))
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
F=W['frames']; ports=W['ports']; dim=[len(b) for b in F]
dot=lambda a,b: bin(a&b).count('1')&1
lab=d['lab']; fin=d['fin']
def coldat(f,k):
    q=ports[lab[k][1]]; return all(dot(b,q)==0 for b in F[f])
def eff(c):
    out={k:v for k,v in c.items() if k in lab and lab[k][0] in('Y','Y2')}
    for k,v in c.items():
        if k in lab and lab[k][0] in ('X','X2'):
            for kk,vv in fin[k].items():
                if kk in lab and lab[kk][0] in ('Y','Y2'):
                    out[kk]=out.get(kk,0)-v*vv
    return {k:v for k,v in out.items() if v}
def kind_hotx(c,f):
    # X-type symbols: hot at chart f if q in chart? (X content 'hot' = contains q_t)
    return None
res=[]
for lid,L in d['lifes'].items():
    evs=L['evs']; mv=[e for e in evs if e[0]=='move']
    if not mv: continue
    typ='D' if dim[mv[0][2]]<dim[mv[0][1]] else 'R'
    seq=''.join('i' if e[0]=='in' else 'o' for e in evs if e[0] in('in','out'))
    firsto=seq.find('o'); gtd = firsto<0 or 'i' not in seq[firsto:]
    nhot=0; nint=0; fracs=False; dens=set()
    for e in evs:
        if e[0]=='in':
            nint+=1; c=eff(e[5])
            nhot+= sum(1 for k in c if not coldat(e[3],k))
            for v in e[5].values(): dens.add(v.denominator)
            fracs |= any(v.denominator>2 for v in e[5].values()) or False
        if e[0]=='scale': dens.add(e[1].denominator)
    shape=[dim[mv[0][1]]]+[dim[e[2]] for e in mv]
    res.append((typ,L['reg'],tuple(shape),seq,gtd,nhot==0,nhot,sorted(dens)))
for o in sorted(res): print(o)
print(Counter((o[0],o[4],o[5]) for o in res))
print('max den over intakes:', max(max(o[7]) if o[7] else 1 for o in res))
