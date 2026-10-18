#!/usr/bin/env python3
"""Faithful regular-operator check, with no import of primary mathematics.
Apache-2.0. Ross Richardson with substantial OpenAI Codex assistance.
"""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Failure(ValueError):
    pass


def require(condition, why):
    if not condition:
        raise Failure(why)


def load(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate key')
            out[key] = value
        return out
    def invalid(value):
        raise Failure('nonfinite value')
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def hash_value(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def action(m, x):
    return ((m[0]*x[0]+m[1]*x[1]) % 2, (m[2]*x[0]+m[3]*x[1]) % 2)


def composition(m, n):
    col0, col1 = action(m, (n[0], n[2])), action(m, (n[1], n[3]))
    return col0[0], col1[0], col0[1], col1[1]


VECTORS = tuple(itertools.product((0, 1), repeat=2))
GROUP = sorted((m for m in itertools.product((0, 1), repeat=4)
                if len({action(m, x) for x in VECTORS}) == 4),
               key=lambda m: sum(x << i for i, x in enumerate(m)))
IDENTITY = (1, 0, 0, 1)
LABELS = {'a': (1, 1, 0, 1), 'b': (1, 0, 1, 1)}
SWAP = (0, 1, 1, 0)
ID_COLUMN = GROUP.index(IDENTITY)


def bm(x, y):
    result = []
    for row in x:
        value = 0
        while row:
            bit = row & -row
            value ^= y[bit.bit_length()-1]
            row -= bit
        result.append(value)
    return result


def eye(n):
    return [1 << i for i in range(n)]


def regular(g):
    result = [0] * 6
    for j, h in enumerate(GROUP):
        result[GROUP.index(composition(g, h))] |= 1 << j
    return result


def target(r, t):
    rows = [0] * (6*r)
    for i in range(r):
        block = regular(SWAP if i < t else IDENTITY)
        for j in range(6):
            rows[6*i+j] = block[j] << (6*i)
    return rows


def scalar_projectors(r):
    out = []
    for image in range(1, 2**r):
        for coimage in range(1, 2**r):
            matrix = [coimage if (image >> i) & 1 else 0 for i in range(r)]
            # Rank one follows because all nonzero rows equal one nonzero row.
            if bm(matrix, matrix) == matrix:
                out.append((image, coimage))
    return out


def operator(call, r):
    require(type(r) is int and 1 <= r <= 6, 'roles')
    require(type(call) is list and len(call) == 3, 'call shape')
    label, image, coimage = call
    require(type(label) is str and label in LABELS, 'label domain')
    require(type(image) is int and type(coimage) is int and 0 < image < 2**r and 0 < coimage < 2**r, 'vectors')
    scalar = [coimage if image & (1 << i) else 0 for i in range(r)]
    require(bm(scalar, scalar) == scalar, 'idempotent')
    delta = [x ^ y for x, y in zip(regular(LABELS[label]), eye(6))]
    result = eye(6*r)
    for i in range(r):
        if image & (1 << i):
            for j in range(r):
                if coimage & (1 << j):
                    for k in range(6):
                        result[6*i+k] ^= delta[k] << (6*j)
    return result


def replay(word, r):
    require(type(word) is list, 'word type')
    result = eye(6*r)
    for call in word:
        result = bm(operator(call, r), result)
    return result


def coefficients(operator_rows, r):
    # Faithfulness: applying a group-algebra block to [identity] reads its coefficients.
    return [[sum(((operator_rows[6*i+k] >> (6*j+ID_COLUMN)) & 1) << k for k in range(6))
             for j in range(r)] for i in range(r)]


def screen():
    rows = []
    patterns = 0
    for t in range(1, 7):
        for q in range(min(3*t, 17)):
            if q % 2 != t % 2:
                continue
            f = s = c = 0
            for labels in itertools.product('ab', repeat=q):
                patterns += 1
                a, b = labels.count('a'), labels.count('b')
                if a < t or b < t:
                    continue
                f += 1
                if a == t or b == t:
                    continue
                s += 1
                # Rebuild every transformed word, instead of using the walk formula.
                allowed = True
                for k in range(q+1):
                    moved = labels[k:] + tuple('b' if g == 'a' else 'a' for g in labels[:k])
                    if moved.count('a') <= t or moved.count('b') <= t:
                        allowed = False
                        break
                c += allowed
            rows.append({'targets':t,'calls':q,'floor':f,'after_saturation':s,'after_cuts':c})
    return {'patterns':patterns,'rows':rows}


def verify():
    receipt = load(HERE / 'RESULT.json')
    require(canonical(receipt['claim']) == canonical({'targets':4,'roles':4,'minimum':12,'extra_dirty_roles':0,'no_new_kappa':True}), 'claim boundary')
    for source in load(HERE / 'PINS.json')['files']:
        require(hashlib.sha256((HERE / source['local_path']).read_bytes()).hexdigest() == source['sha256'], 'source pin')
    classes = []
    for r in range(1, 7):
        transform = target(r, r)
        projectors = scalar_projectors(r)
        values = []
        for u, v in projectors:
            for label in ('a', 'b'):
                op = operator([label, u, v], r)
                conjugated = bm(bm(transform, op), transform)
                require(conjugated == operator(['b' if label == 'a' else 'a', u, v], r), 'conjugation')
                require(bm(op, op) == eye(6*r), 'involution')
                values.append(coefficients(conjugated, r))
        classes.append({'roles':r,'projectors':len(projectors),'checks':len(values),'sha256':hash_value(values)})
    require(canonical(classes) == canonical(receipt['conjugations']), 'conjugation receipt')
    require(len(receipt['fixtures']) == 24, 'positive fixture coverage')
    cuts = omissions = 0
    all_rotated = []
    for fixture in receipt['fixtures']:
        r, word = fixture['roles'], fixture['word']
        require(replay(word,r) == target(r,r), 'full positive operator')
        for k in range(len(word)+1):
            rotated = [x[:] for x in word[k:]] + [['b' if x[0]=='a' else 'a',x[1],x[2]] for x in word[:k]]
            require(replay(rotated,r) == target(r,r), 'full rotated operator')
            all_rotated.append(rotated)
            cuts += 1
        for k in range(len(word)):
            require(replay(word[:k]+word[k+1:],r) != target(r,r), 'omission')
            omissions += 1
    require(type(receipt['cut_checks']) is int and cuts == receipt['cut_checks'], 'cut count')
    require(type(receipt['omission_controls']) is int and omissions == receipt['omission_controls'], 'omission count')
    require(hash_value(all_rotated) == receipt['rotations_sha256'], 'rotation hash')
    require(canonical(screen()) == canonical(receipt['label_screen']), 'label screen')
    r,t,call = 5,4,['a',17,1]
    conjugated = bm(bm(target(r,t),operator(call,r)),target(r,t))
    alphabet = [operator([g,u,v],r) for u,v in scalar_projectors(r) for g in ('a','b')]
    require(conjugated not in alphabet, 'workspace boundary')
    expect = {'roles':r,'targets':t,'call':call,'conjugate':coefficients(conjugated,r),'alphabet_size':len(alphabet)}
    require(canonical(expect) == canonical(receipt['workspace_boundary']), 'boundary receipt')
    # Direct operator corruption: one changed output bit must not be hidden by coefficient projection.
    bad = target(4,4)
    bad[0] ^= 1
    require(bad != replay([['a',1,1],['b',1,1],['a',1,1]] + [[g,1<<i,1<<i] for i in range(1,4) for g in 'aba'],4), 'operator bit corruption')
    return {'conjugations':sum(x['checks'] for x in classes),'cuts':cuts,'omissions':omissions,
            'patterns':receipt['label_screen']['patterns'],'boundary_alphabet':len(alphabet)}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
    print('PASS_INDEPENDENT_FULL_OCCUPANCY minimum=12 no_new_kappa')
