"""Producer of the bitE8 word (Dylan Crow, with Anthropic Claude assistance; Apache-2.0).
usage: E8COORD=ham python3 fullword.py params-r865.json out.json[.gz]
Turn a compiled Word into a complete reversible bit word (JSON 'bitE8/1'):
   D: dirt compensation at frame 0 (y_t += helper r for every helper whose initial value reaches y_t)
   A: phase A (word), S: scatter (y_t += copies of retained totals at frame 0), B: phase B,
   C: cleanup at the full frame (reverse of every helper-destination gate of A and B).
Gate = [frame_id, dst, [srcs]] meaning dst += sum(srcs) over F2."""
import json, gzip, sys
import e8lib as E, frames as Fm, compile as C
V=E.V
def build(W):
    nreg=2*V+W.nh
    frames={}
    def fid(mask):
        if mask not in frames: frames[mask]=len(frames)
        return frames[mask]
    fid(0); fid(Fm.FULL)
    def flat(lst):
        out=[]
        for F,dst,srcs,outs in lst:
            f=fid(F)
            if srcs is not None: out.append([f,dst,list(srcs)])
            if outs is not None:
                for o in outs: out.append([f,o,[dst]])
        return out
    A=flat(W.A); B=flat(W.B)
    # decoder reads
    vals=[0]*nreg
    cent_sup=None
    # compute retained totals' x-content after A to derive scatter table
    val=[1<<s for s in range(V)]+[0]*V+[0]*W.nh
    for f,d,srcs in A:
        for s in srcs: val[d]^=val[s]
    cent=[val[q] for q in W.ret]
    reads=C.decoder(cent)
    scat=[list(r) for r in reads]
    # dirt reaching y: symbolic over dirt columns only
    dv=[0]*nreg
    for r in range(2*V,nreg): dv[r]=1<<(r-2*V)
    for f,d,srcs in A:
        for s in srcs: dv[d]^=dv[s]
    cdirt=[dv[q] for q in W.ret]
    for t in range(V):
        for c in reads[t]: dv[V+t]^=cdirt[c]
    for f,d,srcs in B:
        for s in srcs: dv[d]^=dv[s]
    D=[]
    for t in range(V):
        m=dv[V+t]; srcs=[]
        while m:
            b=m&-m; r=b.bit_length()-1; m^=b; srcs.append(2*V+r)
        if srcs: D.append([fid(0),V+t,srcs])
    Cl=[]
    for f,d,srcs in reversed(A+B):
        if d>=2*V: Cl.append([fid(Fm.FULL),d,srcs])
    fr=[None]*len(frames)
    for mk,i in frames.items(): fr[i]=[s for s in range(V) if mk>>s&1]
    start=[fid(Fm.LINE[s]) for s in range(V)]+[fid(0)]*V+[fid(0)]*W.nh
    final=[fid(Fm.FULL)]*V+[fid(Fm.HYP[t]) for t in range(V)]+[fid(Fm.FULL)]*W.nh
    return dict(format='bitE8/1',coords=E.COORD,h=8,v=V,R=W.nh,lines=[list(r) for r in E.LINES],
                form='<x,y>/2' if E.COORD=='ham' else '<x,y>/4',frames=fr,start=start,final=final,
                ret=list(W.ret),scatter=scat,D=D,A=A,B=B,C=Cl)
def save(cert,path):
    data=json.dumps(cert,separators=(',',':'),sort_keys=True).encode()
    if path.endswith('.gz'):
        with open(path,'wb') as fh:
            with gzip.GzipFile(filename='',mode='wb',fileobj=fh,mtime=0) as gz: gz.write(data)
    else: open(path,'wb').write(data)
if __name__=='__main__':
    import ast, ham2, compile2 as C2
    Pd={ast.literal_eval(k):v for k,v in json.load(open(sys.argv[1]))} if sys.argv[1]!='-' else {}
    ham2.P.clear(); ham2.P.update(Pd)
    h=ham2.build(0,True); W=C2.compile2(h)
    cert=build(W); save(cert,sys.argv[2])
    print('R',W.nh,'gates D/A/B/C',len(cert['D']),len(cert['A']),len(cert['B']),len(cert['C']),'frames',len(cert['frames']))
