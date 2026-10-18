"""Exact native-interior envelope for F0 followed by B1. Apache-2.0.

The rational primitive engine is retained unchanged from commdata2338/PR3226.
The new dispatcher carries every field across the stage boundary and preserves
the full-cover map contract. Counts use a 512-coordinate normalization only.
"""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import sources

sources.authenticate()
from vendor.pr3226 import verify as ref  # noqa: E402

HERE = sources.HERE
require = sources.require


def check_cover_maps(packet):
    used = {e[2] for e in sources.expand(packet, "B_1_2") if e[0] == "cover_map"}
    for name in used:
        record = packet["map_registry"][name]
        columns = record["owner_right_matrix_columns"]
        require(
            len(columns) == 73
            and all(type(x) is int and 0 <= x < 1 << 73 for x in columns),
            "73-axis owner map",
        )
        basis = [0] * 73
        for column in columns:
            for pivot in range(72, -1, -1):
                if column >> pivot & 1:
                    if basis[pivot]:
                        column ^= basis[pivot]
                    else:
                        basis[pivot] = column
                        break
        require(all(basis), "invertible owner map")
        delta = record["payload_translation_at_identity_owner"]
        require(type(delta) is int and 0 <= delta < 1 << 73, "73-axis translation")
        require(
            record["action"]
            == (
                "out(d,z_1,...,z_lambda)=in(d*g,"
                "z_1 XOR d*delta,...,z_lambda XOR d*delta)"
            ),
            "full-cover action",
        )
    return len(used)


def scalar(envelope, state, gate):
    dest = ref.reg(gate[1])
    if gate[0] == "clear":
        require(dest >= 704, "owned clear only")
        state[dest] = ref.ZERO
        envelope.cost["clear_component_writes"] += 1024
    elif gate[0] == "scale":
        state[dest] = envelope.multiply(state[dest], Fraction(gate[2], gate[3]))
    else:
        require(gate[0] == "add", "scalar kind")
        src = ref.reg(gate[2])
        term = envelope.multiply(state[src], Fraction(gate[3], gate[4]))
        state[dest] = envelope.observe(state[dest].plus(term), "scalar-add")
        envelope.cost["scalar_real_additions"] += 1024
    return dest


def native(envelope, state, event, packet, children, adapters, residuals):
    kind = event[0]
    dest = ref.reg(event[1]) if kind in ("native_line", "cover_map") else event[2]
    require(type(dest) is int and 0 <= dest < 712, "native field")
    if kind == "climb":
        state[dest] = envelope.recipe(state[dest], children[event[3], event[4]])
    elif kind == "native_line":
        recipe = packet["native_line_recipes"][event[2]]["recipe"]
        state[dest] = envelope.recipe(state[dest], recipe)
    elif kind == "adapter":
        direction = event[1]
        if direction == "old_to_new" and dest < 112:
            state[dest] = envelope.mono(state[dest], adapters["source", dest]["left"])
        elif direction == "new_to_old" and 112 <= dest < 224:
            state[dest] = envelope.mono(
                state[dest], adapters["target", dest - 112]["left"]
            )
        else:
            envelope.cost["adapter_identity_labels"] += 1
    elif kind == "residual_adapter":
        direction, _, a = event[1:4]
        b = event[4] if len(event) == 5 else 1
        key = str(a) if b == 1 else f"{a}:{b}"
        side = "right" if direction == "pre" else "left"
        state[dest] = envelope.mono(state[dest], residuals["recipes"][key][side])
    else:
        require(kind == "cover_map" and event[2] in packet["map_registry"], "cover map")
        # A bijection of ALL owners/payloads preserves their uniform supremum.
        # This is not a one-owner 512-coordinate permutation or physical tariff.
        envelope.cost["full_cover_maps"] += 1
        envelope.cost["cover_component_transfers"] += 2048
        envelope.observe(state[dest], "cover-uniform-bound")
    return dest


def run_stage(events, state, envelope, packet, children, adapters, residuals, offset):
    completed = hashlib.sha256()
    for index, event in enumerate(events):
        envelope.event = offset + index
        if event[0] == "phase":
            envelope.cost["phase_labels"] += 1
            continue
        if event[0] == "scalar":
            dest = scalar(envelope, state, event[1])
        else:
            dest = native(envelope, state, event, packet, children, adapters, residuals)
        envelope.observe(state[dest], "completed-event")
        completed.update(
            ref.canonical([offset + index, dest, state[dest].record()]) + b"\n"
        )
    return {
        "events": len(events),
        "event_sha256": ref.digest(events),
        "completed_bound_sha256": completed.hexdigest(),
        "final_bounds_sha256": ref.digest([x.record() for x in state]),
        "max_grid_so_far": envelope.max_grid,
        "max_range_so_far": str(envelope.max_range),
    }


def audit():
    packet, recipes, residuals = sources.load()
    cover_maps = check_cover_maps(packet)
    children = {(r["old"], r["new"]): r for r in recipes["children"]}
    adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
    require(len(children) == len(recipes["children"]), "unique children")
    require(len(adapters) == len(recipes["endpoint_adapters"]), "unique adapters")
    state = [ref.UNIT] * 704 + [ref.ZERO] * 8
    envelope = ref.Envelope()
    stages, offset = {}, 0
    for name in ("F_0", "B_1_2"):
        events = sources.expand(packet, name)
        stages[name] = run_stage(
            events, state, envelope, packet, children, adapters, residuals, offset
        )
        offset += len(events)
    require(all(x == ref.ZERO for x in state[704:]), "private return zero")
    require(envelope.cost["full_cover_maps"] == 528, "528 actual full-cover maps")
    envelope.cost["final_owned_scratch_clear_writes"] = 1036
    magnitude_bits = ref.ceil_log2(envelope.max_range)
    return {
        "status": "PASS_QQ16_F0_B1_EXACT_GRID",
        "events": offset,
        "stages": stages,
        "grid_guard": envelope.max_grid,
        "grid_site": envelope.grid_site,
        "range_site": envelope.range_site,
        "range_power_of_two": magnitude_bits,
        "max_range_exact": str(envelope.max_range),
        "signed_width_P_plus": envelope.max_grid + magnitude_bits + 1,
        "primitive_bound_observations": envelope.observations,
        "primitive_bound_sha256": envelope.trace.hexdigest(),
        "direct_cost_normalization_N": 512,
        "direct_cost": dict(sorted(envelope.cost.items())),
        "distinct_cover_maps_checked": cover_maps,
        "payload_words_per_owner": "1426*N+12",
        "payload_dimension": "N=2^73, exactly one tensor layer",
        "physical_routing_priced": False,
        "supplier_admission": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        require(
            result == json.loads((HERE / "RESULT.json").read_text()), "receipt equality"
        )
    print(
        result["status"],
        "grid_guard=" + str(result["grid_guard"]),
        "signed_width=P+" + str(result["signed_width_P_plus"]),
    )


if __name__ == "__main__":
    main()
