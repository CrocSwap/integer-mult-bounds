"""Independent source binding, symbolic cache, and selector review oracle.

Only the proposed precision API and the pinned Grid/product_diagonal bodies
are executed as subjects under test. No author checker, compiler factory,
matrix helper, or earlier reviewer oracle is imported. Universal inequalities
are proved in REVIEW.md; finite checks do not replace those arguments.
"""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
from math import prod
from pathlib import Path
import argparse
import ast
import copy
import importlib.util
import json
import sys

CANDIDATE_PINS = {
    "PROOF-DRAFT.md": "0501a6a9a5f467fff4c998606965babc8157e74d98cf33b93f71fb10674d57bb",
    "precision.py": "9c3e99219f741c5b08c0628c30784cf72c60b4421beae3373fa976aeffcd8e20",
    "check.py": "4eccf9d085d53ebb3580ba0f4868d177c4e077f3146754f2b2b4fb10c9267420",
    "TARGET.md": "c54ce9533c7e82120bb41feae8084b2464c52e34d1f5ec57b3cfd1d7550b32bf",
    "EVIDENCE.json": "d2377d5cb672eee75537553b2e21284db660b6442ede929b5fbd1f7d53b2f395",
}
CUT_PROOF = "e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07"
PARENT_PROOF = "26e4e214f0a5785c1d1414561465bb49a3248f9e6f59f6b514eb95a887bdfe2f"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def authenticate(candidate, cuts, parent):
    for name, expected in CANDIDATE_PINS.items():
        need(digest(candidate/name) == expected, "candidate differs: " + name)
    need(digest(cuts/"PROOF.md") == CUT_PROOF, "cut theorem differs")
    need(digest(parent/"PROOF.md") == PARENT_PROOF, "parent theorem differs")
    records = []
    for root, key in ((cuts, "local"), (parent, "file")):
        origins = json.loads((root/"ORIGINS.json").read_text())
        for item in origins["files"]:
            relative = item[key] if key == "local" else "retained/" + item[key]
            raw = (root/relative).read_bytes()
            need(sha256(raw).hexdigest() == item["sha256"], "source SHA: " + relative)
            blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            need(blob == item["git_blob"], "source Git blob: " + relative)
            records.append({"path": relative, "commit": item["commit"], "sha256": item["sha256"]})
    return records


def named(nodes, name, kind=ast.FunctionDef):
    matches = [node for node in nodes if isinstance(node, kind) and node.name == name]
    need(len(matches) == 1, "unique source definition: " + name)
    return matches[0]


def expression_equal(node, expected):
    normalized = copy.deepcopy(node)
    reference = ast.parse(expected, mode="eval").body
    for tree in (normalized, reference):
        for part in ast.walk(tree):
            if hasattr(part, "ctx"):
                part.ctx = ast.Load()
    return ast.dump(normalized, include_attributes=False) == ast.dump(reference, include_attributes=False)


def assignment(function, name):
    hits = [node.value for node in ast.walk(function) if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)]
    need(len(hits) == 1, "unique assignment: " + name)
    return hits[0]


def source_bindings(cuts, parent):
    full = ast.parse((cuts/"retained/full.py").read_text())
    generator = ast.parse((cuts/"retained/generator.py").read_text())
    source_class = named(full.body, "Full", ast.ClassDef)
    shear = named(source_class.body, "shear")
    calls = [node for node in ast.walk(shear) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == "generator_allocation"]
    need(len(calls) == 1 and expression_equal(calls[0],
         'generator_allocation(m, len(items), be, 1, self.bound["child_target_bits"], 0)'),
         "Full forwards actual rank and be at the original child target")
    prepared = [node for node in ast.walk(shear) if isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "prepare"]
    need(len(prepared) == 1 and expression_equal(prepared[0].targets[0],
         "(items, displacement, be, heights)"), "be is returned by prepare")
    prep = named(generator.body, "prepare")
    need(expression_equal(assignment(prep, "bound_e"),
         "max(max(component_l1(row) for row in displacement), max(component_l1(column) for column in zip(*displacement)))"),
         "actual component envelope")
    child = named(generator.body, "allocation")
    for name, formula in {
        "checkpoint": "10 + 4 * alpha + 2 * kg",
        "child": "max(Q(3200 * m ** 3), 2 + 2 * kg)",
        "execution": "child * checkpoint",
    }.items():
        need(expression_equal(assignment(child, name), formula), "literal child formula: " + name)
    pair = [node for node in child.body if isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Tuple)
            and expression_equal(node.targets[0], "(kg, alpha)")]
    need(len(pair) == 1 and expression_equal(pair[0].value,
         "(2 * m + 16 * m * bound_e, 2 * rank * m * bound_e)"), "literal child kg and alpha")
    root = ast.parse((parent/"retained/root_gate_plan.py").read_text())
    compile_root = named(root.body, "compile_padded_root")
    need(expression_equal(assignment(compile_root, "size_bound"),
         "max(Fraction(1), compiler.full.norm_upper(matrix))"), "component Lambda guard unchanged")
    need(expression_equal(assignment(compile_root, "inverse_bound"),
         "Fraction(2 * target_width) / min(Fraction(1), margin)"), "component Q guard unchanged")
    product_source = ast.parse((parent/"retained/product.py").read_text())
    source_calls = [node for node in ast.walk(product_source) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name) and node.func.id == "fourier_axis"]
    need(len(source_calls) == 1 and expression_equal(source_calls[0],
         "fourier_axis(compiler, r, t, -1, work_bits + 8)"), "external P+8 binding")
    return ["actual prepared be and len(items)", "same original child_target_bits", "exact component row/column envelope",
            "literal child norm formulas", "unchanged component Lambda and Q guards", "external work_bits+8"]


def padd(a, b, sign=1):
    return [((a[i] if i < len(a) else 0) + sign*(b[i] if i < len(b) else 0))
            for i in range(max(len(a), len(b)))]


def pmul(a, b):
    result = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i+j] += x*y
    return result


def ppow(a, k):
    result = [1]
    for _ in range(k):
        result = pmul(result, a)
    return result


def exact_polynomials():
    depth = padd([1], pmul([0, 2], pmul([8, 2], [18, 32, 8])))
    need(depth == [1, 288, 584, 256, 32], "source depth expansion")
    difference = padd([20000*x for x in ppow([2, 1], 6)],
                      [4*x for x in pmul(depth, [11, 12])], -1)
    need(all(x > 0 for x in difference), "universal stage polynomial coefficient certificate")
    # Use exponent vectors for 2^a*t^b. No floating-point logarithms are used.
    def times(*pairs):
        return tuple(sum(x[i] for x in pairs) for i in (0, 1))
    b, h, l0 = (7, 3), (23, 7), (2, 1)
    k = times((1, 0), l0, b, h)
    gate = times((1, 0), b, b, h, h)
    root = times((2, 0), k, (240, 0), (1, 0), gate)
    axis = times((2, 2), root, root)
    scalar = times((240, 0), (1, 0), gate)
    need((k, gate, root, axis, scalar) == ((33, 11), (61, 20), (337, 31), (676, 64), (302, 20)),
         "complete lowering exponent chain")
    need(3200*2318 == 7417600 < 1 << 23, "child constant")
    # The following identities have nonnegative terms for every t>=1.
    # 2318t^4-(10+1280t^4+1028t^3)=10(t^4-1)+1028t^3(t-1).
    need(padd([0, 0, 0, 0, 2318], [10, 0, 0, 1028, 1280], -1)
         == padd([-10, 0, 0, 0, 10], [0, 0, 0, -1028, 1028]), "fragment polynomial factorization")
    return {"depth_coefficients_low_to_high": depth, "stage_difference_coefficients_low_to_high": difference,
            "B": b, "H": h, "K": k, "gate": gate, "routed_root": root, "axis": axis, "diagonal_scalar": scalar,
            "global_spectral_interval": {"d": 2*axis[0]+2, "L": 2*axis[1]},
            "local_error": {"d": scalar[0]+1, "L": scalar[1]}}


def selector_checks(candidate):
    spec = importlib.util.spec_from_file_location("review_subject_precision", candidate/"precision.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    fixtures = []
    for d in range(1, 10):
        for widths in ((1,)*d, (5,)*d, tuple(range(1, d+1)), tuple(1+i % 3 for i in range(d))):
            for p in (1, 17, 72):
                fixtures.append((p, widths))
    fixtures += [(72, (4, 5)), (1, (10**80,)), (10**70, (10**60, 1, 10**61)),
                 (12288, (128,)*16), (9, (1,)*129)]
    examples = []
    for p, widths in fixtures:
        d, length, maximum = len(widths), sum(widths), max(widths)
        stages = 20000*(d+1)*(maximum+2)**6
        coefficient = 4*stages*(d+1)**2+d+1
        # Independent closed form; do not calculate E and A to obtain P.
        proposed = 4*p+277*length+3011*d+(length % 2)+coefficient.bit_length()
        previous = 4*p+1361*length+4746*d+(length % 2)+coefficient.bit_length()
        q = stages*(d+1)
        original = 4*p+32768*(length+6*d)+4*q.bit_length()+64
        result = module.precision_budget(p, widths)
        need(result.fractional_bits == proposed == module.production_precision(p, widths), "selector API equality")
        need(result.interval_exponent == (257*length+1)//2+1354*d, "interval exponent")
        need(result.local_error_exponent == 20*length+303*d, "local exponent")
        need(result.stage_bound == stages and result.envelope_coefficient == coefficient, "stage/coefficient API")
        need(previous-proposed == 1084*length+1735*d, "exact parent improvement")
        need(original > previous > proposed, "both predecessor selectors dominate")
        need(coefficient <= 5*q*q and coefficient.bit_length() <= 2*q.bit_length()+3,
             "universal source-dominance coefficient inequality")
        denominator = 1 << coefficient.bit_length()
        need(coefficient < denominator and 4*stages*(d+1)**2 < denominator, "strict error and bootstrap spend")
        need(2*coefficient >= denominator, "one-bit undercharge loses strict certificate")
        need(result.interval_exponent >= d-1+(length+1)//2, "endpoint bias absorption")
        if (p, widths) in fixtures[-5:]:
            examples.append({"p": p, "widths": widths, "new": proposed, "previous": previous,
                             "original": original, "normalized_error_cap": str(F(coefficient, denominator))})
    invalid = [(0, (1,)), (True, (1,)), (1, ()), (1, (0,)), (1, (-1, 2)), (1, (True,)), (1, (F(1),))]
    for args in invalid:
        try:
            module.production_precision(*args)
        except ValueError:
            pass
        else:
            raise ValueError("invalid selector input accepted: " + repr(args))
    return {"cases": len(fixtures), "invalid_inputs_rejected": len(invalid), "examples": examples}


def extract_tensor_subject(parent):
    tree = ast.parse((parent/"retained/tensor_word.py").read_text())
    grid = named(tree.body, "Grid", ast.ClassDef)
    diagonal = named(tree.body, "product_diagonal")
    namespace = {"Fraction": F, "word_product": lambda a, b: a*b, "prod": prod}
    exec(compile(ast.Module(body=[copy.deepcopy(grid), copy.deepcopy(diagonal)], type_ignores=[]),
                 "pinned_Grid_and_product_diagonal", "exec"), namespace)
    mutant = copy.deepcopy(diagonal)
    carry = [node for node in ast.walk(mutant) if isinstance(node, ast.For)
             and isinstance(node.target, ast.Name) and node.target.id == "k"]
    need(len(carry) == 1, "unique carry suffix loop")
    carry[0].iter = ast.parse("range(0)", mode="eval").body
    mutated = {"prod": prod}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[mutant], type_ignores=[])),
                 "negative_control_skipped_carry_refresh", "exec"), mutated)
    return namespace["Grid"], namespace["product_diagonal"], mutated["product_diagonal"]


class SymbolGrid:
    one = ("one",)

    def multiply(self, left, right):
        if left == self.one:
            return right
        if right == self.one:
            return left
        return ("multiply", left, right)


def coordinates(index, sides):
    result = []
    for side in sides:
        result.append(index % side)
        index //= side
    need(index == 0, "mixed-radix index")
    return result


def expected_tree(index, sides):
    args = [("factor", k, j) for k, j in enumerate(coordinates(index, sides))]
    result = args[-1]
    for arg in reversed(args[:-1]):
        result = ("multiply", arg, result)
    return ("multiply", result, ("data", index))


def cmul(x, y):
    return (x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0])


def abs2(z):
    return z[0]*z[0]+z[1]*z[1]


def sub(x, y):
    return x[0]-y[0], x[1]-y[1]


def cache_checks(parent):
    Grid, apply, mutant = extract_tensor_subject(parent)
    patterns = [(2,), (2, 2), (4, 2), (2, 4, 2), (4, 2, 4, 2),
                (2, 2, 2, 2, 2), (2, 4, 2, 4, 2)]
    symbolic_records = 0
    numerical_records = 0
    zero_factor_records = 0
    for sides in patterns:
        table = [[("factor", k, j) for j in range(side)] for k, side in enumerate(sides)]
        data = [("data", i) for i in range(prod(sides))]
        apply(data, table, SymbolGrid())
        for i, value in enumerate(data):
            need(value == expected_tree(i, sides), "coefficient depends only on current factors")
            symbolic_records += 1
        exact_tables = [[(F(((3*j+2*k) % 9)-4, 3), F(((j+3*k) % 7)-3, 5))
                         if (j+k) % 5 else (F(0), F(0)) for j in range(side)]
                        for k, side in enumerate(sides)]
        for bits in (2, 5, 11):
            grid = Grid(bits)
            tables = [[(round(a*grid.unit), round(b*grid.unit)) for a, b in row] for row in exact_tables]
            coefficients = [grid.one]*prod(sides)
            apply(coefficients, tables, grid)
            inputs = [(grid.unit*(i % 7-3)+1, grid.unit*(i % 5-2)-1) for i in range(prod(sides))]
            actual = list(inputs)
            apply(actual, tables, grid)
            d = len(sides)
            # Every exact table factor has modulus <= its component l1 <= 2.
            need(all(abs(a)+abs(b) <= 2 for row in exact_tables for a, b in row), "independent factor cap")
            factor_product = 2**d
            coefficient_error = F(2*d*2**d*factor_product, grid.unit)
            local_epsilon = F((d+1)**2*2**d*factor_product, grid.unit)
            for index in range(prod(sides)):
                exact = (F(1), F(0))
                factors = [exact_tables[k][j] for k, j in enumerate(coordinates(index, sides))]
                for factor in factors:
                    exact = cmul(exact, factor)
                stored_coefficient = tuple(F(x, grid.unit) for x in coefficients[index])
                need(abs2(sub(stored_coefficient, exact)) <= coefficient_error**2, "coefficient roundoff cap")
                value = tuple(F(x, grid.unit) for x in inputs[index])
                output = tuple(F(x, grid.unit) for x in actual[index])
                cap = local_epsilon*(1+abs(value[0])+abs(value[1]))
                need(abs2(sub(output, cmul(exact, value))) <= cap*cap, "nonlinear local data envelope")
                numerical_records += 1
                zero_factor_records += any(factor == (0, 0) for factor in factors)
    sides = (2, 2)
    bad = [("data", i) for i in range(4)]
    mutant(bad, [[("factor", k, j) for j in range(2)] for k in range(2)], SymbolGrid())
    bad_records = sum(value != expected_tree(i, sides) for i, value in enumerate(bad))
    need(bad_records == 2, "negative control catches skipped carry refresh")
    return {"symbolic_records": symbolic_records, "numerical_records": numerical_records,
            "zero_factor_records": zero_factor_records, "rounding_grids": [2, 5, 11],
            "broken_carry_records_rejected": bad_records}


def domain_controls():
    # Orthogonal rational rotation: exact spectral norm 1, component envelope 7/5.
    a, b = F(3, 5), F(4, 5)
    need(a*a+b*b == 1 and a+b == F(7, 5) > 1, "spectral/component separation")
    # The full inverse of a swap has norm 1, although its first leading section is singular.
    swap = ((0, 1), (1, 0))
    square = tuple(tuple(sum(swap[i][k]*swap[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    need(square == ((1, 0), (0, 1)) and swap[0][0] == 0, "whole inverse cannot replace all leading solves")
    # A strictly accretive, non-Toeplitz padded 3x3 block has leading inverses <= 1.
    skew = ((0, 1, -2, 0), (-1, 0, 3, 0), (2, -3, 0, 0), (0, 0, 0, 0))
    matrix = tuple(tuple(F(i == j) + F(skew[i][j], 16) for j in range(4)) for i in range(4))
    need(all(matrix[i][j]+matrix[j][i] == 2*int(i == j) for i in range(4) for j in range(4)),
         "padded non-Toeplitz accretivity")
    need(matrix[1][0] != matrix[2][1] and matrix[3][3] == 1 and all(matrix[3][j] == 0 for j in range(3)),
         "padding does not preserve Toeplitz structure")
    # ||skew/16|| <= ||.||_F < 1, hence ||matrix|| < 2, uniformly for all leading restrictions.
    frobenius2 = sum(F(x, 16)**2 for row in skew for x in row)
    need(frobenius2 < 1, "independent spectral admission of the padded fixture")
    return {"rotation_component_envelope": "7/5", "full_inverse_only_rejected": True,
            "non_toeplitz_padded_fixture": {"spectral_root_cap": 2, "leading_inverse_cap": 1,
                                            "skew_frobenius_squared": str(frobenius2)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--cuts", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    origins = authenticate(args.candidate, args.cuts, args.parent)
    evidence = {"status": "PASS_INDEPENDENT_SHARP_SELECTOR_REVIEW", "source_records": origins,
                "candidate_pins": CANDIDATE_PINS, "cut_proof": CUT_PROOF, "parent_proof": PARENT_PROOF,
                "source_bindings": source_bindings(args.cuts, args.parent), "polynomials": exact_polynomials(),
                "selector": selector_checks(args.candidate), "cache": cache_checks(args.parent),
                "domain_controls": domain_controls(),
                "limits": "Finite source and exact arithmetic checks supplement the universal written review. Native H, phase/rank, Fourier, storage and recovery contracts remain premises."}
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True)+"\n")
    print(json.dumps({key: evidence[key] for key in ("status", "source_bindings", "cache", "domain_controls")}, indent=2))


if __name__ == "__main__":
    main()
