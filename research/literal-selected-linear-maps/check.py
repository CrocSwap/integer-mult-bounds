"""Author checks against direct selected-matrix XOR addresses, not gate words."""
from pathlib import Path
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import linear as m


def require(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    bits = bin(n)[2:]
    return '0'*(len(bits)-1)+bits


def header(shape):
    return ''.join(gamma(n) for n in shape)


def extent(shape):
    f, r, p, s, w = shape
    return 2*w*p*s*r*(1 << (9*f))


def oracle(payload, shape, rows):
    f, r, p, s, w = shape
    q, row_count, block = 1 << f, 1 << (9*f), 2*w*r*s
    require(len(payload) == p*row_count*block, 'oracle complete field')
    out = ['?']*len(payload)
    for source in range(row_count):
        coordinates = [(source >> ((8-i)*f)) & (q-1) for i in range(9)]
        destination = 0
        for row in rows:
            value = 0
            for i in range(9):
                if (row >> i) & 1:
                    value ^= coordinates[i]
            destination = destination*q+value
        for outer in range(p):
            a, b = (outer*row_count+source)*block, (outer*row_count+destination)*block
            out[b:b+block] = payload[a:a+block]
    require('?' not in out, 'oracle matrix permutation')
    return ''.join(out)


def caps(shape):
    v, e = extent(shape), len(header(shape))
    result = [v]*27
    result[m.HEADER] = result[m.HTRACE] = result[m.LENGTH] = e
    result[m.MODE] = 1
    return result


def packet(shape, payload):
    origins = tuple(7*i-71 for i in range(27))
    tapes = []
    for i, (origin, cap) in enumerate(zip(origins, caps(shape))):
        cells = {origin-3:'1', origin-2:'|', origin+cap+1:'0', origin+cap+2:'|'}
        if i < 2:
            cells[origin-1] = '1'
        tapes.append(m.Tape(cells, origin))
    for i, text in ((m.HEADER, header(shape)), (m.DATA, payload)):
        tapes[i].cells.update({origins[i]+j: bit for j, bit in enumerate(text)})
    return tapes, origins


def execute(side, shape, payload, *, code=None, accept=True, edit=None):
    code = m.compile_linear(side)[0] if code is None else code
    tapes, origins = packet(shape, payload)
    if edit:
        edit(tapes, origins)
    before = [dict(t.cells) for t in tapes]
    owners = tuple(map(id, tapes))
    cpu = m.Machine(code, tapes)
    try:
        cpu.run(2_000_000_000)
        rejected = False
    except ValueError as exc:
        require(str(exc) == 'invalid scanned symbol', 'unexpected machine failure: '+str(exc))
        rejected = True
    require(rejected != accept, 'acceptance mismatch')
    require(tuple(map(id, tapes)) == owners, 'owner identity')
    require(tapes[0].cells == before[0], 'header bytes')
    if accept:
        output = oracle(payload, shape, m.MATRICES[side])
        require(tapes[1].cells == before[1] | {origins[1]+j: b for j,b in enumerate(output)}, 'direct address oracle or public exterior')
        require(all(t.head == u for t,u in zip(tapes, origins)), 'head restoration')
        require(all(t.cells == before[i] for i,t in enumerate(tapes) if i != 1), 'private/exterior restoration')
        v, e, f = extent(shape), len(header(shape)), shape[0]
        require(cpu.steps <= 65536*(f*v+e+1), 'complete time envelope')
        require(sum(t.high-t.low+1 for t in tapes[2:]) <= 64*(v+e+1), 'private history envelope')
        for i,(t,o,cap) in enumerate(zip(tapes,origins,caps(shape))):
            require(t.low >= o-int(i>=2) and t.high <= o+cap, 'role visit cap')
    else:
        require(tapes[1].cells == before[1], 'failed call changed public data')
    return cpu.steps


def main():
    rng = random.Random(2026111205)
    results = []
    words = {}
    for side, rows in m.MATRICES.items():
        word = m.cnot_word(rows)
        words[side] = word
        for x in range(512):
            y = x
            for target, control in word:
                y ^= ((y >> control) & 1) << target
            expected = sum(((row & x).bit_count() % 2) << i for i,row in enumerate(rows))
            require(y == expected, 'fixed GF(2) decomposition')
        code, alphabet = m.compile_linear(side)
        require(set(alphabet) == {'_','0','1','|'}, 'fixed alphabet')
        require(all(i[0] in ('read','write','move','goto','halt') for i in code), 'literal instruction language')
        for shape in ((1,1,1,1,1), (1,2,1,1,2), (1,1,2,1,1), (1,1,1,2,1)):
            payload = ''.join(str(rng.randrange(2)) for _ in range(extent(shape)))
            steps = execute(side, shape, payload, code=code)
            results.append({'side':side,'shape':shape,'steps':steps,'kind':'complete m9 f1'})
        shape=(1,1,1,1,1)
        payload='01'*(extent(shape)//2)
        opaque=gamma((1 << 2048)+12345)+'|10'
        def opaque_tail(tapes, origins):
            start=origins[0]+len(header(shape))
            tapes[0].cells.update({start+j:b for j,b in enumerate(opaque)})
        steps=execute(side,shape,payload,code=code,edit=opaque_tail)
        results.append({'side':side,'shape':shape,'steps':steps,'kind':'opaque sixth Gamma code','opaque_bits':len(opaque)})
        for kind,edit in (
            ('short payload', lambda t,u:t[1].cells.pop(u[1]+extent(shape)-1)),
            ('extra payload', lambda t,u:t[1].cells.__setitem__(u[1]+extent(shape),'1')),
            ('bad header', lambda t,u:t[0].cells.__setitem__(u[0],'|'))):
            steps=execute(side,shape,payload,code=code,accept=False,edit=edit)
            results.append({'side':side,'shape':shape,'steps':steps,'kind':kind})
    print(json.dumps({'status':'PASS_LITERAL_SELECTED_LINEAR_BASE','source_sha256':hashlib.sha256((HERE/'linear.py').read_bytes()).hexdigest(),
        'gate_counts':{s:len(w) for s,w in words.items()},'words':words,'seed':2026111205,'cases':results,
        'scope':'Complete actual m9 f1 packets; full f2 and graph mutants are separate receipts.'},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
