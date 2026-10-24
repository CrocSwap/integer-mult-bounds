"""Check the common-q type through the actual nine-stage DATA views."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
BRIDGE = LANES / "bridge-access-20261017/check_bridge_access.py"
BRIDGE_PIN = "9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111"
TRIPLE = HERE.parent / "phase-coded-triple-20261020/FREEZE.json"
TRIPLE_PIN = "0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b"


def need(test, message):
    if not test:
        raise ValueError(message)


def reduced(word):
    inverse = {"Qp": "qp", "qp": "Qp", "Qr": "qr", "qr": "Qr"}
    result = []
    for letter in word:
        if result and inverse.get(letter) == result[-1]:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def add(*terms):
    out = {}
    for scale, row in terms:
        for word, value in row.items():
            out[word] = out.get(word, F(0)) + scale * value
    return {word: value for word, value in out.items() if value}


def op(letter, row):
    out = {}
    for word, value in row.items():
        key = reduced((letter,) + word)
        out[key] = out.get(key, F(0)) + value
    return {word: value for word, value in out.items() if value}


def forward(state, stage):
    a, u, z, v = state
    return [add((-1, z)), u, add((1, a), (1, op("H" + str(stage), u))),
            add((1, v), (1, op("Qr", u)))]


def backward(state, stage):
    a, u, z, v = state
    return [z, add((1, u), (1, op("D" + str(stage), z)), (-1, op("qr", v))),
            add((-1, a)), v]


def corrected_triple(state, first):
    state = forward(state, first)
    state = backward(state, first + 1)
    state[1] = add((1, state[1]), (-1, op("D" + str(first + 1), state[0])))
    state = forward(state, first + 2)
    state[3] = op("qr", state[3])
    state[2] = add((1, state[2]), (-1, op("H" + str(first + 2), state[1])))
    state[2] = add((1, state[2]), (-1, op("H" + str(first), state[3])))
    return state


def encoded(row):
    return [[list(word), str(value)] for word, value in sorted(row.items())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    need(sha256(BRIDGE.read_bytes()).hexdigest() == BRIDGE_PIN, "Phase source pin")
    need(sha256(TRIPLE.read_bytes()).hexdigest() == TRIPLE_PIN, "Local triple pin")
    spec = importlib.util.spec_from_file_location("chain_source_phase", BRIDGE)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    need(sha256(base.ARCHIVE.read_bytes()).hexdigest() == base.ARCHIVE_PIN,
         "Selected supplier archive")
    with tarfile.open(base.ARCHIVE) as archive:
        name, data_pin = base.MEMBERS["phases"]
        raw = archive.extractfile(name).read()
    need(sha256(raw).hexdigest() == data_pin, "Literal DATA phase member")
    ports = json.loads(raw)["recipes"]
    need(len(ports) == 112, "All supplier ports")
    checks = {
        "natural_FULL_entry": 0, "natural_hole_entry": 0,
        "natural_FULL_exit": 0, "natural_hole_exit": 0,
        "full_shear_views": 0, "own_line_fixed": 0,
    }
    negative = {"omitted_entry_translation": 0, "omitted_exit_translation": 0}
    used_shears = [
        (1, 1), (2, 2), (0, 2),
        (4, 4), (5, 5), (3, 5),
        (7, 7), (8, 8), (6, 8),
    ]
    for port, recipe in enumerate(ports):
        q = recipe["q"]
        basis = base.chart(q)
        need(basis[1:9] == recipe["idle_children"][0]["orthogonal_axes"][:8],
             "Actual complement basis")
        routes = {s: base.route(basis, s) for s in range(9)}
        for s in range(1, 9):
            rho = routes[s]
            alignment = recipe["stage_alignment"][s]
            need(alignment["entry_X"] == alignment["entry_Y"] and
                 alignment["exit_X"] == alignment["exit_Y"], "Paired entry and exit")
            need(base.act(rho, q) == q, "Own line")
            checks["own_line_fixed"] += 1
            delta_in = base.act(rho, alignment["entry_X"])
            delta_out = alignment["exit_X"]
            before = base.UNIT[:9 + 8 * (s - 1)]
            after = base.UNIT[:9 + 8 * s]
            exterior = base.UNIT[9:9 + 8 * s]
            raw_entry = base.product([(base.act(rho, e), 1) for e in before])
            entry = base.add_phase(raw_entry, base.line(delta_in, 2))
            wanted_entry = base.product([(e, 1) for e in exterior] + [(q, 1)])
            need(entry == wanted_entry, "Literal natural FULL entry")
            need(base.add_phase(entry, base.line(q, -1)) ==
                 base.product([(e, 1) for e in exterior]), "Literal natural hole entry")
            checks["natural_FULL_entry"] += 1
            checks["natural_hole_entry"] += 1
            negative["omitted_entry_translation"] += raw_entry != wanted_entry
            raw_exit = base.product([(base.act(rho, e), 1) for e in after])
            exit_phase = base.add_phase(raw_exit, base.line(delta_out, 2))
            wanted_exit = base.product([(e, 1) for e in after])
            need(exit_phase == wanted_exit, "Literal natural FULL exit")
            need(base.add_phase(exit_phase, base.line(q, -1)) ==
                 base.product([(e, 1) for e in after] + [(q, -1)]),
                 "Literal natural hole exit")
            checks["natural_FULL_exit"] += 1
            checks["natural_hole_exit"] += 1
            negative["omitted_exit_translation"] += raw_exit != wanted_exit
        for stage, level in used_shears:
            rho = routes[stage]
            delta = recipe["stage_alignment"][stage]["exit_X"] if stage else 0
            axes = base.UNIT[:9 + 8 * level]
            actual = base.add_phase(
                base.product([(base.act(rho, e), 1) for e in axes]),
                base.line(delta, 2))
            need(actual == base.product([(e, 1) for e in axes]),
                 "The actual shear view is FULL at its execution level")
            need(base.act(rho, delta) == delta, "The FULL affine view is an involution")
            checks["full_shear_views"] += 1
    need(all(checks[k] == 896 for k in checks if k != "full_shear_views") and
         checks["full_shear_views"] == 1008, "Complete phase coverage")
    need(negative == {
        "omitted_entry_translation": 896, "omitted_exit_translation": 896,
    }, "All omitted-translation controls fail")

    a, u, z, v = [{(name,): F(1)} for name in ("a", "u", "z", "v")]
    initial = [op("qp", a), op("qr", u), op("qp", z), v]
    state = corrected_triple(initial, 0)
    expected = [add((-1, op("qp", z))), add((-1, op("qr", v))),
                op("qp", a), op("qr", u)]
    need(state == expected, "First actual block has the common-q signed type")
    endpoints = {"25": [encoded(row) for row in state]}
    for first, dimension in ((3, 49), (6, 73)):
        entered = state[:3] + [op("Qr", state[3])]
        state = corrected_triple(entered, first)
        expected = [add((-1, expected[2])), add((-1, expected[3])),
                    expected[0], expected[1]]
        need(state == expected, "The common-q type is preserved by the next block")
        endpoints[str(dimension)] = [encoded(row) for row in state]
    want = [op("qp", z), op("qr", v), add((-1, op("qp", a))),
            add((-1, op("qr", u)))]
    need(state == want, "The nine-stage endpoint includes the exact sign")
    terminal = [op("Qp" if i % 2 == 0 else "Qr", row) for i, row in enumerate(state)]
    need(terminal == [z, v, add((-1, a)), add((-1, u))],
         "A direct positive line terminal restores the original physical inputs")
    need(op("Qr", op("D4", a)) != op("D4", op("Qp", a)),
         "The algebra does not commute a line through a scatter")

    profile = {"1": 9 * 1392, "2": 9 * 64, "3": 9 * 48, "8": 9 * 16}
    mass = sum(int(rank) * count for rank, count in profile.items())
    need(mass == 224 * 72 == 16128 and mass + 224 == 224 * 73,
         "Exact nine-stage native mass")
    receipt = {
        "status": "PASS_ACTUAL_D73_COMMON_Q_CHAIN",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": {
            "phase_source": {"path": str(BRIDGE), "sha256": BRIDGE_PIN},
            "supplier_archive": {"path": str(base.ARCHIVE), "sha256": base.ARCHIVE_PIN},
            "supplier_member": {"name": name, "sha256": data_pin},
            "local_triple": {"path": str(TRIPLE), "sha256": TRIPLE_PIN},
        },
        "phase_checks": checks,
        "negative_controls": negative,
        "free_operator_endpoints": endpoints,
        "physical_endpoint": "X=F73 q Y0; Y=-F73 q X0",
        "native_profile": profile,
        "native_mass": mass,
        "direct_terminal_positive_lines": 224,
        "native_mass_with_direct_terminal": mass + 224,
        "local_scalar_primitives": 9 * 4632,
        "nine_direct_FULL_shear_primitives": 9 * 2048,
        "added_FULL_affine_map_calls": 1792,
        "unchanged_global_stage_entry_exit_map_calls": 8 * 448,
        "owned_fields": 0,
        "scope": (
            "The exact common-q data type composes through the actual nine "
            "DATA stages. Local helper restoration is inherited; a complete "
            "owner host, recursive gathered-axis join, and numerical-grid "
            "invoice are not proved. The direct terminal has no strict "
            "native-mass improvement."
        ),
    }
    (args.out / "CHECKS.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": receipt["status"], "phase_checks": checks,
        "native_mass": mass, "native_mass_with_direct_terminal": mass + 224,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
