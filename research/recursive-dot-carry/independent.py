"""Independent replay of the frozen recursive dot/carry proof and circuit DAGs."""

import argparse
import ast
from collections import Counter
from decimal import Decimal, localcontext
from hashlib import sha256
from itertools import islice, product
import json
from pathlib import Path
from random import Random


FROZEN_SHA256 = {
    "PROOF.md": "91a07dc16676855f4c8dee00d585aa4b76ecc9598d0bfa9505b2586f117c0f66",
    "verify.py": "d9d79479677fd0bbabb5ea53922d5cd9c77ab63cb9705e10ae8364f640ef30c1",
    "circuits.py": "6c42072338a467acbab3c177fbb9c1a0bd0db22bb550cc31a261bb43951a3ed8",
    "RESULT.json": "0ef14058b848348703d7ae42e89811f881965a0f0bdcc72679754316e8ef6535",
}


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def residue(words, m, a, b):
    x, u, y, v, c = words
    modulus = 1 << m
    d = max(0, m + 1 - a - b)
    mean_x = ((x + u) // 2) % (modulus // 2)
    mean_y = ((y + v) // 2) % (modulus // 2)
    diff_x = (u - x) // (1 << a)
    diff_y = (v - y) // (1 << b)
    return (2 * mean_x * mean_y + ((diff_x * diff_y % (1 << d)) << (a + b - 1)) + c) % modulus


def direct(words, m):
    x, u, y, v, c = words
    return (x * y + u * v + c) % (1 << m)


def congruence_checks():
    # The determinant criterion would erroneously accept this smallest mixed minor.
    pairs_mod_4 = tuple(product(range(4), repeat=2))
    require((2 * 2) % 4 == 0, "determinant control setup")
    require(
        all(tuple(s * t % 4 for s in left for t in right) != (2, 0, 0, 2)
            for left, right in product(pairs_mod_4, repeat=2)),
        "degenerate determinant control",
    )

    exact = 0
    for m in range(2, 6):
        modulus = 1 << m
        pairs = {
            a: [(x, u) for x, u in product(range(modulus), repeat=2) if (u - x) % (1 << a) == 0]
            for a in range(1, m + 1)
        }
        for a, b in product(pairs, repeat=2):
            failed_without_residual = False
            for (x, u), (y, v) in product(pairs[a], pairs[b]):
                c = (3 * x - 7 * u + 11 * y - 13 * v) % modulus - modulus
                words = (x, u, y, v, c)
                want = direct(words, m)
                require(residue(words, m, a, b) == want, (m, a, b, words))
                if ((x + u) * (y + v) // 2 + c) % modulus != want:
                    failed_without_residual = True
                exact += 1
            require(failed_without_residual == (a + b <= m), (m, a, b, "no correction"))

    rng = Random(2941362)
    signed = 0
    residual_witnesses = 0
    for m in (2, 3, 5, 8, 16, 63, 257, 1024):
        modulus = 1 << m
        choices = [(m, 1), (1, m), (m, m), (1, m - 1), (1, 1)]
        choices += [(rng.randint(1, m), rng.randint(1, m)) for _ in range(101)]
        for a, b in choices:
            x, y, v, z, c = (rng.randrange(-2 * modulus, 2 * modulus) for _ in range(5))
            words = (x, x + (v << a), y, y + (z << b), c)
            require(residue(words, m, a, b) == direct(words, m), (m, a, b, "signed lifts"))
            signed += 1
        for a, b in product(range(1, min(m, 8) + 1), repeat=2):
            d = m + 1 - a - b
            if 1 <= d <= 8:
                require(d <= m - a and d <= m - b, "inadmissible residual dimensions")
                for swapped in (False, True):
                    outputs = set()
                    for k in range(1 << d):
                        v, z = (1, k) if swapped else (k, 1)
                        p, q = v << (a - 1), z << (b - 1)
                        words = (-p, p, -q, q, -29)
                        require(residue(words, m, a, b) == direct(words, m), "residual witness")
                        outputs.add(direct(words, m))
                    require(len(outputs) == 1 << d, "narrow residual alias")
                    residual_witnesses += 1

    low_width_alias = [direct((-k, k, -1, 1, 0), 5) for k in (0, 8)]
    require(low_width_alias == [0, 16] and 0 % 8 == 8 % 8, "lost residual bit control")
    return {
        "exhaustive_case_count": exact,
        "independent_signed_lift_cases": signed,
        "residual_separation_families": residual_witnesses,
        "zero_determinant_non_outer_product_mod_4": [[2, 0], [0, 2]],
        "three_bit_alias_outputs_for_four_bit_residual": low_width_alias,
    }


def odd_channel_checks():
    results = []
    for m in range(3, 7):
        modulus = 1 << m
        half = modulus // 2
        inner_mask = half // 2 - 1
        odds = tuple(product(range(1, modulus, 2), repeat=2))
        canonical = {
            (x, u): (x & (half - 1), u ^ (x & half)) for x, u in odds
        }
        # One effective shift for each floor(c/2) mod 2^(m-1), with signed and odd lifts.
        carries = tuple(range(-modulus + 1, 0, 2)) + (0,)
        for carry in carries:
            signatures = {}
            for x, u in odds:
                row = bytes(((x * y + u * v + carry) >> (m - 1)) & 1 for y, v in odds)
                require(0 in row and 1 in row, (m, carry, x, u, "constant row"))
                signature = canonical[x, u]
                require(signatures.setdefault(row, signature) == signature, (m, carry, "wrong alias"))
            row_count = len(signatures)
            require(row_count == 1 << (2 * m - 3), (m, carry, row_count))
            require(row_count > (1 << (2 * m - 3)) - 1, "zero-code exclusion")
        codes = set()
        for x, u in odds:
            code = ((x & half) ^ (u & half)) >> (m - 1)
            code = code << (m - 2) | ((u >> 1) & inner_mask)
            code = code << (m - 2) | ((x >> 1) & inner_mask)
            unpacked_x = 1 | ((code & inner_mask) << 1)
            unpacked_u = 1 | ((code >> (m - 2)) << 1)
            require((unpacked_x, unpacked_u) == canonical[x, u], "channel decode")
            codes.add(code)
        require(codes == set(range(row_count)), "attaining constant-one channels")
        results.append({
            "m": m, "row_classes": row_count, "minimum_total_width_per_side": row_count.bit_length(),
            "distinct_carry_shifts": half, "checked_carry_lifts": len(carries),
        })
    zero_code_outputs = [direct((1, 1, 1, v, 0), 3) >> 2 for v in (1, 3)]
    reflection_outputs = [direct((x, x, 1, 1, 0), 3) >> 2 for x in (1, 3)]
    require(zero_code_outputs == reflection_outputs == [0, 1], "odd-width negative controls")
    return {"rows": results, "zero_code_and_reflection_control_outputs": [0, 1]}


def load_frozen_builder(directory):
    for name, digest in FROZEN_SHA256.items():
        require(sha256((directory / name).read_bytes()).hexdigest() == digest, f"source pin {name}")
    # Extract only the frozen DAG generator. Neither verifier nor evaluator is loaded.
    tree = ast.parse((directory / "circuits.py").read_text(encoding="utf-8"))
    circuit = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Circuit")
    methods = {"__init__", "input", "gate", "add", "low_product"}
    circuit.body = [node for node in circuit.body if isinstance(node, ast.FunctionDef) and node.name in methods]
    build = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build")
    namespace = {}
    exec(compile(ast.Module(body=[circuit, build], type_ignores=[]), "frozen circuit builder", "exec"), namespace)
    return namespace["build"]


def compile_reversible(dag, outputs, width):
    inputs = 5 * width
    require(dag.inputs == inputs and len(outputs) == width, "input/output width")
    instructions = []
    gates = Counter()
    for target, (op, left, right) in enumerate(dag.gates, inputs + 1):
        require(0 < left < right < target and op in ("and", "xor"), (target, op, left, right))
        gates[op] += 1
        if op == "xor":
            instructions.extend(((target, left), (target, right)))
        else:
            instructions.append((target, left, right))
    allocated = inputs + len(dag.gates)
    require(all(0 < source <= allocated for source in outputs), "invalid copy source")
    copy = [(allocated + out, source) for out, source in enumerate(outputs, 1)]
    word = instructions + copy + instructions[::-1]
    types = Counter(map(len, word))
    invoice = {
        "and": gates["and"], "xor": gates["xor"], "clean_scratch_bits": len(dag.gates),
        "clean_cnot": types[2], "clean_toffoli": types[3],
    }
    return word, allocated, invoice


def planes(words, width):
    packed = 0
    for index, word in enumerate(words):
        packed |= word << (index * width)
    columns = ((packed >> bit) for bit in range(width))
    mask = sum(1 << (index * width) for index in range(len(words)))
    return [column & mask for column in columns]


def reversible_batch(cases, width, program, allocated, clean=True):
    read_only = [0]
    for field in zip(*cases, strict=True):
        read_only.extend(planes(field, width))
    input_size = len(read_only)
    seeds = [(37 * i ^ 0xA5) % (1 << width) for i in range(len(cases))]
    initial = planes(seeds, width)
    values = read_only + [0] * (allocated + 1 - input_size) + initial
    for target, control, *other in program:
        update = values[control] & values[other[0]] if other else values[control]
        values[target] ^= update
    expect = planes([direct(case, width) ^ seed for case, seed in zip(cases, seeds)], width)
    require(values[:input_size] == read_only and values[-width:] == expect, ("reversible ports", width))
    scratch_is_zero = not any(values[input_size:-width])
    require(scratch_is_zero == clean, ("clean scratch", width, clean))


def circuit_cases(m):
    if m == 4:
        for x, y, ux, vy, carry in product(range(16), range(16), range(4), range(4), range(16)):
            yield x, x ^ (ux << 2), y, y ^ (vy << 2), carry
    else:
        rng = Random(54103)
        for index in range(4096):
            x, y = ((index >> bit) & 255 for bit in (0, 4)) if index < 256 else (
                rng.randrange(256), rng.randrange(256)
            )
            u, v = x ^ (rng.randrange(16) << 4), y ^ (rng.randrange(16) << 4)
            dot = x * y + u * v
            for carry in (0, 255, -dot, 127 - dot, 128 - dot):
                yield x, u, y, v, carry % 256


def circuit_checks(directory):
    builder = load_frozen_builder(directory)
    expected = json.loads((directory / "RESULT.json").read_text(encoding="utf-8"))["circuits"]
    results = []
    for row in expected:
        width, a, b = (row[key] for key in ("m", "a", "b"))
        programs = {}
        result = {"m": width, "a": a, "b": b}
        for fused, name in ((False, "two_products"), (True, "shared_carry")):
            dag, outputs = builder(width, a, b, fused)
            program, allocated, invoice = compile_reversible(dag, outputs, width)
            require(invoice == row[name], (width, name, invoice, row[name]))
            programs[name] = program, allocated
            result[name] = invoice
        cases = circuit_cases(width)
        count = 0
        while batch := list(islice(cases, 128)):
            for program, allocated in programs.values():
                reversible_batch(batch, width, program, allocated)
            count += len(batch)
        result["independent_cases"] = count
        # Remove the uncompute suffix while keeping correct input/output ports.
        case = [(1, 1, 1, 1, (1 << (width - 1)) - 2)]
        for program, allocated in programs.values():
            reversible_batch(case, width, program[:(len(program) + width) // 2], allocated, clean=False)
        results.append(result)
    bad_no_toggle = (4 + 0) * (4 + 0) // 2
    require(bad_no_toggle % 16 == 8 and direct((0, 4, 0, 4, 0), 4) == 0, "missing toggle control")
    require(direct((1, 1, 1, 1, 6), 4) == 8 and direct((1, 1, 1, 1, 0), 4) == 2, "carry control")
    return results


def compare_price(path):
    quoted = json.loads(path.read_text(encoding="utf-8"))
    target = Decimal(quoted["target"])
    require(target == Decimal("0.003884928046155"), "enrolled target")
    require(target - Decimal(quoted["comparator_upper"]) == Decimal("0.000005"), "target gain")
    require(quoted["source_verified_head"] == "87fbf4f7b35b0f18ab12b5767775a9a424cf0b15", "comparator head")
    crosscheck = {}
    with localcontext() as context:
        context.prec = 75
        for side, native_calls in (("rational", 48), ("binary", 36)):
            invoice = quoted["sides"][side]
            price = {grade: Decimal(grade) ** (1 - target) for grade in invoice["paid"] | invoice["targets"]}
            margin = sum((invoice["targets"].get(k, 0) - invoice["paid"].get(k, 0)) * p for k, p in price.items())
            lower, upper = (Decimal(invoice["signed_margin"][key]) for key in ("lower", "upper"))
            require(lower < margin < upper < 0 and invoice["native_calls"] == native_calls, (side, "price"))
            crosscheck[side] = {"native_calls": native_calls, "unchanged_signed_margin": invoice["signed_margin"]}
    return crosscheck


def main():
    here = Path(__file__).resolve().parent
    primary = here
    if not (primary / "PROOF.md").is_file():
        primary = here.parent.parent / "repo" / "research" / "recursive-dot-carry"
    default_price = here / "reference-price.json"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary", type=Path, default=primary, help="directory of the four pinned primary files")
    parser.add_argument(
        "--comparator", type=Path, default=default_price if default_price.is_file() else None,
        help="pinned price input, defaulting to reference-price.json beside the checker when present",
    )
    args = parser.parse_args()
    result = {
        "status": "PASS_SCOPED_INDEPENDENT_REVIEW",
        "frozen_sha256": FROZEN_SHA256,
        "congruence": congruence_checks(),
        "odd_channels": odd_channel_checks(),
        "circuits": circuit_checks(args.primary),
        "finite_circuit_signed_credit": "0",
    }
    if args.comparator:
        result["comparator_check"] = compare_price(args.comparator)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
