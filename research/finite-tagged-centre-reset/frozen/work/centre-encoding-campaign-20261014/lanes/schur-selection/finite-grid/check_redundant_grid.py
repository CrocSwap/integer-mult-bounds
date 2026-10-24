"""Check the exact backward digit reset and its native error cone."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
CORE = LANES / "history-encoding/FULL-MODE-PROGRAMS.json.gz"
CORE_SHA = "f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205"
MATRIX = LANES / "circuit-interface/INTERFACE.json"
MATRIX_SHA = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
CENTRES = [92, 57, 81, 224, 11, 240, 9, 256]
MODES = [225, 226, 229, 232, 241, 242, 257, 258]
MINOR = [0, 7, 20, 27, 36, 46, 57, 111]
CUT = 12995


def need(test, message):
    if not test:
        raise ValueError(message)


def add(row, other, c):
    out = row.copy()
    for j, x in other.items():
        value = out.get(j, Q(0)) + c * x
        if value:
            out[j] = value
        else:
            out.pop(j, None)
    return out


def gate(event):
    op = event[1]
    need(op[1][0] == "L", "A scalar target is not persistent")
    if op[0] == "add":
        need(op[2][0] == "L", "A scalar source is not persistent")
        return op[0], op[1][1], op[2][1], Q(op[3], op[4])
    need(op[0] == "scale", "An unknown scalar gate is present")
    return op[0], op[1][1], None, Q(op[2], op[3])


def advance(state, event):
    if event[0] == "scalar":
        op, target, source, c = gate(event)
        if op == "add":
            state[target] = add(state[target], state[source], c)
        else:
            state[target] = {j: c * x for j, x in state[target].items() if c * x}
    else:
        need(event[0] in ("climb", "phase", "adapter", "residual_adapter"),
             "An event has no inherited frame interpretation")


def pack(row):
    return [[j, str(x)] for j, x in sorted(row.items())]


def snap(x, step):
    scaled = x / step + Q(1, 2)
    return step * (scaled.numerator // scaled.denominator)


def decode(z, step, delta):
    coarse = snap(z, step)
    query = snap((z - coarse) / delta, step)
    return coarse - query


def main():
    source_raw = gzip.decompress(CORE.read_bytes())
    matrix_raw = MATRIX.read_bytes()
    need(sha256(source_raw).hexdigest() == CORE_SHA, "The core source changed")
    need(sha256(matrix_raw).hexdigest() == MATRIX_SHA, "The interface changed")
    word = json.loads(source_raw)["backward"]
    r = [{int(j): Q(x) for j, x in row.items()} for row in json.loads(matrix_raw)["R"]]
    need(word[CUT] == ["phase", "retained_centre_scale"], "The cut moved")

    state = [{j: Q(1)} for j in range(704)]
    inputs = {}
    denominator = 0
    growth = 0
    ranks = Counter()
    for index, event in enumerate(word):
        if event[0] == "climb":
            ranks[event[5]] += 1
        elif event[0] == "scalar":
            _, _, _, c = gate(event)
            need(c.denominator & (c.denominator - 1) == 0, "A scalar is not dyadic")
            denominator += c.denominator.bit_length() - 1
            growth += (abs(c.numerator) + c.denominator).bit_length()
        if index >= CUT:
            continue
        if event[0] == "climb":
            inputs[index] = state[event[2]].copy()
        advance(state, event)

    cut_rows = []
    for k, field in enumerate(CENTRES):
        expected = add({MODES[k]: Q(1)}, {112 + j: x for j, x in r[k].items()}, Q(1, 4))
        need(state[field] == expected, "A centre row differs")
        cut_rows.append(pack(state[field]))
        need(word[CUT + 1 + k] == ["scalar", ["scale", ["L", field], -1, 1], 415 + k],
             "A centre sign differs")
        state[field] = {MODES[k]: Q(1)}
    for event in word[CUT + 9:]:
        advance(state, event)
    expected = [{j: Q(1)} for j in range(704)]
    for j in range(112):
        expected[j][112 + j] = Q(-1)
    need(state == expected, "The decoded cut does not give the unit backward map")

    response = [{CENTRES.index(j): Q(1)} if j in CENTRES else {} for j in range(704)]
    active = []
    for index in range(CUT - 1, -1, -1):
        event = word[index]
        if event[0] == "climb" and response[event[2]]:
            row = inputs[index]
            need(any(j < 224 for j in row) and any(j >= 224 for j in row),
                 "A counted child is not mixed")
            active.append({"source_event": index, "rank": event[5],
                           "input": pack(row), "centre_response": pack(response[event[2]])})
        elif event[0] == "scalar":
            op, target, source, c = gate(event)
            if op == "add":
                response[source] = add(response[source], response[target], c)
            else:
                response[target] = {j: c * x for j, x in response[target].items() if c * x}
    profile = Counter(x["rank"] for x in active)
    need(profile == {1: 124, 4: 8}, "The centre cone differs")

    a = [[row.get(j, Q(0)) for j in MINOR] for row in r]
    need(all(sum(a[i][k] * a[j][k] for k in range(8)) == 4 * (i == j)
             for i in range(8) for j in range(8)), "The fixed minor is not orthogonal")
    need(max(sum(abs(x) for x in row) for row in zip(*a)) == 4,
         "The minor column bound differs")
    # These 64 tests establish q=v and u+q=0 in eight independent directions.
    for j in range(8):
        v = [Q(int(k == j), 16) for k in range(8)]
        y = [sum(a[k][p] * v[k] for k in range(8)) for p in range(8)]
        q = [sum(a[k][p] * y[p] for p in range(8)) / 4 for k in range(8)]
        need(q == v, "The full-width source witness failed")

    # Exact rational tests include negative numbers and both signed error limits.
    step = Q(1, 16)
    delta = Q(1, 1024)
    cases = 0
    for h_int in range(-16, 17):
        for q_int in range(-16, 17):
            h, q = h_int * step, q_int * step
            for sign in (-1, 0, 1):
                error = sign * delta * step / 16
                z = h + (1 + delta) * q + error
                need(decode(z, step, delta) == h, "The exact digit decoder failed")
                cases += 1
    need(decode(Q(1, 16) + Q(1, 1024) / 16 + step / 8, step, delta) != 0,
         "The coarse-only error control did not fail")
    need(snap(Q(1) + Q(1, 8), step) != Q(1), "The large-tag control did not fail")

    # Every new scalar access uses one cleared private field at the current frame.
    additions = {
        "COPY": 232, "SCALE_DYADIC_UNIT": 240, "ADD_SIGNED_UNIT": 240,
        "CLEAR": 233, "ROUND_GRID": 1416,
    }
    schedule = {"schema": "backward-redundant-grid-word-v1",
                "source_payload_sha256": CORE_SHA,
                "scratch": "one existing owned private centre field C0",
                "entry": [["CLEAR", "C0"], ["FOR_EACH", list(range(224)),
                           [["COPY", "L", "C0"], ["SCALE", "C0", "delta"],
                            ["ADD", "L", "C0", 1], ["CLEAR", "C0"]]]],
                "prefix_source_events": [0, CUT],
                "cut_coarse_round_fields": [j for j in range(704) if j not in CENTRES],
                "cut_centre_fields": CENTRES,
                "cut_centre_word": [["COPY", "L", "C0"], ["ROUND", "C0", "Delta"],
                                    ["ADD", "L", "C0", -1], ["SCALE", "L", "delta^-1"],
                                    ["ROUND", "L", "Delta"], ["SCALE", "L", -1],
                                    ["ADD", "L", "C0", 1], ["CLEAR", "C0"]],
                "suffix_source_events": [CUT + 9, len(word)],
                "exit_round_fields": list(range(704)),
                "exit_round_grid": "2^(-g-2H)",
                "range_convention": "half-open source event ranges"}
    encoded = (json.dumps(schedule, sort_keys=True, separators=(",", ":")) + "\n").encode()
    (HERE / "REDUNDANT-GRID-WORD.json.gz").write_bytes(gzip.compress(encoded, mtime=0))
    receipt = {"status": "PASS_EXACT_REDUNDANT_GRID_CUT_AND_NATIVE_CONE",
               "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "source_payload_sha256": CORE_SHA, "interface_sha256": MATRIX_SHA,
               "word_payload_sha256": sha256(encoded).hexdigest(),
               "canonical_input_columns": 704, "helper_columns_restored": 480,
               "cut": CUT, "cut_rows": cut_rows, "active_native_events": active,
               "fine_native_count": len(active), "fine_native_profile": dict(sorted(profile.items())),
               "fine_native_rank_mass": sum(k * n for k, n in profile.items()),
               "retained_native_profile": dict(sorted(ranks.items())),
               "retained_native_rank_mass": sum(k * n for k, n in ranks.items()),
               "scalar_denominator_sum": denominator, "scalar_growth_upper_sum": growth,
               "added_complex_operations": additions, "added_field_pass_upper_bound": sum(additions.values()),
               "exact_rational_decoder_cases": cases,
               "source_query_minor": MINOR, "source_query_minor_gram": "4 I8",
               "controls": ["coarse-only centre error fails fine extraction", "large tag crosses coarse grid"],
               "scope": "Exact canonical endpoint, native response cone, rational digit identity and operation schedule. Physical frame and error bounds are in GRID-RESET-PROOF.md. The finite global invoice and independent review are separate."}
    (HERE / "REDUNDANT-GRID-CHECK.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({key: receipt[key] for key in ("fine_native_count", "fine_native_profile",
          "fine_native_rank_mass", "added_field_pass_upper_bound", "exact_rational_decoder_cases")}, sort_keys=True))


if __name__ == "__main__":
    main()
