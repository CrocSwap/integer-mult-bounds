import sys; fn=sys.argv[1]; n=int(sys.argv[2]); sys.argv=['x']
import k9b
sets=k9b.parse(fn); print('distinct served sets',len(sets),'sizes',sorted({len(t) for t in sets})[:5],flush=True)
nk=0
for i,t in enumerate(sets):
    if k9b.graphic(t,n): nk+=1; print('GRAPHIC',i,len(t),flush=True)
print('DONE sets',len(sets),'graphic',nk,flush=True)
