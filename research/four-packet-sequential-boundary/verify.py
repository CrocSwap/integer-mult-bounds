#!/usr/bin/env python3
"""Check actual monomials, physical order and owned output retirement."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from boundary import boundary, reorder, Tape
from streams import Meter, need, copy


def units(meter):
    return meter.reads + meter.writes + meter.moves + meter.erases


def load():
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            need(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                 "source hash mismatch")
    path = ROOT / "research/complex-four-base-packet/adapter.py"
    spec = spec_from_file_location("packet_source", path)
    old = module_from_spec(spec); spec.loader.exec_module(old)
    fixture = json.loads((path.parent / "FIXTURE.json").read_text())
    need(fixture["family"] == 65689 and fixture["event_index"] == 8814,
         "wrong source event")
    need(fixture["native_chart_rows"] == [2, 1] + [1 << i for i in range(2, 73)],
         "unsupported source chart")
    return old, fixture


def encode(value, bits):
    return bytes((x >> i) & 1 for x in value for i in range(bits))


def decode(raw, bits):
    values = []
    for half in (raw[:bits], raw[bits:]):
        x = sum(bit << i for i, bit in enumerate(half))
        values.append(x - (1 << bits) if x >> (bits - 1) else x)
    return tuple(values)


def hadamard(source, active_bits, labels, record_bits):
    """Integer Walsh calibration; the production C child remains abstract."""
    bits = record_bits // 2
    for position in range(active_bits):
        suffix = (1 << (len(labels) - position - 1)) * record_bits
        left, right, plus, minus = (Tape(source.meter) for _ in range(4))
        out = Tape(source.meter)
        for _ in range(1 << position):
            copy(source, left, suffix); copy(source, right, suffix)
            left.rewind(); right.rewind()
            for _ in range(suffix // record_bits):
                a = decode(left.read(record_bits), bits); b = decode(right.read(record_bits), bits)
                plus.write(encode(tuple(x + y for x, y in zip(a, b)), bits))
                minus.write(encode(tuple(x - y for x, y in zip(a, b)), bits))
            left.finish(); right.finish(); left.erase(); right.erase()
            plus.rewind(); minus.rewind(); copy(plus, out, suffix); copy(minus, out, suffix)
            plus.finish(); minus.finish(); plus.erase(); minus.erase()
        source.finish(); source.erase(); out.rewind(); source = out
    return source


def oracle(old, fixture, values):
    d = dict(fixture, e=73, f=1, t=0)
    packed = {}
    for x in range(512):
        for tag in range(2):
            packet = dict(remaining_row=0, address=(1 << 70) | x,
                          compact=tag, prefix=17, suffix=3, dirty=tag + 9)
            child, phase = old.pack(d, packet)
            key = (child["active"], child["inactive"], tag)
            packed[key] = (child, old.rotate(values[2*x+tag], phase))
    expected = [None] * 1024
    for (_, inactive, tag), (packet, _) in packed.items():
        y = packet["active"]
        value = tuple(sum((-1)**((x & y).bit_count() % 2) * packed[x, inactive, tag][1][j]
                          for x in range(8)) for j in range(2))
        result, phase = old.unpack(d, packet)
        need(result["address"] >> 9 == (1 << 70) >> 9 and result["dirty"] == tag + 9,
             "source oracle spectator changed")
        expected[2 * (result["address"] & 511) + tag] = old.rotate(value, phase)
    need(all(x is not None for x in expected), "oracle output incomplete")
    return expected


def replay():
    old, fixture = load()
    recipe = fixture["recipe"]
    values = [(i - 512, ((37*i) % 997) - 498) for i in range(1024)]
    bits = 16
    raw = b"".join(encode(x, bits) for x in values)
    expected = oracle(old, fixture, values)
    receipts = []
    for old_size in (0, 17, len(raw) + 13):
        meter = Meter(); source = Tape(meter, raw); output = Tape(meter, bytes(i % 2 for i in range(old_size)))
        borrowed = Tape(meter, b"\x01\x00\x01"); borrowed.head = 2
        child_units = calls = 0
        def child(tape, active, labels, width):
            nonlocal child_units, calls
            calls += 1
            need(active == 3 and labels[:3] == (2, 1, 0), "wrong physical child order")
            start = units(meter)
            result = hadamard(tape, active, labels, width)
            child_units += units(meter) - start
            return result
        receipt = boundary(source, output, list(range(8, -1, -1)) + ["tag"],
                           [list(range(9))], recipe["right"], recipe["left"], 3, bits, child)
        actual = [decode(output.data[i:i+2*bits], bits) for i in range(0, len(raw), 2*bits)]
        need(actual == expected, "physical endpoint differs from independent source oracle")
        need(bytes(source.data) == raw and source.head == output.head == 0, "source or heads changed")
        need(bytes(borrowed.data) == b"\x01\x00\x01" and borrowed.head == 2, "borrowed word changed")
        need(calls == 1 and not meter.ordinary_calls, "child or OLD call count")
        need(units(meter) - child_units == receipt["wrapper_transitions"], "wrapper invoice mismatch")
        receipt["child_transitions"] = child_units
        receipt["output_sha256"] = sha256(output.data).hexdigest()
        receipts.append(receipt)
    # Execute both actual column recipes on a complete 18-bit rectangle.
    table = []
    for x in range(512):
        x = (x & ~3) | ((x & 1) << 1) | ((x >> 1) & 1)
        y, first = old.mono(recipe["right"], x)
        z, second = old.mono(recipe["left"], y)
        z = (z & ~3) | ((z & 1) << 1) | ((z >> 1) & 1)
        table.append((z, (first + second) % 4))
    raw2 = bytearray(); expected2 = bytearray(4 * (1 << 18))
    for x in range(1 << 18):
        value = (x & 1, (x >> 1) & 1)
        raw2.extend(encode(value, 2))
        a, pa = table[x & 511]; b, pb = table[x >> 9]
        destination = a | (b << 9)
        expected2[4*destination:4*destination+4] = encode(old.rotate(value, pa+pb), 2)
    meter=Meter(); source=Tape(meter,raw2); output=Tape(meter,b"\x01")
    receipt2=boundary(source,output,list(range(17,-1,-1)),
                      [list(range(9)),list(range(9,18))],recipe["right"],recipe["left"],
                      3,2,lambda tape,active,labels,width:tape)
    need(output.data == expected2 and source.data == raw2, "two-column payload mismatch")
    need(units(meter) == receipt2["wrapper_transitions"], "two-column invoice")
    receipt2["output_sha256"] = sha256(output.data).hexdigest()
    permutation_cases = 0
    for n in range(2, 8):
        for rotation in range(n):
            labels = list(range(n)); wanted = labels[rotation:] + labels[:rotation]
            raw = b"".join(bytes((i >> j) & 1 for j in range(n)) for i in range(1 << n))
            tape = Tape(Meter(), raw)
            result, swaps = reorder(tape, labels, wanted, n)
            expected_bits = bytearray(n * (1 << n))
            for x in range(1 << n):
                destination = sum(((x >> (n-1-label)) & 1) << (n-1-i) for i,label in enumerate(wanted))
                expected_bits[n*destination:n*(destination+1)] = raw[n*x:n*(x+1)]
            need(result.data == expected_bits, "ordering endpoint")
            need(units(result.meter) == 18 * n * (1 << n) * len(swaps), "ordering invoice")
            permutation_cases += 1
    # Wrong monomial phases, translations and left maps have different witnesses.
    bad = json.loads(json.dumps(fixture)); bad["recipe"]["right"]["phase"] = 0
    need(oracle(old, bad, values) != expected, "absolute-phase control")
    bad = json.loads(json.dumps(fixture)); bad["recipe"]["right"]["offset"] = 0
    need(oracle(old, bad, values) != expected, "translation control")
    bad = json.loads(json.dumps(fixture)); bad["recipe"]["left"] = bad["recipe"]["right"]
    need(oracle(old, bad, values) != expected, "left-right control")
    rejected = 0
    for kind in ("alias", "head", "extent", "axes", "child_shape", "child_alias"):
        meter=Meter(); source=Tape(meter,raw if kind == "extent" else b"".join(encode(x,bits) for x in values))
        output=source if kind == "alias" else Tape(meter)
        if kind == "head":source.head=1
        columns=[[0]*9] if kind == "axes" else [list(range(9))]
        def wrong(tape, active, labels, width):
            if kind == "child_alias":return source
            if kind == "child_shape":tape.erase();return tape
            return tape
        try:
            boundary(source,output,list(range(8,-1,-1))+["tag"],columns,
                     recipe["right"],recipe["left"],3,bits,wrong)
        except ValueError:
            rejected += 1
    need(rejected == 6, "invalid interface accepted")
    return {"status":"PASS_FOUR_PACKET_SEQUENTIAL_BOUNDARY_NO_NEW_KAPPA",
            "source_family":65689,"source_event":8814,"payload_records":1024,
            "payload_cases":3,"ordering_cases":permutation_cases,"negative_controls":9,
            "receipts":receipts,"two_column_receipt":receipt2,"two_column_records":1<<18,
            "production_C_executed":False,
            "sublinear_node_allowance_closed":False}


if __name__ == "__main__":
    result = replay()
    if "--record" in sys.argv:(HERE/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    else:need(result==json.loads((HERE/"RESULT.json").read_text()), "receipt mismatch")
    print(json.dumps(result,sort_keys=True))
