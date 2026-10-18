from vr import *
import json,sys
W0=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz')
NAMES={'r1':239,'r2':240,'r3':245,'r4':246,'s1':265,'s2':266,'s3':271,'s4':272}
ABS={'a3':283,'a1':281,'b9':299,'b7':297}
def build(perm,Q=239):
    w=copy.deepcopy(W0);B=w['B']
    assert B[585][:3]==['add',591,283]
    dead={585}|set(NAMES.values())
    blk=[]
    for n in perm:
        if n in NAMES: blk.append(B[NAMES[n]][:-1]+[None])
        else: blk.append(['add',591,ABS[n],1,1,None])
    newB=[]
    for i,e in enumerate(B):
        if i==Q: newB+=blk
        if i in dead: continue
        newB.append(e)
    w['B']=newB;return w
if __name__=='__main__':
    sols=json.load(open('cluster_sols.json'))
    seen=0
    for perm in sols[:int(sys.argv[1])]:
        w=build(perm);
        r,ch,cone=lazy(w,[591]);b,fr=caps(r);pr=prof(r)
        print(perm, 'changed',ch,'caps',b,'OK' if isinstance(pr,dict) else pr[:60]);sys.stdout.flush()
