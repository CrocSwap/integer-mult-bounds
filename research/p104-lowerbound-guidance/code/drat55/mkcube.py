"""mkcube.py <mask> <out.cnf> : cube for inactive set I=mask exactly as tight55/ic/i<mask>.cnf (s55 body + 16 units + 16 normalization clauses)"""
import pickle, sys
T55='code/tight55/'
mp=pickle.load(open(T55+'s55.cnf.map','rb')); U=mp['used']; NIN=mp['nin']
I=int(sys.argv[1]); out=sys.argv[2]
body=open(T55+'s55.cnf').read().split('\n',1)
hdr=body[0].split(); nv,nc=int(hdr[2]),int(hdr[3]); rest=body[1].rstrip('\n')+'\n'
units=[(U[z,8] if I>>z&1 else -U[z,8]) for z in range(16)]
norm=[[-U[z,7],U[z,8],-NIN[z]] for z in range(16)]
with open(out,'w') as f:
    f.write(f'p cnf {nv} {nc+32}\n'+rest+''.join(f'{u} 0\n' for u in units)+''.join(' '.join(map(str,c))+' 0\n' for c in norm))
