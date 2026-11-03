"""Cross-checks for the residue certificates, schedules and two price families."""
from fractions import Fraction
from itertools import product
from math import gcd, lcm, prod

from oracles import amount_bills, common_bills, literal_bills, strict_records
from pricing import Menu, exact_prefix, first_periodic_replication, frontier, period_and_floor


def require(condition, message):
    if not condition:
        raise ValueError(message)


def invalid_inputs():
    bad_menus = [[], [(0, 1)], [(True, 1)], [(1, 2), (1, 3)], [(2, 0)], [(3, -1)],
                 [(1, True)], [(1, 1.5)]]
    menu = Menu([(1, 1)])
    probes = [(Menu, (rows,)) for rows in bad_menus]
    probes.extend([(period_and_floor, ([],)), (frontier, ([(0, menu)],)),
                   (first_periodic_replication, ([(True, menu)],)), (frontier, ([(1, menu)], 0)),
                   (menu.optimum, (-1,)), (menu.optimum, (True,))])
    for fn, args in probes:
        try:
            fn(*args)
        except ValueError:
            continue
        raise ValueError("invalid pricing input accepted")
    return len(probes)


def check_witness(rows, n, price, counts):
    require(len(rows) == len(counts) and all(type(k) is int and k >= 0 for k in counts),
            "invalid invocation counts")
    require(sum(w*k for (w, _), k in zip(rows, counts, strict=True)) == n,
            "witness fills the wrong cut")
    require(sum(c*k for (_, c), k in zip(rows, counts, strict=True)) == price,
            "witness charged cost mismatch")


def check_table(widths, losses, modulus, table):
    g = gcd(modulus, *widths)
    for r, label in enumerate(table):
        require((label is None) == (r % g != 0), "wrong reachable residue")
        if label is None:
            continue
        require(label.size % modulus == r, "wrong residue witness")
        check_witness(list(zip(widths, losses, strict=True)), label.size, label.loss, label.counts)
        if r == 0:
            require((label.loss, label.size) == (0, 0), "wrong zero label")
        for width, charge in zip(widths, losses, strict=True):
            dest = table[(r + width) % modulus]
            require((dest.loss, dest.size) <= (label.loss + charge, label.size + width),
                    "residue Bellman inequality")


def check_menu(menu):
    check_table(menu.widths, menu.losses, menu.h, menu.labels)
    check_table(menu.widths, menu.losses, menu.anchor, menu.refined)
    normalized = [menu.widths[i] // menu.h for i in menu.best]
    check_table(normalized, [0] * len(normalized), normalized[0], menu.apery)
    for s, label in enumerate(menu.refined):
        if label is not None:
            require(label.loss == menu.labels[s % menu.h].loss, "refined loss projection")
    require(all((item.loss == 0) == (r == 0)
                for r, item in enumerate(menu.labels) if item is not None), "cheap residue zero set")


def menu_grid():
    menus = targets = holes = literal_vectors = literal_targets = refined_exceptions = 0
    for prices in product(range(4), repeat=5):
        rows = [(w, c) for w, c in enumerate(prices, 1) if c]
        if not rows:
            continue
        menus += 1
        menu = Menu(rows)
        check_menu(menu)
        stop = max(48, menu.threshold + 2*menu.anchor)
        oracle = amount_bills(rows, stop)
        prefix = exact_prefix(menu.widths, menu.prices, stop)
        literal, visited = literal_bills(rows, 12)
        require(literal == oracle[:13], "literal partition oracle differs")
        literal_vectors += visited
        literal_targets += 13
        for n, bill in enumerate(oracle):
            opt = menu.optimum(n, prefix)
            require((None if opt is None else opt[0]) == bill, "single-cut amount oracle")
            if opt is None:
                holes += 1
            else:
                check_witness(rows, n, *opt)
            label = menu.refined[n % menu.anchor]
            if label is not None:
                ideal = menu.density*n + label.loss
                require((bill == ideal) == (n >= label.size), "exact onset of residue")
                refined_exceptions += int(bill != ideal)
            targets += 1
    return dict(menus=menus, amount_targets=targets, unreachable_targets=holes,
                literal_targets=literal_targets, literal_count_vectors=literal_vectors,
                early_exceptions=refined_exceptions)


def direct_crosscheck(raw_cuts, parent, cap=0):
    cuts = [(q, Menu(rows)) for q, rows in raw_cuts]
    period, floor, records = frontier(cuts, parent)
    onset = first_periodic_replication(cuts)
    # Independent upper witness: use the largest minimum-density width at each cut.
    witnesses = []
    for q, rows in raw_cuts:
        density = min(Fraction(c) / w for w, c in rows)
        width = max(w for w, c in rows if Fraction(c) / w == density)
        witnesses.append(width // gcd(width, q))
    upper = lcm(*witnesses)
    start = max([1] + [(m.threshold + q - 1)//q for q, m in cuts])
    stop = max(cap, upper, start + 3*period)
    bills = common_bills(raw_cuts, parent, stop)
    expected = strict_records(bills)
    require([(a, fee) for a, fee, _ in records] == expected, "aggregate Pareto records")
    require(expected[-1][1] == floor, "first floor mismatch")
    for a, fee, schedules in records:
        total = Fraction(0)
        for (q, rows), counts in zip(raw_cuts, schedules, strict=True):
            charge = sum(c*k for (_, c), k in zip(rows, counts, strict=True))
            check_witness(rows, a*q, charge, counts)
            total += charge
        require(total == parent*a*fee, "parent normalization mismatch")
    excess = [None if fee is None else (fee-floor)*parent*a for a, fee in enumerate(bills)]
    mismatches = [a for a in range(1, stop-period+1) if excess[a] != excess[a+period]]
    require(onset == 1 + max(mismatches, default=0), "least common onset")
    zero = ((start + period - 1)//period)*period
    require(excess[zero] == 0, "missing zero excess")
    require(all(excess[zero+t] != 0 for t in range(1, period)), "nonminimal excess period")
    return (period, floor, records, onset, stop, len(mismatches))


def read_case(case):
    return [(q, [(w, Fraction(c)) for w, c in rows]) for q, rows in case['cuts']]


def check_examples(cases):
    results = {}
    for case in cases:
        raw = read_case(case)
        period, floor, records, onset, stop, _ = direct_crosscheck(raw, case['parent'])
        require(period == case['period'], "fixture period")
        require(onset == case['onset'], "fixture onset")
        require(floor == Fraction(case['floor']), "fixture floor")
        require([a for a, _, _ in records] == case['records'], "fixture Pareto records")
        results[case['name']] = dict(period=period, onset=onset, floor=str(floor), checked_through=stop,
                                     records=[dict(a=a, cost=str(c), counts=counts) for a,c,counts in records])
    m = Menu([(1, 10), (5, 5), (6, 7)])
    require(m.optimum(1)[0] == 10 and m.refined[1].size == 6, "early expensive fill")
    t = Menu([(1, 2), (4, 4), (7, 7)])
    require(t.conductor == 18 and [x.size for x in t.refined] == [0, 21, 14, 7],
            "tied widths and cheap gaps")
    records = results['source-6658-mix']['records']
    require(records[0]['counts'] == [(1, 1)], "source mixed invocation witness")
    return results


def intersection_grid():
    # Six menus include differing gcds, tied densities, fractional prices and a thin prefix.
    library = [[(1,10),(5,5),(6,7)], [(1,2),(4,4),(7,7)], [(4,4),(6,6),(10,17)],
               [(2,Fraction(3,2)),(3,2),(5,Fraction(11,3))], [(4,4)], [(2,4),(7,8)]]
    cases = horizons = delayed = 0
    for i, one in enumerate(library):
        for j, two in enumerate(library):
            for variant in range(3):
                q1, q2 = 1 + (i+variant)%5, 1 + (2*j+variant)%7
                raw = [(q1, one), (q2, two)]
                if variant == 2:
                    raw.append((2, library[(i+2*j+1)%len(library)]))
                _, _, _, onset, stop, _ = direct_crosscheck(raw, 1 + variant)
                cases += 1
                horizons += stop
                delayed += int(onset > 1)
    return dict(cases=cases, positive_replications=horizons, delayed_cases=delayed)


def check_families(max_n=48):
    long_points = source_points = replications = 0
    for n in range(2, max_n + 1):
        first_menu = [(1, 2), (n, n+1)]
        second_menu = [(1, 2), (n+1, n+2)]
        cap = n*(n+1)
        bills = common_bills([(1, first_menu), (1, second_menu)], 1, cap)
        predicted = [1, n, n+1] + [k*n for k in range(cap//(2*n-1)+1, n+2)]
        require([a for a, _ in strict_records(bills)] == predicted, "fixed-fee family frontier")
        for a in range(1, cap+1):
            # Sum literal minimum invocation counts, retaining one charge at every invocation.
            calls = a//n + a%n + a//(n+1) + a%(n+1)
            require(bills[a] == 2 + Fraction(calls, a), "fixed-fee bill")
        period, floor, records = frontier([(1, Menu(first_menu)), (1, Menu(second_menu))])
        require(period == cap and [(a,c) for a,c,_ in records] == strict_records(bills),
                "fixed-fee schedule records")
        require(floor == 2 + Fraction(1,n) + Fraction(1,n+1), "fixed-fee floor")
        both = [(n, n+1), (n+1, n+2)]
        old = common_bills([(n, both), (n+1, both)], 1, n+1)
        require(strict_records(old) == [(1,Fraction(2*n+3)), (n+1,Fraction((2*n+1)*(n+2),n+1))],
                "source family with charged invocations")
        long_points += len(predicted)
        source_points += 2
        replications += cap
    return dict(first_n=2, last_n=max_n, long_family_records=long_points,
                long_family_replications=replications, source_family_records=source_points)


def check_onset_family():
    checked = 0
    for b in range(2, 49):
        rows = [(1, 2), (b, b), (b+1, b+1)]
        cheap = Menu(rows)
        solo = [(1, cheap)]
        masked = solo + [(1, Menu([(b, b)]))]
        stop = b*(b-1) + b
        bills = amount_bills(rows, stop)
        require(max(a for a in range(1, stop+1) if bills[a] != a) == b*(b-1)-1,
                "quadratic last gap")
        require(all(bills[a] == a for a in range(b, stop+1, b)), "masked expensive fills")
        require(first_periodic_replication(solo) == b*(b-1) and
                first_periodic_replication(masked) == 1, "onset family masking")
        require(period_and_floor(solo) == (1, 1, b) and
                period_and_floor(masked) == (b, 2, b), "onset family periods")
        checked += stop
    return dict(first_b=2, last_b=48, direct_positive_targets=checked)


def large_period():
    primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    cuts = [(1, Menu([(1, 2), (p, p+1)])) for p in primes]
    period = prod(primes)
    scale = 10**72
    expected_floor = len(primes) + sum(Fraction(1, p) for p in primes)
    require(period_and_floor(cuts) == (period, expected_floor, period), "product period and floor")
    require(first_periodic_replication(cuts) == 1, "product onset")
    replications = [period*scale, period*scale+1] + [period*scale + period//p for p in primes]
    for a in replications:
        total = 0
        for p, (_, menu) in zip(primes, cuts, strict=True):
            price, counts = menu.optimum(a)
            big, small = divmod(a, p)
            require(counts == (small, big) and price == a + big + small, "large exact schedule")
            total += price
        require((total == expected_floor*a) == (a % period == 0), "large zero set")
    return dict(cuts=len(primes), period=period, first_floor=period, first_periodic=1,
                anchor_classes=sum(primes), sampled_replications=len(replications),
                largest_replication=str(max(replications)))
