"""Frozen-menu composition, no new exponent-domain or supplier search."""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'inputs'


def need(ok, label):
    if not ok:
        raise ValueError(label)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compose(events, schedules, independent, word):
    current = {h: 0 for h in schedules}
    out, pulses = [], []
    frames = dict(enumerate(word['start']))
    for index, original in enumerate(events):
        event = copy.deepcopy(original)
        for h in sorted(schedules):
            if index in schedules[h]:
                exponent = schedules[h][index]
                change = exponent - current[h]
                if change:
                    need(frames[h] == event[2], 'transition uses actual live frame')
                    q = independent.two_power(change)
                    pulse = ['scalar', ['scale', ['L', h], q.numerator, q.denominator], event[2]]
                    out.append(pulse)
                    pulses.append([index, h, change, event[2], len(out)-1])
                current[h] = exponent
        if event[0] == 'scalar' and event[1][0] == 'add':
            gate = event[1]
            shift = sum(sign * current.get(r[1], 0) for sign, r in
                        zip((1, -1), gate[1:3]) if r[0] == 'L')
            q = independent.Fraction(gate[3], gate[4]) * independent.two_power(shift)
            gate[3:5] = [q.numerator, q.denominator]
        if index == len(events) - 1:
            need(event == ['phase', 'done'], 'terminal boundary')
            for h in sorted(schedules):
                if current[h]:
                    need(frames[h] == word['final'][h], 'restoration actual final frame')
                    q = independent.two_power(-current[h])
                    out.append(['scalar', ['scale', ['L', h], q.numerator, q.denominator], word['final'][h]])
                    pulses.append([index, h, -current[h], word['final'][h], len(out)-1])
        out.append(event)
        if event[0] == 'climb':
            need(frames[event[2]] == event[3], 'original live frame edge')
            frames[event[2]] = event[4]
    need([e for e in out if e[0] != 'scalar'] ==
         [e for e in events if e[0] != 'scalar'], 'nonscalar identity')
    return out, pulses


def menu_census(single, cross):
    # Gray order: exact 2^19 fixed subsets, not optimization of gauge paths.
    n = len(single)
    active, score = [False] * n, 0
    best_score, best_mask = 0, 0
    previous = 0
    for i in range(1, 1 << n):
        mask = i ^ (i >> 1)
        changed = mask ^ previous
        j = changed.bit_length() - 1
        marginal = single[j] + sum(cross[j][k] for k in range(n) if active[k])
        score += -marginal if active[j] else marginal
        active[j] = not active[j]
        if (score, mask) < (best_score, best_mask):
            best_score, best_mask = score, mask
        previous = mask
    return best_score, best_mask


def recurrence_census(single, cross):
    n = len(single)
    values = [0] * (1 << n)
    best = (0, 0)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        i = bit.bit_length() - 1
        rest = mask ^ bit
        total = values[rest] + single[i]
        remaining = rest
        while remaining:
            next_bit = remaining & -remaining
            j = next_bit.bit_length() - 1
            total += cross[i][j]
            remaining ^= next_bit
        values[mask] = total
        best = min(best, (total, mask))
    return best


def run(output, upstream, exhaustive=False):
    need(__debug__ and not sys.flags.optimize, 'assertions required')
    pins = json.loads((HERE / 'MANIFEST.json').read_text())['files']
    for path, digest in pins.items():
        need(sha(HERE / path) == digest, 'package pin ' + path)
    archive = upstream / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    need(sha(archive) == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'upstream archive pin')
    blobs = {}
    with tarfile.open(archive) as bundle:
        for name, digest in json.loads((HERE / 'UPSTREAM.json').read_text())['members'].items():
            member = bundle.getmember(name)
            need(member.isfile(), 'fixed regular archive member')
            raw = bundle.extractfile(member).read()
            need(hashlib.sha256(raw).hexdigest() == digest, 'upstream member pin')
            blobs[Path(name).name] = json.loads(gzip.decompress(raw))
    lib = load('pinned_replay_invoice', INPUT / 'engine/engine.py')
    independent = load('pinned_single_dp', INPUT / 'pr1369/independent.py')
    parent = load('pinned_static_transform', INPUT / 'pr1388/vendor/pr1369/vendor/pr1263/verify.py')
    word = blobs['CANONICAL-WORD.json.gz']
    programs = blobs['LOCAL-PROGRAMS.json.gz']
    gauges = json.loads((INPUT / 'pr1388/vendor/pr1369/vendor/pr1263/GAUGES.json').read_text())
    certificate = json.loads((INPUT / 'pr1369/CERTIFICATE.json').read_text())
    pair = json.loads((INPUT / 'pr1388/RESULT.json').read_text())
    menu = json.loads((HERE / 'MENU.json').read_text())
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    results = {}
    for orientation in ('forward', 'backward'):
        static = parent.transform(lib, word, programs[orientation],
                                  {int(h): int(k) for h, k in gauges[orientation].items()})
        baseline = json.loads(json.dumps(lib.invoice(static, 'copy-init')))
        need(baseline == certificate['orientations'][orientation]['baseline_static_invoice'],
             'exact static baseline invoice')
        rows = certificate['orientations'][orientation]['helpers']
        helpers = sorted(row['helper'] for row in rows)
        need(len(helpers) == 19 and len(set(helpers)) == 19, 'exact19menu')
        schedules, singles = {}, {}
        for row in rows:
            h = row['helper']
            need(str(h) not in gauges[orientation], 'zero static coordinate')
            need(word['start'][h] == 0 and word['final'][h] == 1, 'cold FULL boundary')
            need(not any(e[0] == 'residual_adapter' and e[2] == h for e in static), 'unwrapped')
            need(not any(e[0] == 'scalar' and e[1][0] in ('copy', 'clear') and
                         ['L', h] in e[1][1:] for e in static), 'no COPY CLEAR')
            terms = independent.incident_adds(static, h)
            schedule = {int(i): k for i, k in menu[orientation][str(h)].items()}
            need(set(schedule) == {t[0] for t in terms}, 'complete fixed-menu incident coverage')
            need(all(type(k) is int and row['domain'][0] <= k <= row['domain'][1]
                     for k in schedule.values()), 'pinned exponent domain')
            delta = independent.objective(terms, [schedule[t[0]] for t in terms])
            need(delta == row['best_delta_real'], 'pinned fixed-menu single objective')
            schedules[h] = schedule
            singles[h] = delta
        cross = [[0] * 19 for _ in helpers]
        interactions = []
        for index, e in enumerate(static):
            if e[0] != 'scalar' or e[1][0] != 'add':
                continue
            g = e[1]
            if g[1][0] != 'L' or g[2][0] != 'L':
                continue
            a, b = g[1][1], g[2][1]
            if a not in schedules or b not in schedules:
                continue
            ka, kb = schedules[a][index], schedules[b][index]
            q = lib.Q(g[3], g[4])
            correction = (lib.price(q * lib.power(ka-kb)) - lib.price(q * lib.power(ka))
                          - lib.price(q * lib.power(-kb)) + lib.price(q))
            j, k = helpers.index(a), helpers.index(b)
            cross[j][k] += correction
            cross[k][j] += correction
            interactions.append([index, a, b, ka, kb, correction])
        all19, all_pulses = compose(static, schedules, independent, word)
        all_invoice = lib.invoice(all19, 'copy-init')
        full_delta = sum(singles.values()) + sum(cross[i][j] for i in range(19) for j in range(i))
        need(all_invoice['real_primitives'] - baseline['real_primitives'] == full_delta,
             'quadratic full19 exact invoice')
        marginal = {h: singles[h] + sum(max(0, c) for c in cross[j])
                    for j, h in enumerate(helpers)}
        need(all(bound < 0 for bound in marginal.values()), 'strict negative worst-case marginal')
        best_delta, mask = full_delta, (1 << 19) - 1
        if exhaustive:
            need((best_delta, mask) == menu_census([singles[h] for h in helpers], cross),
                 'Gray fixed-menu oracle')
            need((best_delta, mask) == recurrence_census([singles[h] for h in helpers], cross),
                 'least-bit fixed-menu oracle')
        chosen = [h for j, h in enumerate(helpers) if mask >> j & 1]
        winner, pulses = compose(static, {h: schedules[h] for h in chosen}, independent, word)
        invoice = lib.invoice(winner, 'copy-init')
        need(invoice['real_primitives'] - baseline['real_primitives'] == best_delta,
             'winning subset exact invoice')
        need({str(k): v for k, v in invoice['paid_profile'].items()} ==
             baseline['paid_profile'], 'paid profile equality')
        need(invoice['charged_payload_bits'] == 192 and invoice['prefix_bits'] <= 192, 'payload')
        endpoint = lib.replay(winner, orientation)
        need(endpoint['formal_input_columns'] == 712, 'complete endpoint')
        # Reproduce the strongest comparable published pair on this same menu.
        pair_word, _ = compose(static, {h: schedules[h] for h in (348, 359)}, independent, word)
        pair_invoice = lib.invoice(pair_word, 'copy-init')
        expected_pair = pair['orientations'][orientation]['candidate_invoice']
        need({k: pair_invoice[k] for k in expected_pair} == expected_pair, 'PR1388pair exact')
        need(compose(static, {h: {i: 0 for i in s} for h, s in schedules.items()}, independent, word)[0]
             == static, 'zero menu identity control')
        # Compare the formula against emitted words on both nonzero interactions.
        sample = [helpers.index(h) for h in (348, 359, 479, 515)]
        for small_mask in range(16):
            selected = [i for j, i in enumerate(sample) if small_mask >> j & 1]
            small_word, _ = compose(static, {helpers[i]: schedules[helpers[i]]
                                            for i in selected}, independent, word)
            actual = lib.invoice(small_word, 'copy-init')['real_primitives'] - baseline['real_primitives']
            predicted = sum(singles[helpers[i]] for i in selected) + sum(
                cross[i][j] for i in selected for j in selected if j < i)
            need(actual == predicted, 'four-helper subset direct invoice')
        # Missing restoration must fail the formal-column endpoint predicate.
        wrong = copy.deepcopy(winner)
        need(bool(pulses), 'negative control inserted pulse exists')
        source_index, helper, change, frame, output_index = pulses[-1]
        q = independent.two_power(change)
        expected_scale = ['scalar', ['scale', ['L', helper], q.numerator, q.denominator], frame]
        need(wrong[output_index] == expected_scale, 'recorded inserted pulse exact SCALE')
        del wrong[output_index]
        rejected = False
        try:
            lib.replay(wrong, orientation)
        except ValueError:
            rejected = True
        need(rejected, 'omitted transition endpoint rejected')
        results[orientation] = {'helpers': helpers, 'schedules': schedules, 'single_real_deltas': singles,
                                'shared_ADD_interactions': interactions, 'all19_invoice': all_invoice,
                                'all19_delta_real': full_delta, 'exhaustive_subsets_checked': (1 << 19) if exhaustive else 0,
                                'strict_marginal_bounds': marginal,
                                'unique_fixed_menu_optimum': True,
                                'fixed_menu_winning_helpers': chosen, 'winning_invoice': invoice,
                                'winning_delta_real': best_delta, 'PR1388pair_invoice': pair_invoice,
                                'strictly_better_than_PR1388pair': invoice['complex_primitives'] < pair_invoice['complex_primitives'],
                                'all712_endpoint': endpoint, 'inserted_scales': pulses,
                                'controls': {'zero_menu': True, 'four_helper_direct_invoices': 16,
                                             'omitted_transition': True},
                                'nonscalar_events_unchanged': True}
        prior = expected['orientations'][orientation]
        for field in ('all19_delta_real', 'winning_delta_real', 'winning_invoice',
                      'all19_invoice', 'shared_ADD_interactions', 'fixed_menu_winning_helpers'):
            need(json.loads(json.dumps(results[orientation][field])) == prior[field],
                 'admitted result field ' + field)
    for path, digest in pins.items():
        need(sha(HERE / path) == digest, 'postflight package pin ' + path)
    need(sha(archive) == 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6', 'postflight upstream archive')
    output.write_text(json.dumps({'status': 'PASS_FIXED19_MENU_COMPOSITION', 'orientations': results,
                                 'scope': 'finite scalar fixed-menu optimum; no native/owner/adapter or kappa admission',
                                 'no_new_kappa': True}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, help='fresh JSON file outside this package')
    parser.add_argument('--upstream', type=Path, default=HERE.parents[1],
                        help='checkout containing the pinned archive (default: this repository)')
    parser.add_argument('--exhaustive', action='store_true')
    args = parser.parse_args()
    if args.output is not None:
        need(not args.output.exists(), 'fresh output')
        need(HERE not in args.output.resolve().parents, 'output outside package')
        run(args.output, args.upstream.resolve(), args.exhaustive)
    else:
        with tempfile.TemporaryDirectory(prefix='temporal-menu-') as temporary:
            run(Path(temporary) / 'result.json', args.upstream.resolve(), args.exhaustive)
    print('PASS_FIXED19_MENU_COMPOSITION: 134070/134086 complex primitives; '
          'unique fixed-menu optimum; all 712 scalar columns per orientation')
