"""Independent fixed-instruction interpreter and OLD23 zero oracle."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('root_review_zero', P / 'zero.py')
z = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = z
exec(compile((P / 'zero.py').read_bytes(), str(P / 'zero.py'), 'exec'), z.__dict__)
SCHEMA = ('outer','rows','stock','row_bits','within_bits','record_bits','p','d',
          'K','G','H','q0','qF','qB','D','f','rho','active_start','back_start',
          'selected_axes','entry_start','remainder','cutoff')

def need(ok, message):
    if not ok:
        raise ValueError(message)

def execute(code, memory, heads, origins, high, pc=0, cap=18000000):
    steps = 0
    writes = [0] * 43
    while steps < cap:
        op, *a = code[pc]
        steps += 1
        if op == 'H':
            return a[0], steps, writes
        if op == 'J':
            pc = a[0]
            continue
        t = a[0]
        h = heads[t]
        high[t] = max(high[t], h + 1)
        need(h >= origins[t] - 1, 'left boundary crossed')
        if op == 'R':
            pc = a[1].get(memory[t].get(h, 6), -1)
            if pc == -1:
                return 'REJECT', steps, writes
        elif op == 'W':
            need(t not in (0, 1), 'write attempted on OLD/CONTEXT')
            need(h >= origins[t], 'permanent guard write')
            need(a[1] in (0, 1, 2, 3, 4, 6), 'unexpected hardware symbol')
            writes[t] += 1
            if a[1] == 6:
                memory[t].pop(h, None)
            else:
                memory[t][h] = a[1]
            pc += 1
        elif op == 'M':
            need(a[1] in (-1, 1), 'nonunit move')
            heads[t] += a[1]
            high[t] = max(high[t], heads[t] + 1)
            pc += 1
        else:
            raise ValueError('nonliteral opcode')
    raise TimeoutError('independent bounded run exhausted')

def old_header(h):
    result = []
    for name in SCHEMA:
        binary = list(map(int, format(h[name], 'b')))[::-1]
        result += [1] * len(binary) + [0] + binary
    return result

def gamma(values):
    return [int(c) for n in values for c in '0' * (n.bit_length()-1) + format(n, 'b')]

def fixture(a, u, r, width, rows, cutoff, dirty):
    count = rows * (1 << a)
    h = dict.fromkeys(SCHEMA, 0)
    h.update(outer=1, rows=rows, row_bits=(1 << a)*6*r*(width+1),
             within_bits=a, record_bits=6*r*(width+1), f=1, K=1,
             active_start=u, cutoff=cutoff, stock=(1 << 127)+3)
    values = [(j*j+11*j+5) % (1 << width) for j in range(2*r*count)]
    old = []
    for v in values:
        for k in range(width):
            old += [0, 0, (v >> k) & 1]
        old += [0, 1, 0]
    context = old_header(h)
    header = gamma((1, r, rows*(1 << u), 1 << (a-u-9), width, cutoff))
    expected = header + [0] * (count*2*r*width)
    origins = [7+3*(i % 5) for i in range(43)]
    memory = [{o-1:2, o-2:4, o-3:3} for o in origins]
    for t, payload in ((0,old),(1,context)):
        memory[t].update({origins[t]+j:b for j,b in enumerate(payload)})
    if dirty:
        memory[2].update({origins[2]+j:1 for j in range(len(expected))})
        memory[2][origins[2]+len(expected)] = 3
        memory[2][origins[2]+len(expected)+1] = 4
    heads = origins[:]
    heads[2] -= 1
    high = [max(o+1, max(m)+1) for o,m in zip(origins,memory)]
    high[-1] += 5*(len(old)+len(context)+3)
    return memory, heads, origins, high, expected, len(old), len(context)

def check_case(code, labels, args, omit_clear=False):
    memory, heads, origins, high, expected, volume, encoded = fixture(*args)
    before = [dict(m) for m in memory]
    initial_high = high[:]
    status, steps, writes = execute(code,memory,heads,origins,high)
    need(status == 'LIVE_HOME', 'producer rejected legal source')
    actual = [memory[2].get(origins[2]+j,6) for j in range(len(expected)+2)]
    need(actual == expected+[3,4], 'complete independent typed-zero oracle')
    need(memory[0] == before[0] and memory[1] == before[1], 'source/context altered')
    need(writes[0] == writes[1] == 0, 'protected write count')
    for i in range(43):
        need(heads[i] == origins[i]-(i == 2), 'relative return convention')
        need(all(memory[i].get(origins[i]-k) == before[i][origins[i]-k] for k in (1,2,3)), 'opaque exterior')
        if i >= 3:
            need(memory[i] == before[i], 'guide history not erased')
    growth = sum(x-y for x,y in zip(high,initial_high))
    need(growth <= 64*(volume+encoded+3), 'incremental historical capacity')
    need(steps <= (1 << 20)*(volume+encoded+1), 'complete linear bill')
    clear_steps = None
    if not omit_clear:
        for j in range(len(expected)):
            memory[2][origins[2]+j] = 1
        status, clear_steps, _ = execute(code,memory,heads,origins,high,labels['CLEAR'])
        need(status == 'RETIRED_HOME', 'CLEAR return')
        need([memory[2].get(origins[2]+j,6) for j in range(len(expected)+2)] == [0]*len(expected)+[3,4], 'full arbitrary nonzero CLEAR')
        need(heads == [o-(i == 2) for i,o in enumerate(origins)], 'CLEAR heads')
    return {'arguments':list(args), 'V_old':volume, 'E_old':encoded, 'F':len(expected),
            'producer_steps':steps, 'CLEAR_steps':clear_steps, 'history_growth':growth}

def main():
    abstract, labels = z.compile_zero()
    code = z.hardware_code(abstract)
    cases = [check_case(code,labels,(9,0,1,2,1,(1 << 2048)+7,False)),
             check_case(code,labels,(10,1,2,3,2,17,True))]
    damaged = tuple(('J',pc+1) if ins[0]=='W' and ins[1]==2 and ins[2]==0
                    and labels['ZERO_DATA'] <= pc < labels['ZERO_FINISHED'] else ins
                    for pc,ins in enumerate(code))
    try:
        check_case(damaged,labels,(9,0,1,2,1,1,True),True)
    except ValueError as e:
        need(str(e)=='complete independent typed-zero oracle', 'mutation failed at wrong boundary')
    else:
        raise ValueError('dirty target retained DATA mutation survived')
    print(json.dumps({'status':'PASS_INDEPENDENT_OLD_ZERO','zero_sha256':hashlib.sha256((P/'zero.py').read_bytes()).hexdigest(),
                      'locations':len(code),'cases':cases,'missing_DATA_overwrite':'detected'},indent=2))

if __name__ == '__main__':
    main()
