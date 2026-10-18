#!/usr/bin/env python3
"""Independent exact target-pressure replay of the pinned H6 invoice.

Only the differential-comparison section imports the predecessor calculator.
The oracle constructs each mass/rank term directly, bounds logarithms with
an atanh series and exponentials with a positive Taylor series plus tail.
It proves strict pass/fail at the adjacent helper counts, rather than relying
on a floating root or a bisection monotonicity assertion.
"""

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCALE = 10**60
DISPLAY = 10**24
N, H, BILL = 30960, 17, 12752


def require(ok, message):
    if not ok:
        raise ValueError(message)


def floor_fraction(x):
    return x.numerator // x.denominator


def ceil_fraction(x):
    return -floor_fraction(-x)


def outward(low, high, scale=SCALE):
    return F(floor_fraction(low * scale), scale), F(ceil_fraction(high * scale), scale)


def display_interval(low, high):
    return [floor_fraction(low * DISPLAY), ceil_fraction(high * DISPLAY)]


@lru_cache(None)
def log_interval(x):
    require(x >= 1, "only child contraction ratios >=1 are used")
    shift = 0
    while x >= 2:
        x /= 2
        shift += 1

    def unit(y):
        z = (y - 1) / (y + 1)
        z2 = z * z
        total = F(0)
        power = z
        for j in range(64):
            total += 2 * power / (2 * j + 1)
            power *= z2
        # Every omitted denominator is >=129, bounding the rest geometrically.
        tail = 2 * power / (129 * (1 - z2))
        return total, total + tail

    low, high = unit(x)
    low2, high2 = unit(F(2))
    return outward(low + shift * low2, high + shift * high2)


@lru_cache(None)
def power_interval(base, alpha):
    ll, lu = log_interval(base)
    low, high = alpha * ll, alpha * lu
    require(0 <= low <= high < 1, "positive Taylor interval domain")

    def partial(x):
        term = total = F(1)
        for j in range(1, 33):
            term *= x / j
            total += term
        return total, term

    lower, _ = partial(low)
    upper, last = partial(high)
    # Ratios after the first omitted term are bounded by high/34.
    upper += (last * high / 33) / (1 - high / 34)
    return outward(lower, upper)


def pressure(terms, m, alpha):
    low = high = F(0)
    for mass, rank in terms:
        a, b = power_interval(F(m, rank), alpha)
        low += mass * (a - 1)
        high += mass * (b - 1)
    return low, high


def partition(rank, cap):
    if not rank:
        return []
    count = (rank + cap - 1) // cap
    quotient, remainder = divmod(rank, count)
    return [quotient + (j < remainder) for j in range(count)]


def model(stages):
    m = 16 * stages + 1
    cap = isqrt((m * m - 1) // 2)
    base = [(F(2 * N * stages * 16), 16),
            (F(stages * 17 * 256), 17), (F(stages * 15 * 560), 15)]
    pairs = (stages - 1) // 2
    idle = [32 * (pairs - 1)] if pairs > 1 else []
    for j in range(1, pairs):
        idle.extend([32 * j, 16])
        if pairs - j - 1 > 0:
            idle.append(32 * (pairs - j - 1))
    idle_parts = [partition(rank, cap) for rank in idle]
    for block in idle_parts:
        base.extend((F(2 * N * rank), rank) for rank in block)
    replication, pad = divmod(m, H)
    helper = [(F(stages * rank), rank) for rank in (1, 7, 8, 1)]
    helper.extend((F(stages * rank, replication), rank)
                  for rank in partition(pad, cap))
    stock = (stages - 1) * N
    deficit = stock - stages * BILL
    require(sum(mass for mass, _ in base) == m * stock - deficit,
            "independent base rank-mass equality")
    require(sum(mass for mass, _ in helper) == F(m * stages, replication),
            "independent helper rank-mass equality")
    require(all(0 < rank <= cap for _, rank in base + helper),
            "every child has m^2>2r^2")
    return dict(stages=stages, m=m, cap=cap, replication=replication,
                pad=pad, stock=stock, deficit=deficit, base=base,
                helper=helper, idle_slots=idle, idle_parts=idle_parts)


def boundary(row, target):
    alpha = target / (1 - target)
    bl, bu = pressure(row['base'], row['m'], alpha)
    hl, hu = pressure(row['helper'], row['m'], alpha)
    require(0 < hl <= hu, "strict positive helper pressure proves monotonicity")
    low = (row['deficit'] - bu) / hu
    high = (row['deficit'] - bl) / hl
    count = floor_fraction(low)
    require(count == floor_fraction(high), "certified integer helper boundary")
    pass_slack = (row['deficit'] - bu - count * hu,
                  row['deficit'] - bl - count * hl)
    fail_slack = (row['deficit'] - bu - (count + 1) * hu,
                  row['deficit'] - bl - (count + 1) * hl)
    require(pass_slack[0] > 0 > fail_slack[1], "adjacent strict pass/fail")
    # These controls enforce inclusion of padding and the correct hp profile.
    no_pad = dict(row, helper=row['helper'][:4])
    wrong_hp = dict(row, helper=[(F(row['stages'] * H), H)] + row['helper'][4:])
    no_pad_count = alternate_count(no_pad, alpha)
    wrong_hp_count = alternate_count(wrong_hp, alpha)
    return dict(max_helpers=count, ports_per_helper=str(F(N, count)),
                base_pressure_scaled_1e24=display_interval(bl, bu),
                helper_pressure_scaled_1e24=display_interval(hl, hu),
                threshold_real_interval_scaled_1e24=display_interval(low, high),
                boundary_slack_scaled_1e24=display_interval(*pass_slack),
                next_slack_scaled_1e24=display_interval(*fail_slack),
                controls={'omitted_padding': {'mutated_max_helpers': no_pad_count,
                          'detected': no_pad_count != count},
                          'unsplit_helper': {'mutated_max_helpers': wrong_hp_count,
                          'detected': wrong_hp_count != count}})


def alternate_count(row, alpha):
    bl, bu = pressure(row['base'], row['m'], alpha)
    hl, hu = pressure(row['helper'], row['m'], alpha)
    low, high = (row['deficit'] - bu) / hu, (row['deficit'] - bl) / hl
    require(floor_fraction(low) == floor_fraction(high), "control integer resolves")
    return floor_fraction(low)


def load_predecessor():
    path = ROOT / 'research/h6-banked-breakeven/price_h6.py'
    spec = importlib.util.spec_from_file_location('h6_source_comparison', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    historical = json.loads((ROOT / 'certificates/checkpoints/frontier890.json').read_text())
    packet = json.loads((ROOT / 'research/community-efficient500-audit/packets/1424.json').read_text())
    proposed = re.search(r'\d+\.\d+', packet['title']).group(0)
    targets = [('pr890_rounded', F('0.001661957775')),
               ('pr890_checkpoint', F(historical['kappa'])),
               ('pr1424_pending_title', F(proposed)),
               ('current_selected', F(selected['kappa']))]
    source = load_predecessor()
    expected = {'pr890_rounded': [80558, 89683, 80753],
                'pr890_checkpoint': [80558, 89683, 80753],
                'pr1424_pending_title': [79617, 88409, 79399]}
    results = []
    for name, target in targets:
        rows = []
        for index, stages in enumerate((3, 5, 7)):
            row = model(stages)
            answer = boundary(row, target)
            count = answer['max_helpers']
            if name in expected:
                require(count == expected[name][index], "published boundary agrees")
            require(all(item['detected'] for item in answer['controls'].values()),
                    "invoice mutation controls detected")
            source_counts = {mode: source.breakeven(stages, target, mode)
                             for mode in ('exact', 'float')}
            require(all(value == count for value in source_counts.values()),
                    "predecessor modes agree with independent pressure boundary")
            endpoints = [source.kscaled(stages, count), source.kscaled(stages, count + 1)]
            require(F(endpoints[0]) > target * 10**18 >= F(endpoints[1]),
                    "source lower-endpoint convention matches adjacent boundary")
            # Each source certified interval is narrower than the target margins.
            intervals = [source.b.invoice(N, H, {17: 256, 15: 560}, stages,
                        [16], [1, 7, 8, 1], r, False)
                        ['nominal_kappa_interval_scaled_1e18']
                        for r in (count, count + 1)]
            require(F(intervals[0][0]) > target * 10**18 > F(intervals[1][1]),
                    "both source root intervals lie strictly on the required side")
            answer.update(stages=stages, m=row['m'], deficit=row['deficit'],
                child_cap=row['cap'], stock_replication_factor=row['replication'],
                helper_pad=row['pad'], idle_slots=row['idle_slots'],
                idle_parts=row['idle_parts'], source_mode_counts=source_counts,
                source_root_intervals_scaled_1e18=intervals,
                boundary_stock=str(F(row['stock']) + F(stages * count, row['replication'])))
            rows.append(answer)
        results.append(dict(name=name, target=str(target), rows=rows))
    command = [sys.executable, '-B', str(ROOT / 'research/h6-banked-breakeven/price_h6.py')]
    replay = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    require(replay.stdout == (ROOT / 'research/h6-banked-breakeven/outputs/price_h6.txt').read_text(),
            "source replay equals published price output")
    costs = (ROOT / 'research/niemeier-lattices/COSTS.txt').read_text()
    pauli = F(re.search(r'E8\^2 full Pauli factor\s+\d+\s+\d+\s+\d+\s+(\.\d+)', costs).group(1))
    e8 = F(re.search(r'E8 root reference\s+\d+\s+\d+\s+\d+\s+(\.\d+)', costs).group(1))
    costs_receipt = json.loads((ROOT / 'research/niemeier-lattices/evidence/COSTS.json').read_text())
    # These two rows are the inherited COSTS screens, with rank-max(r,h) idle
    # relaxation. This does not replay the optimizer over all odd stages.
    root_screen = dict(m=41, deficit=120, terms=[(F(9600), 8), (F(360), 9),
                       (F(3840), 16), (F(3840), 16), (F(1920), 9)])
    pauli_model = model(3)
    screens = {'E8_root_reference': root_screen,
               'E8_squared_Pauli_factor': dict(m=49, deficit=23664, terms=pauli_model['base'])}
    paper_intervals = {}
    for name, row in screens.items():
        expected_mass = 41 * 480 - 120 if name == 'E8_root_reference' else 49 * 61920 - 23664
        require(sum(mass for mass, _ in row['terms']) == expected_mass,
                "independent COSTS screen rank-mass equality")
        case = next(item for item in costs_receipt['cases'] if item['name'] == name)
        pair = case['fixed_center_widths']['kappa_interval_scaled_1e18']
        low, high = (F(value, 10**18) for value in pair)
        lower_pressure = pressure(row['terms'], row['m'], low / (1 - low))
        upper_pressure = pressure(row['terms'], row['m'], high / (1 - high))
        require(lower_pressure[1] < row['deficit'] < upper_pressure[0],
                "independent certification of fixed-stage COSTS root endpoints")
        paper_intervals[name] = pair
    ratio_low = F(paper_intervals['E8_squared_Pauli_factor'][0],
                  paper_intervals['E8_root_reference'][1])
    ratio_high = F(paper_intervals['E8_squared_Pauli_factor'][1],
                   paper_intervals['E8_root_reference'][0])
    root_banked = source.b.invoice(120, 9, {9: 8}, 5, [8], [9], 0, False)
    names = ['research/h6-banked-breakeven/README.md',
             'research/h6-banked-breakeven/price_h6.py',
             'research/h6-banked-breakeven/outputs/price_h6.txt',
             'research/niemeier-lattices/workbench/paid-controller/banked.py',
             'research/niemeier-lattices/code/costs.py',
             'research/niemeier-lattices/COSTS.txt',
             'research/niemeier-lattices/evidence/COSTS.json',
             'research/niemeier-lattices/workbench/paid-controller/PAID-CONTROLLER.txt',
             'research/niemeier-lattices/workbench/helper-routes/compensation_rank.py',
             'certificates/selected-result.json', 'certificates/checkpoints/frontier890.json',
             'research/community-efficient500-audit/packets/1424.json',
             'docs/research/community-efficient500-review.md', selected['review'],
             selected['source_manifest'], historical['review']]
    pins = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}
    receipt = dict(status='PASS_INDEPENDENT_FIXED_INVOICE_BOUNDARIES',
        no_new_kappa=True, source_commit='b496aed769dd724cd1ff6b921cade626562be27b',
        source_hashes=pins, arithmetic=dict(log_terms=64, exp_degree=32,
        outward_denominator=str(SCALE), displayed_interval_scale=str(DISPLAY)),
        paper_ratio=str(pauli / e8),
        paper_fixed_stage_intervals_scaled_1e18=paper_intervals,
        paper_ratio_interval_scaled_1e24=display_interval(ratio_low, ratio_high),
        paper_reference_banked_interval_scaled_1e18=
            root_banked['nominal_kappa_interval_scaled_1e18'],
        paper_ratio_scope='COSTS-screen ratio, not banked-invoice ratio: the L5 E8 reference has an idle rank8 relaxed to rank9 by COSTS.instance; banked.base charges its actual rank8. Only the fixed-stage root endpoints were independently recertified, not the inherited all-L optimality proof.',
        selected_context={'review': selected['review'], 'source_manifest': selected['source_manifest'],
                          'reproduce': selected['reproduce']},
        pr1424_context={'head': packet['head'], 'title': packet['title'],
                       'admission': 'Pending parent PR1319 admission per efficient500 maintainer review'},
        source_output_replay='IDENTICAL', targets=results,
        monotonicity='For every fixed alpha>0, P_base(alpha)+R*P_helper(alpha) is strictly increasing in R. Since all child bases exceed 1, pressure is strictly increasing in alpha. The adjacent strict signs therefore prove the globally largest admissible nonnegative integer R for this fixed invoice.',
        scope='Only this nominal complex invoice, fixed data [16], helper [1,7,8,1], nonvirtual, and L=3,5,7. The selected record is compared numerically; its supplier is not repriced. PR1424 is a pinned pending title, not selected admission. No capacity lemma, scalar word, restoration chronology, bit supplier, outer transfer or construction theorem is proved.')
    (HERE / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])
    for item in results:
        print(item['name'], [(r['stages'], r['max_helpers']) for r in item['rows']])


if __name__ == '__main__':
    main()
