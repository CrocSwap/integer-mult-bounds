"""Independent forward-column audit of the frozen formal Laurent caller.

Coefficients are integers in twenty commuting Laurent indeterminates. No
finite-order relation, conjugation, author replay or other verifier is used.
The atomic LOCAL interface is a premise, not physical admission.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
FIELDS, STAGES, VARIABLES = 34, 19, 20
ZERO = (0,) * VARIABLES
PINNED = {
    "sources/CONTROLLER.json": ("6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f", "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"),
    "sources/controller-source.py": ("8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c", "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"),
    "sources/upstream-PROOF.md": ("1fab54bc665bf6882f0bbd772af15fbf69a92eac040951ccd19a5accf02f328e", "08dd3e35b0bdd5a6e39f88183b2793c6bb5af6ca"),
    "sources/NOTICE": ("c0aec2bb7b305c49c8630a801f0ef2d5286cde81025471cc384990440577ad79", "af80ac5d2929d3a3e4ea90c9cf3141d63d358b0c"),
    "sources/module-check-source.py": ("a30e70fe1313f125b276ec97e05c779ff80b6d1aa9f6ba918a61bfb9bb5a2eda", "f394d40ea2e0777f77910cc5a4b1d151c1228cbc"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_bytes())
    require(type(pins) is list and len(pins) == len(PINNED), "Five frozen source pins")
    require({row["file"]: (row["sha256"], row["git_blob"]) for row in pins} == PINNED,
            "Independently fixed source pin inventory")
    for filename, (digest, blob) in PINNED.items():
        raw = (HERE / filename).read_bytes()
        require(sha256(raw).hexdigest() == digest, "Exact source SHA256: " + filename)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Exact source Git blob: " + filename)
    return json.loads((HERE / "sources/CONTROLLER.json").read_bytes())


def parse_events(events):
    """Structural legality only; unique-stage census is separate from this."""
    require(type(events) is list and 0 < len(events) <= 1000, "Bounded literal event list")
    parsed = []
    for event in events:
        require(type(event) is list and event, "Literal caller event")
        op = event[0]
        require(op in ("ADD", "SCALE", "SWAP", "LOCAL", "QUERY", "Q_POWER", "IDLE"),
                "Known caller opcode")
        require(len(event) == {"ADD": 4, "SCALE": 3, "SWAP": 3, "LOCAL": 4,
                               "QUERY": 4, "Q_POWER": 3, "IDLE": 4}[op], "Literal event arity")
        if op == "LOCAL":
            integer(event[1], 1, STAGES + 1, "LOCAL stage")
            src = integer(event[2], 0, FIELDS, "LOCAL source role")
            dst = integer(event[3], 0, FIELDS, "LOCAL destination role")
            require(src != dst, "Distinct LOCAL roles")
        else:
            integer(event[1], 0, FIELDS, "Caller destination role")
            if op in ("ADD", "SWAP", "QUERY", "IDLE"):
                integer(event[2], 0, FIELDS, "Caller second role")
                require(event[1] != event[2], "Distinct caller roles")
            if op in ("ADD", "SCALE"):
                coefficient = event[-1]
                require(type(coefficient) is int and coefficient != 0,
                        "Nonzero integer scalar coefficient")
            elif op == "QUERY":
                require(type(event[3]) is int and event[3] in (-1, 1), "Unit QUERY exponent")
            elif op == "Q_POWER":
                require(type(event[2]) is int and event[2] in (-2, 2), "Ordinary Q_POWER exponent")
            elif op == "IDLE":
                require(type(event[3]) is list and event[3], "Nonempty IDLE stage list")
                for stage in event[3]:
                    integer(stage, 1, STAGES + 1, "IDLE stage")
                require(len(event[3]) == len(set(event[3])), "Distinct stages within an IDLE")
        parsed.append(deepcopy(event))
    return parsed


def parse_word(word):
    require(type(word) is dict and word["schema"] == "binary-query-tree/1", "Frozen caller schema")
    require(type(word["roles"]) is int and word["roles"] == FIELDS
            and type(word["stages"]) is int and word["stages"] == STAGES,
            "Thirty-four fields and nineteen distinct stage variables")
    events = parse_events(word["events"])
    require(len(events) == 353, "Exact source event inventory")
    counts = Counter(event[0] for event in events)
    stages = [event[1] for event in events if event[0] == "LOCAL"]
    require(sorted(stages) == list(range(1, STAGES + 1)), "Every LOCAL stage occurs exactly once")
    require(counts["QUERY"] == 16 and counts["IDLE"] == 16, "Sixteen thin queries and paired idles")
    diagonal = word["diagonal"]
    require(type(diagonal) is list and len(diagonal) == FIELDS, "Every field has an advertised target")
    reduced = []
    for term in diagonal:
        require(type(term) is list and len(term) == VARIABLES + 1,
                "Source diagonal has Q plus stage0..19 slots")
        require(all(type(exponent) is int for exponent in term), "Integer source exponents")
        require(term[0] in (-1, 1) and term[1] == 0
                and all(exponent in (0, 1) for exponent in term[2:]),
                "Explicit central sign, zero dummy stage and distinct stage incidences")
        reduced.append(tuple(term[:1] + term[2:]))
    return events, reduced, counts


def shifted(polynomial, change):
    return {tuple(a + b for a, b in zip(exponents, change)): coefficient
            for exponents, coefficient in polynomial.items()}


def add_into(destination, source, coefficient=1):
    for exponents, value in tuple(source.items()):
        result = destination.get(exponents, 0) + coefficient * value
        if result:
            destination[exponents] = result
        else:
            destination.pop(exponents, None)


def central(exponent):
    return (exponent,) + (0,) * STAGES


def stage_shift(stages):
    indices = set(stages)
    return (0,) + tuple(int(stage in indices) for stage in range(1, STAGES + 1))


def column(events, input_role):
    """Propagate one independent original input through actual chronology."""
    fields = [{ZERO: 1} if r == input_role else {} for r in range(FIELDS)]
    peak_terms, peak_cell_terms = 1, 1
    for event in events:
        op = event[0]
        if op == "ADD":
            add_into(fields[event[1]], fields[event[2]], event[3])
        elif op == "SCALE":
            r, coefficient = event[1:]
            fields[r] = {key: coefficient * value for key, value in fields[r].items()}
        elif op == "SWAP":
            a, b = event[1:]
            fields[a], fields[b] = fields[b], fields[a]
        elif op == "QUERY":
            dst, src, exponent = event[1:]
            add_into(fields[dst], shifted(fields[src], central(exponent)))
        elif op == "LOCAL":
            stage, src, dst = event[1:]
            source, destination = fields[src], fields[dst]
            delta = stage_shift([stage])
            fields[src] = shifted(source, delta)
            fields[dst] = shifted(destination, delta)
            query_delta = tuple(a + b for a, b in zip(delta, central(-1)))
            add_into(fields[dst], shifted(source, query_delta))
        elif op == "Q_POWER":
            fields[event[1]] = shifted(fields[event[1]], central(event[2]))
        else:
            require(op == "IDLE", "Known propagated event")
            a, b, stages = event[1:]
            delta = stage_shift(stages)
            fields[a], fields[b] = shifted(fields[a], delta), shifted(fields[b], delta)
        peak_terms = max(peak_terms, sum(map(len, fields)))
        peak_cell_terms = max(peak_cell_terms, max(map(len, fields)))
        require(peak_terms <= 100000, "Bounded formal-polynomial resource budget")
    return fields, peak_terms, peak_cell_terms


def matrix(events):
    result = [[{} for _ in range(FIELDS)] for _ in range(FIELDS)]
    peak_terms, peak_cell_terms = 0, 0
    for input_role in range(FIELDS):
        outputs, terms, cell_terms = column(events, input_role)
        peak_terms, peak_cell_terms = max(peak_terms, terms), max(peak_cell_terms, cell_terms)
        for output_role, polynomial in enumerate(outputs):
            result[output_role][input_role] = polynomial
    return result, {"peak_terms_in_one_propagated_column": peak_terms,
                    "peak_terms_in_one_polynomial": peak_cell_terms}


def advertised(diagonal):
    return [[{diagonal[r]: 1} if r == c else {} for c in range(FIELDS)]
            for r in range(FIELDS)]


def first_difference(actual, expected):
    for output in range(FIELDS):
        for input_role in range(FIELDS):
            a, b = actual[output][input_role], expected[output][input_role]
            for exponents in sorted(a.keys() | b.keys()):
                if a.get(exponents, 0) != b.get(exponents, 0):
                    return {"output": output, "input": input_role, "exponents": list(exponents),
                            "expected_coefficient": b.get(exponents, 0),
                            "actual_coefficient": a.get(exponents, 0)}
    return None


def encoded_matrix(value):
    return [[[[coefficient, list(exponents)] for exponents, coefficient in sorted(cell.items())]
             for cell in row] for row in value]


def mutation_controls(events, expected):
    mutations = []
    for name, opcode in (("missing_paired_idle", "IDLE"), ("missing_central_translation", "Q_POWER"),
                         ("missing_thin_query", "QUERY")):
        altered = deepcopy(events)
        index = next(i for i, event in enumerate(altered) if event[0] == opcode)
        removed = altered.pop(index)
        mutations.append((name, index, removed, None, altered))
    for name, opcode, slot in (("wrong_query_exponent", "QUERY", 3),
                              ("wrong_add_sign", "ADD", 3),
                              ("wrong_central_power_sign", "Q_POWER", 2)):
        altered = deepcopy(events)
        index = next(i for i, event in enumerate(altered) if event[0] == opcode)
        original = deepcopy(altered[index])
        altered[index][slot] *= -1
        mutations.append((name, index, original, altered[index], altered))
    altered = deepcopy(events)
    index = next(i for i, event in enumerate(altered) if event[0] == "IDLE")
    original = deepcopy(altered[index])
    replacement = next(stage for stage in range(1, STAGES + 1) if stage not in altered[index][3])
    altered[index][3][0] = replacement
    mutations.append(("wrong_idle_stage", index, original, altered[index], altered))
    altered = deepcopy(events)
    index = next(i for i, event in enumerate(altered) if event[0] == "LOCAL")
    original = deepcopy(altered[index])
    altered[index][1] = altered[index][1] % STAGES + 1
    mutations.append(("aliased_local_stage", index, original, altered[index], altered))
    results = []
    for name, index, original, replacement, altered in mutations:
        # Parse legality, then run the full symbolic calculation. Stage census is
        # deliberately not the reason that the altered sequence is rejected.
        parsed = parse_events(altered)
        actual, _ = matrix(parsed)
        witness = first_difference(actual, expected)
        require(witness is not None, "Mutation must yield an actual Laurent coefficient difference: " + name)
        results.append({"mutation": name, "event_index": index, "original_event": original,
                        "replacement_event": replacement, "structurally_legal": True,
                        "coefficient_witness": witness})
    return results


def run():
    word = authenticate()
    events, diagonal, counts = parse_word(word)
    expected = advertised(diagonal)
    actual, intermediate = matrix(events)
    difference = first_difference(actual, expected)
    require(difference is None, "Complete formal caller endpoint mismatch: " + canonical(difference))
    digest = sha256((canonical(encoded_matrix(actual)) + "\n").encode()).hexdigest()
    return {"schema_version": 1, "status": "PASS",
            "method": "independent chronological forward columns over exact integer Laurent polynomials",
            "ring": {"coefficients": "Z", "variables": ["Q"] + ["D" + str(i) for i in range(1, STAGES + 1)],
                     "commuting": True, "invertible": True, "finite_order_relations": False},
            "fields": FIELDS, "input_columns": FIELDS, "output_coordinates": FIELDS,
            "polynomial_cells_compared": FIELDS * FIELDS, "events": len(events),
            "opcode_counts": dict(sorted(counts.items())),
            "source_dummy_stage_zero_removed": True,
            "nonzero_endpoint_monomials": sum(len(cell) for row in actual for cell in row),
            "matrix_sha256": digest, "advertised_diagonal": [list(term) for term in diagonal],
            "intermediate_resources": intermediate, "semantic_mutations": mutation_controls(events, expected),
            "limits": ["LOCAL is assumed to realize D_s [[1,0],[Q^-1,1]] with commuting invertible stage operators.",
                       "No finite-order Q or stage relation is used; signs stay in integer coefficients.",
                       "Mutation witnesses refute formal identities, not physical impossibility under extra operator relations.",
                       "Physical contacts, native phases, helper/owned allocation, erasure, funding and kappa admission are outside this audit."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: oracle.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "ORACLE.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained ORACLE.json receipt")
        print("PASS independent forward Laurent endpoint and retained receipt")
