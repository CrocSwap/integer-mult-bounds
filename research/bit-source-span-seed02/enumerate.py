#!/usr/bin/env python3
"""Generate the bounded source-span census. Hanson Sun, OpenAI Codex; Apache-2.0.

Integer echelon geometry and packed F2 rows. verify.py uses neither this module
nor its geometry, event builder, response representation, or elimination code.
"""
import argparse
import bisect
from collections import Counter
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
SOURCE_SHA256 = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def support(bits):
    return [i for i in range(bits.bit_length()) if bits >> i & 1]


def integer_basis(vectors):
    out = []
    for vector in vectors:
        row = list(vector)
        for pivot, old in out:
            if row[pivot]:
                a, b = old[pivot], row[pivot]
                row = [a*x-b*y for x, y in zip(row, old)]
                divisor = 0
                for x in row:
                    divisor = gcd(divisor, x)
                if divisor:
                    row = [x//divisor for x in row]
        if any(row):
            pivot = next(i for i, x in enumerate(row) if x)
            if row[pivot] < 0:
                row = [-x for x in row]
            out.append((pivot, row))
            out.sort()
    return out


def in_span(vector, basis):
    row = list(vector)
    for pivot, old in basis:
        if row[pivot]:
            a, b = old[pivot], row[pivot]
            row = [a*x-b*y for x, y in zip(row, old)]
            divisor = 0
            for x in row:
                divisor = gcd(divisor, x)
            if divisor:
                row = [x//divisor for x in row]
    return not any(row)


def solve(rows, target):
    """Return (source mask, None) or (None, separating input-coordinate mask)."""
    pivots = {}
    for source, vector in rows:
        mask = 1 << source
        for pivot in sorted(pivots, reverse=True):
            if vector >> pivot & 1:
                old, oldmask = pivots[pivot]
                vector ^= old
                mask ^= oldmask
        if vector:
            pivots[vector.bit_length()-1] = (vector, mask)
    remainder, answer = target, 0
    for pivot in sorted(pivots, reverse=True):
        if remainder >> pivot & 1:
            old, mask = pivots[pivot]
            remainder ^= old
            answer ^= mask
    if not remainder:
        return answer, None
    dual = remainder & -remainder
    for pivot in sorted(pivots):
        if (pivots[pivot][0] & dual).bit_count() % 2:
            dual |= 1 << pivot
    require((target & dual).bit_count() % 2 == 1, 'internal separating target')
    require(all((row & dual).bit_count() % 2 == 0 for _, row in rows),
            'internal separating sources')
    return None, dual


def make_events(word):
    v, n = word['v'], 2*word['v']+word['R']
    rows = [1 << i if i < v else 0 for i in range(n)]
    events, reads = [], {q: [] for q in range(2*v, n) if q not in word['ret']}
    frames = word['start'][:]
    for section in ('A', 'B'):
        if section == 'B':
            for q in word['ret']:
                events.append(('COPY', q, frames[q], q, []))
            for i, slots in enumerate(word['scatter']):
                for k in slots:
                    rows[v+i] ^= rows[word['ret'][k]]
        for index, (frame, dest, sources) in enumerate(word[section]):
            time = len(events)
            events.append((section, index, frame, dest, sources))
            for q in sources:
                if q in reads:
                    target = rows[q]
                    # Normalize the entire source part, allowing cancellation
                    # with source operands already present in the original gate.
                    for s in sources:
                        if s < v:
                            target ^= rows[s]
                    reads[q].append(dict(time=time, section=section, index=index,
                                         destination=dest, target=target,
                                         sources=rows[:v]))
            for s in sources:
                rows[dest] ^= rows[s]
            for r in (dest, *sources):
                frames[r] = frame
    return events, reads


def generate(word):
    v, n = word['v'], 2*word['v']+word['R']
    bases = [integer_basis(word['lines'][i] for i in f) for f in word['frames']]
    closures = [sum(1 << i for i, line in enumerate(word['lines']) if in_span(line, b))
                for b in bases]
    require(closures == [sum(1 << i for i in f) for f in word['frames']],
            'source frame catalogue is not rationally closed')

    def le(a, b):
        return closures[a] & ~closures[b] == 0

    events, reads = make_events(word)
    summary = Counter()
    witnesses, feasible = [], []
    helpers = list(reads)
    # The assignment seed diversifies traversal; no randomized search or restart.
    for q in helpers[2:] + helpers[:2]:
        touches = [[(-1, word['start'][r])] for r in range(n)]
        for time, (_, _, frame, dest, sources) in enumerate(events):
            if dest == q or q in sources:
                continue
            for r in (dest, *sources):
                touches[r].append((time, frame))
        for r in range(n):
            touches[r].append((len(events), word['final'][r]))
        clean_fail, frame_fail = [], []
        helper_solutions = []
        for read in reads[q]:
            time, dest = read['time'], read['destination']

            def interval(register):
                at = bisect.bisect_left(touches[register], (time, -1))
                return touches[register][at-1][1], touches[register][at][1]

            ld, ud = interval(dest)
            eligible = []
            for s in range(v):
                if s != dest:
                    ls, us = interval(s)
                    if le(ld, us) and le(ls, ud):
                        eligible.append(s)
            all_sources = [s for s in range(v) if s != dest]
            unconstrained, clean_dual = solve([(s, read['sources'][s]) for s in all_sources],
                                              read['target'])
            mask, dual = solve([(s, read['sources'][s]) for s in eligible], read['target'])
            summary['reads'] += 1
            summary['all_source_span_pass_reads' if unconstrained is not None
                    else 'all_source_span_fail_reads'] += 1
            summary['frame_span_pass_reads' if mask is not None
                    else 'frame_span_fail_reads'] += 1
            record = dict(helper=q, section=read['section'], index=read['index'],
                          destination=dest, target=support(read['target']),
                          eligible_sources=eligible)
            if unconstrained is None:
                clean_fail.append(dict(record, kind='clean-span', dual=support(clean_dual)))
            elif mask is None:
                frame_fail.append(dict(record, kind='frame-span', dual=support(dual)))
            else:
                helper_solutions.append(dict(record, source_mask=support(mask)))
        if clean_fail:
            summary['clean_span_blocked_helpers'] += 1
            witnesses.append(clean_fail[0])
        elif frame_fail:
            summary['frame_span_blocked_helpers'] += 1
            witnesses.append(frame_fail[0])
        else:
            summary['necessary_condition_survivors'] += 1
            feasible.append(dict(helper=q, reads=helper_solutions))
    summary.update(helpers=n-2*v, retained_helpers=len(word['ret']),
                   screened_helpers=len(reads), rational_frames=len(bases))
    return dict(schema_version=1, assignment_seed=2, source=SOURCE,
                source_sha256=SOURCE_SHA256, summary=dict(sorted(summary.items())),
                exclusions=sorted(witnesses, key=lambda r: r['helper']),
                survivors=sorted(feasible, key=lambda r: r['helper']))


def certificate_text(result):
    """One exclusion per line keeps the finite witness inventory reviewable."""
    fields = []
    for key, value in sorted(result.items()):
        if key == 'exclusions':
            encoded = '[\n' + ',\n'.join('    ' + json.dumps(row, sort_keys=True)
                                         for row in value) + '\n  ]'
        else:
            encoded = json.dumps(value, sort_keys=True)
        fields.append('  ' + json.dumps(key) + ': ' + encoded)
    return '{\n' + ',\n'.join(fields) + '\n}\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='new certificate file; never overwrites')
    args = parser.parse_args()
    payload = (ROOT / SOURCE).read_bytes()
    require(hashlib.sha256(payload).hexdigest() == SOURCE_SHA256, 'source hash mismatch')
    result = generate(json.loads(gzip.decompress(payload)))
    if args.output:
        with args.output.open('x') as out:
            out.write(certificate_text(result))
    else:
        require(result == json.loads((HERE / 'CERTIFICATE.json').read_text()),
                'regenerated certificate differs')
    print('PASS_SOURCE_SPAN_GENERATION', json.dumps(result['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
