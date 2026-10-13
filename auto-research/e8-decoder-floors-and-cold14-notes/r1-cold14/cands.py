import sys
from common import *
V={0:0,1:-3.987,2:-6.531,3:-8.532,4:-10.181,5:-11.569,6:-12.748,7:-13.755,8:-14.614,9:-15.344}
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2]); avals=[int(x) for x in sys.argv[3].split(',')]
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
hf={int(k):span(f) for k,f in w['helper_final'].items()}
P,Pinv,comp=main_maps(w)
H0=[h for h in range(2*v,n) if start[h]==() and h not in hf]
def dy(q): return q.denominator&(q.denominator-1)==0
for a in avals:
    U=span([x for x in range(1,512) if bin(x&a).count('1')%2==0])
    QU={g for g in range(n) if inside(endB[g],U)}
    keepR={g for h in H0 for g,x in Pinv[h].items() if x and g not in QU}
    rb=nullspace_rows([Pinv[h] for h in H0],keepR)
    # column null: m over H0 with sum_j P[g][H0[j]] m_j = 0 for g not in QU  -> left null of columns
    rowsC=[g for g in range(n) if g not in QU]
    cols=[{g:P[g][h] for g in rowsC if P[g].get(h)} for h in H0]
    cb=nullspace_rows(cols,set(rowsC))
    print('U a=%d'%a,U,'rownull',len(rb),'colnull',len(cb))
    for k,r in sorted(rb.items()):
        hk=H0[k]
        if not inside(endB[hk],U): continue
        row={}
        for j,c in r.items():
            for g,x in Pinv[H0[j]].items():
                y=row.get(g,0)+c*x
                if y:row[g]=y
                else:row.pop(g,None)
        # column: try m=e_k
        colk={g:P[g][hk] for g in range(n) if P[g].get(hk)}
        okcol=all(g in QU for g in colk if g!=hk)
        partners=(set(row)|(set(colk) if okcol else set()))-{hk}
        tg=[g for g in partners if v<=g<2*v]
        cost=sum(V[8-len(endB[g])]+V[1]-V[9-len(endB[g])] if len(endB[g])<8 else 0 for g in partners)
        gain=V[8-len(endB[hk])]-V[9-len(endB[hk])]
        print(' k',hk,'endB',len(endB[hk]),'premix',{H0[j]:str(c) for j,c in r.items() if j!=k},'selfcoef',row.get(hk),'colOK',okcol,'partners',sorted((g,len(endB[g])) for g in partners),'targets',tg,'dyadic',all(dy(x) for x in row.values()),'net %.2f'%(gain+cost))
