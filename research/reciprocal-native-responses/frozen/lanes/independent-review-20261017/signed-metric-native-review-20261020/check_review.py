"""Review all signed reciprocal native words without the producer interpreter."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "oblique-native-20261017/signed-metric-reciprocal-20261020"
PINS = {
    "NATIVE-FREEZE.json": "ced70c0c6fe961b1a840819ee5e8cce2756a229d4eee7ec3b5a6f8e4bac6c6eb",
    "MODEL-FREEZE.json": "9dbff19fa68567eadea82cef2add71fda3ffe7228944028d06d53880da8b70f7",
    "NATIVE.md": "1fe48a47d0dca937f8ccc5c27936b3d679cf6c997c6f9156ca4158554a9f19a7",
    "emit_native.py": "b6db27a1a7e990ac297972f0306efa624bfa317d70bcb18615a38a4b8d2aac03",
    "model-normal-v2/RESPONSE.json.gz": "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0",
    "native-normal/NATIVE.json.gz": "f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e",
    "native-normal/CHECKS.json": "e3e6b18efae3b93fa48b95c0c2f238caff1ec3f5a9948bd880e21c9cf75d31b0",
}
OLD = LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz"
OLD_PIN = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
PEER = LANES / "new-native-recipes-20261017/low-displacement-review-20261020"
PEER_PIN = "c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c"


def need(value, label):
    if not value:
        raise ValueError(label)


def read(path, pin):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Source digest: " + str(path))
    return raw


def rows(raw):
    return [{int(j): F(value) for j, value in row.items()} for row in raw]


def eye(size):
    return [{j: F(1)} for j in range(size)]


def add(target, source, value):
    for j, x in source.items():
        result = target.get(j, F(0)) + value*x
        if result:
            target[j] = result
        else:
            target.pop(j, None)


def multiply(a, b):
    result = []
    for row in a:
        target = {}
        for j, value in row.items():
            add(target, b[j], value)
        result.append(target)
    return result


def transpose(a, width):
    result = [{} for _ in range(width)]
    for i, row in enumerate(a):
        for j, value in row.items():
            result[j][i] = value
    return result


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return result


def tariff(gate):
    op, _, _, raw = gate
    value = F(raw)
    a, b = abs(value.numerator), value.denominator
    need(a and b & (b-1) == 0, "Nonzero dyadic coefficient")
    if op == "scale":
        need(a & (a-1) == 0, "Dyadic unit scale")
        return 2*(abs(a.bit_length()-b.bit_length()) + (value < 0))
    need(op == "add", "Known scalar primitive")
    return 2*(1+a.bit_length()+a.bit_count()+b.bit_length())


def reverse_columns(events):
    columns = eye(640)
    for event in reversed(events):
        if event[0] == "native":
            continue
        op, target, origin, raw = event[1]
        value = F(raw)
        if op == "scale":
            columns[target] = {j: value*x for j, x in columns[target].items()}
        else:
            add(columns[origin], columns[target], value)
    return columns


def shear_columns(response, backward):
    result = eye(640)
    for target, row in enumerate(response):
        for origin, value in row.items():
            if backward:
                add(result[112+target], {origin: -value}, F(1))
            else:
                add(result[origin], {112+target: value}, F(1))
    return result


def inverse_adjoint_events(events):
    result = []
    for event in events:
        if event[0] == "native":
            result.append(event)
            continue
        _, gate, frame = event
        op, target, origin, raw = gate
        value = F(raw)
        new = [op, origin, target, str(-value)] if op == "add" else [op, target, None, str(1/value)]
        result.append(["scalar", new, frame])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "New output path")
    saved = {name: read(SOURCE/name, pin) for name, pin in PINS.items()}
    native = json.loads(saved["native-normal/NATIVE.json.gz"])
    model = json.loads(saved["model-normal-v2/RESPONSE.json.gz"])
    old = json.loads(read(OLD, OLD_PIN))
    need(native["model"] == model, "Exact model binding")
    peer = json.loads(read(PEER/"EXTENSIONS-REVIEW-FREEZE.json", PEER_PIN))
    for name, pin in peer["files"].items():
        read(PEER/name, pin)
    accepted_inputs = json.loads((PEER/"extensions-normal/EXTENSIONS-INPUTS.json").read_bytes())
    need(accepted_inputs[str(OLD.relative_to(LANES))]["decompressed_sha256"] == OLD_PIN,
         "The accepted spatial review consumed this exact native source")
    accepted = json.loads((PEER/"extensions-normal/EXTENSIONS-REVIEW.json").read_bytes())["extensions"]["odd-grid-rank16"]
    fresh = accepted["fresh_native_phase_checks"]
    need(len(fresh) == 876 and all(row["spatial_columns"] == 512 for row in fresh),
         "Accepted complete spatial checks")
    accepted_keys = set(accepted["exact_inherited_frame_pairs"]) | {row["edge"] for row in fresh}

    e, ei = rows(model["physical"]["E"]), rows(model["physical"]["inverse_E"])
    ej = rows(model["physical"]["inverse_adjoint_E"])
    j, ji = rows(model["physical"]["J"]), rows(model["physical"]["inverse_J"])
    h, hi = rows(model["pair_code"]), rows(model["pair_code_inverse"])
    need(multiply(e, ei) == multiply(ei, e) == eye(112), "Actual inverse orders")
    need(ej == transpose(ei, 112), "Exact inverse adjoint")
    need(multiply(j, ji) == multiply(ji, j) == eye(112), "Metric unit")
    need(all(set(row) == {p} for p, row in enumerate(j)), "Physical diagonal metric")
    need(multiply(multiply(j, e), ji) == ej, "Actual physical metric conversion")
    need(Counter(row[p] for p, row in enumerate(j)) == Counter({F(1): 80, F(-1, 2): 16, F(-1, 4): 16}),
         "Actual signed metric entries")
    modes = {"forward_E": multiply(multiply(h, e), hi),
             "forward_inverse_adjoint_E": multiply(multiply(h, ej), hi)}
    need(all(p not in row for matrix in modes.values() for p, row in enumerate(matrix)),
         "Both complete mode diagonals vanish")

    def wrapped_events(events, frames_in, frames_out, forward):
        pre, post = (ji, j) if forward else (j, ji)
        result = []
        for bank in (0, 112):
            for p, row in enumerate(pre):
                if row[p] != 1:
                    result.append(["scalar", ["scale", bank+p, None, str(row[p])], frames_in[bank+p]])
        prefix = len(result)
        result += events
        for bank in (0, 112):
            for p, row in enumerate(post):
                if row[p] != 1:
                    result.append(["scalar", ["scale", bank+p, None, str(row[p])], frames_out[bank+p]])
        return result, prefix

    reports = {}
    for provider in ("base", "extra"):
        original = old["providers"][provider]["forward"]
        words = native["providers"][provider]
        need(set(original["native_recipes"]) == accepted_keys, "Accepted phase recipe coverage")
        need(len(original["native_recipes"]) == 1561 and len(original["endpoint_adapters"]) == 224,
             "Complete inherited phase and endpoint tables")
        transfer_slots = {record["event"] for record in original["transfer_records"]}
        need(len(transfer_slots) == len(original["transfer_records"]), "Unique transfer positions")
        for name, mode in modes.items():
            expected_events = []
            for index, event in enumerate(original["events"]):
                if index not in transfer_slots:
                    expected_events.append(event)
                    continue
                need(event[0] == "scalar" and event[1][0] == "add", "Actual source transfer slot")
                _, target, origin, _ = event[1]
                need(112 <= target < 224 and 0 <= origin < 112, "Actual forward transfer addresses")
                coefficient = mode[target-112].get(origin, F(0))
                if coefficient:
                    expected_events.append(["scalar", ["add", target, origin, str(coefficient)], event[2]])
            need(words[name]["events"] == expected_events, "Independent complete retuning: " + name)
        need(words["backward_transpose_E"]["events"] == inverse_adjoint_events(words["forward_E"]["events"]),
             "First literal inverse-adjoint chronology")
        need(words["backward_inverse_E"]["events"] == inverse_adjoint_events(words["forward_inverse_adjoint_E"]["events"]),
             "Second literal inverse-adjoint chronology")
        for name, base, forward in (
                ("forward_inverse_adjoint_by_metric", "forward_E", True),
                ("backward_inverse_by_metric", "backward_transpose_E", False)):
            expected, prefix = wrapped_events(words[base]["events"], original["start"], original["final"], forward)
            actual = words[name]["events"]
            need(prefix == 64 and len(actual) == len(expected), "Complete two-bank wrapper size")
            need(actual[prefix:-prefix] == words[base]["events"], "Unchanged core inside wrapper")
            for left, right in ((actual[:prefix], expected[:prefix]), (actual[-prefix:], expected[-prefix:])):
                need(sorted(left, key=lambda event: event[1][1]) ==
                     sorted(right, key=lambda event: event[1][1]),
                     "Exact per-field diagonal wrapper: " + name)

        reports[provider] = {}
        for name, word in words.items():
            for key in ("native_recipes", "endpoint_adapters", "frames", "start", "final"):
                need(word[key] == original[key], "Exact inherited physical object: " + key)
            need([e for e in word["events"] if e[0] == "native"] ==
                 [e for e in original["events"] if e[0] == "native"], "Exact native occurrence order")
            current, state = list(word["start"]), eye(640)
            need(len(current) == 640, "All640 arbitrary roles")
            profile, progress = Counter(), Counter()
            scalar, maximum, height = 0, F(1), 0
            spaces = [span(frame) for frame in word["frames"]]
            for event in word["events"]:
                if event[0] == "native":
                    _, field, before, after, rank, key = event
                    need(0 <= field < 224 and current[field] == before, "Native field and old frame")
                    need(spaces[before] < spaces[after], "Strict nested native progress")
                    need(rank == len(word["frames"][after])-len(word["frames"][before]) ==
                         word["native_recipes"][key]["rank"], "Actual native rank")
                    need(key == str(before)+":"+str(after), "Ordered recipe key")
                    current[field] = after
                    profile[rank] += 1
                    progress[field] += rank
                    continue
                need(event[0] == "scalar", "Only scalar and native events")
                _, gate, frame = event
                op, target, origin, raw = gate
                value = F(raw)
                need(0 <= target < 224 and current[target] == frame, "Scalar target frame")
                if op == "add":
                    need(0 <= origin < 224 and origin != target and current[origin] == frame,
                         "Equal ordered source and target frames")
                    add(state[target], state[origin], value)
                else:
                    need(op == "scale" and origin is None, "Scale syntax")
                    state[target] = {p: value*x for p, x in state[target].items()}
                scalar += tariff(gate)
                maximum = max(maximum, sum(map(abs, state[target].values()), F(0)))
                for value in state[target].values():
                    need(value.denominator & (value.denominator-1) == 0, "Dyadic scalar prefix")
                    height = max(height, value.denominator.bit_length()-1)
            need(current == word["final"], "Complete final frames")
            need(all(progress[p] == 8 for p in range(224)), "Eight productive ranks on each data field")
            need(profile == Counter({1: 1520, 2: 64, 3: 48}), "Complete native profile")
            need(all(current[p] == word["start"][p] and state[p] == {p: F(1)} for p in range(224, 640)),
                 "All416 arbitrary outside fields and frames unchanged")
            response = e if name in ("forward_E", "backward_transpose_E") else ej
            backward = name.startswith("backward")
            expected_columns = shear_columns(response, backward)
            need(reverse_columns(word["events"]) == expected_columns, "All640 independent reverse columns")
            need(transpose(state, 640) == expected_columns, "All640 forward rows agree")
            expected_scalar = 7080 if name.endswith("by_metric") else 6440
            need(scalar == expected_scalar, "Exact complete scalar invoice")
            reports[provider][name] = {
                "input_columns": 640, "arbitrary_outside_fields": 416, "scalar_real": scalar,
                "prefix_row_one_norm": str(maximum), "binary_height": height,
                "native_profile": dict(sorted(profile.items())), "native_children": sum(profile.values()),
                "native_mass": sum(k*v for k, v in profile.items()), "endpoint_maps": 224,
                "native_side_map_bound": 2*sum(profile.values()), "exact_inherited_recipes": 1561,
            }
        for name in ("forward_E", "backward_inverse_E"):
            events = list(words[name]["events"])
            index = next(record["event"] for record in words[name]["transfer_records"])
            del events[index]
            response = e if name == "forward_E" else ej
            need(reverse_columns(events) != shear_columns(response, name.startswith("backward")),
                 "Missing-transfer negative control")
        malformed = dict(words["forward_E"]["native_recipes"])
        key = next(iter(malformed))
        malformed[key] = dict(malformed[key])
        malformed[key]["rank"] += 1
        need(malformed != original["native_recipes"], "Altered recipe negative control")
    need(reports["base"] == reports["extra"], "Both provider receipts")
    receipt = {
        "status": "PASS_INDEPENDENT_SIGNED_METRIC_NATIVE",
        "source_pins": PINS, "old_native_payload": OLD_PIN, "accepted_phase_review_freeze": PEER_PIN,
        "reports": reports, "words": 12,
        "new_spatial_phase_checks": 0,
        "phase_scope": "Complete ordered frames, native occurrences, full recipes and endpoint records are byte-equal to the accepted source. No new phase recipe is introduced.",
        "scope": "Complete local data service. Outside fields are identity, without productive helper progress. Routed controller, terminal, child host and precision are separate.",
    }
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
