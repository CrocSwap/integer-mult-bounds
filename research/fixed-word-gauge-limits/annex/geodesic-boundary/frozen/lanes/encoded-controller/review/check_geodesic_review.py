"""Check the common-boundary obstruction from independent binary matrices."""

from collections import Counter, deque
from hashlib import sha256
from pathlib import Path
import gzip
import json
import resource
import subprocess
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
ROOT = HERE.parents[4]
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
REPO = ROOT / "worktrees/k5-centre-sharing"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_PIN = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
}
PINS = {
    "history-encoding/FULL-MODE-PROGRAMS.json.gz": "ebc17d1d4c51a9c6b3cb05670d970db3d3e1000f26f1d864cdb27523ce1997dd",
    "history-encoding/ONE-SIDED-MODE-PROGRAMS.json.gz": "2f7d401c237b915db721d83b426cbe0bfa593e7c61170498f3be115cf20d16a7",
    "history-encoding/ONE-SHOT-MAX48.json": "6563798aeebe83d2d62c9d089012d2b7cea3818e673deaa4b2653be183a0ed21",
}
GIT_PINS = {
    "research/complex-t16-rare-pattern-exchanges/data/PLAN.json": "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0",
    "research/community-frontier1094-audit/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "research/format-limits-corrected/README.md": "1bcd80c1cd61fddae9f3a7f00fc9d1c796410408251e576600e94c19b16b1e5e",
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def image(matrix, value):
    result = 0
    for column in matrix:
        if value & 1:
            result ^= column
        value >>= 1
    require(value == 0, "Matrix domain")
    return result


def compose(left, right):
    return tuple(image(left, column) for column in right)


def inverse(matrix):
    n = len(matrix)
    rows = [sum(((column >> i) & 1) << j for j, column in enumerate(matrix)) | (1 << (n + i))
            for i in range(n)]
    for i in range(n):
        pivot = next((j for j in range(i, n) if (rows[j] >> i) & 1), None)
        require(pivot is not None, "Nonsingular binary matrix")
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(n):
            if j != i and (rows[j] >> i) & 1:
                rows[j] ^= rows[i]
    result = tuple(sum(((rows[i] >> (n + j)) & 1) << i for i in range(n)) for j in range(n))
    require(compose(matrix, result) == tuple(1 << i for i in range(n)), "Binary inverse")
    return result


def pairing(a, b, n=9):
    mask = (1 << n) - 1
    return (((a & mask) & (b >> n)).bit_count() + ((b & mask) & (a >> n)).bit_count()) % 2


def canonical_label(frame):
    rows = list(frame)
    pivots = []
    for j in range(9):
        p = len(pivots)
        k = next((k for k in range(p, len(rows)) if (rows[k] >> j) & 1), None)
        if k is None:
            continue
        rows[p], rows[k] = rows[k], rows[p]
        for k in range(len(rows)):
            if k != p and (rows[k] >> j) & 1:
                rows[k] ^= rows[p]
        pivots.append(j)
    require(len(pivots) == len(frame), "Independent canonical frame basis")
    nullspace = []
    for j in range(9):
        if j not in pivots:
            nullspace.append((1 << j) | sum(((rows[i] >> j) & 1) << p for i, p in enumerate(pivots)))
    result = [u | (u << 9) for u in frame] + [v << 9 for v in nullspace]
    require(len(result) == rank(result) == 9, "Lagrangian dimension")
    require(all(pairing(a, b) == 0 for a in result for b in result), "Isotropic canonical label")
    return result


def distance(left, right):
    return rank([sum(pairing(a, b) << j for j, b in enumerate(right)) for a in left])


def read_source():
    process = subprocess.Popen(["git", "show", BASE + ":" + ARCHIVE], cwd=REPO, stdout=subprocess.PIPE)
    digest = sha256()

    class CheckedStream:
        def read(self, size=-1):
            data = process.stdout.read(size)
            digest.update(data)
            return data

    stream = CheckedStream()
    result = {}
    with tarfile.open(fileobj=stream, mode="r|gz") as archive:
        for member in archive:
            if member.name in MEMBERS:
                raw = archive.extractfile(member).read()
                require(sha256(raw).hexdigest() == MEMBERS[member.name], "Local member pin")
                result[member.name] = json.loads(gzip.decompress(raw))
    while stream.read(65536):
        pass
    require(process.wait() == 0 and digest.hexdigest() == ARCHIVE_PIN, "Complete archive pin")
    require(set(result) == set(MEMBERS), "Local source inventory")
    return result["slots/local/CANONICAL-WORD.json.gz"], result["slots/local/LOCAL-PROGRAMS.json.gz"]


def local_paths(word, program, original, matrices):
    current = list(word["start"])
    paid = [0] * len(current)
    touches = [[] for _ in current]
    counts = Counter()
    profile = Counter()
    native_kinds = ("climb", "adapter", "residual_adapter")
    require([e for e in program if e[0] in native_kinds] == [e for e in original if e[0] in native_kinds], "Source native inventory")
    for index, event in enumerate(program):
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate, frame = event[1:]
            require(gate[0] in ("add", "scale"), "No persistent COPY or CLEAR")
            registers = [gate[1]] + ([gate[2]] if gate[0] == "add" else [])
            for bank, register in registers:
                require(bank == "L" and 0 <= register < len(current), "No private array bank")
                require(current[register] == frame, "Equal scalar frames")
                touches[register].append((index, kind, event))
            counts[gate[0]] += 1
        else:
            require(kind in native_kinds, "Native grammar")
            register = event[2]
            touches[register].append((index, kind, event))
            counts[kind] += 1
            if kind == "climb":
                before, after, paid_rank = event[3:]
                require(current[register] == before, "Continuous native path")
                require(rank(word["frames"][before] + word["frames"][after]) == len(word["frames"][after]), "Nested source frames")
                native_rank = distance(matrices[before], matrices[after])
                require(native_rank == paid_rank == len(word["frames"][after]) - len(word["frames"][before]), "Direct symplectic pairing rank")
                paid[register] += paid_rank
                profile[paid_rank] += 1
                current[register] = after
    require(current == word["final"], "Pinned final frames")
    endpoints = [distance(matrices[first], matrices[last]) for first, last in zip(word["start"], current)]
    require(paid == endpoints and sum(paid) == 5522, "All individual endpoint distances")
    boundary_touches = []
    for port, line in enumerate(word["ports"]):
        x, y = port, 112 + port
        empty = [1 << (9 + j) for j in range(9)]
        full = [(1 << j) | (1 << (9 + j)) for j in range(9)]
        line_action = lambda basis: [v ^ (line if ((v >> 9) & line).bit_count() % 2 else 0) for v in basis]
        require(distance(matrices[word["start"][x]], line_action(empty)) == 0
                and distance(matrices[current[x]], full) == 0, "Source line and full frames")
        require(distance(matrices[word["start"][y]], empty) == 0
                and distance(matrices[current[y]], line_action(full)) == 0, "Target empty and complement frames")
        require(endpoints[x] == endpoints[y] == 8 and distance(empty, line_action(empty)) == 1, "Data endpoint distance")
        first, last = touches[x][0], touches[y][-1]
        require(first[1] == last[1] == "adapter" and first[2][1] == "old_to_new" and last[2][1] == "new_to_old", "Rank-zero boundary wrappers")
        first_paid = next(t[0] for t in touches[x] if t[1] == "climb")
        last_paid = next(t[0] for t in reversed(touches[y]) if t[1] == "climb")
        before = sum(first[0] < t[0] < first_paid and t[1] == "scalar" for t in touches[x])
        after = sum(last_paid < t[0] < last[0] and t[1] == "scalar" for t in touches[y])
        require(before > 0 and after > 0, "Paid child has intervening scalar access")
        boundary_touches.append((before, after))
    require(sum(endpoints[224:]) + 224 * 9 == 5746, "All normalized endpoint distances")
    return {"persistent_paths": len(current), "rank_mass": sum(paid),
            "normalized_endpoint_distance_sum": 5746, "native_profile": dict(profile),
            "counts": dict(counts), "scalar_uses_before_first_X_paid_child": sorted({a for a, b in boundary_touches}),
            "scalar_uses_after_last_Y_paid_child": sorted({b for a, b in boundary_touches})}


def clifford_control():
    n, mask = 2, 3
    unit = tuple(1 << i for i in range(4))
    generators = []
    for i in range(n):
        h = list(unit)
        h[i], h[n + i] = h[n + i], h[i]
        generators.append(tuple(h))
        s = list(unit)
        s[i] ^= 1 << (n + i)
        generators.append(tuple(s))
    for i, j in ((0, 1), (1, 0)):
        c = list(unit)
        c[i] ^= 1 << j
        c[n + j] ^= 1 << (n + i)
        generators.append(tuple(c))
    group, pending = {unit}, deque([unit])
    while pending:
        s = pending.popleft()
        for g in generators:
            t = compose(g, s)
            if t not in group:
                group.add(t)
                pending.append(t)
    require(len(group) == 720, "Complete Sp(4,2) control group")
    inverse_group = {s: inverse(s) for s in group}
    labels = {s: inverse_group[s][n:] for s in group}
    distance = lambda a, b: rank(a + b) - n
    spaces = {}
    for basis in labels.values():
        spaces[tuple(sorted((0, basis[0], basis[1], basis[0] ^ basis[1])))] = basis
    require(len(spaces) == 15, "All two-dimensional Lagrangians")
    wrong_order_detected = False
    for t in group:
        for u in group:
            relative = compose(u, inverse_group[t])
            rho = rank([column & mask for column in relative[n:]])
            require(rho == distance(labels[t], labels[u]), "Relative Fourier rank equals endpoint distance")
            wrong = compose(inverse_group[t], u)
            wrong_order_detected |= rank([column & mask for column in wrong[n:]]) != rho
    for a in spaces.values():
        for b in spaces.values():
            for c in spaces.values():
                require(distance(a, c) <= distance(a, b) + distance(b, c), "Metric triangle control")
    monomials = [m for m in group if not rank([v & mask for v in m[n:]])]
    for m in monomials:
        for t in group:
            require(distance(labels[compose(m, t)], labels[t]) == 0, "Left monomial frame invariance")
    require(wrong_order_detected, "Relative operator order negative control")
    return {"symplectic_frames": 720, "ordered_frame_pairs": 720 ** 2,
            "distinct_Lagrangians": 15, "metric_triples": 15 ** 3,
            "left_monomial_checks": len(monomials) * 720, "wrong_relative_order_rejected": True,
            "scope": "A complete two-bit control. The proof for general dimension uses invariance of intersection dimension and the triangle inequality."}


def main():
    report_path = LANES / "source-domain/GEODESIC-CHECKS.json"
    require((HERE / "GEODESIC-rerun.json").read_bytes() == report_path.read_bytes(), "Producer reproduction")
    report = json.loads(report_path.read_text())
    word, original = read_source()
    matrices = [canonical_label(frame) for frame in word["frames"]]
    local = {}
    for variant in ("FULL-MODE", "ONE-SIDED-MODE"):
        relative = "history-encoding/" + variant + "-PROGRAMS.json.gz"
        raw = (LANES / relative).read_bytes()
        require(sha256(raw).hexdigest() == PINS[relative], "Mode program pin")
        programs = json.loads(gzip.decompress(raw))
        require(set(programs) == {"forward", "backward"}, "Orientation inventory")
        local[variant] = {}
        for side, program in programs.items():
            result = local_paths(word, program, original[side], matrices)
            saved = report["local_words"][variant][side]
            require(result["rank_mass"] == saved["rank_mass"] and result["counts"]["add"] == saved["scalar_macros"]["add"], "Saved local invoice")
            require(result["counts"]["scale"] == 731 and result["counts"]["climb"] == 3486
                    and result["counts"]["adapter"] + result["counts"]["residual_adapter"] == 1570, "Complete local event count")
            local[variant][side] = result
    sources = {}
    for path, pin in GIT_PINS.items():
        raw = subprocess.check_output(["git", "show", BASE + ":" + path], cwd=REPO)
        require(sha256(raw).hexdigest() == pin, "Pinned global or prior source")
        sources[path] = raw.decode() if path.endswith(".md") else json.loads(raw)
    prior = sources["research/format-limits-corrected/README.md"]
    require("**Theorem N (proof).**" in prior and "Prepared by DreamingOfClouds with Claude Opus 5.5" in prior, "Prior theorem and source credit")
    plan = sources["research/complex-t16-rare-pattern-exchanges/data/PLAN.json"]
    assembly = sources["research/community-frontier1094-audit/ASSEMBLY.json"]
    require((plan["T"], plan["K"], plan["L"], plan["M"], plan["live"], plan["deficit"]) == (16, 4, 9, 73, 14336, 5120), "Pinned global geometry")
    old_profile = Counter({int(k): v for k, v in assembly["complex_profile"].items()})
    mode_path = LANES / "history-encoding/ONE-SHOT-MAX48.json"
    require(sha256(mode_path.read_bytes()).hexdigest() == PINS["history-encoding/ONE-SHOT-MAX48.json"], "Mode plan pin")
    mode_plan = json.loads(mode_path.read_text())
    delta = Counter({8: -1152, 9: 1152})
    for stage, record in enumerate(mode_plan["stages"]):
        require(record["stage"] == stage and record["mode_copies_all_replicas"] == 128
                and record["active"]["rank"] == 9, "Fresh mode cohort")
        for label, axes in (("preparation", 8 * stage), ("completion", 64 - 8 * stage)):
            ranks = [] if not axes else [axes] if axes <= 48 else [48, axes - 48]
            require([child["rank"] for child in record[label]["children_in_execution_order"]] == ranks, "Mode coordinate splits")
            for r in ranks:
                delta[r] += 128
    require(len(mode_plan["stages"]) == 9, "All fresh cohorts")
    before = Counter(old_profile)
    before.update(delta)
    normalized = Counter(before)
    normalized[1] += 14336
    mass = lambda profile: sum(r * count for r, count in profile.items())
    require(mass(old_profile) == 1041408 and mass(before) == 1116288 and mass(normalized) == 1130624, "Complete native rank invoice")
    require(73 * (plan["live"] + 1152) == mass(normalized), "Productive endpoint lower bound")
    require((mass(normalized) - mass(before)) // 16 == 896, "Per-replica average increase")
    require(max(normalized) == 48 and all(count >= 0 for count in normalized.values()), "Admitted profile ranks")
    require({str(r): c for r, c in normalized.items()} == report["global_ledger"]["literal_normalized_profile"], "Saved complete normalized profile")
    toy = clifford_control()
    files = [LANES / "source-domain" / name for name in ("GEODESIC-BOUNDARY.md", "verify_geodesic.py", "GEODESIC-CHECKS.json")]
    files += [LANES / "temporal-reuse/review_wire_gauge.py", HERE / "check_geodesic_review.py"]
    receipt = {
        "status": "ACCEPTED_INDEPENDENT_COMMON_BOUNDARY_PATH_OBSTRUCTION",
        "source_base": BASE, "source_archive_sha256": ARCHIVE_PIN,
        "source_member_pins": MEMBERS, "source_program_pins": PINS, "source_git_pins": GIT_PINS,
        "local_method": "Construct each canonical Lagrangian with a Gaussian nullspace calculation. Compute each distance as the rank of the 9 by 9 symplectic pairing matrix between its two Lagrangians. This also covers source frames with singular Gram matrices. Check each persistent path and scalar access in all four mode words.",
        "source_frames": len(matrices), "local_words": local, "small_Clifford_control": toy,
        "proof": [
            "Apply S(T)^-1 to both spaces in d(Z,S(T)S(U)^-1 Z) to obtain d(L(T),L(U)). This proves the stated order of U T^-1.",
            "The two intersections inside a middle n-dimensional space give dim(L intersect H) >= dim(L intersect K)+dim(K intersect H)-n. This proves the path triangle bound in every dimension.",
            "A left monomial Clifford preserves Z, so it cannot change L(T). A common right gauge at both helper endpoints applies one symplectic map to both spaces and preserves their distance.",
            "The local frame IDs are relative chart labels in both orientations. The backward chart D_U=T_U F_9^-1 has one common right factor, which preserves every local distance. The global common-I/common-F boundary condition is a separate premise.",
            "Retained paths with I and full-F endpoints each have distance 73. Native events belong to one path. Array permutations transport path labels. No productive path may receive a free frame reset or transfer into zero workspace.",
            "The complete pinned profile plus the checked conditional mode delta gives 1116288 before normalizers. The 15488 common-boundary productive paths require 1130624, an increase of 14336, or 896 per replica on average.",
            "All ranks in the literal normalized profile are below 73. Its rank mass equals 73N, so its moment equals one at exponent zero and exceeds one for every positive exponent. Any admitted retained-path fusion with ranks at most 73 still has moment at least one."
        ],
        "global_ledger": report["global_ledger"],
        "executed_negative_controls": report["negative_controls"],
        "scope": "Retained persistent array paths, their scalar accesses, and common-I/common-F productive endpoints with identity joint content. This is not a lower bound for virtual-Q boundaries or changed controllers.",
        "inherited_premises": ["Exact mode phases and full-F monomial access from the separate interface reviews", "The whole-owner hosting and backfill invoice", "The original selected supplier's native lowering"],
        "not_rerun": ["A global native emitter", "New owner allocation or supplier admission", "The old selected supplier's full admission", "Scalar or address pricing"],
        "scratch_scope": "The emitted array macros have no COPY, CLEAR, or C-bank references. Private scalar temporaries do not add productive native paths. New persistent workspace and lifetime transfers are outside this theorem.",
        "prior_credit": {"source": "https://github.com/CrocSwap/integer-mult-bounds/blob/" + BASE + "/research/format-limits-corrected/README.md#L392-L438",
                         "statement": "Section C.2, Theorem N already gives the canonical-subspace port-gauge geodesic bound.",
                         "source_credit": "The pinned README credits DreamingOfClouds with Claude Opus 5.5 assistance. No external account identity was inferred."},
        "reviewed_files_sha256": {str(path): sha256(path.read_bytes()).hexdigest() for path in files},
        "maximum_resident_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (HERE / "GEODESIC-REVIEW.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print("all_four_local_words=true normalized_rank=1130624 minimum_added_rank=14336")


if __name__ == "__main__":
    main()
