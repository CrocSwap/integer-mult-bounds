#!/usr/bin/env python3
"""Exact source-bound evidence for the QQ16 first-forward logger obstruction.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. The universal claim is proved in README.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBERS = {
    "slots/local/CANONICAL-WORD.json.gz":
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "slots/local/LOCAL-PROGRAMS.json.gz":
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "t16/global/base/work/complex-nine-native/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = [p for p in range(112) if p not in A + T]
ID = tuple(1 << i for i in range(17))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def authenticate(root):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    data = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue
        raw = (root / entry["path"]).read_bytes()
        need(sha256(raw).hexdigest() == entry["sha256"],
             "Source pin differs: " + entry["path"])
        data[entry["path"]] = raw
    return data


def archive_data(raw):
    result = {}
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        for path, pin in MEMBERS.items():
            entries = [e for e in archive.getmembers() if e.name == path]
            need(len(entries) == 1 and entries[0].isfile(), "Unique regular archive member")
            body = archive.extractfile(entries[0]).read()
            need(sha256(body).hexdigest() == pin, "Archive member pin: " + path)
            result[path.rsplit("/", 1)[1]] = json.loads(
                gzip.decompress(body) if path.endswith(".gz") else body)
    return result


def query_columns(local):
    word = local["CANONICAL-WORD.json.gz"]
    need((word["v"], word["R"], word["h"]) == (112, 480, 9), "Selected dimensions")
    # Propagate only derivatives with respect to X. Helpers/Y are independent
    # columns with zero X derivative, not assumed initialized in the theorem.
    rows = [{i: Q(1)} if i < 112 else {} for i in range(712)]
    operations = 0
    for event in local["LOCAL-PROGRAMS.json.gz"]["forward"]:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        gate = event[1]
        reg = lambda token: token[1] + (704 if token[0] == "C" else 0)
        target = reg(gate[1])
        op = gate[0]
        operations += 1
        if op == "clear":
            rows[target] = {}
        elif op == "copy":
            rows[target] = rows[reg(gate[2])].copy()
        elif op == "scale":
            rows[target] = {j: v * Q(gate[2], gate[3]) for j, v in rows[target].items()}
        else:
            need(op == "add", "Known scalar prefix operation")
            for j, v in rows[reg(gate[2])].items():
                value = rows[target].get(j, 0) + Q(gate[3], gate[4]) * v
                if value:
                    rows[target][j] = value
                else:
                    rows[target].pop(j, None)
    else:
        raise ValueError("Missing centre cut")
    R = [[rows[c].get(p, Q(0)) for p in range(112)] for c in word["centers"]]
    need(len(R) == 8 and all(v.denominator == 1 for row in R for v in row), "Integer R")
    columns = [tuple(int(R[k][p]) for k in range(8)) for p in range(112)]
    check_grams(columns)
    return columns, operations


def gram(columns):
    return [[sum(v[i] * v[j] for v in columns) for j in range(8)] for i in range(8)]


def diagonal(value):
    return [[value * int(i == j) for j in range(8)] for i in range(8)]


def check_grams(columns):
    need(len(columns) == 112 and all(sum(v*v for v in c) == 4 for c in columns), "Norm-four ports")
    need(gram(columns) == diagonal(56), "Full Gram 56I")
    need(gram([columns[p] for p in A]) == diagonal(4), "A dyadic section")
    need(gram([columns[p] for p in T]) == diagonal(4), "T dyadic section")
    need(gram([columns[p] for p in U]) == diagonal(48), "Ordinary Gram 48I")


def act(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length() - 1]
        value ^= low
    return result


@lru_cache(maxsize=30000)
def multiply(left, right):
    return tuple(act(left, column) for column in right)


def routes(local):
    phases = local["DATA-PHASES.json"]
    word = local["CANONICAL-WORD.json.gz"]
    need(phases["m"] == 73 and len(phases["recipes"]) == 112, "Actual phase dimensions")
    result = []
    for p, recipe in enumerate(phases["recipes"]):
        basis = [recipe["q"]] + recipe["idle_children"][0]["orthogonal_axes"][:8]
        need(recipe["port"] == p and basis[0] == word["ports"][p], "Port source binding")
        need(all(0 < vector < 512 for vector in basis), "Local basis stays in nine coordinates")
        need(all(((basis[i] & basis[j]).bit_count() % 2) == int(i == j)
                 for i in range(9) for j in range(9)), "Orthonormal local basis")
        # Swap each local basis vector with its stage-one external axis.
        # All remaining 56 coordinates are fixed, so this is the full map's
        # faithful 17-coordinate restriction, not a quotient representation.
        columns = []
        for axis in ID:
            value = axis
            for i, vector in enumerate(basis[1:]):
                external = 1 << (9 + i)
                if ((axis & vector).bit_count() + bool(axis & external)) % 2:
                    value ^= vector ^ external
            columns.append(value)
        route = tuple(columns)
        need(multiply(route, route) == ID, "Actual route involution")
        need(act(route, recipe["q"]) == recipe["q"], "Route fixes port normal")
        need(all(act(route, basis[i + 1]) == 1 << (9 + i) for i in range(8)), "Exact stage-one exchange")
        result.append(route)
    need(len({result[p] for p in U}) == 96, "All ordinary stage-one routes distinct")
    return result


def add_vector(table, key, values, scale=1):
    row = table.setdefault(key, [0] * len(values))
    for i, value in enumerate(values):
        row[i] += scale * value


def clean(table):
    return {key: tuple(value) for key, value in table.items() if any(value)}


def witness(columns, route, coefficient=48, omit_projection=False):
    # All eight e_k columns at once. Coefficients live in the actual finite
    # matrix-group algebra; no enumeration of the enormous regular cover.
    result = []
    for p in U:
        row = {}
        add_vector(row, ID, columns[p], coefficient)
        if not omit_projection:
            for q in U:
                dot = sum(a*b for a, b in zip(columns[p], columns[q]))
                if dot:
                    add_vector(row, multiply(route[p], route[q]), columns[q], -dot)
        result.append(clean(row))
    return result


def apply_query(h, columns, route=None):
    out = {}
    for p, field in zip(U, h):
        for owner, row in field.items():
            label = multiply(route[p], owner) if route is not None else owner
            values = [columns[p][i] * row[k] for i in range(8) for k in range(8)]
            add_vector(out, label, values)
    return clean(out)


def rejected(action):
    try:
        action()
    except ValueError:
        return True
    return False


def finite_loggers():
    """Every scalar A logger over F5 with two ordinary inputs: 500 cases."""
    prime, count, inverse_columns = 5, 0, 0
    for m in range(prime):
        for n in range(prime):
            if m == n:
                continue
            for l0 in range(prime):
                for l1 in range(prime):
                    def source(x, inverse=False):
                        z0, z1, a, c = x
                        if not inverse:
                            f = z0 + a + c
                            return [(z0 - 12*f) % prime, z1,
                                    (m*a + n*c + l0*z0 + l1*z1) % prime, f % prime]
                        w0, w1, d, f = x
                        z0, z1 = (w0 + 12*f) % prime, w1
                        total = f - z0
                        c = ((d - m*total - l0*z0 - l1*z1) * pow(n-m, -1, prime)) % prime
                        return [z0, z1, (total-c) % prime, c]

                    def pair(state, inverse=False):
                        x, y = state[:4], state[4:]
                        output = source(x, inverse)
                        if inverse:
                            target = [(y[0]-x[0]) % prime, (y[1]-x[1]) % prime,
                                      (x[2]+y[2]-output[2]) % prime, (x[3]+y[3]-output[3]) % prime]
                        else:
                            target = [(y[0]+output[0]) % prime, (y[1]+output[1]) % prime,
                                      (x[2]+y[2]-output[2]) % prime, (x[3]+y[3]-output[3]) % prime]
                        return output + target

                    for j in range(8):
                        basis = [int(i == j) for i in range(8)]
                        need(pair(pair(basis), True) == basis, "F5 left inverse on dirty data")
                        need(pair(pair(basis, True)) == basis, "F5 right inverse on dirty data")
                        inverse_columns += 2
                    # B0=[1,0], B1=[0,1], B2=[1,1], h=(1,0).
                    post = [1, 0, 1, 0, 1, 0, -1 % prime, 0]
                    original = pair(post, True)
                    need(pair(original) == post, "Changed first logger pullback")
                    need((original[2]+original[3]) % prime == -1 % prime, "Required initial A+T nonzero")
                    need(original[4:6] == [0, 0], "Initial ordinary Y zero")
                    # Fixed conserved B1, future logger E2, all selected sections
                    # identity in this toy model. This is not a native fixture.
                    x, y = post[:4], post[4:]
                    q2 = sum(y) % prime
                    b1 = (y[1] + q2 + y[3]) % prime
                    driver = x[3]
                    yp = [y[0], (y[1]+12*driver) % prime, q2,
                          (y[3]-b1-11*driver) % prime]
                    xp = [(x[0]-y[0]) % prime, (x[1]-y[1]) % prime,
                          (x[2]+y[2]-yp[2]) % prime, (x[3]+y[3]-yp[3]) % prime]
                    need(xp+yp == [0, 0, 0, 0, 1, 0, 0, 0], "Fixed B1 erases every changed logger witness")
                    count += 1
    need(count == 500, "Complete F5 logger domain")
    return {"field": 5, "loggers": count, "two_sided_dirty_basis_checks": inverse_columns,
            "changed_logger_witnesses": count}


def matvec(matrix, vector):
    return [sum((a*b for a, b in zip(row, vector)), Q(0)) for row in matrix]


def plus(*vectors):
    return [sum(values, Q(0)) for values in zip(*vectors)]


def negative(vector):
    return [-v for v in vector]


def ordered_fixture():
    # M,N do not commute. D=N-M has a two-sided rational inverse.
    M = [[Q(1), Q(1)], [Q(0), Q(1)]]
    N = [[Q(2), Q(1)], [Q(1), Q(3)]]
    Dinv = [[Q(1), Q(0)], [Q(-1, 2), Q(1, 2)]]
    L = [[Q(1), Q(2), Q(0), Q(-1)], [Q(0), Q(1), Q(3), Q(2)]]
    need(matvec(M, matvec(N, [1, 0])) != matvec(N, matvec(M, [1, 0])), "Noncommuting fixture")

    def source(x, inverse=False):
        z, a, c = x[:4], x[4:6], x[6:]
        if not inverse:
            f = plus(z[:2], a, c)
            w = plus(z, [-12*f[0], -12*f[1], 0, 0])
            d = plus(matvec(M, a), matvec(N, c), matvec(L, z))
            return w+d+f
        w, d, f = z, a, c
        z = plus(w, [12*f[0], 12*f[1], 0, 0])
        total = plus(f, negative(z[:2]))
        c = matvec(Dinv, plus(d, negative(matvec(M, total)), negative(matvec(L, z))))
        return z+plus(total, negative(c))+c

    for j in range(8):
        e = [Q(int(i == j)) for i in range(8)]
        need(source(source(e), True) == e, "Ordered logger left inverse")
        need(source(source(e, True)) == e, "Ordered logger right inverse")
    for k in range(2):
        h = [Q(int(i == k)) for i in range(4)]
        post = h+h[:2]+[Q(0), Q(0)]
        old = source(post, True)
        need(source(old) == post, "Noncommuting pullback")
        need(plus(old[4:6], old[6:]) == negative(h[:2]), "Noncommuting initial selected sum")
    return {"centre_dimension": 2, "ordinary_dimension": 4,
            "noncommuting_M_N": True, "two_sided_source_basis_checks": 16,
            "witnesses": 2}


def tail_receipt(data):
    source = json.loads(data["research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"])
    review = json.loads(data["research/joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.json"])
    # Replay only the restricted ordinary h-coefficient trajectory stated by
    # the pinned witness, not the absent full controller or native bank program.
    def run(omit_first_negative=False):
        x, y, trace = [0]*4, [1, 0, 0, 0], []
        for event in source["trajectory_after_B1"]:
            kind = event["kind"]
            if kind == "bridge":
                d, s, c = event["dst"], event["src"], event["coefficient"]
                if not (omit_first_negative and d == 0 and s == 1 and c == -1):
                    x[d] += c*x[s]
                    y[s] -= c*y[d]
            elif kind == "local":
                stage = event["stage"]
                if stage % 2 == 0:
                    need(not any(x), "Later F query source zero")
                else:
                    need(y[stage//2] == 0, "Later B source zero")
            else:
                need(kind == "terminal", "Known tail event")
                x, y = y, [-v for v in x]
            combined = [v for pair in zip(x, y) for v in pair]
            need(combined == event["ordinary"], "Inherited trajectory agreement")
            trace.append({"kind": kind, "x_coefficients": x[:], "y_coefficients": y[:]})
        return trace
    trace = run()
    need(trace == review["tail_trace"], "Independent receipt agreement")
    need(rejected(lambda: run(True)), "Missing cancelling bridge rejected")
    return {"events": len(trace), "forward_queries_zero": [0, 2, 4, 6, 8],
            "final_X_coefficients": trace[-1]["x_coefficients"],
            "final_Y_coefficients": trace[-1]["y_coefficients"],
            "scope": "Restricted inherited h trajectory; not a full controller/native replay"}


def verify(root):
    data = authenticate(root)
    local = archive_data(data[ARCHIVE])
    columns, scalar_prefix = query_columns(local)
    route = routes(local)
    h = witness(columns, route)
    b1 = apply_query(h, columns, route)
    b0 = apply_query(h, columns)
    need(not b1, "Full group-ring B1 h vanishes")
    need(b0[ID] == tuple(v for row in diagonal(2112) for v in row), "Full identity coefficient 2112I")
    serialized = [[[list(g), list(v)] for g, v in sorted(field.items())] for field in h]
    controls = {}
    controls["omitted_projector_term"] = bool(apply_query(witness(columns, route, omit_projection=True), columns, route))
    controls["wrong_gram_coefficient"] = bool(apply_query(witness(columns, route, coefficient=47), columns, route))
    collapsed = [ID]*112
    controls["collapsed_routes_zero_witness"] = not any(witness(columns, collapsed))
    changed = columns[:]
    changed[U[0]] = tuple(v + int(i == 0) for i, v in enumerate(changed[U[0]]))
    controls["corrupted_query_gram"] = rejected(lambda: check_grams(changed))
    controls["extra_B0_observation_detects_witness"] = bool(b0)
    need(all(controls.values()), "Every semantic control must discriminate")
    invoice = json.loads(data["research/joint-query/evidence/CONSERVED-QQ16.json"])
    local_bill = {"native_mass": sum(invoice["invoices"][key]["native_mass"] for key in ("F", "B")),
                  "real_scalar_bound": sum(invoice["invoices"][key]["complete_scalar"]["real_primitives"] for key in ("F", "B")),
                  "added_cover_maps": invoice["native_cases"]["B_1_2"]["explicit_cover_maps"] + invoice["native_cases"]["F_0"]["explicit_cover_maps"],
                  "wrapper_maps": invoice["native_cases"]["B_1_2"]["native_wrapper_maps"] + invoice["native_cases"]["F_0"]["native_wrapper_maps"]}
    need(local_bill == {"native_mass": 11076, "real_scalar_bound": 426196,
                        "added_cover_maps": 528, "wrapper_maps": 64}, "Retained pair invoice")
    return {"status": "PASS_QQ16_FORWARD_LOGGER_OBSTRUCTION",
            "query": {"source_scalar_prefix_operations": scalar_prefix,
                      "columns": 112, "ordinary_columns": 96, "gram": 48,
                      "query_columns_sha256": digest(columns), "stage_one_routes_sha256": digest(route),
                      "distinct_ordinary_routes": len({route[p] for p in U})},
            "witness": {"definition": "(48I-B1*B1)B0*e_k", "independent_directions": 8,
                        "ordinary_field_group_terms": sum(map(len, h)),
                        "canonical_group_ring_sha256": digest(serialized),
                        "B1_h_nonzero_terms": len(b1), "B0_h_group_terms": len(b0),
                        "B0_h_identity_coefficient": diagonal(2112)},
            "finite_logger_fixture": finite_loggers(), "ordered_fixture": ordered_fixture(),
            "tail": tail_receipt(data), "semantic_controls": controls,
            "retained_pair_bill": local_bill,
            "result": "Every invertible source F0 logger with fixed U/T outputs and conserved selected pair sums fails selected restoration under fixed B1 and the retained observation/tail contract, even with zero added logger cost.",
            "limits": ["No arbitrary-first-pair obstruction", "No lower bound on paid ordinary reads",
                       "No native logger synthesis or supplier admission", "No new kappa or formal-kernel proof"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--emit", type=Path, help="Write a fresh result; refuses existing paths")
    args = parser.parse_args()
    result = verify(args.repo.resolve())
    if args.emit:
        with args.emit.open("x") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        need(canonical(result) == canonical(json.loads((PACKAGE / "RESULT.json").read_text())), "Complete canonical RESULT mismatch")
    print(result["status"])
    print("96 distinct routes; 8 B0/B1 witnesses; 500 changed loggers; no new kappa")


if __name__ == "__main__":
    main()
