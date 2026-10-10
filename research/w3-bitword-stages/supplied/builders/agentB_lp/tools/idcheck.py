# Catalog-id-level replay: MOVE old must equal current catalog id; ADD frame must equal both registers' catalog ids.
import sys, json, numpy as np
d=sys.argv[1]
s=json.load(open(d+'/249-states.json'))
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
n=s['n']
cur=np.array([s['initial'][str(r)] for r in range(n)]+[s['ZERO']],dtype=np.int64)
bad=0; badk=[]
ops=rec[:,0]; A=rec[:,1]; B=rec[:,2]; C=rec[:,3]; F=rec[:,4]; Z=rec[:,5]
copied=False
for k in range(len(rec)):
    o=ops[k]
    if o==0:
        if cur[A[k]]!=B[k]: bad+=1; badk.append(k)
        cur[A[k]]=C[k]
    elif o==1:
        if cur[A[k]]!=F[k] or cur[B[k]]!=F[k]: bad+=1; badk.append(k)
    elif o==2:
        if cur[A[k]]!=C[k]: bad+=1; badk.append(k)
        cur[n]=F[k]
    elif o==3:
        cur[n]=s['ZERO']
fin=sum(1 for r in range(n) if cur[r]!=s['final'][str(r)])
print(d,'catalog-id mismatches',bad,'final id mismatches',fin, badk[:5])
