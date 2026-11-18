"""Separately written finite integer-row/CLEAR audit for explicit input files.

The source check.py is neither imported nor changed. A caller chooses a common
grid; no candidate hash is an acceptance condition. This finite ideal audit is
not native column/phase, precision/tape, physical caller or supplier admission.
Apache-2.0; prepared with OpenAI Codex assistance.
"""

import argparse
import collections
import functools
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

DEFAULT_GRID = 10125 * (1 << 21)


class AuditFailure(ValueError):
    def __init__(self, kind, details):
        super().__init__(f"{kind}: {details}")
        self.kind = kind
        self.details = details


def need(condition, kind, details):
    if not condition:
        raise AuditFailure(kind, details)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def exact_divide(numerator, denominator, context):
    need(type(denominator) is int and denominator > 0, "DIVISOR_DOMAIN", context)
    quotient, remainder = divmod(numerator, denominator)
    need(remainder == 0, "NONEXACT_INTEGER_DIVISION", {
        **context, "numerator": str(numerator), "denominator": str(denominator), "remainder": str(remainder)})
    return quotient


def frame_spans(frames):
    need(isinstance(frames, list), "FRAME_DOMAIN", "frames list required")
    result, cache = [], {}
    for index, frame in enumerate(frames):
        need(isinstance(frame, list), "FRAME_DOMAIN", {"frame": index})
        need(all(type(value) is int and 0 < value < 512 for value in frame), "FRAME_VECTOR_DOMAIN", {"frame": index})
        key = tuple(frame)
        if key not in cache:
            closed = {0}
            for value in frame:
                need(value not in closed, "FRAME_NOT_INDEPENDENT", {"frame": index, "vector": value})
                closed |= {value ^ other for other in closed}
            cache[key] = frozenset(closed)
        result.append(cache[key])
    return result


def intended_rows(word, grid):
    """Direct forward target formula, independently encoded as integer rows."""
    public = word["public"]
    live, hosted = word.get("live"), word.get("hosted")
    need(isinstance(live, list) and isinstance(hosted, dict), "TARGET_HEADER", "live and hosted required")
    dports, xs, ys = hosted.get("Dports"), hosted.get("X2"), hosted.get("Y2")
    need(isinstance(dports, list) and isinstance(xs, list) and isinstance(ys, list) and len(xs) == len(ys),
         "TARGET_HEADER", "Dports/X2/Y2 required")
    need(all(type(index) is int and 0 <= index < len(live) for index in dports), "TARGET_HEADER", "Dports index")
    need(all(type(field) is int and 0 <= field < public and field + 112 < public for field in live),
         "TARGET_HEADER", "live pair outside public domain")
    need(all(type(field) is int and 0 <= field < public for field in xs + ys), "TARGET_HEADER", "hosted field")
    dports = set(dports)
    pairs = [(field, field + 112, index in dports) for index, field in enumerate(live)]
    used = [field for first, second, _ in pairs for field in (first, second)] + xs + ys
    need(len(used) == len(set(used)), "TARGET_HEADER", "target blocks must be disjoint")
    rows = [{field: grid} for field in range(public)]
    for first, second, is_d in pairs:
        if is_d:
            rows[first], rows[second] = {first: grid}, {first: grid, second: grid}
        else:
            half = exact_divide(grid, 2, {"phase": "intended target"})
            rows[first], rows[second] = {first: grid, second: -grid}, {first: half, second: half}
    for first, second in zip(xs, ys, strict=True):
        rows[first], rows[second] = {first: grid, second: -grid}, {second: grid}
    return rows


def audit_word(word, certificates, grid=DEFAULT_GRID, header_reference=None):
    """One forward integer program pass: legality, endpoint and every CLEAR.

    CLEAR certificate sources may be any other live public or owned fields,
    at any chart, exactly as the read #7620-rule implementation. Certificate
    denominators are cleared for the whole sum; no extra per-term grid gate.
    """
    need(type(grid) is int and grid > 0, "GRID_DOMAIN", "positive common denominator required")
    need(isinstance(word, dict), "WORD_DOMAIN", "word object required")
    public, owned = word.get("public"), word.get("owned_fields")
    need(type(public) is int and public > 0 and type(owned) is int and owned >= 0, "STATE_DOMAIN", "public/owned_fields")
    count = public + owned
    program, frames = word.get("program"), word.get("frames")
    need(isinstance(program, list), "PROGRAM_DOMAIN", "program list required")
    spans = frame_spans(frames)
    initial, final = word.get("initial"), word.get("final")
    need(isinstance(initial, list) and isinstance(final, list) and len(initial) == len(final) == public,
         "CHART_DOMAIN", "complete public initial/final charts required")

    def chart_ok(chart):
        return type(chart) is int and 0 <= chart < len(spans)

    need(all(chart_ok(chart) for chart in initial + final), "CHART_DOMAIN", "header chart outside frames")
    header_matches = None
    if header_reference is not None:
        need(isinstance(header_reference, dict), "HEADER_REFERENCE_DOMAIN", "header object or word required")
        header_matches = ({key: value for key, value in word.items() if key != "program"}
                          == {key: value for key, value in header_reference.items() if key != "program"})
        need(header_matches, "HEADER_REFERENCE_MISMATCH", "all non-program header fields must match the explicit reference")
    need(isinstance(certificates, dict) and isinstance(certificates.get("clear_event_index"), dict),
         "CERTIFICATE_DOMAIN", "clear_event_index mapping required")
    raw_certs = certificates["clear_event_index"]
    parsed_certs, scalar_cache = {}, {}
    literal_denominators_smooth, certificate_denominator_lcm = True, 1

    def scalar(raw, context):
        need(type(raw) in (str, int), "SCALAR_DOMAIN", context)
        key = type(raw).__name__, raw
        if key not in scalar_cache:
            try:
                value = Fraction(raw)
            except (ValueError, ZeroDivisionError) as error:
                raise AuditFailure("SCALAR_DOMAIN", context) from error
            scalar_cache[key] = value.numerator, value.denominator
        return scalar_cache[key]

    for key, certificate in raw_certs.items():
        need(isinstance(key, str) and key.isdecimal() and str(int(key)) == key,
             "CERTIFICATE_EVENT_DOMAIN", {"key": str(key)})
        event = int(key)
        need(0 <= event < len(program) and isinstance(program[event], list) and program[event]
             and program[event][0] == "CLEAR", "CERTIFICATE_EVENT_DOMAIN", {"event": event})
        need(isinstance(certificate, dict), "CERTIFICATE_DOMAIN", {"event": event})
        terms = {}
        for source, coefficient in certificate.items():
            need(isinstance(source, str) and source.isdecimal() and str(int(source)) == source,
                 "CERTIFICATE_SOURCE_DOMAIN", {"event": event, "source": str(source)})
            field = int(source)
            need(0 <= field < count, "CERTIFICATE_SOURCE_DOMAIN", {"event": event, "source": field})
            terms[field] = scalar(coefficient, {"phase": "certificate", "event": event, "source": field})
        parsed_certs[event] = terms
    rows = [{field: grid} if field < public else {} for field in range(count)]
    current = list(initial) + [None] * owned
    alive, init_chart, labels = set(), {}, set()
    lifetimes, opcode_counts, public_ranks = collections.Counter(), collections.Counter(), collections.Counter()
    peak, seen, word_divisions = 0, 0, 0
    certificate_divisions, certificate_terms, owned_certificate_terms = 0, 0, 0
    zero_clears, zero_with_nonempty_certificate, largest_certificate = 0, 0, 0
    row_denominator_gcd, max_scaled_bits, max_reduced_numerator_bits = grid, 0, 0

    @functools.lru_cache(maxsize=65536)
    def coefficient_signature(value):
        divisor = math.gcd(value, grid)
        numerator = exact_divide(value, divisor, {"phase": "row statistic"})
        return numerator.bit_length(), divisor

    def note(value):
        nonlocal row_denominator_gcd, max_scaled_bits, max_reduced_numerator_bits
        if value:
            absolute = abs(value)
            numerator_bits, divisor = coefficient_signature(absolute)
            row_denominator_gcd = math.gcd(row_denominator_gcd, divisor)
            max_scaled_bits = max(max_scaled_bits, absolute.bit_length())
            max_reduced_numerator_bits = max(max_reduced_numerator_bits, numerator_bits)

    def multiplied(value, numerator, denominator, event, column):
        nonlocal word_divisions
        product = value * numerator
        if denominator == 1:
            return product
        word_divisions += 1
        return exact_divide(product, denominator, {"phase": "program scalar", "event": event, "input_column": column})

    for index, event in enumerate(program):
        need(isinstance(event, list) and len(event) >= 2, "EVENT_SHAPE", {"event": index})
        op, field = event[:2]
        need(type(field) is int and 0 <= field < count, "REGISTER_DOMAIN", {"event": index})
        need(op in ("MOVE", "INIT", "CLEAR", "ADD", "COPY", "SCALE"), "UNKNOWN_OPCODE", {"event": index, "op": op})
        opcode_counts[op] += 1
        if op == "INIT":
            need(len(event) == 3 and field >= public and field not in alive and chart_ok(event[2]),
                 "INIT_LEGALITY", {"event": index, "field": field})
            alive.add(field)
            rows[field], current[field], init_chart[field] = {}, event[2], event[2]
            labels.add(field)
            peak = max(peak, len(alive))
        elif op == "CLEAR":
            need(len(event) == 3 and field >= public and field in alive and chart_ok(event[2]) and current[field] == event[2],
                 "CLEAR_LEGALITY", {"event": index, "field": field})
            need(index in parsed_certs, "MISSING_CLEAR_CERTIFICATE", {"event": index, "field": field})
            terms = parsed_certs[index]
            need(all(source != field and (source < public or source in alive) for source in terms),
                 "CERTIFICATE_SOURCE_NOT_OTHER_LIVE", {"event": index, "field": field})
            denominator = 1
            for _, term_denominator in terms.values():
                denominator = exact_divide(denominator * term_denominator, math.gcd(denominator, term_denominator),
                                           {"phase": "certificate lcm", "event": index})
                certificate_divisions += 1
            certificate_denominator_lcm = exact_divide(certificate_denominator_lcm * denominator,
                math.gcd(certificate_denominator_lcm, denominator), {"phase": "certificate global lcm", "event": index})
            certificate_divisions += 1
            combined = {}
            for source, (numerator, term_denominator) in terms.items():
                factor = numerator * exact_divide(denominator, term_denominator,
                                                   {"phase": "certificate denominator clearing", "event": index})
                certificate_divisions += 1
                for column, value in rows[source].items():
                    total = combined.get(column, 0) + factor * value
                    if total:
                        combined[column] = total
                    else:
                        combined.pop(column, None)
            wanted = {column: denominator * value for column, value in rows[field].items()}
            need(combined == wanted, "CLEAR_CERTIFICATE_EQUALITY", {"event": index, "field": field,
                 "first_differing_input": next((column for column in sorted(set(combined) | set(wanted))
                                                if combined.get(column, 0) != wanted.get(column, 0)), None)})
            seen += 1
            certificate_terms += len(terms)
            owned_certificate_terms += sum(source >= public for source in terms)
            largest_certificate = max(largest_certificate, len(terms))
            zero_clears += not bool(rows[field])
            zero_with_nonempty_certificate += not bool(rows[field]) and bool(terms)
            lifetimes[(field, init_chart.pop(field), event[2])] += 1
            alive.remove(field)
            rows[field], current[field] = {}, None
        elif op == "MOVE":
            need(len(event) == 5 and chart_ok(event[2]) and chart_ok(event[3])
                 and type(event[4]) is bool and event[4] == (field >= public)
                 and current[field] == event[2] and (field < public or field in alive),
                 "MOVE_LEGALITY", {"event": index, "field": field})
            before, after = event[2:4]
            if field < public:
                need(spans[before] < spans[after], "PUBLIC_MOVE_NOT_ASCENT", {"event": index})
                public_ranks[len(frames[after]) - len(frames[before])] += 1
            else:
                need(spans[before] < spans[after] or spans[after] < spans[before],
                     "OWNED_MOVE_NOT_NESTED", {"event": index})
            current[field] = after
        else:
            wanted_length = 4 if op == "SCALE" else 5
            need(len(event) == wanted_length, "EVENT_SHAPE", {"event": index, "op": op})
            chart = event[-1]
            need(chart_ok(chart) and current[field] == chart and (field < public or field in alive),
                 "ARITHMETIC_TARGET_NOT_LIVE_AT_CHART", {"event": index, "field": field})
            numerator, denominator = scalar(event[2] if op == "SCALE" else event[3], {"phase": "literal", "event": index})
            need(numerator != 0, "ZERO_LITERAL_COEFFICIENT", {"event": index})
            residue = denominator
            for prime in (2, 3, 5):
                while residue % prime == 0:
                    residue = exact_divide(residue, prime, {"phase": "literal smoothness", "event": index})
            literal_denominators_smooth = literal_denominators_smooth and residue == 1
            if op == "SCALE":
                rows[field] = {column: multiplied(value, numerator, denominator, index, column)
                               for column, value in rows[field].items()}
                for value in rows[field].values():
                    note(value)
            else:
                source = event[2]
                need(type(source) is int and 0 <= source < count and source != field
                     and current[source] == chart and (source < public or source in alive),
                     "ARITHMETIC_SOURCE_NOT_OTHER_LIVE_AT_CHART", {"event": index, "source": source})
                need(op != "COPY" or not rows[field], "COPY_TARGET_NOT_ZERO", {"event": index, "field": field})
                for column, value in rows[source].items():
                    total = rows[field].get(column, 0) + multiplied(value, numerator, denominator, index, column)
                    if total:
                        rows[field][column] = total
                        note(total)
                    else:
                        rows[field].pop(column, None)
    need(seen == len(parsed_certs), "UNUSED_CLEAR_CERTIFICATE", {"seen": seen, "provided": len(parsed_certs)})
    need(not alive and not init_chart and all(value is None for value in current[public:]),
         "UNCLOSED_OWNED_LIFETIME", {"alive": sorted(alive)})
    need(current[:public] == final, "FINAL_CHART_MISMATCH", "public endpoints")
    need(all(not row for row in rows[public:]), "OWNED_ENDPOINT_NOT_EMPTY", "owned endpoints")
    intended = intended_rows(word, grid)
    differing = [field for field in range(public) if rows[field] != intended[field]]
    need(not differing, "INTENDED_OPERATOR_MISMATCH", {"first_public_rows": differing[:8]})
    denominator_lcm = exact_divide(grid, row_denominator_gcd, {"phase": "observed grid lcm"})
    two_exponent = (denominator_lcm & -denominator_lcm).bit_length() - 1
    odd_lcm = exact_divide(denominator_lcm, 1 << two_exponent, {"phase": "observed odd grid"})
    return {"status": "PASS_FINITE_INTEGER_ROWS_AND_CLEAR_RELATIONS", "public": public, "owned_fields": owned,
            "events": len(program), "opcodes": dict(opcode_counts), "single_forward_program_pass": True,
            "header_matches_reference": header_matches, "header_reference_program_replayed": False,
            "grid_denominator_supplied": grid, "all_program_scalar_divisions_exact": True,
            "nontrivial_program_term_divisions_checked": word_divisions,
            "certificate_denominator_divisions_checked": certificate_divisions,
            "observed_row_denominator_lcm": denominator_lcm, "observed_max_den_exp": two_exponent,
            "observed_odd_denominator_lcm": odd_lcm, "max_reduced_numerator_bits": max_reduced_numerator_bits,
            "max_scaled_integer_bits": max_scaled_bits, "literal_denominators_5_smooth": literal_denominators_smooth,
            "clear_certificates": seen, "certificate_terms": certificate_terms,
            "live_owned_certificate_terms": owned_certificate_terms,
            "certificate_coefficient_denominator_lcm": certificate_denominator_lcm,
            "largest_certificate": largest_certificate, "zero_clear_rows": zero_clears,
            "zero_rows_with_nonempty_valid_certificate": zero_with_nonempty_certificate,
            "certificate_rule": "Exact equality with other live public/owned rows; source charts need not coincide",
            "owned_lifetimes": sum(lifetimes.values()), "owned_peak": peak, "owned_labels_used": len(labels),
            "owned_lifetime_profile": [{"field": field, "initial_chart": begin, "clear_chart": end, "count": value}
                                       for (field, begin, end), value in sorted(lifetimes.items())],
            "public_ascent_ranks": dict(public_ranks), "intended_A_matches": True,
            "integer_endpoint_rows_sha256": sha(canonical(rows)),
            "scope": "Finite ideal scalar/operator/CLEAR evidence only; not precision/tape/native-column/phase/physical/cost/provider admission"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "DUPLICATE_JSON_KEY", str(key))
        result[key] = value
    return result


def read_json(path):
    raw = Path(path).read_bytes()
    payload = gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw
    return json.loads(payload, object_pairs_hook=_unique_object), raw


def run_audit(word_path, certificate_path, header_path, out, grid=DEFAULT_GRID, source_pins_path=None):
    out = Path(out)
    need(not out.exists(), "OUTPUT_EXISTS", "new output directory required")
    word, word_raw = read_json(word_path)
    certs, cert_raw = read_json(certificate_path)
    header, header_raw = read_json(header_path)
    bindings = {"word": {"name": Path(word_path).name, "file_sha256": sha(word_raw), "canonical_sha256": sha(canonical(word))},
                "clear_certificates": {"name": Path(certificate_path).name, "file_sha256": sha(cert_raw)},
                "header_reference_only": {"name": Path(header_path).name, "file_sha256": sha(header_raw), "program_replayed": False},
                "our_separately_written_audit": {"name": Path(__file__).name, "file_sha256": sha(Path(__file__).read_bytes()),
                                                "role": "Our integer interpreter; source check.py not imported or executed"}}
    if source_pins_path is not None:
        pins, pins_raw = read_json(source_pins_path)
        by_hash = collections.defaultdict(list)
        for item in pins.get("files", []):
            by_hash[item["sha256"]].append(item["path"])
        bindings["optional_source_manifest"] = {"name": Path(source_pins_path).name, "file_sha256": sha(pins_raw),
            "reported_head": pins.get("head"), "source_pr": pins.get("source_pr"),
            "word_hash_listed_as": by_hash.get(sha(word_raw), []), "certificate_hash_listed_as": by_hash.get(sha(cert_raw), []),
            "scope": "Provenance identification only; no fixed source hash is a finite audit acceptance condition"}
    try:
        report = audit_word(word, certs, grid, header)
    except AuditFailure as error:
        report = {"status": "REJECTED_FINITE_INTEGER_AUDIT", "kind": error.kind, "details": error.details,
                  "scope": "This input/grid/protocol rejection only; no global framework impossibility claim"}
    report["source_bindings"] = bindings
    out.mkdir(parents=True)
    (out / "AUDIT.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--certificates", type=Path, required=True)
    parser.add_argument("--header-reference", type=Path, required=True)
    parser.add_argument("--grid", type=int, default=DEFAULT_GRID)
    parser.add_argument("--source-pins", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run_audit(args.word, args.certificates, args.header_reference, args.out, args.grid, args.source_pins)
    except (AuditFailure, ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({"status": "INPUT_ERROR", "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "PASS_FINITE_INTEGER_ROWS_AND_CLEAR_RELATIONS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
