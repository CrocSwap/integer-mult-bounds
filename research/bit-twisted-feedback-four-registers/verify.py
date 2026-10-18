"""Complete four-register twisted-helper XOR census. Apache-2.0.

Prepared for ywz65 with substantial OpenAI Codex assistance.
No predecessor implementation is imported.
"""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unit(n):
    return tuple(1 << i for i in range(n))


def alphabet(h, t, feedback):
    return [(d, s) for d in range(h+t) for s in range(h+t)
            if d != s and (feedback or not (d < h <= s))]


def advance(rows, gate):
    d, s = gate
    return rows[:d] + (rows[d] ^ rows[s],) + rows[d+1:]


def bfs(h, t, feedback):
    first = unit(h+t)
    parents = {first: None}
    distance = {first: 0}
    todo = deque([first])
    gates = alphabet(h, t, feedback)
    while todo:
        matrix = todo.popleft()
        for gate in gates:
            other = advance(matrix, gate)
            if other not in distance:
                distance[other] = distance[matrix] + 1
                parents[other] = (matrix, gate)
                todo.append(other)
    return distance, parents


def witness(matrix, parents):
    result = []
    while parents[matrix] is not None:
        matrix, gate = parents[matrix]
        result.append(list(gate))
    return result[::-1]


def endpoint(twist, k, h, t):
    return twist + tuple((1 << (h+i)) | ((k >> (h*i)) & ((1 << h)-1))
                         for i in range(t))


def replay(word, h, t, feedback=True):
    rows = unit(h+t)
    legal = set(alphabet(h, t, feedback))
    for gate in word:
        require(isinstance(gate, list) and len(gate) == 2 and
                all(type(x) is int for x in gate), "typed gate")
        require(tuple(gate) in legal, "illegal gate")
        rows = advance(rows, gate)
    return rows


def group_size(n):
    result = 1
    for j in range(n):
        result *= (1 << n) - (1 << j)
    return result


def census():
    results = []
    for n in range(2, 5):
        full, full_parents = bfs(n, 0, True)
        require(len(full) == group_size(n), "incomplete full group")
        for h in range(1, n):
            t = n-h
            restricted, parents = bfs(h, t, False)
            twists, _ = bfs(h, 0, True)
            require(len(restricted) == group_size(h)*group_size(t)*(1 << (h*t)),
                    "incomplete parabolic group")
            histogram = Counter()
            gains = []
            rows = []
            max_witness = None
            restoration_gains = []
            for twist in sorted(twists):
                for k in range(1 << (h*t)):
                    matrix = endpoint(twist, k, h, t)
                    a, b = restricted[matrix], full[matrix]
                    histogram[(a,b)] += 1
                    wr = witness(matrix, parents)
                    wu = witness(matrix, full_parents)
                    require(replay(wr,h,t,False) == matrix, "restricted witness")
                    require(replay(wu,h,t,True) == matrix, "feedback witness")
                    rows.append([list(twist),k,a,b])
                    entry = dict(twist=list(twist), k=k, restricted=a,
                                 unrestricted=b, restricted_word=wr,
                                 unrestricted_word=wu)
                    if a != b:
                        gains.append(entry)
                    if max_witness is None or a > max_witness["restricted"]:
                        max_witness = entry
                    restored = endpoint(unit(h), k, h, t)
                    # A helper-only inverse has the same XOR cost as T.
                    if b + twists[twist] < full[restored]:
                        restoration_gains.append(entry)
            require(not restoration_gains, "charged correction below global minimum")
            results.append({"helpers":h,"targets":t,"maps":len(rows),
                "full_group_states":len(full),"restricted_group_states":len(restricted),
                "full_distance_histogram":dict(sorted(Counter(full.values()).items())),
                "restricted_distance_histogram":dict(sorted(Counter(restricted.values()).items())),
                "endpoint_cost_histogram":[[a,b,c] for (a,b),c in sorted(histogram.items())],
                "feedback_gains":gains,"maximum_example":max_witness,
                "labeled_distance_sha256":hashlib.sha256(canonical(rows).encode()).hexdigest()})
    return {"schema_version":1,"model":"F2 unit XOR; arbitrary dirty h,y; helper exit T invertible; target exit y+Kh; H+T<=4", "cases":results,
            "maps":sum(x["maps"] for x in results),
            "feedback_gain_maps":sum(len(x["feedback_gains"]) for x in results)}


def controls():
    rejected = []
    def bad(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted control: " + name)
    require(replay([[0,1],[2,0]],2,1) == (3,2,7), "twisted positive fixture")
    require(replay([[0,1],[1,0],[0,1],[1,0],[0,1]],1,1) == (1,3),
            "feedback positive fixture")
    bad("forbidden_feedback",lambda:replay([[0,1]],1,1,False))
    bad("self_xor",lambda:replay([[0,0]],1,1))
    bad("boolean_index",lambda:replay([[True,0]],1,1))
    bad("zero_target_only",lambda:require(replay([[1,0],[2,1]],1,2) == endpoint((1,),3,1,2), "target dirt corrupted"))
    bad("unrestored_feedback",lambda:require(replay([[0,1]],1,1) == endpoint((1,),0,1,1), "helper depends on target"))
    bad("wrong_twist",lambda:require(replay([[0,1],[2,0]],2,1) == endpoint((1,2),3,2,1), "twist omitted"))
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = census()
    result["controls"] = controls()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n", encoding="utf-8")
    require(canonical(json.loads(path.read_text(encoding="utf-8"))) == canonical(result),
            "certificate mismatch")
    print("PASS_TWISTED_FEEDBACK_FOUR_REGISTERS maps=%d feedback_gain_maps=%d controls=%d" %
          (result["maps"],result["feedback_gain_maps"],len(result["controls"])))


if __name__ == "__main__":
    main()
