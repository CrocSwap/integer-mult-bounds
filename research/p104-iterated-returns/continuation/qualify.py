"""Replay the exact bounded scalar application of a pinned carrier."""
import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compiler import apply_expanded, compile_scalar, execute, need, scalar_summary, width

RECIPIENT = HERE.parent
TARGET = '0.00387981257853'
CALLER_PIN = '156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858'
BIT_WORD = 'd3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
BIT_FINITE_PIN = '0cebc543d64ca53ac6c7141dfab40c658bf451fe89bb7744befb76c116ea45e6'
E40B_APP_PIN = '88486d49f2ba1fc0e6c9f4a7402c82e91c44026cf90cd1387d1e5c45cf5e88d3'
PREMISES = ['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery']


def checked_json(path, digest, compressed=True):
    raw = path.read_bytes()
    if not compressed:
        need(sha256(raw).hexdigest() == digest, f'wrong file bytes: {path}')
        return json.loads(raw)
    value = json.loads(gzip.decompress(raw))
    canonical = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    need(sha256(canonical).hexdigest() == digest, f'wrong canonical bytes: {path}')
    return value


def check_sources(cache, package):
    lock = json.loads((package / 'SOURCE-LOCK.json').read_bytes())['sources']
    for key in ('source', 'peer', 'parent'):
        for name, pin in lock[key]['files'].items():
            need(sha256((cache / key / name).read_bytes()).hexdigest() == pin['sha256'],
                 f'pinned compiler source {name}')
    return lock['source']['commit']


def reject(action, error):
    try:
        action()
    except ValueError as failure:
        need(str(failure) == error, f'wrong fault: {failure}')
    else:
        raise ValueError(f'undetected fault: {error}')


def controls(physical):
    prime = 16777259
    need(prime > 2**24 - 1 and all(prime % i for i in range(2, isqrt(prime) + 1)), 'large prime control')
    reject(lambda: compile_scalar(Fraction(1, prime)), f'denominator has a factor above 24 bits: {prime}')
    q = Fraction(63127879, 37)
    plan = compile_scalar(q)
    reject(lambda: execute(plan, 1, 32, physical.scalar_service), 'physical remainder')
    reject(lambda: execute(plan, 37, 26, physical.scalar_service), 'installed scalar overflow')
    correct, _ = execute(plan, -37, 32, physical.scalar_service, (17, -91))
    instructions, result = plan
    bad = tuple((op, out, source, arg - 1 if i == 2 else arg)
                for i, (op, out, source, arg) in enumerate(instructions))
    altered, _ = execute((bad, result), -37, 32, physical.scalar_service, (17, -91))
    need(correct == -63127879 and altered != correct, 'mutated radix factor detected')
    return dict(inexact_rejected=True, installed_overflow_rejected=True, unsplittable_prime=prime,
                radix_fault={'coefficient': str(q), 'x': -37, 'want': correct, 'actual': altered},
                dirty_term_scratch_seed=[17, -91])


def native_replay(reference, supplier, graph, layout, owners, moves, rows, caller):
    physical = supplier.physical
    native = physical.graph_bounds(graph, moves, rows, owners[0])
    coarse = native['path_grid']
    expected = physical.expected_rows(layout['public'], layout, owners, coarse)
    native.update(reference.candidate_grid(physical, graph, moves, rows, coarse, expected))
    grid = native['minimum_product_grid']
    odd, height = physical.grid_parts(grid)
    native.update(path_only_grid=coarse, path_grid=grid, path_grid_odd=odd, path_grid_height=height)
    expected = physical.expected_rows(layout['public'], layout, owners, grid)
    save = physical.SURVIVOR
    if save not in moves:
        physical.SURVIVOR = min(moves)
    try:
        native.update(physical.held_schedule(graph, moves, rows, grid, expected, control=True),
                      live_sender_control_slot=physical.SURVIVOR)
    finally:
        physical.SURVIVOR = save
    need(native['live_sender_alias_control_rejected'], 'dirty live sender rejection')
    factors = reference.factor_odd(odd)
    round_trips = supplier.verify_conversions(layout['public'], grid, factors)
    has_wide = any(width(q) > 24 for row in rows.values() for _, q in row)
    if has_wide:
        reject(lambda: physical.scalar_cases([rows], caller, (2025, *factors)),
               'all literal scalar and division conversions fit W+26')
    scalar = scalar_summary(physical, rows, caller, (2025, *factors))
    return native, dict(odd_factors=factors, round_trips=round_trips, scalar_cases=scalar,
                        default_literal_guard_rejected=has_wide, partial_clear=physical.partial_clear_control())


def qualify(args):
    cache, package = args.cache, args.package
    source_head = check_sources(cache, package)
    parent = cache/'parent'
    sys.path.insert(0, str(parent))
    import qualify_complex as inherited
    reference = inherited.historical_checker(cache/'peer')
    sys.path.insert(0, str(cache/'source/research/p104-dual-supplier-lift/complex'))
    import supplier
    import supplier_gate
    from closed_application import main_boundary, verify_caller

    graph = checked_json(args.word, args.word_sha)
    layout = checked_json(args.layout, args.layout_sha)
    base_app = inherited.json_file(parent/'evidence/application.json')
    e40b_path = args.e40b_receipt or package/'evidence/application.json'
    current_app = checked_json(e40b_path, E40B_APP_PIN, compressed=False)
    binary = checked_json(package/'binary/FINITE.json', BIT_FINITE_PIN, compressed=False)
    checked_json(package/'binary/WORD.json.gz', BIT_WORD)
    need(binary['word_sha256'] == BIT_WORD, 'common BIT source')
    bit_cap = Fraction(binary['ordinary_admitted'])

    main_boundary(graph, layout)
    owners = inherited.owners(layout)
    caller = supplier.read(supplier.SOURCE/'data/CALLER.json.gz')
    phase = supplier.read(supplier.SOURCE/'data/CALLER-PHASE-BASES.json')
    signed, guard, caller_proof, coefficients = verify_caller(caller, graph, layout, phase)
    need(caller_proof['readback']['event_stream_sha256'] == CALLER_PIN and signed['calls'] == 48,
         'same complete 48-call physical caller')
    moves, rows = reference.graph_inputs(graph)
    print('Replaying exact native columns and addressed retirement.', flush=True)
    native, conversion = native_replay(reference, supplier, graph, layout, owners, moves, rows, caller)
    weights = reference.invoice(native, reference.count_caller(caller))
    claim, tested, lower, upper = inherited.price(reference, weights, bit_cap)
    supplier_gate.BIT_PIN = str(bit_cap)
    application = apply_expanded(native, signed, guard, coefficients, conversion, supplier.physical,
                                 claim, tested, lower, upper, bit_cap)
    need(application['invoice'] == {'paid': weights['P'], 'targets': weights['T']}, 'independent signed invoice')
    for comparator in (base_app, current_app):
        if comparator['native_sha256'] == args.word_sha:
            archived = comparator['application']
            archived_invoice = {side: {int(rank): count for rank, count in hist.items()}
                                for side, hist in archived['invoice'].items()}
            need(archived['ordinary'] == application['ordinary'], 'identical retained ordinary bill')
            need(archived_invoice == application['invoice'], 'identical retained signed bill')
    physical = supplier.physical
    common = physical.root_envelope({'tested': native, 'original_7781': base_app['native'],
                                     'current_7786': current_app['native']}, guard)
    inputs = {'tested': application, 'original_7781': base_app['application'], 'current_7786': current_app['application']}
    common_guards = {name: physical.check_depth_guard(common, int(item['compiler']['H']))
                     for name, item in inputs.items()}
    return dict(status='PASS_COMMON_BOUNDED_SCALAR_APPLICATION', word_sha256=args.word_sha,
                layout_sha256=args.layout_sha, donor_head=source_head, caller=CALLER_PIN,
                binary_word=binary['word_sha256'], binary_ordinary=str(bit_cap), premises=PREMISES,
                target=TARGET, target_signed_margin=list(map(str, reference.dyadic_price(weights, TARGET))),
                native=native, conversion=conversion, application=application, common_root=common,
                common_depth_guards=common_guards, caller_census=signed, caller_proof=caller_proof,
                compiler_controls=controls(physical))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--package', type=Path, default=RECIPIENT)
    parser.add_argument('--e40b-receipt', type=Path)
    for key in ('word', 'layout', 'out'):
        parser.add_argument('--'+key, type=Path, required=True)
    for key in ('word-sha', 'layout-sha'):
        parser.add_argument('--'+key, required=True)
    args = parser.parse_args()
    result = qualify(args)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], result['word_sha256'], result['application']['claim'], flush=True)
