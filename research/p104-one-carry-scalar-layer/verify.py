"""Check complete one-carry P104 circuits and the current-source invoice.

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
    for row in json.loads((P/'ORIGINS.json').read_text()):
        need(sha256((P/row['retained_path']).read_bytes()).hexdigest() == row['sha256'],'retained comparator bytes')
    word = json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    return word,load('scalar',ROOT/'research/rank7-one-carry-scalars/scalars.py'),load('binary',ROOT/'research/rank7-aligned-bit-adders/bitadder.py'),load('readonly',P/'inputs/readonly-lower.py')


def alignment(word):
    n = word['public']+word['owned_fields'];rows = [{i:32} if i<word['public'] else {} for i in range(n)];atom = n;checks = 0;digest = sha256()
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':rows[r] = {atom:32};atom += 1
        elif op in ('INIT','CLEAR'):rows[r] = {}
        else:
            q = Q(e[-2]);s = r if op == 'SCALE' else e[2]
            need(all(q.numerator*v%q.denominator == 0 for v in rows[s].values()),'every source grid alignment')
            term = {k:q.numerator*v//q.denominator for k,v in rows[s].items()};checks += 1
            if op in ('SCALE','COPY'):rows[r] = term
            else:
                for k,v in term.items():
                    z = rows[r].get(k,0)+v
                    if z:rows[r][k] = z
                    else:rows[r].pop(k,None)
        digest.update(canonical([j,r,sorted(rows[r].items())]))
    return dict(scalar_events=checks,sha256=digest.hexdigest(),native_returns=atom-n)


def signed(x,w):return x-(1<<w) if x>>(w-1) else x


def fixture(word,tables,width,seed):
    rng = random.Random(seed);mask = (1<<width)-1
    expected = [[Q(32*rng.randrange(-32,33)) for _ in range(2)] for _ in range(word['public'])]+[[Q(0),Q(0)] for _ in range(word['owned_fields'])]
    banks = [[int(v)&mask for v in pair] for pair in expected];digest = sha256();calls = 0
    for j,e in enumerate(word['program']):
        op,r = e[:2]
        if op == 'MOVE':
            expected[r] = [Q(32*rng.randrange(-32,33)) for _ in range(2)];banks[r] = [int(v)&mask for v in expected[r]]
        elif op in ('INIT','CLEAR'):expected[r] = [Q(0),Q(0)];banks[r] = [0,0]
        else:
            q = Q(e[-2]);gates = tables[op,e[-2]]
            if op == 'SCALE':
                expected[r] = [q*v for v in expected[r]];banks[r] = list(L.apply(gates,*banks[r],width));calls += 1
            else:
                source = banks[e[2]].copy()
                if op == 'COPY':need(banks[r] == [0,0],'zero COPY target')
                for k in range(2):
                    expected[r][k] = q*expected[e[2]][k] if op == 'COPY' else expected[r][k]+q*expected[e[2]][k]
                    banks[r][k],restored = L.apply(gates,banks[r][k],source[k],width);calls += 1
                    need(restored == source[k],'complete ADD source restored')
            need(all(v.denominator == 1 and abs(v)<1<<(width-1) for v in expected[r]),'full fixture exact range')
        need([signed(v,width) for v in banks[r]] == expected[r],'complete Gaussian scalar trace')
        digest.update(canonical([j,r,banks[r]]))
    need(all(pair == [0,0] for pair in banks[word['public']:]),'all owned exits reset')
    return dict(events=len(word['program']),circuit_calls=calls,sha256=digest.hexdigest())


def packed_cases(scalar,width,gates,cases,expected):
    wires = [sum(((a>>i)&1)<<j for j,(a,b) in enumerate(cases)) for i in range(width)]
    wires += [sum(((b>>i)&1)<<j for j,(a,b) in enumerate(cases)) for i in range(width)]+[0]
    after = scalar.apply(width,gates,wires)
    for k in range(2*width):
        target = sum(((pair[k//width]>>(k%width))&1)<<j for j,pair in enumerate(expected))
        need(after[k] == target,'all packed truth columns')
    need(after[-1] == 0 and scalar.apply(width,list(reversed(gates)),after) == wires,'all literal inverses and carry return')
    return len(cases)


def verify(write=False):
    word,S,B,R = inputs();grid = alignment(word);keys = sorted({(e[0],e[-2]) for e in word['program'] if e[0] in ('ADD','SCALE','COPY')})
    reports = {};fixtures = [];artifact = None
    for width in (26,27,32,36,64,127,256):
        tables = {key:L.circuit(width,*key,S,B,R) for key in keys};old = {key:R.circuit(width,*key,B) for key in keys}
        current = Counter();baseline = Counter()
        for e in word['program']:
            if e[0] in ('ADD','SCALE','COPY'):
                factor = 1 if e[0] == 'SCALE' else 2
                for g in tables[e[0],e[-2]]:current['cx' if len(g) == 2 else 'ccx'] += factor
                for g in old[e[0],e[-2]]:baseline[g[0]] += 2
            elif e[0] in ('INIT','CLEAR'):current['reset'] += 2*width;baseline['reset'] += 2*width
        need(sum(current.values()) < sum(baseline.values()),'complete gate improvement')
        reports[str(width)] = dict(one_carry=dict(current),readonly=dict(baseline),gate_saving=sum(baseline.values())-sum(current.values()),clean_carry_bits=1,old_clean_carry_bits=width-1)
        if width in (26,64):fixtures.append(fixture(word,tables,width,3159+width))
        if width == 64:artifact = [[op,q,gates] for (op,q),gates in tables.items()]
    raw = canonical(artifact)
    if write:(P/'CIRCUITS64.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    else:need(gzip.decompress((P/'CIRCUITS64.json.gz').read_bytes()) == raw,'complete circuit artifact')
    exhaustive = 0
    for width in (5,6):
        mask = (1<<width)-1;limit = 1<<(width-1)
        for op,coefficient in keys:
            q = Q(coefficient);gates = L.circuit(width,op,coefficient,S,B,R)
            if op == 'ADD':
                cases = [(t&mask,s&mask) for s in range(-limit,limit) if s%q.denominator == 0 for t in range(-limit,limit)]
                expected = [((signed(t,width)+int(q*signed(s,width)))&mask,s) for t,s in cases]
            elif op == 'SCALE':
                values = [v for v in range(-limit+1,limit) if v%q.denominator == 0 and abs(q*v)<limit]
                cases = [(r&mask,i&mask) for r in values for i in values]
                expected = [(int(q*signed(r,width))&mask,int(q*signed(i,width))&mask) for r,i in cases]
            else:cases = [(0,s) for s in range(mask+1)];expected = [(s,s) for _,s in cases]
            exhaustive += packed_cases(S,width,gates,cases,expected)
    controls = 0
    gates = L.circuit(26,'ADD','1/2',S,B,R)
    wrong = list(gates);wrong.pop()
    try:
        t,s = L.apply(wrong,7,(-6)&((1<<26)-1),26)
        need(s == ((-6)&((1<<26)-1)) and signed(t,26) == 4,'missing source cleanup')
    except ValueError:controls += 1
    gates = L.circuit(26,'SCALE','-1',S,B,R)
    try:
        pair = L.apply(gates[:-1],3,5,26);need(pair == (((-3)&((1<<26)-1)),((-5)&((1<<26)-1))),'missing paired gate')
    except ValueError:controls += 1
    try:S.execute(26,S.shifted(26,0),1,2,carry=1)
    except ValueError:controls += 1
    need(controls == 3,'all rejection controls')
    return dict(status='PASS_P104_ONE_CARRY_SCALAR_LAYER',alignment=grid,widths=reports,full_fixtures=fixtures,
                exhaustive_truth_columns=exhaustive,negative_controls=controls,circuits_sha256=sha256(raw).hexdigest(),
                contract='Exclusive temporary source writes; paired Gaussian SCALE; native and reset primitives remain open')


if __name__ == '__main__':
    need(sys.argv[1:] in ([],['--write']),'supported arguments')
    result = verify(sys.argv[1:] == ['--write'])
    if sys.argv[1:] == ['--write']:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result == json.loads((P/'RESULT.json').read_text()),'complete receipt')
    print(result['status'])
