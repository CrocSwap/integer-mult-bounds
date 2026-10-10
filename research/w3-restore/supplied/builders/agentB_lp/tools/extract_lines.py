# Extract per-line LP module structure from a word (out5b) for rebuilding.
import sys, json, pickle, collections
import numpy as np
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
d=sys.argv[1]; evp=sys.argv[2]; modp=sys.argv[3]; out=sys.argv[4]
W=Word(d); rec=W.rec; dim=W.dim; n=W.n; ZERO=W.ZERO; FULL=W.FULL; init=W.init
L=pickle.load(open(evp,'rb')); ev=L['ev']; chain=L['chain']
mods=pickle.load(open(modp,'rb'))['modregs']
NR=len(rec)
# index records by register
byreg=collections.defaultdict(list)
for k in range(NR):
    o,a,b,c,f,z=rec[k]
    byreg[int(a)].append(k)
    if o==1 and b!=a: byreg[int(b)].append(k)
# content per event from ev: map k -> (dst,src,frame,dim,cat,src_content,dst_after)
evk={e[0]:e for e in ev}
lines={}
bad=0
for key in LINEKEYS:
    regs=mods[key]
    blocks=sorted(X for (k2,X) in DBM if k2==key)
    LM=LINEMASK[key]
    planes={}; copies={}; others=[]
    for r in regs:
        c=chain[r]
        if dim[init[r]]==20: copies[r]=None; continue
        if len(c)>1 and c[1][2]==1 and dim[init[r]]==0:
            # plane register: find dim-3 frame and block
            pf=[x for x in c if x[2]==3][0][1]
            # content at plane: events into r at dim<=3
            cont=0
            for k in byreg[r]:
                if k in evk:
                    e=evk[k]
                    if e[1]==r and e[4]<=3: cont=e[7]
            X=[X for X in blocks if DBM[(key,X)]==cont]
            if len(X)!=1: print('plane content mismatch',key,r); bad+=1; continue
            # last record index of cube phase: last ADD into r at dim<=3
            lastcube=max(k for k in byreg[r] if rec[k][0]==1 and rec[k][1]==r and 0<dim[int(rec[k][4])]<=3)
            planes[X[0]]=dict(r=int(r),frame=int(pf),lastcube=int(lastcube))
        else:
            others.append(int(r))
    # copies: P{Z} frame and old output
    outs={}
    for cp in copies:
        ks=[k for k in byreg[cp] if rec[k][0]==1 and rec[k][1]==cp and dim[int(rec[k][4])]==21]
        if len(ks)!=1: print('copy recv count',key,cp,len(ks)); bad+=1; continue
        k=ks[0]; o=int(rec[k][2]); PZ=int(rec[k][4])
        cont=evk[k][6]
        Z=[Z for Z in blocks if lp_mask(key,Z)==cont]
        if len(Z)!=1: print('copy content mismatch',key); bad+=1; continue
        Z=Z[0]
        mv=[kk for kk in byreg[cp] if rec[kk][0]==0]
        outs[Z]=dict(copy=int(cp),old=o,PZ=PZ,kcopy=int(k),copy_init=int(init[cp]))
    if len(planes)!=10 or len(outs)!=10: print('line',key,'planes',len(planes),'outs',len(outs)); bad+=1
    lines[key]=dict(blocks=blocks,planes=planes,outs=outs,others=sorted(others),copies=sorted(int(c) for c in copies))
print('lines',len(lines),'bad',bad)
pickle.dump(lines,open(out,'wb'))
# summary
cnt=collections.Counter(len(v['others']) for v in lines.values()); print('others per line',cnt)
oldkinds=collections.Counter()
for key,v in lines.items():
    pl={p['r'] for p in v['planes'].values()}
    for Z,o in v['outs'].items(): oldkinds['plane' if o['old'] in pl else 'other']+=1
print(oldkinds)
