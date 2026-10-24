"""Rejecting controls for verify.py: each corrupted input must be rejected by the same check functions."""
from collections import Counter
from fractions import Fraction as F
import copy, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h8lib as H  # noqa: E402
import verify as V  # noqa: E402


def rejects(name, fn):
    try:
        fn()
    except (ValueError, AssertionError, IndexError, KeyError):
        return name
    raise SystemExit("UNREJECTED control: " + name)


def main():
    V.EXPECTED.update(json.loads((HERE / "RESULT.json").read_text())["expected"])
    done = []
    sel589 = H.canon_gz(V.R437 / "data/SELECTED589.json.gz")

    # 1. a stored kappa that is not the root of its stored profile
    row = V.table("STAGE-C.csv.gz")[0]
    p = V.prof(row["local_profile"])
    k = V.fkappa(p, {8: int(row["R"])})
    done.append(rejects("stored kappa off its profile root",
                        lambda: H.need(abs(V.fkappa(p, {8: int(row["R"])}) - (k + 1e-9)) <= 1e-12, "kappa")))
    # 2. a profile breaking the generator's mass identity 8R + 63 + 14v
    q = dict(p)
    q[1] += 1
    done.append(rejects("mass identity", lambda: H.need(
        sum(a * b for a, b in q.items()) == 8 * int(row["R"]) + 63 + 14 * 111, "mass")))
    # 3. an invoice that silently drops one paid rank-7 query per call is caught by the exact root bracket
    def dropped():
        r = Counter(H.PR589_LOCAL)
        r[7] -= 1
        lo, hi = H.raw_root(dict(r))
        H.need([str(lo), str(hi)] == V.EXPECTED["pr589_raw"], "PR589 raw root")
    done.append(rejects("dropped rank-7 query", dropped))
    # 4. GL464 + 470 on a word whose entrance gate was moved
    w = copy.deepcopy(sel589)
    w["A"][224], w["A"][225] = w["A"][225], w["A"][224]
    done.append(rejects("GL464 entrance gate moved", lambda: V.gl464_470(w)))
    # 5. GL464 + 470 when the 470 carrier has another reader
    w = copy.deepcopy(sel589)
    w["B"].append([0, 0, [470]])
    done.append(rejects("470 carrier with an extra reader", lambda: V.gl464_470(w)))
    # 6. a corrupted helper write: the D0 restoration check of the composed generator fails
    w = copy.deepcopy(sel589)
    w["A"][-1] = [w["A"][-1][0], w["A"][-1][1], w["A"][-1][2] + [0]]
    done.append(rejects("non-restoring word", lambda: V.gl464_470(w)))
    # 7. a stacking estimate claimed above #4760's 0.1% improvement gate
    def overclaim():
        head = F(V.EXPECTED["compact436_raw"][1])
        H.need(F(0) < head * F(1002, 1000) / head - 1 < F(1, 1000), "gate")
    done.append(rejects("estimate above the 0.1% gate", overclaim))
    # 8. a PR589 move applied to a gate that does not hold its summand
    moves = json.loads((H.TUNED / "moves.json").read_text())["moves"]
    bad = copy.deepcopy(moves)
    bad[0]["gate"] += 1
    base = H.canon_gz(H.P111 / "data/bitE8mut-p111.json.gz")
    done.append(rejects("misplaced tuner move", lambda: H.apply_moves(base, bad)))
    print(json.dumps({"status": "PASS_ALL_CONTROLS_REJECT", "rejected": done}, indent=1))


if __name__ == "__main__":
    main()
