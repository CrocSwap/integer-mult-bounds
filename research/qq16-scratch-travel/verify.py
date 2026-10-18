#!/usr/bin/env python3
"""Exact word-address travel for two pinned QQ16 scalar sweeps. Apache-2.0."""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOWS = ((633, 1066, "L2"), (1172, 2125, "F0_inverse"))
BANKS = 112
MAX_SITES = 64
MAX_BYTES = 256_000
EXPECTED = {
    "L2": {"Z": [416, 76, 107, 2485], "W": [432, 0, 0, 0]},
    "F0_inverse": {"Z": [912, 76, 110, 4396], "W": [944, 0, 15, 1603]},
}
POLYNOMIALS = {
    "L2": {"bank-major": [2516, 154, -2], "site-major": [0, 2902, -234]},
    "F0_inverse": {"bank-major": [6048, 152, 0], "site-major": [0, 6398, -198]},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_word():
    source = json.loads((HERE / "SOURCES.json").read_text())["pending_source"]
    require(source["archive"] == "source-word.json.gz", "fixed archive path")
    require((HERE / source["archive"]).stat().st_size <= MAX_BYTES, "archive bound")
    with gzip.open(HERE / source["archive"], "rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) == source["uncompressed_bytes"] <= MAX_BYTES, "source size")
    require(hashlib.sha256(raw).hexdigest() == source["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    require(
        hashlib.sha1(header + raw).hexdigest() == source["git_blob"], "source Git blob"
    )
    word = json.loads(raw)
    require(type(word) is list and len(word) == 2415, "literal word extent")
    return word


def field(name):
    require(isinstance(name, str) and 1 <= len(name) <= 4, "bounded field name")
    require(name[0] in "ZW" and name[1:].isdigit(), "owned output field")
    bank = int(name[1:])
    require(0 <= bank < BANKS and name == name[0] + str(bank), "canonical bank")
    return name[0], bank


def body_and_trace(word, start, end, name):
    begin, finish = word[start], word[end]
    require(
        begin["op"] == "output_slices_begin" and begin["name"] == name,
        "source begin marker",
    )
    require(
        finish["op"] == "output_slices_end" and finish["name"] == name,
        "source end marker",
    )
    expected = ["W0"] if name == "L2" else [f"W{i}" for i in range(16)]
    require(begin["fields"] == finish["fields"] == expected, "scratch bank order")
    body = word[start + 1 : end]
    traces = {"Z": [], "W": []}
    for event in body:
        op = event["op"]
        require(op in ("add", "clear"), "pointwise scalar-only window")
        if op == "clear":
            require(event["frame"] in ("current", "identity"), "local clear frame")
            roles = [event["field"]]
        else:
            require(
                event["coefficient"] in ("1", "-1", "1/4", "-1/4"),
                "scalar coefficient alphabet",
            )
            require(event["src"] != event["dst"], "distinct ADD fields")
            roles = [event["src"], event["dst"]]
        for role in roles:
            tape, bank = field(role)
            require(tape != "W" or role in expected, "active W slice only")
            traces[tape].append(bank)
    return body, traces


def invariants(sequence):
    require(0 < len(sequence) <= 2000, "bounded nonempty tape trace")
    variation = sum(abs(b - a) for a, b in zip(sequence, sequence[1:], strict=False))
    return [len(sequence), sequence[0], sequence[-1], variation]


def coefficients(summary, layout):
    _, first, last, variation = summary
    if layout == "site-major":
        return [0, variation + 2 * BANKS + first - last, 2 * last - 2 * BANKS]
    require(layout == "bank-major", "known layout")
    if first < last:
        return [variation + last - first, 2 * first, 0]
    return [variation + first - last, 2 * last + 2, -2]


def evaluate(polynomial, sites):
    require(type(sites) is int and sites > 0, "positive site count")
    square, linear, constant = polynomial
    return square * sites * sites + linear * sites + constant


def closed_distance(sequence, sites, layout, return_home=True):
    require(type(sites) is int and 1 <= sites <= MAX_SITES, "literal trace site bound")
    require(layout in ("bank-major", "site-major"), "known layout")
    head, distance = 0, 0
    for site in range(sites):
        for bank in sequence:
            address = (
                bank * sites + site if layout == "bank-major" else BANKS * site + bank
            )
            distance += abs(address - head)
            head = address
    return distance + (head if return_home else 0)


def execute(body, sites, site_major, wrong_owner=False):
    """Exact dirty-state scalar execution; no native or predecessor code imported."""
    require(type(sites) is int and 1 <= sites <= 5, "semantic fixture site bound")
    rows = {
        f"{tape}{bank}": [
            Fraction((bank + 3) ** 2 * (site + 1) + offset, 8) for site in range(sites)
        ]
        for tape, offset in (("Z", 0), ("W", 10000))
        for bank in range(BANKS)
    }
    # A site-major sweep moves only disjoint-site events, preserving each site's order.
    for outer in range(sites if site_major else len(body)):
        for inner in range(len(body) if site_major else sites):
            site, index = (outer, inner) if site_major else (inner, outer)
            event = body[index]
            if event["op"] == "clear":
                rows[event["field"]][site] = Fraction(0)
            else:
                src_site = (site + 1) % sites if wrong_owner else site
                rows[event["dst"]][site] += (
                    Fraction(event["coefficient"]) * rows[event["src"]][src_site]
                )
    return rows


def bridge_body(body):
    """Restore an existing dirty Z0 bank after each W-to-W unit subtraction."""
    out, bridges = [], 0
    for event in body:
        if event["op"] == "add" and event["src"][0] == event["dst"][0] == "W":
            require(event["coefficient"] == "-1", "unit scratch subtraction")
            src, dst = event["src"], event["dst"]
            out.extend(
                [
                    {"op": "add", "src": src, "dst": "Z0", "coefficient": "1"},
                    {"op": "add", "src": "Z0", "dst": dst, "coefficient": "-1"},
                    {"op": "add", "src": src, "dst": "Z0", "coefficient": "-1"},
                    {"op": "add", "src": "Z0", "dst": dst, "coefficient": "1"},
                ]
            )
            bridges += 1
        else:
            out.append(dict(event))
    require(
        all(e["src"][0] != e["dst"][0] for e in out if e["op"] == "add"),
        "streaming ADDs cross the two tapes",
    )
    return out, bridges


def stream_trace(body):
    traces = {"Z": [], "W": []}
    for event in body:
        roles = (
            [event["field"]] if event["op"] == "clear" else [event["src"], event["dst"]]
        )
        for role in roles:
            tape, bank = field(role)
            traces[tape].append(bank)
    return traces


def stream_coefficients(sequence):
    """Each tape visits each instruction's full contiguous site range in order."""
    count, first, last, _ = invariants(sequence)
    linear, constant = first + last + 1 + count, -count - 1
    for before, after in zip(sequence, sequence[1:], strict=False):
        delta = after - before
        linear += delta - 1 if delta >= 1 else 1 - delta
        constant += 1 if delta >= 1 else -1
    return [0, linear, constant]


def stream_distance(sequence, sites):
    require(type(sites) is int and 1 <= sites <= MAX_SITES, "stream site bound")
    head, distance = 0, 0
    for bank in sequence:
        for site in range(sites):
            address = bank * sites + site
            distance += abs(address - head)
            head = address
    return distance + head


def check_stream(body, name):
    candidate, bridges = bridge_body(body)
    require(bridges == (0 if name == "L2" else 8), "exact bridge inventory")
    traces = stream_trace(candidate)
    parts = [stream_coefficients(traces[tape]) for tape in ("Z", "W")]
    total = [sum(part[i] for part in parts) for i in range(3)]
    require(
        total == ([0, 3564, -896] if name == "L2" else [0, 8302, -1944]),
        "stream polynomial coefficients",
    )
    for sites in (*range(1, 33), MAX_SITES):
        distance = sum(stream_distance(seq, sites) for seq in traces.values())
        require(distance == evaluate(total, sites), "literal streaming distance")
    for sites in (2, 3, 5):
        require(
            execute(candidate, sites, False) == execute(body, sites, False),
            "dirty bridge restores every field under event-major execution",
        )
    if bridges:
        wrong = [dict(e) for e in candidate]
        first = next(
            i
            for i, e in enumerate(wrong)
            if e.get("src") == "W8" and e.get("dst") == "Z0"
        )
        wrong[first + 2]["coefficient"] = "1"
        require(
            execute(wrong, 3, False) != execute(body, 3, False),
            "dirty restoration control",
        )
    return {
        "bridges": bridges,
        "extra_unit_adds": 3 * bridges,
        "polynomial": total,
        "tape_touches": {tape: len(seq) for tape, seq in traces.items()},
    }


def scalar_bill(word, extra_unit_adds):
    adds = Counter(
        str(abs(Fraction(e["coefficient"]))) for e in word if e["op"] == "add"
    )
    clears = sum(e["op"] == "clear" for e in word)
    require(adds == {"1": 840, "1/4": 832} and clears == 288, "source scalar invoice")
    # These fixed prices are the pinned PR2651/QQ16 scalar contract, not head travel.
    return {
        "unit_adds": adds["1"] + extra_unit_adds,
        "quarter_adds": adds["1/4"],
        "clears": clears,
        "real_scalar_primitives": 8 * (adds["1"] + extra_unit_adds)
        + 12 * adds["1/4"]
        + 2 * clears,
    }


def check_window(word, start, end, name):
    body, traces = body_and_trace(word, start, end, name)
    summaries = {tape: invariants(sequence) for tape, sequence in traces.items()}
    require(summaries == EXPECTED[name], "literal touch invariants")
    for layout in ("bank-major", "site-major"):
        parts = [coefficients(summaries[tape], layout) for tape in ("Z", "W")]
        total = [sum(part[i] for part in parts) for i in range(3)]
        require(total == POLYNOMIALS[name][layout], "derived polynomial coefficients")
        for sites in (*range(1, 33), MAX_SITES):
            distance = sum(
                closed_distance(traces[tape], sites, layout) for tape in ("Z", "W")
            )
            require(distance == evaluate(total, sites), "literal travel equals formula")
    for sites in (2, 3, 5):
        baseline = execute(body, sites, False)
        require(execute(body, sites, True) == baseline, "disjoint-site commutation")
        require(execute(body, sites, True, True) != baseline, "wrong-owner control")
    return summaries, check_stream(body, name)


def controls(word):
    """Exercise omitted touches/returns, wrong placement, and illegal scalar sites."""
    for start, end, name in WINDOWS:
        _, traces = body_and_trace(word, start, end, name)
        require(
            invariants(traces["Z"][1:]) != EXPECTED[name]["Z"], "missing-touch control"
        )
        for layout in ("bank-major", "site-major"):
            open_path = sum(
                closed_distance(seq, 3, layout, False) for seq in traces.values()
            )
            require(
                open_path != evaluate(POLYNOMIALS[name][layout], 3),
                "return-home control",
            )
        require(
            closed_distance(traces["Z"], 3, "bank-major")
            != closed_distance(traces["Z"], 3, "site-major"),
            "layout control",
        )
    for edit in ("native", "cross-family", "inactive-scratch", "same-field"):
        changed = [dict(event) for event in word]
        if edit == "native":
            changed[634] = {"op": "current_map", "field": "W0", "port": 0}
        elif edit == "cross-family":
            changed[635]["src"] = "X76"
        elif edit == "inactive-scratch":
            changed[635]["dst"] = "W16"
        else:
            changed[635]["src"] = changed[635]["dst"]
        try:
            body_and_trace(changed, 633, 1066, "L2")
        except ValueError:
            continue
        raise ValueError("control accepted: " + edit)


def main():
    word = load_word()
    checked = {
        name: check_window(word, start, end, name) for start, end, name in WINDOWS
    }
    summaries = {name: row[0] for name, row in checked.items()}
    controls(word)
    totals = {
        layout: [
            sum(POLYNOMIALS[name][layout][i] for _, _, name in WINDOWS)
            for i in range(3)
        ]
        for layout in ("bank-major", "site-major")
    }
    stream_total = [
        sum(row[1]["polynomial"][i] for row in checked.values()) for i in range(3)
    ]
    extra_adds = sum(row[1]["extra_unit_adds"] for row in checked.values())
    result = {
        "touch_invariants": summaries,
        "polynomials": POLYNOMIALS,
        "total_bank_major": totals["bank-major"],
        "total_site_major": totals["site-major"],
        "literal_site_cases": [*range(1, 33), MAX_SITES],
        "semantic_site_cases": [2, 3, 5],
        "streaming_variant": {name: row[1] for name, row in checked.items()},
        "streaming_total": stream_total,
        "source_scalar_bill": scalar_bill(word, 0),
        "streaming_scalar_bill": scalar_bill(word, extra_adds),
        "scope": "two scalar sweeps, closed word-address protocol, no new kappa",
    }
    expected = json.loads((HERE / "RESULT.json").read_text())
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "typed result receipt",
    )
    print("PASS_QQ16_SCRATCH_TRAVEL bank=8564*N^2+306*N-2 site=9300*N-432 no_new_kappa")
    print(
        "PASS_QQ16_DIRTY_BRIDGE_STREAM bank=11866*N-2840 "
        "extra_unit_adds=24 no_new_kappa"
    )


if __name__ == "__main__":
    main()
