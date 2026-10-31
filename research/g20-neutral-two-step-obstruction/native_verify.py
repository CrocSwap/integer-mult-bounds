"""Complete native-route lower bill after every cost-neutral first G20 rewrite.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Worker C: indexed scalar domain and exact prefix replay. Worker D: native metric,
all-path lower bound and disjoint partition sign witnesses. No new kappa.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import argparse
import gzip
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CERTIFICATE_SHA = '33c7d4f11e530a7cf64d3ca38f8740913767ec055af8ad6e7669126f0c09d121'
ONE_STEP_SHA = 'ed99ab025914795eb07531cf9b83f213e3442ab965dac4ad7354115446fea948'
DIRECT_SHA = 'b0d62e1faa9aaa7bdde5aac5b55b5d226272461238fa960cc0ad0df0b054bb47'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def module(name, filename, digest):
    path = PACKAGE / filename
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == digest, 'implementation bytes: ' + filename)
    result = ModuleType(name)
    result.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def descriptor(candidate):
    left, right, a, b, corrections = candidate
    return [left, right, a, b, len(corrections)]


def census(primary, native, prefix, original):
    word, records, retained = primary.load_inputs()
    raw_frames = gzip.decompress((ROOT / 'research/bit-g20-contact-expansion-bound/FRAMES.json.gz').read_bytes())
    need(sha256(raw_frames).hexdigest() == native.FRAME_SHA, 'exact rational frame catalogue')
    edges, dims = native.native_graph(json.loads(raw_frames)['frames'])
    need(len(edges) == 52624 and len(dims) == 645, 'complete native graph')
    need(all(edges[pair] == rank for pair, rank in retained.items()), 'retained edges native-admitted')
    distances = native.metric(edges, dims)
    raw_one_step = (PACKAGE / 'NATIVE-ONE-STEP.json.gz').read_bytes()
    need(sha256(raw_one_step).hexdigest() == ONE_STEP_SHA, 'independent one-step certificate bytes')
    one_step = json.loads(gzip.decompress(raw_one_step))
    need(native.metric_digest(distances) == one_step['graph']['metric_sha256'], 'exact full metric')
    direct_raw = gzip.decompress((PACKAGE / 'CERTIFICATE.json.gz').read_bytes())
    need(sha256(direct_raw).hexdigest() == DIRECT_SHA, 'frozen direct certificate bytes')
    direct = json.loads(direct_raw)
    old_branches = {tuple(branch['first']): branch for branch in direct['branches']}
    owned, width = set(word['owned']), len(word['start'])
    endpoint = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
                for i in range(width)]
    need(primary.scalar_rows(records, width, owned) == endpoint, 'source all-column endpoint')
    base, missing = primary.emit(records, word['start'], word['final'], owned, retained)
    need(missing is None and dict(base) == {int(k): v for k, v in one_step['base_paid'].items()}, 'source exact invoice')
    relaxed, _, new_paid = native.invoice(records, word['start'], word['final'], owned, distances, retained)
    need(relaxed == base and not new_paid, 'source exact metric attainer')
    shape_proofs = {}

    def sign(histogram):
        delta = native.signed_delta(histogram, base)
        key = tuple(map(tuple, delta))
        if key not in shape_proofs:
            shape_proofs[key] = native.partition(delta)
        return delta, native.check_partition(delta, shape_proofs[key])

    first_domain = list(primary.candidates(records))
    need(len(first_domain) == len(one_step['outcomes']) == 2270, 'complete first domain')
    saved = prefix.snapshots(records, first_domain, word['start'], owned, distances, edges)
    first, first_counts = [], Counter()
    for candidate, previous in zip(first_domain, one_step['outcomes'], strict=True):
        header = descriptor(candidate)
        need(header == [previous['first'], previous['last'], *previous['gate'], previous['contacts']], 'independent full first domain')
        bill, new_paid = prefix.changed_invoice(records, candidate, saved, word['final'], endpoint)
        delta, verdict = sign(bill)
        need(delta == previous['delta'] and verdict == previous['sign'], 'independent full first invoice equality')
        first_counts[verdict] += 1
        if verdict == 'zero':
            need(not new_paid, 'first zero has direct native paid attainer')
            first.append(candidate)
    del saved
    need(len(first) == 22 and first_counts == {'strict_loss': 2248, 'zero': 22}, 'complete neutral first set')
    need(set(old_branches).issubset({tuple(descriptor(c)) for c in first}), 'all old longer neutral first words included')
    branches, totals = [], Counter()
    for first_candidate in first:
        changed = primary.rewrite(records, first_candidate)
        candidates = list(primary.candidates(changed))
        saved = prefix.snapshots(changed, candidates, word['start'], owned, distances, edges)
        header = descriptor(first_candidate)
        old = old_branches.get(tuple(header))
        if old is not None:
            need([descriptor(c) for c in candidates] == [row[:5] for row in old['outcomes']], 'complete old second-domain inclusion')
        rows, counts, shapes = [], Counter(), Counter()
        for candidate in candidates:
            bill, new_paid = prefix.changed_invoice(changed, candidate, saved, word['final'], endpoint)
            delta, verdict = sign(bill)
            need(verdict != 'zero' or not new_paid, 'second zero has direct native paid attainer')
            counts[verdict] += 1
            counts['candidates'] += 1
            counts['zero_contact'] += not candidate[4]
            shapes[tuple(map(tuple, delta))] += 1
            rows.append(descriptor(candidate) + [delta])
        del saved
        totals.update(counts)
        branches.append({'first': header, 'old_longer_domain': old is not None,
                         'counts': dict(sorted(counts.items())),
                         'shapes': [[shape, count] for shape, count in sorted(shapes.items())], 'outcomes': rows})
    need(totals == {'candidates': 49865, 'strict_loss': 49392, 'zero': 473, 'zero_contact': 47}, 'complete second-domain counts')
    return {'schema': 'g20-all-native-all-neutral-two-step/v1', 'base_paid': dict(sorted(base.items())),
            'first_counts': dict(sorted(first_counts.items())), 'counts': dict(sorted(totals.items())),
            'graph': one_step['graph'], 'branches': branches,
            'partitions': [{'delta': key, 'proof': proof} for key, proof in sorted(shape_proofs.items())],
            'all_column_width': width, 'direct_certificate_sha256': DIRECT_SHA,
            'native_one_step_compressed_sha256': ONE_STEP_SHA,
            'scalar_controls': primary.controls(), 'native_controls': original.controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    expected = None
    if args.output is None:
        expected = gzip.decompress((PACKAGE / 'NATIVE-CERTIFICATE.json.gz').read_bytes())
        need(sha256(expected).hexdigest() == CERTIFICATE_SHA, 'native certificate bytes')
    primary = module('indexed_scalar', 'verify.py', '30e916093afd3f859f26a6e257f66659452999c13d1d3164f1e6d733b297e488')
    native = module('native_floor', 'native_floor.py', '2a9b4cc47ce8ad3a4ab1a0467dda2737202ef9f982da564bd64fe0d3fb9cb5d3')
    prefix = module('prefix_invoice', 'prefix_invoice.py', '83886f01fbe659b9e00347259f7d5acb3e4bcb1e41201e57995395b6fa7bb6bb')
    original = module('native_original_census', 'native_one_step.py', '5bfb36d2854cd59608dcd4a26759d2646dfa63dba1bd371b8dd2812569f2300a')
    result = census(primary, native, prefix, original)
    payload = canonical(result)
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT), 'output must be outside checkout')
        args.output.write_bytes(payload)
    else:
        need(payload == expected, 'complete native two-step certificate mismatch')
    print(json.dumps({'counts': result['counts'], 'first_counts': result['first_counts'], 'graph': result['graph'],
                      'certificate_sha256': sha256(payload).hexdigest()}, sort_keys=True))
    print('PASS_G20_NATIVE_NEUTRAL_TWO_STEP')


if __name__ == '__main__':
    main()
