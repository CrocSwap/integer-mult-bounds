"""Independently check the cover trace and its fixed-stock application."""

from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import io
import json
import tarfile


PHASES = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
PHASES_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
INTERFACE_SHA = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(a, b):
    return (a & b).bit_count() % 2


def apply(columns, x):
    answer = 0
    for i, col in enumerate(columns):
        if (x >> i) & 1:
            answer ^= col
    return answer


def product(left, right):
    return tuple(apply(left, col) for col in right)


def swap_route(q, basis, stage):
    first = 9 + 8 * (stage - 1)
    columns = [1 << i for i in range(73)]
    for i in range(9):
        columns[i] = q if (q >> i) & 1 else 0
        for j, b in enumerate(basis):
            if (b >> i) & 1:
                columns[i] ^= 1 << (first + j)
    columns[first:first + 8] = basis
    return tuple(columns)


def run(repo, campaign):
    own_source = Path(__file__).with_name("verify_domain.py")
    spec = spec_from_file_location("domain_source", own_source)
    source = module_from_spec(spec)
    spec.loader.exec_module(source)
    interface_file = campaign / "lanes/circuit-interface/INTERFACE.json"
    interface_raw = interface_file.read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE_SHA, "The interface changed")
    interface = json.loads(interface_raw)
    with tarfile.open(fileobj=io.BytesIO(source.source(repo, source.ARCHIVE)), mode="r:gz") as stream:
        phase_raw = stream.extractfile(PHASES).read()
        require(sha256(phase_raw).hexdigest() == PHASES_SHA, "The data phases changed")
        phases = json.loads(phase_raw)
        word = json.loads(gzip.decompress(source.pin(source.WORD, stream.extractfile(source.WORD).read())))
        programs = json.loads(gzip.decompress(source.pin(source.PROGRAMS, stream.extractfile(source.PROGRAMS).read())))
    r = source.clean_centre_map(word, programs["forward"])
    require(r == [[Q(interface["R"][i].get(str(j), "0")) for j in range(112)]
                  for i in range(8)], "The interface matrix differs from the frozen word")
    ports = word["ports"]
    require([x["q"] for x in phases["recipes"]] == ports, "The phase port order changed")
    a = [[sum(r[k][i] * r[k][j] for k in range(8)) for j in range(112)] for i in range(112)]
    identity = tuple(1 << i for i in range(73))
    routes = []
    full_dimension_checks = 0
    for q, recipe in zip(ports, phases["recipes"]):
        basis = recipe["idle_children"][0]["orthogonal_axes"][:8]
        require(len(basis) == 8 and all(x < 512 and not parity(q, x) for x in basis),
                "The pinned local complement is invalid")
        require(all(parity(x, y) == (i == j) for i, x in enumerate(basis)
                    for j, y in enumerate(basis)), "The pinned complement is not orthonormal")
        route1 = swap_route(q, basis, 1)
        routes.append(route1)
        for stage in range(1, 9):
            route = swap_route(q, basis, stage)
            require(product(route, route) == identity, "A full route is not an involution")
            require(all(parity(x, y) == (i == j) for i, x in enumerate(route)
                        for j, y in enumerate(route)), "A full route is not orthogonal")
            transport = list(identity)
            for j in range(8):
                left, right = 9 + j, 9 + 8 * (stage - 1) + j
                transport[left], transport[right] = transport[right], transport[left]
            require(product(product(tuple(transport), route1), tuple(transport)) == route,
                    "The 73-dimensional stage embedding changed")
            full_dimension_checks += 1

    buckets = defaultdict(list)
    for b in range(112):
        for c in range(112):
            if a[b][c]:
                buckets[product(routes[b], routes[c])].append((b, c))
    require(len(buckets) == 5825, "The full group labels have different collisions")
    require(buckets[identity] == [(i, i) for i in range(112)], "The identity bucket changed")
    require(all(len(items) == 1 for g, items in buckets.items() if g != identity),
            "Different ordered edges have the same group element")

    # Sum the trace coefficients from the actual group product equality.
    # This does not use the two-case closed formula in the reviewed verifier.
    fourth_integer = Q(0)
    for items in buckets.values():
        for b, c in items:
            for aa, d in items:
                fourth_integer += a[aa][b] * a[b][c] * a[c][d] * a[d][aa]
    first = sum(a[i][i] ** 2 for i in range(112)) / 56 ** 2
    second = fourth_integer / 56 ** 4
    require((first, second) == (Q(4, 7), Q(27, 343)), "The independent trace differs")
    tau_m2 = 16 - 2 * first
    tau_m4 = 16 - 4 * first + 2 * second
    rank_bound = tau_m2 ** 2 / tau_m4
    shift = Q(13, 196)
    common_bound = (second - 2 * shift * first + 8 * shift ** 2) / (1 - shift) ** 2
    require((rank_bound, common_bound) == (Q(2912, 183), Q(8, 183)), "The rank bound changed")

    g01, g10 = product(routes[0], routes[1]), product(routes[1], routes[0])
    require(g01 != g10, "The ordering control does not distinguish multiplication")
    require(all(apply(g01, 1 << i) == apply(routes[0], apply(routes[1], 1 << i))
                for i in range(73)), "The matrix product order is wrong")
    require(all(g01[i] == 1 << i for i in range(17, 73)), "The 17D support is not fixed")
    require(all(g[i] == 1 << i for g in buckets for i in range(17, 73)),
            "A group product escapes the 17D block")

    seen = {0}
    todo = [0]
    while todo:
        i = todo.pop()
        for j in range(112):
            if i != j and a[i][j] and j not in seen:
                seen.add(j)
                todo.append(j)
    require(len(seen) == 112, "The nullspace code graph is not connected")

    margin = Q(896, 73)
    repeated_moment = Q(72 * 896) / (73 * (896 - rank_bound))
    single_global_moment = Q(72 * 14336) / (73 * (14336 - rank_bound))
    require(rank_bound > margin and repeated_moment > 1, "The repeated code was not rejected")
    require(single_global_moment < 1, "The multiplicity control is not effective")
    # On constant cover functions every group element acts as identity.
    # In that representation Q=P, so their difference has rank zero.
    trivial_trace_pq = sum(a[i][j] ** 2 for i in range(112) for j in range(112)) / 56 ** 2
    require(trivial_trace_pq == 8 != first, "The quotient control does not change the trace")

    reviewed = {name: sha256((campaign / "lanes/cover-algebra" / name).read_bytes()).hexdigest()
                for name in ("PROOF.md", "verify_algebra.py")}
    return {
        "status": "PASS_INDEPENDENT_73D_COVER_TRACE_REVIEW",
        "reviewed_files_sha256": reviewed, "interface_sha256": INTERFACE_SHA,
        "source_base": source.BASE, "phase_source_sha256": PHASES_SHA,
        "source_matrix_rederived": True, "full_73d_routes_checked": full_dimension_checks,
        "nonidentity_group_product_buckets": len(buckets) - 1,
        "trace_PQ": str(first), "trace_PQPQ": str(second),
        "difference_trace_square": str(tau_m2), "difference_trace_fourth": str(tau_m4),
        "rank_lower_bound_per_cover_element": str(rank_bound),
        "common_range_upper_bound_per_cover_element": str(common_bound),
        "allowed_codimension_per_replica": str(margin),
        "rank_bound_excess": str(rank_bound - margin),
        "fixed_stock_moment_if_one_coded_bank_per_replica": str(repeated_moment),
        "single_coded_bank_in_all_16_replicas_is_not_excluded_at_zero": str(single_global_moment),
        "trivial_representation_control": {"trace_PQ": str(trivial_trace_pq), "rank_difference": 0},
        "code_projector_graph_component_sizes": [len(seen)],
        "review_findings": ["Corrected a contradictory index condition in the proof case split; the moment value was unchanged."],
        "not_reviewed": ["optional sixth moment", "native phase implementation", "new supplier", "new kappa"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.repo, args.campaign)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("routes73=896 trace_PQ=4/7 trace_PQPQ=27/343 rank>=2912/183>896/73")
