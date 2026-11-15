import sys,json,collections,math
sys.path.insert(0,'.')
from lib import load,Model,span
W=load('inputs/ATTACK/COURIER226/hit_c226_1.json.gz'); M=Model(W); n=W['public']
K=0.00365455370060
def f(d): return d**(1-K) if d>0 else 0.0
def sub(a,b): return M.sp[a]&~M.sp[b]==0          # a subset-or-equal b
def ssub(a,b): return sub(a,b) and M.sp[a]!=M.sp[b]
prog=W['program']
def info(h):
    nd=M.nodes[h]
    w=[k for k in range(len(nd)-1) if nd[k]['ops']]
    k=w[-1] if w else 0
    L=nd[k]['c']; lastop=nd[k]['ops'][-1] if nd[k]['ops'] else (nd[k]['mv'] or 0)
    fin=nd[-1]; firstF=fin['ops'][0] if fin['ops'] else len(prog)
    # does h get written (dst) at its final node?
    dstF=sum(1 for i in fin['ops'] if prog[i][1]==h)
    tail=[x['c'] for x in nd[k:]]
    return dict(L=L,dL=M.dim[L],k=k,lastop=lastop,F=fin['c'],firstF=firstF,nF=len(fin['ops']),dstF=dstF,tail=tail,tailcost=sum(f(abs(M.dim[b]-M.dim[a])) for a,b in zip(tail,tail[1:])))
def arrive(r,G):
    nd=M.nodes[r]
    for x in nd:
        if x['c']==G: return x['mv'] if x['mv'] is not None else 0
    return None
def opt(h,G,Tm):
    """can helper h be at chart G (same frame) after main arrival Tm, inside its post-work window? returns (status, dcost)"""
    I=info(h)
    if I['F']!=127 and not (I['F']==G): return ('notV',None)
    if not sub(I['L'],G): return ('L-not-under-G',None)
    if not ssub(G,I['F']): return ('G-not-under-F',None)
    if I['firstF']<=Tm: return ('time',None)
    new=[I['L']]+([G] if I['L']!=G else [])+[I['F']]
    dc=sum(f(abs(M.dim[b]-M.dim[a])) for a,b in zip(new,new[1:]))-I['tailcost']
    return ('ok' if I['L']!=G else 'ok-atG',dc)
if __name__=='__main__':
    for h in map(int,sys.argv[1:]): print(h,info(h))
