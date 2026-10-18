"""Finite actual tensor-collector audit; standard library and exact integers.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
The signed-floor pair and paired return are credited to Tekalign;
the actual tensor/field-major boundary is Jose Manuel's PR3131. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import oracle


def need(condition, message):
    if not condition:
        raise ValueError(message)


def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def read_json(raw):
    return json.loads(raw, object_pairs_hook=no_duplicates)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def compare_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True, allow_nan=False) ==
         json.dumps(expected, sort_keys=True, allow_nan=False), "complete typed receipt")


def source_inputs():
    raw = {}
    for row in read_json((HERE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row["sha256"], "source hash: " + row["path"])
            raw[row["path"]] = data
    word = read_json(raw["research/p104-rounded-collector/inputs/WORD.json"])
    native = read_json(gzip.decompress(raw["research/p104-rounded-collector/inputs/NATIVE.json.gz"]))
    return raw, word, native


def bind(word, native):
    frame = [256, 136, 64, 40, 16, 4, 2, 1]
    names = ["D31", "D30", "D29", "D28", "D27"]
    expected = [["zero", "C", frame]]
    expected += [["add", "C", name, 1, frame] for name in names]
    expected += [["transport", "C", frame, [364], 7], ["add", "Q7", "C", "1", [364]],
                 ["transport", "C", [364], frame, 7]]
    expected += [["add", "C", name, "-1", frame] for name in reversed(names)]
    expected += [["erase", "C", frame]]
    need(word["program"][2025:2040] == expected, "literal fifteen-event boundary")
    frames = dict(word["initial_frames"])
    for event in word["program"][:2025]:
        if event[0] == "transport":
            need(frames[event[1]] == event[2], "prefix transport entrance")
            frames[event[1]] = event[3]
        elif event[0] == "add":
            need(frames[event[1]] == frames[event[2]] == event[4], "prefix ADD frame")
        else:
            need(event[0] == "sign" and frames[event[1]] == event[3], "prefix sign frame")
    need(all(frames[name] == frame for name in names) and frames["Q7"] == [364], "entrance frames")
    recipes = []
    for index in (2031, 2033):
        matches = [x for x in native["transports"] if index in x["events"]]
        need(len(matches) == 1, "unique native event")
        row = matches[0]
        need(word["program"][index] == ["transport", "C", row["old"], row["new"], 7], "native binding")
        need(row["recipe"]["rank"] == 7, "native rank")
        recipes.append(row["recipe"])
    return recipes


def rot(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def pair(a, b, inverse=False):
    dr, di = a[0] - b[0], a[1] - b[1]
    sr, si = b[0] + dr // 2, b[1] + di // 2
    dr, di = (di, -dr) if inverse else (-di, dr)
    br, bi = sr - dr // 2, si - di // 2
    return (br + dr, bi + di), (br, bi)


def lift(values, rank, inverse=False, order=None):
    out = list(values)
    axes = list(range(rank)) if order is None else list(order)
    for axis in reversed(axes) if inverse else axes:
        bit = 1 << axis
        for index in range(len(out)):
            if index & bit == 0:
                other = index | bit
                out[index], out[other] = pair(out[index], out[other], inverse)
    return out


def plan(record, multiplicity):
    """Expand the affine/quadratic polynomial directly on 9*lambda bits."""
    n = 9 * multiplicity
    rows, linear, quadratic = [], [], []
    offset, constant = 0, multiplicity * record["phase"]
    for field in range(9):
        for column in range(multiplicity):
            axis = field * multiplicity + column
            rows.append(sum(((record["matrix_rows"][field] >> j) & 1) << (j * multiplicity + column)
                            for j in range(9)))
            offset |= ((record["offset"] >> field) & 1) << axis
            linear.append(record["linear_Z4"][field])
            quadratic.append(sum(((record["quadratic_rows"][field] >> j) & 1) << (j * multiplicity + column)
                                 for j in range(field + 1, 9)))
    table = []
    for x in range(1 << n):
        y = offset ^ sum(((mask & x).bit_count() % 2) << j for j, mask in enumerate(rows))
        phase = constant + sum(linear[j] + 2 * (quadratic[j] & x).bit_count()
                               for j in range(n) if x >> j & 1)
        table.append((y, phase % 4))
    need(len({y for y, _ in table}) == 1 << n, "actual tensor bijection")
    return table


def apply_plan(values, table, inverse=False):
    out = [None] * len(values)
    if inverse:
        for x, (y, phase) in enumerate(table):
            out[x] = rot(values[y], -phase)
    else:
        for x, (y, phase) in enumerate(table):
            out[y] = rot(values[x], phase)
    return out


def native(values, plans, rank, inverse=False, order=None):
    left, right = plans
    if inverse:
        out = apply_plan(values, left, True)
        out = lift(out, rank, True, order)
        return apply_plan(out, right, True)
    out = apply_plan(values, right)
    out = lift(out, rank, False, order)
    return apply_plan(out, left)


def fixture(multiplicity, mode):
    n = 1 << (9 * multiplicity)
    if mode == "rounding":
        sources = [[(((j * (37 + 2 * k) + 19 * k) % 1048583) - 524291,
                     ((j * (53 + 4 * k) + 31 * k) % 1048601) - 524300)
                    for j in range(n)] for k in range(5)]
        beta = 0
    elif mode == "promoted":
        sources = [[(((j * (37 + 2 * k) + 19 * k) % 2053) - 1026,
                     ((j * (53 + 4 * k) + 31 * k) % 2063) - 1031)
                    for j in range(n)] for k in range(5)]
        beta = 0
    else:
        big = [((j % 29 - 14) * 2**70 + j % 3, (j % 31 - 15) * 2**70 - j % 5) for j in range(n)]
        tail = [(j % 7 - 3, j % 11 - 5) for j in range(n)]
        residual = [(int(j == 0), -int(j == 7)) for j in range(n)] if mode == "cancellation" else [(0, 0)] * n
        sources = [big, [(-a, -b) for a, b in big], residual, tail, [(-a, -b) for a, b in tail]]
        beta = 8
    query = [(j % 13 - 6, j % 17 - 8) for j in range(n)]
    return sources, query, 3, beta


def execute(sources, query, f, beta, plans, multiplicity):
    count, rank, n = len(query), 7 * multiplicity, 9 * multiplicity
    private = [(0, 0)] * count
    for source in sources:
        private = [(a + c, b + d) for (a, b), (c, d) in zip(private, source, strict=True)]
    entrance = private
    maximum = max(abs(value) for z in private for value in z)
    gamma = (rank - 1).bit_length() + n // 2
    grid = f if maximum == 0 else max(f, beta + 1 + gamma - (maximum.bit_length() - 1 - f))
    shift = grid - f
    fine = [(a << shift, b << shift) for a, b in private]
    sent = native(fine, plans, rank)
    updated = [((a << shift) + c, (b << shift) + d) for (a, b), (c, d) in zip(query, sent, strict=True)]
    returned = native(sent, plans, rank, True)
    need(returned == fine, "exact paired return on the actual tensor")
    divisor = 1 << shift
    need(all(a % divisor == b % divisor == 0 for a, b in returned), "exact private downshift")
    private = [(a // divisor, b // divisor) for a, b in returned]
    for source in reversed(sources):
        private = [(a - c, b - d) for (a, b), (c, d) in zip(private, source, strict=True)]
    need(all(z == (0, 0) for z in private), "private erasure only at zero")
    return dict(grid=grid, entrance=entrance, fine=fine, sent=sent, query=updated, private=private)


def check_case(recipe, plans, multiplicity, mode, return_recipe=None):
    sources, query, f, beta = fixture(multiplicity, mode)
    source_hashes, query_hash = [digest(x) for x in sources], digest(query)
    result = execute(sources, query, f, beta, plans, multiplicity)
    F, total, fine, sent, updated = oracle.collector_query(sources, query, f, beta, recipe, multiplicity)
    need(result["grid"] == F and result["entrance"] == total and result["fine"] == fine,
         "independent gather/grid")
    need(result["sent"] == sent and result["query"] == updated, "independent actual query")
    need([digest(x) for x in sources] == source_hashes and digest(query) == query_hash, "read-only entrances")
    rank, count = 7 * multiplicity, len(query)
    ideal = oracle.ideal_numerator(fine, recipe, multiplicity)
    if return_recipe is not None:
        ideal_return = oracle.ideal_numerator(ideal, return_recipe, multiplicity)
        need(ideal_return == [(a << (2*rank), b << (2*rank)) for a, b in fine],
             "actual outbound/return native recipe ideal fixture")
    error2 = sum(((a << rank) - c)**2 + ((b << rank) - d)**2
                 for (a, b), (c, d) in zip(sent, ideal, strict=True))
    norm2 = sum(a * a + b * b for a, b in fine)
    need((error2 << (2 * beta + 2)) <= (norm2 << (2 * rank)), "exact relative forward bound")
    need(error2 <= rank**2 * (count // 2) * (1 << (2 * rank)), "absolute pair-error bound")
    need(sum(a * a + b * b for a, b in ideal) == norm2 << (2 * rank), "Walsh/native unitarity")
    sent_norm2 = sum(a * a + b * b for a, b in sent)
    need(error2 << (2 * beta) <= sent_norm2 << (2 * rank), "paired inverse relative bound")
    if mode == "zero":
        need(F == f and updated == query and error2 == 0, "zero-sum boundary")
    if mode in ("rounding", "promoted") and multiplicity == 2:
        need(error2 > 0, "genuine nonlinear rounding fixture")
        need((F > f) == (mode == "promoted"), "promotion control distinguishes grids")
    return dict(multiplicity=multiplicity, mode=mode, components=count, rank=rank,
                input_grid=f, beta=beta, output_grid=F, promotion=F-f,
                source_sha256=source_hashes, entrance_query_sha256=query_hash,
                sent_sha256=digest(sent), query_sha256=digest(updated),
                squared_error_numerator=error2, squared_error_denominator=1 << (2*rank),
                input_norm2_at_working_grid=norm2, sent_norm2_at_working_grid=sent_norm2,
                exact_return=True, private_zero=True,
                original_return_recipe_ideal_fixture_checked=return_recipe is not None,
                literal_pair_sites_both_directions=count*rank,
                wrapper_values_both_directions=4*count, scalar_field_adds=11)


def basic_controls(recipe, plans):
    checks = 0
    for ar, ai, br, bi in itertools.product(range(-3, 4), repeat=4):
        values = [(ar, ai), (br, bi)]
        got = list(pair(*values))
        need(got == oracle.rounded(values, 1), "signed pair/parity identity")
        need(list(pair(*got, inverse=True)) == values, "pair bijection")
        checks += 1
    x = [((j * 31) % 41 - 20, (j * 17) % 43 - 21) for j in range(512)]
    got = native(x, plans, 7)
    need(got == oracle.native(x, recipe, 1), "lambda1 independent native")
    need(native(got, plans, 7, True) == x, "lambda1 literal inverse")
    wrong = native(got, plans, 7, True, order=list(reversed(range(7))))
    need(wrong != x, "wrong inverse order must fail")
    impulse = [(1, 0), (0, 0), (0, 0), (0, 0)]
    natural = lift(impulse, 2)
    reordered = lift(impulse, 2, order=[1, 0])
    need(natural != reordered, "forward order is not an ideal tensor identity")
    need(lift(natural, 2, True) == impulse and lift(reordered, 2, True, [1, 0]) == impulse,
         "matching cleanup alone does not distinguish changed forward word")
    return dict(exhaustive_signed_pairs=checks, wrong_inverse_order_rejected=True,
                order_witness=dict(input=impulse, natural=natural, reversed=reordered,
                                   both_paired_inverses_restore=True))


def tensor_controls(recipe, plans):
    """Bind full maps on every address; explicit layout/global-phase controls."""
    markers = [(j + 1, 0) for j in range(1 << 18)]
    receipts = []
    for side, table in zip(("left", "right"), plans, strict=True):
        got = apply_plan(markers, table)
        need(got == oracle.monomial(markers, recipe[side], 2), "all-address exact tensor monomial")
        need(apply_plan(got, table, True) == markers, "full tensor wrapper inverse")
        base = oracle.column_table(recipe[side])
        wrong_layout = None
        for address, expected in enumerate(table):
            lo, hi = address & 511, address >> 9
            wrong = (base[lo][0] | (base[hi][0] << 9), (base[lo][1] + base[hi][1]) % 4)
            if wrong != expected:
                wrong_layout = dict(address=address, correct=list(expected), copy_major=list(wrong))
                break
        need(wrong_layout is not None, "copy-major without conversion changes actual map")
        receipts.append(dict(side=side, addresses=len(table), output_sha256=digest(got),
                             wrong_layout_witness=wrong_layout))
    need(recipe["right"]["phase"] == 1, "nonzero actual right constant")
    # Forgetting one factor's constant rotates every right-wrapper output by -i.
    correct = plans[1][0]
    wrong_constant = (correct[0], (correct[1] - 1) % 4)
    need(wrong_constant != correct, "omitted tensor constant")
    return dict(wrappers=receipts, omitted_tensor_constant=dict(address=0,
                correct=list(correct), wrong=list(wrong_constant)))


def run(full=True):
    _, word, records = source_inputs()
    recipes = bind(word, records)
    small = tuple(plan(recipes[0][side], 1) for side in ("left", "right"))
    controls = basic_controls(recipes[0], small)
    cases = [check_case(recipes[0], small, 1, "rounding")]
    if full:
        large = tuple(plan(recipes[0][side], 2) for side in ("left", "right"))
        controls["tensor"] = tensor_controls(recipes[0], large)
        for mode in ("rounding", "promoted", "cancellation", "zero"):
            cases.append(check_case(recipes[0], large, 2, mode,
                                    recipes[1] if mode == "rounding" else None))
    return dict(schema_version=1, actual_events=[2025, 2039], native_events=[2031, 2033],
                recipe_sha256=[digest(r) for r in recipes], controls=controls, cases=cases,
                scope="finite exact scalar tensor boundary; no fast physical trace, all-size proof or new kappa")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run(not args.quick)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif not args.quick:
        expected = read_json((HERE / "RESULT.json").read_bytes())
        compare_receipt(result, expected)
    print("PASS_P104_TENSOR_COLLECTOR_AUDIT cases=" + str(len(result["cases"])) + " no_new_kappa", file=sys.stderr)


if __name__ == "__main__":
    main()
