"""Offline fixed-graph extension for actual current Word arithmetic.

The inherited divider segment is byte-for-byte unchanged. Runtime contains
only R/W/M/J/H; compile-time digit and slot arithmetic is not a provider.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""

def classify_alias(b, same, different):
    """Compare two encoded six-bit descriptors, restoring both heads."""
    for t in (64,65):b.expect(t,'L');b.op('M',t,1)
    prefix=b.fresh('alias');b.jump(prefix+'_0_0')
    for j in range(6):
        for unequal in (0,1):
            b.mark(prefix+'_'+str(j)+'_'+str(unequal))
            branches={str(x):b.fresh('alias_x') for x in (0,1)};b.read(64,branches)
            for x in (0,1):
                b.mark(branches[str(x)]);other={str(y):b.fresh('alias_y') for y in (0,1)};b.read(65,other)
                for y in (0,1):
                    b.mark(other[str(y)]);b.op('M',64,1);b.op('M',65,1)
                    b.jump(prefix+'_'+str(j+1)+'_'+str(int(unequal or x!=y)))
    for unequal,target in ((0,same),(1,different)):
        b.mark(prefix+'_6_'+str(unequal))
        for t in (64,65):
            b.expect(t,'R')
            for _ in range(7):b.op('M',t,-1)
        b.jump(target)

def primitive(b, d, kind, alias):
    prefix=kind+('_SAME' if alias else '_DISTINCT')
    b.mark(prefix)
    active=(0,) if alias else (0,1)
    if kind!='COMPARE':active=(*active,2)
    for t in active:b.op('M',t,-1);b.expect(t,'L');b.op('M',t,1)
    states=(-1,0,1) if kind=='COMPARE' else (0,1)
    label=lambda stage,state:prefix+'_'+str(stage)+'_'+str(state)
    b.jump(label(0,0))
    for stage in range(5):
        for state in states:
            b.mark(label(stage,state));xs={str(x):b.fresh('digit_x') for x in (0,1)}
            b.read(0,{**xs,**({'R':prefix+'_END_'+str(state)} if stage==4 else {})})
            for x in (0,1):
                b.mark(xs[str(x)])
                ys={x:b.fresh('same_digit')} if alias else {y:b.fresh('digit_y') for y in (0,1)}
                if alias:b.jump(ys[x])
                else:b.read(1,{str(y):target for y,target in ys.items()})
                for y,target in ys.items():
                    b.mark(target)
                    if kind=='COMPARE':nxt=state if x==y else (1 if x>y else -1)
                    else:
                        value=x+y+state if kind=='ADD' else x-y-state
                        nxt=value>>1 if kind=='ADD' else int(value<0)
                        b.expect(2,'_');b.op('W',2,str(value&1))
                    for t in active:b.op('M',t,1)
                    b.jump(label(min(4,stage+1),nxt))
    for state in states:
        b.mark(prefix+'_END_'+str(state))
        if not alias:b.expect(1,'R')
        if kind!='COMPARE':b.expect(2,'_');b.op('W',2,'R')
        for t in active:b.native_rewind(t)
        status=('CMP_'+{-1:'NEG',0:'EQ',1:'POS'}[state]) if kind=='COMPARE' else \
               (('ADD_C' if kind=='ADD' else 'SUB_B')+str(state))
        d.clear_selectors(b,status)

def logical_graph(d):
    b=d.Builder()
    for kind in ('COMPARE','ADD','SUBTRACT'):
        b.mark(kind)
        if kind!='COMPARE':
            d.distinct(b,0,2);d.distinct(b,1,2)
        classify_alias(b,kind+'_SAME',kind+'_DISTINCT')
        primitive(b,d,kind,True);primitive(b,d,kind,False)
    b.mark('FAIL');b.op('H','MALFORMED')
    return b.finish()

def compile_arithmetic(d):
    old,oldlabels,meta=d.compile_divider();logical,ll=logical_graph(d)
    b=d.Builder()
    for pc,row in enumerate(logical):
        b.mark('CORE_'+str(pc));op=row[0]
        if op in ('R','W','M') and row[1]<4:
            d.dispatch(b,row[1],row,'CORE_'+str(pc+1))
        elif op=='R':b.read(row[1],{s:'CORE_'+str(t) for s,t in row[2].items()})
        elif op=='J':b.jump('CORE_'+str(row[1]))
        else:b.op(*row)
    b.mark('FAIL');b.op('H','MALFORMED')
    segment,labels=b.finish();offset=len(old)
    def relocate(row):
        if row[0]=='R':return ('R',row[1],{s:pc+offset for s,pc in row[2].items()})
        if row[0]=='J':return ('J',row[1]+offset)
        return row
    code=old+tuple(relocate(row) for row in segment)
    labels={**oldlabels,**{'SIMPLE_'+s:pc+offset for s,pc in labels.items()}}
    meta=dict(meta,entries={**meta['entries'],**{s:labels['SIMPLE_CORE_'+str(ll[s])] for s in ('COMPARE','ADD','SUBTRACT')}},
              logical_to_physical=meta['logical_to_physical']+[labels['SIMPLE_CORE_'+str(i)] for i in range(len(logical))],
              old_locations=len(old),new_logical_locations=len(logical),simple_logical_labels=ll,
              logical_locations=meta['logical_locations']+len(logical))
    return code,labels,meta
