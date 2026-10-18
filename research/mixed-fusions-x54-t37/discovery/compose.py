"""3-way compose: base J + (F-J) + (X-J) [+ (D-J)] with disjoint list edits; cleanup/early remapped semantically."""
import json,gzip,hashlib,difflib,sys
L=lambda f: json.loads(gzip.decompress(open(f,'rb').read()))
def ops(a,b):
    sm=difflib.SequenceMatcher(None,[json.dumps(x) for x in a],[json.dumps(x) for x in b],autojunk=False)
    return [(t,i1,i2,b[j1:j2]) for t,i1,i2,j1,j2 in sm.get_opcodes() if t!='equal']
def merge(base,diffs):
    allops=sorted([o for d in diffs for o in d],key=lambda o:(o[1],o[2]))
    out=[];pos=0
    for t,i1,i2,new in allops:
        assert i1>=pos,('overlap',t,i1,i2,pos)
        out+=base[pos:i1]+new;pos=i2
    return out+base[pos:]
def compose(J,F,X,D=None):
    W=json.loads(json.dumps(J))
    others=[F,X]+([D] if D else [])
    for k in J:
        if k in ('cleanup','early_cleanup','report'):continue
        ch=[o for o in others if o[k]!=J[k]]
        if not ch: continue
        if isinstance(J[k],list) and len(ch)>1: W[k]=merge(J[k],[ops(J[k],o[k]) for o in ch])
        else:
            assert len(ch)==1,('dict conflict',k); W[k]=ch[0][k]
    for k in F:
        if k not in J: W[k]=F[k]
    # cleanup: X = [xpre]+J.cleanup+[xtail]; composed = [xpre]+F.cleanup+[xtail]
    Jc,Fc,Xc=J['cleanup'],F['cleanup'],X['cleanup']
    assert Xc[1:-1]==Jc
    C=[Xc[0]]+Fc+[Xc[-1]]
    # J index -> F index for kept elements
    sm=difflib.SequenceMatcher(None,[json.dumps(x) for x in Jc],[json.dumps(x) for x in Fc],autojunk=False)
    j2f={}
    for t,i1,i2,j1,j2 in sm.get_opcodes():
        if t=='equal':
            for d in range(i2-i1): j2f[i1+d]=j1+d
    # early lists
    Fe=[[i+1,U] for i,U in F['early_cleanup']]
    Je=J['early_cleanup'];Xe=X['early_cleanup']
    tail=len(Xc)-1
    new=[e for e in Xe if e[0]==tail]; assert len(new)==1
    k=Xe.index(new[0])
    rest=[e for e in Xe if e[0]!=tail]
    assert rest==[[i+1,U] for i,U in Je],'X early = shifted J early + tail'
    # entry following the tail entry in X's list -> its J entry -> its image in F's early list
    if k==0: pos=0
    elif k<len(rest):
        ji,U=Je[k]; img=[j2f[ji]+1,U]
        assert img in Fe,('follower not kept by F',Je[k]); pos=Fe.index(img)
    else: pos=len(Fe)
    E=Fe[:pos]+[[len(C)-1,new[0][1]]]+Fe[pos:]
    W['cleanup']=C;W['early_cleanup']=E
    return W
if __name__=='__main__':
    J,F,X=L(sys.argv[1]),L(sys.argv[2]),L(sys.argv[3]); D=L(sys.argv[4]) if sys.argv[4]!='-' else None
    W=compose(J,F,X,D); W['report']=dict((D or J)['report']); W['report']['local_profile']=json.loads(sys.argv[6])
    raw=json.dumps(W,separators=(',',':')).encode(); open(sys.argv[5],'wb').write(gzip.compress(raw,mtime=0))
    print(hashlib.sha256(raw).hexdigest())
