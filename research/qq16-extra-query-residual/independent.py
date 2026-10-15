#!/usr/bin/env python3
"""Independent, source-derived QQ16 three-query trace audit.

No research-package module is imported. The query rows are reconstructed by
reverse covector propagation; native routes are constructed by swapping two
orthonormal coordinate blocks. Output is deterministic exact JSON. The
finite audit does not enumerate the cover and is not a supplier admission.

Apache-2.0. Substantial mathematical and implementation assistance: OpenAI
Codex. Original scalar programs and native charts retain their source credits.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile


SOURCE_BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE_PATH = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz": (
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
        "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c"),
    "slots/local/LOCAL-PROGRAMS.json.gz": (
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
        "9f41d53659e9be84e20c661560c5687abbf5cd0660cdecbe01ad5eb29e6b8ee3"),
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json": (
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"),
}
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
DIMENSION = 73
IDENTITY = tuple(1 << j for j in range(DIMENSION))


class AuditError(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise AuditError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(raw, expected, name):
    require(digest(raw) == expected, "source digest: " + name)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def exact_json(value):
    if isinstance(value, Fraction):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, (list, tuple)):
        return [exact_json(x) for x in value]
    if isinstance(value, dict):
        return {str(k): exact_json(v) for k, v in value.items()}
    return value


def read_sources(repo):
    raw = subprocess.check_output(
        ["git", "show", SOURCE_BASE + ":" + ARCHIVE_PATH], cwd=repo)
    pinned(raw, ARCHIVE_SHA, ARCHIVE_PATH)
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for name, (compressed_sha, payload_sha) in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(),
                    "exactly one regular archive member: " + name)
            member = archive.extractfile(matches[0]).read()
            pinned(member, compressed_sha, name)
            payload = gzip.decompress(member) if name.endswith(".gz") else member
            pinned(payload, payload_sha, name + " payload")
            decoded[name.rsplit("/", 1)[1]] = json.loads(payload)
    return decoded


def register(token):
    kind, at = token
    require(kind in ("L", "C"), "declared register kind")
    require(0 <= at < (704 if kind == "L" else 8), "declared register index")
    return at + (704 if kind == "C" else 0)


def query_by_reverse_covectors(word, programs):
    """Pull each centre output row back through the scalar prefix.

    For x_t <- x_t+c*x_s, a covector coefficient w_t contributes c*w_t
    to w_s. All 712 input positions remain distinct until the final
    projection onto the 112 source coordinates; no clean-input assumption
    is used to discard dependencies during the propagation.
    """
    require((word["v"], word["R"], word["h"]) == (112, 480, 9),
            "source geometry")
    program = programs["forward"]
    cuts = [i for i, e in enumerate(program) if e == ["phase", "centers"]]
    require(len(cuts) == 1, "unique centre boundary")
    require(len(set(word["centers"])) == 8, "eight distinct centre outputs")
    rows, nuisance = [], []
    for centre in word["centers"]:
        covector = {centre: Fraction(1)}
        for event in reversed(program[:cuts[0]]):
            if event[0] != "scalar":
                continue
            op = event[1]
            kind, target = op[0], register(op[1])
            require(kind in ("clear", "scale", "copy", "add"),
                    "known scalar operation")
            weight = covector.get(target, Fraction(0))
            if not weight:
                continue
            if kind == "clear":
                del covector[target]
            elif kind == "scale":
                covector[target] = weight * Fraction(op[2], op[3])
            else:
                source = register(op[2])
                require(target != source, "distinct scalar operands")
                if kind == "copy":
                    del covector[target]
                    amount = weight
                else:
                    amount = weight * Fraction(op[3], op[4])
                total = covector.get(source, Fraction(0)) + amount
                if total:
                    covector[source] = total
                else:
                    covector.pop(source, None)
        require(not any(112 <= p < 224 or p >= 704 for p in covector),
                "centre source/helper decomposition")
        rows.append([covector.get(p, Fraction(0)) for p in range(112)])
        nuisance.append({p: x for p, x in covector.items() if p >= 224})
    require(all(x.denominator == 1 for row in rows for x in row),
            "integer source query")
    return rows, nuisance, cuts[0]


def gf2_apply(columns, vector):
    require(0 <= vector < 1 << len(columns), "binary vector domain")
    result = 0
    for j, column in enumerate(columns):
        if vector & (1 << j):
            result ^= column
    return result


def gf2_product(left, right):
    """Columns of left*right: right acts first on a column vector."""
    require(len(left) == len(right) == DIMENSION, "route dimensions")
    return tuple(gf2_apply(left, x) for x in right)


def gf2_transpose(columns):
    return tuple(sum(((columns[j] >> i) & 1) << j for j in range(DIMENSION))
                 for i in range(DIMENSION))


def route_by_coordinate_swap(chart, stage):
    """Fix q and swap b_1,...,b_8 with the stage's eight spare axes.

    This is an orthonormal-basis coordinate calculation, rather than the
    native verifier's transvection construction.
    """
    if stage == 0:
        return IDENTITY
    columns = []
    for x in IDENTITY:
        y = x
        for k, b in enumerate(chart[1:]):
            spare = 1 << (9 + 8 * (stage - 1) + k)
            if (x & b).bit_count() % 2:
                y ^= b ^ spare
            if x & spare:
                y ^= spare ^ b
        columns.append(y)
    return tuple(columns)


def native_routes(word, phases):
    require(phases["m"] == DIMENSION and len(phases["recipes"]) == 112,
            "source native dimension and port count")
    routes = [[], [], []]
    for p, record in enumerate(phases["recipes"]):
        require(record["port"] == p and record["q"] == word["ports"][p],
                "source port binding")
        chart = [record["q"]] + record["idle_children"][0]["orthogonal_axes"][:8]
        require(len(chart) == 9 and all(0 < x < 512 for x in chart),
                "nine local binary chart axes")
        require(all((chart[i] & chart[j]).bit_count() % 2 == int(i == j)
                    for i in range(9) for j in range(9)), "orthonormal chart")
        beta = sum((((b.bit_count() - 1) // 2) % 2) << k
                   for k, b in enumerate(chart[1:]))
        beta_chart = 0
        for k, b in enumerate(chart[1:]):
            if beta & (1 << k):
                beta_chart ^= b
        for stage in range(3):
            g = route_by_coordinate_swap(chart, stage)
            require(gf2_product(g, g) == IDENTITY, "route involution")
            require(gf2_transpose(g) == g, "route orthogonality")
            require(gf2_apply(g, chart[0]) == chart[0], "route fixes port normal")
            if stage:
                for k, b in enumerate(chart[1:]):
                    spare = 1 << (9 + 8 * (stage - 1) + k)
                    require(gf2_apply(g, b) == spare and gf2_apply(g, spare) == b,
                            "route swaps the actual chart and stage axes")
                entry = chart[0] ^ beta_chart
                exit_value = beta_chart ^ (beta << (9 + 8 * (stage - 1)))
            else:
                entry = exit_value = 0
            require(record["stage_alignment"][stage] == {
                "entry_X": entry, "entry_Y": entry,
                "exit_X": exit_value, "exit_Y": exit_value},
                "source stage-alignment binding")
            routes[stage].append(g)
    return routes


def zero(size=8):
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def matmul(left, right):
    rt = transpose(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in rt]
            for row in left]


def trace(matrix):
    return sum(matrix[i][i] for i in range(len(matrix)))


def gram(columns):
    return [[sum(c[i] * c[j] for c in columns) for j in range(8)]
            for i in range(8)]


def scalar_identity(value):
    return [[Fraction(value * (i == j)) for j in range(8)] for i in range(8)]


def cross_identity_coefficient(columns, relative_routes):
    """Compute [e] C C* with C=B_s B_t*, retaining every collision.

    Write C=sum_g K_g D_g, K_g=sum_{p:g_p=g} r_p r_p^T.
    Since D_g D_h*=D_(g h^-1), [e] C C*=sum_g K_g K_g^T.
    No port-index distinctness is assumed by this computation.
    """
    require(len(columns) == len(relative_routes), "one route per column")
    buckets = {}
    multiplicity = Counter(relative_routes)
    for column, g in zip(columns, relative_routes):
        block = buckets.setdefault(g, zero())
        for i in range(8):
            for j in range(8):
                block[i][j] += column[i] * column[j]
    coefficient = zero()
    for block in buckets.values():
        square = matmul(block, transpose(block))
        for i in range(8):
            for j in range(8):
                coefficient[i][j] += square[i][j]
    return coefficient, dict(sorted(Counter(multiplicity.values()).items()))


def require_distinct(relative_routes):
    require(len(relative_routes) == len(set(relative_routes)) == 96,
            "96 distinct relative routes")


def require_column_gram(columns):
    require(gram(columns) == scalar_identity(48), "ordinary column Gram")


def expect_rejection(action, reason):
    try:
        action()
    except AuditError as exc:
        require(str(exc) == reason, "negative control rejected by wrong check")
        return
    raise AuditError("negative control unexpectedly accepted: " + reason)


def controls(columns, routes, relatives, source_payload):
    # The first two actual U columns have inner product two, so their
    # forced collision contributes a visible off-diagonal port term.
    collision = relatives.copy()
    collision[1] = collision[0]
    expect_rejection(lambda: require_distinct(collision), "96 distinct relative routes")
    collided, histogram = cross_identity_coefficient(columns, collision)
    require(trace(collided) == 1544, "collision-aware cross-term control")
    require(histogram == {1: 94, 2: 1}, "collision histogram control")
    bad_columns = [c.copy() for c in columns]
    bad_columns[0][0] += 1
    expect_rejection(lambda: require_column_gram(bad_columns), "ordinary column Gram")
    # The algebra must admit a harmless port reordering and independent
    # signs of whole source columns.
    transformed = [[-x for x in c] for c in reversed(columns)]
    transformed_relatives = list(reversed(relatives))
    require(cross_identity_coefficient(transformed, transformed_relatives)[0]
            == scalar_identity(192), "reordering/sign positive control")
    require_column_gram(transformed)
    expected_sha = digest(source_payload)
    expect_rejection(lambda: pinned(source_payload + b" ", expected_sha, "control"),
                     "source digest: control")
    # Orientation cannot be checked by the trace alone: the actual stage
    # routes do not commute, even though reversing every relative route
    # leaves the Gram trace unchanged. Check their ordered action itself.
    g, h = routes[1][U[0]], routes[2][U[0]]
    gh, hg = gf2_product(g, h), gf2_product(h, g)
    witness = next(j for j in range(DIMENSION) if gh[j] != hg[j])
    x = 1 << witness
    require(gh[witness] == gf2_apply(g, gf2_apply(h, x)), "ordered route product")
    expect_rejection(lambda: require(hg[witness] == gf2_apply(g, gf2_apply(h, x)),
                                    "ordered route product"),
                     "ordered route product")
    return {
        "route_collision": {"distinct_routes": 95, "identity_coefficient_trace": 1544,
                            "named_distinctness_check": "REJECT"},
        "coefficient_change": "REJECT: ordinary column Gram",
        "port_reordering_and_whole_column_signs": "PASS",
        "source_payload_mutation": "REJECT: source digest",
        "reversed_noncommuting_route_product": {
            "status": "REJECT: ordered route product", "port": U[0],
            "basis_axis": witness, "correct_image": gh[witness], "reversed_image": hg[witness]},
    }


def audit(repo):
    source = read_sources(repo)
    word = source["CANONICAL-WORD.json.gz"]
    rows, nuisance, cut = query_by_reverse_covectors(word, source["LOCAL-PROGRAMS.json.gz"])
    routes = native_routes(word, source["DATA-PHASES.json"])
    columns = [[row[p] for row in rows] for p in U]
    require(all(sum(x*x for x in c) == 4 for c in columns), "96 column norms")
    require_column_gram(columns)
    same = gram(columns)
    results, relatives = {}, {}
    for s, t in ((0, 1), (0, 2), (1, 2)):
        # B_s B_t*: rho_s followed in the right regular action by rho_t^-1.
        relative = [gf2_product(routes[s][p], gf2_transpose(routes[t][p])) for p in U]
        coefficient, multiplicities = cross_identity_coefficient(columns, relative)
        require_distinct(relative)
        require(coefficient == scalar_identity(192), "cross identity coefficient")
        key = str(s) + "," + str(t)
        relatives[key] = relative
        results[key] = {
            "operator": "B_s B_t* B_t B_s*", "relative_route_order": "rho_s(p) rho_t(p)^-1",
            "distinct_relative_routes": len(set(relative)),
            "route_multiplicity_histogram": multiplicities,
            "relative_route_columns_sha256": digest(canonical(relative)),
            "identity_coefficient": coefficient, "identity_coefficient_trace": trace(coefficient),
        }
    tr = 3 * trace(same)
    tr_square = 3 * trace(matmul(same, same)) + 2 * sum(
        item["identity_coefficient_trace"] for item in results.values())
    rank_lower = tr * tr / tr_square
    residual_lower = rank_lower - 16
    return exact_json({
        "status": "PASS_INDEPENDENT_QQ16_THREE_QUERY_TRACE",
        "source": {"base": SOURCE_BASE, "archive_path": ARCHIVE_PATH,
                   "archive_sha256": ARCHIVE_SHA,
                   "member_sha256_and_payload_sha256": MEMBERS},
        "reconstruction": {
            "method_R": "reverse covectors on all 712 independent input positions, then source projection",
            "method_routes": "orthonormal chart/stage coordinate swaps; 73 binary columns per route",
            "scalar_prefix_event_count": cut, "centre_output_registers": word["centers"],
            "retained_helper_dependencies_per_row": [len(row) for row in nuisance],
            "R_dense": exact_json(rows),
            "R_dense_sha256": digest(canonical(exact_json(rows))),
            "R_rows_integer_json_sha256": digest(canonical(exact_json(rows))),
            "routes_U96_stage_major_sha256": digest(canonical(
                [routes[stage][port] for stage in range(3) for port in U])),
            "stage_0_1_2_route_columns_sha256": digest(canonical(routes)),
            "A_ports": A, "T_ports": T, "U_ports": U,
            "U_column_squared_norm_histogram": {"4": len(U)},
        },
        "same_stage_gram": same, "stage_pairs": results,
        "trace_coefficients_per_regular_cover_order": {
            "stacked_Gram_trace": tr, "stacked_Gram_square_trace": tr_square,
            "stacked_query_rank_lower_bound": rank_lower,
            "rank_B0_restricted_to_joint_kernel_B1_B2_lower_bound": residual_lower,
        },
        "controls": controls(columns, routes, relatives["1,2"], canonical(exact_json(rows))),
        "scope": {
            "finite_coverage": "112 actual R columns and stage 0/1/2 routes; all 96 ordinary columns and all three pairs",
            "representation": "finite regular right cover action, payload-constant fields; arbitrary cover values",
            "matrix_convention": "GF(2) matrices stored as columns; product(g,h) maps x to g(h(x)); D_gD_h=D_(gh)",
            "collision_rule": "sum over each relative-route bucket K_g of K_g K_g^T",
            "not_checked": ["full regular cover enumeration", "QQ16 chronological trajectory", "native phase replay", "precision or physical routing costs", "complete supplier", "new kappa"],
        },
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(audit(args.repo), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
