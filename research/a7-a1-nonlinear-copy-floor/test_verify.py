"""Rejecting controls for verify.py. Each mutation must raise SystemExit."""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

rr, pairing, orth, t16, readers = V.model()
shifts = V.source_shifts()
stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
eight, _ = shifts["eight_active"]
sources, costs = V.invoice(V.decoder(rr, eight), pairing, readers)
rows = stored["witnesses"]["eight_active"]["terms"]


def rejects(name, fn):
    try:
        fn()
    except SystemExit as exc:
        if not str(exc).startswith("FAIL"):
            raise
        return name
    raise AssertionError("control accepted: " + name)


def mutated(edit):
    r = copy.deepcopy(rows)
    edit(r)
    return lambda: V.check_terms(pairing, orth, sources, readers, costs, r)


def singular(r):
    t = r[1]
    t["fooling_sources"][1] = next(i for i in sorted(sources[1])
                                   if i not in t["fooling_sources"]
                                   and pairing[i] == pairing[t["fooling_sources"][0]]) \
        if any(pairing[i] == pairing[t["fooling_sources"][0]] and i not in t["fooling_sources"]
               for i in sources[1]) else t["fooling_sources"][0]


def outside(r):
    r[1]["fooling_sources"][0] = next(i for i in range(120) if i not in sources[1])


def nonedge(r):
    p = r[2]["sideinfo"]["petersen"]
    p[0], p[1] = p[1], p[0]  # vertices 01 and 02 swap roles: edge pattern breaks


def isolated(r):
    info = r[3]["sideinfo"]
    demand = sources[3] & readers[3]
    info["isolated"][0] = next(c for c in sorted(demand)
                               if c not in info["petersen"] + info["isolated"]
                               and any(orth[c][x] for x in info["petersen"]))


def duplicate(r):
    info = r[4]["sideinfo"]
    info["isolated"][1] = info["isolated"][0]


nine, _ = shifts["nine_active"]
n_sources, n_costs = V.invoice(V.decoder(rr, nine), pairing, readers)
n_rows = stored["witnesses"]["nine_active"]["terms"]


def bad_clique():
    r = copy.deepcopy(n_rows)
    r[0]["sideinfo"]["lines"] = [next(iter(sorted(n_sources[0] & readers[0])))] * 1
    r[0]["rank"] = 2
    V.check_terms(pairing, orth, n_sources, readers, n_costs, r)


def changed_shift():
    s = list(eight)
    s[5] += 3
    d4 = V.decoder(rr, s)
    V.require(V.exact(d4, t16, rr), "identity")
    src, cst = V.invoice(d4, pairing, readers)
    V.require(cst == [0] + [9] * 8, "changed shift invoice equals pinned predecessor")


def tampered():
    t = copy.deepcopy(stored)
    t["witnesses"]["eight_active"]["costs"][1] = 8
    V.require(t == json.loads(json.dumps(V.result())), "stored certificate mismatch")


def drifted():
    original = V.ROOT
    try:
        fake = HERE / "_drift"
        target = fake / "research" / "a7-a1-decoder-floor"
        target.mkdir(parents=True, exist_ok=True)
        (target / "RESULT.json").write_text("{}", encoding="utf-8")
        V.ROOT = fake
        V.pinned_inputs()
    finally:
        V.ROOT = original
        for p in sorted((HERE / "_drift").rglob("*"), reverse=True):
            p.unlink() if p.is_file() else p.rmdir()
        (HERE / "_drift").rmdir()


# Every stored row must pass before the controls mean anything.
V.check_terms(pairing, orth, sources, readers, costs, rows)
done = [
    rejects("singular fooling block", mutated(singular)),
    rejects("fooling line outside the term", mutated(outside)),
    rejects("Petersen non-edge swapped", mutated(nonedge)),
    rejects("isolated line orthogonal to the witness", mutated(isolated)),
    rejects("duplicated witness line", mutated(duplicate)),
    rejects("clique too small for its rank", bad_clique),
    rejects("changed shift breaks exactness or invoice", changed_shift),
    rejects("tampered stored certificate", tampered),
    rejects("drifted predecessor input", drifted),
]
print("PASS_A7_A1_NONLINEAR_COPY_FLOOR_CONTROLS rejected=%d" % len(done))
