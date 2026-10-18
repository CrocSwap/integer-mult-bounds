"""Exact caller-boundary norms and grids by observing PR2540's retained replay."""
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import phase


def debt(coefficient):
    phase.need(coefficient != 0, 'nonzero coefficient required')
    d = coefficient.denominator
    phase.need(d & (d-1) == 0, 'non-dyadic logical coefficient')
    numerator = abs(coefficient.numerator)
    return d.bit_length()-1-((numerator & -numerator).bit_length()-1)


def measure(old, word, R, records, expected):
    N = old.N
    source_frames = {f'E{p}': old.OLD for p in old.V}
    source_frames.update({f'X{p}': N.START for p in range(112)})
    source_frames.update({f'Y{p}': N.START+((records[p]['q'], -1),) for p in range(112)})

    @lru_cache(None)
    def form(frame, source, g):
        terms = frame+tuple((N.act(g, v), -c) for v, c in source_frames.get(source, ()))
        a, edges = phase.polynomial(terms, 73)
        # Independent expansion agrees with the retained mod-four character representation.
        linear, upper = N.phase(terms)
        phase.need(a == linear and all((edges[i] >> (i+1)) == (upper[i] >> (i+1)) for i in range(73)),
                   'native phase polynomial binding')
        r = phase.rank(a, edges)
        return a, edges, r

    history = []
    seen = []
    term_checks = 0
    maximum_debt, maximum_gain = 0, Q(1)
    debt_witness, gain_witness = None, None
    debts_by_rank = {}
    gain_rows = []

    def observe(index, event, rows, frames, active):
        nonlocal term_checks, maximum_debt, maximum_gain, debt_witness, gain_witness
        seen.append(index)
        op = event['op']
        if op in ('clear', 'line', 'stage', 'current_map'):
            fields = [event['field']]
        elif op == 'add':
            fields = [event['dst']]
        elif op == 'history_boundary':
            fields = [f'{s}{p}' for s in ('X', 'Y') for p in range(112)]
        elif op == 'private_begin':
            fields = event['fields']
        else:
            phase.need(op in ('private_end', 'checkpoint'), 'observer event coverage')
            fields = []
        for field in fields:
            gain, row_debt = Q(0), 0
            shape = Counter()
            for (source, g), coefficient in rows[field].items():
                a, edges, r = form(frames[field], source, g)
                bits = (r+1)//2
                gain += abs(coefficient)*(1 << bits)
                d = debt(coefficient)+bits
                debts_by_rank[r] = max(debts_by_rank.get(r, -1000), debt(coefficient))
                row_debt = max(row_debt, d)
                shape[(str(coefficient), r)] += 1
                term_checks += 1
                if d > maximum_debt:
                    maximum_debt = d
                    gaussian = phase.witness(a, edges)
                    real, imag = (coefficient*Q(gaussian[k]) for k in ('real', 'imag'))
                    phase.need(max(real.denominator, imag.denominator) == 1 << d,
                               'actual scalar-times-Gaussian denominator')
                    debt_witness = {'event': index, 'field': field, 'source': source,
                                    'owner_columns': list(g), 'coefficient': str(coefficient),
                                    'phase_linear': list(a), 'phase_edges': list(edges),
                                    'kernel': gaussian, 'physical_real': str(real), 'physical_imag': str(imag)}
            history.append([index, field, row_debt, str(gain), len(rows[field])])
            weights = Counter()
            for (c, r), count in shape.items():
                weights[r] += abs(Q(c))*count
            gain_rows.append((index, field, weights))
            if gain > maximum_gain:
                maximum_gain = gain
                gain_witness = {'event': index, 'field': field, 'terms': len(rows[field]),
                                'shape': [[c, r, count] for (c, r), count in sorted(shape.items())]}

    path = Path(old.__file__)
    tree = ast.parse(path.read_bytes())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'replay']
    phase.need(len(functions) == 1, 'exact replay function extraction')
    fn = functions[0]
    loops = [n for n in fn.body if isinstance(n, ast.For)]
    phase.need(len(loops) == 2, 'retained main event loop and final field loop')
    loop = loops[0]
    phase.need(ast.unparse(loop.iter) == 'enumerate(word)', 'exact event loop')
    loop.body.append(ast.Expr(ast.Call(func=ast.Name(id='observe', ctx=ast.Load()),
        args=[ast.Name(id=x, ctx=ast.Load()) for x in ('index', 'e', 'rows', 'frames', 'active')], keywords=[])))
    ast.fix_missing_locations(fn)
    environment = dict(old.__dict__)
    environment['observe'] = observe
    exec(compile(ast.Module(body=[fn], type_ignores=[]), 'authenticated-replay-plus-observer', 'exec'), environment)
    counts = environment['replay'](word, R, records, expected)
    phase.need(seen == list(range(len(word))), 'every event observed exactly once')
    phase.need(set(debts_by_rank) == {0, 1, 8}, 'actual phase ranks')
    phase.need(debts_by_rank[8] == 3 and debts_by_rank[0] <= 7 and debts_by_rank[1] <= 6,
               'uniform fractional envelope 4 lambda + 3')
    # X=2^ceil(lambda/2), Y=16^lambda. Y-16 >= 8*(X-2), X>=2.
    # These finite inequalities therefore certify every positive tensor depth.
    slacks = []
    for index, field, weights in gain_rows:
        b0, b1, b8 = (Q(bound)-weights.get(r, 0) for r, bound in ((0, 48), (1, 48), (8, 144)))
        phase.need(b8 >= 0 and 8*b8+b1 >= 0 and b0+2*b1+16*b8 >= 0,
                   'all-tensor gain envelope at '+str((index, field)))
        slacks.append((b8, 8*b8+b1, b0+2*b1+16*b8))
    # Every changed live field is covered above; unchanged fields keep their previous bound.
    digest = hashlib.sha256(json.dumps(history, separators=(',', ':')).encode()).hexdigest()
    return {'fractional_reserve': maximum_debt, 'amplification': str(maximum_gain),
            'magnitude_guard_bits': (maximum_gain.numerator-1).bit_length()-
                (maximum_gain.denominator.bit_length()-1),
            'word_events': len(word), 'changed_field_boundaries': len(history),
            'term_checks': term_checks, 'phase_operators': form.cache_info().currsize,
            'prefix_table_sha256': digest, 'debt_witness': debt_witness,
            'gain_witness': gain_witness, 'retained_event_counts': counts,
            'scalar_denominator_debt_by_phase_rank': {str(k): v for k, v in sorted(debts_by_rank.items())},
            'all_tensor_fractional_reserve': '4*lambda+3',
            'all_tensor_amplification_bound': '48+48*2^ceil(lambda/2)+144*2^(4*lambda)',
            'all_tensor_magnitude_guard_bits': '4*lambda+8',
            'all_tensor_envelope_checks': len(slacks),
            'minimum_envelope_slacks': [str(min(s[i] for s in slacks)) for i in range(3)]}
