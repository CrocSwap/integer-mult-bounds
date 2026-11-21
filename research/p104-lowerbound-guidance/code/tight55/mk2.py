import pickle,sys
mp=pickle.load(open('s55.cnf.map','rb')); U=mp['used']
lines=open('s55.cnf').read().split('\n'); hdr=lines[0].split(); nv,nc=int(hdr[2]),int(hdr[3])
def cube(name,units):
    open(name,'w').write(f'p cnf {nv} {nc+len(units)}\n'+'\n'.join(lines[1:]).rstrip('\n')+'\n'+''.join(' '.join(map(str,u))+' 0\n' for u in units))
# G{top}_{cap}: d0 == top (U[0,top-1] true, U[0,top] false); others<=cap, and (if lo) some other >= lo
def mk(name,top,cap,lo=None):
    u=[[U[0,top-1]]]+([[-U[0,top]]] if top<9 else [])+[[-U[z,cap]] for z in range(1,16)]
    if lo: u.append([U[z,lo-1] for z in range(1,16)])
    cube(name,u)
for a in sys.argv[1:]:
    top,cap,lo=(a.split(',')+[None])[:3]; top=int(top);cap=int(cap);lo=int(lo) if lo else None
    mk(f'c55_G{top}_{cap}_{lo or 0}.cnf',top,cap,lo); print(f'c55_G{top}_{cap}_{lo or 0}.cnf')
