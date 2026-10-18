#!/usr/bin/env python3
"""PR2157 binary-call widths at PR2972's later-stage cutoff boundary.

Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
The address oracle is independent; the router is authenticated predecessor code.
"""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTER = "research/selected-bit-stream-routes/qadic_streams.py"
STOCK = "research/selected-bootstrap-stock-audit/RESULT.json"
CASES = tuple((q, w) for q, widths in
              ((3, range(1, 5)), (5, range(1, 4)), (7, range(1, 4)),
               (11, range(1, 3)), (17, range(1, 3)), (31, range(1, 3)))
              for w in widths)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pinned_inputs(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (root / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source hash mismatch: " + row["path"])
            result[row["path"]] = raw
    return result


def router_from_bytes(raw):
    # Compile authenticated bytes, preventing a stale .pyc from replacing them.
    name = "_qadic_width_audit_predecessor"
    module = types.ModuleType(name)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        exec(compile(raw, ROUTER, "exec"), module.__dict__)
    finally:
        if previous is None:
            del sys.modules[name]
        else:
            sys.modules[name] = previous
    return module


def ceil_log2(n):
    require(type(n) is int and n >= 1, "positive integer log domain")
    # Different implementation from the predecessor's bit_length expression.
    power, result = 1, 0
    while power < n:
        power *= 2
        result += 1
    return result


def radix_width(radix, size):
    power, width = 1, 0
    while power < size:
        power *= radix
        width += 1
    return width


def payload(q, w):
    high, before, middle = q ** (w - 1), 2, 3
    records = before * high * middle * high
    suffix = max(1, ceil_log2(records))
    # Distinct complete bit records label every coordinate tuple.
    raw = [(address >> bit) & 1 for address in range(records)
           for bit in range(suffix)]
    return high, before, middle, suffix, raw


def destination_oracle(raw, q, w, before, middle, suffix, operation):
    """Forward scatter versus the router's padded inverse-index gather."""
    high, modulus = q ** (w - 1), q ** w
    output = [None] * len(raw)
    residue = -pow(2, -1, modulus)
    for a in range(before):
        for x in range(high):
            for z in range(middle):
                for y in range(high):
                    if operation == "swap":
                        new_x, new_y = y, x
                    else:
                        source, target = ((y, x) if operation == "reverse_add"
                                          else (x, y))
                        full = (q * target + residue * (q - 1 + q * source)) % modulus
                        updated = full // q
                        new_x, new_y = ((updated, source) if operation == "reverse_add"
                                        else (source, updated))
                    start = (((a * high + x) * middle + z) * high + y) * suffix
                    end = (((a * high + new_x) * middle + z) * high + new_y) * suffix
                    require(output[end] is None, "independent destination collision")
                    output[end:end + suffix] = raw[start:start + suffix]
    require(None not in output, "independent destination omission")
    return output


def packet_case(router, q, w, operation, omit_carry=False):
    high, before, middle, suffix, raw = payload(q, w)
    meter = router.Meter()
    source = router.Tape(meter, raw)
    if operation == "swap":
        actual = router.completed_swap_oracle(source, high, before, middle, suffix)
        count = int(w > 1)
    else:
        actual, low = router.physical_add(
            source, q, w, q - 1, 0, Fraction(-1, 2), before, middle, suffix,
            reversed_fields=operation == "reverse_add", omit_carry=omit_carry)
        require(low == (-(q - 1) * pow(2, -1, q)) % q, "low endpoint")
        count = 2 * int(w > 1 and operation == "reverse_add")
    expected = destination_oracle(raw, q, w, before, middle, suffix, operation)
    require(actual.bits == expected, "complete gapped packet differs: " + operation)
    require(len(meter.ordinary) == count, "ordinary call count")
    u, b = ceil_log2(high), ceil_log2(q)
    t = radix_width(q, 2 ** u)
    if w > 1:
        require(w <= u <= b * (w - 1), "width bound at finite probe")
        require(t == w, "round-trip radix callee width")
    for call in meter.ordinary:
        require(call["binary_width"] == u, "binary width invoice")
        require(call["real_volume"] == len(raw), "real-volume invoice")
        padding = before * (2 ** u) ** 2 * middle * suffix
        require(call["padded_volume"] == padding, "complete padding invoice")
        require(padding < 4 * len(raw), "strict padding ratio")
        require((call["before"], call["middle"], call["suffix"]) ==
                (before, middle, suffix), "complete spectator dimensions")
    return {"q": q, "w": w, "operation": operation, "binary_width": u,
            "radix_callee_width": t,
            "ordinary_calls": count, "payload_bits": len(raw),
            "sha256": hashlib.sha256(bytes(actual.bits)).hexdigest()}


def cutoff_rows(stock):
    rows = []
    for branch, data in stock["branches"].items():
        s, stages = Fraction(data["common_saving"]), data["stages"]
        require(len(stages) == 7 and 0 < s < 1, "inherited stage domain")
        for previous, current in zip(stages, stages[1:]):
            old, new = int(previous["cutoff_log2"]), int(current["cutoff_log2"])
            margin, room = s * new - old, (1 - s) * old
            require(margin >= 1, "atom-width membership premise")
            require(room > 0, "inherited routing room")
            require(current["actual_stock_coefficient"] is None,
                    "do not silently admit an actual reserve coefficient")
            rows.append({"branch": branch, "stage": current["stage"],
                         "inherited_margin_floor": margin.numerator // margin.denominator,
                         "inherited_routing_room_floor": room.numerator // room.denominator,
                         "radix_callee_width": "t=w >= e^s",
                         "radix_upper_factor": 1})
    require(len(rows) == 12, "twelve inherited cutoff pairs")
    return rows


def embed_two_fields(raw, old, new, before, middle, suffix):
    require(new >= old, "padding must contain the whole source rectangle")
    out, cursor = [], 0
    for _ in range(before):
        for x in range(new):
            for _ in range(middle):
                for y in range(new):
                    if x < old and y < old:
                        out.extend(raw[cursor:cursor + suffix])
                        cursor += suffix
                    else:
                        out.extend([0] * suffix)
    require(cursor == len(raw), "complete embedding consumption")
    return out


def unpad_two_fields(raw, old, new, before, middle, suffix):
    out, cursor = [], 0
    for _ in range(before):
        for x in range(new):
            for _ in range(middle):
                for y in range(new):
                    record = raw[cursor:cursor + suffix]
                    cursor += suffix
                    if x < old and y < old:
                        out.extend(record)
                    else:
                        require(not any(record), "completed endpoint must preserve dummy rectangle")
    require(cursor == len(raw), "complete unpadding consumption")
    return out


def roundtrip_case(q, w, truncate=False):
    high, before, middle, suffix, raw = payload(q, w)
    binary = 2 ** ceil_log2(high)
    t = radix_width(q, binary)
    require(high < binary < q ** w and t == w, "strict round-trip brackets")
    outer = embed_two_fields(raw, high, binary, before, middle, suffix)
    target = q ** (t - int(truncate))
    inner = embed_two_fields(outer, binary, target, before, middle, suffix)
    require(len(inner) == q * q * len(raw), "exact q-squared call volume")
    # Declared complete radix-q ordinary endpoint, not a physical kernel.
    swapped = [0] * len(inner)
    for a in range(before):
        for x in range(target):
            for z in range(middle):
                for y in range(target):
                    src = (((a * target + x) * middle + z) * target + y) * suffix
                    dst = (((a * target + y) * middle + z) * target + x) * suffix
                    swapped[dst:dst + suffix] = inner[src:src + suffix]
    outer_return = unpad_two_fields(swapped, binary, target, before, middle, suffix)
    actual = unpad_two_fields(outer_return, high, binary, before, middle, suffix)
    expected = destination_oracle(raw, q, w, before, middle, suffix, "swap")
    require(actual == expected, "two completed embeddings and gapped endpoint")
    return {"q": q, "w": w, "binary_width": ceil_log2(high),
            "radix_callee_width": t, "original_volume": len(raw),
            "callee_volume": len(inner), "sha256": hashlib.sha256(bytes(actual)).hexdigest()}


def must_reject(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def controls(raw):
    good = router_from_bytes(raw)
    must_reject(lambda: packet_case(good, 3, 2, "reverse_add", omit_carry=True),
                "omitted low-to-high carry")
    bad = raw.replace(b"u=(qpower-1).bit_length();power=1<<u",
                      b"u=qpower.bit_length()-1;power=1<<u")
    require(bad != raw, "under-padding mutation reached source")
    must_reject(lambda: packet_case(router_from_bytes(bad), 3, 3, "swap"), "underpad")
    missing = router_from_bytes(raw)
    missing.completed_swap_oracle = lambda source, *args: source
    must_reject(lambda: packet_case(missing, 3, 2, "reverse_add"), "order swaps")
    bad = raw.replace(b'"binary_width":u', b'"binary_width":u-1')
    require(bad != raw, "width-invoice mutation reached source")
    must_reject(lambda: packet_case(router_from_bytes(bad), 3, 2, "swap"), "width invoice")
    require(ceil_log2(257 ** 3) == 25 and 25 > 4, "u=w counterexample")
    require(ceil_log2(257) == 9 and 9 > 4 * 2, "c_R=4 counterexample at w=2")
    require(ceil_log2(3 ** 3) == 5 and 5 > 4,
            "floor(log2(q)) cannot bound u/w for all w")
    must_reject(lambda: roundtrip_case(3, 2, truncate=True), "round-trip t=w-1")
    return ["omit_carry", "underpad", "omit_order_swaps", "undercharge_width",
            "binary_equals_radix_width_false", "fixed_radix_free_factor_false",
            "floor_log_factor_false", "truncated_radix_return"]


def replay():
    inputs = pinned_inputs()
    router = router_from_bytes(inputs[ROUTER])
    packets = [packet_case(router, q, w, op) for q, w in CASES
               for op in ("swap", "forward_add", "reverse_add")]
    return {"status": "PASS_QADIC_ROUTE_CUTOFF_AUDIT", "assignment_seed": 73,
            "packet_cases": packets, "cutoff_pairs": cutoff_rows(json.loads(inputs[STOCK])),
            "roundtrip_cases": [roundtrip_case(q, w) for q, w in
                                ((3, 2), (3, 3), (5, 2), (7, 2))],
            "controls": controls(inputs[ROUTER]),
            "scope": "Source-bound binary-call width lemma and finite oracle-bound routing; "
                     "no actual stock coefficient, physical ordinary kernel, supplier or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = replay()
    if args.emit_to:
        with args.emit_to.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((HERE / "EXPECTED.json").read_text()),
                "complete committed receipt mismatch")
    print(result["status"], "packets=48 roundtrips=4 cutoff_pairs=12 controls=8 stock=unresolved")


if __name__ == "__main__":
    main()
