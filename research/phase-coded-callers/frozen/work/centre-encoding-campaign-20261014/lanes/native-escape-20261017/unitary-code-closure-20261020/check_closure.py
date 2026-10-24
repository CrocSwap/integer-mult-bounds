"""Check the exact fresh-stage path separation for unitary scalar codes."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "unitary": (
        "new-core-transfer-20261017/low-displacement-20261020/"
        "metric-completion-20261020/unitary-v2-normal/UNITARY-COMPLETION.json.gz",
        "fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428",
    ),
}
ZERO, ONE = (F(0), F(0)), (F(1), F(0))
I_POWER = (ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))


def need(test, message):
    if not test:
        raise ValueError(message)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def serialized(a):
    return [str(a[0]), str(a[1])]


def matrix(raw):
    return [{int(j): tuple(map(F, coefficient)) for j, coefficient in row.items()}
            for row in raw]


def matmul(a, b):
    result = []
    for row in a:
        out = {}
        for j, c in row.items():
            for k, d in b[j].items():
                out[k] = plus(out.get(k, ZERO), times(c, d))
        result.append({k: c for k, c in out.items() if c != ZERO})
    return result


def act(columns, vector):
    result = 0
    while vector:
        low = vector & -vector
        result ^= columns[low.bit_length() - 1]
        vector ^= low
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    source, pins = {}, {}
    for key, (relative, pin) in PINS.items():
        path = LANES / relative
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, "Exact source " + key)
        source[key] = json.loads(raw)
        pins[key] = {"path": str(path), "sha256": pin}
    entries = {(row["stage"], row["port"]): row for row in source["views"]["entries"]}
    unit = tuple(1 << j for j in range(25))
    omega = (1 << 9) - 1
    fresh1 = sum(unit[9:17])
    fresh2 = sum(unit[17:25])
    q = [entries[0, p]["q"] for p in range(112)]
    need(source["unitary"]["ports"] == q,
         "The code and route payloads use the same physical port order")
    need(all(entries[s, p]["q"] == q[p] for s in range(3) for p in range(112)),
         "Every stage retains the same intrinsic port label")
    routes = {(s, p): tuple(entries[s, p]["route_columns"])
              for s in range(3) for p in range(112)}
    shifts = {(s, p): entries[s, p]["literal_stage_alignment"]["exit_X"]
              for s in (1, 2) for p in range(112)}
    need(len(set(q)) == 112, "Distinct intrinsic port lines")
    by_q = {line: p for p, line in enumerate(q)}
    basis_checks = 0
    for p in range(112):
        need(routes[0, p] == unit, "The root route is the identity")
        for s in (1, 2):
            rho = routes[s, p]
            need(tuple(act(rho, col) for col in rho) == unit, "Route involution")
            need(act(rho, q[p]) == q[p], "The route fixes its own line")
            need(all((a & b).bit_count() % 2 == int(i == j)
                     for i, a in enumerate(rho) for j, b in enumerate(rho)),
                 "The literal route is orthogonal")
            need(act(rho, shifts[s, p]) == shifts[s, p],
                 "The FULL affine view is an involution")
        need(act(routes[1, p], fresh1) == omega ^ q[p],
             "Stage one maps the fresh characteristic vector to the root complement")
        need(act(routes[2, p], fresh2) == omega ^ q[p],
             "Stage two maps the fresh characteristic vector to the root complement")
        need(all(act(routes[1, p], v) == v for v in unit[17:25]) and
             all(act(routes[2, p], v) == v for v in unit[9:17]),
             "Each route fixes the other fresh block")
        basis_checks += 2

    signatures, affine_signatures, certificate = {}, set(), []
    inner_shifts = {}
    for j in range(112):
        for r in range(112):
            image2 = act(routes[2, j], act(routes[1, j], act(routes[1, r], fresh2)))
            image1 = act(routes[2, j], act(routes[1, j], act(routes[1, r], fresh1)))
            signature = image2, image1
            need(signature not in signatures, "Distinct paths have distinct route signatures")
            signatures[signature] = (j, r)
            recovered_j = by_q[omega ^ image2]
            recovered_r = by_q[
                omega ^ act(routes[1, recovered_j], act(routes[2, recovered_j], image1))]
            need((recovered_j, recovered_r) == (j, r), "The two images recover both path indices")
            shift = (shifts[2, j] ^ act(routes[2, j], shifts[1, j]) ^
                     act(routes[2, j], act(routes[1, j], shifts[1, r])))
            inner_shifts[j, r] = shift
            # Use one input with the three payload columns (0, fresh2, fresh1).
            affine_signature = tuple(
                shifts[2, 0] ^ act(routes[2, 0], value)
                for value in (shift, shift ^ image2, shift ^ image1))
            need(affine_signature not in affine_signatures,
                 "One physical width-three input separates all paths")
            affine_signatures.add(affine_signature)
            certificate.append([j, r, image2, image1, shift, list(affine_signature)])
    need(len(signatures) == 112 * 112, "All ordered intermediate pairs are distinct")

    c = matrix(source["unitary"]["code"])
    adjoint = matrix(source["unitary"]["inverse_and_adjoint"])
    transpose = [{} for _ in range(112)]
    for p, row in enumerate(c):
        need(p not in row, "Physical code has zero diagonal")
        for j, coefficient in row.items():
            need(coefficient != ZERO, "Every stored code coefficient is nonzero")
            transpose[j][p] = conjugate(coefficient)
    need(transpose == adjoint, "Stored inverse is the physical adjoint")
    identity = [{p: ONE} for p in range(112)]
    need(matmul(c, adjoint) == matmul(adjoint, c) == identity, "Both unitary orders")
    families = {"C": c, "Cstar": adjoint}
    profiles, basis_witnesses, commutator_witnesses = {}, [], []
    for names in product(families, repeat=3):
        c0, c1, c2 = [families[name] for name in names]
        row_counts = [
            sum(len(c0[r]) for j in c2[p] for r in c1[j])
            for p in range(112)
        ]
        need(min(row_counts) > 1, "Every routed output row is nonmonomial")
        profiles["/".join(names)] = {
            "operator_terms": sum(row_counts),
            "minimum_row_terms": min(row_counts),
            "maximum_row_terms": max(row_counts),
            "row_term_histogram": dict(sorted(Counter(row_counts).items())),
        }
        for p in range(112):
            paths = {}
            for j, a2 in sorted(c2[p].items()):
                for r, a1 in sorted(c1[j].items()):
                    for k, a0 in sorted(c0[r].items()):
                        paths.setdefault(k, []).append((j, r, times(a2, times(a1, a0))))
            k = next(k for k, records in paths.items() if len(records) >= 2)
            point_outputs = []
            for j, r, coefficient in paths[k][:2]:
                def image(vector):
                    for s, port in ((1, r), (1, j), (2, j), (2, p)):
                        vector = act(routes[s, port], vector)
                    return vector
                shift = shifts[2, p] ^ act(routes[2, p], inner_shifts[j, r])
                point_outputs.append({
                    "path": [j, r], "coefficient": serialized(coefficient),
                    "output": [shift, shift ^ image(fresh2), shift ^ image(fresh1)],
                })
            need(point_outputs[0]["output"] != point_outputs[1]["output"],
                 "One input column has at least two nonzero output coordinates")
            basis_witnesses.append({
                "variant": "/".join(names), "output_port": p, "input_port": k,
                "input_columns": [0, fresh2, fresh1], "outputs": point_outputs,
            })

            j, a2 = next(iter(sorted(c2[p].items())))
            r, a1 = next(iter(sorted(c1[j].items())))
            k, a0 = next(iter(sorted(c0[r].items())))
            coefficient = times(a2, times(a1, a0))

            def image(vector):
                for s, port in ((1, r), (1, j), (2, j), (2, p)):
                    vector = act(routes[s, port], vector)
                return vector

            pulled = q[p]
            for s, port in ((2, p), (2, j), (1, j), (1, r)):
                pulled = act(routes[s, port], pulled)
            need(pulled != q[k], "The chosen path does not preserve the intrinsic line")
            chars = [fresh2, fresh1]
            phase_difference = (
                sum((q[p] & image(x)).bit_count() % 2 for x in chars) -
                sum((q[k] & x).bit_count() % 2 for x in chars)) % 4
            chars.append(0 if phase_difference else (pulled ^ q[k]) & -(pulled ^ q[k]))
            outputs = [image(x) for x in chars]
            exponent_out = sum((q[p] & x).bit_count() % 2 for x in outputs) % 4
            exponent_in = sum((q[k] & x).bit_count() % 2 for x in chars) % 4
            phase = plus(I_POWER[exponent_out],
                         (-I_POWER[exponent_in][0], -I_POWER[exponent_in][1]))
            need(phase != ZERO, "The isolated Fourier branch has a nonzero phase difference")
            shift = shifts[2, p] ^ act(routes[2, p], inner_shifts[j, r])
            sign = (-1) ** sum((shift & x).bit_count() % 2 for x in outputs)
            physical_coefficient = times(times(coefficient, (F(sign), F(0))), phase)
            need(physical_coefficient != ZERO, "The affine phase does not cancel the witness")
            commutator_witnesses.append({
                "variant": "/".join(names), "output_port": p, "input_port": k,
                "path": [j, r], "coefficient": serialized(coefficient),
                "input_characters": chars, "output_characters": outputs,
                "output_line_pulled": pulled, "input_line": q[k],
                "output_exponent": exponent_out, "input_exponent": exponent_in,
                "affine_shift": shift, "affine_sign": sign,
                "physical_commutator_coefficient": serialized(physical_coefficient),
            })

    # Scalar multiplication can cancel coefficients when the stage routes are removed.
    scalar_cube = matmul(c, matmul(c, c))
    scalar_count = sum(map(len, scalar_cube))
    routed_count = profiles["C/C/C"]["operator_terms"]
    need(scalar_count < routed_count, "The constant-sector product is not the routed product")
    selected = source["unitary"]["selected_full_ports"]
    readers = matrix(source["unitary"]["original_centre_readers"])
    need(len(selected) == 32 and len(readers) == 16, "Actual centre interface sizes")
    need(len({j for row in readers for j in row}) == 112,
         "Every input port occurs in the original centre readers")
    raw_certificate = (json.dumps(certificate, separators=(",", ":")) + "\n").encode()
    (args.out / "PATH-SIGNATURES.json.gz").write_bytes(gzip.compress(raw_certificate, mtime=0))
    witnesses = {
        "basis_witnesses": basis_witnesses,
        "commutator_witnesses": commutator_witnesses,
    }
    witness_raw = (json.dumps(witnesses, separators=(",", ":"), sort_keys=True) + "\n").encode()
    (args.out / "WIDTH-THREE-WITNESSES.json.gz").write_bytes(gzip.compress(witness_raw, mtime=0))
    receipt = {
        "status": "PASS_ACTUAL_FRESH_STAGE_PATH_SEPARATION",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": pins,
        "distinct_intrinsic_lines": len(set(q)),
        "root_complement_basis_checks": basis_checks,
        "distinct_intermediate_path_pairs": len(signatures),
        "single_physical_input_affine_outputs": len(affine_signatures),
        "signature_decompressed_sha256": sha256(raw_certificate).hexdigest(),
        "witness_decompressed_sha256": sha256(witness_raw).hexdigest(),
        "basis_column_witnesses": len(basis_witnesses),
        "exact_affine_commutator_witnesses": len(commutator_witnesses),
        "logical_path_separation_minimum_width": 2,
        "physical_path_and_commutator_minimum_width": 3,
        "code_row_counts": dict(sorted(Counter(map(len, c)).items())),
        "adjoint_row_counts": dict(sorted(Counter(map(len, adjoint)).items())),
        "routed_variant_profiles": profiles,
        "constant_sector_C_cube_terms": scalar_count,
        "original_centre_reader_source_support": 112,
        "actual_selected_output_coordinates": 32,
        "scope": (
            "Three constant scalar current-chart codes with the actual D25 "
            "routes. One common width-three basis input separates the literal "
            "affine paths. Exact Fourier-character witnesses show Q noncommutation. "
            "There is no small-width independence assumption, general native "
            "decoder lower bound, or claim for an operator-valued code."
        ),
    }
    (args.out / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": receipt["status"], "paths": len(signatures),
        "routed_variants": profiles, "constant_sector_terms": scalar_count,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
