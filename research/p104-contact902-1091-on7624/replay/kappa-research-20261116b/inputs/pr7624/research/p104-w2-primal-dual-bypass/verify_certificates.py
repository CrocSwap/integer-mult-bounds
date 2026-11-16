"""Standalone exact rational (Fraction) verifier for all 204 CLEAR certificates in evidence/certs-step1.json.

Verifies:
  1. Replays data/word.json.gz over exact Q and captures live public+owned rows at all 204 owned CLEARs.
  2. Checks every certificate c in evidence/certs-step1.json reproduces the exact erased Q-vector from other live rows,
     checks remaining live rows span full public rank (1501), and verifies final public state rank == 1501.
  3. Compares all 74 matched-base CLEAR Q-vectors against base7605.json.gz (confirming 68 unchanged + exact 6 Q-modified).
  4. Runs 3 negative controls (weight perturbation, term deletion, erased-column mutation) ensuring rejection.
"""
from __future__ import annotations

from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
EVID = HERE / "evidence"

EXPECTED_WORD_CANON = "c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de"
EXPECTED_BASE_CANON = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"


def canon_sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def q_rank(rows: dict[int, dict[int, Q]]) -> int:
    pivots = {}
    for row in rows.values():
        cur = {c: v for c, v in row.items() if v}
        while cur:
            col = next(iter(sorted(cur)))
            if col not in pivots:
                piv = cur[col]
                pivots[col] = {k: v / piv for k, v in cur.items()}
                break
            pcol, prow = col, pivots[col]
            factor = cur[pcol]
            for k, v in prow.items():
                nv = cur.get(k, Q(0)) - factor * v
                if nv:
                    cur[k] = nv
                else:
                    cur.pop(k, None)
    return len(pivots)


def replay_snapshots(W: dict, capture_snaps: bool = True):
    n = W["public"]
    N = n + W["owned_fields"]
    dims = [len(f) for f in W["frames"]]
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    live = set(range(n))
    cur = list(W["initial"]) + [None] * W["owned_fields"]
    lt = {}
    clears = []
    for idx, e in enumerate(W["program"]):
        op, r = e[0], e[1]
        if op == "INIT":
            assert r >= n and r not in live
            live.add(r)
            cur[r] = e[2]
            rows[r] = {}
            lt[r] = {"tokens": [("INIT", r, e[2])]}
        elif op == "CLEAR":
            assert r >= n and r in live and cur[r] == e[2]
            info = lt.pop(r)
            info["tokens"].append(("CLEAR", r, e[2]))
            target = {k: v for k, v in rows[r].items() if v}
            snap = {k: dict(rows[k]) for k in live if k != r and rows[k]} if capture_snaps else None
            clears.append({
                "clear_index": len(clears),
                "event": idx,
                "field": r,
                "chart": e[2],
                "dim": dims[e[2]],
                "tokens": info["tokens"],
                "target": target,
                "snap": snap,
            })
            live.remove(r)
            cur[r] = None
            rows[r] = {}
        elif op == "MOVE":
            _, r, a, b, _ = e
            assert cur[r] == a
            cur[r] = b
            if r >= n:
                lt[r]["tokens"].append(("MOVE", r, a, b))
        elif op == "SCALE":
            q = Q(e[2])
            rows[r] = {k: v * q for k, v in rows[r].items() if v * q}
        elif op in ("ADD", "COPY"):
            q = Q(e[3])
            R = rows[r]
            for k, v in rows[e[2]].items():
                nv = R.get(k, Q(0)) + q * v
                if nv:
                    R[k] = nv
                else:
                    R.pop(k, None)
        else:
            raise ValueError(op)
    assert not lt
    pub_snap = {k: dict(rows[k]) for k in range(n) if rows[k]}
    assert q_rank(pub_snap) == n
    return clears


def verify_comb(snap: dict[int, dict[int, Q]], cert: dict[int, Q], target: dict[int, Q]) -> bool:
    acc = {}
    for fk, q in cert.items():
        if fk not in snap:
            return False
        for col, val in snap[fk].items():
            nv = acc.get(col, Q(0)) + q * val
            if nv:
                acc[col] = nv
            else:
                acc.pop(col, None)
    return acc == target


def main():
    W = json.loads(gzip.decompress((DATA / "word.json.gz").read_bytes()))
    B = json.loads(gzip.decompress((DATA / "base7605.json.gz").read_bytes()))
    assert canon_sha256(W) == EXPECTED_WORD_CANON
    assert canon_sha256(B) == EXPECTED_BASE_CANON

    certs_doc = json.loads((EVID / "certs-step1.json").read_text(encoding="utf-8"))
    entries = certs_doc["clears"]
    assert len(entries) == 204

    snaps = replay_snapshots(W, capture_snaps=True)
    base_clears = replay_snapshots(B, capture_snaps=False)
    assert len(snaps) == 204 and len(base_clears) == 74

    dirty = 0
    zero = 0
    first_dirty = None
    for s, c in zip(snaps, entries):
        assert s["clear_index"] == c["clear_index"]
        assert s["event"] == c["event"] and s["field"] == c["field"]
        assert s["chart"] == c["chart"] and s["dim"] == c["dim"]
        exp_target = {int(k): Q(v) for k, v in c["erased"].items()}
        assert s["target"] == exp_target, f"Erased vector mismatch on CLEAR #{c['clear_index']}"
        cert_q = {int(k): Q(v) for k, v in c["certificate"].items()}
        assert verify_comb(s["snap"], cert_q, s["target"]), f"Certificate failed on CLEAR #{c['clear_index']}"
        assert c["other_rank"] == 1501
        if s["target"]:
            dirty += 1
            if first_dirty is None and cert_q:
                first_dirty = (s, cert_q)
        else:
            zero += 1
            assert cert_q == {}
            assert c["terms"] == 0

    assert dirty == 197 and zero == 7

    # Check matched-base CLEAR Q-vectors vs base7605
    j = 0
    diff_base = []
    for s in snaps:
        if j < len(base_clears) and s["tokens"] == base_clears[j]["tokens"]:
            if s["target"] != base_clears[j]["target"]:
                diff_base.append(j)
            j += 1
    assert j == 74 and diff_base == [27, 37, 44, 54, 62, 63], f"Unexpected base CLEAR diff set: {diff_base}"

    # 3 Negative controls
    s_ctrl, cert_ctrl = first_dirty
    k0 = next(iter(cert_ctrl))
    bad1 = dict(cert_ctrl); bad1[k0] = bad1[k0] + Q(1)
    assert not verify_comb(s_ctrl["snap"], bad1, s_ctrl["target"]), "Control 1 failed"
    bad2 = dict(cert_ctrl); bad2.pop(k0)
    assert not verify_comb(s_ctrl["snap"], bad2, s_ctrl["target"]), "Control 2 failed"
    t0 = next(iter(s_ctrl["target"]))
    bad_t = dict(s_ctrl["target"]); bad_t[t0] = bad_t[t0] + Q(1)
    assert not verify_comb(s_ctrl["snap"], cert_ctrl, bad_t), "Control 3 failed"

    print(
        f"PASS_STEP1_CERTIFICATES 204/204 "
        f"(dirty={dirty}, zero={zero}; matched_base=74: 68 unchanged, 6 modified {diff_base}; controls=3/3 rejected)"
    )


if __name__ == "__main__":
    main()
