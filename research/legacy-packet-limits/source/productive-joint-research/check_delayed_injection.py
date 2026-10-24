"""Check the delay screen with reverse transport and another tree method.

Use literal subspace point sets and Kruskal's algorithm. Do not import the
screen or the upstream verifier. This is a second method, not a second
human or agent review. Prepared with OpenAI Codex assistance.
"""
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip
import hashlib
import json

if not __debug__:
    raise SystemExit('Run with assertions enabled.')

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
BASE = RUN/'frontier/refresh-6/replay564-root'
receipts = []


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


for name in ('zero', 'four', 'eight'):
    cp = BASE/(name+'-cold-local/CANONICAL-WORD.json.gz')
    rp = BASE/(name+'-cold-word/FULL-WORD.json.gz')
    recorded = HERE/(name.upper()+'-DELAYED-INJECTION.json')
    w, raw, report = read(cp), read(rp), read(recorded)
    assert report['word_sha256'] == hashlib.sha256(cp.read_bytes()).hexdigest()
    frames = w['frames']
    assert len(frames[1]) == 9
    assert all(len(frames[f]) == 8 for f in w['center_frames'])
    spaces = []
    for frame in frames:
        points = {0}
        for row in frame:
            points |= {p^row for p in points}
        assert len(points) == 1 << len(frame)
        spaces.append(sum(1 << p for p in points))

    @lru_cache(None)
    def tree(start, used):
        vertices = sorted(set(used)|{start})
        edges = []
        for i, a in enumerate(vertices):
            for b in vertices[i+1:]:
                common = (spaces[a]&spaces[b]).bit_count()
                assert common > 0 and common & (common-1) == 0
                distance = len(frames[a])+len(frames[b])-2*(common.bit_length()-1)
                edges.append((distance, a, b))
        parent = {v: v for v in vertices}

        def find(v):
            while parent[v] != v:
                v = parent[v]
            return v

        total = 0
        for distance, a, b in sorted(edges):
            a, b = find(a), find(b)
            if a != b:
                parent[a] = b
                total += distance
        return total

    centers = {r: i for i, r in enumerate(w['centers'])}
    initial = [[F(0)]*8 for _ in range(112)]
    for op in w['cut']:
        initial[op[1]-112][centers[op[2]]] += F(op[3], op[4])
    vector = [row.copy() for row in initial]
    current = w['start'].copy()
    for op in w['A']:
        for r in [op[1]]+([op[2]] if op[0] == 'add' else []):
            current[r] = op[-1]
    events = []
    for op in w['B']:
        assert op[0] in ('add', 'scale')
        for r in [op[1]]+([op[2]] if op[0] == 'add' else []):
            old = current[r]
            current[r] = op[-1]
            if old != current[r] and 112 <= r < 224:
                events.append(('frame', r-112, old, current[r]))
        if 112 <= op[1] < 224:
            t = op[1]-112
            if op[0] == 'scale':
                q = F(op[2], op[3])
                vector[t] = [q*x for x in vector[t]]
            elif 112 <= op[2] < 224:
                q, s = F(op[3], op[4]), op[2]-112
                vector[t] = [x+q*y for x, y in zip(vector[t], vector[s])]
            else:
                assert op[2] < 112 or op[2] >= 224
        events.append(('scalar', op))
    # Bind the transported object to the literal complete decoder, not
    # only to a numerical rank or a frame histogram.
    tau = lambda x: x ^ (43 if (x&43).bit_count()%2 else 0)
    expected = [[F(0)]*8 for _ in range(112)]
    for port, root in zip(raw['ports'], raw['root_lines']):
        expected[w['ports'].index(tau(port))] = [F(x, 4) for x in root]
    assert vector == expected
    omitted = [row.copy() for row in initial]
    first = w['cut'][0]
    omitted[first[1]-112][centers[first[2]]] -= F(first[3], first[4])
    for op in w['B']:
        if not 112 <= op[1] < 224:
            continue
        t = op[1]-112
        if op[0] == 'scale':
            q = F(op[2], op[3])
            omitted[t] = [q*x for x in omitted[t]]
        elif 112 <= op[2] < 224:
            q, s = F(op[3], op[4]), op[2]-112
            omitted[t] = [x+q*y for x, y in zip(omitted[t], omitted[s])]
    differences = sum(a != b for x, y in zip(omitted, expected) for a, b in zip(x, y))
    assert differences > 0
    best = [1000]*8
    productive_best = [1000]*8
    count = 0
    target_frames = current[112:224]

    def examine():
        values, productive = [], []
        for k in range(8):
            used = tuple(sorted({target_frames[t] for t in range(112) if vector[t][k]}))
            assert used
            start = w['center_frames'][k]
            values.append(tree(start, used))
            through = []
            for f in used:
                intersection = (spaces[start]&spaces[f]).bit_count().bit_length()-1
                through.append(17-2*intersection)
            bound = max(tree(start, tuple(sorted(set(used)|{1}))), max(through))
            bound += (1-bound)%2
            productive.append(bound-1)
        return values, productive

    values, productive = examine()
    best = [min(x, y) for x, y in zip(best, values)]
    productive_best = [min(x, y) for x, y in zip(productive_best, productive)]
    common = sum(values)
    count += 1
    for event in reversed(events):
        if event[0] == 'frame':
            _, t, old, new = event
            assert target_frames[t] == new
            target_frames[t] = old
        else:
            op = event[1]
            if 112 <= op[1] < 224:
                t = op[1]-112
                if op[0] == 'scale':
                    q = F(op[3], op[2])
                    vector[t] = [q*x for x in vector[t]]
                elif 112 <= op[2] < 224:
                    q, s = F(-op[3], op[4]), op[2]-112
                    vector[t] = [x+q*y for x, y in zip(vector[t], vector[s])]
        values, productive = examine()
        best = [min(x, y) for x, y in zip(best, values)]
        productive_best = [min(x, y) for x, y in zip(productive_best, productive)]
        common = min(common, sum(values))
        count += 1
    assert vector == initial and target_frames == [0]*112
    assert count == report['cuts_checked']
    assert best == [x['lower_copy_transition_rank'] for x in report['best_center_cuts']] == [8]*8
    assert common == report['best_common_cut']['lower_copy_transition_rank_sum'] == 64
    assert productive_best == [x['lower_extra_rank'] for x in report['productive_carrier_best_cuts']] == [16]*8
    assert sum(productive_best) == report['productive_carrier_extra_rank_lower_sum'] == 128
    receipts.append(dict(provider=name, cuts_checked=count, center_lower_bounds=best,
                         common_cut_lower=common, full_decoder_identity='R/4',
                         productive_carrier_extra_rank_lower_sum=sum(productive_best),
                         omitted_first_cut_term_nonzero_output_entries=differences,
                         inputs={str(p.relative_to(RUN)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (cp, rp, recorded)}))
result = dict(status='PASS_REVERSE_TRANSPORT_POINTSET_KRUSKAL_METHOD', providers=receipts,
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              scope='Second algorithm on the same pinned physical words. This is not an independent agent review. It proves only the one-held-copy, one-injection-cut route lower bound; it does not close all productive joint operators.')
(HERE/'DELAYED-INJECTION-SECOND-METHOD.json').write_text(json.dumps(result, indent=2)+'\n')
print(result['status'])
