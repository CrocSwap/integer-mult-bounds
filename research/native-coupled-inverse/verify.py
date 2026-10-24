#!/usr/bin/env python3
"""Verify the native inverse from authenticated source bytes. Apache-2.0."""

from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import importlib.util
import json
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def check(SRC):
    spec = importlib.util.spec_from_file_location("coupled_source", SRC / "verify.py")
    s = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(s)
    s.main()
    source = json.loads(
        gzip.decompress(
            (SRC.parent / "native-center-free-code/SOURCE-WORD.json.gz").read_bytes()
        )
    )
    c = source["canonical"]
    p = json.loads((SRC / "PROVIDER.json").read_text())
    word = json.loads(gzip.decompress((SRC / "WORD.json.gz").read_bytes()))["word"]
    inherited_records = dict(Counter(e[0] for e in word))
    # C0 has no paid call in the changed word. Each live use is a copy of C1..C8.
    new = []
    active = None
    removed = Counter()
    substitutions = []
    for i, e in enumerate(word):
        if e[0] == "scalar":
            op = e[1]
            dst = s.addr(op[1])
            if dst == 632:
                if op[0] == "copy":
                    active = op[2]
                else:
                    active = None
                removed[op[0]] += 1
                continue
            if op[0] in ("add", "copy") and s.addr(op[2]) == 632:
                if active is None:
                    raise ValueError("C0 read has no retained cache")
                e = ["scalar", [op[0], op[1], active, *op[3:]], e[2]]
                substitutions.append([i, active])
        new.append(e)
    if len(substitutions) != 8:
        raise ValueError("expected eight live cache uses")
    # Replaying with an initial dirty C0 clear permits the exact source interpreter.
    fwd = s.replay([["scalar", ["clear", ["C", 0]], 0]] + new, c, 641)
    old = s.replay(word, c, 641)
    if (
        fwd[0] != old[0]
        or fwd[1][:632] + fwd[1][633:] != old[1][:632] + old[1][633:]
        or fwd[2] != old[2]
    ):
        raise ValueError("dead accumulator elimination changed endpoint")

    def identity():
        return [{(j, ()): F(1)} for j in range(641)]

    def linear(ops, rows):
        for e in ops:
            if e[0] == "add":
                s.add(rows[e[1]], rows[e[2]], F(e[3]))
            else:
                rows[e[1]] = {k: v * F(e[2]) for k, v in rows[e[1]].items()}

    # Apply a native word to supplied columns, with exact inverse child frames.
    def apply(program, rows, charts, reverse=False, copy_sign=-1):
        paid = Counter()
        clears = []
        copies = []
        for index, e in (
            reversed(list(enumerate(program))) if reverse else enumerate(program)
        ):
            kind = e[0]
            if kind == "scalar":
                op, frame = e[1:]
                dst = s.addr(op[1])
                if op[0] == "clear":
                    if reverse:
                        if rows[dst]:
                            raise ValueError("reverse initial clear is not zero")
                        clears.append(dst)
                    else:
                        rows[dst] = {}
                        charts[dst] = frame
                elif op[0] == "copy":
                    src = s.addr(op[2])
                    if charts[src] != frame or charts[dst] != frame:
                        raise ValueError("copy charts")
                    if reverse:
                        s.add(rows[dst], rows[src], copy_sign)
                        if rows[dst]:
                            raise ValueError("inverse copy did not erase cache")
                        copies.append(dst)
                    else:
                        if rows[dst]:
                            raise ValueError("copy input not zero")
                        rows[dst] = dict(rows[src])
                elif op[0] == "add":
                    src = s.addr(op[2])
                    if charts[src] != frame or charts[dst] != frame:
                        raise ValueError("add charts")
                    s.add(
                        rows[dst], rows[src], F(op[3], op[4]) * (-1 if reverse else 1)
                    )
                else:
                    if charts[dst] != frame:
                        raise ValueError("scale chart")
                    a = F(op[2], op[3])
                    a = 1 / a if reverse else a
                    rows[dst] = {k: v * a for k, v in rows[dst].items()}
            elif kind == "warp":
                _, ref, w, a, b = e
                dst = s.addr(ref)
                if reverse:
                    w = -w
                    a, b = b, a
                if charts[dst] != a:
                    raise ValueError("warp chart")
                sym = (1 if w > 0 else -1) * (abs(w) + 1000000)
                out = {}
                for (owner, t), v in rows[dst].items():
                    t = t[1:] if t and t[0] == -sym else (sym,) + t
                    s.add(out, {(owner, t): v})
                rows[dst] = out
                charts[dst] = b
            elif kind == "climb":
                _, _, dst, a, b, r = e
                if reverse:
                    a, b = b, a
                if (
                    charts[dst] != a
                    or abs(len(c["frames"][a]) - len(c["frames"][b])) != r
                ):
                    raise ValueError("child chart")
                charts[dst] = b
                paid[r] += 1
            elif kind == "zero_retag":
                _, dst, a, b = e
                if reverse:
                    a, b = b, a
                if charts[dst] != a or rows[dst]:
                    raise ValueError("nonzero retag")
                charts[dst] = b
            elif kind not in ("phase", "adapter", "residual_adapter"):
                raise ValueError(kind)
        return paid, clears, copies

    w = json.loads((SRC / "WITNESS.json").read_text())
    records = p["mode_boundaries"]
    perm = p["candidate_mode_permutation"]
    sign = list(map(F, p["candidate_mode_signs"]))
    factors = {
        r["cache_slot"]: F(w[r["witness_row"]]["zero_factor"]) * sign[r["witness_row"]]
        for r in records
    }

    def full(rows, reverse=False, copy_sign=-1):
        # Logical normalization: physical monomial boundaries are inverted separately.
        for j in range(632, 641) if reverse else [632]:
            rows[j] = {}
        if not reverse:
            charts = c["start"][:] + [None] * 9
            linear(p["input_basis_program"], rows)
            stats = apply(new, rows, charts)
            linear(p["output_basis_program"], rows)
            for r in records:
                a, b = r["owner"], r["cache_slot"]
                f = factors[b]
                rows[b] = {k: v / f for k, v in rows[b].items()}
                if rows[a]:
                    raise ValueError("forward swap owner nonzero")
                rows[a], rows[b] = rows[b], rows[a]
        else:
            charts = c["final"][:] + [None] * 9
            for r in records:
                a, b = r["owner"], r["cache_slot"]
                f = factors[b]
                rows[a], rows[b] = rows[b], rows[a]
                rows[b] = {k: v * f for k, v in rows[b].items()}
                charts[b] = r["frame"]
            linear(p["input_basis_program"], rows)
            stats = apply(new, rows, charts, True, copy_sign)
            linear(p["output_basis_program"], rows)
        if any(rows[632:]):
            raise ValueError("owned output nonzero")
        # Clear the eight owned cache returns after the exact zero check.
        for owner in range(633, 641):
            rows[owner] = {}
        return rows, stats

    f, fs = full(identity())
    b, bs = full(identity(), True)
    if fs[0] != bs[0] or bs[0] != Counter({int(k): v for k, v in p["paid"].items()}):
        raise ValueError("paid mismatch")
    for first, back in ((f, True), (b, False)):
        z, _ = full([dict(r) for r in first], back)
        if z[:632] != identity()[:632] or any(z[632:]):
            raise ValueError("not a two-sided inverse")
    # Check the inverse independently from the full scalar endpoint formula.
    M = json.loads((SRC.parent / "coded-native-caller/NORMALIZERS.json").read_text())[
        "mode_columns"
    ]
    for j in range(632):
        row = {(j, ()): F(1)}
        if j < 112:
            row[(112 + j, ())] = F(1)
            for k in range(8):
                s.add(row, {(p["mode_owners"][k], ()): F(1)}, -F(M[k][j], 4))
                for i in range(112):
                    s.add(row, {(112 + i, ()): F(1)}, -F(M[k][j] * M[k][i], 4))
        if j in p["mode_owners"]:
            k = p["mode_owners"].index(j)
            for i in range(112):
                s.add(row, {(112 + i, ()): F(1)}, M[k][i])
        row = {k: v for k, v in row.items() if v}
        if b[j] != row:
            raise ValueError("independent inverse formula")
    controls = []
    try:
        full(identity(), True, 1)
    except ValueError as exc:
        if str(exc) != "inverse copy did not erase cache":
            raise
        controls.append("wrong inverse COPY sign rejected")
    if len(controls) != 1:
        raise ValueError("wrong COPY sign accepted")
    try:
        apply(
            [["zero_retag", 0, c["start"][0], c["start"][0]]],
            identity(),
            c["start"][:] + [None] * 9,
            True,
        )
    except ValueError as exc:
        if str(exc) != "nonzero retag":
            raise
        controls.append("nonzero reverse retag rejected")
    if len(controls) != 2:
        raise ValueError("nonzero retag accepted")
    # Each inverse rank-r Gaussian is the positive child followed by a bit translation.
    _, _, ce = s.authenticate()
    for rank in range(1, 10):
        G = ce.fourier(9, range(rank))
        positive = G.then(ce.xgate(9, (1 << rank) - 1))
        inverse = G.adjoint()
        if positive.tab != inverse.tab or positive.zero_state() != inverse.zero_state():
            raise ValueError("inverse child phase")
    # Exact adjoints of each physical boundary retain their absolute phases.
    normal = json.loads(
        (SRC.parent / "coded-native-caller/NORMALIZERS.json").read_text()
    )
    words = [r[k]["literal_word"] for r in records for k in ("input_K", "output_N")]
    words += [
        port["compiled_wrappers"][k]["word"]
        for port in normal["ports"]
        for k in (
            "backward_input_X",
            "backward_input_Y",
            "backward_output_X",
            "backward_output_Y",
        )
    ]

    def literal(word):
        op = ce.ident(9)
        for e in word:
            if e[0] == "P":
                a = ce.perm(9, tuple(e[1]))
            elif e[0] == "D":
                a = ce.diag(9, tuple(e[1]), tuple(e[2]))
            elif e[0] == "X":
                a = ce.xgate(9, e[1])
            elif e[0] == "phase":
                a = ce.Op(9, ce.identity(9), [("phase", e[1])])
            else:
                raise ValueError("nonmonomial wrapper")
            op = op.then(a)
        return op

    for word in words:
        A = literal(word)
        B = literal(A.adjoint().circuit)
        for v in (A.then(B), B.then(A)):
            if v.tab != ce.identity(9) or v.zero_state() != ce.ident(9).zero_state():
                raise ValueError("boundary inverse phase")
    bad = literal(words[0]).adjoint()
    bad = ce.Op(9, bad.tab, bad.circuit + [("phase", 1)])
    v = literal(words[0]).then(bad)
    if v.zero_state() == ce.ident(9).zero_state():
        raise ValueError("phase mutation accepted")
    controls.append("same-tableau inverse phase error rejected")
    # Count the literal schedule, including inverse cache ADDs and initialization.
    ordinary_forward = Counter(e[1][0] for e in new if e[0] == "scalar")
    ordinary_inverse = Counter()
    for e in new:
        if e[0] == "scalar" and e[1][0] != "clear":
            ordinary_inverse["add" if e[1][0] == "copy" else e[1][0]] += 1
    for program in (p["input_basis_program"], p["output_basis_program"]):
        for e in program:
            ordinary_forward[e[0]] += 1
            ordinary_inverse[e[0]] += 1
    ordinary_forward.update(clear=9, scale=16, swap=8, monomial=464)
    ordinary_inverse.update(clear=17, scale=16, swap=8, monomial=464)
    # A positive-child inverse needs at most one further translation per paid call.
    ordinary_inverse["child_inverse_translation"] += sum(bs[0].values())

    def log_bound(a):
        e = 0
        while a > 1:
            a /= 2
            e += 1
        return e

    bound = 0
    for e in new:
        if e[0] == "scalar":
            op = e[1]
            if op[0] == "add":
                bound += log_bound(1 + abs(F(op[3], op[4])))
            elif op[0] == "copy":
                bound += 1
            elif op[0] == "scale":
                bound += log_bound(max(F(1), abs(F(op[3], op[2]))))
    for program in (p["input_basis_program"], p["output_basis_program"]):
        for e in program:
            bound += (
                log_bound(1 + abs(F(e[3])))
                if e[0] == "add"
                else log_bound(max(F(1), abs(F(e[2]))))
            )
    bound += sum(log_bound(max(F(1), abs(1 / F(r["cache_scalar"])))) for r in records)
    receipt = {
        "status": "PASS_SAME_PAID_NATIVE_TWO_SIDED_INVERSE",
        "source_pr": 5402,
        "source_head": "3348fccea855082786d5f0fc5558b73d4974e745",
        "independent_original_columns": 632,
        "owned_outputs_zero": 9,
        "paid": dict(sorted(bs[0].items())),
        "removed_dead_C0_records": dict(removed),
        "live_cache_substitutions": substitutions,
        "inverse_copy_uncomputations": bs[2],
        "inherited_record_types": inherited_records,
        "boundary_adjoint_checks": len(words),
        "inverse_child_ranks_checked": list(range(1, 10)),
        "ordinary_forward": dict(ordinary_forward),
        "ordinary_inverse": dict(ordinary_inverse),
        "inverse_local_amplification_power2_bound": bound,
        "failure_controls": controls,
        "scope": "All-width native inverse of the coupled provider; no autonomous credit for the coupled outputs, complete caller, full precision/compiler bill or new kappa.",
    }
    return receipt


def main(emit=False):
    origins = json.loads((HERE / "ORIGINS.json").read_text())
    pins = json.loads((HERE / "SOURCES.json").read_text())
    archive = (HERE / "SOURCE.zip").read_bytes()
    if sha256(archive).hexdigest() != origins["archive_sha256"]:
        raise ValueError("source archive changed")
    with tempfile.TemporaryDirectory(prefix="native-coupled-inverse-") as tmp:
        root = Path(tmp)
        src = root / "research/native-rank8-helper-provider"
        src.mkdir(parents=True)
        with zipfile.ZipFile(HERE / "SOURCE.zip") as z:
            if set(z.namelist()) != {r["file"] for r in origins["files"]}:
                raise ValueError("source archive inventory")
            for row in origins["files"]:
                data = z.read(row["file"])
                if sha256(data).hexdigest() != row["sha256"]:
                    raise ValueError("source archive member changed")
                (src / row["file"]).write_bytes(data)
        for row in pins["files"]:
            if row["usage"] != "input":
                continue
            data = (ROOT / row["path"]).read_bytes()
            if sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("main input changed")
            dst = root / row["path"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
        receipt = check(src)
    receipt = json.loads(json.dumps(receipt))
    if emit:
        (HERE / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    elif receipt != json.loads((HERE / "RESULT.json").read_text()):
        raise ValueError("committed receipt differs")
    print(
        receipt["status"],
        json.dumps(
            {
                "columns": 632,
                "owned_zero": 9,
                "paid": receipt["paid"],
                "controls": len(receipt["failure_controls"]),
            }
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    main(parser.parse_args().emit)
