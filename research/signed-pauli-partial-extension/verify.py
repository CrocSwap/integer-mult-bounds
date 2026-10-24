"""Literal finite-Pauli oracle, partial counts and actual compiler binding."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from pauli import complete, need, apply_word


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_pauli(n, p):
    x, z, phase = p
    return tuple((j ^ x, (phase + 2 * ((j & z).bit_count() % 2)) % 4)
                 for j in range(1 << n))


def product(a, b):
    return tuple((a[k][0], (phase + a[k][1]) % 4) for k, phase in b)


def as_pauli(matrix, n):
    x, phase = matrix[0]
    z = sum((((matrix[1 << j][1] - phase) % 4) // 2) << j for j in range(n))
    p = x, z, phase
    need(literal_pauli(n, p) == matrix, "literal Pauli reconstruction")
    return p


def signed_group(n):
    """Closure using literal monomial products, not the implementation formula."""
    mask = (1 << n) - 1
    ps = [(x, z, ((x & z).bit_count() + 2 * sign) % 4)
          for x in range(1 << n) for z in range(1 << n) for sign in range(2)]
    transitions, actions = [], {}
    for axis in range(1, 1 << (2 * n)):
        x, z = axis & mask, axis >> n
        h = literal_pauli(n, (x, z, (x & z).bit_count() % 4))
        table = {}
        for p in ps:
            matrix = literal_pauli(n, p)
            hp, ph = product(h, matrix), product(matrix, h)
            image = matrix if hp == ph else tuple((k, (phase - 1) % 4) for k, phase in hp)
            table[p] = as_pauli(image, n)
        transitions.append(table)
        actions[("turn", x, z, 1)] = table
    for typ in ("x", "s"):
        for mask in range(1 << n):
            gate = (typ, mask) if typ == "x" else (typ, mask, 2)
            k = literal_pauli(n, (mask, 0, 0) if typ == "x" else (0, mask, 0))
            actions[gate] = {p: as_pauli(product(product(k, literal_pauli(n, p)), k), n)
                             for p in ps}
    identity = tuple([(1 << j, 0, 0) for j in range(n)] +
                     [(0, 1 << j, 0) for j in range(n)])
    seen, queue = {identity}, [identity]
    for tableau in queue:
        for action in transitions:
            target = tuple(action[p] for p in tableau)
            if target not in seen:
                seen.add(target)
                queue.append(target)
    need(len(seen) == {1: 24, 2: 11520}[n], "literal full signed group")
    return identity, seen, actions


def finite_counts(n):
    identity, group, actions = signed_group(n)
    shapes = [[], [0], [0, 1]] if n == 1 else [[], [0], [0, 1],
              [0, 2], [0, 2, 1], [0, 1, 2, 3]]
    reports, compiler_cases = [], []
    for indices in shapes:
        counts = Counter(tuple(tableau[i] for i in indices) for tableau in group)
        transcript = hashlib.sha256()
        longest = 0
        for targets, count in sorted(counts.items()):
            constraints = list(zip([identity[i] for i in indices], targets))
            result = complete(n, constraints)
            need(result["count"] == count, "independent full-group restriction count")
            need(tuple(result["tableau"]) in group, "constructed signed tableau outside group")
            literal = identity
            for gate in result["gates"]:
                literal = tuple(actions[tuple(gate)][p] for p in literal)
            need(literal == tuple(result["tableau"]), "independent literal emitted word")
            need(tuple(literal[i] for i in indices) == targets, "independent partial images")
            need(len(result["gates"]) <= 2 * len(indices) + 2, "gate upper bound")
            longest = max(longest, len(result["gates"]))
            transcript.update(encoded([targets, count, result["tableau"]]).encode())
        chosen = sorted(counts)[len(counts) // 3]
        result = complete(n, list(zip([identity[i] for i in indices], chosen)))
        compiler_cases.append((n, result["gates"], result["tableau"]))
        reports.append({"indices": indices, "restrictions": len(counts),
                        "literal_word_checks": len(counts),
                        "group_order": len(group), "maximum_literal_gates": longest,
                        "sha256": transcript.hexdigest()})
    return {"n": n, "projective_group": len(group), "types": reports}, compiler_cases


def controls():
    x, z, y = (1, 0, 0), (0, 1, 0), (1, 1, 1)
    bad = [
        (1, [(x, x), (z, z), (y, (1, 1, 3))], "central-relations"),
        (1, [(x, x), (x, z)], "label-relations"),
        (1, [(x, x), (z, x)], "label-relations"),
        (2, [(x, x), (z, (2, 0, 0))], "commutators"),
        (1, [((0, 0, 0), (0, 0, 2))], "central-relations"),
    ]
    for n, pairs, reason in bad:
        result = complete(n, pairs)
        need(result["count"] == 0 and result["reason"] == reason, "semantic rejection")
    need(complete(1, [(x, x)])["count"] == 4, "one fixed generator")
    need(complete(1, [(x, x), (z, z)])["count"] == 1, "full signed tableau")
    need(complete(0, [((0, 0, 2), (0, 0, 2))])["count"] == 1, "zero dimension")
    malformed = [(True, []), (10, []), (1, [((True, 0, 0), x)]),
                 (1, [((1, 1, 0), y)]), (1, [((2, 0, 0), x)])]
    for n, pairs in malformed:
        try:
            complete(n, pairs)
        except ValueError:
            continue
        raise ValueError("malformed contract accepted")
    return {"semantic_rejections": len(bad), "malformed_rejections": len(malformed),
            "one_fixed_generator_count": 4, "full_signed_tableau_count": 1,
            "zero_dimensional_count": 1}


def source_bindings(cases):
    source_path = ROOT / "research/native-clifford-gauge-compiler/compiler/clifford_compile.py"
    # run_path reads the authenticated source directly, without an imported pyc.
    source = runpy.run_path(str(source_path), run_name="pinned_native_source")
    records = []
    for n, word, expected in cases:
        need(source["tableau"](n, word) == expected, "actual source signed tableau")
        certificate = source["compile_word"](n, word)
        columns = source["replay"](n, word, certificate, full_columns=n <= 3)
        need(0 <= certificate["paid_rank"] <= n, "source rank-d bound")
        records.append({"n": n, "word": word, "paid_rank": certificate["paid_rank"],
                        "source_replay_columns": columns})
    return source, records


def larger_and_phase_cases():
    cases = []
    for n in (3, 9):
        mask = (1 << n) - 1
        word = [["turn", (7 * j + 3) & mask, (11 * j + 5) & mask,
                 1 if j % 2 else -1] for j in range(12)]
        ps = [(1 << j, 0, 0) for j in range(min(3, n))]
        ps += [(0, 1, 0), (3, 0, 0), (1, 1, 1)]
        constraints = [(p, apply_word(p, word)) for p in ps]
        result = complete(n, constraints)
        need(result["count"] > 0, "larger literal source contract")
        cases.append((n, result["gates"], result["tableau"]))
    return cases


def phase_and_tensor(source):
    negative = [["turn", 1, 0, 1], ["turn", 1, 0, 1],
                ["turn", 0, 1, 1], ["turn", 0, 1, 1]] * 2
    actual = source["compile_word"](1, negative)
    source["replay"](1, negative, actual)
    need(actual["paid_rank"] == 0 and actual["G_global_i"] == 2, "negative identity anchor")
    x, z = (1, 0, 0), (0, 1, 0)
    chosen = complete(1, [(x, x), (z, z)])
    need(chosen["gates"] == [] and source["state"](1, negative) !=
         source["state"](1, chosen["gates"]), "projective is not absolute target equality")
    for f in (2, 3):
        lifted = source["lift_word"](1, [["phase", 1]], f)
        need(lifted == [["phase", f]], "literal phase tensorization")
        certificate = source["compile_word"](f, lifted)
        source["replay"](f, lifted, certificate)
        need(certificate["G_global_i"] == f % 4, "tensor absolute phase")
        need(source["state"](f, lifted) != source["state"](f, [["phase", 1]]),
             "dropped tensor phase must be detected")
    return {"identity_tableau_negative_anchor_rejected": True,
            "literal_global_phase_tensor_widths": [2, 3]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "occupied receipt output")
    pins = json.loads((HERE / "SOURCES.json").read_text())
    live = {}
    for item in pins["files"]:
        if item["usage"] == "input":
            digest = sha(ROOT / item["path"])
            need(digest == item["sha256"], "source authentication: " + item["path"])
            live[item["path"]] = digest
    reports, cases = [], []
    for n in (1, 2):
        report, selected = finite_counts(n)
        reports.append(report)
        cases.extend(selected)
    cases.extend(larger_and_phase_cases())
    source, bindings = source_bindings(cases)
    result = {"schema_version": 1, "finite_domains": reports, "controls": controls(),
              "actual_compiler": bindings, "absolute_phase": phase_and_tensor(source),
              "sources": live, "local_sha256": {p.name: sha(p) for p in sorted(HERE.iterdir())
                 if p.is_file() and p.name != "RESULT.json"},
              "new_kappa": False, "complete_supplier": False,
              "count_contract": "projective Clifford; literal representative chooses its own phase"}
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(encoded(json.loads((HERE / "RESULT.json").read_text())) == encoded(result),
             "type-sensitive receipt mismatch")
    print("PASS_SIGNED_PAULI_PARTIAL_EXTENSION " + encoded({
        "restrictions": sum(t["restrictions"] for r in reports for t in r["types"]),
        "actual_compiler_cases": len(bindings)}))


if __name__ == "__main__":
    main()
