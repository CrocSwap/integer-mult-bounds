"""Replay exact word differences from an immutable baseline and one literal edit."""
import argparse
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import alarm, signal, SIGALRM


BASE_WORD = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
PEER_EDITS = "a49e9962e32d13fd91cd8715d888bb1f4305003e63dd25485aa413905e00b8d9"
BASE_GZIP = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"


def add_scaled(target, source, scale):
    for key, value in source.items():
        result = target.get(key, 0) + scale * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def input_row(tape, cut, role, public):
    row = {role: Fraction(1)}
    for op, dst, *args in reversed(tape[:cut]):
        if dst not in row or op == "MOVE":
            continue
        weight = row[dst]
        if op in ("INIT", "CLEAR", "COPY"):
            del row[dst]
        if op == "SCALE":
            row[dst] = weight * Fraction(args[0])
        if op in ("ADD", "COPY"):
            add_scaled(row, {args[0]: Fraction(args[1])}, weight)
    assert all(role < public for role in row)
    return row


def span(basis):
    points = {0}
    for vector in basis:
        assert vector not in points
        points |= {point ^ vector for point in points}
    return points


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    progress = {"clock": None, "checks": 0}
    copy_checks = 0
    private_checks = 0

    def timeout(_signum, _frame):
        print(json.dumps({"status": "TIME_CAP", **progress}))
        raise SystemExit(124)

    signal(SIGALRM, timeout)
    alarm(30)
    gz = (args.input_root / "word7605.json.gz").read_bytes()
    edits_bin = (args.input_root / "edits7610.json").read_bytes()
    assert sha256(gz).hexdigest() == BASE_GZIP
    assert sha256(edits_bin).hexdigest() == PEER_EDITS
    raw = decompress(gz)
    assert sha256(raw).hexdigest() == BASE_WORD
    baseline = json.loads(raw)
    edits = json.loads(edits_bin)
    tape = baseline["program"]
    public = baseline["public"]
    assert edits["base_events"] + 5 == len(tape) == 76636 and not edits["append"]
    deleted = {clock + 5: event for clock, event in edits["delete"]}
    inserted = {clock + 5 if clock else 0: events for clock, events in edits["insert_before"]}
    assert len(deleted) == len(edits["delete"]) and len(inserted) == len(edits["insert_before"])
    assert all(event == tape[clock] for clock, event in deleted.items())
    assert {event[1] for event in deleted.values()} == {46, 588, 1456}
    candidate = json.loads(decompress(args.candidate.read_bytes()))
    projected = [event for clock, old in enumerate(tape)
                 for event in inserted.get(clock, []) + ([] if clock in deleted else [old])]
    assert candidate == {**baseline, "program": projected}

    forms = {}
    for clock, events in inserted.items():
        for event in events:
            if event[0] == "ADD":
                forms[(clock, event[2])] = input_row(tape, clock, event[2], public)
    for clock, event in deleted.items():
        if event[0] == "ADD":
            forms[(clock, event[2])] = input_row(tape, clock, event[2], public)
    coefficients = [{} for _ in range(public + baseline["owned_fields"])]
    charts = baseline["initial"] + [None] * baseline["owned_fields"]
    spans = [span(frame) for frame in baseline["frames"]]
    max_terms = 0

    def check_equal(role, label):
        actual = {}
        for key, coefficient in coefficients[role].items():
            add_scaled(actual, forms[key], coefficient)
        if actual:
            index = min(actual)
            print(json.dumps({"status": "EXCLUDE_EXACT_DELTA", "label": label, "role": role,
                              "input": index, "new_minus_old": str(actual[index]), **progress}))
            raise SystemExit(2)
        progress["checks"] += 1

    def check_chart(event):
        op, dst, *tail = event
        if op == "MOVE":
            begin, end, owned = tail
            assert charts[dst] == begin and owned == (dst >= public)
            assert spans[begin] < spans[end] or (owned and spans[end] < spans[begin])
            charts[dst] = end
        elif op == "INIT":
            assert dst >= public and charts[dst] is None
            charts[dst] = tail[0]
        elif op == "CLEAR":
            assert dst >= public and charts[dst] == tail[0]
            charts[dst] = None
        else:
            assert charts[dst] == tail[-1] and tail[-1] is not None
            if op in ("ADD", "COPY"):
                assert dst != tail[0] and charts[tail[0]] == tail[-1]
            else:
                assert op == "SCALE"

    for clock, event in enumerate(tape):
        progress["clock"] = clock
        for addition in inserted.get(clock, []):
            check_chart(addition)
            if addition[0] == "MOVE":
                continue
            op, dst, src, scalar, _ = addition
            assert op == "ADD"
            q = Fraction(scalar)
            add_scaled(coefficients[dst], coefficients[src], q)
            add_scaled(coefficients[dst], {(clock, src): q}, 1)
        op, dst, *tail = event
        if clock in deleted:
            if op == "ADD":
                add_scaled(coefficients[dst], {(clock, tail[0]): -Fraction(tail[1])}, 1)
            else:
                assert op == "MOVE"
            continue
        involved = [dst] + ([tail[0]] if op in ("ADD", "COPY") else [])
        has_owned_operand = any(role >= public for role in involved)
        if has_owned_operand and op != "INIT":
            for role in involved:
                check_equal(role, f"owned interface before baseline clock {clock}")
                private_checks += 1
        check_chart(event)
        if op == "CLEAR":
            check_equal(dst, f"CLEAR at baseline clock {clock}")
            coefficients[dst].clear()
        elif op == "INIT":
            coefficients[dst].clear()
        elif op == "SCALE" and coefficients[dst]:
            q = Fraction(tail[0])
            coefficients[dst] = {key: value * q for key, value in coefficients[dst].items()}
        elif op in ("COPY", "ADD"):
            if op == "COPY":
                check_equal(dst, f"zero COPY destination at baseline clock {clock}")
                copy_checks += 1
                coefficients[dst].clear()
            if coefficients[tail[0]]:
                add_scaled(coefficients[dst], coefficients[tail[0]], Fraction(tail[1]))
        if has_owned_operand:
            check_equal(dst, f"owned interface after baseline clock {clock}")
            private_checks += 1
        max_terms = max(max_terms, len(coefficients[dst]))

    assert charts == baseline["final"] + [None] * baseline["owned_fields"]
    assert not any(coefficients[public:])
    for role in range(public):
        check_equal(role, "final endpoint")
    assert public == 1501 and baseline["owned_fields"] == 68
    assert progress["checks"] == public + 74 + copy_checks + private_checks
    canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    receipt = {"status": "PASS_EXACT_NORMALIZED_SCALAR_DIFFERENCE", "source_word_sha256": BASE_WORD,
               "peer_edits_sha256": PEER_EDITS, "candidate_canonical_sha256": sha256(canonical).hexdigest(),
               "public_endpoint_rows": public, "empty_owned_endpoints": baseline["owned_fields"],
               "owned_clear_rows": 74, "events": len(projected),
               "zero_COPY_destinations": copy_checks,
               "owned_interface_row_checks": private_checks,
               "basis_rows": len(forms), "max_form_terms_on_common_event": max_terms,
               "last_baseline_clock": progress["clock"], "seconds_cap": 30}
    print(json.dumps(receipt, sort_keys=True))
    alarm(0)


if __name__ == "__main__":
    main()
