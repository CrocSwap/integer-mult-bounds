"""Role-level compile of a complex producer: every addition, piece and retained total gets its role slots."""
def compile_roles(c):
    users={x:[] for x in c.active}
    for n in sorted(c.active):
        if c.args[n]:
            for pos,x in enumerate(c.args[n]): users[x].append(('g',n,pos))
    for i,(_,n,_) in enumerate(c.pieces): users[n].append(('p',i))
    for name,n in c.retained: users[n].append(('r',name))
    edge={};src={};pout={};rout={};gates=[];size=0
    for n in sorted(c.active):
        if c.args[n]: ins=(edge[n,0],edge[n,1]); piv=ins[0]
        else: piv=size; size+=1; ins=(piv,); src[c.triples[n-1]]=piv
        outs=(piv,)+tuple(range(size,size+len(users[n])-1)); size+=len(users[n])-1
        assert len(set(ins))==len(ins) and set(ins)&set(outs)=={piv}
        gates.append((n,ins,outs))
        for u,sl in zip(users[n],outs):
            if u[0]=='g': edge[u[1],u[2]]=sl
            elif u[0]=='p': pout[u[1]]=sl
            else: rout[u[1]]=sl
    assert size==c.roles
    return dict(size=size,gates=gates,src=src,pout=pout,rout=rout)
