"""Current two-output swaps in the unchanged finite coded-table grammar.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Builder is retained exactly from the published current scalar table package.
All arithmetic below constructs finite control before runtime fields vary.
"""
from vendor.scalar_tables import Builder, need
import hashlib
import json


def compile_swap(op):
    """Return a fixed table on (x,y,staged-x,guide), plus a static receipt.

    SWAP: (x,y) <- (y,x). SIGNED_SWAP: (x,y) <- (y,-x).
    Public values remain untouched until the whole candidate pair passes.
    """
    need(op in ('SWAP','SIGNED_SWAP'),'two-output source operation')
    negate = op == 'SIGNED_SWAP'
    b=Builder(); b.request(('entry',))

    def guide_one():
        b.emit('write',3,1);b.emit('move',3,1)

    def inputs_forward():
        b.emit('move',0,1);b.emit('move',1,1)

    while b.pending:
        key=b.pending.popleft();b.mark(key);tag=key[0]
        if tag=='entry':
            b.branch(2,{4:('guide-entry',)},('reject','nonblank staged work'))
        elif tag=='guide-entry':
            b.branch(3,{4:('begin',)},('reject','nonblank guide work'))
        elif tag=='begin':
            b.emit('write',3,5);b.emit('move',3,1);b.goto(('start',0,False))
        elif tag=='start':
            _,parity,seen=key
            end=('finish-y',) if parity==0 and seen else ('reject','complete nonempty complex field')
            b.branch(0,{0:('read-y',int(negate),parity,0),
                        1:('read-y',int(negate),parity,1),4:end},
                     ('reject','positive component width'))
        elif tag=='scan':
            _,carry,sx,sz,parity=key
            b.branch(0,{0:('read-y',carry,parity,0),1:('read-y',carry,parity,1),
                        2:('component-end',carry,sx,sz,parity)},
                     ('reject','unterminated signed component'))
        elif tag=='read-y':
            _,carry,parity,x=key
            target=('digit',carry,parity,x)
            b.branch(1,{0:target,1:target},('reject','same complete component shape'))
        elif tag=='digit':
            _,carry,parity,x=key
            u=1-x+carry if negate else x
            z,c=u&1,u>>1
            need(c in (0,1),'finite negation carry')
            b.emit('write',2,z);b.emit('move',2,1)
            guide_one();inputs_forward();b.goto(('scan',c,x,z,parity))
        elif tag=='component-end':
            _,carry,sx,sz,parity=key
            failure = negate and sx==1 and sz==1
            target=('reject','signed first-operand overflow') if failure else ('accepted-end',parity)
            b.branch(1,{2:target},('reject','same complete component shape'))
        elif tag=='accepted-end':
            b.emit('write',2,2);b.emit('move',2,1)
            guide_one();inputs_forward();b.goto(('start',key[1]^1,True))
        elif tag=='finish-y':
            b.branch(1,{4:('finish-staged',)},('reject','same complete field frontier'))
        elif tag=='finish-staged':
            b.branch(2,{4:('rewind-step',)},('reject','exact staged frontier'))
        elif tag=='rewind-step':
            b.emit('move',3,-1);b.goto(('rewind-read',))
        elif tag=='rewind-read':
            b.branch(3,{1:('rewind-inputs',),5:('install-start',)},('reject','complete unary guide'))
        elif tag=='rewind-inputs':
            for port in (0,1,2):b.emit('move',port,-1)
            b.goto(('rewind-step',))
        elif tag=='install-start':
            b.emit('move',3,1);b.goto(('install-guide',))
        elif tag=='install-guide':
            b.branch(3,{1:('install-y',),4:('installed-end',0)},('reject','install guide format'))
        elif tag=='install-y':
            b.branch(1,{s:('install-staged',s) for s in (0,1,2)},('reject','complete protected second field'))
        elif tag=='install-staged':
            y=key[1];symbols=(2,) if y==2 else (0,1)
            b.branch(2,{z:('install-symbols',y,z) for z in symbols},('reject','aligned staged component shape'))
        elif tag=='install-symbols':
            _,y,z=key
            b.emit('write',0,y);b.emit('write',1,z)
            for port in (0,1,2,3):b.emit('move',port,1)
            b.goto(('install-guide',))
        elif tag=='installed-end':
            port=key[1]
            target=('halt',) if port==2 else ('installed-end',port+1)
            b.branch(port,{4:target},('reject','exact installed public frontier'))
        elif tag=='halt':b.emit('halt')
        elif tag=='reject':b.emit('reject',key[1])
        else:raise ValueError('unknown two-output compiler state')
    table=b.finish()
    digest=hashlib.sha256(json.dumps(table,separators=(',',':')).encode()).hexdigest()
    return table,dict(operation=op,rows=len(b.rows),states=len(b.labels),
                      public_ports=2,work_ports=2,negated_input=0 if negate else None,
                      table_sha256=digest)


def source_literal(event,caller):
    """Retain exact source order through the original remapping grammar."""
    need(event.op=='SERVICE','original two-output SERVICE')
    need(len(event.fields)==2 and len(set(event.fields))==2,'distinct ordered field ports')
    token=event.token;wrapped=False
    wrappers={'caller-local':4,'product-left':4,'product-right':5,'unit-fragment':6}
    while isinstance(token,(tuple,list)) and token:
        if len(token)==1 and isinstance(token[0],(tuple,list)):
            token=token[0];wrapped=True;continue
        if isinstance(token[0],str) and token[0] in wrappers:
            need(len(token)==wrappers[token[0]],'source remap wrapper grammar')
            token=token[-1];wrapped=True;continue
        break
    need(isinstance(token,(tuple,list)) and token and isinstance(token[0],str),
         'two-output origin grammar')
    tag=token[0]
    if tag in ('boundary-right','boundary-left'):
        need(len(token)==3,'boundary swap token grammar')
        _,column,raw=token
        rows=caller['boundaries'][tag.split('-')[1]+'_program']
        need(tuple(raw) in tuple(tuple(x) for x in rows),'exact boundary source instruction')
        origin=(tag,column,raw[1],raw[2])
    elif tag=='outer':
        need(len(token)==4,'outer swap token grammar')
        _,site,column,raw=token
        need(type(site) is int and 0<=site<len(caller['physical_events']),'actual outer source site')
        need(tuple(raw)==tuple(caller['physical_events'][site]),'exact outer source instruction')
        origin=(tag,site,column)
    else:raise ValueError('original two-output origin')
    need(len(raw)==3 and raw[0] in ('SWAP','SIGNED_SWAP'),'original source swap operation')
    need(type(column) is int and 0<=column<104,'actual source column')
    expected=(raw[1]*104+column,raw[2]*104+column)
    if not wrapped:need(tuple(event.fields)==expected,'original ordered field binding')
    return raw[0],origin


def bind_services(events,caller):
    cache,services,receipt={},{},[]
    for event in events:
        op,origin=source_literal(event,caller)
        if op not in cache:cache[op]=compile_swap(op)
        table,_=cache[op]
        need(event.token not in services or services[event.token]==table,'unambiguous swap service token')
        services[event.token]=table
        receipt.append((origin,op,tuple(event.fields)))
    return services,tuple(cache[op][1] for op in sorted(cache)),tuple(receipt)
