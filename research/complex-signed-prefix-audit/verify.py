#!/usr/bin/env python3
"""Exact signed-prefix audit of the unchanged selected PR1094 local words.

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
Uses the credited Lemma G conjugation invariant; imports no predecessor code.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MANIFEST = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
LOCAL_CHECKER = "research/complex-sw4-frame8/local/hpe_audit_local.py"
INVOICE = "research/gauge44-slots-t16/code/invoice_allcold.py"
BASE = "candidate/strict/global/base/providers/gauge44/"
INPUTS = {ARCHIVE, MANIFEST, LOCAL_CHECKER, INVOICE,
          "research/e8-lemma-g-lean/PROOF.md", "research/hyperplane-end-lean/PROOF.md"}


class AuditError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise AuditError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def pins(root=ROOT):
    source = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [x for x in source["files"] if x["usage"] == "input"]
    need(len(live) == len(INPUTS) and {x["path"] for x in live} == INPUTS,
         "mandatory source inventory")
    for item in live:
        need(digest((root / item["path"]).read_bytes()) == item["sha256"],
             "source hash: " + item["path"])
    selected = json.loads((root / MANIFEST).read_text())["files"]
    need(selected[INVOICE] == digest((root / INVOICE).read_bytes()), "selected invoice binding")
    need(selected["research/complex-sw4-frame8/local/hpe_audit_local.py"]
         == digest((root / LOCAL_CHECKER).read_bytes()), "selected local checker binding")
    return {x["path"]: x["sha256"] for x in live}


def load(root=ROOT):
    hashes = pins(root)
    with tarfile.open(root / ARCHIVE) as archive:
        def raw(name):
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), "unique regular archive member")
            return archive.extractfile(matches[0]).read()
        def read(name):
            b = raw(name)
            return json.loads(gzip.decompress(b) if name.endswith(".gz") else b)
        word = read(BASE + "CANONICAL-WORD.json.gz")
        programs = read(BASE + "LOCAL-PROGRAMS.json.gz")
        retained = read(BASE + "INDEPENDENT-LOCAL-REPLAY.json")
        checks = read(BASE + "LOCAL-CHECKS.json")
        template = read("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz")
        global_prefix = read("candidate/strict/global/audit/GLOBAL-PREFIX.json")
        payload = gzip.decompress(raw("candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz"))
        need(digest(payload) == global_prefix["template_sha256"], "global template binding")
        need(set(template["local_providers"]) == {"gauge44"}, "selected provider set")
        reg = template["local_providers"]["gauge44"]
        for name, field in [("CANONICAL-WORD.json.gz", "canonical_word_sha256"),
                            ("LOCAL-PROGRAMS.json.gz", "local_programs_sha256")]:
            need(digest(raw(BASE + name)) == retained[field], "local receipt source binding")
        need(reg["canonical_word_sha256"] == retained["canonical_word_sha256"], "provider word")
        need(programs == reg["local_programs"] and checks == reg["local_program_checks"],
             "provider programs/checks")
        need(set(programs) == {"forward", "backward"}, "two orientations")
        for name, events in programs.items():
            ph = digest(json.dumps(events, separators=(",", ":")).encode())
            need(ph == checks[name]["sha256"], "program hash")
            calls = [c for c in template["calls"] if c["orientation"] == name]
            need(calls and all(c["local_program_sha256"] == ph and c["provider_id"] == "gauge44"
                               for c in calls), "all invocation program bindings")
        counts = Counter(e["kind"] for e in template["execution_schedule"])
        need(len(template["calls"]) == counts["local_cover_sweep"]
             == global_prefix["complete_invocation_cover_sweeps"] == 144, "invocation count")
        need(counts["bridge"] == global_prefix["bridge_factor_two_sweeps"] == 144, "bridge count")
        need((word["v"], word["R"], word["h"]) == (112, 480, 9), "selected dimensions")
        return word, programs, retained, checks, global_prefix, hashes


def coefficient(a, b):
    need(type(a) is int and type(b) is int and a != 0 and b != 0, "nonzero rational")
    q = Q(a, b)
    need(q.denominator & (q.denominator - 1) == 0, "dyadic coefficient")
    return q


def row_record(row):
    return [[j, q.numerator, q.denominator] for j, q in sorted(row.items())]


def l1(row):
    return sum(map(abs, row.values()), Q(0))


def strict_bits(value):
    need(value > 0, "positive norm")
    k = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    while value >= 2 ** k:
        k += 1
    need(value < 2 ** k and (k == 0 or value >= Q(2) ** (k - 1)), "strict bit boundary")
    return k


class DenseDyadic:
    """Independent integer rows; updates and reductions do not use Fraction."""
    def __init__(self, n):
        self.n = n
        self.rows = {("L", j): (tuple(int(k == j) for k in range(n)), 0) for j in range(n)}

    def normalize(self, nums, exponent):
        nonzero = [abs(x) for x in nums if x]
        if not nonzero:
            return (0,) * self.n, 0
        shift = min(exponent, min((x & -x).bit_length() - 1 for x in nonzero))
        return tuple(x >> shift for x in nums), exponent - shift

    def step(self, op):
        tag, target = op[0], tuple(op[1])
        if tag == "clear":
            self.rows[target] = ((0,) * self.n, 0)
        elif tag == "copy":
            self.rows[target] = self.rows[tuple(op[2])]
        elif tag in ("scale", "add"):
            a, b = op[-2:]
            if b < 0:
                a, b = -a, -b
            need(b > 0 and b & (b - 1) == 0, "dense dyadic denominator")
            shift = b.bit_length() - 1
            if tag == "scale":
                row, exponent = self.rows[target]
                self.rows[target] = self.normalize([a * x for x in row], exponent + shift)
            else:
                row, exponent = self.rows.get(target, ((0,) * self.n, 0))
                src, sexp = self.rows[tuple(op[2])]
                dest_exp = max(exponent, sexp + shift)
                nums = [(x << (dest_exp - exponent)) + a * (y << (dest_exp - sexp - shift))
                        for x, y in zip(row, src)]
                self.rows[target] = self.normalize(nums, dest_exp)
        else:
            raise AuditError("dense unknown scalar")

    def compare(self, target, sparse):
        nums, exponent = self.rows[target]
        need(sum(x != 0 for x in nums) == len(sparse), "dense/sparse support")
        scale = 1 << exponent
        need(all(nums[j] * value.denominator == value.numerator * scale
                 for j, value in sparse.items()), "dense/sparse row")


def audit(word, events, name, crosscheck=True):
    n = 2 * word["v"] + word["R"]
    rows = {("L", j): {j: Q(1)} for j in range(n)}
    envelope = {("L", j): Q(1) for j in range(n)}
    dense = DenseDyadic(n) if crosscheck else None
    cur, private = list(word["start"]), {}
    wrapped = {j for j in range(2 * word["v"], n)
               if word["start"][j] != 0 or word["final"][j] != 1}
    pre, post, entry, exit_ = set(), set(), set(), set()
    phase, witness = None, None
    scalar_count = wrapper_units = 0
    peak = ordinary = work_peak = positive = Q(1)
    trace, phase_peaks, phases = hashlib.sha256(), {}, []

    def observe(value, i, kind, register, row):
        nonlocal peak, witness
        if value > peak:
            peak = value
            witness = dict(event_index=i, kind=kind, register=list(register), phase=phase,
                           l1=str(value), row=row_record(row))
        phase_peaks[phase] = max(phase_peaks.get(phase, Q(1)), value)

    def frame(reg, f, target=False):
        if reg[0] == "L":
            need(0 <= reg[1] < n and cur[reg[1]] == f, "common scalar frame")
            if reg[1] in wrapped:
                need(reg[1] in pre and reg[1] not in post, "scalar outside wrapper interval")
        else:
            need(reg[0] == "C" and 0 <= reg[1] < len(word["centers"]), "private namespace")
            if target and reg not in private:
                need(not rows.get(reg), "unlabelled nonzero private row")
                private[reg] = f
            need(private.get(reg) == f, "private common frame")

    for i, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            phase = event[1]
            phases.append(phase)
            phase_peaks[phase] = max([Q(1)] + [l1(row) for row in rows.values()])
        elif tag == "adapter":
            _, direction, r, f = event
            if direction == "old_to_new":
                need(phase == "entry_adapters" and r not in wrapped and r not in entry
                     and f == word["start"][r], "entry adapter")
                entry.add(r)
            else:
                need(direction == "new_to_old" and phase == "exit_adapters" and r not in exit_
                     and f == word["final"][r] and (r < 2 * word["v"] or f == 1), "exit adapter")
                exit_.add(r)
        elif tag == "residual_adapter":
            _, direction, r, f, *end = event
            need(r in wrapped and f == word["start"][r], "wrapper role and entrance")
            need(end == ([word["final"][r]] if word["final"][r] != 1 else []), "wrapper terminal pair")
            need(rows["L", r] == {r: Q(1)}, "wrapper unit row")
            wrapper_units += 1
            if direction == "pre":
                need(phase == "entry_adapters" and r not in pre, "pre wrapper placement")
                pre.add(r)
            else:
                need(direction == "post" and phase == "full_frame_cleanup" and r in pre
                     and r not in post and cur[r] == word["final"][r], "post wrapper placement")
                post.add(r)
        elif tag == "climb":
            _, part, r, a, b, rank = event
            need(phase == part and cur[r] == a and rank > 0, "climb label transition")
            cur[r] = b
        elif tag == "center":
            _, k, a, b, rank = event
            need(phase == "centers" and private.get(("C", k)) == a and rank > 0,
                 "centre label transition")
            private["C", k] = b
        elif tag == "scalar":
            _, op, f = event
            kind, target = op[0], tuple(op[1])
            source = tuple(op[2]) if kind in ("add", "copy") else None
            if kind == "clear" and target[0] == "C":
                need(private.get(target, f) == f, "private clear frame")
                private.pop(target, None)
            else:
                frame(target, f, target=True)
                if source is not None:
                    frame(source, f)
            if kind == "clear":
                rows[target], envelope[target] = {}, Q(0)
            elif kind == "copy":
                rows[target], envelope[target] = rows[source].copy(), envelope[source]
            elif kind == "scale":
                q = coefficient(op[2], op[3])
                a = abs(q.numerator)
                need(a & (a - 1) == 0, "power-of-two scale")
                rows[target] = {j: q * x for j, x in rows[target].items()}
                envelope[target] *= abs(q)
            elif kind == "add":
                need(source != target, "coefficient source alias")
                q = coefficient(op[3], op[4])
                numerator = abs(q.numerator)
                # Every unsigned-Horner/halving intermediate is k times this
                # source row, with 0 <= k <= numerator (PROOF.md).
                work = {j: numerator * x for j, x in rows[source].items()}
                wnorm = l1(work)
                work_peak = max(work_peak, wnorm)
                observe(wnorm, i, "coefficient_numerator", source, work)
                positive = max(positive, numerator * envelope[source])
                envelope[target] = envelope.get(target, Q(0)) + abs(q) * envelope[source]
                row = rows.setdefault(target, {})
                for j, x in rows[source].items():
                    value = row.get(j, Q(0)) + q * x
                    if value:
                        row[j] = value
                    else:
                        row.pop(j, None)
            else:
                raise AuditError("unknown scalar")
            if dense is not None:
                dense.step(op)
                dense.compare(target, rows[target])
            scalar_count += 1
            rnorm = l1(rows[target])
            ordinary, positive = max(ordinary, rnorm), max(positive, envelope[target])
            observe(rnorm, i, "register", target, rows[target])
            trace.update(canonical([i, op, row_record(rows[target]), str(rnorm)]))
        else:
            raise AuditError("unknown event")
    need(phases == ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
                    "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"],
         "phase sequence")
    need(cur == word["final"] and not private, "final labels/private state")
    need(pre == post == wrapped and entry == set(range(n)) - wrapped, "complete wrappers/entry")
    need(exit_ == {j for j in range(n) if j < 2 * word["v"] or word["final"][j] == 1},
         "complete exit adapters")
    for j in range(n):
        expected = {j: Q(1)}
        if name == "forward" and word["v"] <= j < 2 * word["v"]:
            expected[j - word["v"]] = Q(1)
        elif name == "backward" and j < word["v"]:
            expected[j + word["v"]] = Q(-1)
        need(rows["L", j] == expected, "scalar endpoint")
    need(all(not row for reg, row in rows.items() if reg[0] == "C"), "private zero endpoints")
    need(witness is not None, "nontrivial peak")
    # Real/imaginary or coordinatewise execution can temporarily combine
    # parts of two consecutive complex states. Orthogonal projection gives
    # ||P v + (I-P) u||^2 <= ||v||^2 + ||u||^2 <= 2 * peak^2.
    split_squared = 2 * peak * peak
    split_bits = strict_bits(peak)
    while split_squared >= 2 ** (2 * split_bits):
        split_bits += 1
    return dict(events=len(events), scalar_prefixes=scalar_count, persistent_columns=n,
                common_frame_checks=True, wrapper_unit_rows=wrapper_units,
                exact_peak=str(peak), register_peak=str(ordinary), coefficient_peak=str(work_peak),
                strict_bits=strict_bits(peak), positive_envelope=str(positive),
                split_component_squared_bound=str(split_squared), split_component_bits=split_bits,
                positive_strict_bits=strict_bits(positive), peak_witness=witness,
                prefix_row_trace_sha256=trace.hexdigest(),
                phase_peaks={k: str(v) for k, v in phase_peaks.items()}, dense_integer_crosscheck=crosscheck)


def adjoint_witness(events, witness):
    """Pull one observed functional back, independently of forward row replay."""
    stop, reg = witness["event_index"], tuple(witness["register"])
    if witness["kind"] == "coefficient_numerator":
        op = events[stop][1]
        functional = {reg: Q(abs(coefficient(op[3], op[4]).numerator))}
        prefix = events[:stop]
    else:
        functional, prefix = {reg: Q(1)}, events[:stop + 1]
    for event in reversed(prefix):
        if event[0] != "scalar":
            continue
        op, target = event[1], tuple(event[1][1])
        weight = functional.get(target, Q(0))
        if not weight:
            continue
        if op[0] == "clear":
            functional.pop(target)
        elif op[0] == "scale":
            functional[target] *= Q(op[2], op[3])
        else:
            source = tuple(op[2])
            if op[0] == "copy":
                functional.pop(target)
                q = Q(1)
            else:
                q = Q(op[3], op[4])
            value = functional.get(source, Q(0)) + q * weight
            if value:
                functional[source] = value
            else:
                functional.pop(source, None)
    need(all(reg[0] == "L" for reg in functional), "witness depends on private initial input")
    row = {reg[1]: x for reg, x in functional.items()}
    need(row_record(row) == witness["row"], "reverse functional witness")
    return row


def literal_witness(events, witness, n):
    """Run every unsigned-Horner primitive numerically on the attaining input."""
    row = adjoint_witness(events, witness)
    state = {("L", j): Q((row.get(j, 0) > 0) - (row.get(j, 0) < 0)) for j in range(n)}
    peak, observed, primitives = Q(1), None, 0

    def touch(value):
        nonlocal peak, primitives
        peak = max(peak, abs(value))
        primitives += 1

    for i, event in enumerate(events):
        if event[0] != "scalar":
            continue
        op, target = event[1], tuple(event[1][1])
        if op[0] == "clear":
            state[target] = Q(0)
            touch(state[target])
        elif op[0] == "copy":
            state[target] = state[tuple(op[2])]
            touch(state[target])
        elif op[0] == "scale":
            q = Q(op[2], op[3])
            for _ in range(abs(q.numerator).bit_length() - 1):
                state[target] *= 2
                touch(state[target])
            for _ in range(q.denominator.bit_length() - 1):
                state[target] /= 2
                touch(state[target])
            if q < 0:
                state[target] = -state[target]
                touch(state[target])
        else:
            q, source = Q(op[3], op[4]), state[tuple(op[2])]
            work = Q(0)
            touch(work)
            for j, bit in enumerate(bin(abs(q.numerator))[2:]):
                if j:
                    work *= 2
                    touch(work)
                if bit == "1":
                    work += source
                    touch(work)
            if i == witness["event_index"] and witness["kind"] == "coefficient_numerator":
                observed = work
            for _ in range(q.denominator.bit_length() - 1):
                work /= 2
                touch(work)
            state[target] = state.get(target, Q(0)) + (work if q > 0 else -work)
            touch(state[target])
            work = Q(0)
            touch(work)
        if i == witness["event_index"] and witness["kind"] == "register":
            observed = state[tuple(witness["register"])]
    need(observed == Q(witness["l1"]) == peak, "attaining primitive witness")
    return dict(input_nonzero=len(row), input_sup=1, observed=str(observed), primitive_peak=str(peak),
                real_component_primitives=2 * primitives, reverse_functional_matches=True)


def result(root=ROOT):
    word, programs, retained, checks, global_prefix, hashes = load(root)
    reports = {}
    for name in ("forward", "backward"):
        report = audit(word, programs[name], name)
        old = retained["local"][name]
        need(report["positive_envelope"] == old["prefix_l1_upper"]
             and report["positive_strict_bits"] == old["prefix_bits_upper"], "positive-envelope comparison")
        witness = literal_witness(programs[name], report["peak_witness"], report["persistent_columns"])
        need(witness["real_component_primitives"] == checks[name]["real_component_primitive_bound"],
             "primitive recount matches source")
        report["attainment"] = witness
        reports[name] = report
    local = max(r["split_component_bits"] for r in reports.values())
    oldlocal = max(r["positive_strict_bits"] for r in reports.values())
    need(oldlocal == global_prefix["local_scalar_coefficient_work_prefix_bits"], "retained local bound")
    rest = sum(global_prefix[k] for k in ["stream_input_sup_to_l2_bits", "complete_invocation_cover_sweeps",
                                         "bridge_factor_two_sweeps", "primitive_arithmetic_margin_bits"])
    need(oldlocal + rest == global_prefix["global_prefix_bits"], "retained global arithmetic")
    return dict(status="PASS_COMPLEX_SIGNED_PREFIX_AUDIT", source_sha256=hashes, orientations=reports,
                conditional_global=dict(old_local_bits=oldlocal, signed_local_bits=local,
                                        unchanged_other_allowances=rest, old_sufficient_bits=oldlocal + rest,
                                        signed_sufficient_bits=local + rest,
                                        retained_payload_bits=global_prefix["retained_payload_bits"]),
                scope="Exact scalar/Horner prefix and conditional unitary common-frame norm corollary. "
                      "Recursive child internals, physical compiler/hosting, roundoff, native admission "
                      "and analytic transfer remain inherited. No production payload or kappa change.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write checked receipt to a new path")
    args = parser.parse_args()
    receipt = result()
    need(receipt == json.loads((PACKAGE / "EXPECTED.json").read_text()), "committed receipt mismatch")
    if args.output:
        with args.output.open("x") as handle:
            handle.write(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], "local_bits=52,68->18,21",
          "conditional_global_bits=397->350 payload=512 kappa=unchanged",
          "receipt_sha256=" + digest(canonical(receipt)))


if __name__ == "__main__":
    main()
