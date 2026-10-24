"""Check the exact source cuts for the current reciprocal reader."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "model": (
        "oblique-native-20261017/signed-metric-reciprocal-20261020/"
        "model-normal-v2/RESPONSE.json.gz",
        "df2d2028c99028db3c645b3311d7f31ff96efe72f6f9257f99157ce030ff43d0",
    ),
    "native": (
        "oblique-native-20261017/signed-metric-reciprocal-20261020/"
        "native-normal/NATIVE.json.gz",
        "f528752be6222da2b64522f9a124622acab4413e79d403d58b592d2533307d1e",
    ),
    "views": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "scalar_tariff": (
        "new-core-transfer-20261017/low-displacement-20261020/check_response.py",
        "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def rows(raw):
    return [{int(k): F(v) for k, v in row.items()} for row in raw]


def identity(n):
    return [{i: F(1)} for i in range(n)]


def add(target, source, coefficient):
    for k, v in source.items():
        value = target.get(k, F(0)) + coefficient * v
        if value:
            target[k] = value
        else:
            target.pop(k, None)


def product(a, b):
    out = []
    for row in a:
        target = {}
        for k, v in row.items():
            add(target, b[k], v)
        out.append(target)
    return out


def act(columns, vector):
    out = 0
    while vector:
        low = vector & -vector
        out ^= columns[low.bit_length() - 1]
        vector ^= low
    return out


def phase(terms):
    """Return the complete degree-two Z4 phase polynomial."""
    out = {}
    for vector, coefficient in terms:
        bits = [i for i in range(25) if vector >> i & 1]
        for i in bits:
            out[i, i] = (out.get((i, i), 0) + coefficient) % 4
        for a, i in enumerate(bits):
            for j in bits[a + 1:]:
                out[i, j] = (out.get((i, j), 0) - 2 * coefficient) % 4
    return {k: v for k, v in out.items() if v}


def query_word(reader, source_offset):
    return [["add", 640 + i, source_offset + p, str(c)]
            for i, row in enumerate(reader) for p, c in sorted(row.items())]


def replay(word):
    state = identity(656)
    for op, target, source, coefficient in word:
        need(op == "add" and target >= 640 and source < 224,
             "Only the supplied reader bank is written")
        add(state[target], state[source], F(coefficient))
    return state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources, pins = {}, {}
    for name, (relative, expected) in PINS.items():
        path = LANES / relative
        raw = path.read_bytes()
        if path.suffix == ".gz":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == expected, "Exact source " + name)
        sources[name] = None if path.suffix == ".py" else json.loads(raw)
        pins[name] = {"path": str(path), "sha256": expected}
    model, native = sources["model"], sources["native"]
    view = {(r["stage"], r["port"]): r for r in sources["views"]["entries"]}
    q, anchors = model["ports"], model["centre_ports"]
    need(len(q) == 112 and len(anchors) == len(set(anchors)) == 16, "Port dimensions")
    need(all(view[s, p]["q"] == q[p] for s in range(3) for p in range(112)),
         "Exact physical port order")
    E, Ei, R, P = [rows(model["physical"][name]) for name in ("E", "inverse_E", "R", "P")]
    U, L = rows(model["reflection_U"]), rows(model["reflection_L"])
    I = identity(112)
    difference = [dict(row) for row in R]
    for i in range(112):
        add(difference[i], I[i], F(-1))
    need(product(U, L) == difference and product(L, U) == [{i: F(-2)} for i in range(16)],
         "Actual physical reflection factor")
    need(product(P, R) == E and product(P, P) == product(R, R) == I,
         "Exact local response factors")
    need(product(P, product(Ei, P)) == product(P, R),
         "The wrapped reciprocal backward map has cross P R")
    need(all(P[p] == I[p] for p in anchors), "P fixes all chosen centre anchors")
    need(native["contracts"]["input"] ==
         "Physical X=Qx, Y=y. The native adapters are explicit.", "Native input type")
    need(native["contracts"]["forward_E"] == "Physical X=F x, Y=F q(y+E x).",
         "Native forward contract")
    need(native["contracts"]["backward_inverse_E"] ==
         "Physical X=F(x-E^-1 y), Y=F q y.", "Native reciprocal contract")
    cuts = {}
    for provider, words in native["providers"].items():
        need(set(("forward_E", "backward_inverse_E")) <= set(words), "Required literal words")
        cuts[provider] = {}
        for name in ("forward_E", "backward_inverse_E"):
            word = words[name]
            need(len(word["start"]) == len(word["final"]) == 640, "Complete local role set")
            need(all(word["frames"][word["final"][p]] == list(reversed([1 << i for i in range(9)]))
                     for p in range(112)), "Every raw source output is FULL")
            cuts[provider][name] = {"literal_events": len(word["events"]),
                                    "entry_before_endpoint_adapters": True,
                                    "exit_after_complete_raw_word": True}

    unit = [1 << i for i in range(25)]
    counts = Counter()
    negative_controls = 0
    for s in (1, 2):
        for p in range(112):
            record = view[s, p]
            rho = record["route_columns"]
            delta = record["literal_stage_alignment"]
            need(act(rho, q[p]) == q[p], "The route fixes its own intrinsic line")
            previous = [(a, 1) for a in unit[:9 + 8 * (s - 1)]]
            exterior = [(act(rho, a), 1) for a in unit[9:9 + 8 * s]]
            # The source record stores the entry translation before the route.
            correction = [(delta["entry_X"], 2)]
            need(phase(previous + correction) == phase(exterior + [(q[p], 1)]),
                 "FULL source entry has exactly one current Q")
            counts["FULL_source_entry"] += 1
            need(phase(previous + [(q[p], -1)] + correction) == phase(exterior),
                 "Current Y entry has a common I body frame")
            counts["hole_target_entry"] += 1
            full = [(a, 1) for a in unit[:9 + 8 * s]]
            need(phase(full + [(act(rho, delta["exit_X"]), 2)]) ==
                 phase([(act(rho, a), 1) for a in unit[:9 + 8 * s]]),
                 "FULL reader exit has the exact anchor route")
            counts["FULL_exit"] += 1
            negative_controls += phase(previous) != phase(exterior + [(q[p], 1)])
    need(negative_controls > 0, "Omitting the actual entry translations is rejected")

    coefficient_counts = Counter(c for row in L for c in row.values())
    need(set(coefficient_counts) == {F(-1), F(1)}, "Signed-unit reader coefficients")
    programs = {}
    for name, offset in (("FULL_X", 0), ("current_I_Y", 112)):
        word = query_word(L, offset)
        state = replay(word)
        need(state[:640] == identity(640), "All data and helper values remain unchanged")
        for i, row in enumerate(L):
            expected = {640 + i: F(1)}
            add(expected, {offset + p: c for p, c in row.items()}, F(1))
            need(state[640 + i] == expected, "The arbitrary accumulator baseline is retained")
        inverse = [[op, t, s, str(-F(c))] for op, t, s, c in reversed(word)]
        need(replay(word + inverse) == identity(656), "Exact local read and erase order")
        programs[name] = {"events": word, "inverse_events": inverse,
                          "complex_ADDs": len(word), "real_scalar_units": 8 * len(word),
                          "prefix_row_one_norm": str(max(sum(abs(c) for c in row.values())
                                                          for row in state)),
                          "additional_coefficient_binary_height": 0}
    output = {
        "schema": "reciprocal-reader-current-cuts-v1",
        "source_pins": pins,
        "centre_anchors": anchors,
        "literal_native_cut_locations": cuts,
        "programs": programs,
        "cut_types": [
            {"stage": 0, "source": "raw FULL X before post-P0", "stored_logical_source": "x",
             "reader": "c0=ell0 x", "global_accumulator_frame": "F9"},
            {"stage": 1, "source": "current-I Y before pre-P1", "stored_logical_source": "P0 t",
             "reader": "c1=ell1 P0 t", "global_accumulator_frame": "F9 q_anchor"},
            {"stage": 2, "source": "raw FULL X before post-P2", "stored_logical_source": "(P1 P0) w",
             "reader": "c2=ell2 (P1 P0) w", "global_accumulator_frame": "F25"},
        ],
        "obligations": [
            "Each ADD word requires16 independent accumulator fields in the declared body frame.",
            "The accumulator may be dirty; the output retains its arbitrary baseline.",
            "No storage, owner lease, record transport, or late erase is supplied.",
            "The native transcript and its helper contract are inherited; this checker does not replay them.",
        ],
    }
    payload = (json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (args.out / "READERS.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    receipt = {
        "status": "PASS_EXACT_CURRENT_READER_CUTS",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_decompressed_sha256": sha256(payload).hexdigest(),
        "source_pins": pins,
        "phase_counts": dict(counts),
        "omitted_entry_translation_failures": negative_controls,
        "reader_nonzeros": sum(map(len, L)),
        "reader_source_port_support": len({p for row in L for p in row}),
        "reader_row_lengths": dict(Counter(map(len, L))),
        "reader_coefficients": {str(c): n for c, n in coefficient_counts.items()},
        "per_reader_real_scalar_units": 8 * sum(map(len, L)),
        "prefix_row_one_norm": programs["FULL_X"]["prefix_row_one_norm"],
        "additional_coefficient_binary_height": 0,
        "arbitrary_input_columns_per_local_reader": 656,
        "source_or_helper_fields_modified": 0,
        "independent_typed_accumulators_required": 16,
        "extra_source_native_lines_at_these_cuts": 0,
        "record_retention_or_restoration_claimed": False,
        "native_word_replayed_here": False,
        "complete_supplier_claimed": False,
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": receipt["status"], "phases": sum(counts.values()),
                      "reader_ADDs": sum(map(len, L)), "scalar": receipt["per_reader_real_scalar_units"]}))


if __name__ == "__main__":
    main()
