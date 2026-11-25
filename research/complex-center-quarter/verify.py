#!/usr/bin/env python3
"""Factor copied-center quarter coefficients; exact, offline finite verification.

Prepared for @ssteeper with substantial OpenAI Codex assistance. Apache-2.0.
The retained emitter and native auditor are credited in README.md.
"""

import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
SELECTED = "certificates/selected-result.json"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
INVENTORY = "research/community-k492-audit/SELECTED-SOURCE.json"
AUDITOR = "research/complex-sw4-frame8/local/hpe_audit_local.py"
EMITTER = "research/complex-k492-owner-repair/code/hpe_emit_local.py"
INVOICE = "research/complex-k492-owner-repair/code/invoice_allcold.py"
REPLAY = "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
PROVIDERS = ("jp8", "ck")  # Seed 35 selects JP8 first.
W = ("W", 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def read(path):
    return json.loads(payload(path))


def check_sources():
    pins = read(HERE / "SOURCES.json")
    require(pins["base_commit"] == BASE, "base pin")
    for rel, pin in pins["files"].items():
        path = (ROOT / rel).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), "invalid source path")
        require(pin["mode"] in ("bytes", "decompressed"), "unknown source pin mode")
        data = payload(path) if pin["mode"] == "decompressed" else path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin: " + rel)
    selection = read(ROOT / SELECTED)
    spec = read(ROOT / SPEC)
    inventory = read(ROOT / INVENTORY)
    require(selection["kappa"] == "51110230636731/31250000000000000", "selected kappa")
    require(selection["source_manifest"] == INVENTORY, "selected inventory link")
    require(selection["audited_source_head"] == pins["reviewed_heads"]["626"], "selected head")
    for pr, head in pins["reviewed_heads"].items():
        require(selection["reviewed_dependency_heads"][pr] == head, "reviewed head: " + pr)
    inventory_keys = {
        SPEC: SPEC,
        AUDITOR: "research/complex-k492-owner-repair/code/hpe_audit_local.py",
        EMITTER: EMITTER,
        INVOICE: INVOICE,
    }
    for rel in (SPEC, AUDITOR, EMITTER, INVOICE):
        require(inventory["files"][inventory_keys[rel]] == pins["files"][rel]["sha256"],
                "inventory pin: " + rel)
    for name in PROVIDERS:
        desc = spec["providers"][name]
        for filename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            rel = f"{REPLAY}/{name}/{filename}"
            require(desc["artifact_semantic_sha256"][filename] == pins["files"][rel]["sha256"],
                    "SPEC artifact binding")
        programs = read(ROOT / REPLAY / name / "LOCAL-PROGRAMS.json.gz")
        require({d: digest(es) for d, es in programs.items()} == desc["program_hashes"],
                "SPEC program binding")
    return spec


def center_blocks(events):
    """Parse the complete selected center phase, refusing other event shapes."""
    start = events.index(["phase", "centers"]) + 1
    stop = next(i for i in range(start, len(events)) if events[i][0] == "phase")
    phase = events[start:stop]
    require(len(phase) == 8 * 32, "eight 32-event reference center blocks required")
    return start, stop, [phase[i:i + 32] for i in range(0, len(phase), 32)]


def transform(events, backward):
    start, stop, blocks = center_blocks(events)
    replacement, recipes = [], []
    for k, block in enumerate(blocks):
        center = ["C", k]
        child_indices = [i for i, e in enumerate(block) if e[0] == "center"]
        require(len(child_indices) == 1, "one paid center child")
        ci = child_indices[0]
        child = block[ci]
        require(child[1] == k and child[4] == 8, "center index/rank")
        require(child[2 if backward else 3] == 0, "center child meets zero frame")
        require(ci == (29 if backward else 2), "reference center chronology")
        require(block[-1] == ["scalar", ["clear", center], child[3]], "terminal center clear")
        require(block[0] == ["scalar", ["clear", center], child[2]], "initial center clear")
        if backward:
            exit_add = block[-2]
            require(exit_add[0] == "scalar" and exit_add[2] == child[3]
                    and exit_add[1][0] == "add" and exit_add[1][2:] == [center, -1, 1],
                    "backward center subtraction")
        else:
            require(block[1][0] == "scalar" and block[1][1][:2] == ["copy", center]
                    and block[1][2] == child[2], "forward center source copy")
        changed = copy.deepcopy(block)
        taps = changed[1:29] if backward else changed[3:31]
        require(len(taps) == 28, "28 center taps")
        for e in taps:
            require(e[0] == "scalar" and e[2] == 0 and e[1][0] == "add", "zero-frame tap")
            op = e[1]
            require(op[1 if backward else 2] == center and op[3] in (-1, 1) and op[4] == 4,
                    "signed quarter coefficient")
            other = op[2 if backward else 1]
            require(other[0] == "L" and 112 <= other[1] < 224, "target port tap")
            op[4] = 1
        insertion = ci if backward else ci + 1
        changed.insert(insertion, ["scalar", ["scale", center, 1, 4], 0])
        replacement.extend(changed)
        recipes.append({"center": k, "reference_start": start + 32 * k,
                        "tap_count": 28, "negative_taps": sum(e[1][3] < 0 for e in taps),
                        "paid_child": child, "scale_frame": 0,
                        "scale_position": "before_child" if backward else "after_child"})
    result = copy.deepcopy(events[:start]) + replacement + copy.deepcopy(events[stop:])
    require([e for e in events if e[0] != "scalar"] == [e for e in result if e[0] != "scalar"],
            "paid events or wrappers changed")
    return result, recipes


def lower(op):
    """Literal original binary-Horner lowering, one real component.

    Work is private and cleared after each add. No #696 or other pending
    lowering is imported. Each yielded instruction costs one primitive.
    """
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        yield ("clear", target)
    elif tag == "copy":
        yield ("copy", target, tuple(op[2]))
    elif tag == "scale":
        q = Q(op[2], op[3])
        a, b = abs(q.numerator), q.denominator
        require(a > 0 and a & (a - 1) == 0 and b & (b - 1) == 0, "dyadic unit scale")
        for _ in range(abs(a.bit_length() - b.bit_length())):
            yield ("double" if a > b else "half", target)
        if q < 0:
            yield ("negate", target)
    else:
        require(tag == "add", "unknown scalar operation")
        source, q = tuple(op[2]), Q(op[3], op[4])
        require(source != target and W not in (source, target), "coefficient work alias")
        a, b = abs(q.numerator), q.denominator
        require(a > 0 and b & (b - 1) == 0, "nonzero dyadic addition")
        yield ("clear", W)
        # Leading digit is added to cleared work, exactly as priced by emitter.
        bits = bin(a)[2:]
        for i, bit in enumerate(bits):
            if i:
                yield ("double", W)
            if bit == "1":
                yield ("plus", W, source)
        for _ in range(b.bit_length() - 1):
            yield ("half", W)
        yield ("plus" if q > 0 else "minus", target, W)
        yield ("clear", W)


def cost_prefix(events):
    """Triangle-inequality envelope, including Horner work, not just endpoints."""
    norms = {("L", r): Q(1) for r in range(716)}
    norms.update({("C", k): Q(1) for k in range(8)})
    peak, primitives, macros = Q(1), 0, 0
    for e in events:
        if e[0] != "scalar":
            continue
        op = e[1]
        primitives += sum(1 for _ in lower(op))
        macros += 1
        tag, t = op[0], tuple(op[1])
        if tag == "clear":
            norms[t] = Q(0)
        elif tag == "copy":
            norms[t] = norms[tuple(op[2])]
        elif tag == "scale":
            norms[t] *= abs(Q(op[2], op[3]))
        else:
            s, q = tuple(op[2]), Q(op[3], op[4])
            peak = max(peak, abs(q.numerator) * norms[s])
            norms[t] += abs(q) * norms[s]
        peak = max(peak, norms[t])
    require(peak < 2 ** 192, "192-bit payload allowance")
    return {"real_primitives": 2 * primitives, "scalar_macros": macros,
            "prefix_l1": str(peak), "prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1}


def apply_primitive(rows, instruction):
    tag, t = instruction[:2]
    if tag == "clear":
        rows[t] = {}
    elif tag == "copy":
        rows[t] = rows[instruction[2]].copy()
    elif tag in ("double", "half", "negate"):
        q = {"double": Q(2), "half": Q(1, 2), "negate": Q(-1)}[tag]
        rows[t] = {j: q * x for j, x in rows[t].items()}
    else:
        require(tag in ("plus", "minus"), "unknown primitive")
        source = instruction[2]
        require(source != t, "aliased primitive")
        sign = 1 if tag == "plus" else -1
        for j, x in rows[source].items():
            value = rows[t].get(j, Q(0)) + sign * x
            if value:
                rows[t][j] = value
            else:
                rows[t].pop(j, None)


def block_map(block):
    regs = set()
    for e in block:
        if e[0] == "scalar":
            op = e[1]
            regs.add(tuple(op[1]))
            if op[0] in ("copy", "add"):
                regs.add(tuple(op[2]))
    regs.add(W)
    rows = {r: {r: Q(1)} for r in regs}
    checkpoints, count = [], 0
    for e in block:
        if e[0] == "center":
            # Child treated as the same formal scalar interface on both sides.
            # Equality of its input is checked, so the rewrite does not commute
            # a scaling past an unknown recursive operation.
            checkpoints.append(rows[("C", e[1])].copy())
        elif e[0] == "scalar":
            for instruction in lower(e[1]):
                apply_primitive(rows, instruction)
                count += 1
    return rows, checkpoints, count


def check_block_pair(original, candidate, backward):
    a, ac, ca = block_map(original)
    b, bc, cb = block_map(candidate)
    require(a == b, "arbitrary-input block boundary differs")
    require(ac == bc, "recursive center input differs")
    require(all(not row for reg, row in b.items() if reg[0] in ("C", "W")), "private output not erased")
    require([e for e in original if e[0] != "scalar"] == [e for e in candidate if e[0] != "scalar"],
            "paid center event differs")
    require(ca - cb == 54, "complete per-component block saving")
    return {"arbitrary_inputs": len(a), "reference_primitives_per_component": ca,
            "candidate_primitives_per_component": cb,
            "recursive_input_digest": digest([[str(j), str(x)] for j, x in sorted(bc[0].items())])}


def full_scalar_replay(events, backward):
    """All 716 persistent and 8 private formal columns; no clean-input premise."""
    regs = [("L", r) for r in range(716)] + [("C", k) for k in range(8)]
    rows = {r: {r: Q(1)} for r in regs}
    for e in events:
        if e[0] != "scalar":
            continue
        op, t = e[1], tuple(e[1][1])
        tag = op[0]
        if tag == "clear":
            rows[t] = {}
        elif tag == "copy":
            rows[t] = rows[tuple(op[2])].copy()
        elif tag == "scale":
            q = Q(op[2], op[3])
            rows[t] = {j: q * x for j, x in rows[t].items()}
        else:
            s, q = tuple(op[2]), Q(op[3], op[4])
            require(t != s, "macro alias")
            for j, x in rows[s].items():
                value = rows[t].get(j, Q(0)) + q * x
                if value:
                    rows[t][j] = value
                else:
                    rows[t].pop(j, None)
    for r in range(716):
        expected = {("L", r): Q(1)}
        if backward and r < 112:
            expected[("L", r + 112)] = Q(-1)
        elif not backward and 112 <= r < 224:
            expected[("L", r - 112)] = Q(1)
        require(rows[("L", r)] == expected, "full scalar boundary: " + str(r))
    require(all(not rows[("C", k)] for k in range(8)), "full private-center clearing")
    return {"input_columns": 724, "persistent_outputs": 716, "private_outputs": 8,
            "dirty_helpers_restored": 492}


def controls(reference, candidate, backward):
    """Seed-selected center 3; each rejected defect has a mathematical cause."""
    start, _, blocks = center_blocks(reference)
    old = blocks[3]
    new = candidate[start + 33 * 3:start + 33 * 4]
    rejected = []

    def reject(label, mutate):
        bad = copy.deepcopy(new)
        mutate(bad)
        try:
            check_block_pair(old, bad, backward)
        except (ValueError, KeyError):
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)

    si = next(i for i, e in enumerate(new) if e[0] == "scalar" and e[1][0] == "scale")
    ti = next(i for i, e in enumerate(new) if e[0] == "scalar" and e[1][0] == "add")
    reject("omitted_quarter_scale", lambda b: b.pop(si))
    reject("wrong_quarter_scale", lambda b: b[si][1].__setitem__(3, 2))
    reject("wrong_tap_sign", lambda b: b[ti][1].__setitem__(3, -b[ti][1][3]))
    reject("omitted_terminal_clear", lambda b: b.pop())
    reject("omitted_paid_center", lambda b: b.pop(next(i for i, e in enumerate(b) if e[0] == "center")))
    if backward:
        reject("omitted_initial_dirty_center_clear", lambda b: b.pop(0))
        # Endpoint is unchanged, but the call receives 4 times its specified input.
        def after_child(b):
            scale = b.pop(si)
            ci = next(i for i, e in enumerate(b) if e[0] == "center")
            b.insert(ci + 1, scale)
        reject("scale_after_recursive_gather", after_child)
    else:
        reject("omitted_source_copy", lambda b: b.pop(1))
        def before_child(b):
            scale = b.pop(si)
            ci = next(i for i, e in enumerate(b) if e[0] == "center")
            b.insert(ci, scale)
        reject("scale_before_recursive_scatter", before_child)
    # The final coefficient-work clear is required even when native endpoints
    # have the correct values. Execute a literal dirty-work basis column.
    tap = new[ti][1]
    lowered = list(lower(tap))
    regs = {tuple(tap[1]), tuple(tap[2]), W}
    a = {r: {r: Q(1)} for r in regs}
    for op in lowered[:-1]:
        apply_primitive(a, op)
    require(a[W], "missing-work-clear control must leave a nonzero private row")
    rejected.append("omitted_coefficient_work_clear")
    return rejected


def run_native(canonical, programs):
    """Run the pinned, unchanged frame/wrapper auditor with assertions enabled."""
    with tempfile.TemporaryDirectory(prefix="center-quarter-") as tmp:
        out = Path(tmp).resolve()
        require(out.is_relative_to(Path(tempfile.gettempdir()).resolve()) and out.name.startswith("center-quarter-"),
                "native scratch directory must be inside the temporary root")
        (out / "CANONICAL-WORD.json.gz").write_bytes(gzip.compress(json.dumps(canonical).encode(), mtime=0))
        (out / "LOCAL-PROGRAMS.json.gz").write_bytes(gzip.compress(json.dumps(programs).encode(), mtime=0))
        proc = subprocess.run([sys.executable, "-I", "-B", str(ROOT / AUDITOR), str(out)],
                              capture_output=True, text=True, timeout=240)
        require(proc.returncode == 0, "native audit failed:\n" + proc.stdout + proc.stderr)
        result = read(out / "INDEPENDENT-LOCAL-REPLAY.json")
        return {"status": result["status"], "paid_profiles": result["paid_profiles"],
                "local": result["local"], "negative_controls_rejected": result["negative_controls_rejected"]}


def price_local(canonical, programs, contract):
    """Complete conservative local bound of the *literal* macro rewrite.

    The eight extra scales increase the generic adapter allowance. This is
    deliberately recorded as a cost regression, not hidden behind scalar
    savings. No global admission or a cheaper grouped-macro rule is assumed.
    """
    children = sum(canonical["local_profile"].values())
    n = 2 * canonical["v"] + canonical["R"]
    centres = len(canonical["centers"])
    m = 73  # The pinned invoice's fixed local compiler parameter.
    compiler = 64 * (m + 1) ** 3
    prices = {"compiler": compiler, "children": children, "native_registers": n, "centres": centres}
    for variant in ("original", "factored"):
        macros = max(p[variant]["scalar_macros"] for p in programs.values())
        scalar = max(p[variant]["real_primitives"] for p in programs.values())
        adapters = 16 * (macros + children + n + centres) + 64 * m
        prices[variant] = {"scalar_worst_orientation": scalar, "macro_bound": macros,
                           "local_adapters": adapters, "local_primitive_bound": scalar + adapters * compiler}
    for key in ("compiler", "children"):
        require(prices[key] == contract[key], "original complete contract: " + key)
    for key in ("local_adapters", "local_primitive_bound"):
        require(prices["original"][key] == contract[key], "original local invoice: " + key)
    prices["adapter_allowance_increase"] = prices["factored"]["local_adapters"] - prices["original"]["local_adapters"]
    prices["bound_increase"] = prices["factored"]["local_primitive_bound"] - prices["original"]["local_primitive_bound"]
    require(prices["adapter_allowance_increase"] == 128 and prices["bound_increase"] == 3319594144,
            "extra-macro cost must be charged")
    require(prices["factored"]["local_primitive_bound"] < 2**48, "inherited local bound cap")
    prices["scope"] = "Scalar circuit improves; literal generic local invoice worsens; no global invoice or kappa gain."
    return prices


def verify():
    spec = check_sources()
    result = {"status": "PASS_COMPLEX_CENTER_QUARTER", "base_commit": BASE,
              "assignment_seed": 35, "kappa": "unchanged", "providers": {}}
    for name in PROVIDERS:
        directory = ROOT / REPLAY / name
        canonical = read(directory / "CANONICAL-WORD.json.gz")
        programs = read(directory / "LOCAL-PROGRAMS.json.gz")
        local_checks = read(directory / "LOCAL-CHECKS.json")
        inherited = read(directory / "INDEPENDENT-LOCAL-REPLAY.json")
        changed, outputs = {}, {}
        for direction in ("forward", "backward"):
            events = programs[direction]
            backward = direction == "backward"
            modified, recipes = transform(events, backward)
            start, _, blocks = center_blocks(events)
            block_checks = [check_block_pair(old, modified[start + 33*k:start + 33*(k+1)], backward)
                            for k, old in enumerate(blocks)]
            before, after = cost_prefix(events), cost_prefix(modified)
            require(before["real_primitives"] == local_checks[direction]["real_component_primitive_bound"],
                    "reference cost binding")
            require(before["prefix_l1"] == inherited["local"][direction]["prefix_l1_upper"], "reference prefix binding")
            require(before["prefix_l1"] == after["prefix_l1"], "prefix envelope changed")
            require(before["real_primitives"] - after["real_primitives"] == 864, "complete saving")
            require(before["scalar_macros"] + 8 == after["scalar_macros"], "eight charged scales")
            full_scalar_replay(events, backward)
            scalar_check = full_scalar_replay(modified, backward)
            changed[direction] = modified
            outputs[direction] = {"original": before, "factored": after, "saved_real_primitives": 864,
                                  "program_sha256": digest(modified), "recipes": recipes,
                                  "blocks": block_checks, "full_scalar_replay": scalar_check,
                                  "controls": controls(events, modified, backward)}
        native = run_native(canonical, changed)
        for direction in changed:
            require(native["paid_profiles"][direction] == spec["providers"][name]["expected_profile"], "paid profile")
            require(native["local"][direction]["prefix_l1_upper"] == outputs[direction]["factored"]["prefix_l1"],
                    "native prefix agreement")
        local_price = price_local(canonical, outputs, spec["providers"][name]["complete_contract"])
        result["providers"][name] = {"programs": outputs, "native": native, "complete_local_price": local_price}
        print("verified", name, "forward/backward: saving 864 each; native frames/wrappers pass", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="create a new receipt; refuses to overwrite")
    args = parser.parse_args()
    if args.write_receipt:
        require(not args.write_receipt.exists(), "receipt output already exists")
    result = verify()
    if args.write_receipt:
        with args.write_receipt.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        require(result == read(HERE / "EXPECTED.json"), "receipt mismatch")
    print("PASS_COMPLEX_CENTER_QUARTER programs=4 centers=32 saving=864_each columns=724 controls=32+50 invoice_delta=+3319594144 kappa=unchanged")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError) as error:
        raise SystemExit("FAIL: " + str(error)) from error
