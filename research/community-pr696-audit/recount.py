"""Independent recount of PR #696's complex scalar-primitive claim.

Rohan Guliani (@Rohansguliani), with substantial AI assistance. Apache-2.0.
Audits PR #696 by Sagar Thakrar (thakrarsagar) at
5a3f983715027c4fd83f50bc9001d4b18463bed1. No PR #696 code is imported.

Python 3.11+, standard library, offline, writes nothing. Run from anywhere:

    python3 -B research/community-pr696-audit/recount.py
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
REPLAY = ROOT / "research/community-k492-audit/pr626/replay"
PROVIDERS = REPLAY / "mixed-global/base/providers"
INVOICE = REPLAY / "mixed-global/audit/PREFIX-AND-INVOICE.json"
ASSEMBLY = REPLAY / "ASSEMBLY.json"
SELECTED = ROOT / "certificates/selected-result.json"
W = ("W",)

# Numbers claimed in PR #696 (README table and verify.py output).
CLAIM = {
    ("ck", "forward"): (224938, 169618),
    ("ck", "backward"): (224986, 169634),
    ("jp8", "forward"): (257232, 200380),
    ("jp8", "backward"): (257280, 200396),
}


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def old_word(op):
    """Original cleared-work binary Horner, transcribed from the macro meaning."""
    tag, t = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", t)]
    if tag == "copy":
        return [("copy", t, tuple(op[2]))]
    if tag == "scale":
        q = Q(op[2], op[3])
        k = abs(q.numerator).bit_length() - q.denominator.bit_length()
        return [("mul", t, Q(2) if k > 0 else Q(1, 2))] * abs(k) + ([("mul", t, Q(-1))] if q < 0 else [])
    s, q = tuple(op[2]), Q(op[3], op[4])
    a = abs(q.numerator)
    word = [("clear", W)]
    for i, bit in enumerate(bin(a)[2:]):
        if i:
            word.append(("mul", W, Q(2)))
        if bit == "1":
            word.append(("acc", W, s, 1))
    word += [("mul", W, Q(1, 2))] * (q.denominator.bit_length() - 1)
    word += [("acc", t, W, 1 if q > 0 else -1), ("clear", W)]
    return word


def new_word(op):
    """PR #696's described rule, re-implemented: copy-init; unit = acc + clear."""
    if op[0] != "add":
        return old_word(op)
    t, s, q = tuple(op[1]), tuple(op[2]), Q(op[3], op[4])
    sign = 1 if q > 0 else -1
    if abs(q) == 1:
        return [("acc", t, s, sign), ("clear", W)]
    word = old_word(op)
    assert word[0] == ("clear", W) and word[1] == ("acc", W, s, 1)
    return [("copy", W, s)] + word[2:]


def run(regs, word, trace=None):
    for p in word:
        if p[0] == "clear":
            regs[p[1]] = 0
        elif p[0] == "copy":
            regs[p[1]] = regs[p[2]]
        elif p[0] == "mul":
            regs[p[1]] = regs[p[1]] * p[2]
        else:
            regs[p[1]] = regs.get(p[1], 0) + p[3] * regs[p[2]]
        if trace is not None:
            trace.setdefault(p[1], set()).add(regs[p[1]])


def main():
    out = {}
    rng = random.Random(696)
    for pid in ("ck", "jp8"):
        programs = load(PROVIDERS / pid / "LOCAL-PROGRAMS.json.gz")
        checks = load(PROVIDERS / pid / "LOCAL-CHECKS.json")
        for ori in ("forward", "backward"):
            events = programs[ori]
            digest = hashlib.sha256(json.dumps(events, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            assert digest == checks[ori]["sha256"], "program hash"
            scalars = [e[1] for e in events if e[0] == "scalar"]
            old = 2 * sum(len(old_word(op)) for op in scalars)
            new = 2 * sum(len(new_word(op)) for op in scalars)
            adds = [op for op in scalars if op[0] == "add"]
            units = sum(abs(Q(op[3], op[4])) == 1 for op in adds)
            assert old == checks[ori]["real_component_primitive_bound"], "baseline differs from emitter"
            assert old - new == 2 * (len(adds) + units)
            assert (old, new) == CLAIM[(pid, ori)], ("claim mismatch", pid, ori, old, new)
            # Randomised whole-program replay on complex inputs (two real
            # components) with dirty private work, including per-macro prefix
            # containment: every value the new word writes to a register also
            # occurs in that register under the old word from the same state.
            for trial in range(2):
                for comp in range(2):
                    a = {}
                    for op in scalars:
                        for r in [op[1]] + ([op[2]] if op[0] in ("add", "copy") else []):
                            a.setdefault(tuple(r), Q(rng.randint(-10**6, 10**6), rng.randint(1, 999)))
                    a[W] = Q(rng.randint(-10**6, 10**6), 7)
                    b = dict(a)
                    for op in scalars:
                        before = dict(b)
                        old_trace, new_trace = {}, {}
                        run(a, old_word(op), old_trace)
                        run(b, new_word(op), new_trace)
                        assert a == b, "state diverged"
                        for r, vals in new_trace.items():
                            assert vals <= old_trace.get(r, set()) | {before.get(r)}, "prefix escape"
                        if op[0] == "add":
                            assert b[W] == 0
            out[f"{pid}/{ori}"] = dict(old=old, new=new, saved=old - new,
                                       percent=f"{100 * (old - new) / old:.2f}",
                                       additions=len(adds), unit_additions=units,
                                       primitive_tags=dict(sorted(Counter(2 * [p[0] for op in scalars for p in new_word(op)]).items())))

    # kappa sensitivity: kappa is a function of the paid profile only; the
    # scalar bill enters the finite per-vertex invoice and pass/fail checks.
    invoice = load(INVOICE)
    counts = invoice["provider_counts"]
    selected_saved = sum(out[f"{c['provider_id']}/{c['orientation']}"]["saved"]
                         for c in invoice["selected_calls"])
    assembly, selected = load(ASSEMBLY), load(SELECTED)
    assert assembly["kappa"] == selected["kappa"]
    result = dict(
        status="PASS_PR696_INDEPENDENT_RECOUNT",
        programs=out,
        selected_calls=counts,
        selected_real_component_primitives=invoice["selected_real_component_primitives"],
        selected_saved=selected_saved,
        conservative_pervertex_used=invoice["conservative_pervertex_used"],
        pervertex_fraction_saved=f"{selected_saved / invoice['conservative_pervertex_used']:.3e}",
        kappa=selected["kappa"],
        kappa_inputs="paid profile, m=73, live, deficit, cited bit profile (complex-k492-owner-repair/code/assemble.py)",
    )
    print(json.dumps(result, indent=2))
    pcts = [float(r["percent"]) for r in out.values()]
    print(f"PASS_PR696_INDEPENDENT_RECOUNT savings="
          + ",".join(str(r["saved"]) for r in out.values())
          + f" percent={min(pcts):.2f}-{max(pcts):.2f} kappa_inputs_unchanged=True")


if __name__ == "__main__":
    main()
