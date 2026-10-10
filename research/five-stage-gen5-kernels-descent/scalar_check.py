"""Fresh F2 source proof, independent literal projection/inverse and controls.
No saved execution receipt is accepted. Uses the actual clean source context
and freshly emitted local physical records. Assisted with ChatGPT (source527).
Rebound to the gen5 word: 19406 formal columns; the controls corrupt the actual
gen5 context (responses, read chronology, alias reads, gates, centres, partner
deliveries, injections and signs) instead of absent source527 selections.
Gen5 rebinding and controls by DreamingOfClouds with Anthropic Claude assistance.
"""
from collections import Counter,defaultdict
from copy import copy
import hashlib,json,time

N=19406;V=1760   # the event count, coefficient counts and event hash of the kernel word are pinned in expected/kernel-pins.json


def events(records,reverse=False):
    center=None
    for k in (range(len(records)-6,-1,-6) if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if b==N:
                assert center is not None
                b=center
            assert 0<=a<N and 0<=b<N and a!=b
            yield a,b,-c if reverse else c
        elif op==(3 if reverse else 2):
            assert center is None and b==N
            center=a
        elif op==(2 if reverse else 3):
            assert center==a and b==N
            center=None
    assert center is None


def replay_projection(records,reverse=False,omit_event=None):
    n=N;v=V
    columns=[1<<i for i in range(n)];norms=[1]*n
    wanted=columns[:]
    for i in range(v):wanted[v+i]^=1<<i
    largest=1;counts=Counter();digest=hashlib.sha256();count=0
    for event_index,(a,b,c) in enumerate(events(records,reverse)):
        if event_index==omit_event:continue
        if c&1:columns[a]^=columns[b]
        norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a])
        counts[abs(c)]+=1
        digest.update(json.dumps([a,b,c],separators=(',',':')).encode());digest.update(b'\n');count+=1
    assert columns==wanted,'independent literal all-column endpoint'
    from pins import pin
    pin('scalar_events',count);pin('scalar_coefficient_counts',dict(counts))
    if not reverse:pin('scalar_event_sha256',digest.hexdigest())
    return dict(all_formal_columns=n,all_source_and_dirty_restored=True,
                arbitrary_target_contents_preserved=True,
                event_sha256=digest.hexdigest(),weighted_additions=count,
                coefficient_counts=dict(counts),literal_unit_additions=sum(c*n for c,n in counts.items()),
                max_intermediate_row_l1=largest,final_source_row_l1=max(norms[:v]),
                final_target_row_l1=max(norms[v:2*v]),final_dirty_row_l1=max(norms[2*v:]))


def mutated_namespaces(context):
    """Actual-context corruptions; each must make the unchanged scalar program fail."""
    W=context['W'];adj=context['adj'];at=context['at']
    recipients={b:d for b,d in W.pairs}
    odd=lambda s:any(c%2 for c in adj[s].values())
    plain_gauge=next(s for s in W.order if s not in recipients and odd(s))
    recipient=next(b for b in W.order if b in recipients and odd(b))
    dirty=next(s for s in range(W.R) if s not in W.gauge and s in set(W.phys.values()) and odd(s) and s not in context['borrow'])
    def with_adj(role,row):
        a=list(adj);a[role]=row;return dict(adj=a)
    def drop_first(role):
        # an odd coefficient: even responses vanish over F2 and would not test anything
        t=next(u for u,c in adj[role].items() if c%2);return with_adj(role,{u:c for u,c in adj[role].items() if u!=t})
    def move_read(role,time):
        a=defaultdict(list,{k:list(v) for k,v in at.items()})
        a[W.readtime[role]].remove(role);a[time].append(role);return dict(at=a)
    def proxy(**changes):
        P=copy(W);P.__dict__.update(changes);return dict(W=P)
    yield 'omit_gauge_compensation','F2',drop_first(plain_gauge)
    yield 'omit_dirty_compensation','F2',drop_first(dirty)
    yield 'omit_alias_recipient_compensation','F2',drop_first(recipient)
    t=next(u for u,c in adj[plain_gauge].items() if c%2);other=(t+1)%V
    while other in adj[plain_gauge]:other=(other+1)%V
    row=dict(adj[plain_gauge]);row[other]=row.pop(t)
    yield 'misrouted_gauge_response','F2',with_adj(plain_gauge,row)
    row=dict(adj[plain_gauge]);row[t]=-row[t]
    yield 'flipped_gauge_compensation_sign','Z',with_adj(plain_gauge,row)
    position={i:j for j,i in enumerate(W.rest)}
    def last_write(d):
        js=[position[i] for i in W.role_ops[d] if W.ops[i][0]==d and i in position]
        return max(js) if js else None
    written=next(b for b in W.order if b in recipients and odd(b) and last_write(recipients[b]) is not None)
    yield 'alias_read_before_donor_last_write','F2',move_read(written,last_write(recipients[written]))
    yield 'gauge_read_after_first_use','F2',move_read(plain_gauge,W.first[plain_gauge]+1)
    gate=next(i for i in W.rest if W.ops[i][0] not in W.gauge)
    yield 'omitted_gate','F2',dict(omitted={gate})
    roots=[dict(r) for r in W.g['roots']];j=next(k for k,r in enumerate(roots) if r['kind']=='center');roots[j]['targets']=roots[j]['targets'][1:]
    yield 'omitted_centre_scatter','F2',proxy(g=dict(W.g,roots=roots))
    deliveries=defaultdict(list,{k:list(v) for k,v in context['deliveries'].items()});k=next(k for k,v in sorted(deliveries.items()) if v);deliveries[k]=deliveries[k][1:]
    yield 'omitted_partner_delivery','F2',dict(deliveries=deliveries)
    source=dict(W.source);source.pop(next(iter(source)))
    yield 'omitted_source_injection','F2',proxy(source=source)


def run(context,records,progress=lambda text:None):
    import gc
    started=time.monotonic();ns=dict(context);source=ns['SOURCE_TEXT']
    assert hashlib.sha256(source.encode()).hexdigest()=='e675d4eb9d90ff0b44279fae0b46f1a8b39f65421cc38454b70a6b75d0e10b42'
    exec(compile(source,'retained source527 exact scalar word','exec'),ns)
    progress('Checking all19406 source, target and arbitrary dirty F2 columns')
    exact=ns['replay']('F2');assert exact['formal_columns']==N and exact['all_targets']and exact['all_source_and_dirty_restored']
    progress('Checking independent literal physical projection and inverse')
    forward=replay_projection(records);inverse=replay_projection(records,True)
    from pins import pin
    pin('forward_max_row_l1',forward['max_intermediate_row_l1']);pin('inverse_max_row_l1',inverse['max_intermediate_row_l1'])
    try:replay_projection(records,omit_event=forward['weighted_additions']-1)
    except AssertionError:filtered_control='omitted surviving odd payload ADD rejected'
    else:raise AssertionError('filtered odd payload omission accepted')
    bound=ns['replay']('bound');bits=8*((bound.bit_length()+2+7)//8);assert 1<<bits>2*bound
    progress('Checking the signed integer source decoder and dirty restoration')
    integer=[]
    for direction in(1,-1):integer.append(ns['replay']('Z',direction,bits));gc.collect()
    controls={}
    for name,mode,changes in mutated_namespaces(context):
        bad=dict(context);bad.update(changes);exec(compile(source,'retained source527 exact scalar word','exec'),bad)
        try:bad['replay'](mode,bits=bits)
        except AssertionError as error:controls[name]=dict(rejected=True,reason=str(error)[:200])
        else:raise AssertionError('invalid gen5 context mutation accepted: '+name)
    assert len(controls)==11
    return dict(status='PASS_FRESH_GEN5_PRODUCER_SIGNED_DECODER_AND_PARITY_FUSED_F2_INVERSE_AND_CONTROLS',filtered_control=filtered_control,F2=exact,integer=integer,majorant=dict(residual_bound=bound,packing_bits=bits),forward=forward,inverse=inverse,controls=controls,source_sha256=hashlib.sha256(source.encode()).hexdigest(),seconds=time.monotonic()-started,scope='The retained source527 scalar program, run on the gen5 context, proves the signed defining-integer decoder in both directions and rejects11 actual-context corruptions. The emitted parity-filtered word is independently checked on all19406formal F2columns and literalreverse, with its own cancellation-free signed-lift prefix bounds. Its integer endpoint is not asserted equal to the producer decoder; F2payload identity supplies the bit contract. Odd-prime address arithmetic is unchanged.')
