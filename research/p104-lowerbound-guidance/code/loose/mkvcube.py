"""VALUE cube (always a sound partition): base CNF with the GLOBAL d-lex-leader; fix d_z (z = 0..k-1) to given values.
d_z = #used rows of U_z^perp (9 = inactive). usage: mkvcube.py base.cnf "a,b,c" out.cnf"""
import pickle,sys
base,vals,out=sys.argv[1],[int(x) for x in sys.argv[2].split('.')],sys.argv[3]
mp=pickle.load(open(base+'.map','rb')); U=mp['used']
k0=next(iter(U))[0]
uz=(lambda k,i:U[('z',k),i]) if isinstance(k0,tuple) else (lambda k,i:U[k,i])
units=[]
for z,a in enumerate(vals):
    if a>0: units.append([uz(z,a-1)])
    if a<9: units.append([-uz(z,a)])
with open(base) as fh: hdr=fh.readline().split(); body=fh.read()
with open(out,'w') as fh:
    fh.write(f'p cnf {hdr[2]} {int(hdr[3])+len(units)}\n'); fh.write(body.rstrip('\n')+'\n')
    for u in units: fh.write(' '.join(map(str,u))+' 0\n')
