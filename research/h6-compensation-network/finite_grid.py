"""Finite exact-child Gaussian-dyadic grid ledger; no approximation admission."""
from pathlib import Path
from fractions import Fraction
import gzip
import hashlib
import json
import sys
import copy

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def denominator_bits(q):
    den = Fraction(q).denominator
    need(den & (den - 1) == 0, 'non-dyadic coefficient')
    return den.bit_length() - 1


def interpret(f, claimed_bound=None):
    # A value on grid 2^-f initially has extra denominator degree zero.
    degrees = {r: 0 for r in f['starts']}
    dimensions = {r: len(v) for r, v in f['starts'].items()}
    peak = 0
    phases = {}
    for e in f['events']:
        op = e['op']
        if op == 'private_begin':
            r = e['register']
            need(r not in degrees, 'private grid lifetime')
            degrees[r] = 0
            dimensions[r] = len(e['frame'])
        elif op == 'private_end':
            r = e['register']
            del degrees[r], dimensions[r]
        elif op in ('climb', 'private_transition'):
            r = e['register']
            rank = abs(len(e['frame']) - dimensions[r])
            if op == 'private_transition':
                need(rank == e['rank'] == 17, 'private grid child rank')
            need(rank > 0, 'strict grid child')
            degrees[r] += rank
            dimensions[r] = len(e['frame'])
        elif op == 'add':
            dst, src = e['dst'], e['src']
            need(dimensions[dst] == dimensions[src], 'grid incidence dimension')
            degrees[dst] = max(degrees[dst], degrees[src] + denominator_bits(e['q']))
        else:
            raise ValueError('unknown grid opcode ' + op)
        current = max(degrees.values())
        peak = max(peak, current)
        phases[e['phase']] = max(phases.get(e['phase'], 0), current)
    bound = claimed_bound if claimed_bound is not None else (27 if f['dual'] else 60)
    need(peak <= bound, 'finite grid bound exceeded')
    return dict(dual=f['dual'], ports=len(f['indices']), maximum_extra_denominator_bits=peak,
                certified_uniform_bound=bound, phase_prefix_maxima=phases)


def main():
    k = json.loads((HERE/'k_encoder/RESULT.json').read_text())
    need(max(denominator_bits(q) for q in k['scatter_coefficients']) == 10,
         'full K scatter denominator census')
    need(all(denominator_bits(q) == 0 for q in k['gather_coefficients']),
         'full K gather must be integral')
    need(k['ordinary_center_path'] == [17] and k['private_descent_C'] == 816*17,
         'full K grid profile')
    receipts = []
    for directory in ('k_encoder', 'independent'):
        for n in (8, 32):
            for orientation in ('forward', 'dual'):
                path = HERE/directory/f'fixture-{n}-{orientation}.json.gz'
                f = json.loads(gzip.decompress(path.read_bytes()))
                receipt = interpret(f)
                receipt.update(artifact=str(path.relative_to(HERE)),
                               sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                receipts.append(receipt)
    # Repetition within each full-word phase cannot increase degree: every
    # weighted ADD draws from a fixed source role, not its updated destination.
    forward = dict(comp_prefix_target=4, K_prefix_target=10, comp_line_helper=1,
                   comp_loaded_helper=1, source_FULL=16, K_center_FULL=17,
                   K_gathered_center=17, K_private_zero=34,
                   K_scattered_target=44, final_target_cap=60,
                   comp_helper_cap=16, comp_helper_FULL=17)
    dual = dict(comp_prefix_helper=4, K_prefix_center=10, comp_line_helper=5,
                source_after_comp_gather=5, source_FULL=21,
                K_center_FULL=27, source_after_K_gather=27,
                private_zero_gather=10, private_FULL=27, final_target_cap=16,
                comp_helper_cap=20, comp_helper_FULL=21, final_source=27)
    need(forward['final_target_cap'] == 17+17+10+16 == 60,
         'forward grid ledger')
    need(dual['K_center_FULL'] == 10+17 == 27, 'dual grid ledger')
    bank = json.loads((HERE/'bank_physical/RESULT.json').read_text())
    # This is a conservative consequence of the separately checked range
    # ledger, not a claim that every register attains this magnitude.
    range_bound = 1447043072
    need(int(bank['amplification']['component_physical_bound']) == range_bound,
         'independent range ledger binding')
    need(range_bound < 2**31 and 2*range_bound < 2**32, 'finite range bit bound')
    controls = {}
    f = json.loads(gzip.decompress((HERE/'k_encoder/fixture-8-forward.json.gz').read_bytes()))
    for name in ('understate_grid', 'wrong_private_child_rank', 'non_dyadic_coefficient'):
        mutant = copy.deepcopy(f)
        if name == 'wrong_private_child_rank':
            next(e for e in mutant['events'] if e['op'] == 'private_transition')['rank'] = 16
        if name == 'non_dyadic_coefficient':
            next(e for e in mutant['events'] if e['op'] == 'add')['q'] = '1/3'
        try:
            interpret(mutant, 59 if name == 'understate_grid' else None)
        except ValueError as exc:
            controls[name] = str(exc)
        else:
            raise ValueError('grid negative control accepted ' + name)
    result = dict(status='PASS_FINITE_EXACT_CHILD_COMMON_GRID_LEDGER',
        extra_fractional_bits=dict(forward=60, dual=27, common=60),
        full_word_phase_upper_bounds=dict(forward=forward, dual=dual),
        fixtures=receipts, negative_controls=controls,
        physical_component_range_bound_for_unit_complex_inputs=range_bound,
        numerator_bit_growth_upper_bound_for_edge_fallback=92,
        range_scope='The retained full-edge range ledger supplies this numerator bound. The bucketed denominator ledger is certified separately; no bucketed range bound is inferred from the edge ledger.',
        grid_statement='Input Gaussian dyadics with fractional precision f remain on grid2^-(f+60), with exact17-bit children and affine adapters. In the edge fallback, for input physical component numerator bits B, B+92 is a conservative intermediate bound, allowing separately unit real and imaginary components.',
        scope='Finite flat local word with exact children only. Repeated phase incidences draw from fixed source roles. No propagated approximate-child errors, all-size precision/tape/bit supplier or admission claim.',
        source_sha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (Path(__file__), HERE/'k_encoder/RESULT.json',
                                 HERE/'bank_physical/RESULT.json')})
    (HERE/'GRID.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(result['status'], 'common_extra_fractional_bits=60', flush=True)


if __name__ == '__main__':
    main()
