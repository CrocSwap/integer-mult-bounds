"""Independent interpreter of exported addressed steps; no generator import.

Native/completed atom/routing primitives have literal finite semantics here.
This is an operational contract interpreter, not their fixed-tape lowering.
"""
from copy import deepcopy
from fractions import Fraction
from math import gcd


def require(ok,message):
    if not ok:raise ValueError(message)


def matmul(a,b,m):
    return [[sum(x*y for x,y in zip(row,col))%m for col in zip(*b)] for row in a]


def invert(a,m):
    n=len(a);a=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for col in range(n):
        pivot=next((i for i in range(col,n) if gcd(a[i][col],m)==1),None)
        require(pivot is not None,'noninvertible current cover')
        a[col],a[pivot]=a[pivot],a[col];z=pow(a[col][col],-1,m);a[col]=[x*z%m for x in a[col]]
        for i in range(n):
            if i!=col:
                z=a[i][col];a[i]=[(x-z*y)%m for x,y in zip(a[i],a[col])]
    return [row[n:] for row in a]


def run(program,state,fault=None):
    q=program['q']
    require(type(q) is int and q>=3 and q%2==1,'odd prime radix')
    divisor=3
    while divisor*divisor<=q:
        require(q%divisor!=0,'prime radix required');divisor+=2
    p=deepcopy(state);n=8*program['f'];w=program['w'];e=w-1;k=program['borrowed_digits'];M=q**w;R=q**e
    owner,other=map(str,program['owners']);slots=p['slots']
    require(owner!=other and slots[owner]!=slots[other],'distinct physical owners')
    require(state['owners'][owner] is not state['owners'][other],'aliased owner objects')
    data=p['owners'][owner];spectator=deepcopy(p['owners'][other]);outer=(tuple(data['outer']),tuple(data['z']),data['tape_head'])
    require(all(len(data[x])==n*n for x in ('low','high')) and all(len(data[x])==n for x in ('h','d')),'complete owner layout')
    require(all(type(x) is int and 0<=x<q for x in data['low']),'complete low range')
    require(all(type(x) is int and 0<=x<R for x in data['high']),'complete high range')
    require(all(type(x) is int and 0<=x<M for key in ('h','d') for x in data[key]),'complete argument ranges')
    S8=[[Fraction(v) for v in row] for row in program['matcher']]
    def lift(a,modulus):
        return [[(a[i//program['f']][j//program['f']].numerator*pow(a[i//program['f']][j//program['f']].denominator,-1,modulus))%modulus if i%program['f']==j%program['f'] else 0 for j in range(n)] for i in range(n)]
    S=lift(S8,M);Sinv=invert(S,M)
    cache=None;copied=None;cleared=None;inner=None;padding=None;outer_active=False;direction=None
    route_returns=[];restorations=[];calls={};peak_cache=0;mutated=False
    def snapshot():return tuple(data['outer']),tuple(data['z']),data['tape_head']
    def digits(value):return [(value//q**i)%q for i in range(e)]
    def value(ds):return sum(v*q**i for i,v in enumerate(ds))
    def require_row():
        require(snapshot()==outer and p['owners'][other]==spectator,'restored outer ROW and complete spectators')
    for pc,step in enumerate(program['steps']):
        op=step['op'];addresses=step['addresses'];calls[op]=calls.get(op,0)+1
        if op not in ('native_canonical',):
            require(all(type(a) is int and 0<=a<n*n for a in addresses),'address outside owned matrix')
        if len(addresses)==2:require(addresses[0]!=addresses[1],'aliased primitive arguments')
        before_high=tuple(data['high']);before_low=tuple(data['low']);before_h=tuple(data['h']);before_d=tuple(data['d'])
        allowed_high=set();allow_low=allow_body=False
        if op=='outer_enter':
            require(not outer_active,'duplicate outer borrow');outer_active=True
        elif op=='route_enter':
            require(outer_active and direction is None,'route ownership state');direction=step['direction']
        elif op=='cache_allocate':
            require(cache is None,'duplicate cache allocation');cache=[None]*(n*n);copied=set();cleared=set();peak_cache=max(peak_cache,len(cache))
        elif op=='cache_copy':
            a,=addresses;require(cache is not None and a not in copied,'initialized owned low cache');cache[a]=data['low'][a];copied.add(a)
        elif op in ('unit_scale','ordered_shift'):
            require(len(copied)==n*n and inner is None,'complete low snapshot and no active borrow')
            z=Fraction(*step['coefficient']);z=z.numerator*pow(z.denominator,-1,R)%R
            a=addresses[0];allowed_high={a}
            if op=='unit_scale':require(gcd(z,R)==1,'nonunit scale');data['high'][a]=data['high'][a]*z%R
            else:data['high'][a]=(data['high'][a]+z*data['high'][addresses[1]])%R
        elif op=='older_full_swap':
            require(inner is None and padding is None,'fallback owns complete arguments');a,b=addresses;allowed_high={a,b}
            data['high'][a],data['high'][b]=data['high'][b],data['high'][a]
        elif op=='inner_borrow':
            require(inner is None and padding is None and 2*k<e,'legal inner borrow')
            a,b=addresses;ha,db=digits(data['high'][a]),digits(data['high'][b])
            inner=dict(addresses=tuple(addresses),row=tuple(ha[-k:]),other_hi=tuple(db[-k:]))
        elif op=='row_pad':
            require(inner is not None and padding is None,'ROW padding owner')
            size=q**k;stock=program['reserve'];total=((size+stock-1)//stock)*stock
            require(size>=stock and size<=total<2*size,'finite ROW padding bound')
            padding={'size':size,'total':total,'zeros':[0]*(total-size),'returned':False}
        elif op in ('body_sub','body_add','body_rsub','raw_reverse_swap'):
            require(inner is not None and padding is not None and tuple(addresses)==inner['addresses'],'inner primitive ownership')
            a,b=addresses;ha,db=digits(data['high'][a]),digits(data['high'][b]);x,y=ha[:-k],db[:-k];allowed_high={a,b}
            if op=='body_sub':y=[(v-u)%q for u,v in zip(x,y)]
            elif op=='body_add':y=[(v+u)%q for u,v in zip(x,y)]
            elif op=='body_rsub':y=[(u-v)%q for u,v in zip(x,y)]
            else:x,y=list(reversed(y)),list(reversed(x))
            data['high'][a]=value(x+ha[-k:]);data['high'][b]=value(y+db[-k:])
        elif op=='inner_return':
            require(inner is not None and padding is not None and tuple(addresses)==inner['addresses'],'active inner return')
            a,b=addresses
            if fault=='borrowed_row_write' and not mutated:data['high'][a]=(data['high'][a]+q**(e-k))%R;mutated=True
            require(tuple(digits(data['high'][a])[-k:])==inner['row'] and tuple(digits(data['high'][b])[-k:])==inner['other_hi'],'restored borrowed ROW')
            restorations.append(inner['row']);padding['returned']=True;inner=None
        elif op=='row_unpad':
            require(inner is None and padding is not None and padding['returned'],'unpad only after ROW return')
            require(all(x==0 for x in padding['zeros']),'owned padding erasure');padding=None
        elif op=='older_high_swap':
            require(inner is None and padding is None,'high interchange after ROW restoration')
            a,b=addresses;ha,db=digits(data['high'][a]),digits(data['high'][b]);allowed_high={a,b}
            data['high'][a]=value(ha[:-k]+db[-k:]);data['high'][b]=value(db[:-k]+ha[-k:])
        elif op=='carry_shift':
            require(cache is not None and len(copied)==n*n and not cleared,'complete low cache for carry')
            a,=addresses;row,col=divmod(a,n);matrix=S if step['direction']==1 else Sinv
            total=sum(cache[row*n+j]*matrix[j][col] for j in range(n));carry=(total-total%q)//q%R
            data['high'][a]=(data['high'][a]+carry)%R;allowed_high={a}
        elif op=='low_type_commit':
            require(cache is not None and len(copied)==n*n and not cleared,'complete low cache for low permutation')
            matrix=S if step['direction']==1 else Sinv
            data['low']=[sum(cache[row*n+j]*matrix[j][col] for j in range(n))%q for row in range(n) for col in range(n)];allow_low=True
        elif op=='cache_clear':
            a,=addresses;require(cache is not None and a in copied and a not in cleared,'owned cache clear');cache[a]=0;cleared.add(a)
        elif op=='cache_release':
            require(cache is not None and len(cleared)==n*n and all(x==0 for x in cache),'complete owned cache erasure');cache=copied=cleared=None
        elif op=='route_return':
            require(inner is padding is cache is None and direction==step['direction'],'complete route return')
            route_returns.append([data['low'][i]+q*data['high'][i] for i in range(n*n)]);direction=None
        elif op=='native_canonical':
            require(outer_active and direction is None and inner is padding is cache is None and addresses==[4*program['f']],'completed canonical invocation')
            g=[[data['low'][i*n+j]+q*data['high'][i*n+j] for j in range(n)] for i in range(n)];gi=invert(g,M)
            projection=matmul([[g[i][j] if j<4*program['f'] else 0 for j in range(n)] for i in range(n)],gi,M)
            ph=[sum(x*y for x,y in zip(row,data['h']))%M for row in projection];pd=[sum(x*y for x,y in zip(row,reversed(data['d'])))%M for row in projection]
            data['h']=[(x-a+b)%M for x,a,b in zip(data['h'],ph,pd)]
            data['d']=[(x+a-b)%M for x,a,b in zip(data['d'],reversed(ph),reversed(pd))];allow_body=True
        elif op=='outer_return':
            require(outer_active and direction is None and inner is padding is cache is None,'all leases returned');outer_active=False
        else:raise ValueError('unsupported primitive: '+op)
        if fault=='outer_row_write' and op=='raw_reverse_swap' and not mutated:data['outer'][0]+=1;mutated=True
        require_row()
        require(allow_low or tuple(data['low'])==before_low,'complete low spectators')
        require(allow_body or (tuple(data['h'])==before_h and tuple(data['d'])==before_d),'complete payload spectators')
        require(all(x==before_high[i] for i,x in enumerate(data['high']) if i not in allowed_high),'complete high spectators')
    require(not outer_active and direction is inner is padding is cache is None,'no outstanding ownership')
    return p,dict(calls=calls,route_returns=route_returns,borrowed_rows_returned=len(restorations),peak_owned_low_cells=peak_cache)
