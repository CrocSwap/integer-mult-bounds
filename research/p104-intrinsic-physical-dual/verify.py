"""Exact endpoint bridge; no predecessor executable or compiler imports.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
N = 9
SIZE = 1 << N


def need(ok, label):
    if not ok:
        raise ValueError(label)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate():
    for entry in json.loads((P / "SOURCES.json").read_text())["files"]:
        if entry["usage"] == "input":
            raw = (ROOT / entry["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source SHA256")
            need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                 == entry["git_blob"], "source Git blob")
    pin = json.loads((P / "PREDECESSOR.json").read_text())
    raw = (P / pin["local_path"]).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "predecessor SHA256")
    need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
         == pin["git_blob"], "predecessor Git blob")


def parity(x):
    return x.bit_count() & 1


def mv(rows, x):
    return sum(parity(row & x) << i for i, row in enumerate(rows))


def transpose(rows):
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(N))


def inverse(rows):
    rows = [row | (1 << (N+i)) for i, row in enumerate(rows)]
    for j in range(N):
        pivot = next((i for i in range(j, N) if rows[i] >> j & 1), None)
        need(pivot is not None, "nonsingular binary matrix")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(N):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    return tuple(row >> N for row in rows)


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in tuple(result)}
    return result


def phase_at(quadratic, linear, x):
    return (sum(linear[i] for i in range(N) if x >> i & 1)
            + 2 * sum(parity((quadratic[i] >> (i+1)) & (x >> (i+1)))
                      for i in range(N) if x >> i & 1)) % 4


def rotate(z, exponent):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def times(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def conjugate(z):
    return z[0], -z[1]


def kernel(rank):
    """Numerators of F_rank, with denominator 2**rank."""
    result = []
    for mask in range(1 << rank):
        z = (1, 0)
        for i in range(rank):
            z = times(z, (1, -1 if mask >> i & 1 else 1))
        result.append(z)
    return result


def chart_table(frame):
    """Gamma_W = E F_rank E^-1, evaluated without a gate interpreter.

    Column x has outputs x xor M*mask with coefficient
    i**(d(output)-d(x)) * F_rank[mask]. Return conjugated kernels.
    """
    basis = list(frame)
    need(len(span(basis)) == 1 << len(basis), "independent chart basis")
    for e in (1 << i for i in range(N)):
        if e not in span(basis):
            basis.append(e)
    matrix = transpose(basis)
    columns = transpose(inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(columns))
                      for i, a in enumerate(columns))
    linear = tuple((row >> i) & 1 for i, row in enumerate(quadratic))
    phases = [phase_at(quadratic, linear, x) for x in range(SIZE)]
    return [(mv(matrix, mask), conjugate(z)) for mask, z in enumerate(kernel(len(frame)))], phases


def monomial_table(recipe):
    need(type(recipe["rank"]) is int and recipe["rank"] == 0 and recipe["right"] is None,
         "rank-zero endpoint recipe")
    m = recipe["left"]
    need(len(m["matrix_rows"]) == len(m["quadratic_rows"]) == len(m["linear_Z4"]) == N,
         "monomial dimension")
    need(tuple(m["quadratic_rows"]) == transpose(m["quadratic_rows"]), "quadratic symmetry")
    inverse(m["matrix_rows"])
    addresses = [mv(m["matrix_rows"], x) ^ m["offset"] for x in range(SIZE)]
    need(set(addresses) == set(range(SIZE)), "monomial permutation")
    phases = [(phase_at(m["quadratic_rows"], m["linear_Z4"], x) + m["phase"]) % 4
              for x in range(SIZE)]
    return addresses, phases


def derive(native):
    adapters = deepcopy(native["endpoint_adapters"])
    for entry in adapters:
        # Off-diagonal quadratic coefficients are 2 mod 4: self-conjugate.
        m = entry["recipe"]["left"]
        m["linear_Z4"] = [-a % 4 for a in m["linear_Z4"]]
        m["phase"] = -m["phase"] % 4
    return {"schema_version": 1, "chart": "ordinary physical inverse-transpose",
            "added_positive_profile": {}, "adapters": adapters}


def geometry(native, fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0]*8
            v[i], v[j] = 2, 2*sign
            roots.append(tuple(v))
    roots += [(1, *tail) for tail in product((-1, 1), repeat=7) if tail.count(-1) % 2 == 0]
    roots.sort()
    iso = native["label_isometry"]
    inner = lambda a, b: sum(x*y for x, y in zip(a, b)) // 4
    binary = [sum(((inner(a, b)+1) & 1) << j for j, b in enumerate(roots)) for a in roots]
    compressed = [sum(((x >> j) & 1) << k for k, j in enumerate(iso["pivot_root_indices"])) for x in binary]
    gram = [compressed[i] for i in iso["pivot_root_indices"]]
    need(gram == iso["compressed_gram"], "compressed Gram")
    dual = inverse(gram)
    need(list(dual) == iso["compressed_dual_gram"], "dual Gram")
    orth = iso["orthonormal_basis_compressed"]
    dot = lambda a, b: parity(a & mv(dual, b))
    need(len(orth) == N and all(dot(a, b) == int(i == j)
         for i, a in enumerate(orth) for j, b in enumerate(orth)), "isometry")
    cv = lambda x: sum(dot(x, v) << j for j, v in enumerate(orth))
    physical = list(map(cv, compressed))
    need(physical == iso["physical_root_labels"], "physical labels")
    need(all(parity(a & b) == ((binary[i] >> j) & 1)
         for i, a in enumerate(physical) for j, b in enumerate(physical)), "all 14400 pairings")
    removed = {tuple(x) for x in fixture["F0"] + fixture["C"]}
    ports = [q for r, q in zip(roots, physical) if r not in removed]
    need(len(ports) == 104 and all(parity(q) for q in ports), "104 odd ports")
    return ports, cv


def validate(certificate, native, fixture, witness, word):
    ports, cv = geometry(native, fixture)
    need(certificate["added_positive_profile"] == {}, "no added positive children")
    expected_keys = {("entry", "X"+str(i)) for i in range(104)} | {("exit", "Y"+str(i)) for i in range(104)}
    keys = [(e["position"], e["register"]) for e in certificate["adapters"]]
    need(len(keys) == 208 and set(keys) == expected_keys, "complete unique port coverage")
    initial, final = word["initial_frames"], word["final_frames"]
    need(len(initial) == len(final) == 358 and set(initial) == set(final), "358 public roles")
    for r in initial:
        if r.startswith("X"):
            need(initial[r] == [ports[int(r[1:])]] and len(span(final[r])) == SIZE, "canonical X boundary")
        elif r.startswith("Y"):
            need(initial[r] == [] and span(final[r]) == {x for x in range(SIZE) if not parity(x & ports[int(r[1:])])}, "canonical Y boundary")
        else:
            need(initial[r] == [] and len(span(final[r])) == SIZE, "identity helper adapters")
    f9 = kernel(N)
    columns = 0
    for entry in certificate["adapters"]:
        r, position, q = entry["register"], entry["position"], entry["normal"]
        need(q == ports[int(r[1:])], "port normal")
        frame = entry["frame"]
        pinned_frame = witness["initial_frames" if position == "entry" else "final_frames"][r]
        need(span(frame) == span(map(cv, pinned_frame)), "original canonical frame")
        need(frame == (initial[r] if position == "entry" else final[r]), "dual canonical frame")
        addresses, phases = monomial_table(entry["recipe"])
        shifts, d = chart_table(frame)
        if position == "entry":
            # J_i conjugate(C_q) = conjugate(Gamma_line).
            for x in range(SIZE):
                actual = {addresses[y]: rotate(z, phases[y])
                          for y, z in ((x, (1, -1)), (x ^ q, (1, 1)))}
                expected = {x ^ shift: rotate(z, d[x]-d[x ^ shift]) for shift, z in shifts}
                need(actual == expected, "intrinsic entry column")
                columns += 1
        else:
            # J_f conjugate(Gamma_hyperplane) = conjugate(F9 C_q^-1).
            target_kernel = []
            for z in range(SIZE):
                a, b = times((1, -1), f9[z]), times((1, 1), f9[z ^ q])
                target_kernel.append(conjugate((a[0]+b[0], a[1]+b[1])))
            need(sum(z != (0, 0) for z in target_kernel) == 256, "intrinsic exit support")
            for x in range(SIZE):
                actual = {}
                for shift, z in shifts:
                    y = x ^ shift
                    value = rotate(z, d[x]-d[y]+phases[y])
                    actual[addresses[y]] = (4*value[0], 4*value[1])
                expected = {x ^ z: value for z, value in enumerate(target_kernel) if value != (0, 0)}
                need(actual == expected, "intrinsic exit column")
                columns += 1
    profile = Counter(e[4] for e in word["program"] if e[0] == "transport")
    need(dict(sorted(profile.items())) == {1:1632, 2:74, 3:86, 4:104, 5:48, 6:42, 7:76, 8:8}, "pinned middle transport inventory")
    return {"status": "PASS_P104_INTRINSIC_PHYSICAL_DUAL_BRIDGE", "adapters": 208,
            "basis_columns": columns, "address_dimension": SIZE, "public_roles": 358,
            "helper_roles_with_identity_adapters": 150, "added_positive_profile": {},
            "retained_positive_profile": dict(sorted(profile.items())),
            "retained_rank_mass": sum(k*v for k, v in profile.items()),
            "retained_events": len(word["program"]), "wrapped_events": len(word["program"])+208,
            "scope": "Exact intrinsic boundary bridge; interior correctness, native middle recipes, hosting and supplier admission are not recertified."}


def controls(certificate, native, fixture, witness, word):
    faults = {}
    a = deepcopy(certificate)
    a["adapters"].pop()
    faults["missing_port"] = a, "complete unique port coverage"
    a = deepcopy(certificate)
    a["adapters"][0]["recipe"]["left"]["phase"] ^= 1
    faults["global_phase"] = a, "intrinsic entry column"
    a = deepcopy(certificate)
    a["adapters"][0]["normal"] ^= 1
    faults["wrong_normal"] = a, "port normal"
    a = deepcopy(certificate)
    a["adapters"][0]["recipe"]["rank"] = 1
    faults["positive_child"] = a, "rank-zero endpoint recipe"
    a = deepcopy(certificate)
    a["adapters"] = deepcopy(native["endpoint_adapters"])
    faults["unconjugated_forward_adapters"] = a, "intrinsic entry column"
    a = deepcopy(certificate)
    for e in a["adapters"]:
        if e["position"] == "exit":
            e["recipe"]["left"]["offset"] ^= 1
            break
    faults["wrong_exit_address"] = a, "intrinsic exit column"
    for name, (fault, expected_label) in faults.items():
        try:
            validate(fault, native, fixture, witness, word)
        except ValueError as error:
            need(str(error) == expected_label, "control rejected for wrong reason: " + name)
            continue
        raise ValueError("control accepted: " + name)
    return sorted(faults)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write derived adapter certificate to a new file")
    args = parser.parse_args()
    authenticate()
    base = ROOT / "research/p104-native-channel"
    native = json.loads(gzip.decompress((base / "NATIVE-RECIPES.json.gz").read_bytes()))
    fixture = json.loads((base / "inputs/P104-FIXTURE.json").read_text())["section4_explicit_P104"]
    witness = json.loads((base / "inputs/LOWRANK-WITNESS.json").read_text())
    word = json.loads((P / "inputs/PR2586-WORD.json").read_text())
    derived = derive(native)
    if args.emit:
        result = validate(derived, native, fixture, witness, word)
        with args.emit.open("x") as handle:
            json.dump(derived, handle, sort_keys=True, indent=2)
            handle.write("\n")
    else:
        saved = json.loads((P / "ADAPTERS.json").read_text())
        need(canonical_json(saved) == canonical_json(derived), "complete regenerated adapter payload")
        result = validate(saved, native, fixture, witness, word)
        result["rejecting_controls"] = controls(saved, native, fixture, witness, word)
        expected = json.loads((P / "RESULT.json").read_text())
        need(canonical_json(result) == canonical_json(expected), "complete saved receipt")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
