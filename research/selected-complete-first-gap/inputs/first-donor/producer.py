"""Literal productive MOVE28039 on its real pre-MOVE field, then C4 SUB.

All Python construction is offline and independent of runtime parameters.
Runtime uses only the frozen fixed-tape transition alphabet. Apache-2.0;
prepared for @CubeJerry with substantial OpenAI assistance and source credit.
"""
from functools import cache
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys
import types

HERE = Path(__file__).resolve().parent
G = (3, 4, 8, 17, 32, 64, 128, 1, 256)
Q = (128, 0, 0, 128, 0, 0, 0, 9, 0)
ALPHA = (0,)*9
TAPES = 44
CORE_TAPES = 31
EVENTS = (28037, 28039, 28041)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE/'SOURCE-PINS.json').read_text())
    for pin in manifest['files']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'frozen input drift: '+pin['local'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['blob'],
             'frozen Git blob drift: '+pin['local'])
    for pin in manifest['generated']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'source witness drift: '+pin['local'])
    return manifest


def load(path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    sys.modules[name] = value
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value


@cache
def lifetime():
    authenticate()
    return load(HERE/'inputs/lifetime/protocol.py', '_producer_frozen_lifetime')


def source_binding(witness):
    need(witness['index'] == 28039 and witness['event'] == ['MOVE',1349,3,601,False],
         'actual productive source event')
    need(witness['frames'] == {'3':[], '601':[137]}, 'actual source frames')
    need(witness['public'] == 1480 and 1349 < witness['public'], 'productive owner kind')
    need(witness['current_frames_before_MOVE'] == {'1349':3,'1526':601}
         and witness['checked_prefix_events'] == 28039, 'actual live pre-MOVE frames')
    expected = [[28037,['INIT',1526,601]], [28038,['ADD',212,449,'1/2',3]],
                [28039,['MOVE',1349,3,601,False]], [28040,['ADD',124,212,'1',3]],
                [28041,['ADD',1526,1349,'-1',601]]]
    need(witness['first_contacts'] == expected, 'unchanged first-gap chronology')


def compile_native(*, mutation=None):
    """New source-specific five-factor core using unchanged literal kernels."""
    need(mutation in (None, 'wrong-phase'), 'unknown native control mutation')
    c4 = lifetime()
    _, _, home = c4.inputs()
    r2 = home.C
    word = r2.LINEAR.cnot_word(G)
    need(len(word) == 21, 'frozen137 binary word')
    factors = [
        ('right_D_', r2.PHASE.compile_phase(ALPHA, Q, int(mutation == 'wrong-phase'))),
        ('right_G_', r2.compile_word(tuple(reversed(word)))),
        ('central_C_', r2.LEAF.compile_leaf()),
        ('left_G_', r2.compile_word(word)),
        ('left_D_', r2.PHASE.compile_phase(ALPHA, Q, 0)),
    ]
    a = r2.Builder()
    blank, one, mark = r2.BLANK, r2.ONE, r2.MARK
    data, work, trace = r2.DATA, r2.WORK, r2.TRACE
    for tape in (work, trace):
        a.op('move', tape, -1)
        a.op('write', tape, mark)
        a.op('move', tape, 1)
    a.mark('clone')
    a.op('read', data, {'0':'clone0', one:'clone1', blank:'cloned'})
    for bit in ('0', one):
        a.mark('clone'+bit)
        a.op('write', work, bit)
        a.op('move', work, 1)
        a.op('move', data, 1)
        a.op('write', trace, one)
        a.op('move', trace, 1)
        a.op('goto', 'clone')
    a.mark('cloned')
    r2.return_source(a)
    a.rewind(work, ('0', one))
    entries = {}
    for index, (name, (code, alphabet)) in enumerate(factors):
        entries[name] = len(a.code)
        after = factors[index+1][0]+'0' if index+1 < len(factors) else 'commit'
        r2.insert(a, name, code, alphabet, after)
    a.mark('commit')
    entries['commit'] = len(a.code)
    a.op('read', work, {'0':'commit0', one:'commit1', blank:'committed'})
    for bit in ('0', one):
        a.mark('commit'+bit)
        a.op('write', data, bit)
        a.op('write', work, blank)
        a.op('move', work, 1)
        a.op('move', data, 1)
        a.op('write', trace, one)
        a.op('move', trace, 1)
        a.op('goto', 'commit')
    a.mark('committed')
    r2.return_source(a)
    a.rewind(work, (blank,))
    for tape in (work, trace):
        a.op('move', tape, -1)
        a.op('write', tape, blank)
        a.op('move', tape, 1)
    a.op('halt')
    code, alphabet = a.finish((blank, '0', one, mark))
    need(max(row[1] for row in code if row[0] in ('read','write','move')) == 30,
         'native31-tape inventory')
    need(all(row[:2] != ('write',data) for row in code[:entries['commit']]),
         'native donor write before complete successful commit')
    return code, alphabet, entries


def embed_native(g, code, after):
    """Fixed pc/port relocation; native0..30 maps to B1-local3..33."""
    labels = [g.state('PRODUCE28039') for _ in code]
    for pc,(op,*args) in enumerate(code):
        state = labels[pc]
        g.rules.setdefault(state, [])
        nxt = labels[pc+1] if pc+1 < len(code) else after
        if op == 'read':
            for symbol,destination in args[1].items():
                g.add(state, labels[destination], tests=((3+args[0],symbol),))
        elif op == 'write':
            g.add(state, nxt, writes=((3+args[0],args[1]),))
        elif op == 'move':
            need(args[1] in (-1,1), 'nonunit native instruction')
            g.add(state, nxt, moves=((3+args[0],args[1]),))
        elif op == 'goto':
            g.add(state, labels[args[0]])
        elif op == 'halt':
            g.add(state, after)
        else:
            raise ValueError('nonliteral native instruction')
    return labels[0]


def adapter(g, code, after, *, stale=False):
    """Paid inherited six-code split/rejoin with the new native core.

    This is the frozen #7564 adapter scan with only its native invocation
    supplied by embed_native. Constants/ports/cleanup are unchanged.
    """
    _, _, frozen = lifetime().inputs()
    h, data, guide = 3, 4, 34
    stages = {'primitive_return':after}
    cleanup = after
    for tape in range(33,4,-1):
        cleanup = frozen.steps(g,tape,-2,cleanup)
    cleanup = g.rewind(data,cleanup)
    cleanup = g.rewind(h,cleanup)
    cleanup = g.rewind(1,cleanup)
    outside = g.state('producer-outside-delimiter')
    g.add(outside,cleanup,tests=((1,'|'),))
    out_data = frozen.copy_out(g,data,1,outside)
    out_header = frozen.copy_out(g,h,1,out_data)
    post = g.jump(out_header,((1,1),))
    stages['core_return'] = post
    entry = post if stale else embed_native(g,code,post)
    stages['core_entry'] = entry
    ready = g.rewind(1,entry)
    ready = g.rewind(guide,ready)
    for tape in (data,h):
        ready = g.rewind(tape,frozen.steps(g,tape,2,ready))
    incoming = g.state('producer-complete-DATA')
    g.add(incoming,ready,tests=((1,'|'),))
    for bit in '01':
        g.add(incoming,incoming,tests=((1,bit),),writes=((data,bit),),moves=((1,1),(data,1)))
    nxt = incoming
    for field in range(5,-1,-1):
        prefix = g.state('producer-Gamma-prefix')
        pop = g.state('producer-Gamma-pop')
        suffix = g.state('producer-Gamma-suffix')
        g.add(prefix,prefix,tests=((1,'0'),),writes=((h,'0'),(guide,'1')),
              moves=((1,1),(h,1),(guide,1)))
        g.add(prefix,pop,tests=((1,'1'),),writes=((h,'1'),),moves=((1,1),(h,1),(guide,-1)))
        g.add(pop,nxt,tests=((guide,'^'),),moves=((guide,1),))
        g.add(pop,suffix,tests=((guide,'1'),),writes=((guide,'_'),),moves=((guide,-1),))
        for bit in '01':
            g.add(suffix,pop,tests=((1,bit),),writes=((h,bit),),moves=((1,1),(h,1)))
        nxt = prefix
    start = g.jump(nxt,((1,1),(guide,1)))
    for tape in range(33,2,-1):
        start = frozen.steps(g,tape,2,start)
    stages['adapter_entry'] = start
    return start,stages


def reachable(graph, entries):
    """Offline removal of other C4 contact entries; no runtime dispatch work."""
    live, pending = set(), list(entries)
    while pending:
        state = pending.pop()
        if state == 'HALT' or state in live:
            continue
        need(state in graph.rules, 'undefined reachable state')
        live.add(state)
        pending.extend(rule.target for rule in graph.rules[state])
    graph.rules = {name:rules for name,rules in graph.rules.items() if name in live}


def compile_join(*, mutation=None):
    need(mutation in (None,'wrong-phase','stale-donor'), 'unknown verifier-only mutation')
    source_binding(json.loads((HERE/'SOURCE-EVENT.json').read_text()))
    c4 = lifetime()
    graph, original = c4.compile_protocol()
    retained_entries = {event:original['entries'][event] for event in (28037,28041)}
    retained_returns = {event:original['returns'][event] for event in (28037,28041)}
    returned = graph.state('RETURN-28039')
    graph.add(returned,'HALT')
    code,alphabet,core_stages = compile_native(mutation='wrong-phase' if mutation == 'wrong-phase' else None)
    need(alphabet == ('_','0','1','|'), 'native alphabet')
    scatter = c4.bank_transfer(graph,0,3,False,returned)
    invoke,stages = adapter(c4.Relocate(graph),code,scatter,stale=mutation == 'stale-donor')
    entry = c4.bank_transfer(graph,0,3,True,invoke)
    entries = retained_entries | {28039:entry}
    returns = retained_returns | {28039:returned}
    graph.start = entries[28037]
    graph.execution_start = graph.start
    reachable(graph,entries.values())
    graph.validate()
    ports = {t for rules in graph.rules.values() for r in rules
             for pairs in (r.tests,r.writes,r.moves) for t,_ in pairs}
    need(ports == set(range(TAPES)), 'joined44-port inventory')
    return graph, {'entries':entries,'returns':returns,'producer_stages':stages,
                   'native_stages':core_stages,'native_locations':len(code),
                   'source_event':28039,'retained_C4_entries':retained_entries}


def digest(graph):
    return lifetime().digest(graph)


if __name__ == '__main__':
    graph,meta = compile_join()
    print(json.dumps({'states':len(graph.rules),'tapes':TAPES,'native_locations':meta['native_locations'],
                      'graph_sha256':digest(graph),'meta':meta},indent=2))
