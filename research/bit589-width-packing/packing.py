# SPDX-License-Identifier: Apache-2.0
"""Width packing of the selected PR589 nine-stage bit hosting.

Usage: packing.py OUT.json

1. Derives the idle-slot model of the frozen nine-stage hosting selection from the
   pinned PR589 record (profile, local histogram) and its selection file.
2. Certifies that no other no-bank placement of the 439 width-8 residuals per call
   raises the bit endpoint on the 10^-24 grid (per-unit cost argument at c0 + 10^-24).
3. Prices width-7 residuals (hyperplane-ended or rank-one-entrance helpers), which fill
   the 7k-capacity slots exactly, with a two-sided bracket for the local change.
Standard library only; the rational engines are the pinned ones of the selected assembly.
"""
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = json.loads((HERE / 'SOURCES.json').read_text())
M_BIT = 64            # 1 + 7L with L = 9 stages
T = 32                # replicas
STAGES = 9


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def pinned_json(key):
    src = SOURCES['inputs'][key]
    data = (ROOT / src['path']).read_bytes()
    require(sha256(data) == src['sha256'], f'{key}: digest mismatch')
    return json.loads(data)


def engine(name):
    path = ROOT / SOURCES['engines']['directory'] / (name + '.py')
    require(sha256(path.read_bytes()) == SOURCES['engines'][name + '.py'], f'engine pin {name}')
    spec = importlib.util.spec_from_file_location('pinned_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOMENT, BASE_TWO, OUTER = engine('moment'), engine('base_two_moment'), engine('outer')


def cj(c):
    return {str(k): c[k] for k in sorted(c) if c[k]}


# ---------------------------------------------------------------------------
# 1. Slot model.

def slot_model(record, selection):
    word, nine = record['word'], record['nine']
    v, R = word['v'], word['R']
    require(nine['bit']['live'] == 2 * 4 * v * T, 'live stock is 2KvT')
    H = Counter({int(k): n for k, n in nine['profile'].items()})
    local = Counter({int(k): n for k, n in word['local_histogram'].items()})
    calls = STAGES * T
    idle = Counter(H)
    idle.subtract(Counter({r: n * calls for r, n in local.items()}))
    idle = +idle
    require(all(n % T == 0 for n in idle.values()), 'idle profile is replica-uniform')
    idle_rep = Counter({r: n // T for r, n in idle.items()})
    pats = selection['bit']['patterns']
    fams = Counter()
    hosted = {}
    for s, widths, count in pats:
        require(all(w == 8 for w in widths), 'every PR589 residual has width 8')
        fams[s] += count
        hosted.setdefault(s, []).append((8 * len(widths), count))
    require(set(fams.values()) == {2 * v}, 'each slot index holds one pair (2v families)')
    st = Counter()
    for s, w, stage, count in selection['bit']['stages']:
        st[s] += w * count
    require(st == Counter({s: sum(h * n for h, n in L) for s, L in hosted.items()}), 'stage and pattern totals agree')
    require(sum(st.values()) == 8 * STAGES * R, 'every residual is hosted, no banks')
    # Capacity of each slot index: a multiple of 7 whose remainders reproduce the idle profile.
    ranks = set(idle_rep)
    options = {}
    for s, L in hosted.items():
        options[s] = [c for c in range(7, 8 * 7, 7) if all(c >= h and c - h in ranks for h, _ in L)]
    solutions = []

    def search(keys, chosen):
        if not keys:
            rem = Counter()
            for s, c in chosen.items():
                for h, n in hosted[s]:
                    rem[c - h] += n
            if rem == idle_rep:
                solutions.append(dict(chosen))
            return
        for c in options[keys[0]]:
            search(keys[1:], {**chosen, keys[0]: c})
    search(sorted(hosted), {})
    require(len(solutions) == 1, f'capacity model is not unique: {solutions}')
    caps = solutions[0]
    pending = sum(c * fams[s] for s, c in caps.items())
    # Coverage: data families get 7 coordinates per invocation plus one free coordinate.
    require(pending == 2 * v * (M_BIT - 1 - 7 * 3) + 6 * v * (M_BIT - 1 - 7 * 2), 'pending capacity matches coverage')
    slots = Counter()
    for s, c in caps.items():
        slots[c] += fams[s]
    return dict(v=v, R=R, calls=calls, H=H, local=local, idle_rep=idle_rep, caps=caps, slots=slots,
                pending=pending, deficit=M_BIT * nine['bit']['live'] - sum(r * n for r, n in H.items()))


# ---------------------------------------------------------------------------
# Certified values of g(r) = r (m/r)^c with the engine's outward-rounded series.

def g_interval(r, c):
    lo_l, hi_l = MOMENT.logarithm(Q(M_BIT, r))
    lo_e, hi_e = MOMENT.exponential(c * lo_l, c * hi_l)
    return r * lo_e, r * hi_e


def width8_optimality(model, c_star):
    """Every no-bank width-8 placement has the same number of idle children, one per slot.
    Its idle part exceeds the selected one by sum_slots u_s * rho(t_s, u_s), where u_s is the
    number of unused width-8 places. If rho is minimal only at (42, 5), the selected placement,
    which spends all slack on fully idle 42-slots, minimizes the moment at c_star."""
    rmin = {c: c % 8 for c in model['slots']}
    umax = {c: c // 8 for c in model['slots']}
    require(all(rmin[c] > 0 for c in rmin), 'no slot capacity is divisible by 8')
    slack = sum(umax[c] * n for c, n in model['slots'].items()) - STAGES * model['R']
    require(slack == 45, 'slack per replica')
    sel = Counter({c: n for c, n in model['idle_rep'].items()})
    require(sel == Counter({7: 666, 6: 444, 4: 444, 2: 435, 42: 9}), 'selected remainders')
    rho = {}
    for c in sorted(model['slots']):
        for u in range(1, umax[c] + 1):
            a_lo, a_hi = g_interval(rmin[c] + 8 * u, c_star)
            b_lo, b_hi = g_interval(rmin[c], c_star)
            rho[(c, u)] = ((a_lo - b_hi) / u, (a_hi - b_lo) / u)
    best = rho[(42, 5)]
    others = {k: v for k, v in rho.items() if k != (42, 5)}
    require(all(best[1] < lo for lo, _ in others.values()), 'fully idle 42-slots are the unique cheapest units')
    second = min(others, key=lambda k: others[k][0])
    return dict(slack_units_per_replica=slack, minimal_remainders={str(c): rmin[c] for c in sorted(rmin)},
                per_unit_cost_at_c_star={f'{c}:{u}': [str(Decimal(lo.numerator) / Decimal(lo.denominator))[:32],
                                                       str(Decimal(hi.numerator) / Decimal(hi.denominator))[:32]]
                                         for (c, u), (lo, hi) in sorted(rho.items())},
                cheapest='capacity 42, fully idle (u = 5)', runner_up=f'capacity {second[0]}, u = {second[1]}',
                margin_lower_bound=str(Decimal((others[second][0] - best[1]).numerator) /
                                       Decimal((others[second][0] - best[1]).denominator))[:24])


def width7_idle(model):
    """All residuals of width 7: exact fits; the slack majorization optimum (6,...,6,rest)."""
    units = sum((c // 7) * n for c, n in model['slots'].items()) - STAGES * model['R']
    q, rest = divmod(units, 6)
    out = Counter({42: q})
    if rest:
        out[7 * rest] += 1
    return units, out


def width7_partial_idle(model, k):
    """k converted helpers per call (9k width-7 residuals per replica), constructive placement:
    width-7 residuals fill empty capacity-7 slots exactly; width-8 residuals keep the minimal
    remainders, and all width-8 slack goes to fully idle 42-slots (the certified cheapest units),
    with at most one partially idle 42-slot."""
    slots = model['slots']
    require(STAGES * k <= slots[7], 'this construction places width-7 residuals in 7-slots only')
    slack = 45 + STAGES * k
    full, part = divmod(slack, 5)
    idle = Counter({7: slots[7] - STAGES * k, 6: slots[14], 4: slots[28], 42: full})
    rest42 = slots[42] - full - (1 if part else 0)
    require(rest42 >= 0, 'enough 42-slots')
    idle[2] += rest42
    if part:
        idle[2 + 8 * part] += 1
    hosted8 = sum((c // 8) * n for c, n in slots.items()) - slack
    require(hosted8 == STAGES * (model['R'] - k), 'every width-8 residual hosted')
    return +idle


def local_bracket(local, k):
    """Remove one unit from one child for each of k converted helpers per call."""
    opt = Counter(local)
    require(opt[1] >= k, 'enough rank-one children')
    opt[1] -= k
    pes = Counter(local)
    left = k
    for r in sorted(local, reverse=True):
        take = min(left, local[r])
        pes[r] -= take
        if r > 1:
            pes[r - 1] += take
        left -= take
        if not left:
            break
    require(left == 0, 'enough children')
    return +opt, +pes


def endpoint(H, W):
    b = Q(MOMENT.certify(H, M_BIT, W, True)['lower'])
    for z, accept in ((b, True), (b + Q(1, 10 ** 24), False)):
        lo, hi = MOMENT.moment(H, M_BIT, W, z, True)
        blo, bhi = BASE_TWO.moment(M_BIT, W, list(H.items()), z)
        flo, fhi = BASE_TWO.moment(M_BIT, W, [(1, 32 * M_BIT * M_BIT * sum(H.values()))], z)
        blo += flo / 10 ** 16
        bhi += fhi / 10 ** 16
        require((hi < 1 and bhi < 1) if accept else (lo > 1 and blo > 1), 'bit endpoint certification')
    return b


def kappa_cap(c):
    """kappa of the selected T37 outer witness when the bit side binds (complex b = 2c)."""
    ow = SOURCES['outer_witness']
    eta = beta = Q(ow['eta'])
    bb = 2 * c
    s = min(c, (1 - beta) * bb) - Q(1, 10 ** 27)
    chain = [Q(ow['bootstrap_start'])]
    for _ in range(ow['bootstrap_steps']):
        old = chain[-1]
        a = (1 - s) * s + s * old
        require(old < a < s < 1 - a, 'bootstrap step')
        chain.append(a)
    q = chain[-1] * (1 - 2 * eta)
    ticks = (1 - eta) * q / (1 + q) * 10 ** 18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10 ** 18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10 ** 6) - Q(51 * 20161, 25)}}
    out = OUTER.assembly(chain[-1], bb, bridge, k, eta=eta, beta=beta)
    require(all(x > 0 for x in out['strict_constraints'].values()), 'outer inequalities')
    try:
        OUTER.assembly(chain[-1], bb, bridge, k + Q(1, 10 ** 18), eta=eta, beta=beta)
    except AssertionError:
        return k
    raise ValueError('next grid point accepted')


def dec(x, prec=40):
    with localcontext() as ctx:
        ctx.prec = prec
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def main():
    record = pinned_json('bit_record')
    selection = pinned_json('selection')
    assembly = pinned_json('selected_assembly')
    require(SOURCES['inputs']['bit_record']['sha256'] == assembly['input_sha256']['package:inputs/PR589-EXPECTED.json'],
            'bit record is the input of the selected assembly')
    model = slot_model(record, selection)
    W = record['nine']['bit']['live']
    H0 = dict(model['H'])
    c0 = endpoint(H0, W)
    require(str(c0) == assembly['bit_lower'] == record['nine']['bit_lower'], 'baseline bit endpoint')
    c_star = c0 + Q(1, 10 ** 24)
    optimality = width8_optimality(model, c_star)
    calls = model['calls']
    rows = {}

    def add(key, local, idle_rep, description):
        H = Counter({r: n * calls for r, n in local.items()})
        H.update({r: n * T for r, n in idle_rep.items()})
        H = +H
        require(M_BIT * M_BIT > 2 * max(H) ** 2, f'{key}: halving guard')
        require(sum(r * n for r, n in H.items()) == sum(r * n for r, n in H0.items()), f'{key}: rank mass changes')
        c = endpoint(dict(H), W)
        k = kappa_cap(c)
        rows[key] = dict(description=description, profile=cj(H), children=sum(H.values()), bit_lower=str(c),
                         bit_decimal=dec(c), bit_gain_percent=dec(100 * (c - c0) / c0, 12),
                         bit_bound_kappa_cap=str(k), bit_bound_kappa_cap_decimal=dec(k))

    add('selected', model['local'], model['idle_rep'], 'Selected PR589 profile (reproduced exactly).')
    units, idle7 = width7_idle(model)
    opt, pes = local_bracket(model['local'], model['R'])
    add('width7_all_optimistic', opt, idle7,
        'All 439 helpers width 7; each removes one rank-one child; slot-exact packing with all slack in '
        'fully idle 42-slots.')
    add('width7_all_pessimistic', pes, idle7,
        'Same packing; each converted helper trims one of the 439 largest distinct local children by one.')
    for k in (1, 10, 37, 74):
        opt_k, pes_k = local_bracket(model['local'], k)
        idle_k = width7_partial_idle(model, k)
        add(f'width7_k{k}_optimistic', opt_k, idle_k,
            f'{k} helpers per call width 7 (each removes one rank-one child); their residuals fill '
            f'empty 7-slots; width-8 slack in fully idle 42-slots.')
        add(f'width7_k{k}_pessimistic', pes_k, idle_k,
            f'Same placement; each of the {k} converted helpers trims one of the largest distinct children.')
    for cap in (42, 45):
        mass = sum(r * n for r, n in model['idle_rep'].items())
        q, rest = divmod(mass, cap)
        idle = Counter({cap: q})
        if rest:
            idle[rest] += 1
        add(f'width8_free_concentration_{cap}', model['local'], idle,
            f'Relaxation: the width-8 idle mass placed in children of rank {cap}, ignoring slots and windows.')
    result = dict(status='PASS_BIT589_WIDTH_PACKING', base_commit=SOURCES['base_commit'],
                  slot_model=dict(capacity_by_slot_index={str(s): c for s, c in sorted(model['caps'].items())},
                                  slots_per_replica=cj(model['slots']), pending_per_replica=model['pending'],
                                  idle_per_replica=cj(model['idle_rep']), deficit=model['deficit'],
                                  deficit_identity='live - 63*calls = %d' % (W - 63 * calls)),
                  width8_optimality=optimality,
                  width7=dict(slack_units_per_replica=units, optimal_idle_per_replica=cj(idle7),
                              idle_children_per_replica=sum(idle7.values()),
                              selected_idle_children_per_replica=sum(model['idle_rep'].values())),
                  scenarios=rows)
    require(model['deficit'] == W - 63 * calls, 'deficit identity')
    with open(sys.argv[1], 'w') as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + '\n')
    print(result['status'])
    print('slots per replica', cj(model['slots']), 'slack', optimality['slack_units_per_replica'],
          'runner-up', optimality['runner_up'], 'margin', optimality['margin_lower_bound'])
    for key, row in rows.items():
        print(f"{key:30s} c {row['bit_decimal'][:22]}  gain {row['bit_gain_percent'][:9]}%  "
              f"bit-bound kappa cap {row['bit_bound_kappa_cap_decimal'][:21]}")


if __name__ == '__main__':
    main()
