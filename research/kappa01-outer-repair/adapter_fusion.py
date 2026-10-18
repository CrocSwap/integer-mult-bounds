#!/usr/bin/env python3
"""Compile actual local Walsh-retarget address maps into Fourier calls.

This prices one concrete generalized-layout implementation, not an optimal
compiler or a whole supplier. Quadratic phases have a proved algebraic
completion in ADAPTER-FUSION.md; this executable does not emit or replay
that scalar phase program. The finite paid profile below records Fourier
children only. See that file for the exact scope and invariant.
"""
from collections import Counter
from decimal import Decimal, localcontext
from functools import lru_cache
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BASE = "997e6a9ca7b4f95d50e366f61412fd640d72a88a"
SOURCE = "research/involutive-walsh-lift/evidence/WALSH-RETARGET-NATIVE.json.gz"
N = 9
I = tuple(1 << i for i in range(N))


def require(ok, what):
    if not ok:
        raise RuntimeError(what)


def mv(A, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(A))


def mm(A, B):
    return tuple(xor(B[j] for j in range(N) if row >> j & 1) for row in A)


def xor(xs):
    out = 0
    for x in xs:
        out ^= x
    return out


@lru_cache(maxsize=None)
def inv(A):
    rows = [row | (1 << (N+i)) for i, row in enumerate(A)]
    for j in range(N):
        p = next(i for i in range(j, N) if rows[i] >> j & 1)
        rows[p], rows[j] = rows[j], rows[p]
        for i in range(N):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    require(tuple(r & ((1 << N)-1) for r in rows) == I, "inverse")
    return tuple(r >> N for r in rows)


def affine_mul(A, B):
    # Composition A after B.
    return mm(A[0], B[0]), mv(A[0], B[1]) ^ A[1]


def affine_inv(A):
    return inv(A[0]), mv(inv(A[0]), A[1])


def apply_op(rows, op):
    if op[0] == "swap":
        _, i, j = op
        rows[i], rows[j] = rows[j], rows[i]
    else:
        require(op[0] == "shear", "op")
        old = tuple(rows)
        targets = {i for i, _ in op[1]}
        require(all(not any(mask >> j & 1 for j in targets) for _,mask in op[1]),
                "rectangular shear has unchanged controls")
        for i, mask in op[1]:
            rows[i] ^= xor(old[j] for j in range(N) if mask >> j & 1)


def fuse_ops(ops):
    result = []
    for op in ops:
        if op[0] != "shear" or not result or result[-1][0] != "shear":
            result.append(op)
            continue
        previous = dict(result[-1][1])
        current = dict(op[1])
        targets = set(previous) | set(current)
        controls = xor([])  # OR, not XOR: used only to test dependency.
        for mask in list(previous.values())+list(current.values()):
            controls |= mask
        if any(controls >> j & 1 for j in targets):
            result.append(op)
            continue
        for j, mask in current.items():
            previous[j] = previous.get(j, 0) ^ mask
        previous = {j:mask for j,mask in previous.items() if mask}
        if previous:
            result[-1] = ("shear", tuple(sorted(previous.items())))
        else:
            result.pop()
    return tuple(result)


def reduce_word(A, mode):
    rows = list(A)
    ops = []
    if mode == "column":
        for j in range(N):
            p = next(i for i in range(j, N) if rows[i] >> j & 1)
            if p != j:
                op = ("swap", p, j)
                apply_op(rows, op)
                ops.append(op)
            for i in range(N):
                if i != j and rows[i] >> j & 1:
                    op = ("shear", ((i, 1 << j),))
                    apply_op(rows, op)
                    ops.append(op)
    else:
        # Determine a row permutation giving a unit-pivot LU decomposition.
        work, permutation = list(A), list(range(N))
        for j in range(N):
            p = next(i for i in range(j, N) if work[i] >> j & 1)
            work[p], work[j] = work[j], work[p]
            permutation[p], permutation[j] = permutation[j], permutation[p]
            for i in range(j+1, N):
                if work[i] >> j & 1:
                    work[i] ^= work[j]
        labels = list(range(N))
        for i, label in enumerate(permutation):
            j = labels.index(label)
            if j != i:
                op = ("swap", i, j)
                apply_op(rows, op)
                ops.append(op)
                labels[i], labels[j] = labels[j], labels[i]
        for indices in (range(N), range(N-1, -1, -1)):
            forward = isinstance(indices, range) and indices.step == 1
            for i in indices:
                mask = 0
                for j in (range(i) if forward else range(i+1, N)):
                    if rows[i] >> j & 1:
                        rows[i] ^= rows[j]
                        mask ^= 1 << j
                require(rows[i] >> i & 1, "unit LU pivot")
                if mask:
                    ops.append(("shear", ((i, mask),)))
    require(tuple(rows) == I, "word reduces the exact source matrix")
    # Every op is involutive; reverse the reduction to implement A.
    return fuse_ops(tuple(reversed(ops)))


def profile(ops):
    result = Counter()
    for op in ops:
        if op[0] == "swap":
            result[2] += 3
        else:
            result[len(op[1])] += 2
    return result


def score(hist):
    # Numerical choice among exact valid programs. It affects optimality only.
    return sum(count * rank ** (8/9) for rank, count in hist.items())


@lru_cache(maxsize=None)
def synthesize(A):
    candidates = []
    # Exact dense rectangular block shear, without decomposing its rows.
    changed = tuple(i for i in range(N) if A[i] != (1 << i))
    controls = tuple((i, A[i] ^ (1 << i)) for i in changed)
    if all(not any(mask >> j & 1 for j in changed) for _,mask in controls):
        candidates.append((("shear", controls),) if controls else ())
    for mode in ("column", "lu"):
        candidates.append(reduce_word(A, mode))
        candidates.append(fuse_ops(tuple(reversed(reduce_word(inv(A), mode)))))
    ops = min(candidates, key=lambda word:(score(profile(word)), len(word), word))
    rows = list(I)
    for op in ops:
        apply_op(rows, op)
    require(tuple(rows) == A, "compiled exact address matrix")
    return ops


def perm(record):
    return tuple(record["matrix_rows"]), record["offset"]


def normalize(hist):
    return dict(sorted(hist.items()))


def compile_program(program, recipes, policy):
    start = program.index(["phase", "A"])+1
    end = program.index(["phase", "exit_adapters"])
    events = program[start:end]
    pending = [(I,0) for _ in range(712)]
    native, extra, charged_linear, charged_offsets = Counter(), Counter(), Counter(), Counter()
    counts, nonidentity_by_reason = Counter(), Counter()
    fingerprint = hashlib.sha256()

    def charge(A, why, offset=True):
        word = synthesize(A[0])
        ph = profile(word)
        extra.update(ph)
        charged_linear.update(ph)
        if offset and A[1]:
            rank = A[1].bit_count()
            extra[rank] += 2
            charged_offsets[rank] += 2
            counts["translation_jobs"] += 1
        if word:
            counts["nonidentity_linear_jobs"] += 1
            nonidentity_by_reason[why] += 1
        counts[why] += 1
        fingerprint.update(repr((why,A,word,offset)).encode())

    def reg(arg):
        return arg[1]+(704 if arg[0] == "C" else 0)

    for event in events:
        kind = event[0]
        if kind in ("climb", "center"):
            if kind == "climb":
                r, old, new, rank = event[2:]
            else:
                r, old, new, rank = event[1:]
                r += 704
            record = recipes[(old,new,rank)]
            left, right = perm(record["left"]), perm(record["right"])
            native[rank] += 1
            if policy == "literal":
                charge(right, "right_adapter")
                charge(left, "left_adapter")
            else:
                combined = affine_mul(right, pending[r])
                # All binary translations commute with coordinate C_r.
                # Push that translation through the child into its left map.
                charge((combined[0],0), "fused_child_entrance")
                pending[r] = affine_mul(left, (I,combined[1]))
        elif kind == "scalar":
            gate = event[1]
            tag, target = gate[0], reg(gate[1])
            counts["scalar_"+tag] += 1
            if policy == "literal":
                continue
            if tag == "scale":
                continue  # Every address permutation commutes with a scale.
            if tag == "clear":
                pending[target] = (I,0)
                continue
            source = reg(gate[2])
            if tag == "copy":
                pending[target] = pending[source]
                continue
            require(tag == "add", "expected interior scalar opcode")
            if pending[target] == pending[source]:
                counts["already_common_layout_adds"] += 1
                continue
            if policy == "flush":
                charge(pending[target], "scalar_flush")
                charge(pending[source], "scalar_flush")
                pending[target] = pending[source] = (I,0)
                continue
            # One actual relative map suffices; compare both legal choices.
            to_target = affine_mul(affine_inv(pending[target]), pending[source])
            to_source = affine_mul(affine_inv(pending[source]), pending[target])
            def cost(A):
                ph = profile(synthesize(A[0]))
                if A[1]: ph[A[1].bit_count()] += 2
                return score(ph)
            if (cost(to_target),repr(to_target)) <= (cost(to_source),repr(to_source)):
                charge(to_target, "relative_alignment")
                # Check the representation invariant for the changed source.
                require(affine_mul(pending[target],to_target) == pending[source],
                        "source relative alignment")
                pending[source] = pending[target]
            else:
                charge(to_source, "relative_alignment")
                require(affine_mul(pending[source],to_source) == pending[target],
                        "target relative alignment")
                pending[target] = pending[source]
        else:
            require(kind == "phase", "unpriced event in the chosen interior")
    before_exit = extra.copy()
    if policy != "literal":
        for A in pending:
            if A != (I,0):
                charge(A, "returned_layout")
    expected = Counter({1:2412,2:418,3:432,4:142,5:82,8:8})
    require(native == expected, "exact source child inventory")
    combined = native+extra
    with localcontext() as ctx:
        ctx.prec = 60
        m, streams_per_invocation = Decimal(73), Decimal(896)/9
        def moment(hist):
            return sum(Decimal(n)*(Decimal(r)/m)**(Decimal(8)/9)
                       for r,n in hist.items())/streams_per_invocation
        numerical = dict(native_only=str(moment(native)),
                         augmented_interior_only=str(moment(combined)),
                         augmented_even_if_boundary_layouts_free=str(moment(native+before_exit)))
    mass = sum(r*n for r,n in combined.items())
    # This is an exact exclusion for this compiler: t^(8/9) >= t on (0,1].
    linear_floor = Fraction(mass*9,73*896)
    boundary_count = sum(nonidentity_by_reason.values())
    interior_boundary_count = boundary_count - nonidentity_by_reason["returned_layout"]
    independent_boundary_floor = Fraction(2*interior_boundary_count*9,73*896)
    return dict(policy=policy, start_event_inclusive=start, end_event_exclusive=end,
                event_count=len(events), native_profile=normalize(native),
                added_linear_profile=normalize(charged_linear),
                added_translation_profile=normalize(charged_offsets),
                augmented_profile=normalize(combined), rank_mass=mass,
                exact_normalized_linear_rank_floor=str(linear_floor),
                target_moment_exceeds_one_from_exact_floor=linear_floor>1,
                diagnostic_decimal_moments=numerical,
                nonidentity_linear_jobs_by_reason=dict(sorted(nonidentity_by_reason.items())),
                independent_single_array_boundary_floor=dict(
                    interior_nonidentity_maps=interior_boundary_count,
                    minimum_fourier_calls=2*interior_boundary_count,
                    exact_adapter_only_normalized_rank_floor=str(independent_boundary_floor),
                    exceeds_one=independent_boundary_floor>1,
                    scope="Only implementations keeping these independent monomial boundaries; no auxiliary arrays or cross-child fusion"),
                events=dict(sorted(counts.items())), program_sha256=fingerprint.hexdigest())


def main():
    raw = subprocess.check_output(["git","show",BASE+":"+SOURCE],cwd=ROOT)
    data = json.loads(gzip.decompress(raw))
    recipes = {}
    for record in data["children"]:
        key = record["old"],record["new"],record["rank"]
        require(key not in recipes, "unique native recipe")
        recipes[key] = record
    results = {}
    for orientation, program in sorted(data["programs"].items()):
        results[orientation] = [compile_program(program,recipes,policy)
                                for policy in ("literal","flush","relative")]
    result = dict(status="EXACT CONCRETE ADAPTER COMPILER; NO OPTIMALITY OR SUPPLIER CLAIM",
                  source_commit=BASE, source_path=SOURCE,
                  source_sha256=hashlib.sha256(raw).hexdigest(),
                  source_recipe_count=len(recipes), orientation_results=results,
                  distinct_linear_maps_compiled=synthesize.cache_info().currsize,
                  scope=["Canonical-frame local interior only; external normalization and global jobs omitted",
                         "Recursive Fourier calls may target arbitrary subsets; uniform physical shape theorem still required",
                         "Monomial phases retained by algebraic conjugation, scalar/guard costs not replayed",
                         "Compiler choice uses floats only to choose among exact validated programs",
                         "Failure is proved by exact rank mass, not the diagnostic decimal moments"])
    (OUT/"ADAPTER-RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    for orientation, rows in results.items():
        print(orientation,[(r["policy"],r["rank_mass"],
                            r["diagnostic_decimal_moments"]["augmented_interior_only"][:16])for r in rows])
    print("PASS exact matrix compiler and deferred-layout invariants; every concrete profile fails.")


if __name__ == "__main__":
    main()
