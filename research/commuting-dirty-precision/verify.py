"""Source-bound budget audit and literal target-dependent rounded controls.
Philipp (@mightyOil), substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent

def load(path, name):
    spec=importlib.util.spec_from_file_location(name, path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

p=load(HERE/'precision.py','commuting_precision')
d=load(HERE/'vendor/pr1054/dirty_stride.py','pinned_dirty_stride')
old=load(HERE/'vendor/pr1054/budget.py','pinned_old_budget')
need=p.need

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()

def pins():
    rows=json.loads((HERE/'VENDOR-PINS.json').read_text())['sources']
    expected={'vendor/pr1054/'+f for f in ('budget.py','dirty_stride.py','PROOF.md','NOTICE.md')}
    expected|={'vendor/pr1085/PROOF.md','vendor/pr1085/README.md', 'vendor/pr1278/PROOF.md',
               'vendor/pr1278/NOTICE.md','vendor/pr628/dirty.py','vendor/pr628/NOTICE.md','vendor/LICENSE'}
    need({r['path'] for r in rows}==expected,'source inventory')
    for r in rows:
        raw=(HERE/r['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==r['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'source Git blob')
    return len(rows)


def binding_checks():
    """Bind the actual PR1054 logical dispatch to PR628 in both directions.

    Only the numerical leaf body is instrumented away. The recursive split,
    argument wiring, signs and depth-reused scratch are literal source AST.
    """
    source=ast.parse((HERE/'vendor/pr1054/dirty_stride.py').read_text())
    compose=next(node for node in source.body if isinstance(node,ast.FunctionDef) and node.name=='compose')
    run=next(node for node in compose.body if isinstance(node,ast.FunctionDef) and node.name=='run')
    leaf=run.body[0]
    need(isinstance(leaf,ast.If) and ast.unparse(leaf.test)=='hi - lo == 1','source leaf boundary')
    leaf.body=ast.parse('out.append((src, dst, lo, direction)); return').body
    source_tree=ast.fix_missing_locations(ast.Module(body=[run],type_ignores=[]))
    original=ast.parse((HERE/'vendor/pr628/dirty.py').read_text())
    dispatch=next(node for node in original.body if isinstance(node,ast.FunctionDef) and node.name=='compose')
    oldtree=ast.Module(body=[dispatch],type_ignores=[])
    rows=[]
    for n in tuple(range(1,34))+(63,64,65,127,128,129):
        h=(n-1).bit_length()
        for sign in (-1,1):
            out=[];env={'scratch':list(range(2,h+2)), 'out':out}
            exec(compile(source_tree,'pinned-pr1054-dispatch','exec'),env)
            env['run'](0,1,0,n,0,sign)
            banks=[[0] for _ in range(h+2)];ids={id(b):i for i,b in enumerate(banks)};ref=[]
            def observe(x,y,j,phases,beta,bits,direction,s,stats):
                ref.append((ids[id(x)],ids[id(y)],j,s))
            env2={'c':SimpleNamespace(need=need,norm2=lambda z:z*z),'leaf':observe}
            exec(compile(oldtree,'pinned-pr628-dispatch','exec'),env2)
            env2['compose'](banks[0],banks[1],list(range(n)),banks[2:],[1],F(1,2),64,1,sign)
            need(out==ref,'literal recursive-word binding')
            need(len(out)==p.structure(n)[1],'dispatch exact paid count')
            rows.append((n,sign,len(out),digest(out)))
    return dict(cases=len(rows),literal_leaves=sum(r[2] for r in rows),sha256=digest(rows))


def budget_checks():
    rows=[]
    def calls(n):
        return 1 if n==1 else 2*(calls(n//2)+calls(n-n//2))
    def ceil_power(x):
        k=0
        while (1 << k)<x:k+=1
        return k
    for r in range(3,513):
        if not p.prime_power(r):continue
        prime=next(i for i in range(2,r+1) if r%i==0)
        phi=r-r//prime
        for target in (0,1,16,128,1024):
            for m in (0,20,128):
                for incoming in (0,64,10**10):
                    z=p.uniform(r,target,m,incoming)
                    v=old.uniform(r,target,m,incoming)
                    n=r-1; h=(n-1).bit_length(); C=h+2; N=calls(n)
                    ell=ceil_power(r); d0=1+2*ell+r*n*phi; a0=2*d0+r+2
                    K=a0+2*r+ell; c=ceil_power(C)
                    need(z['leaf_calls']==N and z['phi']==phi,'independent count/phi')
                    need(z['prefix_exponent']==K+c and z['interval_exponent']==K+2*c,'transport exponents')
                    W=z['working_bits']; A=z['local_error_exponent']; g=z['margin_exponent']
                    # Prove the bounds by exact integer exponent inequalities; no floats.
                    slack=W-target-m-A-(2*K+3*c)-3
                    need(slack>=0 and N <= 1<<slack,'error exponent')
                    need(W>=incoming and W>=4*g+16,'grid and admission')
                    need(W>=A+K+2*c+ceil_power(N)+1,'feedback')
                    need(z['integer_bits']==K+c+m+8*g+2*ell+16,'inverse preimage guard')
                    need(z['factor_bits']==v['factor_bits'] and z['preparation_error_exponent']==v['preparation_error_exponent'],'preparation unchanged')
                    need(z['leaf_calls']==v['leaf_calls'] and z['depth']==v['depth'],'paid recursion unchanged')
                    need(W<=v['working_bits'] and z['integer_bits']<=v['integer_bits'],'monotone improvement')
                    need(W<=max(target,incoming)+m+15*r**3 and z['integer_bits']<=m+15*r**3,'cubic envelopes')
                    rows.append(z)
    table=[]
    for r in (3,4,8,16,32,64,128,256,512):
        z=p.uniform(r,128,20,0);v=old.uniform(r,128,20,0)
        table.append(dict(radix=r,old_fractional=v['working_bits'],new_fractional=z['working_bits'],
                          old_integer=v['integer_bits'],new_integer=z['integer_bits'],
                          leaf_calls=z['leaf_calls'],borrowed_arrays=z['depth'],
                          factor_bits=z['factor_bits']))
    generic=[]
    for n in (1,2,3,4,7,8,15,16):
        for beta in (F(1,2),F(1,3),F(1,16)):
            for G in (F(1),F(7,3),F(32)):
                for D in (F(0),F(1,3),F(4)):
                    z=p.choose(n,8,beta,G,D,32,16);v=old.choose(n,8,beta,G,D,32,16)
                    need(z['working_bits']<=v['working_bits'],'generic precision monotonicity')
                    B=z['prefix_bound'];L=z['interval_bound'];a=z['local_error'];u=F(1,1<<z['working_bits'])
                    need(z['error']==2*z['leaf_calls']*L*a*u*(B*D+1),'generic transport')
                    need(z['error']<=F(1,1<<33),'generic error')
                    generic.append(z)
    return dict(uniform_cases=len(rows),uniform_sha256=digest(rows),generic_cases=len(generic),
                generic_sha256=digest(generic),comparison=table)

class Bank:
    # Independent literal index counter; input and private dirty values retained.
    def __init__(self, data):
        self.data=list(data);self.reads=0;self.writes=0;self.peak=max(abs(a)+abs(b) for a,b in data)
    def __len__(self):return len(self.data)
    def __getitem__(self, i):
        need(type(i) is int,'scalar indexed read');self.reads+=1;return self.data[i]
    def __setitem__(self, i, value):
        need(type(i) is int,'scalar indexed write');self.writes+=1;self.data[i]=value
        self.peak=max(self.peak,abs(value[0])+abs(value[1]))
    def __iter__(self):raise ValueError('unpriced array iteration')

def values(length,bits,salt):
    u=F(1,1<<bits)
    return [(F(2*((5*i+salt)%13)-11,8)+u,F(2*((7*i+salt)%11)-9,16)+u) for i in range(length)]

def oracle(source,b,stride):
    # Finite geometric sum, separately written; no rounded source algorithm.
    length=len(source);q=length//gcd(length,stride);power=d.ONE
    weights=[]
    for _ in range(q):weights.append(power);power=d.mul(power,b)
    den=d.sub(d.ONE,power)
    return [d.div(tuple(sum(w[k]*x[0]-w[1-k]*x[1] if k==0 else w[0]*x[1]+w[1]*x[0]
                           for w,x in [(weights[t],source[(i-t*stride)%length]) for t in range(q)])
                       for k in range(2)),den) for i in range(length)]

def ideal(source,factors,tau,stride):
    result=source
    for inside,b,scale in factors:
        phase=(tau[0],-tau[1]) if inside else tau
        coeff=d.mul(b,phase);mult=phase if inside else (-b[0],-b[1])
        mult=tuple(scale*z for z in mult);s=-stride if inside else stride;shift=-stride if inside else 0
        solved=oracle(result,coeff,s)
        result=[d.mul(mult,solved[(i-shift)%len(source)]) for i in range(len(source))]
    return result

def rounded_checks():
    rows=[];nonzero=0;total_leaves=0
    for n in (2,3,4,7,8):
        r=n+1;beta=F(1,2);G=F(r)*2**n
        budget=p.choose(n,r,beta,G,4,40,16);oldbudget=old.choose(n,r,beta,G,4,40,16)
        W=budget['working_bits'];h=budget['dirty_arrays']
        factors=[(bool(j%2),(F(3,10),F(2,5)),F(r if j==0 else 1)) for j in range(n)]
        # Each inverse factor has norm <= 2; the one scale r is charged.
        for length,stride in ((3,1),(5,-2)):
            for tau in (d.ONE,(F(3,5),F(4,5))):
                originals=[values(length,W,36+7*j) for j in range(h+2)]
                need(max(abs(a)+abs(b) for bank in originals for a,b in bank)<=4,'input magnitude')
                need(all((v*(1<<W)).numerator%2 for bank in originals for pair in bank for v in pair),'arbitrary low dirty bits')
                exact=ideal(originals[0],factors,tau,stride);arrays=[Bank(bank) for bank in originals]
                bills=[];errors=[]
                for sign in (1,-1,-1,1):
                    before=[b.data[:] for b in arrays];reads=sum(b.reads for b in arrays);writes=sum(b.writes for b in arrays)
                    meter=d.compose(arrays[0],arrays[1],factors,arrays[2:],tau,beta,W,stride,sign)
                    need(sum(b.reads for b in arrays)-reads==meter.reads and sum(b.writes for b in arrays)-writes==meter.writes,'actual data access accounting')
                    need(arrays[0].data==originals[0] and [b.data for b in arrays[2:]]==originals[2:],'dirty restoration')
                    err=max(d.norm2(d.sub(d.sub(y,z),tuple(sign*t for t in e))) for y,z,e in zip(arrays[1].data,before[1],exact))
                    need(err<=budget['error']**2,'complete signed word error')
                    nonzero+=bool(err);errors.append(p.clog(err) if err else None)
                    need(meter.leaves==budget['leaf_calls'],'paid leaf count')
                    need(meter.tape_moves<=8192*(meter.leaves+1)*(h+2)*length,'full routing bill')
                    need(all(v==0 for v in meter.heads.values()),'heads restored')
                    need(max(b.peak for b in arrays)<=budget['internal_magnitude'],'signed internal guard')
                    bills.append({k:getattr(meter,k) for k in ('reads','writes','tape_moves','products','power_products','divisions','nodes','leaves')})
                    total_leaves+=meter.leaves
                    if len(bills) in (2,4):need([b.data for b in arrays]==originals,'whole word inverse')
                # Same incoming data also lies on the older finer grid. Compare the
                # literal paid operation census, not numerical equality across grids.
                older=[Bank(bank) for bank in originals]
                meter=d.compose(older[0],older[1],factors,older[2:],tau,beta,oldbudget['working_bits'],stride,1)
                need({k:getattr(meter,k) for k in bills[0]}==bills[0],'unchanged full operation bill at new width')
                rows.append(dict(n=n,length=length,stride=stride,tau=list(map(str,tau)),working_bits=W,old_working_bits=oldbudget['working_bits'],integer_bits=budget['integer_bits'],error_log2_squared=errors,forward_bill=bills[0]))
    need(nonzero>0,'rounded tests must exercise nonlinear errors')
    # Concrete target dependence: a target-independent surrogate is insufficient.
    inc=[]
    for salt in (1,2):
        x=Bank(values(3,48,36));y=Bank(values(3,48,salt));before=y.data[:]
        d.lift(x,y,(F(3,10),F(2,5)),F(1,2),48,1)
        inc.append([d.sub(a,b) for a,b in zip(y.data,before)])
    need(inc[0]!=inc[1],'actual target dependence control')
    return dict(cases=len(rows),signed_words=4*len(rows),signed_leaf_calls=total_leaves,
                nonzero_error_words=nonzero,target_dependent=True,rows=rows)

def controls():
    names=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,ZeroDivisionError):names.append(name)
        else:raise ValueError('accepted '+name)
    reject('non-prime-power',lambda:p.uniform(6,1,0,0))
    reject('negative-target-precision',lambda:p.uniform(3,-1,0,0))
    reject('missing-feedback',lambda:p.execute(8,8,F(1,2),10**30,4,20))
    reject('unsafe-length-admission',lambda:p.execute(1,1,F(1,2),1,0,4))
    reject('unpaid-subset-budget',lambda:p.choose(2,3,F(1,2),F(1,2),1,40,0))
    z=p.uniform(64,128,20,0)
    K=z['subset_exponent'];c=z['coefficient_exponent'];A=z['local_error_exponent'];N=z['leaf_calls']
    wrong=z['working_bits']-K
    need(wrong<128+3+p.clog(N)+A+20+2*K+3*c,'dropping second subset factor detected')
    names.append('second-subset-factor-retained')
    oldI=z['prefix_exponent']+20+7*z['margin_exponent']+2*p.clog(64)+16
    need(oldI<z['integer_bits'],'inverse-preimage-factor retained');names.append('inverse-preimage-reserve-retained')
    # PR1244 seven-factor obstruction at real leaf-destination cut [13,27).
    # Every descending subset is I, J, D or DJ with norm <= M, but this
    # actual interval has a diagonal block I-JD of norm 1+M^2 > C^2 M.
    M=100
    J=((F(0),F(M)),(F(-1,M),F(0)));D=((F(1,M),F(0)),(F(0),F(M)))
    mm=lambda a,b:[[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    norm=lambda a:max(sum(abs(t) for t in row) for row in a)
    need(norm(J)==M and norm(D)==M and norm(mm(D,J))==1,'ordered subset premise')
    def word(lo,n,x,y,depth):
        if n==1:return [(x,y,lo,1)]
        k=n//2;left=word(lo,k,x,depth+2,depth+1);right=word(lo+k,n-k,depth+2,y,depth+1)
        inverse=lambda w:[(x,y,j,-sign) for x,y,j,sign in reversed(w)]
        return left+right+inverse(left)+inverse(right)
    literal=word(0,7,0,1,0)
    E=[[F(i==j) for j in range(10)] for i in range(10)]
    factors=[((F(1),F(0)),(F(0),F(1))) for _ in range(7)]
    factors[1]=J;factors[4]=D
    for x,y,j,sign in literal[13:27]:
        original=[row[:] for row in E]
        for a in range(2):
            for b in range(10):E[2*y+a][b]+=sign*sum(factors[j][a][k]*original[2*x+k][b] for k in range(2))
    need(abs(E[8][8])+abs(E[8][9])==1+M*M and norm(E)>25*M,'actual noncommuting interval counterexample')
    names.append('noncommuting-interval-rejects-linear-G')
    return names

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    receipt=dict(status='PASS_COMMUTING_DIRTY_PRECISION',seed=64,sources=pins(),dispatch=binding_checks(),budgets=budget_checks(),rounded=rounded_checks(),controls=controls())
    if args.write:
        with args.write.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
    else:need(receipt==json.loads((HERE/'CERTIFICATE.json').read_text()),'certificate mismatch')
    print(receipt['status'], 'uniform='+str(receipt['budgets']['uniform_cases']), 'rounded_words='+str(receipt['rounded']['signed_words']), 'controls='+str(len(receipt['controls'])))
if __name__=='__main__':main()
