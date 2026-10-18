from lib import *
import sys
w=load(sys.argv[1] if len(sys.argv)>1 else __import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');P=w['ports']
n=2*V+w['report']['R']
seq=[('A',i,e) for i,e in enumerate(w['A'])]+[('C',i,e) for i,e in enumerate(w['cut'])]+[('B',i,e) for i,e in enumerate(w['B'])]
rows=[{r:Q(1)} for r in range(n)]
# first write / first-drag time per reg wrt target
viol={170:('B',945,591,58),171:('B',929,283,59),174:('B',930,379,62),175:('B',946,598,63)}
firstw={}
for k,(p,i,e) in enumerate(seq):
    if p=='C': 
        G.apply_op(e,rows);firstw.setdefault(e[1],k);continue
    t=e[1]
    if (p,i)==viol.get(t,(0,0))[:2] if False else False: pass
    for y,(pp,ii,s,tg) in viol.items():
        if (p,i)==(pp,ii):
            print('y',y,'src',s,'support',len(rows[s]),'leaves:',sorted(rows[s].items())[:0])
            sup=rows[s]
            bad=[]
            for j in sup:
                fw=firstw.get(j,None)
                bad.append((j,'unwritten' if fw is None else 'written@%d'%fw))
            from collections import Counter
            print(Counter(b[1][:5] for b in bad)); print([b for b in bad if b[1]!='unwritten'][:20]);
            print('regkinds',Counter('x' if j<112 else 'y' if j<224 else 'h' for j in sup))
    G.apply_op(e,rows); firstw.setdefault(e[1],k)
