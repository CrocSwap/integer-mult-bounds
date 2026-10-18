#!/usr/bin/env python3
"""All eight-transfer schedules of the free-port two-connector five-source family.

PR1438/PR1498 model: five read-only sources, two arbitrary-dirty connectors,
every B_j and A_m called exactly twice, freely chosen ports, and t paid
one-way transfers C: z0 += z1. PR1615 (bbMisk) first proved the sharp
threshold of eight. This standard-library verifier re-certifies it (all 31
nonzero masks are realizable iff t is even and t >= 8) and classifies every
eight-transfer solution.

Parts, each registered as its own command in VERIFY.json:
  controls  The engine reproduces PR943's in-repo 105- and 945-word censuses
            (n=4, 5) and PR1438's in-repo full-placement T=2 censuses (n=1..5)
            bin for bin. It pins the complete per-split coverage histograms
            at T=0 and T=4, finds no universal schedule there, and finds no
            restored odd-T schedule.
  six       Exhaustive T=6 census over every word and port split: no
            universal schedule, with the complete coverage histogram pinned.
  eight     Exhaustive T=8 census: exactly 2,502 universal schedules, with a
            pinned digest. Every one replays as a complete 80-call program on
            dense random F2 maps. Discussion 1412's pilot is among them, and
            deletion and wrong-port mutants fail.

Gap reduction (README): between consecutive B calls, z1 is fixed, so further
transfers only alternate z0 between two states. Three transfers in one gap
therefore have the coverage and parities of one, and four those of two. A
schedule with a gap of three or more reduces to one with T - 2 transfers and
equal coverage. Hence censuses with at most two transfers per gap, run for
T = 0, 2, 4, 6, exclude every universal schedule with t <= 7. They also make
the T = 8 count exact.

Sagar Thakrar with substantial Anthropic Claude assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from multiprocessing import Pool
import os
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from engine import census_word, words  # noqa: E402
from replay import place_readouts, program, run  # noqa: E402

EXPECTED = json.loads((PACKAGE/'EXPECTED.json').read_bytes())
PR943 = ROOT/'research/universal-connector-boundary/CERTIFICATE.json'
PR1438 = ROOT/'research/two-connector-transfer-boundary/EXPECTED.json'


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


def check_pins():
    rows = json.loads((PACKAGE/'SOURCES.json').read_bytes())['files']
    for row in rows:
        if row['usage'] == 'input':
            require(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'Pinned input: ' + row['path'])
    for row in json.loads((PACKAGE/'REMOTE-SOURCES.json').read_bytes())['copies']:
        require(sha256((PACKAGE/row['copy']).read_bytes()).hexdigest() == row['sha256'], 'Pinned remote copy: ' + row['copy'])


def _task(arg):
    word, n, T, reduced, want = arg
    return census_word(word, n, T, list(range(1 << n)), reduced=reduced, want_full=want)


def census(n, T, reduced=True, want_full=False):
    """Aggregate over all words and port splits: (leaves, Counter{(r, size)}, full schedules)."""
    jobs = [(w, n, T, reduced, want_full) for w in words(n)]
    leaves, hist, full = 0, Counter(), []
    with Pool(os.cpu_count() or 1) as pool:
        for lv, h, f in pool.imap_unordered(_task, jobs, chunksize=4):
            leaves += lv
            hist.update(h)
            full += f
    return leaves, hist, sorted(full)


def hist_sha256(hist):
    return sha256(json.dumps(sorted([r, size, count] for (r, size), count in hist.items())).encode()).hexdigest()


def no_universal(T, key):
    """Exhaustive reduced census with the complete (split, coverage) histogram pinned."""
    _, hist, full = census(5, T, want_full=True)
    want = EXPECTED[key]
    require(not full and max(size for _, size in hist) < 32, 'T=%d has a universal schedule' % T)
    require(sum(hist.values()) == want['restored'] and maxima(hist) == want['max_by_split'], 'T=%d census' % T)
    require(hist_sha256(hist) == want['histogram_sha256'], 'T=%d coverage histogram' % T)
    return hist


def maxima(hist):
    out = {}
    for (r, size), _ in hist.items():
        out[r] = max(out.get(r, 0), size)
    return {str(r): out[r] for r in sorted(out)}


def sizes(hist, r=None):
    out = Counter()
    for (split, size), count in hist.items():
        if r is None or split == r:
            out[str(size)] += count
    return dict(out)


def part_controls():
    certificate = json.loads(PR943.read_bytes())
    for row in certificate['censuses']:
        _, hist, _ = census(row['sources'], 0)
        require(sizes(hist, 0) == row['histogram'], 'PR943 %d-source census' % row['sources'])
    print('PR943 single-connector censuses reproduced:', [row['sources'] for row in certificate['censuses']])
    for row in json.loads(PR1438.read_bytes())['censuses']:
        n = row['sources']
        _, hist, _ = census(n, 2, reduced=False)
        require(sum(hist.values()) == row['restored'] and sizes(hist) == row['coverage_histogram'],
                'PR1438 %d-source T=2 census' % n)
    print('PR1438 full-placement T=2 censuses reproduced for 1-5 sources')
    hist = no_universal(0, 'zero')
    print('T=0: no universal schedule for any split; maxima by split', maxima(hist))
    hist = no_universal(4, 'four')
    print('T=4: no universal schedule; maxima by split', maxima(hist))
    for T in (1, 3, 5):
        _, hist, _ = census(5, T)
        require(sum(hist.values()) == 0, 'odd T=%d restored a schedule' % T)
    print('odd T = 1, 3, 5: no schedule restores both connectors')


def part_six():
    hist = no_universal(6, 'six')
    print('T=6: %d restored schedules, none universal; maxima by split %s' % (sum(hist.values()), maxima(hist)))


def part_eight():
    leaves, hist, full = census(5, 8, want_full=True)
    want = EXPECTED['eight']
    by_split = Counter(bin(ports).count('1') for _, ports, _ in full)
    digest = sha256(json.dumps(full).encode()).hexdigest()
    require(sum(hist.values()) == want['restored'] and maxima(hist) == want['max_by_split'], 'T=8 census')
    require(len(full) == want['universal'] and dict(sorted(by_split.items())) == {int(k): v for k, v in want['universal_by_split'].items()},
            'T=8 universal schedules')
    require(digest == want['universal_sha256'], 'T=8 universal schedule digest')
    pilot = want['discussion1412_pilot']
    require((tuple(pilot['word']), pilot['ports'], tuple(pilot['gaps'])) in set(full), 'Discussion 1412 pilot')
    for i, (word, ports, gaps) in enumerate(full):
        ops, cuts = program(word, ports, list(gaps))
        prog = place_readouts(ops, cuts)
        require(len(prog) == 80 and sum(op[0] == 'A' for op in prog) == 62, 'program shape')
        require(run(prog, trials=3, seed=i), 'replay of universal schedule %d' % i)
    # Mutation controls on three witnesses: the first r = 1 schedule, the first r = 5 schedule and the pilot.
    first = {r: next(s for s in full if bin(s[1]).count('1') == r) for r in (1, 5)}
    for word, ports, gaps in (first[1], first[5], (tuple(pilot['word']), pilot['ports'], tuple(pilot['gaps']))):
        ops, cuts = program(word, ports, list(gaps))
        prog = place_readouts(ops, cuts)
        for kind in ('C', 'A'):
            for i in [k for k, op in enumerate(prog) if op[0] == kind]:
                require(not run(prog[:i] + prog[i+1:], trials=5), 'deleting one %s still passed' % kind)
        for i in [k for k, op in enumerate(prog) if op[0] == 'A']:
            mutant = prog[:i] + [('A', prog[i][1], 1 - prog[i][2])] + prog[i+1:]
            require(not run(mutant, trials=5), 'a wrong-port readout still passed')
    print('T=8: %d universal schedules %s, digest %s' % (len(full), dict(sorted(by_split.items())), digest[:16]))
    print('all universal schedules replay as 80-call programs on dense random F2 maps; Discussion 1412 pilot included;',
          'on three witnesses every C or A deletion and every wrong-port readout fails')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', choices=['controls', 'six', 'eight'], required=True)
    args = parser.parse_args()
    require(sys.version_info >= (3, 11), 'Python 3.11 or later')
    check_pins()
    dict(controls=part_controls, six=part_six, eight=part_eight)[args.part]()
    print('PASS_TWO_CONNECTOR_TRANSFER_THRESHOLD', args.part)


if __name__ == '__main__':
    main()
