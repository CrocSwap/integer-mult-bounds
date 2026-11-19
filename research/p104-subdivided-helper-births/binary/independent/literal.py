#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent literal verifier for the Ali Romman and #7001 BIT lineage."""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
PAIRED = Path('research/paired-query-only-bit')
ALI = Path('research/p104-dual-supplier-lift')
OLD_WORD = PAIRED / 'retained' / 'inputs' / 'BIT-NATIVE-WORD.json.gz'
OLD_WORD_SHA = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
OLD_RESULT_SHA = '907858ba4c6f4c110662c8ea9faa1209acca07a9ae281ba29e9291a41fe8e6e1'
CALLER_SHA = '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
WORD_GZIP_SHA = 'a63f07a5f5ac4aa28b5b635c7836f36efafd03b735ab13f24c8b481d137d54e8'
WORD_SHA = 'e5871a4cf87d62aa90e6660d351636aa5ca47f50239916a0943cd433c7f3d323'
CANONICAL_WORD = '861f5181e4f34db638ab0c573c319fe26ff034d63b21242d67220a4a5d6433ff'
RECIPE_SHA = '9cdb651f7166c01abb9027535d36424da71944932f3b6f84057a12ae12ba6ad2'
RESIDUAL_WORD = '07f5fe923b50ecc26983054cf8f462b1a2b4a008a5e2c7a472209363abaaa35c'
PR7776_HEAD = '4f7c67ae387cc91580f469aeda4d508b372b9ec1'


def need(test, description):
    if not test:
        raise ValueError(description)


def canonical(obj):
    return sha256(json.dumps(obj, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def pinned(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, f'immutable input bytes for {path.name}')
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def candidate_word(path):
    packed = path.read_bytes()
    need(sha256(packed).hexdigest() == WORD_GZIP_SHA, 'checked-in compressed word SHA-256')
    raw = gzip.decompress(packed)
    need(sha256(raw).hexdigest() == WORD_SHA, 'literal word SHA-256')
    word = json.loads(raw)
    need(canonical(word) == CANONICAL_WORD, 'canonical word SHA-256')
    return word


def determinant(rows):
    square = [list(row) for row in rows]
    n = len(square)
    value = F(1)
    for c in range(n):
        pivot = next((i for i in range(c, n) if square[i][c]), None)
        need(pivot is not None, 'singular rational frame')
        if pivot != c:
            square[c], square[pivot] = square[pivot], square[c]
            value *= -1
        entry = square[c][c]
        value *= entry
        for i in range(c + 1, n):
            factor = square[i][c] / entry
            if factor:
                square[i] = [x - factor * y for x, y in zip(square[i], square[c])]
    return value


def orthogonal(xs, ys):
    return all(sum(x * y for x, y in zip(v, w)) == 0 for v in xs for w in ys)


class Charts:
    def __init__(self, frames):
        self.frames = {}
        self.prime_factors = {2}
        for label, frame in frames.items():
            b = [tuple(map(F, row)) for row in frame['B']]
            a = [tuple(map(F, row)) for row in frame['A']]
            need(
                len(b) == frame['dim']
                and len(a) + len(b) == 8
                and all(len(row) == 8 for row in b + a),
                'physical frame ranks',
            )
            need(orthogonal(b, a), 'dual rational frame annihilation')
            d = determinant(b + a)
            self.prime_factors.update([abs(d.numerator), d.denominator])
            self.prime_factors.update(x.denominator for row in b + a for x in row)
            self.frames[int(label)] = (b, a)
        self.rank = {label: len(b) for label, (b, _) in self.frames.items()}

    @cache
    def leg(self, a, b):
        lower, upper = sorted((a, b), key=self.rank.__getitem__)
        n = self.rank[upper] - self.rank[lower]
        need(
            n > 0 and orthogonal(self.frames[lower][0], self.frames[upper][1]),
            'positive nested rational MOVE or helper grade',
        )
        return n

    def main_contacts(self, start, end):
        for j in range(111):
            x, y = j, j + 111
            head = self.frames[start[x]][0]
            body = self.frames[end[y]][0]
            need(
                len(head) == 1
                and len(body) == 7
                and not self.rank[start[y]]
                and self.rank[end[x]] == 8,
                'literal main port quartet',
            )
            need(orthogonal(head, body), 'same fixed head and disjoint rational body')
            d = determinant(head + body)
            self.prime_factors.update([abs(d.numerator), d.denominator])
        return 111


def tape(word, charts, *, adjoint=False, omit=None, readouts=()):
    public, owned = word['public'], word['owned_fields']
    steps = word['program']
    bank = [(1 << j) if j < public else 0 for j in range(public + owned)]
    origin, destination = (
        (word['final'], word['start']) if adjoint else (word['start'], word['final'])
    )
    tags = list(origin) + [None] * owned
    counts, paid, routes = Counter(), Counter(), Counter()
    live, peak, erase_dirty = 0, 0, 0
    found = {}
    sequence = range(len(steps) - 1, -1, -1) if adjoint else range(len(steps))
    for clock in sequence:
        if clock == omit:
            continue
        operation, r, *args = steps[clock]
        need(0 <= r < len(bank), f'bank address at {clock}')
        counts[operation] += 1
        if operation in ('INIT', 'CLEAR'):
            need(r >= public and args[0] in charts.frames, f'private lifetime at {clock}')
            opens = (operation == 'CLEAR') if adjoint else (operation == 'INIT')
            if opens:
                need(tags[r] is None, f'activation of live bank at {clock}')
                live += 1
                peak = max(peak, live)
                tags[r] = args[0]
            else:
                need(tags[r] == args[0], f'wrong chart at erasure {clock}')
                live -= 1
                erase_dirty += int(bool(bank[r]))
                tags[r] = None
            bank[r] = 0
        elif operation == 'ADD':
            source, chart = args
            need(
                0 <= source < len(bank)
                and r != source
                and tags[r] == tags[source] == chart
                and chart in charts.frames,
                f'XOR chart contact at {clock}',
            )
            if clock in readouts:
                found[clock] = bank[r if adjoint else source]
            if adjoint:
                bank[source] ^= bank[r]
            else:
                bank[r] ^= bank[source]
        elif operation == 'SWAP':
            (other,) = args
            need(
                0 <= other < len(bank)
                and r != other
                and tags[r] is not None
                and tags[other] is not None,
                f'whole-field swap at {clock}',
            )
            bank[r], bank[other] = bank[other], bank[r]
            tags[r], tags[other] = tags[other], tags[r]
        else:
            need(operation == 'MOVE' and r >= public, f'paid owned transfer at {clock}')
            a, b = args[::-1] if adjoint else args
            need(tags[r] == a, f'literal MOVE chronology at {clock}')
            paid[charts.leg(a, b)] += 1
            routes[a, b] += 1
            tags[r] = b
    need(
        tags == list(destination) + [None] * owned and not live and not any(bank[public:]),
        'public endpoints and complete private retirement',
    )
    return (
        bank[:public],
        dict(counts=counts, paid=paid, routes=routes, peak=peak, erase_dirty=erase_dirty),
        found,
    )


def expected_rows(n, adjoint):
    result = []
    for r in range(n):
        want = 1 << r
        if adjoint and r < 111:
            want ^= 1 << (r + 111)
        if not adjoint and 111 <= r < 222:
            want ^= 1 << (r - 111)
        result.append(want)
    return result


def different(observed, expected):
    return (
        tuple(i for i, (actual, want) in enumerate(zip(observed, expected)) if actual != want),
        sum((a ^ b).bit_count() for a, b in zip(observed, expected)),
    )


def held_out(word, charts, paid_banks):
    n = word['public']
    held = n - 1
    choices = {
        i
        for i, (op, dst, *args) in enumerate(word['program'])
        if op == 'ADD' and args[0] == held and dst in paid_banks
    }
    _, _, forward = tape(word, charts, readouts=choices)
    official, _, backward = tape(word, charts, adjoint=True, readouts=choices)
    need(official == expected_rows(n, True), 'official transpose before omission')
    clock = min(i for i in choices if forward[i] and backward[i])
    mutated, _, _ = tape(word, charts, omit=clock)
    flipped, number = different(mutated, expected_rows(n, False))
    transpose, _, _ = tape(word, charts, adjoint=True, omit=clock)
    columns, count = different(transpose, expected_rows(n, True))
    expected_columns = tuple(j for j in range(n) if (forward[clock] >> j) & 1)
    expected_outputs = tuple(j for j in range(n) if (backward[clock] >> j) & 1)
    need(
        flipped == expected_outputs and columns == expected_columns and number == count > 0,
        'held-out XOR omission with a nonzero exact endpoint change',
    )
    retired = next(i for i, e in enumerate(word['program']) if e[0] == 'CLEAR')
    try:
        tape(word, charts, omit=retired)
    except ValueError as exc:
        need(str(exc) == 'public endpoints and complete private retirement', 'dirty CLEAR control')
    else:
        raise ValueError('held-out erasure accepted')
    return dict(
        helper=held,
        omitted_ADD_clock=clock,
        operation=word['program'][clock],
        changed_output_rows=flipped,
        changed_input_columns=columns,
        changed_coefficients=number,
        omitted_CLEAR_clock=retired,
        dirty_CLEAR_control='rejected at terminal retirement',
    )


def birth_deltas(word, old, witness, paid_routes, charts):
    # Ali's eight source restrictions are projected in the published #7776 binary proof.
    removed_helpers = {633, 638, 646, 640, 649, 636, 651, 635}
    removed_paid_ordinals = {
        2323,
        2657,
        2342,
        2669,
        2381,
        2695,
        2453,
        2743,
        2496,
        2771,
        2497,
        2773,
        2513,
        2783,
        2532,
        2795,
    }
    old_start = [c for j, c in enumerate(old['start']) if j not in removed_helpers]
    old_end = [c for j, c in enumerate(old['final']) if j not in removed_helpers]
    original_moves = [
        (clock, tuple(e[2:])) for clock, e in enumerate(old['program']) if e[0] == 'MOVE'
    ]
    retained = {
        clock: edge
        for j, (clock, edge) in enumerate(original_moves)
        if j not in removed_paid_ordinals
    }
    base_routes = Counter(retained.values())
    base_native_paid = Counter()
    for (a, b), amount in base_routes.items():
        base_native_paid[charts.leg(a, b)] += amount
    base_native_targets = Counter(
        charts.leg(old_start[j], old_end[j]) for j in range(222, len(old_start))
    )
    need(
        len(old_start) == len(old_end) == 651 and len(witness['steps']) == 21,
        'source birth lineage inventory',
    )
    revised_start, revised_end = old_start.copy(), old_end.copy()
    seen, seen_clocks = set(), set()
    paid_deltas, target_deltas = Counter(), Counter()
    for entry in witness['steps']:
        role, via = (entry['witness'][k] for k in ('role', 'chart'))
        need(
            role >= 222 and role not in seen and entry['reverse'],
            'distinct transposed helper birth',
        )
        seen.add(role)
        a, b = entry['old_move_charts'][::-1]
        clock = entry['original_selected_source_clock']
        need(
            retained.get(clock) == (a, b) and clock not in seen_clocks and base_routes[a, b] > 0,
            'distinct retained archived MOVE with the exact oriented charts',
        )
        seen_clocks.add(clock)
        base_routes[a, b] -= 1
        base_routes[a, via] += 1
        base_routes[via, b] += 1
        paid_deltas[charts.leg(a, b)] -= 1
        paid_deltas[charts.leg(a, via)] += 1
        paid_deltas[charts.leg(via, b)] += 1
        s, t = revised_start[role], revised_end[role]
        need([t, s] == entry['old_helper_charts'], 'archived helper start and end')
        need(
            charts.rank[s] < charts.rank[via] < charts.rank[t], 'strict forward helper grade split'
        )
        need(
            [charts.leg(b, via), charts.leg(via, a)] == entry['paid_daughter_ranks']
            and [charts.leg(t, via), charts.leg(via, s)] == entry['target_daughter_ranks'],
            'literal daughter ranks',
        )
        target_deltas[charts.leg(s, t)] -= 1
        target_deltas[charts.leg(s, via)] += 1
        target_deltas[charts.leg(via, t)] += 1
        revised_start[role] = via
        revised_start.append(s)
        revised_end.append(via)
    need(
        (revised_start, revised_end) == (word['start'], word['final']),
        'every old and new helper boundary',
    )
    need(base_routes == paid_routes, 'complete literal oriented route multiset matches 21 births')
    return dict(
        parent_native_paid=base_native_paid,
        parent_native_targets=base_native_targets,
        native_paid_delta=paid_deltas,
        native_target_delta=target_deltas,
        split_roles=sorted(seen),
    )


def shift(form, count, q=False):
    return {(monomial + count) ^ int(q): coefficients for monomial, coefficients in form.items()}


def add(receiver, donor):
    out = receiver.copy()
    for monomial, coefficients in donor.items():
        value = out.get(monomial, 0) ^ coefficients
        if value:
            out[monomial] = value
        else:
            out.pop(monomial, None)
    return out


def caller_monomial(stages):
    return sum(1 << (10 * (stage - 1) + 1) for stage in stages)


def caller_rows(caller, adjoint=False):
    """Encode independent stage exponents in disjoint 10-bit slots, q in low bit."""
    n = caller['roles']
    need(len(caller['events']) < 2**10, 'independent stage monomial exponents cannot carry')
    rows = [{0: 1 << j} for j in range(n)]
    order = reversed(caller['events']) if adjoint else caller['events']
    for op, *args in order:
        if op == 'ADD' or op == 'QUERY':
            destination, source = args[::-1] if adjoint else args
            rows[destination] = add(rows[destination], shift(rows[source], 0, op == 'QUERY'))
        elif op == 'SWAP':
            a, b = args
            rows[a], rows[b] = rows[b], rows[a]
        elif op == 'LOCAL':
            stage, a, b = args
            if adjoint:
                a, b = b, a
            count = caller_monomial([stage])
            rows[a], rows[b] = shift(rows[a], count), shift(
                add(rows[b], shift(rows[a], 0, True)), count
            )
        elif op == 'IDLE_ONE':
            a, stages = args
            rows[a] = shift(rows[a], caller_monomial(stages))
        else:
            raise ValueError(f'unknown caller event {op}')
    return rows


def paired_invoice(caller, native_paid, native_targets, caller_event_counts):
    need(
        (
            caller['roles'],
            caller['ports'],
            caller['stages'],
            caller['body_rank'],
            caller['ambient_rank'],
        )
        == (38, 111, 18, 7, 127),
        '111 physical ports, 38 root roles, 18 stages and seven body directions',
    )
    roots = [
        {caller_monomial(owner['stages']) | owner['q']: 1 << j}
        for j, owner in enumerate(caller['diagonal'])
    ]
    need(
        caller_rows(caller) == roots == caller_rows(caller, True),
        'every paired caller coefficient in both directions',
    )
    need(
        all(
            owner['q'] == 1
            and owner['stages']
            and set(owner['stages']) <= set(range(1, 19))
            and len(owner['stages']) == len(set(owner['stages']))
            for owner in caller['diagonal']
        ),
        'nonempty root body and productive q grade',
    )
    paid, targets = Counter(), Counter()
    stage_roles = {}
    stages = []
    ports = caller['ports']
    for op, *args in caller['events']:
        if op in ('ADD', 'SWAP', 'QUERY'):
            a, b = args
            need(a != b and 0 <= a < 38 and 0 <= b < 38, 'distinct cocharted caller operands')
            if op == 'QUERY':
                paid[1] += ports
        elif op == 'LOCAL':
            stage, a, b = args
            touched = stage_roles.setdefault(stage, set())
            need(
                a != b
                and 0 <= a < 38
                and 0 <= b < 38
                and stage in range(1, 19)
                and not touched.intersection({a, b}),
                'both actual disjoint main pairs at their fresh stage',
            )
            touched.update((a, b))
            stages.append(stage)
            paid.update(native_paid)
            targets.update(native_targets)
        elif op == 'IDLE_ONE':
            a, ss = args
            need(
                0 <= a < 38 and ss and len(ss) == len(set(ss)) and set(ss) <= set(range(1, 19)),
                'complete charged idle mask',
            )
            paid[7 * len(ss)] += ports
    need(stages == [i for i in range(1, 19) for _ in range(2)], '36 actual sealed LOCAL blocks')
    for owner in caller['diagonal']:
        targets[1 + 7 * len(owner['stages'])] += ports
    copies = caller_event_counts['LOCAL']
    need(
        sum(targets.values()) == 111 * 38 + copies * sum(native_targets.values()),
        'complete public count with disjoint independent helpers',
    )
    return paid, targets


def ordinary(word, caller, events, paid, targets):
    ports, roles = caller['ports'], caller['roles']
    copies, query, idles = (events[k] for k in ('LOCAL', 'QUERY', 'IDLE_ONE'))
    owned, public = word['owned_fields'], word['public']
    scratch = 4
    banks = owned + public + scratch
    native_flow = 16 * banks * len(word['program'])
    total_op = ports * (8 * (events['ADD'] + 3 * events['SWAP']) + 256 * (copies + query + roles))
    groups = 4 * (sum(targets.values()) + sum(paid.values())) + 8 * ports * (copies + idles)
    route_flow = groups * 80 * (134**2 + 134)
    whole = copies * native_flow + total_op + route_flow
    reserve = (
        copies * (owned + scratch)
        + 2 * ports * roles * len(caller['events'])
        + 16 * ports * (copies + query + roles)
    )
    need(whole < 10**12 and reserve < 10**7, 'whole-job raw ordinary and owned allowances')
    return dict(
        native_banks_and_scratch=banks,
        native_bank_transits_per_call=native_flow,
        caller_bank_transits=total_op,
        route_groups=groups,
        route_records=route_flow,
        ordinary_records=whole,
        owned_backing=reserve,
        raw_ordinary_allowance=10**12,
        raw_owned_allowance=10**7,
    )


def histogram(row):
    return Counter({int(k): n for k, n in row.items()})


def verify(source_root, word_path):
    word = candidate_word(word_path)
    witness = pinned(HERE.parent / 'BIRTHS.json', RECIPE_SHA)
    old = pinned(source_root / OLD_WORD, OLD_WORD_SHA)
    old_result = pinned(source_root / ALI / 'BIT-RESULT.json', OLD_RESULT_SHA)
    caller = pinned(source_root / PAIRED / 'EFREE-CALLER.json.gz', CALLER_SHA)
    n = word['public']
    need(
        witness['parent_head'] == PR7776_HEAD
        and witness['parent_pr'] == 7776
        and witness['parent_program_sha256']
        == old_result['native']['program_sha256']
        == RESIDUAL_WORD,
        'recipe and published #7776 residual native word',
    )
    need(witness['program_sha256'] == CANONICAL_WORD and n == 672, 'frozen 672-owner construction')
    need(
        word['frames'] == old['frames'] and len(word['frames']) == 636,
        'all physical frames unchanged',
    )
    charts = Charts(word['frames'])
    main_ports = charts.main_contacts(word['start'], word['final'])
    forward, forward_log, _ = tape(word, charts)
    transpose, reverse_log, _ = tape(word, charts, adjoint=True)
    need(
        forward == expected_rows(n, False) and transpose == expected_rows(n, True),
        'all arbitrary native scalar coefficients',
    )
    need(forward_log['paid'] == reverse_log['paid'], 'both literal paid rank histograms')
    native_targets = Counter(
        charts.leg(a, b) for a, b in zip(word['start'][222:], word['final'][222:])
    )
    need(
        all(
            charts.rank[a] < charts.rank[b]
            for a, b in zip(word['start'][222:], word['final'][222:])
        ),
        'positive native helper grades',
    )
    composition = birth_deltas(word, old, witness, forward_log['routes'], charts)
    paid_banks = {event[1] for event in word['program'] if event[0] == 'MOVE'}
    controls = held_out(word, charts, paid_banks)
    call_events = Counter(e[0] for e in caller['events'])
    paid, targets = paired_invoice(caller, forward_log['paid'], native_targets, call_events)
    old_paid, old_targets = paired_invoice(
        caller, composition['parent_native_paid'], composition['parent_native_targets'], call_events
    )
    need(
        old_paid == histogram(old_result['paid'])
        and old_targets == histogram(old_result['targets']),
        'independently reconstructed #7776 full signed invoice',
    )
    old_paid.update({k: 36 * v for k, v in composition['native_paid_delta'].items()})
    old_targets.update({k: 36 * v for k, v in composition['native_target_delta'].items()})
    need(paid == old_paid and targets == old_targets, 'complete 36-call independent invoice')
    ledger = ordinary(word, caller, call_events, paid, targets)
    return dict(
        status='PASS_INDEPENDENT_LITERAL_BINARY_BIRTHS',
        source_pr=7776,
        source_head=PR7776_HEAD,
        source_residual_native_sha256=RESIDUAL_WORD,
        candidate_file_sha256=WORD_SHA,
        candidate_gzip_sha256=WORD_GZIP_SHA,
        candidate_canonical_sha256=CANONICAL_WORD,
        source_word_sha256=OLD_WORD_SHA,
        caller_sha256=CALLER_SHA,
        witnessed_input_sha256=RECIPE_SHA,
        public=n,
        native_scalar_coefficients_each_way=n * n,
        caller_polynomial_coefficients_each_way=38**2,
        frames=len(charts.frames),
        main_ports=main_ports,
        raw_prime_exclusion_factors=sorted(charts.prime_factors),
        instruction_counts=forward_log['counts'],
        forward_peak_owned=forward_log['peak'],
        reverse_peak_owned=reverse_log['peak'],
        owned_nonzero_CLEAR=forward_log['erase_dirty'],
        dual_nonzero_retirement=reverse_log['erase_dirty'],
        birth_composition=composition,
        native_paid=forward_log['paid'],
        native_targets=native_targets,
        held_out_controls=controls,
        caller_events=call_events,
        native_calls=36,
        paid=paid,
        targets=targets,
        signed_rank_surplus=sum(r * k for r, k in targets.items())
        - sum(r * k for r, k in paid.items()),
        ordinary=ledger,
    )
