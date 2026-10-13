#!/usr/bin/env python3
"""Screen exact protected-response-preserving scalar source exchanges.

Every data column and every already-entering dirty helper is protected. Other
dirty compensation is reconstructed later by the native auditor. Source
exchanges keep scalar frame labels and must pass the complete frame chain.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import time

from search_suffix_kernels import add, basis, inside, frames, entropy


def signature(row):
    if not row:
        return (), Q(1)
    value = row[min(row)]
    return tuple((key, q / value) for key, q in sorted(row.items())), value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--retain', type=int, default=20)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    original = g.profile(word)
    protected = set(range(112)) | set(map(int, word['start_extra']))
    rows = [{r: Q(1)} if r in protected else {} for r in range(728)]
    buckets = defaultdict(set)
    signs = [signature(row) for row in rows]
    for r, (key, _) in enumerate(signs):
        if not 112 <= r < 224:
            buckets[key].add(r)
    found, counts = [], Counter()
    start = time.monotonic()
    for part in ('A', 'cut', 'B'):
        if part != 'cut':
            _, before, after = frames(word, part)
        for index, event in enumerate(word[part]):
            target = event[1]
            if part != 'cut' and event[0] == 'add':
                source, q = event[2], Q(event[3], event[4])
                frame = basis(tuple(event[-1]))
                key, value = signs[source]
                for donor in sorted(buckets[key] - {source, target}):
                    if not inside(before[index][donor], frame) or not inside(frame, after[index][donor]):
                        continue
                    coefficient = q * value / signs[donor][1]
                    if coefficient.denominator & (coefficient.denominator - 1):
                        continue
                    counts['exact_protected_exchanges'] += 1
                    candidate = copy.deepcopy(word)
                    new = candidate[part][index]
                    new[2], new[3], new[4] = donor, coefficient.numerator, coefficient.denominator
                    try:
                        profile = g.profile(candidate)
                    except AssertionError:
                        counts['rejected_frame_chain'] += 1
                        continue
                    candidate['cleanup'] = [g.inverse(e, g.FULL)
                                            for e in reversed(candidate['A'] + candidate['B'])
                                            if not 112 <= e[1] < 224]
                    delta = {r: profile[r] - original[r] for r in set(profile) | set(original)
                             if profile[r] != original[r]}
                    assert sum(r * n for r, n in delta.items()) == 0
                    candidate['report']['local_profile'] = dict(profile)
                    record = dict(part=part, index=index, old_source=source, new_source=donor,
                                  old_coefficient=str(q), new_coefficient=str(coefficient),
                                  protected_columns=len(protected), profile_delta=delta,
                                  entropy_gain=entropy(delta))
                    found.append((record, candidate))
            previous_key = signs[target][0]
            if event[0] == 'add':
                add(rows[target], rows[event[2]], Q(event[3], event[4]))
            else:
                rows[target] = {key: value * Q(event[2], event[3]) for key, value in rows[target].items()}
            signs[target] = signature(rows[target])
            if not 112 <= target < 224:
                buckets[previous_key].discard(target)
                buckets[signs[target][0]].add(target)
        print(json.dumps(dict(part=part, counts=dict(counts), seconds=time.monotonic() - start)), flush=True)
    found.sort(key=lambda pair: (-pair[0]['entropy_gain'], pair[0]['part'], pair[0]['index']))
    for index, (record, candidate) in enumerate(found[:args.retain]):
        name = 'candidate-%03d' % index
        (args.out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        (args.out / (name + '.json.gz')).write_bytes(g.dump(candidate))
    report = dict(status='PASS_EXACT_PROTECTED_SOURCE_EXCHANGE_SCREEN',
                  source_content_sha256=hashlib.sha256(raw).hexdigest(),
                  counts=dict(counts), candidates=[record for record, _ in found],
                  seconds=time.monotonic() - start,
                  scope='Exact prefix rows on all original data and entering-helper columns '
                        'must agree up to a dyadic-compatible scalar. Every source replacement '
                        'passes the actual frame chain. Full native dirty compensation and '
                        'phase/owner/moment verification remain separate.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(counts=dict(counts), candidates=len(found),
                          strict_entropy_gains=sum(record['entropy_gain'] > 1e-10 for record, _ in found),
                          best=found[0][0] if found else None), indent=2))


if __name__ == '__main__':
    main()
