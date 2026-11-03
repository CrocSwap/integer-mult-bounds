"""Bind every selected scalar event to a literal Boolean implementation.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def load(name,path):
    s = importlib.util.spec_from_file_location(name,path);m = importlib.util.module_from_spec(s);s.loader.exec_module(m)
    return m


L = load('lower',P/'lower.py');need = L.need


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def inputs():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],'source hash')
    word = json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    return word,load('adder',ROOT/'research/rank7-aligned-bit-adders/bitadder.py')


def alignment(word):
    n = word['public']+word['owned_fields'];rows = [{i:32} if i<word['public'] else {} for i in range(n)];atom = n
    checks = 0;digest = sha256()
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':rows[r] = {atom:32};atom += 1
        elif op in ('INIT','CLEAR'):rows[r] = {}
        else:
            q = Q(e[-2]);s = r if op == 'SCALE' else e[2]
            need(all((q.numerator*v)%q.denominator == 0 for v in rows[s].values()),'all-atom source alignment')
            term = {k:q.numerator*v//q.denominator for k,v in rows[s].items()};checks += 1
            if op in ('SCALE','COPY'):rows[r] = term
            else:
                for k,v in term.items():
                    z = rows[r].get(k,0)+v
                    if z:rows[r][k] = z
                    else:rows[r].pop(k,None)
        digest.update(canonical([j,r,sorted(rows[r].items())]))
    return dict(scalar_events=checks,prefix_sha256=digest.hexdigest(),native_returns=atom-n)


def signed(value,width):
    return value-(1 << width) if value >> (width-1) else value


def templates(word,width,adder,policy=True):
    keys = sorted({(e[0],e[-2]) for e in word['program'] if e[0] in ('ADD','SCALE','COPY')})
    return {key:L.circuit(width,*key,adder,signed=policy) for key in keys}


def gate_bill(word,tables,width):
    counts = Counter()
    for e in word['program']:
        if e[0] in ('ADD','SCALE','COPY'):counts.update(g[0] for g in tables[e[0],e[-2]])
        elif e[0] in ('INIT','CLEAR'):counts['reset'] += width
    return dict(counts)


def fixture(word,tables,width,seed):
    rng = random.Random(seed);mask = (1 << width)-1;n = word['public']+word['owned_fields']
    expected = [Q(32*rng.randrange(-32,33)) for _ in range(word['public'])]+[Q(0)]*word['owned_fields']
    banks = [int(x)&mask for x in expected];digest = sha256();events = 0
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':expected[r] = Q(32*rng.randrange(-32,33));banks[r] = int(expected[r])&mask
        elif op in ('INIT','CLEAR'):expected[r] = Q(0);banks[r] = 0
        else:
            q = Q(e[-2]);src = 0 if op == 'SCALE' else banks[e[2]]
            if op == 'SCALE':expected[r] *= q
            elif op == 'COPY':
                need(banks[r] == 0,'clean owned COPY destination');expected[r] = q*expected[e[2]]
            else:expected[r] += q*expected[e[2]]
            need(expected[r].denominator == 1 and abs(expected[r]) < 1 << (width-1),'fixture exact range')
            banks[r],carry = L.apply(tables[op,e[-2]],src,banks[r],width)
            need(carry == 0,'all shared carry bits returned')
        need(signed(banks[r],width) == expected[r],'literal scalar trace')
        digest.update(canonical([j,r,banks[r]]));events += 1
    need(all(v == 0 for v in banks[word['public']:]),'owned fields reset')
    return dict(events=events,sha256=digest.hexdigest())


def verify(write=False):
    word,adder = inputs();grid = alignment(word);reports = {};fixtures = [];artifacts = None
    for width in (26,27,32,36,64,127,256):
        tables = templates(word,width,adder);control = templates(word,width,adder,False)
        reports[str(width)] = dict(signed=gate_bill(word,tables,width),binary_control=gate_bill(word,control,width),clean_carry_bits=width-1,constant_backing_bits=0)
        # Extremal signed values and aligned values exercise every actual template.
        checks = 0;mask = (1 << width)-1
        for (op,coefficient),gates in tables.items():
            q = Q(coefficient)
            for value in (-32,-16,-1,0,1,16,32):
                source = value*q.denominator;target = 19 if op == 'ADD' else 0
                if op == 'SCALE':target = source;source = 0;expected = q*target
                else:expected = target+q*source
                got,carry = L.apply(gates,source&mask,target&mask,width)
                need(signed(got,width) == expected and carry == 0,'scalar template and carry cleanup');checks += 1
        reports[str(width)]['template_cases'] = checks
        if width in (26,64):fixtures.append(fixture(word,tables,width,6030+width))
        if width == 64:artifacts = [[op,q,gates] for (op,q),gates in tables.items()]
    raw = canonical(artifacts)
    if write:(P/'CIRCUITS64.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    else:need(gzip.decompress((P/'CIRCUITS64.json.gz').read_bytes()) == raw,'complete serialized circuits')
    # Independent bit-list interpretation checks every gate type and SCALE family.
    checks = 0
    for q in sorted({e[-2] for e in word['program'] if e[0] == 'SCALE'}):
        gates = L.circuit(26,'SCALE',q,adder)
        for v in range(-32,33):
            value = v*Q(q).denominator;bits = {('t',i):(value>>i)&1 for i in range(26)}
            bits.update({('c',i):0 for i in range(25)})
            for g in gates:
                toggle = all(bits[w] for w in g[1:-1]);bits[g[-1]] ^= int(toggle)
            observed = signed(sum(bits['t',i]<<i for i in range(26)),26)
            need(observed == Q(q)*value and not any(bits['c',i] for i in range(25)),'independent SCALE bits');checks += 1
    gates = L.circuit(26,'SCALE','2',adder)
    wrong,_ = L.apply(gates[:-1],0,(-3)&((1<<26)-1),26)
    need(signed(wrong,26) != -6,'missing sign-fill gate rejected')
    gates = L.circuit(26,'SCALE','-1',adder)
    wrong,carry = L.apply(gates[:-1],0,3,26)
    need(signed(wrong,26) != -3 or carry,'missing increment gate rejected')
    gates = L.circuit(26,'ADD','1/2',adder)
    wrong,_ = L.apply(gates,1,0,26)
    need(Q(signed(wrong,26)) != Q(1,2),'unaligned domain control')
    return dict(status='PASS_P104_BOOLEAN_SCALAR_LAYER',alignment=grid,word_events=len(word['program']),
                widths=reports,full_fixtures=fixtures,independent_scale_cases=checks,semantic_controls=3,
                serialized_circuits_sha256=sha256(raw).hexdigest(),native_implementation='not supplied',reset_primitive='charged, not lowered')


if __name__ == '__main__':
    need(sys.argv[1:] in ([],['--write']),'supported arguments')
    result = verify(sys.argv[1:] == ['--write'])
    if sys.argv[1:] == ['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result == json.loads((P/'RESULT.json').read_text()),'complete receipt')
    print(result['status'])
