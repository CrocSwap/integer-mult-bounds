#!/usr/bin/env python3
"""Exact, source-bound X4 precondition lowering; no changed kappa claim.

Philipp (@mightyOil), with substantial OpenAI Codex assistance. Apache-2.0.
The retained X4 word/emitter and their contributors are credited in README.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier799-audit/integrated799-replay.tar.gz"
ARCHIVE_SHA = "70dfdfcf2ff95352c6020ee9dfca6dca9032b33c10daed3f3dc574c014f4e2cb"
PAYLOADS = {
    "native/local/CANONICAL-WORD.json.gz": "1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa",
    "native/local/LOCAL-PROGRAMS.json.gz": "223c2bb27ad68a4e9468c3ddaece1899d577b661190922fdd25f5976052c4cab",
    "native/local/LOCAL-CHECKS.json": "bbde5cea7bfd5df3d3ee7dfada0ff9d165af43a4d1dec6a9597cbfd8f87cc3b2",
}
PROFILE = {1: 2548, 2: 338, 3: 430, 4: 194, 5: 56, 8: 8}
WORK = ("W", 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def load_inputs(root=ROOT):
    path = root / ARCHIVE
    require(digest(path.read_bytes()) == ARCHIVE_SHA, "source archive digest")
    result = []
    with tarfile.open(path, "r:gz") as archive:
        for member, expected in PAYLOADS.items():
            payload = archive.extractfile(member).read()
            if member.endswith(".gz"):
                payload = gzip.decompress(payload)
            require(digest(payload) == expected, "source payload digest: " + member)
            result.append(json.loads(payload))
    return result


def pairs(word):
    pre = word["precondition"]
    require(len(pre) == 168, "56 complete precondition triples required")
    result = []
    used = set()
    for i in range(0, len(pre), 3):
        a, b, c = pre[i:i + 3]
        x, y = a[1], b[2]
        require(pre[i:i + 3] == [
            ["scale", x, -1, 2, 0], ["add", x, y, 1, 2, 0],
            ["add", y, x, -1, 1, 0]], "precondition triple shape")
        require(x != y and x not in used and y not in used, "disjoint pair support")
        require(word["start"][x] == word["start"][y] == 0, "zero-frame start")
        require(word["v"] <= x < 2 * word["v"] and
                word["v"] <= y < 2 * word["v"], "target-only support")
        used.update((x, y))
        result.append((x, y))
    return result


def expected_macros(x, y, backward):
    x, y = ["L", x], ["L", y]
    if backward:
        return [["scale", x, 2, -1], ["add", y, x, -1, 2], ["add", x, y, 1, 1]]
    return [["scale", x, -1, 2], ["add", x, y, 1, 2], ["add", y, x, -1, 1]]


def replacement(x, y, backward):
    x, y = ("L", x), ("L", y)
    # Forward: x = (y-x)/2, y = (x_old+y_old)/2.
    # Backward: inverse transpose, x = y_old-x_old, y = x_old+y_old.
    return [("add", x, y, -1), ("neg", x),
            ("double", y) if backward else ("half", x), ("add", y, x, -1)]


def lower(op):
    """Literal implementation of retained hpe_emit_local.primitive_bound.

    Every macro explicitly clears its private coefficient register before/after
    use. No work-cell initialization, copy, scale, or source read is free.
    """
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        return [("copy", target, tuple(op[2]))]
    q = Q(op[3], op[4]) if tag == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b - 1) == 0, "nonzero dyadic coefficient")
    if tag == "scale":
        require(a & (a - 1) == 0, "power-of-two scale")
        k = a.bit_length() - b.bit_length()
        return ([("neg", target)] if q < 0 else []) + [
            ("double" if k > 0 else "half", target)] * abs(k)
    require(tag == "add", "known scalar macro")
    source = tuple(op[2])
    require(source != WORK and target != WORK and source != target, "private work and distinct operands")
    out = [("clear", WORK)]
    for i, bit in enumerate(bin(a)[2:]):
        if i:
            out.append(("double", WORK))
        if bit == "1":
            out.append(("add", WORK, source, 1))
    out.extend([("half", WORK)] * (b.bit_length() - 1))
    out.extend([("add", target, WORK, 1 if q > 0 else -1), ("clear", WORK)])
    return out


class Replay:
    """All formal columns at once, sparse exact rational row arithmetic."""
    def __init__(self, n):
        self.rows = {("L", r): {r: Q(1)} for r in range(n)}
        # Nine independent dirty private columns: eight center cells and the
        # Horner work cell. Their first clear/copy must actually erase the dirt.
        self.rows.update({("C", i): {n + i: Q(1)} for i in range(8)})
        self.rows[WORK] = {n + 8: Q(1)}
        self.count = 0
        self.peak_l1 = Q(1)
        self.peak_fraction_bits = 0
        self.opcodes = Counter()

    def apply(self, op):
        tag, t = op[:2]
        row = self.rows.setdefault(t, {})
        if tag == "clear":
            row = {}
        elif tag == "copy":
            row = self.rows.get(op[2], {}).copy()
        elif tag in ("neg", "half", "double"):
            q = {"neg": Q(-1), "half": Q(1, 2), "double": Q(2)}[tag]
            row = {j: q * value for j, value in row.items()}
        elif tag == "add":
            require(t != op[2] and op[3] in (-1, 1), "signed unit addition")
            for j, value in list(self.rows.get(op[2], {}).items()):
                z = row.get(j, Q(0)) + op[3] * value
                if z:
                    row[j] = z
                else:
                    row.pop(j, None)
        else:
            raise ValueError("unknown primitive " + tag)
        self.rows[t] = row
        self.count += 1
        self.opcodes[tag] += 1
        self.peak_l1 = max(self.peak_l1, sum(map(abs, row.values()), Q(0)))
        for value in row.values():
            d = value.denominator
            require(d & (d - 1) == 0, "dyadic prefix")
            self.peak_fraction_bits = max(self.peak_fraction_bits, d.bit_length() - 1)

    def endpoint(self, n, v, backward):
        for r in range(n):
            want = {r: Q(1)}
            if backward and r < v:
                want[r + v] = Q(-1)
            if not backward and v <= r < 2 * v:
                want[r - v] = Q(1)
            require(self.rows[("L", r)] == want, "complete endpoint column row " + str(r))
        require(all(not row for r, row in self.rows.items() if r[0] != "L"), "all private cells cleared")

    def receipt(self):
        return dict(real_component_primitives=2 * self.count, per_component_primitives=self.count,
                    exact_prefix_row_l1=str(self.peak_l1), exact_prefix_fraction_bits=self.peak_fraction_bits,
                    per_component_opcodes=dict(sorted(self.opcodes.items())))


def run_orientation(word, program, checks, pair_list, backward):
    require(digest(canonical(program)) == checks["sha256"], "program digest")
    require(program[0] == ["phase", "zero_frame_precondition"], "precondition phase")
    n, v = 2 * word["v"] + word["R"], word["v"]
    old, new = Replay(n), Replay(n)
    cursor = 1
    for x, y in pair_list:
        expected = [["scalar", op, 0] for op in expected_macros(x, y, backward)]
        require(program[cursor:cursor + 3] == expected, "emitted triple binding")
        for _, macro, _ in expected:
            for op in lower(macro):
                old.apply(op)
        for op in replacement(x, y, backward):
            new.apply(op)
        require(old.rows[("L", x)] == new.rows[("L", x)] and
                old.rows[("L", y)] == new.rows[("L", y)], "pair endpoint mismatch")
        cursor += 3
    pre = {"retained": old.receipt(), "replacement": new.receipt()}
    paid = Counter()
    # All later events, source reads, frames, adapters and wrappers are unchanged.
    for event in program[cursor:]:
        if event[0] == "scalar":
            for op in lower(event[1]):
                old.apply(op)
                new.apply(op)
        elif event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
    old.endpoint(n, v, backward)
    new.endpoint(n, v, backward)
    require(dict(paid) == PROFILE, "paid profile")
    require(old.count * 2 == checks["real_component_primitive_bound"], "retained complete primitive invoice")
    require((old.count - new.count) * 2 == 784, "real-component primitive saving")
    require(new.peak_l1 <= old.peak_l1 and new.peak_fraction_bits <= old.peak_fraction_bits,
            "complete exact prefix budget must not increase")
    return dict(retained=old.receipt(), replacement=new.receipt(), precondition=pre,
                saved_real_component_primitives=784, formal_columns=n + 9,
                native_columns=n, dirty_private_columns=9,
                private_cells_cleared=True, paid_profile=PROFILE,
                unchanged_suffix_sha256=digest(canonical(program[cursor:])))


def controls(pair_list):
    """Every pair, every instruction deletion and signed-add inversion, both ways."""
    rejected = 0
    for backward in (False, True):
        # OS assignment seed 22 fixes mutation traversal, not a random proof.
        ordered = pair_list[22:] + pair_list[:22]
        for x, y in ordered:
            program = replacement(x, y, backward)
            ref = Replay(max(x, y) + 1)
            for op in program:
                ref.apply(op)
            mutants = [program[:i] + program[i + 1:] for i in range(len(program))]
            for i in (0, 3):
                change = list(program[i]); change[3] *= -1
                mutants.append(program[:i] + [tuple(change)] + program[i + 1:])
            for mutant in mutants:
                test = Replay(max(x, y) + 1)
                for op in mutant:
                    test.apply(op)
                require(any(test.rows[("L", r)] != ref.rows[("L", r)] for r in (x, y)),
                        "mutation did not fail the pair identity")
                rejected += 1
    return rejected


def verify():
    word, programs, checks = load_inputs()
    require(word["v"] == 112 and word["R"] == 504, "selected X4 dimensions")
    require({int(k): v for k, v in word["local_profile"].items()} == PROFILE, "selected profile")
    ps = pairs(word)
    results = {}
    for orientation in ("forward", "backward"):
        results[orientation] = run_orientation(word, programs[orientation], checks[orientation], ps,
                                               orientation == "backward")
    return dict(status="PASS_X4_PRECONDITION_SEED22", assignment_seed=22,
                base_commit="f567884aeb8851b6e794af1184119a3bfbe1e631",
                archive_sha256=ARCHIVE_SHA, payload_sha256=PAYLOADS, pair_count=len(ps),
                pairs=ps, orientations=results, rejected_instruction_mutants=controls(ps),
                per_pair_per_component={"retained_horner": 11, "gatewise_conjugation": 6,
                                        "fused": 4},
                saved_vs_gatewise_conjugation_real_primitives_per_orientation=224,
                new_kappa_claim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = verify()
    # JSON normalizes tuples and integer dictionary keys.
    result = json.loads(json.dumps(result))
    if args.check:
        require(result == json.loads(args.check.read_text()), "result certificate differs")
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], "pairs=56 columns=737x2 saved=784/784 controls=672 no_new_kappa")


if __name__ == "__main__":
    main()
