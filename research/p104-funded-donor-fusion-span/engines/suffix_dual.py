"""Independent exact output-coordinate obstruction for the missing chart-240 correction."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD_SHA = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
PRICE_SHA = '25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b'
START, END, TARGET = 37765, 76460, 48184
DONOR, CACHE, CHART = 1355, 1568, 240
LIMIT = 512


def checked(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError('changed dependency: ' + path.name)
    return raw


def apply_adjoint(weights, event):
    op, dst, *args = event
    if op in ('INIT', 'CLEAR'):
        weights.pop(dst, None)
    elif op == 'SCALE':
        if dst in weights:
            weights[dst] *= Fraction(args[0])
    elif op in ('ADD', 'COPY'):
        weight = weights.get(dst, 0)
        if op == 'COPY':
            weights.pop(dst, None)
        if weight:
            src = args[0]
            value = weights.get(src, 0) + Fraction(args[1]) * weight
            if value:
                weights[src] = value
            else:
                weights.pop(src, None)
    else:
        assert op == 'MOVE'


def chart_contacts(events, start, end, chart):
    marks = {start, end}
    for clock in range(start, end):
        event = events[clock]
        involved = event[2:4] if event[0] == 'MOVE' else [event[-1]]
        if chart in involved:
            marks.update((clock, clock + 1))
    return sorted(marks)


def geometry(word, events, deadline):
    cuts = chart_contacts(events, START, END, CHART)
    cut_set = set(cuts)
    charts = word['final'].copy()
    eligible = {role for role, chart in enumerate(charts) if chart == CHART and role not in (863, DONOR)}
    banks = {}
    next_scalar_contact = {}
    covered = set()
    for cut in range(len(events), START - 1, -1):
        if monotonic() >= deadline:
            return cuts, banks, cut
        if cut < len(events):
            op, role, *args = events[cut]
            if op in ('ADD', 'COPY') and cut != TARGET - 1:
                next_scalar_contact[role] = next_scalar_contact[args[0]] = cut
            elif op == 'SCALE':
                next_scalar_contact[role] = cut
            if op == 'MOVE' and role < word['public']:
                a, b, owned = args
                assert charts[role] == b and owned is False
                charts[role] = a
                if role not in (863, DONOR):
                    if b == CHART:
                        eligible.remove(role)
                    if a == CHART:
                        eligible.add(role)
        if cut in cut_set:
            selected = []
            for role in sorted(eligible):
                key = role, next_scalar_contact.get(role)
                if key not in covered:
                    covered.add(key)
                    selected.append(role)
            banks[cut] = selected
    assert sorted(banks) == cuts
    return cuts, banks, None


def probe(events, banks, covector, deadline):
    weights = covector.copy()
    tested = []
    target = None
    for cut in range(len(events), START - 1, -1):
        if monotonic() >= deadline:
            return target, tested, cut
        if cut < len(events) and cut != TARGET - 1:
            apply_adjoint(weights, events[cut])
        if cut == TARGET:
            target = -2 * weights.get(DONOR, 0)
        if cut in banks:
            tested.extend([cut, role, str(weights.get(role, 0))] for role in banks[cut])
    return target, tested, None


def target_response(events, public):
    """Direct forward action on the one missing signed impulse."""
    rows = {DONOR: Fraction(-2)}
    for op, dst, *args in events[TARGET:]:
        if op in ('INIT', 'CLEAR'):
            rows.pop(dst, None)
        elif op == 'SCALE':
            if dst in rows:
                rows[dst] *= Fraction(args[0])
        elif op in ('ADD', 'COPY'):
            old = rows.get(dst, 0) if op == 'ADD' else 0
            value = old + Fraction(args[1]) * rows.get(args[0], 0)
            if value:
                rows[dst] = value
            else:
                rows.pop(dst, None)
        else:
            assert op == 'MOVE'
    assert all(role < public for role in rows)
    return rows


def controls():
    # A cut before the ADD sees a response from the source; after it the
    # corresponding response is zero, so both endpoints must be represented.
    event = ['ADD', 1, 0, '3/7', CHART]
    assert chart_contacts([event], 0, 1, CHART) == [0, 1]
    w = {1: Fraction(1)}
    assert w.get(0, 0) == 0
    apply_adjoint(w, event)
    assert w == {1: 1, 0: Fraction(3, 7)}
    apply_adjoint(w, ['COPY', 1, 2, '-1/2', CHART])
    assert w == {0: Fraction(3, 7), 2: Fraction(-1, 2)}
    apply_adjoint(w, ['CLEAR', 2, CHART])
    assert w == {0: Fraction(3, 7)}
    return ['both_chart_contact_sides', 'signed_add_copy_and_clear_adjoint']


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=Path('inputs'))
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    assert __debug__
    control = controls()
    if args.controls_only:
        print(json.dumps(control))
        return
    deadline = monotonic() + 27
    quote = json.loads(checked(args.inputs / 'price.json', PRICE_SHA))
    assert (quote['head'], quote['word_sha256']) == (HEAD, WORD_SHA)
    word = json.loads(decompress(checked(args.inputs / 'WORD.json.gz', WORD_SHA)))
    events = word['program']
    assert len(events) == END + 1
    assert events[START - 1] == ['ADD', CACHE, 863, '1', CHART]
    assert events[TARGET - 2:TARGET + 1] == [
        ['MOVE', DONOR, 739, CHART, False], ['ADD', DONOR, CACHE, '-2', CHART],
        ['MOVE', DONOR, CHART, 127, False]]
    assert events[END] == ['CLEAR', CACHE, CHART]
    for event in events[START:END]:
        assert event[1] != CACHE
        if event[0] in ('ADD', 'COPY') and event[2] == CACHE:
            assert event[0] == 'ADD' and event[-1] == CHART
    cuts, banks, incomplete = geometry(word, events, deadline)
    sites = sum(map(len, banks.values()))
    result = {'head': HEAD, 'word_sha256': WORD_SHA, 'price_sha256': PRICE_SHA,
              'controls': control, 'representative_cuts': cuts, 'eligible_representative_sites': sites,
              'coverage_cap': LIMIT, 'unvisited_clock': incomplete,
              'compression': 'both sides of chart touches, deduplicated by role and next scalar contact'}
    if incomplete is not None or sites > LIMIT:
        result.update(status='UNRESOLVED_GEOMETRY_OR_CAP', unvisited_keys=[
            [cut, role] for cut in sorted(banks) for role in banks[cut]], tested=[])
    else:
        response = target_response(events, word['public'])
        probes = []
        for output, wanted in sorted(response.items()):
            target, tested, stop = probe(events, banks, {output: Fraction(1)}, deadline)
            if stop is not None:
                break
            assert target == wanted and len(tested) == sites
            nonzero = [row for row in tested if Fraction(row[2])]
            probes.append([output, str(wanted), len(nonzero)])
            if not nonzero:
                result.update(status='EXACT_SEPARATION', terminal_covector={output: '1'},
                              target_pairing=str(target), nonzero_candidate_pairings=[],
                              tested=tested, unvisited_keys=[])
                break
        else:
            stop = None
        if 'status' not in result:
            result.update(status='UNRESOLVED', unvisited_clock=stop,
                          unvisited_keys=[] if stop is None else [[c,r] for c in sorted(banks) if c <= stop for r in banks[c]])
        result.update(target_response={str(k):str(v) for k,v in sorted(response.items())}, coordinate_probes=probes)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
