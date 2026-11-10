#!/usr/bin/env python3
"""Exact arithmetic for the written theorem; no predecessor code is imported.

The published table's group identification is a cited input, not proved by
orthogonality. Prepared for alephnan with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORDER, SP_ORDER = 92897280, 1451520


def need(ok, message):
    if not ok:
        raise ValueError(message)


def quotient(data):
    a = data['characters']
    need(len(a) == 67 and all(len(r) == 67 for r in a), 'table dimensions')
    need(all(type(x) is int for r in a for x in r), 'integer entries')
    need(data['order'] == ORDER and a[0] == [1]*67, 'order and trivial character')
    need(data['adjoint_character_rows'] == [1,10] and data['pauli_nonidentity_class'] == 2,
         'published representation identification')
    need(all(r[0] > 0 for r in a) and sum(r[0]**2 for r in a) == ORDER, 'degrees')
    centralizers = [sum(r[j]**2 for r in a) for j in range(67)]
    need(all(ORDER % c == 0 for c in centralizers), 'integral class sizes')
    sizes = [ORDER//c for c in centralizers]
    need(sum(sizes) == ORDER and sizes[:2] == [1,63], 'class inventory')
    orthogonal(a, sizes, ORDER)
    inf = [i for i,r in enumerate(a) if r[0] == r[1]]
    buckets = {}
    for j in range(67):
        buckets.setdefault(tuple(a[i][j] for i in inf), []).append(j)
    need(len(inf) == len(buckets) == 30, 'quotient dimensions')
    chars = [[key[i] for key in buckets] for i in range(30)]
    ad = [1+x for x in a[9]]
    need(all(x == 0 or (x > 0 and x & (x-1) == 0) for x in ad), 'trace alphabet')
    qs, dims = [], []
    for js in buckets.values():
        mass = sum(sizes[j] for j in js)
        need(mass % 64 == 0, 'quotient class mass')
        qs.append(mass//64)
        nz = {ad[j] for j in js if ad[j]}
        need(len(nz) == 1, 'one fixed dimension per class')
        x = nz.pop()
        need(x*sum(sizes[j] for j in js if ad[j]) == mass, 'Pauli-coset averaging law')
        dims.append(x.bit_length()-1)
    need(sum(qs) == SP_ORDER and all(0 <= d <= 6 for d in dims), 'symplectic inventory')
    orthogonal(chars, qs, SP_ORDER)
    trans = [j for j,(s,d) in enumerate(zip(qs,dims)) if s == 63 and d == 5]
    need(len(trans) == 1, 'transvection class')
    return dict(chars=chars, sizes=qs, dims=dims, trans=trans[0],
                rows=[i+1 for i in inf], classes=[[j+1 for j in js] for js in buckets.values()])


def orthogonal(chars, sizes, order):
    for i in range(len(chars)):
        for j in range(i+1):
            need(sum(s*x*y for s,x,y in zip(sizes,chars[i],chars[j]))
                 == (order if i == j else 0), 'character orthogonality')


def multiplicities(q, f, phase=True, average=True):
    need(f > 0 and f % 2 == 1, 'positive odd width')
    if f % 4 == 1:
        t = (f-1)//4
        exponent, sign = 2*t, t
    else:
        t = (f-3)//4
        exponent, sign = 2*t+1, t+1
    if not average:
        exponent += 1
    values = [(-1)**(sign*d if phase else 0)*2**(exponent*d) for d in q['dims']]
    ms = [F(sum(s*x*y for s,x,y in zip(q['sizes'],values,r)),SP_ORDER) for r in q['chars']]
    need(all(m.denominator == 1 and m >= 0 for m in ms), 'tensor multiplicities')
    need(sum(m*r[0] for m,r in zip(ms,q['chars'])) == 8**(f-1), 'tensor dimension')
    return [int(m) for m in ms]


def nine(q, ms):
    missing = [i for i,m in enumerate(ms) if m == 0]
    need(len(missing) == 1, 'sole missing constituent')
    i = missing[0]
    need(q['rows'][i] == 2 and q['chars'][i][0] == 7, 'degree-seven defect')
    need(q['chars'][i][q['trans']] == -5, 'transvection trace minus five')
    ratios = [F(m,r[0]) for m,r in zip(ms,q['chars']) if m]
    need(min(ratios) == F(1,2) and max(ratios) == 269, 'multiplicity ratios')
    rank = sum((8*r[0])**2 for m,r in zip(ms,q['chars']) if m)
    need(rank == ORDER-56**2, 'width-nine nullity')
    return i,rank


def quadratic_counts():
    par = lambda x: x.bit_count() % 2
    forms = [(a,b,par(a&b)) for a in range(8) for b in range(8)]
    ns = [sum(e == t for _,_,e in forms) for t in range(2)]
    need(ns == [36,28], 'Arf orbit sizes')
    for v in range(1,64):
        x,z = v&7,v>>3
        counts = [0,0]
        for a,b,e in forms:
            if par(x&z) ^ par(a&x) ^ par(b&z):
                counts[e] += 1
        need(counts == [16,16], 'sixteen fixed forms in each orbit')
    return ns


def constants(ns, fixed=16):
    need(ns == [36,28], 'both Pauli orbits')
    remaining = [F(5*n-7*fixed,12*n) for n in ns]
    need(min(remaining) == F(1,12), 'strict completion margin')
    lo,hi = F(ORDER,24*8**10),F(269*ORDER,8**10)
    need(lo == F(945,262144) and hi == F(762615,32768), 'spectral bounds')
    need(hi/lo == 6456, 'condition bound')
    return list(map(str,remaining)),str(lo),str(hi)


def reject(fn, name):
    try:
        fn()
    except (ValueError,KeyError,TypeError,IndexError):
        return name
    raise ValueError('surviving negative control: '+name)


def main():
    source = json.loads((HERE/'SOURCES.json').read_text(encoding='utf8'))
    pins = 0
    for item in source['files']:
        if item['usage'] == 'input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'source pin')
            pins += 1
    ext = json.loads((HERE/'EXTERNAL.json').read_text(encoding='utf8'))
    need(sha256((HERE/'table.json').read_bytes()).hexdigest() == ext['table_sha256'], 'table pin')
    data = json.loads((HERE/'table.json').read_text(encoding='utf8'))
    q = quotient(data)
    ms = {str(f):multiplicities(q,f) for f in [1,3,5,7,9,11,13]}
    idx,rank = nine(q,ms['9'])
    ns = quadratic_counts()
    rem,lo,hi = constants(ns)
    ranks = {f:sum((8*r[0])**2 for m,r in zip(mm,q['chars']) if m) for f,mm in ms.items()}
    need(list(ranks.values()) == [64,45760,8961920,77913472,92894144,ORDER,ORDER], 'rank fixtures')
    bad = deepcopy(data)
    bad['characters'][1][2] += 1
    wrong = deepcopy(data)
    wrong['adjoint_character_rows'] = [1,11]
    fake = ms['9'][:]
    fake[idx] = 1
    controls = [
        reject(lambda:quotient(bad),'changed table cell'),
        reject(lambda:quotient(wrong),'wrong adjoint identification'),
        reject(lambda:need(multiplicities(q,5,phase=False) == ms['5'], 'width-five phase fixture'),
               'discarded native fourth-power sign'),
        reject(lambda:multiplicities(q,9,average=False),'omitted Pauli average'),
        reject(lambda:nine(q,fake),'false width-nine independence'),
        reject(lambda:constants(ns,fixed=20),'overfunded transvection trace'),
        reject(lambda:constants([36]),'omitted odd-Arf orbit'),
        reject(lambda:multiplicities(q,10),'even width through odd-sector formula')]
    print(json.dumps(dict(status='PASS_THREE_QUBIT_CLIFFORD_THRESHOLD_TEN',
        source_pins=pins, projective_order=ORDER, symplectic_order=SP_ORDER,
        quotient_source_rows=q['rows'], quotient_source_classes=q['classes'],
        quotient_class_sizes=q['sizes'], fixed_dimensions=q['dims'],
        transvection_column_one_based=q['trans']+1,
        odd_tensor_multiplicities=ms, odd_tensor_ranks=ranks,
        width_nine_nullity=ORDER-rank, sharp_threshold=10,
        quadratic_orbit_sizes=ns, transvection_fixtures=63,
        remaining_degree_fractions=rem, uniform_spectral_bounds_from_ten=[lo,hi],
        uniform_condition_upper_bound=6456, negative_controls=controls,
        scope='Exact arithmetic supporting PROOF.md; the published character identification is a cited input, not reconstructed.'), indent=2))


if __name__ == '__main__':
    main()
