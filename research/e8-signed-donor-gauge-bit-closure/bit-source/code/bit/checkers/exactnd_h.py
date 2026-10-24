import json, sys, collections
def bareiss_det(M):
    M=[row[:] for row in M]; n=len(M); sign=1; prev=1
    for k in range(n-1):
        if M[k][k]==0:
            sw=next((i for i in range(k+1,n) if M[i][k]!=0),None)
            if sw is None: return 0
            M[k],M[sw]=M[sw],M[k]; sign=-sign
        for i in range(k+1,n):
            for j in range(k+1,n):
                M[i][j]=(M[i][j]*M[k][k]-M[i][k]*M[k][j])//prev
        prev=M[k][k]
    return sign*M[n-1][n-1]
def rank_int(B):
    # exact rank via fraction-free elimination
    M=[r[:] for r in B]; r=0; cols=len(M[0]) if M else 0
    for c in range(cols):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                a,b=M[r][c],M[i][c]; M[i]=[x*a-y*b for x,y in zip(M[i],M[r])]
        r+=1
    return r
HH=20
new_dir=sys.argv[1]; base_dir=sys.argv[2]
fr=json.load(open(new_dir+'/frames.json'))['frames']; old=json.load(open(base_dir+'/frames.json'))['frames']
new=[k for k in fr if k not in old or fr[k]['B']!=old[k]['B']]
bad=0; stats=collections.Counter()
for k in new:
    B=fr[k]['B']; A=fr[k].get('A',[])
    d=len(B)
    if d==0: continue
    assert rank_int(B)==d, ('basis rank',k)
    if A:
        assert all(sum(a*b for a,b in zip(ra,rb))==0 for ra in A for rb in B), ('A.B',k)
        assert len(A)+d==HH, ('A dim',k)
    s=[sum(r) for r in B]
    M=[[9*sum(B[i][t]*B[j][t] for t in range(HH))-s[i]*s[j] for j in range(d)] for i in range(d)]
    det=bareiss_det(M)
    stats[(d, det!=0)]+=1
    if det==0: bad+=1
print('changed/new frames:',len(new),' exactly degenerate:',bad,' by (dim,nonzero det):',dict(stats))
