"""Read-only exact check; unchanged native recipes remain inherited, not replayed."""
from pathlib import Path
import argparse
import copy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def native_check(certificate, N, columns=True):
    records = certificate["transports"]
    M.need(len(records) == 2, "native coverage")
    checked = 0
    for record, (role, old, new, rank) in zip(records, M.EDGES):
        M.need((record["role"], tuple(record["old"]), tuple(record["new"])) ==
               (role, old, new), "native occurrence binding")
        recipe = record["recipe"]
        M.need(type(recipe["rank"]) is int and recipe["rank"] == rank, "native child rank")
        direct = M.conjugate(N.adjoint(N.frame(old, 9)) + N.frame(new, 9))
        via_common = M.conjugate(N.adjoint(N.frame(old, 9)) + N.frame(M.COMMON, 9)
                                + N.adjoint(N.frame(M.COMMON, 9)) + N.frame(new, 9))
        actual = N.recipe(recipe)
        N.equal(actual, direct, "new native recipe")
        N.equal(actual, via_common, "two predecessor edges")
        if columns:
            for basis in range(512):
                M.need(N.state(actual, basis) == N.state(direct, basis), "physical column")
                checked += 1
    return dict(recipes=2, signed_pauli_and_phase_equalities=4, exact_basis_columns=checked)


def reject(name, action, fragment):
    try:
        action()
    except (ValueError, AssertionError) as error:
        M.need(fragment in str(error), name + " rejected for unexpected reason: " + str(error))
        return name
    raise ValueError("fault accepted: " + name)


def controls(source, candidate, native, N):
    results = []
    wrong = copy.deepcopy(candidate)
    add = next(e for e in wrong["program"] if e[:4] == ["add", "X90", "N90", "1/2"])
    add[4] = list(M.COMMON)
    results.append(reject("old ADD chart", lambda: M.replay(wrong), "ADD common frame"))
    wrong = copy.deepcopy(candidate)
    index = next(i for i,e in enumerate(wrong["program"])
                 if e == ["transport", "N90", [391], list(M.FULL), 8])
    wrong["program"][index][3:] = [list(M.COMMON), 7]
    results.append(reject("only one operand moved", lambda: M.replay(wrong), "ADD common frame"))
    wrong = copy.deepcopy(candidate)
    next(e for e in wrong["program"] if e[0] == "sign" and e[1] == "X90" and e[3] == list(M.FULL))[3] = list(M.COMMON)
    results.append(reject("stale sign chart", lambda: M.replay(wrong), "sign frame"))
    wrong = copy.deepcopy(candidate)
    next(e for e in wrong["program"] if e[:4] == ["add", "X90", "N90", "1/2"])[3] = "-1/2"
    results.append(reject("wrong ADD coefficient", lambda: M.replay(wrong), "all-input endpoint"))
    wrong = copy.deepcopy(candidate)
    del wrong["program"][next(i for i,e in enumerate(wrong["program"]) if e[0] == "add" and e[1] == "C")]
    results.append(reject("private cleanup omitted", lambda: M.replay(wrong), "exact private zero erasure"))
    wrong = copy.deepcopy(source)
    wrong["program"][4000] = ["add", "X90", "N90", "1", list(M.COMMON)]
    results.append(reject("new source dependency", lambda: M.rewrite(wrong), "retiming dependency window"))
    wrong = copy.deepcopy(native)
    wrong["transports"][0]["recipe"]["left"]["phase"] ^= 2
    results.append(reject("native phase", lambda: native_check(wrong, N, False), "exact global phase"))
    wrong = copy.deepcopy(native)
    wrong["transports"][1]["recipe"]["rank"] = 7
    results.append(reject("unpaid compensation rank", lambda: native_check(wrong, N, False), "native child rank"))
    return results


def compute():
    M.authenticate()
    source = M.read(M.P/"inputs/PR2662-WORD.json")
    candidate = M.read(M.P/"WORD.json")
    M.need(M.encoded(M.rewrite(source)) == M.encoded(candidate), "literal candidate reconstruction")
    original, result = M.replay(source), M.replay(candidate)
    inherited = M.read(M.P/"inputs/PR2662-RESULT.json")["candidate"]
    for key in ("events", "counts", "profile", "rank_mass", "boundary_coefficients"):
        M.need(M.encoded(original[key]) == M.encoded(inherited[key]), "source invoice: " + key)
    M.need(original["endpoint_sha256"] == result["endpoint_sha256"], "unchanged complete logical map")
    M.need(result["rank_mass"] == original["rank_mass"] == 3542, "rank mass")
    M.need((result["events"], result["counts"]["transport"], result["zero_erasures"])
           == (5268, 1940, 8), "complete candidate invoice")
    delta = {str(r): result["profile"].get(str(r), 0)-original["profile"].get(str(r), 0)
             for r in range(1,10)}
    delta = {r: n for r, n in delta.items() if n}
    M.need(delta == {"1": -2, "6": -1, "8": 1}, "exact profile delta")
    for op in ("add", "sign", "zero", "erase"):
        M.need(original["counts"][op] == result["counts"][op], "retained scalar/private counts")
    scalar = lambda w: [e[:4] if e[0] == "add" else e[:3] for e in w["program"]
                        if e[0] in ("add", "sign")]
    M.need(scalar(source) == scalar(candidate), "scalar order and coefficients")
    private = lambda w: [e for e in w["program"] if e[0] in ("zero", "erase")]
    M.need(private(source) == private(candidate), "private lifetime order and charts")
    N = M.native_module("native_verify.py")
    native = M.read(M.P/"NATIVE.json")
    checked = native_check(native, N)
    negatives = controls(source, candidate, native, N)
    equivalent = copy.deepcopy(candidate)
    next(e for e in equivalent["program"] if e[0] == "transport" and e[1] == "X90" and e[4] == 7)[3].reverse()
    M.need(M.replay(equivalent) == result, "equivalent frame basis positive control")
    return dict(schema_version=1, status="PASS", baseline=original, candidate=result,
                profile_delta=delta, native=checked, rejecting_controls=negatives,
                moment_change="(8^p - 6^p - 2)/m^p < 0 for m>0 and 0<p<1",
                scope="One exact finite two-register ADD retiming; no supplier or new kappa")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()
    if args.out:
        M.need(not args.out.exists(), "exclusive output")
    result = compute()
    if args.regenerate:
        import build
        word, native = build.construct()
        M.need(M.encoded(word) == M.encoded(M.read(M.P/"WORD.json")), "regenerated word")
        M.need(M.encoded(native) == M.encoded(M.read(M.P/"NATIVE.json")), "regenerated native recipes")
    if args.out:
        M.write_new(args.out, result)
    else:
        M.need(M.encoded(result) == M.encoded(M.read(M.P/"RESULT.json")), "complete typed receipt")
    print("PASS_P104_DUAL_ADD_RETIMING events=5268 transports=1940 mass=3542 "
          "coefficients=128164 columns=1024 zero_erases=8 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
