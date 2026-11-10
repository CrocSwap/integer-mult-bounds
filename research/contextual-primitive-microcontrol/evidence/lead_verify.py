"""Lead-written target-graph probes; no source executor import."""
import sys
from pathlib import Path
p = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(p))
from lower import Layout, compile_primitive

def run(program, bodies, heads):
    cells = [{-1: 2, **dict(enumerate(x))} for x in bodies]
    heads = list(heads)
    state, clock = program.initial, 0
    while clock < 100000:
        op, *args = program.states[state]
        if op == 'stop': return tuple(args), clock, cells, heads
        clock += 1
        if op == 'nop': state = args[0]
        elif op == 'read':
            port, edges = args
            state = edges[cells[port].get(heads[port], 6)]
        elif op == 'write':
            port, value, state = args
            cells[port][heads[port]] = value
        elif op == 'move':
            port, delta, state = args
            heads[port] += delta
        else: raise RuntimeError(op)
    raise RuntimeError('unexpected nontermination')

layout = Layout(4, (2,), (0,), (3,))
program = compile_primitive((('halt',),), layout)
count = 0
for length in (0, 1, 5, 31, 97):
    for head in (0, length, length+13):
        for ctx_head in (0, 11):
            bodies = [[1]*length, [4,5,3], [], [0,1]*6]
            result, clock, cells, heads = run(program, bodies, [head,1,0,ctx_head])
            if result != ('success','') or clock != 2*head+5*length+2*ctx_head+24:
                raise RuntimeError('independent wrapper equation')
            if heads != [0,1,0,0] or any(cells[0].get(i,6) != 6 for i in range(length)):
                raise RuntimeError('cleanup/head mismatch')
            if cells[1] != {-1:2,0:4,1:5,2:3} or cells[3] != {-1:2,**dict(enumerate(bodies[3]))}:
                raise RuntimeError('spectator/context mutation')
            count += 1
bad, clock, _, _ = run(program, [[3], [], [], [0]], [0,0,0,0])
if bad != ('reject','contiguous binary body') or clock != 4:
    raise RuntimeError('pre-retirement failure boundary')
for symbol in range(7):
    write = compile_primitive((('write',2,symbol),('halt',)), layout)
    bad, clock, _, _ = run(write,[[],[],[],[1]],[0,0,0,0])
    if bad != ('reject','native context is read-only') or clock != 8:
        raise RuntimeError('readonly rejection boundary')
print(f'PASS_LEAD_CONTEXTUAL_PRIMITIVE probes={count+8} no_source_executor_import')
