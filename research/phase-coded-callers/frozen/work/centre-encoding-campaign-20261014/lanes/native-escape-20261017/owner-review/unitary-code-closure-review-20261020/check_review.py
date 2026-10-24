"""Check common-input route separation and exact commutator witnesses."""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
from itertools import product
import json
from pathlib import Path
import shutil


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
PINS = {
    "views": (
        LANES / "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "unitary": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/"
        "metric-completion-20261020/unitary-v2-normal/UNITARY-COMPLETION.json.gz",
        "fd3b442caa13104cef4b7c046e1c2781f2ffa216d8d098b4e2a4e51e6063f428",
    ),
}
ZERO, ONE = (F(0), F(0)), (F(1), F(0))
UNITS = tuple(1 << j for j in range(25))
OMEGA = sum(UNITS[:9])
E1, E2 = sum(UNITS[9:17]), sum(UNITS[17:25])


def need(ok, label):
    if not ok:
        raise ValueError(label)


def digest(raw):
    return sha256(raw).hexdigest()


def act(columns, vector):
    value = 0
    for bit, column in enumerate(columns):
        if vector & (1 << bit):
            value ^= column
    return value


def dot(x, y):
    return (x & y).bit_count() & 1


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def sparse(raw):
    return [{int(j): tuple(map(F, value)) for j, value in row.items()} for row in raw]


def matmul(a, b):
    result = []
    for row in a:
        out = {}
        for j, c in row.items():
            for k, d in b[j].items():
                out[k] = add(out.get(k, ZERO), mul(c, d))
        result.append({k: value for k, value in out.items() if value != ZERO})
    return result


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return digest(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, "At least 3 GiB free")
    args.out.mkdir(parents=True, exist_ok=False)
    source, manifest = {}, {}
    for name, (path, pin) in PINS.items():
        raw = path.read_bytes()
        decoded = gzip.decompress(raw) if path.suffix == ".gz" else raw
        need(digest(decoded) == pin, "Exact input " + name)
        source[name] = json.loads(decoded)
        manifest[name] = {"path": str(path), "sha256": digest(raw), "payload_sha256": pin}
    records = {(row["stage"], row["port"]): row for row in source["views"]["entries"]}
    need(len(source["views"]["entries"]) == 336 and
         set(records) == {(s, p) for s in range(3) for p in range(112)}, "All actual D25 routes")
    q = [records[0, p]["q"] for p in range(112)]
    need(len(set(q)) == 112 and all(0 < v < 512 for v in q), "Distinct nonzero root lines")
    need(q == source["unitary"]["ports"] and
         all(records[s, p]["q"] == q[p] for s in range(3) for p in range(112)),
         "Unitary code and every route use the same physical port order")
    rho = {key: tuple(row["route_columns"]) for key, row in records.items()}
    for p in range(112):
        need(rho[0, p] == UNITS, "Root-stage identity")
        for s in (1, 2):
            matrix = rho[s, p]
            need(all(act(matrix, matrix[j]) == UNITS[j] for j in range(25)), "Involution")
            need(all(dot(matrix[i], matrix[j]) == (i == j) for i in range(25) for j in range(25)),
                 "Orthogonal route and Fourier action convention")
            need(act(matrix, q[p]) == q[p], "Own line fixed")
        need(act(rho[1, p], E1) == OMEGA ^ q[p] and
             act(rho[2, p], E2) == OMEGA ^ q[p], "Fresh characteristic images")
        need(all(act(rho[1, p], v) == v for v in UNITS[17:25]) and
             all(act(rho[2, p], v) == v for v in UNITS[9:17]), "Other fresh block fixed pointwise")

    def tail(j, r, vector):
        return act(rho[2, j], act(rho[1, j], act(rho[1, r], vector)))

    def path(p, j, r, vector):
        return act(rho[2, p], tail(j, r, vector))

    def dual_path(p, j, r, vector):
        return act(rho[1, r], act(rho[1, j], act(rho[2, j], act(rho[2, p], vector))))

    by_line = {vector: p for p, vector in enumerate(q)}
    signatures, signature_rows = {}, []
    for j in range(112):
        for r in range(112):
            images = tail(j, r, E2), tail(j, r, E1)
            need(images not in signatures, "One two-column input separates every path")
            recovered_j = by_line[images[0] ^ OMEGA]
            recovered_r = by_line[OMEGA ^ act(rho[1, recovered_j], act(rho[2, recovered_j], images[1]))]
            need((recovered_j, recovered_r) == (j, r), "Both tags recover the path")
            signatures[images] = j, r
            signature_rows.append([j, r, *images])
    counts = Counter()
    for p in range(112):
        for j in range(112):
            image2, image1 = act(rho[2, j], q[p]), act(rho[1, j], q[p])
            need(bool(image2 & E2) == (p != j), "Final off-diagonal edge has a fresh2 line component")
            need(bool(image1 & E1) == (p != j), "Earlier off-diagonal edge has a fresh1 line component")
            counts["fresh2_line_tests"] += 1
            counts["fresh1_line_tests"] += 1
    c = sparse(source["unitary"]["code"])
    star = sparse(source["unitary"]["inverse_and_adjoint"])
    want_star = [{} for _ in range(112)]
    for p, row in enumerate(c):
        need(row and p not in row, "Actual forward code has a nonempty off-diagonal row")
        for j, coefficient in row.items():
            need(coefficient != ZERO, "Stored coefficient is nonzero")
            want_star[j][p] = coefficient[0], -coefficient[1]
    need(star == want_star, "Actual adjoint")
    identity = [{p: ONE} for p in range(112)]
    need(matmul(c, star) == matmul(star, c) == identity, "Both unitary orders")
    families = {"C": c, "Cstar": star}
    witnesses, profiles = [], {}
    for names in product(families, repeat=3):
        c0, c1, c2 = [families[name] for name in names]
        row_sizes = [sum(len(c0[r]) for j in c2[p] for r in c1[j]) for p in range(112)]
        need(min(row_sizes) > 1, "Actual path expansion has multiple terms in every row")
        profiles["/".join(names)] = {"total_terms": sum(row_sizes),
                                     "row_term_histogram": dict(sorted(Counter(row_sizes).items()))}
        for p in range(112):
            j = min(c2[p])
            r = min(c1[j])
            k = min(c0[r])
            need(j != p, "Actual final edge is off diagonal")
            coefficient = mul(c2[p][j], mul(c1[j][r], c0[r][k]))
            need(coefficient != ZERO, "Witness path coefficient")
            pulled_line = dual_path(p, j, r, q[p])
            need(pulled_line & E2 and pulled_line != q[k], "Witness path breaks the intrinsic line")
            prefix = [E2, E1]
            difference = sum(dot(q[p], path(p, j, r, x)) - dot(q[k], x) for x in prefix) % 4
            separating = pulled_line ^ q[k]
            extra = 0 if difference else separating & -separating
            columns = prefix + [extra]
            images = [path(p, j, r, x) for x in columns]
            left_power = sum(dot(q[p], x) for x in images) % 4
            right_power = sum(dot(q[k], x) for x in columns) % 4
            need(left_power != right_power, "Exact nonzero three-column commutator phase")
            recovered_signature = tuple(act(rho[2, p], x) for x in images[:2])
            need(signatures[recovered_signature] == (j, r), "No other path reaches the witness output")
            witnesses.append({"variant": list(names), "output_port": p, "input_port": k,
                              "intermediate_ports": [j, r], "coefficient": list(map(str, coefficient)),
                              "input_characters": columns, "output_characters": images,
                              "left_i_power": left_power, "right_i_power": right_power,
                              "pulled_output_line": pulled_line})
    need(len(witnesses) == 896, "One witness in every row of all eight actual variants")
    need(all(digest(Path(item["path"]).read_bytes()) == item["sha256"] for item in manifest.values()),
         "Inputs remain unchanged")
    pins = {"SOURCE-MANIFEST.json": write_json(args.out / "SOURCE-MANIFEST.json", manifest),
            "TWO-TAG-SIGNATURES.json": write_json(args.out / "TWO-TAG-SIGNATURES.json", signature_rows),
            "COMMUTATOR-WITNESSES.json": write_json(args.out / "COMMUTATOR-WITNESSES.json", witnesses)}
    result = {"status": "PASS_COMMON_INPUT_REPRESENTATION_REVIEW", "output_sha256": pins,
              "logical_path_separation_minimum_width": 2,
              "physical_affine_monomial_obstruction_minimum_width": 3,
              "commutator_witness_minimum_width": 3,
              "distinct_path_pairs": len(signatures), "line_tests": dict(counts),
              "actual_physical_port_order_checked": True,
              "actual_commutator_witnesses": len(witnesses), "actual_profiles": profiles,
              "physical_affine_translations_recomputed": False,
              "native_word_replayed": False, "width_one_or_two_commutator_claim": False,
              "general_decoder_lower_bound": False}
    write_json(args.out / "CHECKS.json", result)
    print(json.dumps({"status": result["status"], "paths": len(signatures),
                      "commutator_witnesses": len(witnesses)}, sort_keys=True))


if __name__ == "__main__":
    main()
