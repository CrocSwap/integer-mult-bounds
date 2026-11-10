#!/usr/bin/env python3
"""Bind two retained local proofs and precision constants to #7000.

No contributor scientific code is imported. This is source binding, not a
replacement for the completed full-word/chronology checks or supplier admission.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = (ROOT / path).read_bytes()
    pins = json.loads((HERE / 'SOURCES.json').read_text())['files']
    pin = next(row for row in pins if row['path'] == path)
    need(sha256(raw).hexdigest() == pin['sha256'], 'source drift: ' + path)
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


def rises(word):
    result = []
    for index, event in enumerate(word['program']):
        if event[0] != 'MOVE':
            continue
        _, role, start, end, *_ = event
        if role >= word['public'] and len(word['frames'][end]) > len(word['frames'][start]):
            result.append((role - word['public'], start, end, index))
    return result


def owner_order(rows):
    result = defaultdict(list)
    for owner, start, end, _ in rows:
        result[owner].append((start, end))
    return dict(result)


def main():
    prefix = 'research/shared-wire-split-composition/'
    word = read(prefix + 'data/final.json.gz')
    caller = read(prefix + 'data/caller.json')
    receipt = read(prefix + 'FULL-RESULT.json')
    old = read('research/owned-ascent-contract/retained/native-word.json.gz')
    recipes = read('research/owned-ascent-contract/RECIPES.json')
    need(word['frames'] == old['frames'], 'exact same frame representatives')
    current_rises, old_rises = rises(word), rises(old)
    recipe_keys = Counter((r['role'] - old['public'], r['start'], r['end']) for r in recipes)
    need(Counter(row[:3] for row in current_rises) == recipe_keys,
         'every actual rise has an independently checked exact recipe')
    need(owner_order(current_rises) == owner_order(old_rises), 'per-owner rise order')
    need(len(current_rises) == 23, 'all actual rises covered')
    rank_mass = sum(len(word['frames'][end]) - len(word['frames'][start])
                    for _, start, end, _ in current_rises)
    need(rank_mass == 56, 'actual paid rank mass')
    max_pair = max(len(r['left_records']) + len(r['right_records']) for r in recipes)
    need(max_pair == 147 and max_pair < 1000, 'two adapters fit retained record group')
    # Reuse full chronology evidence for frame/same-chart validity. This scan
    # independently checks current bank inventory; old peak=30 is not reused.
    live = set()
    peak = births = 0
    for event in word['program']:
        if event[0] == 'INIT':
            need(event[1] >= word['public'] and event[1] not in live, 'fresh owned birth')
            live.add(event[1]); births += 1; peak = max(peak, len(live))
        elif event[0] == 'CLEAR':
            need(event[1] in live, 'live owned clear')
            live.remove(event[1])
    need(not live and births == 54 and peak == 43 and word['owned_fields'] == 51,
         'current lifetime and storage census')

    uses = Counter()
    all_ports = []
    for name, kind in caller['types'].items():
        all_ports.extend(kind['ports'])
        need(kind['roles'] == 38, 'root role inventory')
    need(sorted(all_ports) == list(range(len(word['ports']))), 'disjoint complete port partition')
    for event in caller['events']:
        if event[1] == 'LAMBDA':
            name, _, role, sign = event
            need(name in caller['types'] and sign in (-1, 1), 'global normalizer orientation')
            kind = caller['types'][name]
            need(kind['offset'] <= role < kind['offset'] + kind['roles'], 'global root role')
            for port in kind['ports']:
                need(0 < word['ports'][port] < 512, 'nonzero nine-axis central direction')
            uses[name] += len(kind['ports'])
    need(sum(uses.values()) == 14480, 'all source normalizer uses')
    need(sum(uses.values()) * 1000 == receipt['ordinary']['lambda_second_charge'],
         'separate movement allowance paid in current receipt')
    ordinary = receipt['ordinary']
    need(ordinary['raw_upper'] + ordinary['per_input_conversion']
         + ordinary['lambda_second_charge'] == ordinary['conservative_total'] == 826790496,
         'current source-unit total (not physical tape-step conversion)')

    grid = receipt['precision']['common_grid']
    need(grid['word']['odd_scale_lcm'] == 1125, 'per-call odd scale')
    need(grid['word']['dyadic_height'] == 24 and grid['word']['numerator_bits'] == 24,
         'local precision bounds from completed exact-source scan')
    need(Fraction(grid['word']['maximum_scaled_mass']) < 2 ** 37, 'local mass envelope')
    need(grid['caller']['denominator_height'] == 163 and grid['caller']['pre_joint_height'] == 154,
         'caller height')
    need(Fraction(grid['caller']['maximum_mass']) < 2 ** 126
         and Fraction(grid['caller']['pre_joint_mass']) < 2 ** 124, 'caller mass')
    need(grid['context_height'] == max(163, 154 + 24) == 178
         and grid['context_mass_bits'] == max(126, 124 + 37) == 161
         and grid['context_c'] == 356, 'retained all-size induction constants')
    # H is separately established by the complex interval/threshold replay.
    H = int(receipt['gate']['H'])
    need(H == 14174600000000000000 and receipt['gate']['written_log_power'] == 2228,
         'current source threshold')
    K_star = 1920 * 153 ** 1920 * (H + 1) ** 2
    need((4096 * K_star).bit_length() < H, 'fresh threshold absorbs context depth')
    print(json.dumps(dict(status='PASS_PR7000_LOCAL_INTERFACE_BINDINGS',
        owned_rises=len(current_rises), owned_rank_mass=rank_mass,
        same_per_owner_rise_order=True, maximum_adapter_records=max_pair,
        owned_labels=51, lifetimes=births, peak_owned=peak,
        lambda_uses=dict(uses), lambda_route_units=sum(uses.values()) * 1000,
        ordinary_source_units=ordinary['conservative_total'],
        context_height=178, context_mass_bits=161, K_star_bits=K_star.bit_length(),
        H=H, current_rise_events=[row[3] for row in current_rises],
        scope='Exact unary recipe and source-census transfer; proof supplies universal-width '
              'implication under retained contracts. Precision envelope engines are reused, '
              'not independently reimplemented here. No complete provider/layout/cost admission.'), indent=2))


if __name__ == '__main__':
    main()
