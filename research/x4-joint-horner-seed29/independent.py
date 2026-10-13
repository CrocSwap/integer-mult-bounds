"""Code-disjoint integer matrix, price and path-certificate crosscheck.

Does not import Fraction, joint.py, verify.py or predecessor code.
Written by the same Codex agent for Ross Richardson; not a human peer review.
Apache-2.0. Baseline semantics are the credited PR696 copy/unit lowering.
"""
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
W = ("W", 0)


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def rational(p, d):
    demand(type(p) is int and type(d) is int and d != 0 and p != 0, "invalid dyadic")
    if d < 0:
        p, d = -p, -d
    g = gcd(abs(p), d)
    p, d = p//g, d//g
    demand(d & (d-1) == 0, "non-dyadic")
    return p, d


def single(op):
    tag, dest = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", dest)]
    if tag == "copy":
        return [("copy", dest, tuple(op[2]))]
    if tag == "scale":
        n, d = rational(*op[2:])
        demand(abs(n) & (abs(n)-1) == 0, "non-binary scale")
        power = abs(n).bit_length()-d.bit_length()
        return [("double" if power > 0 else "halve", dest)]*abs(power) + ([("negate", dest)] if n < 0 else [])
    demand(tag == "add", "unknown macro")
    n, d = rational(*op[3:])
    src = tuple(op[2])
    sign = "add" if n > 0 else "subtract"
    if abs(n) == d:
        return [(sign, dest, src), ("clear", W)]
    word = [("copy", W, src)]
    for bit in format(abs(n), "b")[1:]:
        word += [("double", W)]
        if bit == "1":
            word += [("add", W, src)]
    return word + [("halve", W)]*(d.bit_length()-1) + [(sign, dest, W), ("clear", W)]


def pair(a, b):
    ns = [rational(*op[3:]) for op in (a,b)]
    common = max(d for _, d in ns)
    values = [p*(common//d) for p,d in ns]
    degree = max(abs(v).bit_length() for v in values)-1
    terms = [(place, col, 1 if value > 0 else -1)
             for place in range(degree, -1, -1)
             for col, value in enumerate(values) if abs(value) & (1 << place)]
    leading_place, first_col, orientation = terms[0]
    sources = [tuple(a[2]), tuple(b[2])]
    word = [("copy", W, sources[first_col])]
    for place, col, sign in terms[1:]:
        word += [("double", W)]*(leading_place-place)
        word += [("add" if sign == orientation else "subtract", W, sources[col])]
        leading_place = place
    word += [("double", W)]*leading_place
    word += [("halve", W)]*(common.bit_length()-1)
    return word + [("add" if orientation == 1 else "subtract", tuple(a[1]), W), ("clear", W)]


def matrix_check(a, b, word):
    registers = [tuple(a[1]), tuple(a[2]), tuple(b[2]), W]
    demand(len(set(registers)) == 4, "aliased local circuit")
    matrix = [[int(i == j) for j in range(4)] for i in range(4)]
    denominator = 1
    for op in word:
        tag, dest = op[:2]
        r = registers.index(dest)
        if tag == "clear":
            matrix[r] = [0]*4
        elif tag == "copy":
            matrix[r] = matrix[registers.index(op[2])].copy()
        elif tag == "double":
            matrix[r] = [2*v for v in matrix[r]]
        elif tag == "halve":
            for k in range(4):
                if k != r:
                    matrix[k] = [2*v for v in matrix[k]]
            denominator *= 2
        elif tag in ("add", "subtract"):
            source = matrix[registers.index(op[2])]
            matrix[r] = [x + (y if tag == "add" else -y) for x,y in zip(matrix[r], source)]
        else:
            raise ValueError("unknown paired primitive")
    pa, da = rational(*a[3:])
    pb, db = rational(*b[3:])
    common = max(da, db)
    expected = [[common, pa*(common//da), pb*(common//db), 0],
                [0,common,0,0], [0,0,common,0], [0,0,0,0]]
    demand(all(matrix[i][j]*common == expected[i][j]*denominator for i in range(4) for j in range(4)),
           "integer four-column endpoint")


def eligible(a,b):
    if a[0] != "scalar" or b[0] != "scalar" or a[2] == 0 or a[2] != b[2]:
        return False
    x,y = a[1],b[1]
    return x[0] == y[0] == "add" and x[1] == y[1] and len({tuple(x[1]),tuple(x[2]),tuple(y[2]),W}) == 4


def run():
    pins = json.loads((HERE/"SOURCES.json").read_text())
    for path, digest in pins["files"].items():
        possibilities = [path]
        if path == "certificates/selected-result.json":
            possibilities += ["certificates/checkpoints/frontier799.json"]
        demand(any((ROOT/p).is_file() and hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest
                   for p in possibilities), "independent source pin")
    with tarfile.open(ROOT/pins["archive"]) as t:
        raw = gzip.decompress(t.extractfile("native/local/LOCAL-PROGRAMS.json.gz").read())
    demand(hashlib.sha256(raw).hexdigest() == pins["members"]["native/local/LOCAL-PROGRAMS.json.gz"], "independent payload pin")
    events = json.loads(raw)["backward"]
    expected = json.loads((HERE/"EXPECTED.json").read_text())
    starts = expected["selected_events"]
    demand(all(type(i) is int and 0 <= i < len(events)-1 for i in starts), "bad selected index")
    demand(starts == sorted(set(starts)) and all(b-a > 1 for a,b in zip(starts,starts[1:])), "overlapping pairs")
    census, weights = [], {}
    for i in range(len(events)-1):
        if not eligible(events[i],events[i+1]):
            continue
        a,b = events[i][1],events[i+1][1]
        word = pair(a,b)
        matrix_check(a,b,word)
        old = len(single(a))+len(single(b))
        saving = old-len(word)
        qs = []
        for op in (a,b):
            n,d = rational(*op[3:])
            qs.append(str(n) if d == 1 else str(n)+"/"+str(d))
        census.append(dict(event=i,frame=events[i][2],coefficients=qs,before=old,after=len(word),saving=saving))
        if saving > 1:
            weights[i] = saving
    # Forward longest path, independent of the nomination's backward recurrence.
    prefix = [0]*(len(events)+1)
    for end in range(1,len(prefix)):
        prefix[end] = prefix[end-1]
        if end-2 in weights:
            prefix[end] = max(prefix[end], prefix[end-2]+weights[end-2])
    demand(all(i in weights for i in starts), "unprofitable/ineligible recipe")
    score = sum(weights[i] for i in starts)
    demand(score == prefix[-1] and 2*score == expected["saving_real_primitives"], "path optimality")
    demand(hashlib.sha256(encode(census)).hexdigest() == expected["census_sha256"], "independent census")
    stream = hashlib.sha256()
    chosen = set(starts)
    count, i = 0,0
    while i < len(events):
        e = events[i]
        if e[0] != "scalar":
            stream.update(encode(e)+b"\n")
            i += 1
            continue
        size = 2 if i in chosen else 1
        word = pair(e[1],events[i+1][1]) if size == 2 else single(e[1])
        for op in word:
            stream.update(encode(["primitive",e[2],op])+b"\n")
        count += len(word)
        i += size
    demand(stream.hexdigest() == expected["candidate"]["primitive_stream_sha256"], "independent complete stream")
    demand(2*count == expected["candidate"]["real_primitives"], "independent complete count")
    # These are genuine adverse endpoint controls, not just receipt mutations.
    a,b = [events[starts[29]][1],events[starts[29]+1][1]]
    word = pair(a,b)
    rejected = 0
    for bad in (word[1:],word[:-1],word[:-2]+word[-1:],word[:1]+word[2:]):
        try:
            matrix_check(a,b,bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("integer control accepted")
    return dict(status="PASS_INDEPENDENT_JOINT_HORNER", integer_pair_matrices=len(census),
                matrix_entries_checked=16*len(census), optimal_single_component_saving=score,
                complete_real_primitives=2*count, complete_stream_sha256=stream.hexdigest(),
                selected_pairs=len(starts), controls=rejected)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
