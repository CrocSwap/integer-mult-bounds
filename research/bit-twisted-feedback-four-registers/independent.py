"""Truth-table BFS corroboration; imports no primary or predecessor code.

Apache-2.0. Prepared for ywz65 with substantial OpenAI Codex assistance.
"""
from collections import Counter, deque
import hashlib
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def walk(h, t, feedback):
    n = h+t
    gates = [(d,s) for d in range(n) for s in range(n) if d != s
             and (feedback or d >= h or s < h)]
    trans = [bytes(x ^ (((x >> s) & 1) << d) for x in range(256))
             for d,s in gates]
    initial = bytes(range(1 << n))
    lengths = {initial:0}
    queue = deque([initial])
    while queue:
        table = queue.popleft()
        for transform in trans:
            nxt = table.translate(transform)
            if nxt not in lengths:
                lengths[nxt] = lengths[table]+1
                queue.append(nxt)
    return lengths


def desired(twist, k, h, t):
    values = []
    for x in range(1 << (h+t)):
        y = 0
        for i,row in enumerate(twist):
            y |= ((row & x).bit_count() & 1) << i
        for i in range(t):
            row = (k >> (i*h)) & ((1 << h)-1)
            y |= (((row & x).bit_count() ^ (x >> (h+i))) & 1) << (h+i)
        values.append(y)
    return bytes(values)


def literal(word, n):
    outputs = []
    for x in range(1 << n):
        state = [(x >> i) & 1 for i in range(n)]
        for d,s in word:
            check(d != s and type(d) is int and type(s) is int
                  and 0 <= d < n and 0 <= s < n, "invalid word")
            state[d] ^= state[s]
        outputs.append(sum(value << i for i,value in enumerate(state)))
    return bytes(outputs)


def main():
    receipt = json.loads((Path(__file__).parent / "RESULT.json").read_text(encoding="utf-8"))
    expected_shapes = {(h,n-h) for n in range(2,5) for h in range(1,n)}
    check([(c['helpers'],c['targets']) for c in receipt['cases']] ==
          sorted(expected_shapes,key=lambda q:(sum(q),q)), "complete shapes")
    full_groups = {n:walk(n,0,True) for n in range(2,5)}
    total = gains = 0
    for case in receipt['cases']:
        h,t = case['helpers'],case['targets']
        full = full_groups[h+t]
        restricted = walk(h,t,False)
        helper_tables = walk(h,0,True)
        twists = sorted(tuple(sum(((table[1 << j] >> i) & 1) << j for j in range(h))
                              for i in range(h)) for table in helper_tables)
        check(len(full) == case['full_group_states'], "full group count")
        check(len(restricted) == case['restricted_group_states'], "restricted group count")
        check({str(k):v for k,v in Counter(full.values()).items()} == case['full_distance_histogram'], "full layers")
        check({str(k):v for k,v in Counter(restricted.values()).items()} == case['restricted_distance_histogram'], "restricted layers")
        rows = []
        histogram = Counter()
        for twist in twists:
            for k in range(1 << (h*t)):
                table = desired(twist,k,h,t)
                a,b = restricted[table],full[table]
                histogram[a,b] += 1
                rows.append([list(twist),k,a,b])
                gains += a != b
        check(len(rows) == case['maps'], "map count")
        check([[a,b,c] for (a,b),c in sorted(histogram.items())] == case['endpoint_cost_histogram'], "cost histogram")
        check(hashlib.sha256(encode(rows).encode()).hexdigest() == case['labeled_distance_sha256'], "all labeled costs")
        maximum = case['maximum_example']
        target = desired(maximum['twist'],maximum['k'],h,t)
        check(maximum['restricted'] == max(x[2] for x in rows), "maximum attainment")
        for name,dist in [('restricted',restricted),('unrestricted',full)]:
            word = maximum[name+'_word']
            check(len(word) == maximum[name] == dist[target], "minimum word length")
            check(literal(word,h+t) == target, "every dirty input")
            if name == 'restricted':
                check(all(not(d<h<=s) for d,s in word), "forbidden feedback")
        check(not case['feedback_gains'], "expected no gains")
        total += len(rows)
    check(total == receipt['maps'] == 1478 and gains == receipt['feedback_gain_maps'] == 0,
          "final counts")
    print("PASS_TWISTED_FEEDBACK_TRUTH_TABLES maps=1478 feedback_gain_maps=0 full_GL4=20160")


if __name__ == '__main__':
    main()
