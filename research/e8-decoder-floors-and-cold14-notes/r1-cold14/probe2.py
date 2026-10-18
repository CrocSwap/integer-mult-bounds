import sys
from common import *
V={0:0,1:-3.987,2:-6.531,3:-8.532,4:-10.181,5:-11.569,6:-12.748,7:-13.755,8:-14.614,9:-15.344}
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
P,Pinv,comp=main_maps(w)
U30=span([256,128,64,32,18,10,6,1]);U24=span([256,128,64,32,24,4,2,1])
for U,combos in ((U30,[(542,518,Q(1,2)),(543,519,Q(-1)),(554,530,Q(-1)),(555,531,Q(-1))]),(U24,[(566,494,Q(-1)),(567,495,Q(-1)),(578,506,Q(-1)),(579,507,Q(-1))])):
  QU={g for g in range(n) if inside(endB[g],U)}
  for k,j,c in combos:
    row=dict(Pinv[k])
    for g,x in Pinv[j].items():
        y=row.get(g,0)+c*x
        if y:row[g]=y
        else:row.pop(g)
    col={g:P[g][k] for g in range(n) if P[g].get(k)}
    colj={g:P[g][j] for g in range(n) if P[g].get(j)}
    bad=[g for g in row if g not in QU]; badc=[g for g in col if g!=k and g not in QU]
    partners=(set(row)|set(col))-{k}
    cost=sum(V[8-len(endB[g])]+V[1]-V[9-len(endB[g])] if len(endB[g])<8 else 0 for g in partners)
    gain=V[8-len(endB[k])]-V[9-len(endB[k])]
    print(k,j,'row',{g:(str(x),len(endB[g])) for g,x in row.items()},'bad',bad,'col',{g:str(x) for g,x in col.items()},'badc',badc,'net %.2f'%(gain+cost))
hf={int(k):span(f) for k,f in w['helper_final'].items()}
first={}
for part in ('A','B'):
    for e in w[part]:
        for r in regs(e): first.setdefault(r,span(e[-1]))
print('--- column fixes')
for E,U,ks in (((30,),U30,[542,543,554,555]),((24,),U24,[566,567,578,579])):
    QU={g for g in range(n) if inside(endB[g],U)}
    H=[h for h in range(2*v,n) if h not in hf and (start[h]==E or (start[h]==() and first.get(h)==E))]
    rowsC=[g for g in range(n) if g not in QU]
    cols=[{g:P[g][h] for g in rowsC if P[g].get(h)} for h in H]
    cb=nullspace_rows(cols,set(rowsC))
    print(E,'H',len(H),'colnull',len(cb))
    for pv,m in cb.items():
        if any(H[j] in ks for j in m):
            col={}
            for j,c in m.items():
                for g in range(n):
                    x=P[g].get(H[j])
                    if x:
                        y=col.get(g,0)+c*x
                        if y:col[g]=y
                        else:col.pop(g)
            print('  m',{H[j]:str(c) for j,c in m.items()},'col support',{g:(str(x),len(endB[g])) for g,x in col.items()})
