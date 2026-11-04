"""Check the caller by reverse rows and check both dual-pair identities.

This engine uses one row or column at a time. It does not call the source
matrix replay. The exact coefficient ring comes from the retained source.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from algebra import Q, coefficient, accumulate, shifted, zmul, need


def scalar_step(value, event, width):
    op = event[0]
    if op == 'SCALE':
        return {key:zmul(coefficient(event[-1]),c) for key,c in value.items()}
    if op == 'Q_POWER':
        return shifted([value],(event[-1],)+(0,)*(width-1))[0]
    if op == 'LAMBDA':
        out = {}
        accumulate(out,value,(Q(1,2),Q(event[-1],2)))
        accumulate(out,shifted([value],(2,)+(0,)*(width-1))[0],(Q(1,2),Q(-event[-1],2)))
        return out
    raise ValueError('Scalar opcode')


def apply(vector, event, width, reverse=False):
    op = event[0]
    if op in ('SCALE','Q_POWER','LAMBDA'):
        r=event[1]
        vector[r]=scalar_step(vector[r],event,width)
    elif op == 'SWAP':
        a,b=event[1:]
        vector[a],vector[b]=vector[b],vector[a]
    elif op in ('ADD','QUERY','LOCAL'):
        if op == 'LOCAL':
            stage,src,dst=event[1:]
            exponent,c=-1,coefficient(1)
            term=(0,)+tuple(int(i==stage)for i in range(width-1))
            if reverse:
                for r in (src,dst):vector[r]=shifted([vector[r]],term)[0]
        else:
            dst,src=event[1:3]
            exponent,c=(0,coefficient(event[3]))if op=='ADD' else(event[3],coefficient(1))
        a,b=(src,dst)if reverse else(dst,src)
        accumulate(vector[a],shifted([vector[b]],(exponent,)+(0,)*(width-1))[0],c)
        if op == 'LOCAL' and not reverse:
            for r in (src,dst):vector[r]=shifted([vector[r]],term)[0]
    elif op in ('IDLE','IDLE_ONE'):
        roles,stages=(event[1:3],event[3])if op=='IDLE' else([event[1]],event[2])
        term=(0,)+tuple(int(i in stages)for i in range(width-1))
        for r in roles:vector[r]=shifted([vector[r]],term)[0]
    else:
        raise ValueError('Caller opcode')


def transpose(word):
    n,width=word['roles'],word['stages']+2
    zero=(0,)*width
    for output in range(n):
        vector=[{}for _ in range(n)]
        vector[output]={zero:coefficient(1)}
        for event in reversed(word['events']):apply(vector,event,width,True)
        expected=[{}for _ in range(n)]
        d=word['diagonal'][output]
        expected[output]={(d[0]%4,*d[1:]):coefficient(1)}
        need(vector==expected,'Every independent reverse caller coefficient')
    return {'rows':n,'coefficients':n*n}


def product(a,b,width):
    out={}
    for key,c in a.items():
        accumulate(out,shifted([b],key)[0],c)
    return out


def dual_pair(source, boundary, middle):
    n,width=source['roles'],source['stages']+2
    zero=(0,)*width
    one={zero:coefficient(1)}
    lam=scalar_step(one,['LAMBDA',0,1],width)
    inv=scalar_step(one,['LAMBDA',0,-1],width)
    def vec(entries):
        out=[{}for _ in range(n)]
        for r,value in entries.items():out[r]=value if isinstance(value,dict)else{zero:coefficient(value)}
        return out
    neg=lambda value:{k:zmul(coefficient(-1),c)for k,c in value.items()}
    a=vec({1:1,2:-2,20:neg(lam),21:1})
    b=vec({2:-1,21:-1})
    c=vec({20:1,4:-1})
    d=vec({21:neg(inv),4:-1})
    s=shifted([lam],(-1,)+(0,)*(width-1))[0]
    for events,left,right in ((boundary,c,d),(middle,a,b)):
        column=[dict(v)for v in right]
        for event in events:apply(column,event,width)
        unit=vec({4:1})
        need(column==unit,'The basis sends the dual column to the pivot')
        row=vec({4:1})
        for event in reversed(events):apply(row,event,width,True)
        need(row==left,'The pivot row is the declared dual functional')
    for x,y in ((a,b),(c,d)):
        value={}
        for u,v in zip(x,y):accumulate(value,product(u,v,width))
        need(value==one,'Unit dual pairing')
    column=[dict(v)for v in d]
    for event in source['events'][:329]:apply(column,event,width)
    need(column==[product(s,v,width)for v in b],'Prefix times d equals S times b')
    row=[dict(v)for v in a]
    for event in reversed(source['events'][:329]):apply(row,event,width,True)
    need(row==[product(s,v,width)for v in c],'a times prefix equals S times c')
    return {'cut_after':328,'input_pairing':'1','cut_pairing':'1',
            'prefix_column':'P d = S b','prefix_row':'a P = S c'}
