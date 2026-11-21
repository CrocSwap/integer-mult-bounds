"""write cube CNF for inactive set I (mask over Z16): z in I <-> d_z=9 (used[z,8]); base cnf + units. usage: mkcube.py base.cnf mask out.cnf [extra units as a,b;c ...]"""
import pickle,sys
base,mask,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
mp=pickle.load(open(base+'.map','rb')); U=mp['used']
units=[[U[z,8]] if mask>>z&1 else [-U[z,8]] for z in range(16)]
if len(sys.argv)>4:
    for c in sys.argv[4].split(';'):
        if c: units.append([int(v) for v in c.split(',')])
with open(base) as fh: hdr=fh.readline().split(); body=fh.read()
with open(out,'w') as fh:
    fh.write(f'p cnf {hdr[2]} {int(hdr[3])+len(units)}\n'); fh.write(body.rstrip('\n')+'\n')
    for u in units: fh.write(' '.join(map(str,u))+' 0\n')
