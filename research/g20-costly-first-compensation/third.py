"""Exact third neighborhood of the five attained costly-first ties.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json, gzip, argparse, collections, hashlib
from types import ModuleType
from pathlib import Path
P = Path(__file__).resolve().parent

def mod(name, path):
    m = ModuleType(name)
    m.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m
M = mod('newv', P / 'verify.py')
M.authenticate()
V = mod('oldv', M.ROOT / M.PREFIX / 'verify.py')
T = mod('trace', P / 'trace.py')
D = mod('domain', P / 'domain.py')
N = mod('native', M.ROOT / M.PREFIX / 'native_floor.py')
w, rec, own, end, edges, dist, base, old = M.prepare(V, N)
firsts = list(V.candidates(rec))
full = json.loads(gzip.decompress((P / 'CERTIFICATE.json.gz').read_bytes()))
tie_rows = [{'firstid': x['first_id'], 'second': x['second']} for x in full['exceptions'] if x['sign'] == 'zero']
M.need(len(tie_rows) == 5, 'five attained hosts')
allcounts = collections.Counter()
branches = []
shapes = collections.Counter()
prior = json.loads(gzip.decompress((M.ROOT / M.PREFIX / 'NATIVE-CERTIFICATE.json.gz').read_bytes()))
first_index = {tuple(M.descriptor(c)): c for c in firsts}
known = set()
known_paths = 0
hashword = lambda records: hashlib.sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest()
for branch in prior['branches']:
    oldfirst = V.rewrite(rec, first_index[tuple(branch['first'])])
    oldindex = {tuple(M.descriptor(c)): c for c in V.candidates(oldfirst)}
    for row in branch['outcomes']:
        if row[5]:
            continue
        known_paths += 1
        known.add(hashword(V.rewrite(oldfirst, oldindex[tuple(row[:5])])))
M.need(known_paths == 473 and len(known) == 242, 'pinned previous neutral-first tie catalogue')
for tie in tie_rows:
    first = V.rewrite(rec, firsts[tie['firstid']])
    second = next((c for c in V.candidates(first) if M.descriptor(c) == tie['second']))
    host = V.rewrite(first, second)
    tr = T.Trace(host, w['start'], w['final'], own, dist)
    cs = list(V.candidates(host))
    M.need(cs == list(D.candidates(host)), 'complete independent third domain')
    M.need(tr.endpoint == end and tr.base == [base[i] for i in range(9)], 'host exact endpoint and invoice')
    M.need(hashword(host) not in known, 'new literal costly-first tie')
    M.need(not any((e[0] == 'ADD' and (not value[1]) for e, value in zip(host, tr.values, strict=True))), 'literal host normalization')
    hostpaid, _, hostnew = N.invoice(host, w['start'], w['final'], own, dist, edges)
    M.need(hostpaid == base and (not hostnew), 'host direct native attainer')
    counts = collections.Counter()
    neutral = []
    h = hashlib.sha256()
    for c in cs:
        delta = tuple(tr.delta(c)[1:])
        q = M.hinges(delta)
        if min(q) < 0:
            raise ValueError(('candidate', tie, M.descriptor(c), delta))
        if not any(delta):
            final = V.rewrite(host, c)
            bill, _, new = N.invoice(final, w['start'], w['final'], own, dist, edges)
            M.need(bill == base and (not new), 'zero third native attainer')
            M.need(V.scalar_rows(final, 685, own) == end, 'zero third685-column endpoint')
            neutral.append(M.descriptor(c))
        verdict = 'strict_loss' if any(delta) else 'zero'
        counts[verdict] += 1
        counts['candidates'] += 1
        counts['zero_contact'] += not c[4]
        shapes[delta] += 1
        h.update(json.dumps([M.descriptor(c), delta], separators=(',', ':')).encode() + b'\n')
    allcounts.update(counts)
    branches.append({'firstid': tie['firstid'], 'counts': dict(counts), 'digest': h.hexdigest(), 'neutral': neutral})
result = {'prior_tie_paths': known_paths, 'prior_distinct_words': len(known), 'counts': dict(allcounts), 'branches': branches, 'shapes': [[d, n, M.hinges(d)] for d, n in sorted(shapes.items())]}
payload = M.canonical(result)
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
if args.output:
    M.need(not args.output.resolve().is_relative_to(M.ROOT), 'external receipt output')
    args.output.write_bytes(payload)
else:
    M.need(payload == gzip.decompress((P / 'THIRD.json.gz').read_bytes()), 'exact third receipt')
print(json.dumps({'counts': dict(allcounts), 'shapes': len(shapes)}, sort_keys=True))
print('PASS_G20_FIVE_TIES_THIRD_NEIGHBORHOOD')
