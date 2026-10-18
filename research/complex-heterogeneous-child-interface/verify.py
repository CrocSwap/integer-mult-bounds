#!/usr/bin/env python3
"""Exact heterogeneous native-child interface evidence. Apache-2.0.

Adam Gall, with substantial OpenAI Codex assistance. The all-width theorem
is proved in README.md; finite checks do not establish an unbounded theorem.
No predecessor checker is imported. The pinned ceiling engine is used only
for the explicitly hypothetical profile screen.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = "research/r480-owner-optimum/inputs/local/"
INPUTS = {
    LOCAL + "CANONICAL-WORD.json.gz",
    LOCAL + "LOCAL-PROGRAMS.json.gz",
    "notes/general-clifford-frames.tex",
    "research/selector-batching/README.md",
    "research/complex-local-word-ceiling/ceiling.py",
}
PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(value).hexdigest()


def sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    need(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
         "complete external input inventory")
    for row in rows:
        need(digest((ROOT / row["path"]).read_bytes()) == row["sha256"],
             "source pin: " + row["path"])
    return {name: json.loads(gzip.decompress((ROOT / (LOCAL + name)).read_bytes()))
            for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz")}


@lru_cache(None)
def spectrum(n):
    """Multiplicities at 1,i,-1,-i, computed directly from binomial sums."""
    need(type(n) is int and n >= 0, "nonnegative literal width")
    return tuple(sum(comb(n, k) for k in range(j, n + 1, 4)) for j in range(4))


def predicted(p, q, sign):
    """Forward narrower lane; sign on wider lane; return (child width, phase)."""
    need(type(p) is int and type(q) is int and 1 <= p < q, "unequal positive widths")
    need(type(sign) is int and sign in (-1, 1), "exact direction")
    if sign == 1:
        return None
    if q == p + 1 and p % 4 in (1, 2):
        return q + 2, (2 if p % 4 == 1 else 3)
    if q == p + 2 and p % 4 == 1:
        return q + 2, 2
    return None


def counts(p, q, sign, d, phase):
    """Use a common physical lane volume; no compressed-volume comparison."""
    m = max(q, d)
    n = 1 << m
    a, b, c = spectrum(p), spectrum(q), spectrum(d)
    target = tuple((n >> p) * a[j] + (n >> q) * b[(sign * j) % 4]
                   for j in range(4))
    child = tuple((2 * n >> d) * c[(j - phase) % 4] for j in range(4))
    return target, child


def spectral_census():
    recurrence = [1, 0, 0, 0]
    for n in range(68):
        need(tuple(recurrence) == spectrum(n), "binomial/cyclic spectrum disagreement")
        need(sum(recurrence) == 1 << n, "full native dimension")
        if n:
            need(recurrence[0] - recurrence[1] + recurrence[2] - recurrence[3] == 0,
                 "positive-width square trace")
        recurrence = [recurrence[j] + recurrence[(j - 1) % 4] for j in range(4)]
    matches, trials = [], 0
    for p in range(1, 64):
        for q in range(p + 1, 65):
            for sign in (-1, 1):
                expected = predicted(p, q, sign)
                found = []
                for d in range(1, q + 4):
                    for phase in range(4):
                        target, child = counts(p, q, sign, d, phase)
                        trials += 1
                        equal = target == child
                        need(equal == (expected == (d, phase)), "classification counterexample")
                        if equal:
                            found.append((d, phase))
                need(len(found) == int(expected is not None), "complete candidate sweep")
                if found:
                    matches.append([p, q, sign, *found[0]])
    # Inverting both lanes is complex conjugation; inverse children are phase
    # rotations. Verify those reductions separately, not by assuming signs free.
    sign_checks = 0
    for p, q, sign, d, phase in matches:
        target, child = counts(p, q, sign, d, phase)
        conjugate_phase = (-phase - d) % 4
        n = 1 << max(q, d)
        conjugate_child = tuple((2*n >> d) * spectrum(d)[(j-conjugate_phase) % 4]
                                for j in range(4))
        need(conjugate_child == tuple(target[-j % 4] for j in range(4)),
             "opposite lane-sign conjugation")
        inverse_phase = (phase + d) % 4
        inverse_child = tuple((2*n >> d) * spectrum(d)[-(j-inverse_phase) % 4]
                              for j in range(4))
        need(inverse_child == child, "inverse child phase reduction")
        sign_checks += 2
    return {"width_range": [1, 64], "candidate_width_max": "q+3",
            "spectral_trials": trials, "independent_cyclic_widths": 68,
            "signed_reductions": sign_checks, "matches": matches}


def gf2_rank(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def scan(events, word, backward=False):
    frames = word["frames"]
    dimensions = [gf2_rank(f) for f in frames]
    current = list(word["start"])
    gates = {"A": word["A"], "B": word["B"], "cleanup_tail": word["tail"]}
    index, histogram, shapes = Counter(), Counter(), Counter()
    phase, pending, unequal = None, [], []
    for position, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            need(not pending, "orphan gate climb at phase boundary")
            phase = event[1]
        elif tag == "climb":
            _, part, register, old, new, rank = event
            need(part == phase and current[register] == old, "source old-frame chain")
            need(gf2_rank(frames[old] + frames[new]) == dimensions[new], "nested source frames")
            need(rank == dimensions[new] - dimensions[old] and rank > 0, "source quotient rank")
            histogram[rank] += 1
            current[register] = new
            if phase in gates:
                pending.append((register, old, new, rank))
        elif tag == "center":
            need(not pending, "orphan climb at centre")
            histogram[event[-1]] += 1
        elif tag == "scalar" and phase in gates:
            gate_number = index[phase]
            gate = gates[phase][gate_number]
            index[phase] += 1
            op, frame = event[1], event[2]
            need(frame == gate[-1], "source common frame")
            need(len({p[0] for p in pending}) == len(pending), "duplicate operand climb")
            need(all(p[2] == frame for p in pending), "mismatched climb destination")
            if gate[0] == "add":
                dest, source, numerator, denominator = gate[1:5]
                coefficient = Q(numerator, denominator)
                expected = (source, dest, -coefficient) if backward else (dest, source, coefficient)
                need(op[0] == "add" and (op[1][1], op[2][1], Q(op[3], op[4])) == expected,
                     "source rational ADD orientation")
                need(set(p[0] for p in pending) <= {dest, source}, "unrelated gate climb")
                need(current[dest] == current[source] == frame, "operand endpoint frame")
                if len(pending) == 2:
                    shape = tuple(sorted(p[3] for p in pending))
                    if shape[-1] > 1:
                        shapes[shape] += 1
                        if shape[0] != shape[1]:
                            unequal.append({"phase": phase, "gate": gate_number,
                                            "event": position, "registers": [dest, source],
                                            "old_frames": [p[1] for p in pending],
                                            "frame": frame, "ranks": list(shape),
                                            "coefficient": str(coefficient)})
            else:
                need(gate[0] == op[0] == "scale", "known source gate")
                reg, numerator, denominator = gate[1:4]
                coefficient = Q(numerator, denominator)
                if backward:
                    coefficient = 1 / coefficient
                need(op[1][1] == reg and Q(op[2], op[3]) == coefficient, "source SCALE orientation")
                need(set(p[0] for p in pending) <= {reg}, "unrelated scale climb")
            pending = []
        else:
            need(not pending, "unconsumed source climb")
    need(current == word["final"], "source final frames")
    need(all(index[k] == len(v) for k, v in gates.items()), "complete source gate coverage")
    need(dict(histogram) == PROFILE, "complete local child histogram")
    return unequal, shapes


def source_census(data):
    word, programs = data["CANONICAL-WORD.json.gz"], data["LOCAL-PROGRAMS.json.gz"]
    forward, sf = scan(programs["forward"], word)
    backward, sb = scan(programs["backward"], word, True)
    need(forward == backward and sf == sb, "both orientation censuses")
    need(len(forward) == 215 and sum(sf.values()) == 359, "source high-rank pair inventory")
    # For any column multiplicity f>=1 the same-direction p=rf,q=sf theorem
    # rejects all heterogeneous rows. Opposite-sign matches below are context,
    # not a reversal of either lane in the actual source word.
    hypothetic = Counter(PROFILE)
    for row in forward:
        r, s = row["ranks"]
        need(r < s and predicted(r, s, 1) is None, "heterogeneous source theorem domain")
        hypothetic[r] -= 1
        hypothetic[s] -= 1
        hypothetic[r+s] += 1
    need(sum(r*n for r, n in hypothetic.items()) == 5586, "hypothetical rank-mass conservation")
    return {"orientation_events": {k: len(v) for k, v in programs.items()},
            "all_high_rank_shapes": {f"{r},{s}": n for (r,s), n in sorted(sf.items())},
            "heterogeneous_pairs": len(forward), "equal_rank_predecessor_pairs": 359-len(forward),
            "heterogeneous_rows": forward,
            "hypothetical_profile": {str(r): n for r,n in sorted(hypothetic.items()) if n}}


def gadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def gmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def phase_mul(a, phase):
    return gmul(a, (ONE, (Q(0),Q(1)), (-Q(1),Q(0)), (Q(0),-Q(1)))[phase % 4])


def native(values, width, sign=1, phase=0):
    """Literal Gaussian-rational butterfly, acting on low address bits."""
    out = list(values)
    a, b = (Q(1,2),Q(sign,2)), (Q(1,2),Q(-sign,2))
    for bit in range(width):
        for x in range(len(out)):
            if not (x >> bit & 1):
                y = x | (1 << bit)
                left, right = out[x], out[y]
                out[x] = gadd(gmul(a,left), gmul(b,right))
                out[y] = gadd(gmul(b,left), gmul(a,right))
    return [phase_mul(v, phase) for v in out]


def rational_apply(matrix, vector):
    return [tuple(sum(c*v[j] for c,v in zip(row,vector)) for j in range(2)) for row in matrix]


def walsh_columns(width, volume, offset, total, phase=0, sign=1):
    columns = []
    for block in range(volume >> width):
        for frequency in range(1 << width):
            vector = [0] * total
            for x in range(1 << width):
                vector[offset + (block << width) + x] = -1 if (x & frequency).bit_count() % 2 else 1
            columns.append(((phase + sign*frequency.bit_count()) % 4, vector, 1 << width))
    return columns


def fixture(p, q, m, d, phase):
    n, size = 1 << m, 2 << m
    need(1 <= p < q <= m and d <= m+1, "dimension-feasible fixture")
    target_columns = walsh_columns(p,n,0,size) + walsh_columns(q,n,n,size,sign=-1)
    child_columns = walsh_columns(d,size,0,size,phase=phase)
    buckets = defaultdict(list)
    for eigen, vector, norm in child_columns:
        buckets[eigen].append((vector,norm))
    matches = []
    for eigen, vector, norm in target_columns:
        need(bool(buckets[eigen]), "fixture eigenvalue capacity")
        child_vector, child_norm = buckets[eigen].pop()
        matches.append((vector,norm,child_vector,child_norm))
    need(not any(buckets.values()), "fixture complete full-space encoding")
    encode = [[sum(Q(v[i]*u[j], un) for u,un,v,vn in matches) for j in range(size)]
              for i in range(size)]
    decode = [[sum(Q(u[i]*v[j], vn) for u,un,v,vn in matches) for j in range(size)]
              for i in range(size)]
    need(all(sum(encode[i][k]*decode[k][j] for k in range(size)) == int(i==j)
             for i in range(size) for j in range(size)), "reciprocal rational encoding")
    failures = {}
    for column in range(size):
        x = [ONE if j==column else ZERO for j in range(size)]
        expected = native(x[:n],p) + native(x[n:],q,sign=-1)
        encoded = rational_apply(encode,x)
        actual = rational_apply(decode,native(encoded,d,phase=phase))
        need(actual == expected, "full rational basis intertwiner")
        for name, wrong in (("wrong_phase", rational_apply(decode,native(encoded,d,phase=(phase+1)%4))),
                            ("same_direction", native(x[:n],p)+native(x[n:],q))):
            if wrong != expected and name not in failures:
                failures[name] = [column, next(j for j in range(size) if wrong[j]!=expected[j])]
    need(set(failures) == {"wrong_phase","same_direction"}, "fixture semantic controls")
    serial = lambda matrix: [[str(v) for v in row] for row in matrix]
    return {"p":p,"q":q,"m":m,"child_width":d,"phase_exponent":phase,
            "lane_volume":n,"child_volume":size,"matrix_entries":size*size,
            "encode":serial(encode),"decode":serial(decode),"negative_witnesses":failures}


def controls(data):
    names = []
    def reject(name, fn):
        try:
            fn()
        except (ValueError, IndexError, ZeroDivisionError):
            names.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    word, original = data["CANONICAL-WORD.json.gz"], data["LOCAL-PROGRAMS.json.gz"]["forward"]
    for name, field in (("changed_rank",5),("changed_old_frame",3)):
        events = deepcopy(original)
        event = next(e for e in events if e[0]=="climb" and e[1]=="A")
        event[field] += 1
        reject(name, lambda: scan(events,word))
    events = deepcopy(original)
    position = next(i for i,e in enumerate(events) if e==["phase","A"])
    gate = next(e for e in events[position:] if e[0]=="scalar" and e[1][0]=="add")
    gate[1][3] += gate[1][4]
    reject("changed_scalar_coefficient", lambda: scan(events,word))
    reject("equal_width_outside_new_theorem", lambda: predicted(2,2,-1))
    reject("zero_width_outside_new_theorem", lambda: predicted(0,2,-1))
    # Trace-square mismatch rejects one native child acting on only one lane,
    # with the second lane left as an arbitrary dirty spectator.
    target, child = counts(1,2,-1,4,2)
    need(target==child, "positive unequal signed control")
    need(sum((-1)**j*target[j] for j in range(4)) == 0, "zero target square trace")
    one_lane_child = tuple(child[j]//2 + (16 if j==0 else 0) for j in range(4))
    need(sum((-1)**j*one_lane_child[j] for j in range(4)) == 16,
         "missing second-volume rejection")
    names.append("missing_second_child_volume")
    for p,q in ((1,4),(3,4),(2,4)):
        need(predicted(p,q,-1) is None, "signed nonexample")
        names.append(f"signed_nonexample_{p}_{q}")
    return names


def profile_screen(census):
    spec = importlib.util.spec_from_file_location("pinned_ceiling", ROOT / "research/complex-local-word-ceiling/ceiling.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    hypothetical = {int(r):n for r,n in census["hypothetical_profile"].items()}
    baseline = module.ceiling(PROFILE,73,896,9,64,grid=Q(1,10**12))
    counterfactual = module.ceiling(hypothetical,73,896,9,64,grid=Q(1,10**12))
    return {"baseline_bracket":[str(x) for x in baseline],
            "hypothetical_215_pair_bracket":[str(x) for x in counterfactual],
            "status":"Hypothetical rank-sum screen only; no row is realizable by the declared same-direction reciprocal one-child replacement.",
            "admitted_replacement_profile":None}


def run():
    data = sources()
    census = source_census(data)
    spectra = spectral_census()
    fixtures = [fixture(1,2,3,4,2), fixture(2,3,4,5,3), fixture(1,3,4,5,2)]
    return {"schema_version":1,"status":"PASS_HETEROGENEOUS_CHILD_INTERFACE",
            "spectra":spectra,"source":census,"fixtures":fixtures,
            "controls":controls(data),"profile_screen":profile_screen(census),
            "scope":"Exact canonical normalized reciprocal interface; no unrestricted adapter, physical supplier, runtime lower bound or new kappa claim."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write a fresh deterministic receipt; refuse overwrite")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as out:
            out.write(json.dumps(result,indent=2)+"\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(expected) == canonical(result), "committed deterministic receipt")
    print("PASS_HETEROGENEOUS_CHILD_INTERFACE"
          f" spectral_trials={result['spectra']['spectral_trials']}"
          f" matches={len(result['spectra']['matches'])}"
          f" heterogeneous_gates={result['source']['heterogeneous_pairs']}"
          f" fixtures={len(result['fixtures'])} controls={len(result['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
