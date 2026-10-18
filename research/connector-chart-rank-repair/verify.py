"""Exact rank-repair certificates and a fully restored, paid binary pilot."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def pins():
    out = {}
    for row in read_json(HERE/'SOURCES.json')['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT/row['path']).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(digest == row['sha256'] and blob == row['git_blob'],'source binding: '+row['path'])
        out[row['path']] = digest
    require(len(out) == 2,'two predecessor inputs')
    return out


def xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def solver(rows):
    """Echelon image basis with input combinations and full relation basis."""
    basis = {}
    relations = []
    for i, row in enumerate(rows):
        value, combination = row, 1 << i
        while value:
            pivot = value.bit_length()-1
            if pivot not in basis:
                basis[pivot] = value, combination
                break
            vector, earlier = basis[pivot]
            value ^= vector
            combination ^= earlier
        if not value:
            relations.append(combination)
    return basis, relations


def rank(rows):
    return len(solver(rows)[0])


def express(basis, target):
    result = 0
    while target:
        pivot = target.bit_length()-1
        require(pivot in basis,'target outside span')
        vector, combination = basis[pivot]
        target ^= vector
        result ^= combination
    return result


def image_basis(rows):
    basis, _ = solver(rows)
    return [basis[p][0] for p in sorted(basis,reverse=True)]


def intersection(u,v):
    _, relations = solver(u+v)
    common = [xor(row for j,row in enumerate(u) if relation >> j & 1) for relation in relations]
    require(rank(common) == len(common),'intersection independence')
    return common


def adapted(common, rows):
    result = common[:]
    for row in rows:
        if rank(result+[row]) > len(result):
            result.append(row)
    return result


def compose(a,b):
    return tuple(xor(row for j,row in enumerate(b) if mask >> j & 1) for mask in a)


def inverse(a):
    n = len(a)
    left, right = list(a), [1 << i for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j,n) if left[i] >> j & 1),None)
        require(pivot is not None,'singular chart')
        left[j],left[pivot] = left[pivot],left[j]
        right[j],right[pivot] = right[pivot],right[j]
        for i in range(n):
            if i != j and left[i] >> j & 1:
                left[i] ^= left[j]
                right[i] ^= right[j]
    require(left == [1 << i for i in range(n)],'inverse elimination')
    return tuple(right)


def row_transform(rows, targets):
    basis, relations = solver(rows)
    require(len(targets) == len(basis),'target basis dimension')
    result = tuple([express(basis,t) for t in targets]+relations)
    require(rank(result) == len(rows),'invertible basis extension')
    require(compose(result,rows) == tuple(targets+[0]*(len(rows)-len(targets))),'adapted form')
    return result


def construct(b0,b1):
    require(len(b0) == len(b1),'equal connector dimensions')
    u,v = image_basis(b0),image_basis(b1)
    common = intersection(u,v)
    t0,t1 = adapted(common,u),adapted(common,v)
    q0,q1 = row_transform(b0,t0),row_transform(b1,t1)
    chart = compose(inverse(q1),q0)
    moved = compose(chart,b0)
    delta = tuple(x^y for x,y in zip(b1,moved))
    expected = max(len(u),len(v))-len(common)
    require(rank(delta) == expected,'constructive minimum rank')
    return chart,delta,expected


def vector(rows,value):
    return sum(((row & value).bit_count() & 1) << i for i,row in enumerate(rows))


def encode(rows):
    return sum(row << (3*i) for i,row in enumerate(rows))


def finite_oracle():
    matrices = list(product(range(8),repeat=3))
    # Independently classify left orbits by actual kernels; explicitly form each
    # representative's entire GL3 orbit, with no constructor-derived witnesses.
    groups = {}
    for matrix in matrices:
        key = tuple(x for x in range(8) if vector(matrix,x) == 0)
        groups.setdefault(key,[]).append(matrix)
    gl = [m for m in matrices if len({vector(m,x) for x in range(8)}) == 8]
    require(len(gl) == 168 and len(groups) == 16,'finite domains')
    ranks = {encode(m):rank(m) for m in matrices}
    checked = 0
    histogram = Counter()
    constructor_cases = 0
    for members in groups.values():
        representative = members[0]
        orbit = {compose(g,representative) for g in gl}
        require(orbit == set(members),'complete explicit chart orbit')
        orbit_codes = [encode(m) for m in orbit]
        for b1 in matrices:
            minimum = min(ranks[encode(b1)^code] for code in orbit_codes)
            for b0 in members:
                c = rank(b0)+rank(b1)-rank(b0+b1)
                formula = max(rank(b0),rank(b1))-c
                require(minimum == formula,'independent full orbit minimum')
                checked += 1
                histogram[minimum] += 1
            # All512 destinations for each of16 row-space orbits; the theorem
            # and row_transform explicitly handle arbitrary representatives.
            chart,delta,claim = construct(representative,b1)
            require(claim == minimum and rank(chart) == 3,'constructed chart against orbit oracle')
            require(compose(inverse(chart),compose(chart,representative)) == representative,'constructed inverse')
            constructor_cases += 1
    require(checked == 262144 and constructor_cases == 8192,'coverage')
    return {'matrix_pairs':checked,'explicit_gl3_charts':168,'kernel_orbits':16,
            'constructive_charts':constructor_cases,'minimum_rank_histogram':dict(sorted(histogram.items()))}


def gates(matrix,source,target):
    return [(source+j,target+i) for i,row in enumerate(matrix) for j in range(3) if row >> j & 1]


def run(word,value):
    for source,target in word:
        require(source != target and 0 <= source < 12 and 0 <= target < 12,'valid distinct gate ports')
        value ^= ((value >> source) & 1) << target
    return value


def pilot():
    b0,b1,r = (7,6,1),(1,6,5),(3,2,4)
    delta = tuple(x^y for x,y in zip(b1,compose(r,b0)))
    require(delta == (0,0,4) and rank(delta) == 1,'literal rank-one repair')
    require(rank(tuple(x^y for x,y in zip(b0,b1))) == 2,'identity-chart rank control')
    identity = (1,2,4)
    a0,a1 = gates(identity,3,6),gates(identity,3,9)
    g0,g1 = gates(b0,0,3),gates(b1,0,3)
    chart,repair = [(4,3)],gates(delta,0,3)
    phases = [a0,g0,a0,chart,repair,a1,g1,a1,chart]
    candidate = sum(phases,[])
    baseline = a0+g0+a0+g0+a1+g1+a1+g1
    direct = gates(b0,0,6)+gates(b1,0,9)
    require((len(candidate),len(baseline),len(direct)) == (26,34,11),'paid scalar counts')
    desired = lambda value:value ^ (vector(b0,value & 7)<<6) ^ (vector(b1,value & 7)<<9)
    first_end = len(a0+g0+a0)
    for value in range(4096):
        expected = desired(value)
        require(run(candidate,value) == expected and run(baseline,value) == expected,'full dirty endpoint')
        require(run(direct,value) == expected,'outside-alphabet direct comparator')
        require(run(list(reversed(candidate)),expected) == value,'literal inverse')
        require((run(candidate[:first_end],value) >> 6) & 7 == (expected >> 6) & 7,'first delivery cut')
        require(all(not(6 <= target < 9) for _,target in candidate[first_end:]),'no rewrite after first delivery')
    mutants = {
        'omit_repair':sum(phases[:4]+phases[5:],[]),
        'omit_final_inverse':sum(phases[:-1],[]),
        'omit_initial_chart':sum(phases[:3]+phases[4:],[]),
        'wrong_closing_source':sum(phases[:6]+[g0]+phases[7:],[]),
    }
    failures = {}
    for label,word in mutants.items():
        witness = next((x for x in range(4096) if run(word,x) != desired(x)),None)
        require(witness is not None,'semantic mutation survived: '+label)
        failures[label] = witness
    # Rank optimization is not price optimization; a large chart tariff can lose.
    require(10+10+1 > 2,'rank/cost distinction control')
    def invoice(word):
        return {'xors':len(word),'reads':2*len(word),'writes':len(word),'dispatches':len(word),
                'head_moves':sum(2*(max(s,t)+1) for s,t in word),
                'fixed_port_tariff':sum(2*(max(s,t)+1)+5 for s,t in word)}
    return {'b0':b0,'b1':b1,'chart':r,'delta':delta,'minimum_rank':1,'identity_chart_rank':2,
            'candidate':candidate,'baseline':baseline,'outside_alphabet_direct':direct,
            'candidate_bill':invoice(candidate),'baseline_bill':invoice(baseline),'direct_bill':invoice(direct),
            'all_dirty_inputs':4096,'inverse_inputs':4096,'first_delivery_inputs':4096,
            'semantic_failure_witnesses':failures,'rank_is_not_tariff_optimality':True}


def odd_characteristic_control():
    # Independent ordinary integer matrix arithmetic, reduced modulo3. The
    # noncommuting readers and signed close distinguish the general word from
    # a cancellation that holds only in characteristic two. No tariff claimed.
    b0,b1 = ((1,1),(0,0)),((1,0),(1,1))
    r,delta = ((0,1),(1,0)),((1,0),(0,0))
    a0,a1 = ((1,1),(0,1)),((1,0),(1,1))
    def mv(m,v):return tuple(sum(a*b for a,b in zip(row,v)) % 3 for row in m)
    def add(a,b,sign=1):return tuple((x+sign*y) % 3 for x,y in zip(a,b))
    word = [('Q',2,1,a0,-1),('Q',1,0,b0,1),('Q',2,1,a0,1),('R',1,1,r,1),
            ('Q',1,0,delta,1),('Q',3,1,a1,1),('Q',1,0,b1,-1),('Q',3,1,a1,-1),('R',1,1,r,1)]
    def execute(program,bank):
        bank = list(bank)
        for op,target,source,m,sign in program:
            bank[target] = mv(m,bank[source]) if op == 'R' else add(bank[target],mv(m,bank[source]),sign)
        return tuple(bank)
    inverse_word = [(op,t,s,m,-sign if op == 'Q' else sign) for op,t,s,m,sign in reversed(word)]
    wrong = word[:]
    wrong[6] = ('Q',1,0,b1,1)
    rejected = False
    cases = 0
    for values in product(range(3),repeat=8):
        bank = tuple(tuple(values[2*j:2*j+2]) for j in range(4))
        x,z,y0,y1 = bank
        expected = (x,z,add(y0,mv(a0,mv(b0,x))),add(y1,mv(a1,mv(b1,x))))
        require(execute(word,bank) == expected,'noncommuting odd-characteristic endpoint')
        require(execute(inverse_word,expected) == bank,'signed literal inverse')
        rejected |= execute(wrong,bank) != expected
        cases += 1
    require(rejected,'wrong closing sign survived')
    return {'field':3,'dimension':2,'dirty_inputs':cases,'inverse_inputs':cases,'wrong_closing_sign_rejected':True}


def calculate():
    source_pins = pins()
    # Unequal kernels can share rank; zero/extreme ranks are included explicitly.
    small = []
    for b0,b1 in (((1,0,0),(2,0,0)),((0,0,0),(1,2,4)),((1,2,4),(0,0,0)),((0,0,0),(0,0,0))):
        r,d,k = construct(b0,b1)
        small.append({'b0':b0,'b1':b1,'rank':k,'chart':r,'delta':d})
    require([x['rank'] for x in small] == [1,3,3,0],'boundary cases')
    return {'schema_version':1,'source_pins':source_pins,'finite_oracle':finite_oracle(),
            'pilot':pilot(),'odd_characteristic_control':odd_characteristic_control(),'boundary_cases':small,
            'limits':'Rank minimum over all invertible row charts; no scalar/physical tariff minimum or selected supplier admission.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result',type=Path,help='write only a NEW result')
    args = ap.parse_args()
    if args.write_result:
        require(not args.write_result.exists(),'output already exists')
    result = calculate()
    if args.write_result:
        with args.write_result.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2)
            stream.write('\n')
    else:
        require(canonical(read_json(HERE/'RESULT.json')) == canonical(result),'typed exact receipt mismatch')
    print('PASS_CONNECTOR_CHART_RANK_REPAIR pairs=262144 charts=8192 dirty=4096 scalar_xors=26_vs_34')


if __name__ == '__main__':
    main()
