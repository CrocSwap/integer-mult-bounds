"""Read-only exact boundary audit; no producer or Clifford compiler imports.

Native Gaussian-dyadic interpreter credit: retained PR1991/1862 lineage.
The new coverage is complete program transposition with owned collectors.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[1]
BASE = H.parent / 'p104-native-channel'
N = None


def need(value, why):
    if not value:
        raise ValueError(why)


def pins():
    for row in json.loads((H / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        data = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'input SHA256 ' + row['path'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'input Git blob')
    for row in json.loads((H / 'PREDECESSORS.json').read_text())['files']:
        data = (H / row['local']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'predecessor SHA256')
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'predecessor Git blob')


def canonical(vectors):
    """Unique high-pivot reduced GF(2) basis, independently reconstructed."""
    values = {0}
    for v in vectors:
        values |= {x ^ v for x in tuple(values)}
    out = []
    for bit in range(8, -1, -1):
        candidates = [v for v in values if v.bit_length() == bit + 1]
        if candidates:
            out.append(min(candidates))
    return tuple(out)


def roots():
    rr = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            rr.add(tuple(r))
    for s in product((-1, 1), repeat=7):
        if s.count(-1) % 2 == 0:
            rr.add((1, *s))
    need(len(rr) == 120, '120 E8 root lines')
    return sorted(rr)


def chart_converter(base, fixture):
    rr = roots()
    inner = lambda a, b: sum(x*y for x, y in zip(a, b)) // 4
    binary = [sum(((inner(a, b)+1) & 1) << j for j, b in enumerate(rr)) for a in rr]
    iso = base['label_isometry']
    ix = iso['pivot_root_indices']
    need(len(set(ix)) == len(ix) == 9, 'isometry pivot size')
    compressed = [sum(((row >> j) & 1) << k for k, j in enumerate(ix)) for row in binary]
    gram = [compressed[i] for i in ix]
    need(gram == iso['compressed_gram'], 'physical Gram')
    dual = list(N.inverse(tuple(gram)))
    need(dual == iso['compressed_dual_gram'], 'physical dual Gram')
    orth = iso['orthonormal_basis_compressed']
    def dot(a, b):
        image = sum(((row & b).bit_count() % 2) << i for i, row in enumerate(dual))
        return (a & image).bit_count() % 2
    need(len(orth) == 9 and all(dot(a,b) == int(i==j) for i,a in enumerate(orth) for j,b in enumerate(orth)), 'physical orthonormal basis')
    convert = lambda v: sum(dot(v, b) << j for j, b in enumerate(orth))
    q = [convert(v) for v in compressed]
    need(q == iso['physical_root_labels'], 'all physical labels')
    need(all(((a&b).bit_count() % 2) == ((binary[i] >> j) & 1) for i,a in enumerate(q) for j,b in enumerate(q)), 'all14400 physical pairings')
    removed = {tuple(v) for v in fixture['F0'] + fixture['C']}
    ports = [v for v in rr if v not in removed]
    need(len(ports) == 104, 'P104 port set')
    return lambda vs: canonical([convert(v) for v in vs]), ports, dict(zip(rr, q))


def forward_word(w, c):
    need(c['source_witness_sha256'] == hashlib.sha256((BASE / 'inputs/LOWRANK-WITNESS.json').read_bytes()).hexdigest(), 'correction witness binding')
    need(c['targets'] == [0, 1], 'two corrected targets')
    cuts = {}
    for row in c['insertions']:
        cut = row['completed_cut']
        need(cut not in cuts and 0 <= cut <= len(w['program']), 'unique insertion cut')
        cuts[cut] = row['events']
    result, origin = [], []
    for cut in range(len(w['program']) + 1):
        for j, e in enumerate(cuts.get(cut, [])):
            result.append(e)
            origin.append(('added', cut, j))
        if cut < len(w['program']):
            result.append(w['program'][cut])
            origin.append(('base', cut))
    need(not (set(w['initial_frames']) & set(c['initial_frames'])), 'distinct added helpers')
    return result, origin, w['initial_frames'] | c['initial_frames'], w['final_frames'] | c['final_frames']


def expected_rows(names, ports, direction):
    out = {r: {r: Q(1)} for r in names}
    for t, a in enumerate(ports):
        for s, b in enumerate(ports):
            coeff = Q(int(t == s)) if t < 2 else Q(sum(x*y for x,y in zip(a,b)), 8)
            if coeff:
                if direction == 'forward':
                    out['Y'+str(t)]['X'+str(s)] = coeff
                else:
                    out['X'+str(s)]['Y'+str(t)] = -coeff
    return out


def replay(events, initial, final, chart, zero_discard=False):
    frames = {r: chart(f) for r,f in initial.items()}
    rows = {r: {r: Q(1)} for r in initial}
    counts, profile, lifetimes = Counter(), Counter(), []
    active = None
    for i, e in enumerate(events):
        op, reg = e[:2]
        counts[op] += 1
        if op == 'transport':
            _, reg, old, new, rank = e
            a, b = chart(old), chart(new)
            need(reg in frames and frames[reg] == a, 'transport entry frame')
            need(len(a) == len(old) and len(b) == len(new), 'independent transport frames')
            need(canonical(a+b) in (a, b) and abs(len(a)-len(b)) == rank > 0, 'nested exact transport rank')
            frames[reg] = b
            profile[rank] += 1
        elif op == 'zero':
            need(reg == 'C' and reg not in rows and active is None, 'fresh owned collector')
            rows[reg], frames[reg] = {}, chart(e[2])
            active = dict(start=i, adds_into=0, adds_out=0, initial_frame=e[2])
        elif op == 'erase':
            need(reg == 'C' and active is not None and frames[reg] == chart(e[2]), 'owned discard frame')
            if zero_discard:
                need(not rows[reg], 'stronger zero-restored discard fails')
            active.update(end=i, final_frame=e[2], nonzero_at_discard=bool(rows[reg]), support_at_discard=len(rows[reg]))
            lifetimes.append(active)
            active = None
            del rows[reg], frames[reg]
        elif op == 'sign':
            need(reg.startswith('X') and e[2] == '-1' and frames[reg] == chart(e[3]), 'explicit source sign')
            rows[reg] = {k:-v for k,v in rows[reg].items()}
        elif op in ('copy', 'add'):
            src = e[2]
            frame = chart(e[-1])
            need(reg != src and frames[reg] == frames[src] == frame, 'scalar common chart')
            if op == 'copy':
                need(reg == 'C' and not rows[reg], 'COPY destination zero')
                rows[reg] = dict(rows[src])
            else:
                coeff = Q(e[3])
                for k, v in tuple(rows[src].items()):
                    value = rows[reg].get(k, Q(0)) + coeff*v
                    if value:
                        rows[reg][k] = value
                    else:
                        rows[reg].pop(k, None)
                if reg == 'C':
                    active['adds_into'] += 1
                if src == 'C':
                    active['adds_out'] += 1
        else:
            raise ValueError('unknown event')
    need(active is None and set(rows) == set(initial) == set(final), 'persistent boundary names and closed private storage')
    need(frames == {r: chart(f) for r,f in final.items()}, 'all exit frames')
    return rows, dict(counts), dict(sorted(profile.items())), lifetimes


def bind_dual(dual, forward, initial, final):
    need(dual['schema_version'] == 1 and dual['initial_frames'] == final and dual['final_frames'] == initial, 'backward charts')
    p = dual['program']
    need(len(p) == len(forward) + 208, 'complete dual event count')
    for k in range(104):
        need(p[k] == ['sign', 'X'+str(k), '-1', final['X'+str(k)]], 'input sign pass')
        need(p[-104+k] == ['sign', 'X'+str(k), '-1', initial['X'+str(k)]], 'output sign pass')
    for f, d in zip(forward, reversed(p[104:-104])):
        if f[0] == 'add':
            need(d == ['add',f[2],f[1],f[3],f[4]], 'ADD adjoint binding')
        elif f[0] == 'copy':
            need(d == ['add',f[2],f[1],'1',f[3]], 'COPY collector accumulation binding')
        elif f[0] == 'transport':
            need(d == ['transport',f[1],f[3],f[2],f[4]], 'native adjoint occurrence binding')
        else:
            need(f[0] in ('zero','erase') and d == [('erase' if f[0]=='zero' else 'zero'),f[1],f[2]], 'embedding projection adjoint binding')


def bind_clean(clean, owned):
    """Check the frozen completion and its unchanged-gather-source premise."""
    need({k:v for k,v in clean.items() if k!='program'} ==
         {k:v for k,v in owned.items() if k!='program'}, 'same clean boundary charts')
    expected, life, additions = [], [], []
    for e in owned['program']:
        if e[0] == 'zero':
            need(not life, 'nonoverlapping owned lifetimes')
            life = [e]
        elif life:
            life.append(e)
        if e[0] != 'erase':
            expected.append(e)
            continue
        gathers, climb, give = life[1:-3], life[-3], life[-2]
        need(climb[0:2] == ['transport','C'] and climb[4] == 7 and
             give[0] == 'add' and give[2:4] == ['C','1'], 'single climb and owner return')
        line, cap = climb[2:4]
        need(life[0] == ['zero','C',line] and e == ['erase','C',cap], 'collector endpoints')
        owner = give[1]
        need(give[-1] == cap and all(g[0:2] == ['add','C'] and g[-1] == line and
             g[2] not in ('C',owner) for g in gathers), 'gather sources unchanged and disjoint from owner')
        # The entire interior is exactly these C writes plus one Q write.
        # Thus the values and charts of every gather source remain untouched.
        back = ['transport','C',cap,line,7]
        expected.append(back)
        expected.extend(['add','C',g[2],str(-Q(g[3])),line] for g in reversed(gathers))
        expected.append(['erase','C',line])
        additions.append(dict(owner=owner, gather_sources=[g[2] for g in gathers],
                              extra_adds=len(gathers), extra_rank=7, return_transport=back))
        life = []
    need(not life and clean['program'] == expected, 'complete clean-return word binding')
    need(len(additions) == 8 and sum(r['extra_adds'] for r in additions)==32, 'eight returns and32inverse gathers')
    return additions


def native_audit(base, added, w, c, word, origins, chart, ports, labels, clean_events):
    """Bind every forward occurrence, then verify its complete adjoint operator."""
    assigned, pair_keys = {}, set()
    edges = 0
    phase_control = None
    for group, records in [('base', base['transports']), ('added', added['transports'])]:
        for rec in records:
            a, b = tuple(rec['old']), tuple(rec['new'])
            need(canonical(a) == a and canonical(b) == b, 'exact canonical native representatives')
            pair_keys.add((a,b))
            recipe = rec['recipe'] if group == 'base' else rec['forward']
            rank = rec['rank']
            need(rank == abs(len(a)-len(b)) > 0 and recipe['rank'] == rank, 'native positive child rank')
            forward = N.recipe(recipe)
            # C_j^-1 = X_j C_j. Thus F_k^-1 = X_(2^k-1) F_k:
            # reverse monomials but retain ONE positive child, explicitly
            # charging the additional rank-zero XOR in the left adapter.
            backward = (N.adjoint(N.monomial(recipe['left'])) + N.fourier(rank)
                        + (('X', (1 << rank)-1),) + N.adjoint(N.monomial(recipe['right']))) if group == 'base' else N.recipe(rec['adjoint'])
            need(sum(g[0]=='C' for g in backward) == rank and
                 all(g[2] == 1 for g in backward if g[0]=='C'), 'one positive rank-k child')
            if group == 'added':
                need(rec['adjoint']['rank'] == rank, 'adjoint child rank')
            N.equal(forward, N.adjoint(N.frame(a,9))+N.frame(b,9), 'complete forward native operator')
            expected = N.adjoint(N.frame(b,9))+N.frame(a,9)
            N.equal(backward, expected, 'complete backward native operator')
            if phase_control is None:
                phase_control = (backward + (('phase', 1),), expected)
            if group == 'base':
                occurrences = [('base', i) for i in rec['events']]
            else:
                occurrences = [('added', c['insertions'][i]['completed_cut'], j) for i,j in rec['occurrences']]
            for key in occurrences:
                need(key not in assigned, 'unique native occurrence')
                assigned[key] = (a,b,rank)
            edges += 1
    need(len(pair_keys) == edges, 'distinct directed native pairs')
    for e, key in zip(word, origins):
        if e[0] != 'transport':
            need(key not in assigned, 'no native binding on scalar')
            continue
        need(key in assigned and assigned[key] == (chart(e[2]),chart(e[3]),e[4]), 'literal full-word native binding')
    need(set(assigned) == {key for e,key in zip(word,origins) if e[0]=='transport'}, 'complete native coverage')
    # Each ordinary backward edge uses the checked adjoint. Each added
    # collector return uses the checked forward operator of that same edge.
    clean_pairs = set()
    clean_occurrences = 0
    for e in clean_events:
        if e[0] == 'transport':
            pair = (chart(e[2]),chart(e[3]))
            need(pair in pair_keys or pair[::-1] in pair_keys, 'every clean-word native operator bound')
            clean_pairs.add(pair)
            clean_occurrences += 1
    need(clean_occurrences==1654, 'complete clean native occurrence count')
    adapters = set()
    for r in base['endpoint_adapters']:
        where, reg, f = r['position'], r['register'], tuple(r['frame'])
        need((where,reg) not in adapters and r['recipe']['rank'] == 0, 'unique rank-zero intrinsic adapter')
        adapters.add((where,reg))
        normal = labels[ports[int(reg[1:])]]
        need(r['normal'] == normal, 'intrinsic root label')
        if where == 'entry':
            need(reg.startswith('X') and f == chart(w['initial_frames'][reg]) == (normal,), 'intrinsic source entry')
            forward = N.adjoint((('C',normal,1),)) + N.frame(f,9)
        else:
            need(where == 'exit' and reg.startswith('Y') and f == chart(w['final_frames'][reg]), 'intrinsic target exit')
            need(all(not((v&normal).bit_count()%2) for v in f), 'intrinsic target hyperplane')
            forward = N.adjoint(N.frame(f,9)) + (('C',normal,-1),) + N.fourier(9)
        N.equal(N.recipe(r['recipe']), forward, 'forward intrinsic endpoint')
        N.equal(N.adjoint(N.recipe(r['recipe'])), N.adjoint(forward), 'backward intrinsic endpoint')
    need(adapters == {('entry','X'+str(k)) for k in range(104)} | {('exit','Y'+str(k)) for k in range(104)}, 'all208 endpoint adjoints')
    try:
        N.equal(*phase_control, 'phase corruption must fail')
    except ValueError:
        phase_rejected = True
    else:
        raise ValueError('accepted native adjoint global phase corruption')
    return dict(distinct_transport_pairs=edges, transport_occurrences=len(assigned),
                clean_distinct_directed_pairs=len(clean_pairs),clean_transport_occurrences=clean_occurrences,
                intrinsic_adjoint_adapters=len(adapters), exact_phase_control=phase_rejected)


def run():
    global N
    pins()
    spec = importlib.util.spec_from_file_location('p104_native_gaussian', BASE / 'vendor/native_verify.py')
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)
    w = json.loads((BASE/'inputs/LOWRANK-WITNESS.json').read_text())
    c = json.loads((H/'inputs/CIRCUIT.json').read_text())
    base = json.loads(gzip.decompress((BASE/'NATIVE-RECIPES.json.gz').read_bytes()))
    added = json.loads(gzip.decompress((H/'inputs/NATIVE.json.gz').read_bytes()))
    fixture = json.loads((BASE/'inputs/P104-FIXTURE.json').read_text())['section4_explicit_P104']
    dual = json.loads((H/'DUAL.json').read_text())
    clean = json.loads((H/'CLEAN-DUAL.json').read_text())
    chart, ports, labels = chart_converter(base, fixture)
    word, origins, initial, final = forward_word(w,c)
    need(base['source_witness_sha256'] == c['source_witness_sha256'], 'inherited witness binding')
    bind_dual(dual,word,initial,final)
    additions = bind_clean(clean,dual)
    f, fc, fp, fl = replay(word,initial,final,chart)
    d, dc, dp, dl = replay(dual['program'],final,initial,chart)
    need(len(initial) == 358 and f == expected_rows(initial,ports,'forward'), 'all128164 forward coefficients')
    need(d == expected_rows(initial,ports,'dual'), 'all128164 inverse-transpose coefficients')
    need(fp == dp and sum(k*v for k,v in dp.items()) == 3070, 'unchanged complete positive rank invoice')
    need(len(fl) == len(dl) == 8 and all(r['adds_into'] > 0 and r['adds_out'] == 1 and r['nonzero_at_discard'] for r in dl), 'eight actual owned collectors')
    cleaned, cc, cp, cl = replay(clean['program'],final,initial,chart,True)
    need(cleaned==d and len(cl)==8 and all(not r['nonzero_at_discard'] for r in cl), 'all-input clean zero return')
    need(cp == (dp | {7:dp[7]+8}) and sum(k*v for k,v in cp.items())==3126, 'complete clean positive rank invoice')
    native = native_audit(base,added,w,c,word,origins,chart,ports,labels,clean['program'])
    controls = {'native_adjoint_phase': native.pop('exact_phase_control')}
    def reject(label, events, clean=False):
        try:
            rows,_,_,_ = replay(events,final,initial,chart,clean)
            need(rows == expected_rows(initial,ports,'dual'), 'semantic endpoint')
        except (ValueError, KeyError):
            controls[label] = True
        else:
            raise ValueError('accepted control '+label)
    p = dual['program']
    reject('omitted_input_sign',p[1:])
    reject('forward_chronology',[*p[:104],*reversed(p[104:-104]),*p[-104:]])
    bad = copy.deepcopy(p)
    i = next(i for i,e in enumerate(bad) if e[0]=='add' and e[2]=='C')
    bad[i][3] = '0'
    reject('missing_collector_return',bad)
    bad = copy.deepcopy(p)
    i = next(i for i,e in enumerate(bad) if e[0]=='add' and e[2]=='C')
    e = bad[i]
    bad[i] = ['copy','C',e[1],e[-1]]
    reject('COPY_instead_of_adjoint_accumulate',bad)
    bad = copy.deepcopy(p)
    i = next(i for i,e in enumerate(bad) if e[0]=='zero')
    bad[i][2] = []
    reject('wrong_collector_entry_chart',bad)
    bad = [e for e in p if not(e[0]=='transport' and e[1]=='C')]
    reject('omitted_collector_transport',bad)
    reject('zero_restored_discard_claim',p,True)
    clean_p=clean['program']
    reject('clean_missing_return_transport',[e for e in clean_p if not(e[0]=='transport' and e[1]=='C' and len(e[2])==8)],True)
    bad=copy.deepcopy(clean_p)
    i=next(i for i,e in enumerate(bad) if e[0]=='erase')
    bad[i-1][3]='0'
    reject('clean_missing_inverse_gather',bad,True)
    bad=copy.deepcopy(clean_p)
    i=next(i for i,e in enumerate(bad) if e[0]=='erase')
    bad[i-1][3]=str(-Q(bad[i-1][3]))
    reject('clean_wrong_inverse_gather_sign',bad,True)
    wrong = {r:{r:Q(1)} for r in initial}
    for t in range(104):
        for s in range(104):
            a = f['Y'+str(t)].get('X'+str(s),Q(0))
            if a:
                wrong['X'+str(t)]['Y'+str(s)] = -a
    need(d != wrong, 'asymmetric correction detects untransposed C')
    controls['untransposed_C_oracle'] = True
    alternative = list(reversed(p[:104])) + p[104:]
    need(replay(alternative,final,initial,chart)[0] == d, 'accepted equivalent input sign order')
    transpose = {r:{} for r in initial}
    for r,row in f.items():
        for s,v in row.items():
            transpose[s][r] = v
    for r,row in transpose.items():
        composition = {}
        for middle,a in row.items():
            for s,b in d[middle].items():
                composition[s] = composition.get(s,Q(0))+a*b
        need({s:v for s,v in composition.items() if v} == {r:Q(1)}, 'S transpose times D identity')
    return dict(status='PASS_P104_OWNED_COLLECTOR_DUAL', boundary_inputs=358, boundary_coefficients=358**2,
                forward_events=len(word), backward_events=len(p), scalar_operations=dc,
                backward_positive_profile=dp, rank_mass=3070, native=native,
                owned_collectors=dl, controls=controls, equivalent_sign_order=True,
                clean_return=dict(events=len(clean_p),scalar_operations=cc,positive_profile=cp,rank_mass=3126,
                                  lifetimes=cl,extensions=additions,all_private_zero_at_erase=True),
                scope='Exact finite logical inverse-transpose in backward canonical/intrinsic charts, with8 private collectors restored to zero; no paired supplier or new kappa.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit-initial-result', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = run()
    if not args.emit_initial_result:
        need(json.dumps(result,sort_keys=True,allow_nan=False) ==
             json.dumps(json.loads((H/'RESULT.json').read_text()),sort_keys=True,allow_nan=False), 'committed receipt mismatch')
    else:
        need(args.out is not None, 'explicit output required for authoring')
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2,sort_keys=True)
            stream.write('\n')
    print('PASS_P104_OWNED_COLLECTOR_DUAL inputs=358 collectors=8 clean_rank_mass=3126 controls=12 no_new_kappa')


if __name__ == '__main__':
    main()
