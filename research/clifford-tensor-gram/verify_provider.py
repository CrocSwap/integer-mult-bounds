"""Check the complete selected provider and the fixed pair-fusion domain.

Use --write to save receipts. Normal replay does not change package files.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compact
import certify as c
import provider as p
from check_witness import word_endpoint
from quadratic import Paths, partial_inner, inverse_circuit
from verify import source_integrity

HERE = Path(__file__).resolve().parent


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def saved(name, value, write):
    raw = canonical(value)
    path = HERE / "provider" / name
    if write:
        path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith(".gz") else raw)
    else:
        expected = path.read_bytes()
        if name.endswith(".gz"):
            expected = gzip.decompress(expected)
        p.need(expected == raw, "Provider receipt differs: " + name)
    return hashlib.sha256(raw).hexdigest()


def equal(left, right):
    a, b = Paths(p.N, left), Paths(p.N, right)
    value = partial_inner(a, b) / p.D
    p.need(value == 1, "Exact native Gram equality with absolute phase")
    return a


def check_catalogue(model, data, audits):
    expected = {(a, b, direction): rank for direction, audit in audits.items()
                for (a, b), rank in audit["pairs"].items()}
    header, *records = data["paid"]
    raw = gzip.decompress((HERE / "provider/WORD.json.gz").read_bytes())
    p.need(header["word_payload_sha256"] == hashlib.sha256(raw).hexdigest()
           and not header["partial"], "Complete catalogue bound to the exact word")
    seen, traces = set(), {}
    for row in records:
        a, b, direction = row["input"], row["output"], row["direction"]
        key = a, b, direction
        p.need(key in expected and key not in seen and row["rank"] == row["recipe"]["rank"] == expected[key],
               "Unique actual paid class and rank")
        actual = equal(model.edge(a, b, direction), p.recipe(row["recipe"]))
        traces[key] = actual.trace() / p.D
        seen.add(key)
    p.need(seen == set(expected) and len(seen) == header["expected_complete_oriented_classes"],
           "All oriented paid classes, without gaps")

    warp_records = {(row["operator"], row["input"], row["output"]): row
                    for row in data["phases"]["actual_warp_classes"]}
    p.need(len(warp_records) == len(data["phases"]["actual_warp_classes"]), "No duplicate warp classes")
    for direction, audit in audits.items():
        p.need(set(warp_records) == audit["warps"], "All actual native warp classes")
        for (signed, a, b), row in warp_records.items():
            rec = row["recipes"][direction]
            p.need(rec["rank"] == 0, "Every warp is a monomial")
            equal(model.warp(signed, a, b, direction), p.recipe(rec))

    helpers = {}
    for row in data["helpers"]["new_physical_edges_and_boundaries"]:
        helpers[row["old"], row["new"]] = row
    for row in data["phases"]["changed_helper_boundaries"]:
        helpers[row["input"], row["output"]] = row
    actual_helpers = Counter(zip(model.c["start"][224:], model.c["final"][224:]))
    helper_profile = Counter()
    for (a, b), count in sorted(actual_helpers.items()):
        u, v = model.c["frames"][a], model.c["frames"][b]
        r = len(v)-len(u)
        p.need(r > 0 and p.rank(u+v) == len(v), "Strict productive helper boundary")
        helper_profile[r] += count
        for direction in ("forward", "backward"):
            rec = helpers[a, b]["recipes"][direction]
            p.need(rec["rank"] == r, "Complete helper recipe rank")
            equal(model.edge(a, b, direction), p.recipe(rec))

    adapters = json.loads((HERE / "provider/MAIN-ADAPTERS.json").read_bytes())
    adapter_seen = set()
    for row in adapters:
        entrance, register, f = row["entrance"], row["role"], row["frame"]
        p.need(type(entrance) is bool and type(register) is int and 0 <= register < 224,
               "Main adapter label")
        key = entrance, register
        p.need(key not in adapter_seen and f == model.c["start" if entrance else "final"][register],
               "Exact complete adapter boundary")
        p.need(row["recipe"]["rank"] == 0, "Main adapter is a monomial")
        target = inverse_circuit(p.N, model.old_frame(register, entrance)) + model.frame(f)
        decoded = p.recipe(row["recipe"])
        for direction in ("forward", "backward"):
            equal(target if direction == "forward" else p.conjugate(target),
                  decoded if direction == "forward" else p.conjugate(decoded))
        adapter_seen.add(key)
    p.need(adapter_seen == {(side, r) for side in (False, True) for r in range(224)},
           "All main adapters in both orientations")
    return traces, dict(paid_oriented_classes=len(seen), warp_oriented_classes=2*len(warp_records),
                        helper_oriented_classes=2*len(actual_helpers), helper_roles=sum(actual_helpers.values()),
                        helper_profile=dict(sorted(helper_profile.items())),
                        main_adapter_oriented_classes=2*len(adapter_seen))


def fusion_census(model, traces):
    evidence, trace_counts, kinds, ranks = {}, Counter(), Counter(), Counter()
    for direction, program in model.word["programs"].items():
        rows = []
        for pair in p.fusion_pairs(program):
            row = p.contact_witness(program, pair)
            a, b, c0, d = row["frames"]
            for name, key in (("late_trace", (a, b, direction)), ("early_trace", (c0, d, direction))):
                tau = traces[key]
                # f=1: Re(tau)<=1/2. f>=2: |tau|^f<=1/2.
                p.need(tau.real <= Q(1, 2) and c.norm2(tau) <= Q(1, 2), "Uniform noncentral trace bound")
                row[name] = str(tau)
                trace_counts[str(tau)] += 1
            p.need(Q(row["coefficient"]) != 0, "Nonzero contact coefficient")
            kinds[direction + ("_row" if row["output"] == row["role"] else "_column")] += 1
            ranks[str(row["ranks"])] += 1
            rows.append(row)
        evidence[direction] = rows
    minimum = min(Q(row["coefficient"])**2 for rows in evidence.values() for row in rows)
    return evidence, dict(trace_counts=dict(sorted(trace_counts.items())), contact_types=dict(sorted(kinds.items())),
                          rank_pairs=dict(sorted(ranks.items())), uniform_squared_cut_block_lower_bound=str(minimum),
                          pairs_by_direction={d: len(rows) for d, rows in evidence.items()},
                          rejected_fusions=2*sum(map(len, evidence.values())),
                          width_domain="every positive integer",
                          normalized_squared_cut_defect_lower_bound="coefficient^2")


def check_contact_certificates(model, evidence):
    """Check coverage by role lists, then use the older input-column engine."""
    count = 0
    for direction, certificates in evidence.items():
        events = model.word["programs"][direction]
        expected = set()
        for register in range(p.PERSISTENT):
            climbs = [(j, event) for j, event in enumerate(events)
                      if event[0] == "climb" and event[2] == register]
            expected.update((a, b) for j, (a, _) in enumerate(climbs) for b, _ in climbs[j+1:])
        p.need(len(certificates) == len(expected) and {(r["first"], r["second"]) for r in certificates} == expected,
               "Independent complete same-role pair census")
        skeleton = []
        for event in events:
            instructions = []
            if event[0] == "warp":
                instructions.append(dict(op="apply", dst=p.role(event[1]), symbol=str(abs(event[2])), inverse=event[2] < 0))
            elif event[0] == "scalar":
                gate = event[1]
                target, op = p.role(gate[1]), gate[0]
                if op in ("clear", "copy"):
                    instructions.append(dict(op="scale", dst=target, coefficient="0"))
                if op in ("copy", "add"):
                    instructions.append(dict(op="add", src=p.role(gate[2]), dst=target,
                                             coefficient=str(Q(1) if op == "copy" else Q(gate[3], gate[4]))))
                elif op == "scale":
                    instructions.append(dict(op="scale", dst=target, coefficient=str(Q(gate[2], gate[3]))))
            skeleton.append(instructions)
        interface = dict(roles=p.PERSISTENT+1, operators={str(j): None for j in range(1, 73)})
        for row in certificates:
            program = [instruction for event in skeleton[row["first"]+1:row["second"]] for instruction in event]
            result = word_endpoint(interface, program, row["input"])[row["output"]]
            word = tuple((str(abs(signed)), signed < 0) for signed in row["word"])
            p.need(result == {word: c.G(row["coefficient"])}, "Separate complete contact coefficient replay")
            count += 1
    return count


def fused_program(problem, offsets, pair, early):
    first, second, *_ = pair
    program = problem["program"]
    merged = program[offsets[first]:offsets[first+1]] + program[offsets[second]:offsets[second+1]]
    return (program[:offsets[first]] + (merged if early else [])
            + program[offsets[first+1]:offsets[second]] + ([] if early else merged)
            + program[offsets[second+1]:])


def full_witness(problem, program, reference):
    """Find a width-one basis witness, then check a separate input-column replay."""
    actual, _ = p.complete_endpoint(problem, program)
    names = list(problem["operators"])
    bank = compact.validate(problem)
    for output, (left, right) in enumerate(zip(actual, reference)):
        difference = left.copy()
        p.add(difference, right, Q(-1))
        for entry in sorted({key[0] for key in difference}):
            terms = [(word, q) for (source, word), q in difference.items() if source == entry]
            circuits = [[gate for signed in reversed(word)
                         for gate in bank[names[abs(signed)-1], signed < 0]] for word, q in terms]
            coefficients, paths, inner = compact.merge_terms([c.G(q) for word, q in terms],
                                                             [Paths(p.N, circuit) for circuit in circuits])
            if not coefficients or c.energy(coefficients, inner, 1) == 0:
                continue
            witness = compact.entry_witness(coefficients, paths, inner, 1)
            literal = word_endpoint(problem, program, entry)[output]
            wanted = word_endpoint(problem, problem["reference"], entry)[output]
            from check_witness import add_term
            for word, q in wanted.items():
                add_term(literal, word, -q)
            # Independent source amplitude evaluator; no Gram or path sum.
            sys.path.insert(0, str(HERE / "vendor"))
            import clifford_exact as source
            value = c.G(0)
            for word, q in literal.items():
                circuit = [gate for letter in reversed(word) for gate in bank[letter]]
                vector, denominator = source.Op(p.N, source.identity(p.N), circuit).zero_state(witness["input_tuple"][0])
                real, imag = vector[witness["output_tuple"][0]]
                value += q*c.G.pair(Q(real, 1 << denominator), Q(imag, 1 << denominator))
            p.need(value != 0 and str(value) == witness["discrepancy"], "Independent complete-provider basis witness")
            return dict(output_role=output, input_role=entry, **witness,
                        normalized_squared_norm=str(c.energy(coefficients, inner, 1)),
                        mutated_program_sha256=hashlib.sha256(canonical(program)).hexdigest())
    raise ValueError("No width-one full-program witness")


def rejection(name, action):
    try:
        action()
    except (ValueError, KeyError) as error:
        return dict(name=name, rejected=str(error))
    raise ValueError("Accepted negative control: " + name)


def verify(write=False):
    source_integrity()
    manifest, data = p.read_inputs()
    model = p.Provider(data["word"])
    audits = {d: model.audit_word(d) for d in ("forward", "backward")}
    traces, native = check_catalogue(model, data, audits)
    print("PASS_ALL_PROVIDER_NATIVE_CLASSES", native, flush=True)
    results, witnesses = {}, []
    for direction in ("forward", "backward"):
        problem, offsets = model.problem(direction)
        actual, support = p.complete_endpoint(problem, problem["program"])
        reference, _ = p.complete_endpoint(problem, problem["reference"])
        p.need(actual == reference, "Complete sparse physical endpoint")
        certificate = compact.certify(problem)
        p.need(certificate["equivalent_at_all_positive_widths"], "Complete compact provider certificate")
        p.need(not actual[p.OWNED], "Arbitrary owned input is erased at return")
        results[direction] = dict(certificate=certificate, support=support, instructions=len(problem["program"]),
                                  native_symbols=len(problem["operators"]), events=audits[direction]["events"],
                                  paid=audits[direction]["paid"])
        pairs = p.fusion_pairs(model.word["programs"][direction])
        selected = [min(pairs, key=lambda row: (row[1]-row[0], row)),
                    min((row for row in pairs if row[4] != row[5]), key=lambda row: (row[1]-row[0], row))]
        events = model.word["programs"][direction]
        selected.append(min((row for row in pairs if max(events[row[0]][5], events[row[1]][5]) > 1
                             and any(event[0] == "climb" and event[2] == row[2]
                                     for event in events[row[0]+1:row[1]])),
                            key=lambda row: (row[1]-row[0], row)))
        for pair in selected:
            for early in (True, False):
                witness = full_witness(problem, fused_program(problem, offsets, pair, early), reference)
                witnesses.append(dict(direction=direction, placement="early" if early else "late",
                                      pair=list(pair), **witness))
        print("PASS_COMPLETE_PROVIDER", direction, support, flush=True)
    fusions, fusion_result = fusion_census(model, traces)
    fusion_result["separate_contact_replays"] = check_contact_certificates(model, fusions)
    controls = []
    bad = deepcopy(data)
    bad["paid"] = bad["paid"][:-1]
    controls.append(rejection("missing_paid_class", lambda: check_catalogue(model, bad, audits)))
    first = data["paid"][1]
    wrong = deepcopy(first["recipe"])
    wrong["left"]["phase"] = (wrong["left"]["phase"]+1) % 4
    controls.append(rejection("paid_absolute_phase", lambda: equal(model.edge(first["input"], first["output"], first["direction"]), p.recipe(wrong))))
    broken = deepcopy(data["word"])
    broken["programs"]["forward"].insert(0, ["scalar", ["clear", ["L", 224]], broken["canonical"]["start"][224]])
    controls.append(rejection("borrowed_erasure", lambda: p.Provider(broken).audit_word("forward")))
    broken_live = deepcopy(data["word"])
    prog = broken_live["programs"]["backward"]
    at = next(j for j, event in enumerate(prog) if event[0] == "center")
    prog.insert(at, next(event for event in prog if event[0] == "climb"))
    controls.append(rejection("live_owned_cut", lambda: p.Provider(broken_live).audit_word("backward")))
    # A block with no contact can permit fusion. The exclusion needs its contact witness.
    p.need(all(not row for j, row in enumerate(p.interval([], -1, 0, 0)) if j != 0), "Identity interval positive control")
    controls.append(rejection("missing_contact_is_not_a_certificate", lambda: p.contact_witness([], (-1, 0, 0, 0, 2, 2, 3))))
    evidence_sha = saved("FUSIONS.json.gz", fusions, write)
    witness_sha = saved("WITNESSES.json", witnesses, write)
    result = dict(status="PASS_COMPLETE_PR4610_PROVIDER_AND_30328_FUSION_OBSTRUCTIONS", source_main=manifest["base_commit"],
                  provider_head=manifest["provider_head"], admission_head=manifest["admission_head"],
                  complete_local_provider=results, native=native, fusion=fusion_result,
                  fusion_payload_sha256=evidence_sha, witness_payload_sha256=witness_sha,
                  full_program_basis_witnesses=len(witnesses), controls=controls,
                  new_kappa=False, achieved_paid_delta={},
                  limits="Fixed early/late fusion of any two persistent paid climbs on one role; no changed contacts, coupled fusions, new controller or physical/outer admission.")
    saved("RESULT.json", result, write)
    print(result["status"], flush=True)
    return result


if __name__ == "__main__":
    p.need(sys.argv[1:] in ([], ["--write"]), "Use --write or no argument")
    verify("--write" in sys.argv)
