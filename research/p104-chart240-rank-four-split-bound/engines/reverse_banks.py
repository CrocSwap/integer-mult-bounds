"""Independent exact occupied-chart census for the #7314 chart-240 cohort."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD = '7314/WORD.json.gz'
CALLER = '7113/CALLER.json'
PINS = {
    WORD: 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    CALLER: '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
PROTECTED = {863, 1355, 1568}
BOUNDARY = (3, 240)
MIXED_CHARTS = (76, 399)
PROTECTED_OWNER = 863
COHORT = [93, 337, 341, 346, 712, 714, 715, 863, 1099, 1103, 1108, 1342]
KEY_CAP = 256


def decode(raw):
    def unique(items):
        obj = dict(items)
        if len(obj) != len(items):
            raise ValueError('duplicate JSON key')
        return obj

    return loads(raw, object_pairs_hook=unique)


def audit(word, deadline, boundary, mixed, fixed_owner, protected):
    public = word['public']
    main = set(word['live']) | {r + 112 for r in word['live']}
    main.update(word['hosted']['X2'], word['hosted']['Y2'])
    origins = dict(enumerate(word['initial']))
    ends = dict(enumerate(word['final']))
    assert len(origins) == len(ends) == public
    cohort = {r for r in origins if r not in main and (origins[r], ends[r]) == boundary}
    pivots = cohort - protected
    assert fixed_owner in cohort and fixed_owner in protected

    frames = word['frames']

    @cache
    def span(chart):
        vectors = {0}
        for v in frames[chart]:
            assert v not in vectors, 'dependent chart basis'
            vectors.update(x ^ v for x in tuple(vectors))
        return frozenset(vectors)

    start, end = boundary
    dimensions = [len(basis) for basis in frames]
    assert span(start) < span(end) and dimensions[end] - dimensions[start] == 4
    assert {dimensions[f] - dimensions[start] for f in mixed} == {1, 3}
    assert all(span(start) < span(f) < span(end) for f in mixed)
    rank_two = {f for f in range(len(frames))
                if dimensions[f] - dimensions[start] == 2 and span(start) < span(f) < span(end)}
    chosen = rank_two | set(mixed)
    state = ends.copy()
    banks = defaultdict(set)
    for role, chart in state.items():
        banks[chart].add(role)

    tape = word['program']
    high = {f: len(tape) for f in chosen}
    segments = []
    occupied = Counter()
    cuts = Counter()
    paid = Counter()
    owner_moves = []
    visited = 0

    def segment(chart, low):
        bank = banks[chart]
        tier = 'mixed_863' if chart in mixed else 'cohort_rank_two'
        upper = high[chart]
        assert low <= upper
        if tier == 'mixed_863' and fixed_owner not in bank:
            return
        available = sorted(bank & pivots)
        if available:
            occupied[tier] += 1
            cuts[tier] += upper - low + 1
            segments.append(dict(tier=tier, chart=chart, basis=frames[chart], cut=low,
                                 first_cut=low, last_cut=upper, pivots=available,
                                 public_bank=sorted(r for r in bank if r < public),
                                 owned_bank=sorted(r for r in bank if r >= public)))
        elif tier == 'mixed_863':
            occupied['mixed_863_without_peer'] += 1
            cuts['mixed_863_without_peer'] += upper - low + 1

    for clock in range(len(tape) - 1, -1, -1):
        if monotonic() >= deadline:
            break
        visited += 1
        op, dest, *args = tape[clock]
        if op == 'MOVE':
            old, new, owned = args
            assert owned == (dest >= public) and state[dest] == new
            assert span(old) < span(new) or owned and span(new) < span(old), 'illegal chart MOVE'
            charts = (old, new)
            paid[abs(dimensions[old] - dimensions[new])] += 1
            if dest == fixed_owner:
                owner_moves.append([clock, old, new])
        elif op in ('INIT', 'CLEAR'):
            chart, = args
            assert dest >= public
            assert state.get(dest) == (chart if op == 'INIT' else None)
            charts = (chart,)
        else:
            assert op in ('ADD', 'COPY', 'SCALE') and Fraction(args[-2])
            chart = args[-1]
            assert state[dest] == chart
            if op in ('ADD', 'COPY'):
                assert args[0] != dest and state[args[0]] == chart
                assert op != 'COPY' or dest >= public
            charts = (chart,)

        # Cut k is before tape[k]. Record every segment above the event before undoing it.
        for chart in charts:
            if chart in chosen:
                segment(chart, clock + 1)
                high[chart] = clock
        if op == 'MOVE':
            banks[new].remove(dest)
            banks[old].add(dest)
            state[dest] = old
        elif op == 'INIT':
            banks[chart].remove(dest)
            del state[dest]
        elif op == 'CLEAR':
            banks[chart].add(dest)
            state[dest] = chart

    complete = visited == len(tape)
    if complete:
        assert state == origins
        for chart in chosen:
            segment(chart, 0)
    else:
        # Retain the known part of the interval above the last completed event.
        for chart in chosen:
            segment(chart, len(tape) - visited)

    segments.sort(key=lambda row: (row['tier'] != 'mixed_863', row['cut'], row['chart']))
    keys = {tier: [[r['cut'], r['chart'], p] for r in segments if r['tier'] == tier for p in r['pivots']]
            for tier in ('mixed_863', 'cohort_rank_two')}
    eligible = keys['mixed_863'] + keys['cohort_rank_two']
    return dict(
        cut_convention='cut k is before literal event k, with k=len(program) after the final event',
        representative_convention='smallest cut of each inclusive run bounded by operations touching the chart',
        scope_complete=complete, visited_events=visited, literal_events=len(tape),
        unvisited_reverse_clock=None if complete else len(tape) - visited - 1,
        cohort=sorted(cohort), protected_roles=sorted(protected),
        eligible_public_pivots=sorted(pivots), rank_two_charts=sorted(rank_two),
        protected_owner_moves=sorted(owner_moves), paid_native_histogram=dict(paid),
        occupied_segments=dict(occupied), covered_cuts=dict(cuts), segments=segments,
        keys_by_tier=keys, representative_keys=eligible[:KEY_CAP],
        overflow_keys=eligible[KEY_CAP:],
    )


def controls():
    toy = dict(public=2, live=[], hosted={'X2': [], 'Y2': []},
               frames=[[], [1], [1, 2], [1, 2, 4], [1, 2, 4, 8]],
               initial=[0, 0], final=[4, 4], program=[
                   ['MOVE', 0, 0, 1, False],
                   ['MOVE', 1, 0, 1, False],
                   ['ADD', 0, 1, '-2', 1],
                   ['MOVE', 1, 1, 2, False],
                   ['MOVE', 0, 1, 3, False],
                   ['MOVE', 1, 2, 3, False],
                   ['MOVE', 0, 3, 4, False],
                   ['MOVE', 1, 3, 4, False],
               ])
    d = audit(toy, float('inf'), (0, 4), (1, 3), 0, {0})
    assert d['scope_complete'] and d['keys_by_tier']['mixed_863'] == [[2, 1, 1], [3, 1, 1], [6, 3, 1]]
    assert d['keys_by_tier']['cohort_rank_two'] == [[4, 2, 1]]
    assert all(0 not in row['pivots'] for row in d['segments'])
    assert d['covered_cuts']['mixed_863_without_peer'] == 3
    bad = toy | {'frames': [[], [1], [2, 4], [1, 2, 4], [1, 2, 4, 8]]}
    try:
        audit(bad, float('inf'), (0, 4), (1, 3), 0, {0})
    except AssertionError as exc:
        assert str(exc) == 'illegal chart MOVE'
    else:
        raise AssertionError('invalid nested MOVE passed')
    return ['scalar_contact_breaks_cut_run', 'protected_pivot_excluded',
            'rank_two_requires_live_pivot', 'exact_nonnested_move_rejected']


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('inputs', type=Path, nargs='?', default=Path(__file__).resolve().parent / 'inputs')
    p.add_argument('--price', type=Path)
    p.add_argument('--price-sha')
    p.add_argument('--seconds', type=int, default=15, choices=range(2, 16), metavar='2..15')
    p.add_argument('--controls-only', action='store_true')
    args = p.parse_args()
    if args.controls_only:
        print(dumps(controls()))
        return
    if args.price is None or args.price_sha is None:
        p.error('authenticated saved price and SHA-256 are required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM, stop)
    alarm(args.seconds)
    deadline = monotonic() + args.seconds - 1
    try:
        raw = args.price.read_bytes()
        assert sha256(raw).hexdigest() == args.price_sha, 'changed price receipt'
        assert decode(raw)['head'] == HEAD, 'wrong price comparator'
        files = {}
        for name, digest in PINS.items():
            data = (args.inputs / name).read_bytes()
            assert sha256(data).hexdigest() == digest, ('changed input', name)
            files[name] = data
        caller = decode(files[CALLER])
        assert [e[1] for e in caller['events'] if e[0] == 'J'] == list(range(1, 18))
        checks = controls()
        result = audit(decode(decompress(files[WORD])), deadline, BOUNDARY,
                       MIXED_CHARTS, PROTECTED_OWNER, PROTECTED)
        assert result['cohort'] == COHORT
        if result['scope_complete']:
            assert result['visited_events'] == 76461
            assert sum(result['paid_native_histogram'].values()) == 6280
            assert result['protected_owner_moves'] == [[36056, 3, 76], [36069, 76, 399], [36081, 399, 240]]
    except TimeoutError:
        print(dumps(dict(head=HEAD, status='hard_timeout', scope_complete=False), sort_keys=True))
        raise SystemExit(2)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, input_sha256=PINS, controls=checks, geometry_only=True,
                     price_sha256=args.price_sha, seconds_cap=args.seconds, key_cap=KEY_CAP,
                     **result), sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
