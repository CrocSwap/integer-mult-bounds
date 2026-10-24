"""Check the raw common-response controller and its finite terminal."""

from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
N = 73
UNIT = [1 << j for j in range(N)]
CYCLE = LANES / "bridge-access-20261017/cycle-cover-response-20261018/CYCLE-COVER-PROGRAMS.json"
SCHEDULE = LANES / "encoded-controller/NORMALIZATION-PROGRAMS.json"
INTERFACE = LANES / "circuit-interface/INTERFACE.json"
PINS = {
    CYCLE: "759f85673b0fda9ba4ff7312c18c80f8a8b72a3ad0a7b1192a8d08571d0095da",
    SCHEDULE: "7ce02810ecaca13ba084c365ec9c781a211e3c94dbf0f64e8717ca6d1c0b0ca9",
    INTERFACE: "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def act(columns, value):
    out = 0
    while value:
        bit = value & -value
        out ^= columns[bit.bit_length() - 1]
        value ^= bit
    return out


def transpose(columns):
    return [sum(((columns[j] >> i) & 1) << j for j in range(N))
            for i in range(N)]


def compose(left, right):
    return [act(left, column) for column in right]


def parity(value):
    return value.bit_count() & 1


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            lead = value.bit_length() - 1
            if lead in pivots:
                value ^= pivots[lead]
            else:
                pivots[lead] = value
                break
    return len(pivots)


def transvection(vector, value):
    return value ^ (vector if parity(vector & value) else 0)


def child_basis(q, last):
    anchor = next(e for e in UNIT if e != 1 and e != last and not e & q)
    v1, v2 = 1 ^ anchor, anchor ^ q
    need(not parity(v1) and not parity(v2), "Both transvections are orthogonal")
    columns = [transvection(v2, transvection(v1, e)) for e in UNIT]
    columns[1], columns[65] = columns[65], columns[1]
    inverse = transpose(columns)
    need(columns[:2] == [q, last], "The child uses the two stated lines")
    need(compose(columns, inverse) == compose(inverse, columns) == UNIT,
         "The child basis is orthogonal")
    return columns, inverse, [v1, v2]


def add_row(target, source, coefficient=1, shift=0):
    out = dict(target)
    for (input_row, exponent), value in source.items():
        key = (input_row, exponent + shift)
        out[key] = out.get(key, 0) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def recipe(pairs):
    events = [{"kind": "local", "stage": 0, "pair": 0, "reverse": False}]
    for i in range(pairs):
        s, t = 2 * i + 1, 2 * i + 2
        events.append({"kind": "local", "stage": s, "pair": i, "reverse": True})
        if i + 1 < pairs:
            events.extend([
                {"kind": "idle", "pair": i + 1, "from": -1, "to": s},
                {"kind": "bridge", "dst": i, "src": i + 1, "coefficient": 1},
            ])
        events.append({"kind": "local", "stage": t, "pair": i, "reverse": False})
        if i + 1 < pairs:
            events.extend([
                {"kind": "idle", "pair": i + 1, "from": s, "to": t},
                {"kind": "bridge", "dst": i, "src": i + 1, "coefficient": -1},
            ])
    events.extend({"kind": "idle", "pair": i, "from": 2 * i + 2, "to": 2 * pairs}
                  for i in range(pairs))
    events.extend({"kind": "bridge", "dst": i, "src": i - 1, "coefficient": 1}
                  for i in range(pairs - 1, 0, -1))
    events.append({"kind": "terminal", "pairs": pairs})
    return events


def run(pairs, events, backward_power=-1):
    state = [{(j, 0): 1} for j in range(2 * pairs)]
    for event in events:
        if event["kind"] == "local":
            x, y = 2 * event["pair"], 2 * event["pair"] + 1
            if event["reverse"]:
                state[x] = add_row(state[x], state[y], -1, backward_power)
            else:
                state[y] = add_row(state[y], state[x], shift=1)
        elif event["kind"] == "bridge":
            d, s, c = event["dst"], event["src"], event["coefficient"]
            state[2 * d] = add_row(state[2 * d], state[2 * s], c)
            state[2 * s + 1] = add_row(state[2 * s + 1], state[2 * d + 1], -c)
    return state


def controller_checks(actual):
    need(actual == recipe(4), "The pinned nineteen content events and ten idle sites")
    tests = []
    for pairs in range(1, 9):
        wanted = []
        for i in range(pairs):
            wanted.extend([{(2 * i + 1, -1): -1}, {(2 * i, 1): 1}])
        need(run(pairs, recipe(pairs)) == wanted, "All arbitrary controller inputs")
        need(run(pairs, recipe(pairs), 1) != wanted, "A forward response is not its inverse")
        tests.append({"pairs": pairs, "arbitrary_input_blocks": 4 * pairs * pairs})
    return tests


def terminal_record(record, ports):
    p, q = record["port"], record["q"]
    need(ports[p] == q, "The intrinsic direction is the actual supplier port")
    left, inverse = record["L_columns"], record["L_inverse_columns"]
    delta = record["FULL_E_output_translation"]
    epsilon = record["FULL_E_inverse_output_translation"]
    cycle = record["cycle_vectors"]
    need(inverse == transpose(left), "The cover cycle is orthogonal")
    need(compose(left, inverse) == compose(inverse, left) == UNIT, "Both cover inverse orders")
    need([act(left, value) for value in cycle] == cycle[1:] + cycle[:1], "The exact cover cycle")
    need(cycle[0] == q and cycle[-1] == 1 << 65, "The fixed final fresh axis")
    need(all(parity(a & b) == int(i == j)
             for i, a in enumerate(cycle) for j, b in enumerate(cycle)), "All ten cycle vectors")
    power = list(UNIT)
    for _ in range(10):
        power = compose(left, power)
    need(power == UNIT, "The cover cycle has order ten")
    last = act(inverse, q)
    need(last == cycle[-1], "The first terminal line is transported from the source cover")
    need(act(left, epsilon) == delta, "Both FULL translation conventions")
    g, gi, transvections = child_basis(q, last)
    offset = act(gi, epsilon)
    need(act(g, offset) == epsilon, "The left wrapper translation")
    bblock = [(q if parity(q & e) else 0) ^ (last if parity(last & e) else 0)
              for e in UNIT]
    need(rank(bblock) == 2, "The terminal block has exact Fourier rank two")

    characters = [0] + UNIT + [UNIT[i] ^ UNIT[j] for i in range(N) for j in range(i)]
    wrong = {key: None for key in ["omit_inverse_FULL_translation", "omit_forward_FULL_translation",
                                  "use_q_twice", "omit_target_line", "omit_source_line"]}
    for eta in characters:
        phi = eta.bit_count() % 4
        phi_l = act(inverse, eta).bit_count() % 4
        phi_i = act(left, eta).bit_count() % 4
        pd, pe = 2 * parity(delta & eta), 2 * parity(epsilon & eta)
        need((phi_l - phi - pd) % 4 == 0, "The full forward Z4 phase polynomial")
        need((phi_i - phi - pe) % 4 == 0, "The full inverse Z4 phase polynomial")
        line_q, line_last = parity(q & eta), parity(last & eta)
        pre_x = (phi_i - line_last) % 4
        actual_x = (pe + line_q + line_last + pre_x) % 4
        target_x = (phi + line_q) % 4
        need(actual_x == target_x, "The complete X terminal equals F Q on raw X")
        need((pd + phi_l) % 4 == phi, "The complete Y terminal equals F on raw Y")
        values = {
            "omit_inverse_FULL_translation": (line_q + line_last + pre_x) % 4 != target_x,
            "omit_forward_FULL_translation": phi_l != phi,
            "use_q_twice": (pe + 2 * line_q + pre_x) % 4 != target_x,
            "omit_target_line": (pe + line_last + pre_x) % 4 != target_x,
            "omit_source_line": (pe + line_q + pre_x) % 4 != target_x,
        }
        for key, failed in values.items():
            if failed and wrong[key] is None:
                wrong[key] = eta
    need(all(value is not None for value in wrong.values()), "All phase mutations fail")
    need(compose(left, left) != UNIT, "The wrong cover direction does not restore the input address")
    # The four translation coefficients are Gaussian integers divided by two.
    source_stencil = {0: (0, 1), 1: (1, 0), 2: (1, 0), 3: (0, -1)}
    target_stencil = {act(g, shift): value for shift, value in source_stencil.items()}
    need(target_stencil == {0: (0, 1), q: (1, 0), last: (1, 0), q ^ last: (0, -1)},
         "The exact rank-two child kernel after both linear views")
    return {
        "port": p, "q": q, "second_native_line": last,
        "X_child": {
            "rank": 2, "sign": 1,
            "right_view_cover_columns": inverse,
            "right_view_payload_at_output_cover_h_columns": g,
            "left_view_payload_columns_in_h_coordinates": gi,
            "left_view_payload_offset": offset,
            "basis_transvections_in_time_order": transvections,
            "basis_input_axis_swap": [1, 65],
            "output_translation_in_h_coordinates": epsilon,
        },
        "Y_source_map": {"cover_columns": left, "payload_translation_in_h_coordinates": delta},
        "final_exchange": "(X,Y)=(processed_V,-processed_U)",
        "negative_control_characters": wrong,
        "wrong_cover_direction_residual_columns": compose(left, left),
        "phase_coefficient_checks": len(characters),
    }


def main():
    for path, pin in PINS.items():
        need(sha256(path.read_bytes()).hexdigest() == pin, "Pinned input: " + str(path))
    actual = [event for event in json.loads(SCHEDULE.read_bytes())["schedule"]
              if event["kind"] in ("local", "idle", "bridge", "terminal")]
    tests = controller_checks(actual)
    ports = json.loads(INTERFACE.read_bytes())["ports"]
    source = json.loads(CYCLE.read_bytes())
    need(len(ports) == len(source["records"]) == 112, "All 112 ports")
    records = [terminal_record(record, ports) for record in source["records"]]
    need([record["port"] for record in records] == list(range(112)), "Every port occurs once")
    inventory = {
        "pairs": 4, "ports_per_bank": 112, "rank_two_children": 448,
        "native_rank_mass": 896, "child_wrapper_maps": 896,
        "FULL_source_maps": 448, "total_monomial_maps": 1344,
        "old_line_square_maps_removed": 448, "net_added_monomial_maps": 896,
        "retained_signed_exchanges": 448, "retained_unit_complex_ADDs": 1344,
        "retained_exchange_real_primitives": 10752,
        "new_top_level_scalar_primitives_beyond_retained_exchange": 0,
        "new_full_cover_records": 0,
    }
    payload = {
        "schema": "common-cover-integrated-terminal-v1",
        "input_contract": "U=-F E^-1 y; V=F Q^-1 E x; original raw input is (Qx,y)",
        "output_contract": "(F Qx,F y), with no residual port or cover code",
        "source_pins": {str(path.relative_to(LANES)): pin for path, pin in PINS.items()},
        "inventory_per_replica": inventory,
        "records": records,
    }
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (HERE / "TERMINAL-PROGRAMS.json").write_bytes(raw)
    receipt = {
        "status": "PASS_COMMON_COVER_INTEGRATED_TERMINAL",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_sha256": sha256((HERE / "COMMON-TERMINAL.md").read_bytes()).hexdigest(),
        "program_sha256": sha256(raw).hexdigest(),
        "source_pins": payload["source_pins"],
        "all_m_free_E_tests": tests,
        "actual_content_events": sum(e["kind"] != "idle" for e in actual),
        "actual_idle_sites": sum(e["kind"] == "idle" for e in actual),
        "port_phase_polynomial_checks": 112 * 2 * (1 + 73 + 2628),
        "exact_native_kernel_checks": 112,
        "negative_controls": {"nonreciprocal_controller": 8, "phase_mutations": 560,
                              "wrong_cover_direction": 112},
        "inventory_per_replica": inventory,
        "scope": "Finite terminal and ordered raw controller. The local native words, complete owner schedule, recursive child hosting, map price, and precision are separate dependencies. The conditional native rank balance gives no positive kappa gain.",
    }
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
