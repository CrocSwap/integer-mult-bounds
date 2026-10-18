#!/usr/bin/env python3
"""Independent, exact replay of the pinned PR1185 six-source query witness.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported or executed.

Algebra: a row is a finite subset of words (operator,...,operator,@input).
The subset is its coefficient vector over F2; symmetric difference is addition.
Left-prefixing a generator implements that generator's linear action. Distinct
operator words are NEVER identified or commuted. Induction on the literal
program therefore identifies its state in the free associative F2 module.
Equality here survives every substitution by same-space F2-linear operators,
including singular, noncommuting maps, at any dimension. This is an executable
finite symbolic certificate, not a proof-assistant theorem.

For F = L R (R applied first), lowering emits R, L, inverse(R), inverse(L),
using a borrowed dirty row w. Its target increment is
L(w + R(x)) + L(w) = L R(x); w and all descendant scratch are restored.
The inverse of a primitive additive update is itself, so a program's inverse
is its reversal. A completed additive child is itself an involution too; we
check that valid substitution explicitly instead of calling it a fault.

The invoice is I + sum(P_f) + D + sum(m_f*c_f(L)). I, coefficient preparation
P_f and dispatch D remain caller charges. Each c_f is a COMPLETE primitive
call price including coefficient/source access, target update, private scratch,
frames and head return. We certify m_f, not a physical implementation or kappa.
The independent recurrence is ell(1)=1; ell(n)=2ell(floor(n/2))+2ell(ceil(n/2)).
Peak borrowed rows are one root connector plus ceil(log2(max factor length)).
"""

import argparse
from collections import Counter
from hashlib import sha256, sha1
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = "1b59b624d21924f8e3537cdc1ac52d3be6eda2fe"
PREDECESSOR = "4a60772285ce70f6414458f6d3a54948652bbed0"
ROOT_HASH = "e589507497ee1a17861933a6a1334dd20a01038fe2989a58415a30a0f8934ccb"
DATA_ROWS = tuple([f"x{j}" for j in range(6)] + [f"y{m}" for m in range(1, 64)] + ["z"])
SCRATCH = ("s0", "s1", "s2")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def read(path):
    return json.loads(path.read_text())


def verify_sources(package):
    manifest = read(package / "SOURCES.json")
    require(manifest["base_commit"] == BASE, "base pin")
    references = manifest["references"]
    expected_names = {"PR1185-verify.py", "PR1185-EXPECTED.json", "PR1185-NOTICE.md",
                      "PR943-README.md", "PR943-NOTICE.md"}
    require(len(references) == 5 and {Path(r["local_path"]).name for r in references} == expected_names,
            "reference inventory")
    for ref in references:
        path = package / ref["local_path"]
        require(path.parent == package / "references", "reference path")
        data = path.read_bytes()
        require(sha256(data).hexdigest() == ref["sha256"], "source SHA256: " + path.name)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(sha1(blob).hexdigest() == ref["git_blob_sha1"], "source Git blob: " + path.name)
        wanted_commit = PREDECESSOR if path.name.startswith("PR1185") else BASE
        require(ref["commit"] == wanted_commit, "reference commit")
    return manifest


def load_fixture(package):
    fixture = read(package / "FIXTURE.json")
    source = read(package / "references/PR1185-EXPECTED.json")
    require(fixture["schema"] == "connector-free-algebra-fixture-v1", "fixture schema")
    require(type(fixture["assignment_seed"]) is int and fixture["assignment_seed"] == 79, "seed")
    ops = fixture["root_ops"]
    require(len(ops) == 142, "root query count")
    for op in ops:
        require(isinstance(op, list) and len(op) == 2, "root operation shape")
        kind, index = op
        require(kind in ("A", "B") and type(index) is int, "root operation type")
        require(0 <= index < (63 if kind == "A" else 6), "root operation range")
    # Match the producer's documented serialization, not this tool's digest format.
    require(sha256(json.dumps(ops).encode()).hexdigest() == ROOT_HASH, "literal root word pin")
    require(fixture["root_ops_sha256"] == source["batch"]["witness_ops_sha256"] == ROOT_HASH,
            "predecessor witness binding")
    require(fixture["source_word"] == source["constructions"]["6"]["word"] ==
            [op[1] for op in ops if op[0] == "B"], "source word binding")
    require(fixture["source_factor_lengths"] == [1 + (79 + j) % 8 for j in range(6)], "source lengths")
    require(fixture["output_factor_lengths"] == [1 + (79 * m) % 8 for m in range(1, 64)], "output lengths")
    return fixture


def initial(rows):
    require(len(rows) == len(set(rows)), "aliased initial rows")
    return {row: {(f"@{row}",)} for row in rows}


def step(state, gate):
    symbol, source, target = gate
    require(isinstance(symbol, str) and symbol and not symbol.startswith("@"), "operator symbol")
    require(source in state and target in state and source != target, "invalid or aliased gate ports")
    state[target].symmetric_difference_update((symbol,) + term for term in state[source])


def run(program, rows):
    state = initial(rows)
    for gate in program:
        step(state, gate)
    return state


def state_record(state):
    return {row: [list(term) for term in sorted(terms)] for row, terms in sorted(state.items())}


def residual(actual, wanted):
    require(set(actual) == set(wanted), "row inventory mismatch")
    return {row: sorted(actual[row] ^ wanted[row]) for row in actual if actual[row] != wanted[row]}


def root_gate(op):
    kind, index = op
    if kind == "B":
        return f"B{index}", f"x{index}", "z"
    require(kind == "A", "unknown query")
    return f"A{index + 1}", "z", f"y{index + 1}"


def factor_bank(fixture):
    lengths = {f"B{j}": d for j, d in enumerate(fixture["source_factor_lengths"])}
    lengths.update({f"A{m}": d for m, d in enumerate(fixture["output_factor_lengths"], 1)})
    return {operator: tuple(f"{operator}.f{k}" for k in range(d)) for operator, d in lengths.items()}


def expected_state(rows, factors=None):
    state = initial(rows)
    for mask in range(1, 64):
        for j in range(6):
            if mask & (1 << j):
                a, b = f"A{mask}", f"B{j}"
                word = (a, b) if factors is None else tuple(reversed(factors[a])) + tuple(reversed(factors[b]))
                state[f"y{mask}"].add(word + (f"@x{j}",))
    return state


def lower_product(factors, source, target, scratch):
    require(factors, "empty factor product")
    require(source != target and len(set(scratch)) == len(scratch), "aliased lowering ports")
    require(source not in scratch and target not in scratch, "scratch aliases a live port")
    if len(factors) == 1:
        return [(factors[0], source, target)]
    require(scratch, "insufficient scratch")
    middle = len(factors) // 2
    right = lower_product(factors[:middle], source, scratch[0], scratch[1:])
    left = lower_product(factors[middle:], scratch[0], target, scratch[1:])
    return right + left + right[::-1] + left[::-1]


def leaf_weights(factors, multiplier=1):
    """Price by tree depth, separately from the emitted instruction list."""
    if len(factors) == 1:
        return Counter({factors[0]: multiplier})
    half = len(factors) // 2
    return leaf_weights(factors[:half], 2 * multiplier) + leaf_weights(factors[half:], 2 * multiplier)


def leaf_count(n):
    require(type(n) is int and n >= 1, "positive factor count")
    if n == 1:
        return 1
    return 2 * (leaf_count(n // 2) + leaf_count(n - n // 2))


def check_invoice(program, paid):
    require(all(type(n) is int and n > 0 for n in paid.values()), "invalid primitive multiplicity")
    require(Counter(g[0] for g in program) == paid, "complete primitive invoice mismatch")


def lower_batch(ops, factors, scratch=SCRATCH):
    require(not set(scratch) & set(DATA_ROWS), "scratch aliases a protected data row")
    chunks = []
    for op in ops:
        operator, source, target = root_gate(op)
        chunks.append(lower_product(factors[operator], source, target, scratch))
    return chunks


def check_local_products(factors):
    records = []
    for operator, word in sorted(factors.items()):
        rows = ("source", "target") + SCRATCH
        program = lower_product(word, "source", "target", SCRATCH)
        wanted = initial(rows)
        wanted["target"].add(tuple(reversed(word)) + ("@source",))
        for direction in (program, program[::-1]):
            require(run(direction, rows) == wanted, "local product identity: " + operator)
        require(Counter(g[0] for g in program) == leaf_weights(word), "local leaf invoice")
        require(len(program) == leaf_count(len(word)), "local recurrence")
        records.append([operator, len(word), len(program), digest(state_record(wanted))])
    return records


def substitute_root(state, factors):
    result = {}
    for row, terms in state.items():
        substituted = set()
        for term in terms:
            expanded = tuple(letter for symbol in term[:-1] for letter in reversed(factors[symbol])) + term[-1:]
            # Explicit parity, also correct if a future bank identifies factors.
            substituted.symmetric_difference_update([expanded])
        result[row] = substituted
    return result


def check_boundaries(ops, chunks, factors):
    trace = sha256()
    rows = DATA_ROWS + SCRATCH
    for orientation in ("forward", "reverse"):
        root_state, low_state = initial(rows), initial(rows)
        blocks = list(zip(ops, chunks))
        if orientation == "reverse":
            blocks = [(op, chunk[::-1]) for op, chunk in blocks[::-1]]
        for index, (op, chunk) in enumerate(blocks):
            step(root_state, root_gate(op))
            for gate in chunk:
                step(low_state, gate)
            require(low_state == substitute_root(root_state, factors),
                    f"dirty-state query boundary {orientation}:{index}")
            trace.update(canonical([orientation, index, state_record(low_state)]) + b"\n")
    return {"boundaries": 2 * len(ops), "state_trace_sha256": trace.hexdigest()}


def concrete_counterexample(program, wanted, rows, row, term):
    """Separate a nonzero word with a finite, nilpotent path representation.

    For term g_k ... g_1 @input, set input=e_0 and every other row to zero.
    The matrix for g has edge e_(i-1) -> e_i precisely where g_i=g. Only
    that operator word has a nonzero e_k coefficient. Thus the matrices
    isolate its coefficient even when the residual has many other words.
    They are an explicit finite counterexample to the MUTATED program.
    """
    application_order = term[:-1][::-1]
    edges = {}
    for index, symbol in enumerate(application_order):
        edges.setdefault(symbol, []).append((index, index + 1))

    def apply(symbol, vector):
        value = 0
        for source, target in edges.get(symbol, []):
            if vector & (1 << source):
                value ^= 1 << target
        return value

    input_row = term[-1][1:]
    state = {name: int(name == input_row) for name in rows}
    for symbol, source, target in program:
        state[target] ^= apply(symbol, state[source])
    expected_value = 0
    for monomial in wanted[row]:
        if monomial[-1] != term[-1]:
            continue
        value = 1
        for symbol in monomial[:-1][::-1]:
            value = apply(symbol, value)
        expected_value ^= value
    coordinate = len(application_order)
    require((state[row] ^ expected_value) & (1 << coordinate), "finite matrix counterexample failed")
    return {"dimension": coordinate + 1, "input_row": input_row, "input_vector": 1,
            "other_inputs": 0, "output_row": row, "differing_coordinate": coordinate,
            "actual_vector": state[row], "expected_vector": expected_value,
            "matrix_edges_source_target": {k: [list(edge) for edge in val] for k, val in sorted(edges.items())},
            "unlisted_matrices": "zero"}


def rejection_witness(program, wanted, rows):
    wrong = residual(run(program, rows), wanted)
    require(wrong, "semantic negative control unexpectedly passed")
    row = sorted(wrong)[0]
    return {"wrong_rows": sorted(wrong), "first_row": row,
            "first_residual_word": list(wrong[row][0]), "residual_sha256": digest(wrong),
            "concrete_counterexample": concrete_counterexample(program, wanted, rows, row, wrong[row][0])}


def negative_controls(ops, factors, chunks):
    controls = {}
    root = [root_gate(op) for op in ops]
    root_wanted = expected_state(DATA_ROWS)
    last_b = max(i for i, op in enumerate(ops) if op[0] == "B")
    bad = root[:last_b] + root[last_b + 1:]
    controls["omit_final_source_restoration"] = rejection_witness(bad, root_wanted, DATA_ROWS)
    require(controls["omit_final_source_restoration"]["wrong_rows"] == ["z"], "output-invisible control")
    first_a = next(i for i, op in enumerate(ops) if op[0] == "A")
    controls["omit_one_readout"] = rejection_witness(root[:first_a] + root[first_a + 1:], root_wanted, DATA_ROWS)
    changed = root[:]
    symbol, src, _ = changed[first_a]
    changed[first_a] = (symbol, src, "y63")
    controls["wrong_readout_destination"] = rejection_witness(changed, root_wanted, DATA_ROWS)

    rows = DATA_ROWS + SCRATCH
    program = [gate for chunk in chunks for gate in chunk]
    wanted = expected_state(rows, factors)
    # The last leaf of a length-eight B0 product restores private scratch only.
    index = next(i for i, op in enumerate(ops) if op == ["B", 0])
    offset = sum(map(len, chunks[:index + 1])) - 1
    bad = program[:offset] + program[offset + 1:]
    controls["omit_recursive_cleanup_leaf"] = rejection_witness(bad, wanted, rows)

    reversed_factors = dict(factors)
    reversed_factors["B0"] = factors["B0"][::-1]
    bad = [g for chunk in lower_batch(ops, reversed_factors) for g in chunk]
    controls["reverse_noncommuting_B0_factors"] = rejection_witness(bad, wanted, rows)

    # Replaying a COMPLETE child forward is valid in F2, even for a literal
    # non-palindromic word. Omitting a complete cleanup child is invalid.
    word = factors["A3"]
    half = len(word) // 2
    right = lower_product(word[:half], "source", "s0", SCRATCH[1:])
    left = lower_product(word[half:], "s0", "target", SCRATCH[1:])
    local_rows = ("source", "target") + SCRATCH
    local_wanted = initial(local_rows)
    local_wanted["target"].add(tuple(reversed(word)) + ("@source",))
    require(run(right + left + right + left[::-1], local_rows) == local_wanted,
            "completed additive child involution positive control")
    controls["omit_complete_cleanup_child"] = rejection_witness(right + left + right[::-1], local_wanted, local_rows)

    for name, scratch in [("aliased_data_scratch", ("x0", "s1", "s2")),
                          ("duplicated_scratch", ("s0", "s0", "s2")),
                          ("insufficient_scratch", ("s0", "s1"))]:
        try:
            lower_batch(ops, factors, scratch)
        except ValueError as error:
            controls[name] = {"rejected": str(error)}
        else:
            raise ValueError("admission control unexpectedly passed: " + name)
    counted = Counter(g[0] for g in program)
    undercounted = counted.copy()
    undercounted[program[0][0]] -= 1
    try:
        check_invoice(program, undercounted)
    except ValueError as error:
        controls["unpaid_primitive"] = {"symbol": program[0][0], "unpaid_calls": 1, "rejected": str(error)}
    else:
        raise ValueError("invoice negative control unexpectedly passed")
    return controls


def compute(package=HERE):
    manifest = verify_sources(package)
    fixture = load_fixture(package)
    ops = fixture["root_ops"]
    root = [root_gate(op) for op in ops]
    wanted_root = expected_state(DATA_ROWS)
    for program in (root, root[::-1]):
        require(run(program, DATA_ROWS) == wanted_root, "root free-algebra identity")
    require(run(root + root, DATA_ROWS) == initial(DATA_ROWS), "root involution")

    factors = factor_bank(fixture)
    locals_receipt = check_local_products(factors)
    chunks = lower_batch(ops, factors)
    program = [gate for chunk in chunks for gate in chunk]
    rows = DATA_ROWS + SCRATCH
    wanted = expected_state(rows, factors)
    for direction in (program, program[::-1]):
        require(run(direction, rows) == wanted, "expanded free-algebra identity")
    require(run(program + program, rows) == initial(rows), "expanded involution")
    boundary_receipt = check_boundaries(ops, chunks, factors)

    paid = Counter()
    for operator, _, _ in root:
        paid.update(leaf_weights(factors[operator]))
    check_invoice(program, paid)
    require(sum(paid.values()) == sum(leaf_count(len(factors[op])) for op, _, _ in root), "aggregate recurrence")
    controls = negative_controls(ops, factors, chunks)
    return {
        "schema": "connector-free-algebra-result-v1", "status": "PASS_CONNECTOR_FREE_ALGEBRA",
        "base_commit": BASE, "predecessor_head": PREDECESSOR, "assignment_seed": 79,
        "root": {"queries": len(root), "symbolic_input_rows": len(DATA_ROWS), "output_masks": list(range(1, 64)),
                 "ordered_AB_terms": sum(len(wanted_root[f"y{mask}"]) - 1 for mask in range(1, 64)),
                 "forward_reverse_and_involution": True,
                 "root_ops_sha256": ROOT_HASH, "final_state_sha256": digest(state_record(wanted_root))},
        "expanded": {"primitive_calls": len(program), "primitive_operators": len(paid),
                     "symbolic_input_rows": len(rows), "borrowed_dirty_rows_including_z": 1 + len(SCRATCH),
                     "product_lengths_checked": sorted({len(v) for v in factors.values()}),
                     "local_products": len(locals_receipt), "local_products_sha256": digest(locals_receipt),
                     "forward_reverse_and_involution": True,
                     "literal_program_sha256": digest(program), "final_state_sha256": digest(state_record(wanted)),
                     **boundary_receipt},
        "invoice": {"primitive_multiplicities": dict(sorted(paid.items())),
                    "leaf_recurrence_values_1_through_8": [leaf_count(n) for n in range(1, 9)],
                    "caller_charges": ["input admission I", "coefficient preparation sum(P_f)", "instruction generation/access/dispatch D"],
                    "primitive_price_contract": "complete c_f(L), including source/coefficient access, target update, private restoration, frames, head return"},
        "negative_controls": controls,
        "positive_controls": ["complete additive child forward equals inverse in F2"],
        "scope": {"algebra": "free associative F2 module; arbitrary same-space linear operator substitution",
                  "not_checked": ["census or optimality", "physical supplier/hosting", "compiler/tape/precision/recovery", "analytic transfer", "Lean"],
                  "kappa_claim": None},
        "input_sha256": {name: sha256((package / name).read_bytes()).hexdigest() for name in ("SOURCES.json", "FIXTURE.json")},
        "reference_count": len(manifest["references"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="Write a newly computed receipt to this path instead of comparing EXPECTED.json")
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        # Exclusive creation: no silent overwrite of a reviewed receipt.
        with args.write_result.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(read(HERE / "EXPECTED.json") == result, "EXPECTED.json differs from exact replay")
    print("PASS_CONNECTOR_FREE_ALGEBRA queries=142 leaves=" + str(result["expanded"]["primitive_calls"]) +
          " rows=" + str(result["expanded"]["symbolic_input_rows"]) +
          " boundaries=284 controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    main()
