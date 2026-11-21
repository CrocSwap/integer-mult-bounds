# SPDX-License-Identifier: Apache-2.0
"""Read conservative dependencies for all occurrences in the literal BIT tapes."""


def bits(mask):
    while mask:
        b=mask&-mask
        yield b.bit_length()-1
        mask^=b


def moves(graph):
    dim={int(i):row['dim'] for i,row in graph['frames'].items()}
    val={i:1<<i for i in range(graph['public'])}
    for clock,(op,i,*args) in enumerate(graph['program']):
        if op=='MOVE':
            a,b=args
            yield abs(dim[b]-dim[a]),tuple(bits(val[i])),clock
        elif op=='INIT':val[i]=0
        elif op=='CLEAR':val.pop(i)
        elif op=='ADD':val[i]^=val[args[0]]
        elif op=='SWAP':
            j,=args;val[i],val[j]=val[j],val[i]
        else:raise AssertionError(op)


def packed_counts(graph,caller):
    ports=caller['ports']; n=caller['roles']
    body=caller['body_rank']; m=2*ports
    dim={int(i):e['dim'] for i,e in graph['frames'].items()}
    targets=[(1+body*len(e['stages']),('root',i,p)) for i,e in enumerate(caller['diagonal']) for p in range(ports)]
    calls=list(moves(graph));edges=[];labels=[]
    states=[{(i,0)} for i in range(n)]

    def shift(seq,mask):return {(i,m^mask) for i,m in seq}
    def sources(i,p):return tuple(sorted({j*ports+p for j,_ in states[i]}))

    for when,(op,*a) in enumerate(caller['events']):
        if op=='LOCAL':
            stage,x,y=a;mask=1<<stage
            rows=[sources(i,p) for i in (x,y) for p in range(ports)]
            for h in range(m,graph['public']):
                rows.append((len(targets),))
                targets.append((abs(dim[graph['start'][h]]-dim[graph['final'][h]]),('helper',when,h)))
            for cost,spin,j in calls:
                support=tuple(sorted(set(k for i in spin for k in rows[i])))
                edges.append((cost,support));labels.append(('move',when,j))
            sy=states[y]^shift(states[x],1)
            states[x]=shift(states[x],mask);states[y]=shift(sy,mask)
        elif op=='IDLE_ONE':
            x,s=a;mask=sum(1<<j for j in s)
            for p in range(ports):
                edges.append((body*len(s),sources(x,p)));labels.append(('idle',when,p))
            states[x]=shift(states[x],mask)
        else:
            x,y=a
            if op=='QUERY':
                for p in range(ports):
                    edges.append((1,sources(y,p)));labels.append(('query',when,p))
                states[x]^=shift(states[y],1)
            elif op=='SWAP':states[x],states[y]=states[y],states[x]
            elif op=='ADD':states[x]^=states[y]
            else:raise AssertionError(op)
    for i,e in enumerate(caller['diagonal']):
        assert states[i]=={(i,1+sum(1<<j for j in e['stages']))}
    assert len(targets)==18906 and len(edges)==104904
    return targets,edges,labels
