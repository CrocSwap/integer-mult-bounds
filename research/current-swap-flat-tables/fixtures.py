"""Observer-only physical fixtures and an independent permutation/sign oracle.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from physical import A,Tape,encode_symbols,symbols_for
from vendor.scalar_tables import need


class CountedTable:
    """Count row fetches without changing the emitted finite table or ports."""
    def __init__(self,table):self.table,self.steps=table,0
    def __getitem__(self,index):
        self.steps+=1
        return self.table[index]


def encode_field(values,widths):
    need(len(values)==len(widths),'fixture component count')
    return encode_symbols(tuple(s for value,width in zip(values,widths)
                                for s in symbols_for((value,),width)))


def decode_field(body):
    need(len(body)%3==0,'whole coded fixture')
    symbols=[4*body[i]+2*body[i+1]+body[i+2] for i in range(0,len(body),3)]
    values,widths,bits=[],[],[]
    for s in symbols:
        if s==2:
            need(bits,'positive decoded component')
            values.append(sum(x<<i for i,x in enumerate(bits))-(bits[-1]<<len(bits)))
            widths.append(len(bits));bits=[]
        else:
            need(s in (0,1),'numeric output symbol');bits.append(s)
    need(not bits,'complete decoded component')
    return tuple(values),tuple(widths)


def oracle(op,xs,ys,widths):
    """Direct original permutation/sign definition, no transducer recurrence."""
    expected=(tuple(ys),tuple(-x if op=='SIGNED_SWAP' else x for x in xs))
    allowed=all(-(1<<(w-1))<=value<(1<<(w-1))
                for row in expected for value,w in zip(row,widths))
    return allowed,expected


def execute(table,xs,ys,widths,work=None,contexts=()):
    public=[Tape(encode_field(xs,widths),origin=17),Tape(encode_field(ys,widths),origin=29)]
    work=work if work is not None else [Tape(origin=41),Tape(origin=53)]
    before=[t.body() for t in public]
    ports=public+work+list(contexts)
    initial=sum(t.actions for t in ports)
    dirty=sum(len(t.body()) for t in work)
    previous_backing=tuple(t.highwater-t.origin for t in work)
    counted=CountedTable(table);error=None
    try:
        for t in work:A.retire(t)
        A.execute_table(counted,tuple(public+work),readonly_context=tuple(contexts))
        for t in work:A.retire(t)
    except ValueError as exc:error=str(exc)
    actions=sum(t.actions for t in ports)-initial
    return dict(error=error,public=public,work=work,contexts=contexts,before=before,
                actions=actions,steps=counted.steps,initial_dirty=dirty,previous_backing=previous_backing,
                output=None if error else tuple(decode_field(t.body()) for t in public))


def check_case(table,op,xs,ys,widths,**kwargs):
    allowed,expected=oracle(op,xs,ys,widths)
    result=execute(table,xs,ys,widths,**kwargs)
    need((result['error'] is None)==allowed,'independent exact signed admission iff')
    public,work=result['public'],result['work']
    ports=public+work+list(result['contexts'])
    need(all(t.sentinel_ok() for t in ports),'protected ancestor sentinels')
    if allowed:
        need(tuple(row[0] for row in result['output'])==expected,'independent permutation/sign endpoint')
        need(all(row[1]==tuple(widths) for row in result['output']),'exact complete component shapes')
        need(all(len(t.body())==len(old) for t,old in zip(public,result['before'])),'same public physical extents')
        need(all(t.blank() for t in work),'literal success work erasure')
        need(all(t.pos==t.origin for t in ports),'complete supplied head return')
        length=sum(w+1 for w in widths)
        need(result['actions']+result['steps'] <= 1024*(length+1)+8*result['initial_dirty']+32*(len(work)+len(result['contexts'])),
             'complete physical-plus-control ceiling')
        need(work[0].highwater-work[0].origin <= max(3*length,result['previous_backing'][0]),
             'staged current backing bound')
        need(work[1].highwater-work[1].origin <= max(3*(length+1),result['previous_backing'][1]),
             'guide current backing bound')
    else:
        need(all(t.body()==old and t.writes==0 for t,old in zip(public,result['before'])),
             'whole-field rejection before either public write')
    return int(allowed),result
