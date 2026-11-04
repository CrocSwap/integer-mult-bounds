"""Independent two-sided prefix identities at the literal new cut."""
from algebra import Q,need,coefficient,accumulate,shifted
from rows import apply,scalar_step,product

def verify(word,G,J):
    n,width=word['roles'],word['stages']+2;zero=(0,)*width;one={zero:coefficient(1)}
    def vec(entries):
        out=[{}for _ in range(n)]
        for i,value in entries.items():out[i]={zero:coefficient(value)}
        return out
    a=vec({1:1,20:-1,21:1});b=vec({0:-2,2:2,20:-2,21:-1})
    c=vec({20:1,4:-1});d=vec({4:-1,21:-1})
    S=shifted([scalar_step(one,['LAMBDA',0,1],width)],(-1,)+(0,)*(width-1))[0]
    for events,left,right in ((G,c,d),(J,a,b)):
        column=[dict(x)for x in right]
        for e in events:apply(column,e,width)
        need(column==vec({4:1}),'Ordinary basis maps column to pivot')
        row=vec({4:1})
        for e in reversed(events):apply(row,e,width,True)
        need(row==left,'Ordinary pivot row is the dual functional')
    for left,right in ((a,b),(c,d)):
        value={}
        for u,v in zip(left,right):accumulate(value,product(u,v,width))
        need(value==one,'Unit independent dual pairing')
    cut=353;need(word['events'][cut]==['LAMBDA',20,1],'Source-specific literal cut')
    column=[dict(x)for x in d]
    for e in word['events'][:cut+1]:apply(column,e,width)
    need(column==[product(S,x,width)for x in b],'P d = S b')
    row=[dict(x)for x in a]
    for e in reversed(word['events'][:cut+1]):apply(row,e,width,True)
    need(row==[product(S,x,width)for x in c],'a P = S c')
    return {'cut_after':cut,'input_pairing':'1','cut_pairing':'1','prefix_column':'P d = S b',
            'prefix_row':'a P = S c','ordinary_coefficients':'rational dyadics; no unpaid S or stage factor'}
