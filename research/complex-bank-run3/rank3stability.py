#!/usr/bin/env python3
"""Is the rank-3 rung stable?  Measured against every head of #233, and against every other
width-66 row this repository's certificates carry.

The rung's contract (`EXPORT-CONTRACT-RANK3.md`) is priced on **one** row: PR233's layer
certificate at head `109a857`.  That row is not merged, so the honest question is not "is the
number right" but "does the rung survive the branch moving, and is it a property of the family
or of this particular row".  This module answers both by measurement:

* **every head of #233 that touches that certificate** -- six commits, all vendored under
  `references/pr233-heads/` so the comparison is offline and pinned rather than dependent on a
  live branch.  Each head is profiled, its whole-bank eligibility list is computed, and where
  rank 3 is eligible the rung is re-priced in full.
* **every other width-66 row in this repository's certificates** -- found by the same walk
  `suppliers.py` uses, deduplicated by (W, deficit, histogram), each scored for the same
  question: would the rank-3 rung exist on it, and at what price.

The finding is that the rung's *eligibility* is not stable across the heads and its *price* is,
and the reason is arithmetic rather than incidental.  A family of rank `r` with `n` children in
the ledger row the absorption uses (three copies) fills whole width-``m`` banks exactly when
`m | r * n`; for `m = 66` that is a condition on `n` alone, `n` a multiple of `m / gcd(r, m)`, so:

    rank  3:  22 | n_3      rank 11:  6 | n_11      rank 18: 11 | n_18
    rank  4:  33 | n_4      rank 16: 33 | n_16      rank 20: 33 | n_20

Every family's eligibility is therefore a modular accident of its child count, and the module
checks that rule against `ledger3.eligibility` on every row it examines rather than trusting it.
It also records, for each row, how many registers the family falls short of a whole bank -- the
number that says *how close* a row came, which for the early heads of #233 is three.
"""
import json
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import instantiate_rank3  # noqa: E402
import ledger3  # noqa: E402
import rank3contract  # noqa: E402
import suppliers  # noqa: E402

COLLECTION = 'references/pr233-heads'
FAMILY = 3
WIDTH = instantiate_rank3.WIDTH
COPIES = instantiate_rank3.COPIES

# The six heads of #233 that touch the layer certificate, in commit order, each with the file
# this package vendored from it.  The last head is the row the contract is priced on, vendored
# at the package root because the contract cites it there.
HEADS = (
    ('52c6fba58ff74fdca1131e50379287491e599f74', '2026-10-10 02:01:05 +0400', '52c6fba',
     'A stronger complex supplier: PR200\'s physical layer on the source-assisted v4 word, '
     'complex saving 7.0861e-4 (no new kappa)', COLLECTION + '/52c6fba.certificate.json'),
    ('7f909fb1413ea7994f3c4b5107dc6d15418cadb8', '2026-10-10 02:07:25 +0400', '7f909fb',
     'verify: record the checker\'s source hashes by repo-relative path (the certificate was '
     'keyed by temp paths)', COLLECTION + '/7f909fb.certificate.json'),
    ('cf08677072c2e0d29fe14fb4df8e7233d1deea50', '2026-10-10 02:15:35 +0400', 'cf08677',
     'verify: certificate.json keeps exact fields only; floats and generated-artifact hashes '
     'go to report.json', COLLECTION + '/cf08677.certificate.json'),
    ('c3f9ba18ae6a9fad0cdb4ce8cd41e6baa52f9797', '2026-10-10 02:20:13 +0400', 'c3f9ba1',
     'verify: drop the candidate-file hashes from the certificate (their profiles carry '
     'floats); report field-level differences', COLLECTION + '/c3f9ba1.certificate.json'),
    ('246f6f944c64eb7047026b3780636eeb61d30cf7', '2026-10-10 02:26:24 +0400', '246f6f9',
     'Layer with 98% of the operations frozen: complex saving 7097667/10^10 = 7.0977e-4 '
     '(+1.26% over PR194), 435 frames changed', COLLECTION + '/246f6f9.certificate.json'),
    ('109a857a329d18ed5552d5573f17ddfa886ae57f', '2026-10-10 02:40:40 +0400', '109a857',
     'Pairs only: PR168\'s frames unchanged, PR200\'s maximum-weight reuse pairing; complex '
     'saving 3549537/5000000000 = 7.0991e-4 (+1.28% over PR194)',
     instantiate_rank3.ROW_NAME),
)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def profile_of(path):
    """A certificate file's ledger row, in PR219's profile form."""
    return ledger3.profile(json.loads(path.read_text())['complex_profile'])


def row_label(profile):
    """What identifies a row here: its width, its deficit and its child histogram."""
    text = '%d:%d:%s' % (profile['W'], profile['N'],
                         instantiate_rank3.histogram_digest(profile['child_multiplicities']))
    return sha256(text.encode('ascii')).hexdigest()[:12]


def criterion(family, width=WIDTH):
    """The child count a family of this rank needs (ledger row) to fill whole width-`width`
    banks.

    `width | family * n` with `d = gcd(family, width)` is `width / d | n`: a condition on the
    count alone, which is what makes eligibility a modular property of the row rather than of
    the family.  (The supplier publishes counts per copy; the ledger row this package absorbs
    from is three copies of it, and for rank 3 -- 22 | 3n if and only if 22 | n -- the two
    readings coincide.)
    """
    d = _gcd(family, width)
    return dict(rank=family, divisor=width // d, gcd=d,
                rule='%d | n_%d' % (width // d, family))


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def analyze(profile, interval=None, leaf=None, price=True):
    """One row, and what the rank-3 rung would be on it."""
    copied = ledger3.three_copies(profile)
    eligibility = ledger3.eligibility(copied)
    counts = copied['child_multiplicities']
    ranked = {str(rank): dict(count=counts[rank], volume=rank * counts[rank],
                              registers_short=(-(rank * counts[rank])) % WIDTH,
                              divides_width=(WIDTH % rank == 0),
                              eligible=(rank in eligibility))
              for rank in sorted(counts)}
    for rank in sorted(counts):
        entry = ranked[str(rank)]
        assert entry['eligible'] == ((rank * counts[rank]) % WIDTH == 0), \
            'divisibility is the criterion: rank %d' % rank
        assert entry['eligible'] == (counts[rank] % criterion(rank)['divisor'] == 0), \
            'and the count alone decides it: rank %d' % rank
    out = dict(m=profile['m'], W=profile['W'], deficit=profile['N'], mass=profile['total_rank'],
               families=len(counts), maxchild=max(counts),
               histogram_digest=instantiate_rank3.histogram_digest(counts),
               eligibility=eligibility, families_at_width=ranked,
               rank3_eligible=(FAMILY in eligibility))
    if not out['rank3_eligible']:
        out['verdict'] = ('the rung does not exist on this row: %d registers short of a whole '
                          'bank' % ranked[str(FAMILY)]['registers_short'])
        return out
    step = ledger3.absorb(copied, FAMILY)
    retained = step['retained']
    out['rung'] = dict(volume=step['volume'], banks=step['banks'],
                       banks_per_copy=step['banks'] // COPIES,
                       blocks_per_bank=WIDTH // FAMILY, divides_width=step['rank_divides_width'],
                       padding_per_bank=0,
                       stock_drop=step['stock_drop'], mass_drop=step['volume'],
                       retained_W=retained['W'], retained_deficit=retained['N'],
                       retained_mass=retained['total_rank'],
                       retained_children=sum(retained['child_multiplicities'].values()),
                       retained_families=len(retained['child_multiplicities']),
                       retained_eligibility=ledger3.eligibility(retained),
                       retained_histogram_digest=instantiate_rank3.histogram_digest(
                           retained['child_multiplicities']))
    if price:
        point = rank3contract.price(interval, retained)
        published_top = Q(json.loads((HERE / 'certificate.json').read_text())['top']['kappa'])
        out['point'] = dict(
            coarse=str(point['coarse']), coarse_decimal=float(point['coarse']),
            next_excluded=str(point['next_excluded']),
            leaf=str(point['leaf']), kappa=str(point['kappa']),
            kappa_decimal=float(point['kappa']), binding=point['binding'],
            complex_ceiling=str(point['complex_ceiling']),
            ceiling_gap=str(point['ceiling_gap']),
            tightest_constraint=str(point['assembly']['minimum_constraint']),
            budget_is_the_leaf=(point['budget'] == point['leaf']),
            adjacent_grid_rejected=point['adjacent_grid_rejected'],
            gain_vs_published_top_percent=float(point['kappa'] / published_top - 1) * 100)
    out['verdict'] = ('the rung exists on this row: %d banks, no padding, kappa %s (%s-bound)'
                      % (step['banks'], out.get('point', {}).get('kappa', 'NOT PRICED'),
                         out.get('point', {}).get('binding', 'NOT PRICED')))
    return out


def corpus(root=None, priced=False, interval=None, leaf=None):
    """Every distinct width-66 row this repository's certificates carry, with the same reading.

    Rows of another width are another word and another contract (`widths66.py` prices what a
    narrower modulus would take), so they are counted and left out rather than misreported.
    """
    root = root or suppliers.REPO
    found, seen = [], {}
    for path, where, profile in suppliers.walk_profiles(root):
        if profile['m'] != WIDTH or max(profile['child_multiplicities']) > WIDTH:
            continue
        if WIDTH * profile['W'] - profile['total_rank'] != profile['N']:
            continue
        key = (profile['W'], profile['N'],
               tuple(sorted(profile['child_multiplicities'].items())))
        row = seen.get(key)
        if row is None:
            row = seen[key] = dict(m=WIDTH, W=profile['W'], N=profile['N'], L=0,
                                   child_multiplicities=profile['child_multiplicities'],
                                   total_rank=profile['total_rank'],
                                   maxchild=max(profile['child_multiplicities']),
                                   sources=[])
            found.append(row)
        row['sources'].append(path + ('#' + where if where else ''))
    for row in found:
        row.update(analyze(row, interval=interval, leaf=leaf, price=priced))
        row['sources'] = sorted(set(row['sources']))
    return dict(rows=found, width=WIDTH,
                note='rows of another width are not this contract\'s; they are counted and left '
                     'out.  A row appears once per distinct (W, deficit, histogram), with every '
                     'certificate that carries it listed.')


def build(priced=True):
    """The stability measurement: the heads, the corpus, and what is stable."""
    interval = ledger3.engine()
    schedule, arithmetic = ledger3.run1()
    leaf = arithmetic.build(schedule.build())['ordinary_leaf']
    heads, rows = [], {}
    for sha, date, short, subject, source in HEADS:
        path = HERE / source
        profile = profile_of(path)
        facts = analyze(profile, interval=interval, leaf=leaf, price=priced)
        label = row_label(profile)
        rows.setdefault(label, dict(facts, source=source))
        heads.append(dict(sha=sha, short=short, date=date, subject=subject, source=source,
                          bytes=len(path.read_bytes()), sha256=digest(path),
                          row=label, rank3_eligible=facts['rank3_eligible']))
    eligible = [head for head in heads if head['rank3_eligible']]
    rung_rows = sorted({head['row'] for head in eligible})
    points = {rows[label].get('point', {}).get('kappa') for label in rung_rows}
    next_eligible = {label: rows[label]['rung']['retained_eligibility'] for label in rung_rows}
    return dict(
        analysis='whether the rank-3 rung survives #233 moving, and whether it is a property of '
                 'the family or of one row: every head that touches the layer certificate, and '
                 'every other width-66 row the repository carries',
        criterion=dict(
            rule='a family of rank r with n children in the ledger row fills whole width-m banks '
                 'exactly when m | r * n.  At m = 66 that is a condition on the count alone: the '
                 'ledger-row count must be a multiple of 66 / gcd(r, 66),',
            families={rank: criterion(int(rank))
                      for rank in sorted(rows[heads[-1]['row']]['families_at_width'],
                                         key=int)},
            why='so eligibility is a modular accident of each family\'s child count, and it '
                'moves whenever the supplier\'s pairing moves a few children between ranks.  The '
                'module checks the rule against the ledger\'s own divisibility test on every row '
                'it examines.',
            registers_short='the third number recorded per family: how many registers the family '
                            'misses a whole bank by, which is how close a row came.'),
        heads=heads,
        rows=rows,
        stability=dict(
            heads=len(heads), distinct_rows=len(rows), heads_where_the_rung_exists=len(eligible),
            heads_where_it_does_not=len(heads) - len(eligible),
            eligibility_stable=len(rung_rows) == len(heads),
            price_stable=(len(points) == 1),
            kappas=sorted(str(k) for k in points),
            rows_where_the_rung_exists=sorted(rung_rows),
            next_rung_eligible_sets=next_eligible,
            next_rung_stable=len({json.dumps(v) for v in next_eligible.values()}) == 1),
        corpus=corpus(priced=True, interval=interval, leaf=leaf),
        reading='the rung\'s eligibility is not stable across the heads -- it exists on the last '
                'two (246f6f9, 109a857) and not on the first four, whose row is one rank-3 child '
                'per copy short of the 22-multiple the criterion needs, i.e. nine registers over '
                'the ledger\'s three copies, not a different family but a different rounding '
                '-- while the price is stable wherever it exists, because the bit leaf binds on '
                'both and the assembly\'s floor is a function of the budget rather than of the '
                'coarse saving.  The next rung\'s eligibility, by contrast, is not stable '
                'either: it is rank 4 only on the pinned head, and the retained eligibility '
                'differs between the two heads that carry the rung.  And no other width-66 row '
                'in the repository carries the rung at all, so it is a property of this row and '
                'not of the family.  What this does not measure: any head that does not exist '
                'yet, and any row outside the repository.  Some corpus rows are carried by an '
                'audit sub-block rather than by a `complex_profile` -- the walk finds every '
                'profile a certificate holds, and each row lists its sources.',
        status='MEASURED AND MACHINE-CHECKED: verify.py -> check_rank3_stability re-derives every '
               'head from the vendored certificates, re-scores the corpus, and asserts the '
               'stability reading and the modular criterion it rests on.')


def main():
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    out = build()
    target = HERE / 'rank3-stability.json'
    target.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + '\n',
                      newline='\n')
    print('criterion  %s' % out['criterion']['rule'])
    print('           ' + ', '.join('%s -> %s' % (value['rank'], value['rule'])
                                   for _, value in sorted(out['criterion']['families'].items(),
                                                          key=lambda kv: int(kv[0]))))
    print('heads      %d across %d distinct rows; the rung exists on %d'
          % (out['stability']['heads'], out['stability']['distinct_rows'],
             out['stability']['heads_where_the_rung_exists']))
    for head in out['heads']:
        row = out['rows'][head['row']]
        print('  %-9s %s  rank3 %-5s elig %-16s %s'
              % (head['short'], head['row'], head['rank3_eligible'], row['eligibility'],
                 row['verdict']))
    print('price      stable: %s (kappas %s); next rung stable: %s'
          % (out['stability']['price_stable'], out['stability']['kappas'],
             out['stability']['next_rung_stable']))
    print('corpus     %d distinct width-66 rows; the rung exists on %d'
          % (len(out['corpus']['rows']),
             sum(1 for row in out['corpus']['rows'] if row['rank3_eligible'])))
    for row in sorted(out['corpus']['rows'], key=lambda r: -r['W']):
        print('  W=%-6d elig %-16s r3 %-5s short %-3d %s'
              % (row['W'], row['eligibility'], row['rank3_eligible'],
                 row['families_at_width'][str(FAMILY)]['registers_short'], row['verdict'][:52]))
    print('write ' + str(target))


if __name__ == '__main__':
    main()
