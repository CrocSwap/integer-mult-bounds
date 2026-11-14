"""One literal selected INIT28037 through SUB28041 graph.

The new even signed half-copy uses frozen physical Gamma/unary helpers.
All table construction is offline and independent of runtime field sizes.
Apache-2.0; @CubeJerry/OpenAI assistance, with predecessor credit.
"""
from functools import cache
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys
import types

HERE = Path(__file__).resolve().parent
TAPES = 45
PUBLIC_BANK = 44
PUBLIC_OWNERS = (124,212,449)
EVENTS = (28037,28038,28039,28040,28041)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for pin in manifest['files']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'frozen source bytes: '+pin['local'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['blob'],
             'frozen source Git blob: '+pin['local'])
    for pin in manifest['generated']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'source prefix witness: '+pin['local'])
    return manifest


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module


@cache
def predecessor():
    authenticate()
    return load(HERE/'inputs/first-donor/producer.py','_first_gap_frozen_C5')


def source_binding(witness):
    expected = [[28037,['INIT',1526,601]], [28038,['ADD',212,449,'1/2',3]],
                [28039,['MOVE',1349,3,601,False]], [28040,['ADD',124,212,'1',3]],
                [28041,['ADD',1526,1349,'-1',601]]]
    need(witness['events'] == expected, 'exact five-event chronology')
    need(witness['frames'] == {'3':[], '601':[137]}, 'exact source frames')
    need(witness['public'] == 1480 and all(x < 1480 for x in PUBLIC_OWNERS+(1349,)),
         'actual public source owners')
    need(witness['initial_before_28037'] == {'124':3,'212':3,'449':3,'1349':3}
         and witness['owned1526_inactive_before_INIT'] is True,
         'actual live/inactive prefix entry')
    need(witness['final_frames'] == {'124':3,'212':3,'449':3,'1349':601,'1526':601}
         and witness['typed_prefix_events_checked'] == 28042, 'actual source prefix exit')


def bank_transfer(g, selected, work, gather, after):
    """Inherited scan pattern, with fixed bank44 and exactly three fields."""
    need(type(selected) is int and 0 <= selected < 3, 'fixed new public slot')
    cleanup = g.rewind(PUBLIC_BANK,g.rewind(work,after,erase=not gather))
    tail = g.state('first-gap-public-dollar')
    g.add(tail,cleanup,tests=((PUBLIC_BANK,'$'),))
    nxt = tail
    for index in range(2,-1,-1):
        active = index == selected
        loop = g.state('first-gap-gather' if gather else 'first-gap-scatter')
        boundary = ((PUBLIC_BANK,'|'),)
        if active and not gather:
            boundary += ((work,'|'),)
        g.add(loop,nxt,tests=boundary,writes=((work,'|'),) if active and gather else (),
              moves=((PUBLIC_BANK,1),))
        for bit in '01':
            if not active:
                g.add(loop,loop,tests=((PUBLIC_BANK,bit),),moves=((PUBLIC_BANK,1),))
            elif gather:
                g.add(loop,loop,tests=((PUBLIC_BANK,bit),),writes=((work,bit),),
                      moves=((PUBLIC_BANK,1),(work,1)))
            else:
                for output in '01':
                    g.add(loop,loop,tests=((PUBLIC_BANK,bit),(work,output)),
                          writes=((PUBLIC_BANK,output),),moves=((PUBLIC_BANK,1),(work,1)))
        nxt = loop
    return g.jump(nxt,((PUBLIC_BANK,1),(work,1)))


def half_primitive(g, after, *, mutation=None, stages=None):
    """Halve only the owned source copy, preserving the target copy."""
    need(mutation in (None,'zero-fill'), 'unknown half control mutation')
    _,add,_ = predecessor().lifetime().inputs()
    S,T,L,W,B = add.S,add.T,add.L,add.W,add.B
    need((S,T,L,W,B) == (1,2,3,4,5), 'frozen signed primitive ports')
    stages = {} if stages is None else stages
    done = g.rewind(S,g.rewind(T,g.rewind(L,g.rewind(B,after))))
    clear = g.state('half-retire-width')
    g.add(clear,g.rewind(W,done),tests=((W,'_'),))
    g.add(clear,clear,tests=((W,'1'),),writes=((W,'_'),),moves=((W,1),))
    component = g.state('half-next-component')
    reject = g.state('half-odd-source')
    g.rules[reject] = []
    reset = add.origin_one(g,W,component)
    loops = {previous:g.state('half-previous-'+str(previous)) for previous in (0,1)}
    checks = {current:g.state('half-end-check-'+str(current)) for current in (0,1)}
    for current,check in checks.items():
        g.add(check,loops[current],tests=((W,'1'),))
        g.add(check,reject if current else reset,tests=((W,'_'),))
    for previous,loop in loops.items():
        for current in (0,1):
            for target in (0,1):
                g.add(loop,checks[current],tests=((S,str(current)),(T,str(target)),(W,'1')),
                      writes=((S,str(previous)),),moves=((S,1),(T,1),(W,1)))
    g.add(component,clear,tests=((S,'|'),(T,'|')))
    for source in (0,1):
        for target in (0,1):
            g.add(component,loops[0 if mutation == 'zero-fill' else source],
                  tests=((S,str(source)),(T,str(target))))
    stages['component_entry'] = component
    stages['odd_reject'] = reject
    # Exact retained paired-header scan: only the fifth value becomes unary.
    nxt = component
    for field in range(5,-1,-1):
        prefix = g.state('half-Gamma-prefix')
        pop = g.state('half-Gamma-pop')
        suffix = g.state('half-Gamma-suffix')
        g.add(prefix,prefix,tests=((S,'0'),(T,'0')),writes=((L,'1'),),
              moves=((S,1),(T,1),(L,1)))
        writes = ((W,'1'),) if field == 4 else ()
        g.add(prefix,pop,tests=((S,'1'),(T,'1')),writes=writes,
              moves=((S,1),(T,1),(L,-1)))
        g.add(pop,nxt,tests=((L,'^'),),moves=((L,1),))
        g.add(pop,suffix,tests=((L,'1'),),writes=((L,'_'),),moves=((L,-1),))
        for bit in (0,1):
            resume = g.jump(pop,((S,1),(T,1)))
            destination = add.double_plus(g,bit,resume) if field == 4 else resume
            g.add(suffix,destination,tests=((S,str(bit)),(T,str(bit))))
        nxt = prefix
    entry = g.jump(nxt,tuple((t,1) for t in (S,T,L,W,B)))
    stages['entry'] = entry
    stages['return'] = after
    return entry


def new_add(g, event, target_slot, source_slot, after, *, half=False, mutation=None):
    old = predecessor().lifetime()
    _,add,_ = old.inputs()
    returned = g.state('RETURN-'+str(event))
    g.add(returned,after)
    cleanup = old.clear_work(g,old.SOURCE_WORK,returned)
    scatter = bank_transfer(g,target_slot,old.TARGET_WORK,False,cleanup)
    proxy = old.Relocate(g)
    scalar_stages = {}
    invoke = add.primitive(proxy,'ADD',2,scatter,scalar_stages)
    half_stages = {}
    if half:
        invoke = half_primitive(proxy,invoke,mutation=mutation,stages=half_stages)
    target = bank_transfer(g,target_slot,old.TARGET_WORK,True,invoke)
    entry = bank_transfer(g,source_slot,old.SOURCE_WORK,True,target)
    return entry,returned,{'scalar':scalar_stages,'half':half_stages,'scatter':scatter}


def redirect_return(g, returned, next_entry):
    rows = g.rules[returned]
    need(len(rows) == 1 and rows[0].target == 'HALT'
         and not rows[0].tests and not rows[0].writes and not rows[0].moves,
         'exact frozen return edge')
    g.rules[returned] = []
    g.add(returned,next_entry)


def compile_gap(*, mutation=None):
    need(mutation in (None,'zero-fill','skip-28038'), 'unknown verification mutation')
    source_binding(json.loads((HERE/'SOURCE-PREFIX.json').read_text()))
    p = predecessor()
    g,old = p.compile_join()
    entry40,return40,stages40 = new_add(g,28040,0,1,old['entries'][28041])
    entry38,return38,stages38 = new_add(g,28038,1,2,old['entries'][28039],half=True,
                                      mutation='zero-fill' if mutation == 'zero-fill' else None)
    redirect_return(g,old['returns'][28037],old['entries'][28039] if mutation == 'skip-28038' else entry38)
    redirect_return(g,old['returns'][28039],entry40)
    g.start = old['entries'][28037]
    g.execution_start = g.start
    p.reachable(g,(g.start,))
    g.validate()
    ports = {t for rules in g.rules.values() for r in rules
             for pairs in (r.tests,r.writes,r.moves) for t,_ in pairs}
    need(ports == set(range(TAPES)), 'fixed45-tape inventory')
    entries = old['entries'] | {28038:entry38,28040:entry40}
    returned = old['returns'] | {28038:return38,28040:return40}
    return g,{'entries':entries,'returns':returned,'new_stages':{28038:stages38,28040:stages40},
              'replaced_C5_returns':(old['returns'][28037],old['returns'][28039]),
              'retained_C5_graph_sha256':'fec60dd4653c6c06846850b2d318d9eec0b7d9856af6b65bae2d336d5c5f99a0',
              'fixed_tapes':TAPES,'new_public_bank_owners':PUBLIC_OWNERS,'events':EVENTS}


def digest(g):
    return predecessor().digest(g)


if __name__ == '__main__':
    graph,meta = compile_gap()
    print(json.dumps({'states':len(graph.rules),'tapes':TAPES,'graph_sha256':digest(graph),'meta':meta},indent=2))
