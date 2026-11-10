#!/usr/bin/env python3
"""Source-bound 134-axis supplement to #7001, not supplier admission.

Maintainer review prepared with OpenAI Codex assistance. Apache-2.0.
Retains CubeJerry's paired caller and the credited ambient-cap argument.
No contributor checker or interval implementation is imported.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKAGE = ROOT / 'research/paired-query-only-bit'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(relative):
    path = PACKAGE / relative
    raw = path.read_bytes()
    pins = json.loads((HERE / 'SOURCES.json').read_text())['files']
    pin = next(row for row in pins if row['path'] == path.relative_to(ROOT).as_posix())
    need(sha256(raw).hexdigest() == pin['sha256'], 'source drift: ' + relative)
    return json.loads(gzip.decompress(raw) if relative.endswith('.gz') else raw)


def log_bounds(x):
    """Positive rational logarithm via range reduction and a geometric tail."""
    x = Q(x)
    need(x > 0, 'positive logarithm argument')
    if x < 1:
        lo, hi = log_bounds(1 / x)
        return -hi, -lo

    def reduced(y):
        z = (y - 1) / (y + 1)
        need(0 <= z <= Q(1, 3), 'range-reduced logarithm')
        count = 80
        lower = 2 * sum((z ** (2 * j + 1) / (2 * j + 1)
                         for j in range(count)), Q(0))
        tail = 2 * z ** (2 * count + 1) / ((2 * count + 1) * (1 - z * z))
        return lower, lower + tail

    exponent = 0
    while x >= 2:
        x /= 2
        exponent += 1
    lo, hi = reduced(x)
    two_lo, two_hi = reduced(Q(2))
    return exponent * two_lo + lo, exponent * two_hi + hi


def margins(saving, ambient, power, log_power):
    la, ua = log_bounds(ambient)
    lt, ut = log_bounds(1 - saving)
    ltheta, utheta = log_bounds(Q(42, 43))
    ltwo, utwo = log_bounds(2)
    return ((lt - power * saving * ua - log_power * utheta,
             ut - power * saving * la - log_power * ltheta),
            (log_power * ltwo - power * saving * ua,
             log_power * utwo - power * saving * la))


def main():
    receipt = read('EFREE-RESULT.json')
    caller = read('EFREE-CALLER.json.gz')
    native = read('retained/inputs/BIT-NATIVE-WORD.json.gz')
    seed = Q(read('data/selected_claim.json')['admitted_BIT_saving'])
    calls = [event for event in caller['events'] if event[0] == 'LOCAL']
    need(Counter(event[1] for event in calls) == Counter({s: 2 for s in range(1, 19)}),
         'two actual native calls per stage')
    need(native['public'] == 659 and caller['roles'] == 38 and caller['ports'] == 111,
         'reviewed source dimensions')

    # Each invocation maps the native's 111 X and 111 Y arrays to distinct
    # caller fields. Its remaining 437 arbitrary helper inputs get fresh IDs.
    helper_ids = set()
    for index, (_, stage, source, destination) in enumerate(calls):
        need(source != destination and 0 <= source < 38 and 0 <= destination < 38,
             'distinct root roles')
        mapping = [('root', port, source) for port in range(111)]
        mapping += [('root', port, destination) for port in range(111)]
        helpers = [('helper', index, role) for role in range(222, native['public'])]
        need(not helper_ids.intersection(helpers), 'fresh independent helper inputs')
        helper_ids.update(helpers)
        need(len(set(mapping + helpers)) == native['public'], 'injective native placement')
    for stage in range(1, 19):
        roles = [role for event in calls if event[1] == stage for role in event[2:]]
        need(len(set(roles)) == 4, 'two disjoint main pairs at each stage')
    need(38 * 111 + len(helper_ids) == receipt['productive_fields'] == 19950,
         'no cloned or missing productive input')

    native_axes = max(frame['dim'] for frame in native['frames'].values())
    need(native_axes == 8 and caller['body_rank'] == 7 and caller['stages'] == 18,
         'retained native/stage geometry')
    ambient = native_axes + caller['body_rank'] * caller['stages']
    need(ambient == 134 and caller['ambient_rank'] == 127,
         'working cap differs from recorded maximum target rank')
    saving = Q(receipt['raw_tested'])
    power = receipt['finite_admission']['tensor_power']
    need(power == 768 and saving == Q('.00385253'), 'exact tested source price')
    old = margins(saving, 127, power, 610)
    failed = margins(saving, ambient, power, 610)
    need(min(old[0][0], old[1][0]) > 0, 'reproduce original 127-axis success')
    need(failed[0][1] < 0, 'original power fails conservative 134-axis comparison')
    log_power = 617
    corrected = margins(saving, ambient, power, log_power)
    need(min(corrected[0][0], corrected[1][0]) > 0, 'corrected majorant')
    need(margins(saving, ambient, power, log_power - 1)[0][1] < 0,
         'preceding logarithm power fails')
    need(15 ** 43 < 16 ** 42 and 2 * 15 ** (power * 43) <= ambient ** (power * 42),
         'separated and shifted exits')
    step = 10 ** 10
    wins = lambda j: (step * j + 1) ** log_power < 2 ** j
    lo, hi = 1, 2
    while not wins(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if wins(mid):
            hi = mid
        else:
            lo = mid
    need(wins(hi) and not wins(hi - 1), 'exact threshold and preceding-grid control')

    ops = Counter(event[0] for event in caller['events'])
    paid = sum(receipt['paid'].values())
    targets = sum(receipt['targets'].values())
    routes = 4 * (paid + targets) + 8 * 111 * len(calls) + 8 * 111 * ops['IDLE_ONE']
    visible = (len(calls) * 10 ** 7 + 111 * 8 * (ops['ADD'] + 3 * ops['SWAP'])
               + 256 * 111 * (len(calls) + ops['QUERY'] + caller['roles']))
    need(routes == receipt['whole_job_route_count'] and visible == receipt['ordinary_visible_records'],
         'source-bound route and visible census')
    revised_routes = routes * 8 * (10 * ambient * ambient + 10 * ambient)
    total = revised_routes + visible
    need(total == 824677050000 and total < 10 ** 12, 'revised inherited-tariff allowance')
    owned = (len(calls) * native['owned_fields'] + 2 * 111 * 38 * len(caller['events'])
             + 16 * 111 * (len(calls) + ops['QUERY'] + 38))
    need(owned == receipt['owned_bank_bound'] < 10 ** 7, 'unchanged owned bank')
    covered = saving - 2 * Q(1, 10 ** 10)
    previous = seed
    bootstrap = []
    for admitted in (Q('.0038507'), Q('.00385248')):
        envelope = Q(249, 250) * covered + Q(1, 250) * previous
        need(previous < admitted < envelope < covered < Q(1, 250) < 1 - envelope,
             'acyclic ordinary bootstrap with positive stock and relaxation gaps')
        bootstrap.append(dict(previous=str(previous), admitted=str(admitted),
                              envelope=str(envelope), slack=str(envelope - admitted)))
        previous = admitted
    def interval(pair):
        scale = 10 ** 30
        return [str(Q((pair[0] * scale).__floor__(), scale)),
                str(Q(-(-pair[1] * scale).__floor__(), scale))]
    print(json.dumps(dict(status='PASS_PAIRED_BIT_134_AXIS_SUPPLEMENT',
        ambient=ambient, original_ambient=127, original_log_power=610,
        corrected_log_power=log_power, grid_index=hi, H=step * hi,
        original_134_log_complement_margin=interval(failed[0]),
        corrected_log_complement_margin=interval(corrected[0]),
        corrected_log_base_margin=interval(corrected[1]),
        native_occurrences=len(calls), productive_fields=targets,
        route_groups=routes, routed_records=revised_routes, visible_records=visible,
        ordinary_records=total, owned_bank=owned, bootstrap=bootstrap,
        scope='Conservative ambient-cap application and arithmetic under retained whole-job, '
              'spectator, chronological-product and tariff contracts. No all-width provider '
              'proof, source tariff conversion, or selected-frontier admission.'), indent=2))


if __name__ == '__main__':
    main()
