"""All eight QQ16 local-axis families: a sharp ordinary-port read criterion.

New partition/kernel argument and certificates: Gareth Davidson with substantial
OpenAI Codex assistance. Retained source and logical algebra: commdata2338,
Ali Romman and the credited QQ16 predecessors. Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from algebra import rref, rank, null_vector, inverse, mv
from logical import replay as logical_replay


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    out = {}
    for key, value in items:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def read(path):
    def reject(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique, parse_constant=reject)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sources(root=ROOT):
    pins = read(HERE / 'SOURCES.json')
    live = {}
    for row in pins['files']:
        if row['usage'] == 'input':
            raw = (root / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'live source hash: ' + row['path'])
            live[row['path']] = row['sha256']
    retained = read(HERE / 'PREDECESSOR.json')
    for path, row in retained['files'].items():
        need(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == row['sha256'],
             'predecessor source hash: ' + path)
    spec = importlib.util.spec_from_file_location('qq16_prior', HERE / 'predecessor/verify.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    packet, phases, template, previous, old_pins = prior.sources(root)
    need(canonical(live) == canonical(old_pins), 'all six live source pins retained')
    bases, routes = prior.derive_routes(packet, phases)
    model = prior.Model(packet, routes)
    return prior, model, bases, routes, template, previous, live


def owner_certificate(prior, bases, routes, certificate):
    """Actual registered generator words, not formal independent bit symbols."""
    words = certificate['owner_words_by_prefix']
    need(set(words) == {str(x) for x in range(512)}, 'complete owner-prefix coverage')
    rows = []
    for prefix in range(512):
        word = words[str(prefix)]
        need(isinstance(word, list) and len(word) <= 4 and
             all(type(p) is int and 0 <= p < 112 for p in word), 'owner word domain')
        vector = 1
        for p in word:
            # rho_1(p) is an orthogonal involution, so its transpose is itself.
            vector = prior.action(routes[1, p], vector)
        need(vector & 511 == prefix, 'actual owner prefix')
        rows.append(vector)
    axes = sorted({b for p in prior.U for b in bases[p]})
    need(axes == certificate['occurring_axes'], 'occurring chart axes')
    masks = {b: sum(((prefix & b).bit_count() % 2) << prefix for prefix in range(512))
             for b in axes}
    for b in axes:
        for c in axes:
            # sum_x (-1)^(x.b) bit(x.c) = -256 delta(b,c).
            need(masks[c].bit_count() - 2 * (masks[b] & masks[c]).bit_count()
                 == (-256 if b == c else 0), 'exact Walsh left inverse')
    tuples = [tuple(bases[p]) for p in prior.U]
    need(len(set(tuples)) == len(tuples), 'distinct complete chart tuples')
    return rows, axes


def make_witness(unread, model, bases):
    """Constructively prove the projection argument for any dependent unread set."""
    need(len(set(unread)) == len(unread), 'distinct unread ports')
    cols = [[row[p] for p in unread] for row in model.R]
    c = {p: q for p, q in zip(unread, null_vector(cols)) if q}
    target = min(c)
    for axis in range(8):
        need(not any(sum(row[p] * q for p, q in c.items()) for row in model.R),
             'projection input remains in source kernel')
        group = {p: q for p, q in c.items() if bases[p][axis] == bases[target][axis]}
        partial = [sum(row[p] * q for p, q in group.items()) for row in model.R]
        if any(partial):
            return axis, c, target
        c = group
    raise ValueError('distinct chart tuples should isolate a nonzero column')


def field_values(functions, vector):
    return [sum(q * ((b & vector).bit_count() % 2) for b, q in f.items()) for f in functions]


def witness_check(prior, model, bases, template, previous, owner_rows, unread):
    axis, coefficients, target = make_witness(unread, model, bases)
    h = prior.zero_bank()
    for p, c in coefficients.items():
        h[p] = {bases[p][axis]: c}
    H = model.query(h, 0)
    prefix = next((i for i, vector in enumerate(owner_rows) if any(field_values(H, vector))), None)
    need(prefix is not None, 'nonzero defect at an actual owner')
    reads = [p for p in prior.U if p not in unread]
    initial_A, H, trace = logical_replay(prior, model, template, h, reads, owner_rows[prefix])
    need([r['ordinary'] for r in trace[2:]] ==
         [r['ordinary'] for r in previous['trajectory_after_B1']], 'retained complete tail')
    return {'unread_ports': unread, 'read_count': len(reads), 'axis_zero_based': axis,
            'coefficients': {str(p): str(c) for p, c in sorted(coefficients.items())},
            'isolated_port': target, 'owner_prefix': prefix,
            'old_query_at_owner': list(map(str, field_values(H, owner_rows[prefix]))),
            'initial_A_at_owner': list(map(str, field_values(initial_A, owner_rows[prefix]))),
            'trace_sha256': hashlib.sha256(canonical(trace).encode()).hexdigest()}, (h, trace)


def grouped(unread, bases, count):
    groups = {}
    for p in unread:
        groups.setdefault(tuple(bases[p][:count]), []).append(p)
    return list(groups.values())


def safe(unread, model, bases, count):
    total = sum(rank([[row[p] for p in group] for row in model.R])
                for group in grouped(unread, bases, count))
    return total == rank([[row[p] for p in unread] for row in model.R])


def hierarchy(prior, model, bases):
    out = []
    for count in range(1, 9):
        groups = grouped(prior.U, bases, count)
        rows = [{'ports': group, 'rank': rank([[row[p] for p in group] for row in model.R])}
                for group in groups]
        dependent = [r for r in rows if r['rank'] < len(r['ports'])]
        need(len(dependent) <= 1, 'at most one redundant common-refinement class')
        nullity = sum(len(r['ports']) - r['rank'] for r in rows)
        unread = list(dependent[0]['ports']) if dependent else []
        for p in prior.U:
            if p not in unread and rank([[row[q] for q in unread + [p]] for row in model.R]) > rank([[row[q] for q in unread] for row in model.R]):
                unread.append(p)
        need(len(unread) == 8 + nullity and safe(unread, model, bases, count),
             'sharp prefix-family attaining set')
        out.append({'axes': count, 'classes': rows, 'total_internal_nullity': nullity,
                    'maximum_safe_unread': len(unread), 'minimum_reads': 96 - len(unread),
                    'attaining_unread': sorted(unread)})
    return out


def mixed_decoder(prior, model, bases, owner_rows, unread, count):
    """Decode the target from actual array samples; internal redundancy is allowed."""
    read_ports = [p for p in prior.U if p not in unread]
    _, pivots = rref([[row[p] for p in unread] for row in model.R])
    basis = [unread[j] for j in pivots]
    need(len(basis) == 8, 'attaining unread set spans the query')
    inv = inverse([[row[p] for p in basis] for row in model.R])
    free = [p for p in prior.U if p not in basis]
    coefficients = []
    for j in range(count):
        c = {p: Q(((p + 3) * (j + 7) + (p ^ j)) % 11 - 5) for p in free}
        rhs = [-sum(row[p] * c[p] for p in free) for row in model.R]
        c.update(zip(basis, mv(inv, rhs)))
        need(not any(sum(row[p] * c[p] for p in prior.U) for row in model.R), 'mixed input source kernel')
        coefficients.append(c)
    arrays = {p: [sum(coefficients[j][p] * ((v & bases[p][j]).bit_count() % 2)
                      for j in range(count)) for v in owner_rows] for p in read_ports}
    recovered = []
    for j in range(count):
        c = {p: Q(0) for p in prior.U}
        for p in read_ports:
            b = bases[p][j]
            c[p] = -sum((1 - 2 * ((v & b).bit_count() % 2)) * value
                         for v, value in zip(owner_rows, arrays[p])) / 256
        rhs = [-sum(row[p] * c[p] for p in read_ports) for row in model.R]
        c.update(zip(basis, mv(inv, rhs)))
        recovered.append(c)
    def target(cs):
        h = prior.zero_bank()
        for p in prior.U:
            h[p] = prior.combination((cs[j][p], {bases[p][j]: Q(1)}) for j in range(count))
        return model.query(h, 0)
    expected, got = target(coefficients), target(recovered)
    need(got == expected, 'complete mixed-axis target recovery')
    return {'axis_parameters': count, 'ordinary_ports': 96, 'read_ports': read_ports,
            'unread_ports': unread, 'completion_basis': basis,
            'exact_target_recovered': True, 'all_coefficients_recovered': recovered == coefficients,
            'target_sha256': hashlib.sha256(canonical([prior.serialize(f) for f in got]).encode()).hexdigest(),
            'basis_inverse': [[str(x) for x in row] for row in inv]}


def run():
    prior, model, bases, routes, template, previous, pins = sources()
    certificate = read(HERE / 'CERTIFICATE.json')
    owner_rows, axes = owner_certificate(prior, bases, routes, certificate)
    ordinary = [[row[p] for p in prior.U] for row in model.R]
    _, pivots = rref(ordinary)
    basis = [prior.U[j] for j in pivots]
    need(len(basis) == 8 and basis == certificate['unread_basis'], 'rank-eight source basis')
    need(all(any(row[p] for row in model.R) for p in prior.U), 'nonzero source columns')
    witnesses = []
    first = None
    for p in prior.U:
        if p not in basis:
            item, runtime = witness_check(prior, model, bases, template, previous, owner_rows, sorted(basis + [p]))
            witnesses.append(item)
            if first is None:
                first = (item, runtime)
    legacy, _ = witness_check(prior, model, bases, template, previous, owner_rows, prior.UNREAD)
    levels = hierarchy(prior, model, bases)
    decoders = [mixed_decoder(prior, model, bases, owner_rows, row['attaining_unread'], row['axes'])
                for row in levels if row['axes'] in (1, 2, 3, 4, 8)]
    deeper = []
    for row in levels[:3]:
        group = next(g['ports'] for g in row['classes'] if len(g['ports']) > g['rank'])
        item, _ = witness_check(prior, model, bases, template, previous, owner_rows, group)
        need(item['axis_zero_based'] == row['axes'], 'next-axis projection witness')
        deeper.append(item)
    controls = []
    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('control was not rejected: ' + name)
    from copy import deepcopy
    bad = deepcopy(certificate)
    bad['owner_words_by_prefix']['0'] = []
    rejects('wrong actual owner word', lambda: owner_certificate(prior, bases, routes, bad))
    bad = deepcopy(certificate);bad['owner_words_by_prefix'].pop('511')
    rejects('missing owner prefix', lambda: owner_certificate(prior, bases, routes, bad))
    bad = deepcopy(certificate);bad['occurring_axes'].pop()
    rejects('omit occurring bit function', lambda: owner_certificate(prior, bases, routes, bad))
    rejects('independent unread basis has no kernel witness', lambda: make_witness(basis, model, bases))
    item, (h, trace) = first
    vector = owner_rows[item['owner_prefix']]
    reads = [p for p in prior.U if p not in item['unread_ports']]
    rejects('read a nonzero hidden port', lambda: logical_replay(prior, model, template, h,
            reads + [int(next(iter(item['coefficients'])))], vector))
    rejects('wrong initial A cancellation', lambda: logical_replay(prior, model, template, h, reads, vector, 1))
    bad_template = deepcopy(template)
    bad_template['recipe'] = [e for e in bad_template['recipe'] if e !=
                             {'kind': 'bridge', 'src': 1, 'dst': 0, 'coefficient': -1}]
    rejects('missing cancelling bridge', lambda: logical_replay(prior, model, bad_template, h, reads, vector))
    bad_routes = dict(routes);p = int(next(iter(item['coefficients'])))
    bad_routes[1, p] = prior.IDENTITY
    wrong_model = deepcopy(model); wrong_model.routes = bad_routes
    rejects('omit owner action', lambda: logical_replay(prior, wrong_model, template, h, reads, vector))
    # Credit the known first-axis blind relation as a boundary of a one-axis claim.
    old = prior.zero_bank()
    for p, c in prior.COEFFICIENTS.items():
        old[p] = {bases[p][0]: Q(c)}
    need(not any(model.query(old, 0)), 'credited first-axis invisible relation')
    controls.append('first-axis-only family has a nontrivial kernel (positive boundary)')
    return {'schema': 'qq16-eight-axis-readsets/1', 'status': 'PASS_QQ16_EIGHT_AXIS_READSETS',
            'source_sha256': pins, 'predecessor_head': read(HERE / 'PREDECESSOR.json')['head'],
            'certificate_sha256': hashlib.sha256((HERE / 'CERTIFICATE.json').read_bytes()).hexdigest(),
            'ordinary_ports': 96, 'source_rank': 8, 'sharp_family_read_threshold': 88,
            'distinct_full_axis_tuples': 96, 'occurring_bit_functions': len(axes),
            'certified_owner_prefixes': 512, 'maximum_owner_word_length': max(map(len, certificate['owner_words_by_prefix'].values())),
            'registered_routes': len(routes), 'all_axis_route_checks': 112 * 8 * 8,
            'walsh_pair_checks': len(axes) ** 2,
            'boundary_87_read_witnesses': witnesses, 'predecessor_66_read_set': legacy,
            'logical_events_per_witness': len(trace), 'complete_trace': trace,
            'axis_prefix_thresholds': levels, 'mixed_axis_decoders': decoders,
            'deeper_axis_witnesses': deeper, 'controls': controls,
            'criterion': 'A fixed read set eliminates all eight local-axis families iff its unread R columns are independent.',
            'full_controller_sufficiency': False, 'native_cost_bound': False,
            'formal_kernel_checked': False, 'new_kappa_claim': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit-result', type=Path)
    args = parser.parse_args()
    need(args.emit_result is None or not args.emit_result.exists(), 'output already exists')
    result = run()
    if args.emit_result:
        with args.emit_result.open('x') as f:
            json.dump(result, f, indent=2, sort_keys=True);f.write('\n')
    else:
        need(canonical(result) == canonical(read(HERE / 'RESULT.json')), 'complete typed receipt differs')
    print(result['status'], 'threshold=88', 'boundary_witnesses=88', 'owner_prefixes=512',
          'controls=' + str(len(result['controls'])), 'no_new_kappa')


if __name__ == '__main__':
    main()
