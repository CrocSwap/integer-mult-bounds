"""Exact point-column actions and a legal formal/physical norm-shear witness."""
import argparse
from collections import deque
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def sources():
    manifest = read_json(HERE/'SOURCES.json')
    result = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT/row['path']).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(sha == row['sha256'] and blob == row['git_blob'], 'source binding '+row['path'])
        result[row['path']] = sha
    need(len(result) == 2, 'two credited source inputs')
    return result


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            pivot = value.bit_length()-1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def vector(matrix, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(matrix))


def compose(g, h):
    a, b = g
    c, e = h
    matrix = tuple(xor(c[j] for j in range(len(a)) if row >> j & 1) for row in a)
    return matrix, vector(a, e) ^ b


def identity(d):
    return tuple(1 << i for i in range(d)), 0


def generators(d, affine):
    rows, _ = identity(d)
    out = []
    for i in range(d):
        for j in range(d):
            if i != j:
                a = list(rows)
                a[i] ^= 1 << j
                out.append((tuple(a), 0))
    if affine:
        out.extend((rows, 1 << i) for i in range(d))
    return out


def group(d, affine):
    matrices = [rows for rows in product(range(1 << d), repeat=d) if rank(rows) == d]
    elements = [(a, b) for a in matrices for b in range((1 << d) if affine else 1)]
    alphabet = generators(d, affine)
    paths = {identity(d): ()}
    queue = deque(paths)
    while queue:
        g = queue.popleft()
        for i, label in enumerate(alphabet):
            h = compose(label, g)
            if h not in paths:
                paths[h] = paths[g]+(i,)
                queue.append(h)
    need(set(paths) == set(elements), 'coordinate generators exhaust independent invertible-matrix list')
    return elements, alphabet, paths


def act(g, address, d, w):
    a, b = g
    mask = (1 << d)-1
    return sum((vector(a, (address >> (d*j)) & mask) ^ b) << (d*j) for j in range(w))


def gl_order(d):
    out = 1
    for i in range(d):
        out *= (1 << d)-(1 << i)
    return out


def threshold(d, affine):
    if d == 1:
        return int(affine)
    return d+int(affine)


def orbit_census(d, affine, gs):
    out = []
    for w in range(threshold(d, affine)+1):
        unseen = set(range(1 << (d*w)))
        rows = []
        while unseen:
            x = min(unseen)
            images = [act(g,x,d,w) for g in gs]
            orbit = set(images)
            stabilizer = images.count(x)
            columns = [(x >> (d*j)) & ((1 << d)-1) for j in range(w)]
            if affine and not w:
                expected = len(gs)
                span = 0
            else:
                vectors = [v ^ columns[0] for v in columns[1:]] if affine else columns
                span = rank(vectors)
                expected = (1 << (span*(d-span)))*gl_order(d-span)
            need(stabilizer == expected and len(orbit)*stabilizer == len(gs), 'pointwise stabilizer formula')
            norm_output = xor(1 << y for y in images)
            need(norm_output == (0 if stabilizer % 2 == 0 else sum(1 << y for y in orbit)), 'norm action')
            unseen.difference_update(orbit)
            rows.append([len(orbit), stabilizer, span])
        if w < threshold(d, affine):
            need(all(s % 2 == 0 for _,s,_ in rows), 'nonzero norm annihilates every delta below threshold')
        else:
            need(any(s == 1 for _,s,_ in rows), 'regular orbit at threshold')
            columns = ([0] if affine else [])+[1 << j for j in range(d)]
            if d == 1:
                columns = [0] if affine else []
            point = sum(v << (d*j) for j,v in enumerate(columns))
            images = [act(g,point,d,w) for g in gs]
            need(len(set(images)) == len(gs), 'every formal basis coefficient recoverable from one delta')
            coeffs = [int(i % 3 == 1 or i == len(gs)-1) for i in range(len(gs))]
            output = xor(1 << y for y,c in zip(images,coeffs) if c)
            need([(output >> y) & 1 for y in images] == coeffs, 'nonconstant coefficient recovery')
        out.append({'d':d,'affine':affine,'w':w,'group_order':len(gs),'domain':1 << (d*w),'orbits':rows})
    return out


def formal_word(word, gs, alphabet):
    index = {g:i for i,g in enumerate(gs)}
    one = 1 << index[identity(2)]
    entries = [one,0,0,one]
    def left(bits, label):
        return xor(1 << index[compose(label,g)] for i,g in enumerate(gs) if bits >> i & 1)
    for op, k in word:
        if op == 'X':
            entries[0] ^= entries[2]
            entries[1] ^= entries[3]
        else:
            entries[0] = left(entries[0],alphabet[k])
            entries[1] = left(entries[1],alphabet[k])
    return entries


def physical_word(word, alphabet, w, initial):
    n = 1 << (2*w)
    values = initial[:]
    for op, k in word:
        if op == 'X':
            values[0] ^= values[1]
        else:
            values[0] = xor(1 << act(alphabet[k],x,2,w) for x in range(n) if values[0] >> x & 1)
    return values


def legal_witness():
    gs, alphabet, paths = group(2,False)
    word = []
    for g,path in paths.items():
        if g != identity(2):
            word.extend(('D',k) for k in path)
            word.append(('X',None))
            word.extend(('D',k) for k in reversed(path))
            word.append(('X',None))
    one = 1 << gs.index(identity(2))
    target = [one,(1 << len(gs))-1,0,one]
    need(formal_word(word,gs,alphabet) == target, 'complete formal norm shear, including both dirty diagonals')
    paid = sum(op == 'D' for op,_ in word)
    need(paid == 18 and len(word)-paid == 10, 'fully charged address calls and free XORs')
    cases = []
    for w in (1,2):
        n = 1 << (2*w)
        differences = 0
        for column in range(2*n):
            initial = [0,0]
            initial[column//n] = 1 << (column % n)
            actual = physical_word(word,alphabet,w,initial)
            expected = initial[:]
            if initial[1]:
                expected[0] ^= xor(1 << act(g,column % n,2,w) for g in gs)
            need(actual == expected, 'all physical input columns agree with exact formal norm shear')
            differences += actual != initial
        need(differences == (0 if w == 1 else 6), 'width-sensitive legal identity control')
        cases.append({'w':w,'input_columns':2*n,'nonidentity_columns':differences})
    omitted = 0
    for i,(op,_) in enumerate(word):
        if op == 'D':
            need(formal_word(word[:i]+word[i+1:],gs,alphabet) != target, 'omitted paid call must fail formal endpoint')
            omitted += 1
    translation = (identity(2)[0],1)
    need(act(translation,0,2,2) == 5 and act(translation,0,2,2) != 1, 'same affine translation on both point columns')
    need(target[1] != 0 and target[0] == target[3] == one and target[2] == 0, 'clean-only testing is insufficient')
    return {'paid_cnot_calls':paid,'free_scalar_xors':len(word)-paid,'word':word,
            'formal_coefficients':target,'physical_cases':cases,'omitted_paid_call_controls':omitted,
            'affine_same_translation_control':True,'clean_only_control':True}


def calculate(source_pins):
    orbits = []
    for affine in (False,True):
        for d in (1,2,3):
            gs,_,_ = group(d,affine)
            need(len(gs) == gl_order(d)*((1 << d) if affine else 1), 'group order')
            orbits.extend(orbit_census(d,affine,gs))
    return {'schema_version':1,'source_pins':source_pins,'orbit_cases':orbits,'legal_word':legal_witness()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result',type=Path,help='write a new receipt; existing files are refused')
    args = parser.parse_args()
    result = calculate(sources())
    if args.write_result:
        with args.write_result.open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(result,indent=2)+'\n')
    else:
        need(canonical(read_json(HERE/'RESULT.json')) == canonical(result),'typed exact receipt')
    print('PASS_BINARY_STREAM_FAITHFULNESS orbit_cases='+str(len(result['orbit_cases']))+' paid=18 free=10 dirty_columns=40 omitted_controls=18')


if __name__ == '__main__':
    main()
