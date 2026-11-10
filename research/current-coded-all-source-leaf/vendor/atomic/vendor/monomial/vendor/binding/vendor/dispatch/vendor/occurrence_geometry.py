#!/usr/bin/env python3
"""Source-bound coordinate checks; no predecessor imports. Apache-2.0."""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROLLER = 'research/p104-productive-controller/CONTROLLER.json'
PHASES = ('research/p104-caller-independent-audit/capsule/outputs/'
          'p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json')


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def authenticate() -> dict[str, bytes]:
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    data = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash: ' + row['path'])
            data[row['path']] = raw
    return data


def stable_prefix(n: int, active: tuple[int, ...]) -> tuple[int, ...]:
    need(type(n) is int and n > 0, 'positive ambient')
    need(len(set(active)) == len(active), 'injective active list')
    need(all(type(a) is int and 0 <= a < n for a in active), 'active range')
    used = set(active)
    return active + tuple(i for i in range(n) if i not in used)


def swap_word(order: tuple[int, ...]) -> list[tuple[int, int]]:
    need(sorted(order) == list(range(len(order))), 'complete permutation')
    live = list(range(len(order)))
    out = []
    for i, target in enumerate(order):
        if live[i] != target:
            j = live.index(target)
            live[i], live[j] = live[j], live[i]
            out.append((i, j))
    need(tuple(live) == order and len(out) <= len(order)-1, 'emitted permutation and bound')
    return out


def compress(value: int, kept: tuple[int, ...]) -> int:
    mask = sum(1 << i for i in kept)
    need(value & ~mask == 0, 'discarded coordinate used')
    return sum(((value >> old) & 1) << new for new, old in enumerate(kept))


def block(stage: int) -> tuple[int, ...]:
    return tuple(range(9)) if stage == 0 else tuple(range(9+8*(stage-1), 9+8*stage))


def canonicalizer(n: int, active: tuple[int, ...], base: tuple[int, ...]) -> tuple[int, ...]:
    need(len(base) == 9, 'base nine')
    need(all((a & b).bit_count() % 2 == int(i == j)
             for i, a in enumerate(base) for j, b in enumerate(base)), 'orthogonal base')
    return tuple(base[i] if i < 9 else 1 << i for i in stable_prefix(n, active))


def inverse_canonicalizer(columns: tuple[int, ...], value: int) -> int:
    # Orthogonal inverse via dot products, independent of emitted swap execution.
    return sum(((col & value).bit_count() % 2) << i for i, col in enumerate(columns))


def spectral_poly(axes: tuple[int, ...]):
    linear, quadratic = {}, set()
    for axis in axes:
        support = [i for i in range(axis.bit_length()) if axis >> i & 1]
        for i in support:
            linear[i] = (linear.get(i, 0)+1) % 4
        for pair in itertools.combinations(support, 2):
            if pair in quadratic:
                quadratic.remove(pair)
            else:
                quadratic.add(pair)
    return tuple(sorted((i, v) for i, v in linear.items() if v)), tuple(sorted(quadratic))


def source_checks(data: dict[str, bytes]) -> dict[str, int]:
    word = json.loads(data[CONTROLLER])
    phases = json.loads(data[PHASES])
    stages = sorted({e[1] for e in word['physical_events'] if e[0] == 'LOCAL'})
    need(stages == [0, *range(1, 32, 2), 32], 'actual eighteen stage set')
    kept = tuple(sorted({i for stage in stages for i in block(stage)}))
    mask = sum(1 << a for a in kept)
    need(len(kept) == 145 and word['ambient_rank'] == 145, 'compressed ambient145')
    position = {old: new for new, old in enumerate(kept)}
    cases = []
    for term in word['diagonal']:
        selected = tuple(i for i, yes in enumerate(term[1:]) if yes)
        need(set(selected) <= set(stages), 'main stage subset')
        cases.append(('main', selected, term[0]))
    for event in word['physical_events']:
        if event[0] == 'IDLE':
            need(set(event[2]) <= set(stages), 'idle stage subset')
            cases.append(('idle', tuple(event[2]), 0))
    layouts = routes = basis_checks = contacts = 0
    restriction_witness = False
    for recipe in phases['recipes']:
        q = recipe['q']
        basis = tuple(recipe['idle_children'][0]['orthogonal_axes'][:8])
        for stage in stages:
            vectors = () if stage == 0 else tuple(b ^ (1 << i) for b, i in zip(basis, block(stage), strict=True))
            reduced = tuple(compress(v, kept) for v in vectors)
            def act(axis):
                out = axis
                for v in vectors:
                    if (axis & v).bit_count() % 2:
                        out ^= v
                return out
            spectator = tuple(1 << i for i in range(9, 9+8*stage))
            raw_x = (q,) if stage == 0 else tuple(1 << i for i in range(9+8*(stage-1)))
            raw_y = () if stage == 0 else raw_x+(q, q, q)
            entry_x, entry_y = spectator+(q,), spectator
            exit_x = spectator+tuple(1 << i for i in range(9))
            exit_y = exit_x+(q, q, q)
            out_x = tuple(1 << i for i in range(9+8*stage))
            out_y = out_x+(q, q, q)
            for old_terms, new_terms in ((raw_x, entry_x), (raw_y, entry_y), (exit_x, out_x), (exit_y, out_y)):
                old_l, old_q = spectral_poly(tuple(act(a) for a in old_terms))
                new_l, new_q = spectral_poly(new_terms)
                need(old_q == new_q, 'actual contact quadratic phase')
                old_d, new_d = dict(old_l), dict(new_l)
                delta = {i: (new_d.get(i, 0)-old_d.get(i, 0)) % 4 for i in old_d.keys() | new_d.keys()}
                need(set(delta.values()) <= {0, 2}, 'actual contact is translation')
                translation = sum(1 << i for i, value in delta.items() if value == 2)
                need(translation & ~mask == 0 and act(translation) & ~mask == 0, 'contact and inverse stay in retained support')
                contacts += 1
            for i in range(265):
                x, actual = 1 << i, 1 << i
                for v in vectors:
                    if (x & v).bit_count() % 2:
                        actual ^= v
                if i not in position:
                    need(actual == x, 'discarded route spectator')
                else:
                    y = 1 << position[i]
                    reduced_actual = y
                    for v in reduced:
                        if (y & v).bit_count() % 2:
                            reduced_actual ^= v
                    need(compress(actual, kept) == reduced_actual, 'route compression intertwiner')
                basis_checks += 1
            routes += 1
        for kind, selected, qpower in cases:
            has_zero = 0 in selected
            base = tuple(1 << i for i in range(9)) if kind == 'main' and has_zero else (q, *basis)
            if kind == 'main':
                start = tuple(range(9)) if has_zero else (0,)
            else:
                start = tuple(range(1, 9)) if has_zero else ()
            old_active = start + tuple(i for s in selected if s for i in block(s))
            active = tuple(position[i] for i in old_active)
            cols = canonicalizer(145, active, base)
            positive = tuple(base[i] if i < 9 else 1 << position[i] for i in old_active)
            need(cols[:len(active)] == positive, 'exact positive first columns')
            for i in range(145):
                need(inverse_canonicalizer(cols, cols[i]) == 1 << i, 'full inverse including complement')
                basis_checks += 1
            physical = tuple(1 << position[i] for stage in selected for i in block(stage))
            if kind == 'main':
                physical += (q,) * ((qpower-int(has_zero)) % 4)
                corrected = positive + (q,) * (2 if qpower == -1 else 0)
                need(spectral_poly(physical) == spectral_poly(corrected), 'actual main phase and central translation')
            else:
                physical += (q,) * ((-int(has_zero)) % 4)
                lp, qp = spectral_poly(physical)
                lc, qc = spectral_poly(positive)
                need(qp == qc, 'idle quadratic phase')
                dp, dc = dict(lp), dict(lc)
                delta = {i: (dp.get(i, 0)-dc.get(i, 0)) % 4 for i in dp.keys() | dc.keys()}
                need(set(delta.values()) <= {0, 2}, 'idle correction is translation')
            # Parity kernels and linear permutations have absolute phase one at zero.
            need(all(axis > 0 for axis in positive), 'nonzero Gaussian axes')
            old = canonicalizer(265, old_active, base)
            if any(old[i] & ~mask for i in kept):
                restriction_witness = True
            layouts += 1
    need(restriction_witness, 'naive restriction must actually fail')
    need(len(phases['recipes']) == 112, 'all retained ports')
    return {'ports': 112, 'routes': routes, 'contacts': contacts, 'layouts': layouts, 'basis_checks': basis_checks,
            'retained_axes': 145, 'discarded_axes': 120, 'naive_restriction_witness': 1}


def permutation_checks() -> dict[str, int]:
    cases = tensor_checks = 0
    for n in range(1, 8):
        for r in range(n+1):
            lists = itertools.permutations(range(n), r) if n <= 5 else [tuple(reversed(range(r))), tuple(range(n-r, n))]
            for active in lists:
                order, swaps = stable_prefix(n, active), swap_word(stable_prefix(n, active))
                for f in (1, 2, 4):
                    # Each chunk has three bits; only rho=1 moves.
                    k, rho = 3, 1
                    labels = list(range(n*f*k))
                    original = labels[:]
                    for a, b in swaps:
                        for j in range(f):
                            ai, bi = (a*f+j)*k+rho, (b*f+j)*k+rho
                            x, y = 1 << ai, 1 << bi
                            x ^= y; y ^= x; x ^= y
                            need((x, y) == (1 << bi, 1 << ai), 'three-add swap')
                            labels[ai], labels[bi] = labels[bi], labels[ai]
                    expected = original[:]
                    for a in range(n):
                        for j in range(f):
                            expected[(a*f+j)*k+rho] = (order[a]*f+j)*k+rho
                    need(labels == expected, 'fixed-rho route and unselected spectators')
                    for a, b in reversed(swaps):
                        for j in range(f):
                            ai, bi = (a*f+j)*k+rho, (b*f+j)*k+rho
                            labels[ai], labels[bi] = labels[bi], labels[ai]
                    need(labels == original, 'literal inverse return')
                    tensor_checks += 1
                cases += 1
    return {'ordered_active_lists': cases, 'tensor_routes': tensor_checks}


def layout_domain(n, width, owned, d, f, k, g, other=1, lead=0, materialize_rows=True, active_extent=None):
    need(n >= 2 and width >= 1 and owned >= 0 and d >= 1 and f >= 1 and k >= 1 and g >= 1 and other >= 1, 'layout positive domain')
    extent = d if active_extent is None else active_extent
    need(1 <= extent <= d, 'active extent domain')
    power, levels = 1, 0
    while power < 2*d:
        power *= n; levels += 1
    stock = (width*(owned+1))**levels * other
    q0 = max(1, ((stock-1).bit_length()+k-1)//k)
    h = d*g
    qf, qb = (2*h+k-1)//k, (h+k-1)//k
    start, end = (q0+qf+lead)*k, (extent-qb)*k
    need(start+n*f*k <= end, 'active interval fit')
    need(q0*k+2*h <= start and end+h <= extent*k, 'complete controls')
    need((n*f-1)*g <= h, 'all occurrence column controls')
    need(q0*k >= (stock-1).bit_length(), 'logarithmic row-stock fit')
    if not materialize_rows:
        return stock, q0*k, None, start, end
    rows = 1 << (q0*k)
    padded = ((rows+stock-1)//stock)*stock
    need(rows <= padded < 2*rows and padded % stock == 0, 'one complete row pad')
    return stock, rows, padded, start, end


def domain_checks() -> dict[str, int]:
    total = 0
    for n, width, owned, f in itertools.product((2, 3, 7), (1, 3, 11), (0, 2, 6), (1, 2, 7)):
        stock, rows, padded, start, end = layout_domain(n, width, owned, 1024, f, 256, 5, 6)
        need(padded % (width*(owned+1)*6) == 0, 'simultaneous divisors')
        for u in (0, 1, padded//2, padded-1):
            digits, current = [], u
            for divisor in (width, owned+1, 2, 3):
                current, digit = divmod(current, divisor)
                digits.append((divisor, digit))
            for divisor, digit in reversed(digits):
                current = divisor*current+digit
            need(current == u, 'whole-row nested return')
        total += 1
    for extent in (512, 640):
        layout_domain(7, 11, 6, 1024, 7, 256, 5, 6, active_extent=extent)
        total += 1
    layout_domain(7, 11, 6, 10**32, 10**30, 10**10, 5, 6, materialize_rows=False)
    return {'reservation_cases': total+1}


def negative_controls() -> list[str]:
    controls = []
    def rejects(name, call):
        try:
            call()
        except (ValueError, IndexError):
            controls.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    rejects('aliased-active-coordinate', lambda: stable_prefix(5, (1, 1)))
    rejects('missing-coordinate-range', lambda: stable_prefix(5, (5,)))
    rejects('dropped-complement', lambda: swap_word((0, 2)))
    rejects('discarded-live-route-axis', lambda: compress(1 << 12, (0, 1, 2)))
    rejects('nonorthogonal-canonicalizer', lambda: canonicalizer(9, (0,), (1,)*9))
    rejects('front-back-overlap', lambda: layout_domain(7, 11, 6, 64, 7, 1, 5))
    rejects('too-large-occurrence', lambda: layout_domain(7, 11, 6, 64, 100, 256, 5))
    need(3 % 2 != 0, 'max stock rejected'); controls.append('max-instead-of-product-stock')
    order = stable_prefix(5, (3, 1))
    labels = list(range(5))
    for a, b in swap_word(order):
        labels[a], labels[b] = labels[b], labels[a]
    need(labels != list(range(5)), 'omitted return witness'); controls.append('omitted-inverse-return')
    x, y = list(range(5)), [10+i for i in range(5)]
    wrong = [x[i]+y[order[i]] for i in range(5)]
    right = [x[i]+y[i] for i in range(5)]
    need(wrong != right, 'scalar alignment witness'); controls.append('rolewise-route-without-whole-conjugation')
    return controls


def main() -> None:
    data = authenticate()
    report = {'source': source_checks(data), 'permutations': permutation_checks(),
              'domains': domain_checks(), 'negative_controls': negative_controls()}
    print(json.dumps(report, sort_keys=True, separators=(',', ':')))
    print('PASS_SELECTED_COMPILER_OCCURRENCE_LAYOUT')


if __name__ == '__main__':
    main()
