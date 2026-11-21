"""Adaptive SOUND cube runner (sequential, one kissat at a time).
Cube = (I, fixes): inactive set I (lexmax in its Aut-orbit, or 0) + d-lex-leader over Stab(I) + value fixes d_z = v.
UNKNOWN cubes are split on the first free active slot z (z not in I, not fixed): children d_z = 0..8 (a complete value partition).
State in <tag>.state.json (resumable); log in cubes/<tag>.alog.  usage: arun.py base.cnf masksfile tag timeout"""
import sys,os,json,pickle,subprocess,time
base,mfile,tag,T=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
os.chdir('code/loose')
mp=pickle.load(open(base+'.map','rb')); U=mp['used']
k0=next(iter(U))[0]
uz=(lambda k,i:U[('z',k),i]) if isinstance(k0,tuple) else (lambda k,i:U[k,i])
P=[tuple(p) for p in pickle.load(open('../tight55/perms.pkl','rb'))]
with open(base) as fh: hdr=fh.readline().split(); body=fh.read().rstrip('\n')+'\n'
NV,NC=int(hdr[2]),int(hdr[3])
st_file=f'{tag}.state.json'
if os.path.exists(st_file): st=json.load(open(st_file))
else: st={'queue':[[int(m),[]] for m in open(mfile).read().split()],'done':[]}
log=open(f'cubes/{tag}.alog','a')
def build(mask,fixes,out):
    ind=[mask>>j&1 for j in range(16)]; nv=NV; cls=[]
    for z in range(16): cls.append([uz(z,8)] if ind[z] else [-uz(z,8)])
    for z,a in fixes:
        if a>0: cls.append([uz(z,a-1)])
        if a<9: cls.append([-uz(z,a)])
    for p in P:
        if any(ind[p[j]]!=ind[j] for j in range(16)) or all(p[j]==j for j in range(16)): continue
        prev=None
        for j in range(16):
            if p[j]==j: continue
            nv+=1; e=nv; pre=[] if prev is None else [-prev]
            for v in range(9): cls.append(pre+[-uz(p[j],v),uz(j,v)])
            ss=[]
            for v in range(9):
                nv+=1; ss.append(nv); cls.append([-nv,uz(j,v)]); cls.append([-nv,-uz(p[j],v)])
            cls.append(pre+[e]+ss); prev=e
    with open(out,'w') as fh:
        fh.write(f'p cnf {nv} {NC+len(cls)}\n'); fh.write(body)
        for c in cls: fh.write(' '.join(map(str,c))+' 0\n')
while st['queue']:
    mask,fixes=st['queue'][0]
    tmp=f'cubes/tmp_{tag}.cnf'; build(mask,fixes,tmp)
    t0=time.time()
    r=subprocess.run(['kissat',f'--time={T}','-q',tmp],capture_output=True,text=True)
    dt=time.time()-t0
    s=[l for l in r.stdout.split('\n') if l.startswith('s ')]; s=s[0][2:] if s else 'ERR'
    log.write(f'{mask} {fixes} {s} {dt:.0f}s\n'); log.flush()
    st['queue'].pop(0)
    if s=='SATISFIABLE':
        open(f'cubes/{tag}_SAT_{mask}_{len(st["done"])}.out','w').write(r.stdout)
    if s=='UNKNOWN':
        fixed={z for z,_ in fixes}
        free=[z for z in range(16) if not (mask>>z&1) and z not in fixed]
        if free:
            z=free[0]; st['queue']=[[mask,fixes+[[z,v]]] for v in range(9)]+st['queue']
        else: s='UNRESOLVED'
    st['done'].append([mask,fixes,s])
    json.dump(st,open(st_file,'w'))
    os.remove(tmp)
log.write('DONE\n'); log.close()
