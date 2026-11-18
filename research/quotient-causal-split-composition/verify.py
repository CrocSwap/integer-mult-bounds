"""Check two literal causal splits on the fixed compact helper graph."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from basis_engine import Graph, basis, encoded, histogram, layouts, require, sparse, vector_sum

COMPACT = "16e99893a2c669467ce74f214e8eb5150402f0267aaa8d67aad5d870aa4d5c18"


def read_graph(name):
    value = json.loads(gzip.decompress((HERE / name).read_bytes()))
    if "first_output" in value:
        graph = Graph(value["initial"], value["final"],
                      {k: (a, b) for k, a, b in value["moves"]},
                      {k: sparse(row) for k, row in value["forms"]}, value["first_output"])
    else:
        graph = Graph(value["initial"], value["final"],
                      {int(k): tuple(pair) for k, pair in value["moves"].items()},
                      {int(k): {int(d): Fraction(q) for d, q in row.items()}
                       for k, row in value["forms"].items()}, value["first"])
    graph.order()
    return graph, value


def fractions(value):
    denominator, row = value
    return {k: Fraction(v, denominator) for k, v in row.items()}


def add(row, donor, factor):
    result = dict(row)
    for k, value in donor.items():
        result[k] = result.get(k, 0) + factor * value
    return {k: v for k, v in result.items() if v}


def literals(source):
    records = []
    for role, fresh, chart in ((126, 1501, 498), (281, 1503, 595)):
        require(source.initial[role] == 3 and source.final[role] == chart and
                (source.initial[fresh], source.final[fresh]) == (chart, 127), "source split owners")
        prefix = source.forms[source.first + role]
        inject = {k: row[~fresh] for k, row in source.forms.items() if ~fresh in row}
        require(inject and all(k in source.moves and source.moves[k][0] == chart for k in inject),
                "source departure injection")
        records.append(dict(role=role, source_fresh=fresh, chart=chart, prefix=prefix, inject=inject))
    return records


def evidence(graph, record, mains):
    prefix, inject, chart = record["prefix"], record["inject"], record["chart"]
    for k in prefix:
        require(k in graph.moves and graph.moves[k][1] == chart, "prefix bank")
    require(all(k in graph.moves and graph.moves[k][0] == chart for k in inject), "injection bank")
    ancestors, pending = set(), list(prefix)
    while pending:
        k = pending.pop()
        if k < 0 or k in ancestors:
            continue
        ancestors.add(k)
        pending.extend(graph.forms[k])
    require(not ancestors.intersection(inject), "readout depends on its injection")
    values, forward_products, _ = basis(graph, prefix)
    ell = fractions(vector_sum((q, values[k]) for k, q in prefix.items()))
    responses, reverse_products, _ = basis(graph.transpose(), inject)
    direction = fractions(vector_sum((q, responses[k]) for k, q in inject.items()))
    group = {r for r, (a, b) in enumerate(zip(graph.initial, graph.final))
             if r not in mains and (a, b) == (3, 127)}
    require(ell.keys() <= group and direction.keys() <= group, "helper-only readout and response")
    pairing = sum(q * direction.get(k, 0) for k, q in ell.items())
    require(pairing == 1, "literal unit pairing")
    return ell, direction, group, dict(entrance_terms=len(ell), response_terms=len(direction),
                                      pairing=str(pairing), prefix_ancestors=len(ancestors),
                                      products=[forward_products, reverse_products])


def construct(graph, record, mains, role, *, compensation=True, decoding=True):
    ell, direction, group, audit = evidence(graph, record, mains)
    require(role in group and ell.get(role), "retired helper pivot")
    encoding = {}
    for j in group:
        if j == role:
            encoding[~j] = {~i: -q / ell[role] for i, q in ell.items() if i != role}
            encoding[~j][~role] = direction.get(j, 0)
        else:
            encoding[~j] = {~j: Fraction(1), ~role: direction.get(j, 0)}
    forms = {}
    for k, row in graph.forms.items():
        new = {}
        for donor, value in row.items():
            new = add(new, encoding.get(donor, {donor: Fraction(1)}), value)
        forms[k] = new
    fresh = len(graph.initial)
    for k, value in record["inject"].items():
        forms[k] = add(forms[k], {~fresh: Fraction(1)}, value)
        if compensation:
            forms[k] = add(forms[k], record["prefix"], -value)
    output = {}
    for j, value in ell.items():
        output = add(output, forms[graph.first + j], value)
    if decoding:
        for j in group - {role}:
            forms[graph.first + j] = add(forms[graph.first + j], output, -direction.get(j, 0))
    forms[graph.first + role] = dict(record["prefix"])
    forms[graph.first + fresh] = output
    final = list(graph.final)
    final[role] = record["chart"]
    final.append(127)
    result = Graph(graph.initial + [record["chart"]], final, dict(graph.moves), forms, graph.first)
    result.order()
    return result, audit, direction


def serialized_vector(row):
    return [[k, str(v)] for k, v in sorted(row.items())]


def full_invoice(hist, fixed):
    total = Counter({int(k): v for k, v in fixed.items()})
    total.update({k: 16 * v for k, v in hist.items()})
    return {str(k): v for k, v in sorted(total.items())}


def summary(invoice):
    return {field: dict(jobs=sum(counts.values()), mass=sum(int(k)*v for k, v in counts.items()))
            for field, counts in invoice.items()}


def run():
    for pin in json.loads((HERE / "SOURCE-PINS.json").read_text())["files"]:
        require(sha256((HERE / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                "input identity " + pin["path"])
    graph, value = read_graph("compact.json.gz")
    require(sha256(encoded(value)).hexdigest() == COMPACT, "compact source hash")
    parent, _ = read_graph("parent.json.gz")
    source, _ = read_graph("source-split-circuit.json.gz")
    interface = json.loads((HERE / "interface.json").read_text())
    parent_interface = json.loads((HERE / "parent-interface.json").read_text())
    mains, original_mains = set(interface["main_roles"]), set(parent_interface["main_roles"])
    keep = interface["keep"]
    require(len(keep) == len(graph.initial) == 1468 and len(mains) == 400 and
            {keep[r] for r in mains} == original_mains and 239 not in keep, "compact main labels")
    frames = value["frames"]
    require(len(frames[3]) == 0 and len(frames[127]) == 9, "source helper rank")
    require(92659 in source.forms[source.first + 239] and 92659 not in graph.moves and
            ~1502 in source.forms[93428] and 93428 not in graph.moves, "excluded literal split")
    old_hist = histogram(graph, frames, mains)
    reference, reference_products, _ = basis(graph, graph.forms)
    for r in range(len(graph.initial)):
        row = reference[graph.first + r]
        require(row[1].keys() <= mains if r in mains else row == (1, {r: 1}), "compact endpoint split")
    initial_paid = graph.moves
    parent_terms = sum(map(len, graph.forms.values()))
    records, controls, certificates = [], [], []
    for literal in literals(source):
        _, _, _, positive = evidence(parent, literal, original_mains)
        before = graph
        role, fresh = keep.index(literal["role"]), len(before.initial)
        ell, response, _, independent = evidence(before, literal, mains)
        graph, audit, direction = construct(before, literal, mains, role)
        require(graph.moves == initial_paid, "paid inventory and routes changed")
        rows, products, _ = basis(graph, graph.forms)
        for r in range(len(graph.initial)):
            expected = reference[graph.first + r] if r in mains else (1, {r: 1})
            require(rows[graph.first + r] == expected, "joint arbitrary-input endpoint")
        bad, _, _ = construct(before, literal, mains, role, compensation=False)
        bad_rows, _, _ = basis(bad, [bad.first + fresh])
        bad_row = fractions(bad_rows[bad.first + fresh])
        require(bad_row.get(role) == 1 and bad_row.get(fresh) == 1,
                "missing compensation control")
        controls.append(dict(chart=literal["chart"], fault="omit subtraction of the prefix",
                             input_role=role, input_value=1, observed_fresh=1, expected_fresh=0))
        bad, _, _ = construct(before, literal, mains, role, decoding=False)
        other = next(j for j in sorted(direction) if j != role)
        bad_rows, _, _ = basis(bad, [bad.first + other])
        bad_value = fractions(bad_rows[bad.first + other]).get(fresh, 0)
        require(bad_value == direction[other] != 0, "missing decoder control")
        controls.append(dict(chart=literal["chart"], fault="omit exit decoder", input_role=fresh,
                             input_value=1, output_role=other, observed=str(bad_value), expected=0))
        saved = [len(frames[literal["chart"]]), 9 - len(frames[literal["chart"]])]
        require(sum(saved) == 9 and all(0 < d < 9 for d in saved), "target rank split")
        records.append(dict(chart=literal["chart"], source_role=literal["role"], compact_role=role,
                            fresh_role=fresh, target_ranks=saved, source_positive_control=positive,
                            compact_evidence=audit, public_rows=len(graph.initial),
                            all_row_products=products, scalar_terms=sum(map(len, graph.forms.values()))))
        certificates.append(dict(chart=literal["chart"], readout=serialized_vector(ell),
                                 response=serialized_vector(response),
                                 prefix=serialized_vector(literal["prefix"]),
                                 injection=serialized_vector(literal["inject"])))
    desired = {graph.first + i: {} for i in range(len(graph.initial))}
    for r in range(len(graph.initial)):
        denominator, row = reference[graph.first + r] if r in mains else (1, {r: 1})
        for i, v in row.items():
            desired[graph.first + i][r] = Fraction(v, denominator)
    reversed_rows, reverse_products, _ = basis(graph.transpose(), desired)
    require(all(fractions(reversed_rows[k]) == row for k, row in desired.items()), "joint transpose endpoint")
    new_hist = histogram(graph, frames, mains)
    expected_targets = old_hist[1].copy()
    expected_targets.subtract({9: 2})
    expected_targets.update([4, 5, 1, 8])
    require(new_hist[0] == old_hist[0] and new_hist[1] == expected_targets, "all native target debits")
    missing_debits = old_hist[1].copy()
    missing_debits.update([4, 5, 1, 8])
    require(missing_debits != new_hist[1], "missing rank-nine target debits accepted")
    application = json.loads((HERE / "parent-application.json").read_text())
    fixed = [application["caller"]["fixed_caller_paid"], application["caller"]["fixed_root_targets"]]
    invoices = [{key: full_invoice(hist, base) for key, hist, base in zip(("paid", "targets"), pair, fixed)}
                for pair in (old_hist, new_hist)]
    require(all(invoices[0][k] == application["invoice"][k] for k in ("paid", "targets")),
            "source full invoice")
    totals = list(map(summary, invoices))
    require(totals[0]["paid"] == totals[1]["paid"] == {"jobs": 100416, "mass": 268368} and
            totals[0]["targets"] == {"jobs": 20624, "mass": 269696} and
            totals[1]["targets"] == {"jobs": 20656, "mass": 269696}, "full signed totals")
    digest = sha256(encoded(layouts(graph, frames))).hexdigest()
    return dict(status="PASS_QUOTIENT_CAUSAL_SPLIT_COMPOSITION", parent_sha256=COMPACT,
                candidate_sha256=digest, records=records, certificates=certificates,
                compact_parent_products=reference_products, transpose_products=reverse_products,
                public=1470, mains=400, helpers=1070, paid_native=len(graph.moves),
                scalar_terms={"parent":parent_terms, "candidate":sum(map(len, graph.forms.values()))},
                invoice_totals=totals, invoices=invoices, controls=controls,
                missing_target_debit_rejected=True, physical_admission_checked=False,
                source_chart480_excluded="role 239 and its prefix/injection banks were removed")


if __name__ == "__main__":
    result = json.loads(json.dumps(run()))
    path = HERE / "RESULT.json"
    if path.exists():
        require(result == json.loads(path.read_text()), "receipt mismatch")
        print(result["status"], result["public"], result["paid_native"], result["helpers"])
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
