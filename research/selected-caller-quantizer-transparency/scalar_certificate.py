"""Every literal local scalar product, chart cut, and owned lifetime."""
from collections import Counter
from fractions import Fraction
import hashlib

from common import debt, digest, encoded, integer, mass, rational, require, row_record, span


def certify(word, source_result, coefficient_bits=4):
    integer(coefficient_bits, 0, 4, 'coefficient certificate budget')
    scale = 1 << coefficient_bits
    require(set(word) == {'schema', 'public', 'owned_fields', 'initial', 'final',
                         'frames', 'live', 'ports', 'program'}, 'complete word grammar')
    require(word['schema'] == 'p104-accumulated-block-composition/2', 'selected word schema')
    public = integer(word['public'], 770, 770, 'public fields')
    owned = integer(word['owned_fields'], 29, 29, 'owned labels')
    require(len(word['program']) == 22803 and len(word['initial']) == len(word['final']) == public,
            'complete source chronology and endpoints')
    require(len(word['live']) == len(word['ports']) == 104 and len(set(word['live'])) == 104,
            'ordered live ports')
    for role in word['live']:
        integer(role, 0, 111, 'X role')
    spaces = [span(frame) for frame in word['frames']]
    for frame in word['initial']+word['final']:
        integer(frame, 0, len(spaces)-1, 'source chart index')
    rows = [{i: Fraction(1)} for i in range(public)]+[{} for _ in range(owned)]
    grid = [{i: scale} for i in range(public)]+[{} for _ in range(owned)]
    current = word['initial'][:]+[None]*owned
    live = set()
    maximum_debt = maximum_product_debt = peak = lifetimes = erased_nonzero = 0
    maximum_mass = maximum_product_mass = Fraction(0)
    products = divisions = visits = 0
    first_witness = None
    counts, paid = Counter(), Counter()
    cuts = hashlib.sha256()
    for index, event in enumerate(word['program']):
        require(type(event) is list and len(event) >= 2, 'literal instruction')
        kind, target = event[:2]
        require(type(kind) is str, 'opcode type')
        integer(target, 0, public+owned-1, 'target role')
        require(target < public or target in live or kind == 'INIT', 'no freed owned read/write')
        counts[kind] += 1
        product, grid_product = {}, {}
        prior_erased = None
        if kind == 'MOVE':
            require(len(event) == 5, 'MOVE arity')
            _, _, old, new, private = event
            integer(old, 0, len(spaces)-1, 'MOVE old chart')
            integer(new, 0, len(spaces)-1, 'MOVE new chart')
            require(type(private) is bool and private == (target in live) and current[target] == old,
                    'MOVE source chart and ownership')
            require(spaces[new] < spaces[old] if private else spaces[old] < spaces[new],
                    'strict selected nested MOVE')
            paid[abs(len(word['frames'][new])-len(word['frames'][old]))] += 1
            current[target] = new
        elif kind in ('INIT', 'CLEAR'):
            require(len(event) == 3 and target >= public, 'owned reset arity/role')
            integer(event[2], 0, len(spaces)-1, 'owned reset chart')
            if kind == 'INIT':
                require(target not in live and current[target] is None, 'fresh owned lifetime')
                live.add(target)
                current[target] = event[2]
                peak = max(peak, len(live))
                lifetimes += 1
            else:
                require(target in live and current[target] == event[2], 'current owned CLEAR')
                prior_erased = row_record(rows[target])
                erased_nonzero += bool(rows[target])
                live.remove(target)
                current[target] = None
            rows[target], grid[target] = {}, {}
        else:
            require(kind in ('ADD', 'COPY', 'SCALE') and len(event) == (4 if kind == 'SCALE' else 5),
                    'scalar opcode/arity')
            coefficient, chart = rational(event[-2]), event[-1]
            integer(chart, 0, len(spaces)-1, 'scalar chart')
            require(current[target] == chart and abs(coefficient.numerator) <= 16
                    and coefficient.denominator <= 16, 'bounded scalar and destination chart')
            source = target if kind == 'SCALE' else integer(event[2], 0, public+owned-1, 'source role')
            require(current[source] == chart and (source < public or source in live), 'source common chart')
            if kind != 'SCALE':
                require(source != target, 'distinct scalar source')
            if kind == 'COPY':
                require(target in live and not rows[target], 'COPY into owned zero')
            product = {k: coefficient*v for k, v in rows[source].items()}
            for key, value in grid[source].items():
                numerator = coefficient.numerator*value
                require(numerator % coefficient.denominator == 0, 'pre-product coefficient division at '+str(index))
                grid_product[key] = numerator//coefficient.denominator
                divisions += 1
            require(product == {k: Fraction(v, scale) for k, v in grid_product.items()}, 'independent product representation')
            products += len(product)
            product_debt = debt(product)
            if product_debt > maximum_product_debt:
                maximum_product_debt = product_debt
                first_witness = [index, 'product', row_record(product)]
            maximum_product_mass = max(maximum_product_mass, mass(product))
            if kind == 'ADD':
                for key in rows[target].keys() | product.keys():
                    value = rows[target].get(key, 0)+product.get(key, 0)
                    if value:
                        rows[target][key] = value
                    else:
                        rows[target].pop(key, None)
                for key, value in grid_product.items():
                    total = grid[target].get(key, 0)+value
                    if total:
                        grid[target][key] = total
                    else:
                        grid[target].pop(key, None)
            else:
                rows[target], grid[target] = product, grid_product
        require(rows[target] == {k: Fraction(v, scale) for k, v in grid[target].items()}, 'all stored cuts agree independently')
        maximum_debt = max(maximum_debt, debt(rows[target]))
        maximum_mass = max(maximum_mass, mass(rows[target]))
        visits += len(rows[target])
        cuts.update(encoded([index, kind, target, current[target], row_record(rows[target]),
                             row_record(product), prior_erased]))
    require(not live and current == word['final']+[None]*owned, 'complete chart/owned return')
    for target, row in enumerate(rows):
        expected = {target: Fraction(1)} if target < public else {}
        if target-112 in word['live']:
            expected[target-112] = Fraction(1)
        require(row == expected, 'integral complete public endpoint')
    source = source_result['local']
    require((lifetimes, peak) == (source['owned_lifetimes'], source['peak_owned_fields']), 'source owned chronology')
    require(dict(paid) == {int(k): v for k, v in source['paid'].items()}, 'complete local native invoice')
    require(maximum_debt <= coefficient_bits and maximum_product_debt <= coefficient_bits and maximum_mass <= 850
            and maximum_product_mass <= 504, 'proved local source guard/range')
    return {'events': len(word['program']), 'coefficient_bits': coefficient_bits, 'counts': dict(sorted(counts.items())),
            'stored_debt': maximum_debt, 'product_debt': maximum_product_debt,
            'maximum_stored_mass': str(maximum_mass), 'maximum_product_mass': str(maximum_product_mass),
            'stored_term_visits': visits, 'product_terms': products, 'checked_integer_divisions': divisions,
            'owned_lifetimes': lifetimes, 'peak_live_owned': peak, 'nonzero_ideal_clears': erased_nonzero,
            'first_maximum_product_witness': first_witness, 'complete_cut_sha256': cuts.hexdigest(),
            'integer_public_endpoints': True, 'endpoint_sha256': digest([row_record(r) for r in rows])}
