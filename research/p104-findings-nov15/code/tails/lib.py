import sys,gzip,json,math,collections
sys.path.insert(0,'inputs/PRICEKIT')
import pricekit as pk
KAPPA=0.00365305686569
def load(p): return json.loads(gzip.open(p).read())
def span(b):
    s=1  # bitmask over 512 elements: bit x set if x in span
    S={0}
    for v in b: S|={x^v for x in S}
    m=0
    for x in S: m|=1<<x
    return m
def f(r): return r**(1-KAPPA) if r>0 else 0.0
class Model:
    def __init__(s,W):
        s.W=W; n=W['public']; s.n=n
        s.sp=[span(b) for b in W['frames']]; s.dim=[len(b) for b in W['frames']]
        s.nodes=collections.defaultdict(list)   # reg -> list of node dict(chart, ops, hop_ev)
        for r in range(n): s.nodes[r].append(dict(c=W['initial'][r],ops=[],mv=None))
        s.owned_touch=set()
        s.opnode={}  # event idx -> list of (reg,node)
        for i,e in enumerate(W['program']):
            op,r=e[0],e[1]
            if op=='MOVE':
                if r>=n: continue
                nd=s.nodes[r]; assert nd[-1]['c']==e[2]; nd.append(dict(c=e[3],ops=[],mv=i))
            elif op in('INIT','CLEAR'): pass
            else:
                regs=[r]+([e[2]] if op in('ADD','COPY') else [])
                s.opnode[i]=[(x,len(s.nodes[x])-1 if x<n else None) for x in regs]
                for x,k in s.opnode[i]:
                    if x<n: s.nodes[x][k]['ops'].append(i)
        for r in range(n): assert s.nodes[r][-1]['c']==W['final'][r]
    def cost(s,chs):
        t=0.0
        for a,b in zip(chs,chs[1:]):
            d=abs(s.dim[b]-s.dim[a]); t+=f(d)
        return t
