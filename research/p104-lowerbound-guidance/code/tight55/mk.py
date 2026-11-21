import pickle,sys
mp=pickle.load(open('s55.cnf.map','rb')); U=mp['used']
def cube(name,units):
    lines=open('s55.cnf').read().split('\n'); hdr=lines[0].split(); nv,nc=int(hdr[2]),int(hdr[3])
    open(name,'w').write(f'p cnf {nv} {nc+len(units)}\n'+'\n'.join(lines[1:]).rstrip('\n')+'\n'+''.join(f'{u} 0\n' for u in units))
cube('c55_Fa.cnf',[U[0,8]]+[-U[z,6] for z in range(1,16)])
cube('c55_Fb.cnf',[U[0,8]]+[-U[z,7] for z in range(1,16)]+[U[z,6] for z in []])
