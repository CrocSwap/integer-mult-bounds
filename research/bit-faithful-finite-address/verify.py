"""Bounded-support faithful cyclic replay. Apache-2.0; OpenAI Codex assistance."""
import ast,hashlib,itertools,json,math,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];Z=(0,)*9;I=(1,0,0,0,1,0,0,0,1)
def need(x,m):
    if not x:raise ValueError(m)
def unit(i,j):return tuple(int((r,c)==(i,j)) for r in range(3) for c in range(3))
def add(x,y):return tuple(a+b for a,b in zip(x,y))
def mm(a,b):return tuple(sum(a[3*i+k]*b[3*k+j] for k in range(3))%2 for i in range(3) for j in range(3))
def formal(ops):
    out={Z:I}
    for a,n in ops:
        nxt={}
        for b,m in out.items():
            for d,k in ((Z,tuple(x^y for x,y in zip(I,n))),(a,n)):
                e=add(b,d);v=mm(m,k);nxt[e]=tuple(x^y for x,y in zip(nxt.get(e,Z),v))
        out={e:v for e,v in nxt.items() if any(v)}
    return out
def support(ops,target):
    exps={Z}
    for a,n in ops:exps|={add(e,a) for e in exps}
    exps.add(target);return exps
def encode(exps):
    widths=[max(e[i] for e in exps)-min(e[i] for e in exps) for i in range(9)]
    weights=[];q=1
    for width in widths:weights.append(q);q*=width+1
    enc=lambda a:sum(x*y for x,y in zip(a,weights))%q
    need(len({enc(e) for e in exps})==len(exps),'support collision')
    return q,weights,widths
def finite(ops,target,q,weights):
    mask=(1<<q)-1
    def rotate(x,k):
        k%=q;return ((x<<k)&mask) | (x>>(q-k) if k else 0)
    def code(a):return sum(x*y for x,y in zip(a,weights))%q
    for source in range(3):
        for pos in range(q):
            state=[0,0,0];state[source]=1<<pos
            for a,n in reversed(ops):
                old=state;z=[0,0,0]
                for r in range(3):
                    for c in range(3):
                        if n[3*r+c]:z[r]^=old[c]
                state=[old[r]^z[r]^rotate(z[r],code(a)) for r in range(3)]
            expected=[0,0,0];expected[source]=1<<((pos+code(target))%q)
            if state!=expected:return False
    return True
def run():
    for f in json.loads((H/'SOURCES.json').read_text())['files']:
        if f['usage']=='input':need(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source '+f['path'])
    # Extract the frozen noncommuting scalar codes as literals, without importing its implementation.
    tree=ast.parse((ROOT/'research/bit-three-register-lower-bound/controls.py').read_text())
    function=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='check_formal_controls')
    codes=None
    for node in ast.walk(function):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='projectors' for t in node.targets):codes=ast.literal_eval(node.value.args[0].args[1])
    need(codes==(3,1,1,16,16,256,256,3),'source scalar fixture')
    baseline=[(unit(i,i),unit(w,w)) for w in range(3) for i in range(3)]
    a,b,c,d,e=[unit(i,j) for i,j in ((0,0),(1,1),(2,2),(1,0),(0,1))]
    neg=lambda x:tuple(-v for v in x)
    frames=[c,a,b,add(a,d),add(b,neg(d)),add(a,e),add(b,neg(e)),neg(c)]
    noncomm=list(zip(frames,[tuple((code>>i)&1 for i in range(9)) for code in codes]))
    receipts=[]
    for name,ops,target in [('nine-call',baseline,I),('eight-call-rank-two',noncomm,add(a,b))]:
        exps=support(ops,target);q,weights,widths=encode(exps)
        need(formal(ops)=={target:I},'formal '+name);need(finite(ops,target,q,weights),'finite '+name)
        mutant=[(tuple(2*x for x in ops[0][0]),ops[0][1])]+ops[1:]
        mq,mw,_=encode(support(mutant,target));need(formal(mutant)!={target:I} and not finite(mutant,target,mq,mw),'mutant '+name)
        receipts.append(dict(name=name,calls=len(ops),support_count=len(exps),modulus=q,weights=weights,widths=widths,regular_columns=3*q,mutant_modulus=mq))
    alias=[]
    for q in range(2,12):
        ops=[(tuple((q+1)*x for x in baseline[0][0]),baseline[0][1])]+baseline[1:]
        # Deliberately bad quotient discards off-diagonal coordinates (all zero in this fixture).
        weights=[1,0,0,0,q,0,0,0,q*q]
        need(finite(ops,I,q,weights),'alias must pass unsafe finite quotient')
        need(formal(ops)!={I:I},'alias formal failure')
        safe,ws,_=encode(support(ops,I));need(not finite(ops,I,safe,ws),'faithful quotient rejects alias')
        alias.append(dict(unsafe_modulus=q,safe_modulus=safe))
    return dict(status='PASS_FAITHFUL_FINITE_ADDRESS',fixtures=receipts,alias_controls=alias,rational_denominators='Clear a common denominator first; never reduce rational address entries as F2 scalars.',no_new_kappa=True)
if __name__=='__main__':
    x=run();p=H/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(json.loads(p.read_text())==x,'receipt')
    print(x['status'],json.dumps(x['fixtures']), 'aliases=10')
