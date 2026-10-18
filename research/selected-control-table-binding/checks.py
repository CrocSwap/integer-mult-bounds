"""Actual selected-label fixtures and adversarial binding controls."""
from dataclasses import asdict, replace
from hashlib import sha256
import json

import binding as b
import oracle


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def indices(size):
    return sorted({0, size - 1} | {size * j // 17 for j in range(1, 17)})


def root_coupling(width, root_size):
    e = width * root_size
    b.need((width - 1) ** 10000 < e ** 17 <= width ** 10000,
           "fixture satisfies the retained original-width coupling")


def fields_for(headers):
    return b.FrozenFields.from_headers(headers)


def prepare_case(catalogue, descriptions, q=3, width=2, root_size=64**4 + 17, root_unit=2):
    root_coupling(width, root_size)
    events, headers = [], []
    for kind, request, high, field, half in descriptions:
        header = b.provider.fixture_header(catalogue, request, q, width,
                                           bad=kind != "good", high=high)
        headers.append(header)
        events.append(b.Event(kind, request, header.raw.low, field,
                              kind == "pair" and field >= 64, half))
    fields = fields_for(tuple(headers))
    compilation = b.compile_chain(q, width, root_size, root_unit,
                                  tuple(events), fields, catalogue)
    reference = b.bound_reference(compilation, fields_for(tuple(headers)), catalogue)
    return compilation, reference, tuple(events), tuple(headers)


def check_case(catalogue, descriptions, **kwargs):
    compilation, reference, events, headers = prepare_case(catalogue, descriptions, **kwargs)
    values, reads = [], set()
    for i in indices(reference.size):
        actual, meter = b.run(compilation, i)
        b.need(actual == reference.value(i), "compiled value equals actual generated descriptor")
        reads.update(meter.field_reads)
        values.append([i, actual])
    b.need(reads <= set(compilation.live_slots), "reset dead ancestry is never read")
    return {"q": compilation.program.q, "width": compilation.program.width,
            "root_size": compilation.program.root_size, "root_unit": compilation.program.unit,
            "events": [[e.kind, e.request.record(), e.field, e.reverse, e.half] for e in events],
            "final_size": reference.size, "global_slots_read": sorted(reads),
            "table_sha256": digest([asdict(t) for t in compilation.tables]),
            "values": values}, (compilation, reference, events, headers)


def actual_requests(catalogue):
    chosen = [next(r for r in catalogue.requests if r.kind == "MOVE" and r.base.rank == rank)
              for rank in range(1, 8)]
    chosen.append(next(r for r in catalogue.requests if r.kind == "IDLE" and r.base.rank == 42))
    for frame in (510, 518):
        chosen.append(next(r for r in catalogue.requests if r.kind == "COPY" and r.old_frame == frame))
    chosen += [next(r for r in catalogue.requests if r.kind == "MOVE" and r.chart.kind == "data" and r.stage == 8),
               next(r for r in catalogue.requests if r.kind == "MOVE" and r.chart.kind == "host" and r.chart.port >= 0),
               next(r for r in catalogue.requests if r.kind == "MOVE" and r.chart.kind == "host" and r.chart.port < 0)]
    return list(dict.fromkeys(chosen))


def independent_last_step(catalogue, fixture):
    compilation, reference, events, headers = fixture
    event, header = events[-1], headers[-1]
    p = oracle.actual_projector(header)
    b.need(p == header.direct_projector(), "independent raw-label projector equality")
    if len(events) == 1:
        parent = b.d.Root(compilation.program.root_size, header.q**header.width, compilation.program.unit)
    else:
        prefix = b.compile_chain(header.q, header.width, compilation.program.root_size,
                                 compilation.program.unit, events[:-1], fields_for(headers[:-1]), catalogue)
        parent = b.bound_reference(prefix, fields_for(headers[:-1]), catalogue)
    modulus = header.q**header.width
    f = parent.size // 64
    columns = sorted({0, f // 3, f // 2, f - 1})
    checked, permutation_changes = 0, 0
    signatures = []
    for t in columns:
        incoming = [parent.value(row*f + t) for row in range(64)]
        if event.kind == "good":
            pivots = oracle.weighted_good_pivots(p, incoming, event.request.base.rank, modulus)
            for k, value in enumerate(pivots):
                b.need(b.run(compilation, k*f+t)[0] == value,
                       "compiled good value equals independent weighted LU pivot")
                checked += 1
            signatures.append(pivots)
        else:
            b.need(event.kind == "pair", "independent last-step domain")
            weighted = oracle.weighted_residual(p, incoming, modulus)
            diagonal, pi = oracle.normalized_elimination(weighted, modulus)
            table = compilation.tables[-1]
            bank = incoming + [1]*64
            expected = tuple(table.diagonal[j] * bank[table.permutation[j]] *
                             pow(bank[j], -1, modulus) % modulus for j in range(128))
            b.need(diagonal == expected and pi == table.permutation,
                   "all weighted diagonal entries and original-row permutation")
            i = f - 1 - t if event.reverse else t
            b.need(b.run(compilation, i)[0] == diagonal[event.field],
                   "compiled pair value equals independent weighted elimination")
            checked += 129
            permutation_changes += sum(i != j for i, j in enumerate(pi))
            signatures.append(diagonal)
    return {"kind": event.kind, "columns": columns, "equalities": checked,
            "nonidentity_permutation_entries": permutation_changes,
            "independent_values_sha256": digest(signatures)}


def rejects(thunk, label):
    try:
        thunk()
    except ValueError:
        return label
    raise ValueError("invalid binding was accepted: " + label)


def differs(compilation, reference, label):
    for i in indices(reference.size):
        actual = b.run(compilation, i)[0]
        if actual != reference.value(i):
            return {"control": label, "index": i, "incorrect": actual, "correct": reference.value(i)}
    raise ValueError("mutation did not exercise its proposed failure: " + label)


def controls(catalogue, good_fixture, pair_fixture, reverse_fixture, reset_fixture):
    out = []
    comp, ref, events, headers = good_fixture
    h = headers[-1]
    low = replace(h, raw=replace(h.raw, high=tuple((0,)*64 for _ in range(64))))
    table = b.prepare_table(low, "good", comp.tables[-1].tag)
    out.append(differs(replace(comp, tables=comp.tables[:-1]+(table,)), ref, "low-only coefficients"))
    comp, ref, events, headers = pair_fixture
    table = replace(comp.tables[-1], permutation=tuple(range(128)))
    out.append(differs(replace(comp, tables=comp.tables[:-1]+(table,)), ref, "discard original-row permutation"))
    comp, ref, events, headers = reverse_fixture
    step = replace(comp.program.steps[-1], reverse=False)
    program = replace(comp.program, steps=comp.program.steps[:-1]+(step,))
    out.append(differs(replace(comp, program=program), ref, "omit physical atom reversal"))
    comp, ref, events, headers = reset_fixture
    q, width, n, a = comp.program.q, comp.program.width, comp.program.root_size, comp.program.unit
    out.append(rejects(lambda: b.run(replace(comp, tables=comp.tables[2:]), 0), "compact frozen slots after reset"))
    f = fields_for(headers)
    swapped = replace(f, specifications=f.specifications[:-2]+tuple(reversed(f.specifications[-2:])))
    out.append(rejects(lambda: b.compile_chain(q, width, n, a, events, swapped, catalogue), "swap exact field specifications"))
    extra = replace(f, high_matrices=f.high_matrices+(f.high_matrices[-1],),
                    specifications=f.specifications+(f.specifications[-1],))
    out.append(rejects(lambda: b.compile_chain(q, width, n, a, events, extra, catalogue), "capture current fresh matrix"))
    changed = list(events)
    alternate = next(r for r in catalogue.requests if r.base.rank == events[-1].request.base.rank and
                     r != events[-1].request)
    changed[-1] = replace(changed[-1], request=alternate)
    out.append(rejects(lambda: b.compile_chain(q, width, n, a, tuple(changed), fields_for(headers), catalogue),
                       "same-rank wrong selected request"))
    changed = events[:-1]+(replace(events[-1], reverse=False),)
    out.append(rejects(lambda: b.compile_chain(q, width, n, a, changed, fields_for(headers), catalogue),
                       "orientation not in actual macroplan"))
    good, _, ev, hs = good_fixture
    wrong_branch = (replace(ev[0], kind="pair", field=1),)
    out.append(rejects(lambda: b.compile_chain(good.program.q, good.program.width, good.program.root_size,
                                              good.program.unit, wrong_branch, fields_for(hs), catalogue),
                       "pair on a good low class"))
    wrong_reset = (replace(ev[0], kind="unit"),)
    out.append(rejects(lambda: b.compile_chain(good.program.q, good.program.width, good.program.root_size,
                                              good.program.unit, wrong_reset, fields_for(hs), catalogue),
                       "unit reset absent from macroplan"))
    out.append(rejects(lambda: fields_for(headers).unused, "unused stock is inaccessible"))
    mutated_headers = tuple(replace(h, raw=replace(h.raw, high=tuple((0,)*64 for _ in range(64))))
                            if i < 2 else h for i, h in enumerate(headers))
    changed_fields = fields_for(mutated_headers)
    changed_comp = b.compile_chain(q, width, n, a, events, changed_fields, catalogue)
    b.need(changed_fields.reads == list(comp.live_slots), "dead high fields were not prepared")
    b.need(changed_comp.tables == comp.tables, "unit reset removes dead numerical dependence")
    out.append("dead high-field change leaves tables and values unchanged")
    bad_header = pair_fixture[3][-1]
    out.append(rejects(lambda: b.prepare_table(bad_header, "good", 1), "nonunit good pivot"))
    return out


def run(catalogue):
    chosen = actual_requests(catalogue)
    records, oracle_records = [], []
    good_fixture = None
    for request in chosen:
        for high in (0, 1, 2):
            for kind, field in (("good", 0), ("pair", 0)):
                record, fixture = check_case(catalogue, [(kind, request, high, field, False)], root_size=209)
                records.append(record)
                if high == 1:
                    oracle_records.append(independent_last_step(catalogue, fixture))
                if request.base.rank == 42 and kind == "good" and high == 1:
                    good_fixture = fixture
    r42 = next(r for r in chosen if r.base.rank == 42)
    r7 = next(r for r in chosen if r.base.rank == 7)
    paths = {
        "good_pair_forward": [("good", r42, 1, 0, False), ("pair", r42, 1, 1, False)],
        "good_pair_reverse": [("good", r42, 1, 0, False), ("pair", r42, 1, 126, False)],
        "good_pair_good_pair": [("good", r42, 1, 0, False), ("pair", r7, 1, 1, False),
                                ("good", r7, 2, 0, False), ("pair", r42, 1, 126, False)],
        "good_reset_good_pair": [("good", r42, 1, 0, False), ("unit", r7, 1, 0, True),
                                 ("good", r7, 2, 0, False), ("pair", r42, 1, 126, False)],
        "good_reset_pair": [("good", r42, 1, 0, False), ("unit", r7, 1, 0, False),
                            ("pair", r42, 1, 126, False)],
    }
    fixtures = {}
    for q, width, root_size in ((3, 2, 64**4+17), (5, 2, 64**4+17), (3, 3, 2**600)):
        for name, descriptions in paths.items():
            record, fixture = check_case(catalogue, descriptions, q=q, width=width, root_size=root_size)
            record["path"] = name
            records.append(record)
            oracle_records.append(independent_last_step(catalogue, fixture))
            if (q, width) == (3, 2):
                fixtures[name] = fixture
    empty = b.compile_chain(3, 1, 1, 2, (), b.FrozenFields((), ()), catalogue)
    b.need(b.run(empty, 0)[0] == 2 and not empty.tables, "width-one root bypass")
    failure_controls = controls(catalogue, good_fixture, fixtures["good_pair_forward"],
                                fixtures["good_pair_reverse"], fixtures["good_reset_good_pair"])
    catalogue_receipt = catalogue.receipt()
    # The reused producer exposes integer histogram keys; the receipt boundary
    # is JSON, whose object keys are strings. Normalize this one known mapping
    # before strict comparison, without relaxing any value types or fields.
    catalogue_receipt["rank_histogram"] = {
        str(k): v for k, v in catalogue_receipt["rank_histogram"].items()}
    return {"status": "PASS_SELECTED_CONTROL_TABLE_BINDING",
            "catalogue": catalogue_receipt, "selected_request_representatives": len(chosen),
            "fixture_cases": len(records), "coordinate_equalities": sum(len(r["values"]) for r in records),
            "independent_local_oracles": oracle_records,
            "independent_equalities": sum(r["equalities"] for r in oracle_records),
            "width_one_root": True, "controls": failure_controls, "fixtures": records,
            "scope": "Actual selected-label coefficient binding and conditional structural proof; no complete payload, physical runtime, supplier admission or new kappa."}
