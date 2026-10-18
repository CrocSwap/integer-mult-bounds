#!/usr/bin/env python3
"""Exact bounded replay; finite evidence, not a full multiplication proof."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

p = load('program')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + '\n'


def symbolic(word, count):
    state = [{((), i): 1} for i in range(count)]
    for sign, f, source, target in word:
        require(sign in (-1, 1) and 0 <= source < count and 0 <= target < count and source != target,
                'invalid operation')
        for (w, row), c in list(state[source].items()):
            term = ((f,) + w, row)
            state[target][term] = state[target].get(term, 0) + sign * c
            if not state[target][term]:
                del state[target][term]
    return state


def expected(m, k, rows, factors):
    state = [{((), i): 1} for i in range(rows)]
    for i in range(k):
        for j in range(m):
            w = tuple(reversed(factors[f'A{i}'])) + tuple(reversed(factors[f'B{j}']))
            state[m+i][(w, j)] = 1
    return state


def check_query_alphabet(word, m, k):
    for sign, f, src, dst in word:
        require(sign in (-1, 1), 'non-unit coefficient')
        require(m <= dst < m+k, 'query writes protected source')
        if f.startswith('B'):
            j = int(f[1:])
            require(0 <= j < m and src == j, 'B source mismatch')
        elif f.startswith('A'):
            i = int(f[1:])
            require(0 <= i < k and dst == m+i and m <= src < m+k and src != dst,
                    'A query port mismatch')
        else:
            raise ValueError('unknown query operator')


def check_child_ownership(block, source, target, pool):
    allowed = {source, target, *pool}
    require(all(op[2] in allowed and op[3] in allowed for op in block), 'child ownership')


def check_case(m, k, lengths):
    factors = {f: [f'{f}.{i}' for i in range(n)] for f, n in lengths.items()}
    names = sorted(x for fs in factors.values() for x in fs)
    pool_size = max(p.scratch(n) for n in lengths.values())
    result = {}
    for kind, queries in p.schedules(m, k).items():
        base = m + k + int(kind == 'dedicated')
        pool = list(range(base, base + pool_size))
        rows = base + pool_size
        if kind != 'dedicated':
            check_query_alphabet(queries, m, k)
        require(symbolic(queries, base) == expected(m, k, base, {f:[f] for f in factors}),
                'query identity')
        word, boundaries = p.expand(queries, factors, pool)
        require(all(op[3] >= m for op in word), 'source immutability')
        for start, end, sign, f, source, target in boundaries:
            block = word[start:end]
            check_child_ownership(block, source, target, pool)
            want = [{((), i): 1} for i in range(rows)]
            want[target][(tuple(reversed(factors[f])), source)] = sign
            require(symbolic(block, rows) == want, 'complete child boundary')
        want = expected(m, k, rows, factors)
        require(symbolic(word, rows) == want, 'expanded identity')
        require(symbolic(word + p.inverse(word), rows) == [{((),i):1} for i in range(rows)],
                'literal inverse')
        require(len(word) == sum(p.leaf_count(lengths[f]) for _,f,_,_ in queries), 'leaf recurrence')
        multiplicity = Counter(f for _,f,_,_ in queries)
        if kind == 'borrowed':
            require(all(multiplicity[f'B{j}'] == 4 for j in range(m)), 'B count')
            require(all(multiplicity[f'A{i}'] == 2 for i in range(k)), 'A count')
        result[kind] = {'queries':queries, 'word':word, 'boundaries':boundaries,
                        'rows':rows, 'extra_dirty_rows':rows-m-k,
                        'query_multiplicity':dict(sorted(multiplicity.items())),
                        'leaf_multiplicity':p.multiplicities(word),
                        'invoice_L3':p.invoice(word, rows, names, 3)}
    return factors, result


def negative_controls():
    m, k = 3, 4
    queries = p.schedules(m,k)['borrowed']
    want = expected(m,k,m+k,{f:[f] for f in [*(f'B{j}' for j in range(m)),*(f'A{i}' for i in range(k))]})
    controls = {}
    mutants = {
        'omit_last_source_restore': queries[:-1],
        'reverse_one_sign': [(-q[0],*q[1:]) if i==0 else q for i,q in enumerate(queries)],
        'wrong_source_column': [(s,f,1 if f=='B0' else a,b) for s,f,a,b in queries],
        'wrong_left_operator': [(s,'A0' if f=='A1' else f,a,b) for s,f,a,b in queries],
        'omit_pivot_completion': queries[:2*(k-1)+2*m],
        'swap_noncommuting_order': [queries[6], *queries[1:6], queries[0], *queries[7:]],
    }
    for name, word in mutants.items():
        require(symbolic(word,m+k) != want, 'undetected '+name)
        controls[name] = 'rejected'
    for name, thunk in {
        'source_write':lambda:check_query_alphabet([(1,'B0',0,1)],m,k),
        'self_query':lambda:check_query_alphabet([(1,'A0',m,m)],m,k),
        'nonunit_query':lambda:check_query_alphabet([(2,'B0',0,m)],m,k),
        'aliased_child_port':lambda:p.product(['u','v'],m,m+1,[m]),
        'borrow_unrelated_output_as_child_scratch':lambda:check_child_ownership(
            [(1,'u',m,m+2)],m,m+1,[m+k]),
        'insufficient_child_scratch':lambda:p.product(['u','v','w'],m,m+1,[m+k]),
    }.items():
        try:
            thunk()
        except ValueError:
            controls[name]='rejected'
        else:
            raise ValueError('undetected '+name)
    # Deterministic invertibility does not imply dirty-independent linearity.
    def rounded(dirt):
        st=[1,0,dirt]
        for sign,f,src,dst in p.schedules(1,2)['borrowed']:
            v=st[src]//2 if f=='A0' else st[src]
            st[dst] += sign*v
        return st
    require(rounded(0)[1] != rounded(1)[1], 'nonlinear boundary not exposed')
    controls['nonlinear_dirty_dependence']={'dirt0':rounded(0),'dirt1':rounded(1)}
    order = p.product(['u','v'], 0, 1, [2])
    reversed_order = p.product(['v','u'], 0, 1, [2])
    require(symbolic(order,3) != symbolic(reversed_order,3), 'factor-order control')
    controls['reversed_noncommuting_product'] = 'rejected'
    return controls


def source_check():
    spec=json.loads((ROOT/'SOURCES.json').read_text())
    for entry in spec['references']:
        data=(ROOT/entry['local']).read_bytes()
        require(hashlib.sha256(data).hexdigest()==entry['sha256'], 'source SHA256 '+entry['local'])
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require(blob==entry['git_blob'], 'source Git blob '+entry['local'])
    return spec


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--write',action='store_true',help='regenerate only this package certificate')
    args=ap.parse_args()
    sources=source_check()
    independent=load('independent')
    evidence={'base':'abdc6a7002abdbcd9e21bfc5e1a795784deacfdf','seed':54,
              'scope':'exact rectangular recursive interface; no new kappa','sources':sources}
    counts={'cases':0,'complete_child_boundaries':0,'symbolic_leaf_occurrences':0}
    independent_grid=[]
    for m in range(1,5):
        for k in range(2,6):
            lengths={**{f'B{j}':1+(j+m)%4 for j in range(m)},
                     **{f'A{i}':1+(i+k)%4 for i in range(k)}}
            grid_factors, cases=check_case(m,k,lengths)
            independent_grid.append({'m':m,'k':k,'receipt':independent.check(cases,grid_factors,m=m,k=k)})
            counts['cases']+=1
            counts['complete_child_boundaries']+=sum(len(c['boundaries']) for c in cases.values())
            counts['symbolic_leaf_occurrences']+=sum(len(c['word']) for c in cases.values())
    lengths={**{f'B{j}':j+2 for j in range(3)},**{f'A{i}':i+1 for i in range(4)}}
    factors,cases=check_case(3,4,lengths)
    evidence['domain']={'sources':[1,2,3,4],'outputs':[2,3,4,5],
                        'factor_length_rule':'B_j=1+(j+m)%4; A_i=1+(i+k)%4','counts':counts}
    evidence['seed_fixture']={'m':3,'k':4,'factor_lengths':lengths,'schedules':cases}
    evidence['negative_controls']=negative_controls()
    # Independent backend operates only on the emitted instruction values.
    evidence['independent']=independent.check(cases,factors,m=3,k=4)
    evidence['independent_grid']=independent_grid
    evidence['minimum_word_census']=independent.minimum_census()
    evidence['direct_full_word_census']=load('full_census').replay()
    # Actual port prices are not covered by the per-operator optimum theorem.
    def port_price(word):
        return sum(1000 if f == 'A0' and src == 6 else 1 for _,f,src,_ in word)
    borrowed_price=port_price(cases['borrowed']['queries'])
    separate_price=port_price(cases['separate_outputs']['queries'])
    require(borrowed_price > separate_price, 'port-dependent price scope control')
    evidence['port_price_scope_control']={'price_rule':'1000 for A0 reading output row 6; 1 otherwise',
                                         'borrowed':borrowed_price,'separate_outputs':separate_price}
    encoded=canonical(evidence)
    certificate=ROOT/'CERTIFICATE.json'
    if args.write:
        certificate.write_text(encoded)
    else:
        require(certificate.read_text()==encoded, 'certificate differs from complete replay')
    print('PASS_RECTANGULAR_OUTPUT_BORROWING queries=20_vs_32_vs_36 leaves=182_vs_302_vs_306 dirty_rows=2 dedicated=122_leaves_3_rows minimum_2x2_words=76032 no_new_kappa')
    return evidence

if __name__=='__main__':
    main()
