"""Exact corroboration of the selected phase's sharp linear statistic."""

import hashlib
import itertools
import json
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SUPPORT = (0, 1, 2, 3, 5, 6)
SOURCE_HASH = "96fadb44c3316be93c6c02f50cd2c841a9541d67b98fd94fc47b73fa64dd404c"
FILES = (
    "README.md", "PROOF.md", "PREDECESSOR-RECIPE.json", "verify.py",
    "TASK.json", "SOURCES.json", "VERIFY.json",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_recipe():
    path = ROOT / "PREDECESSOR-RECIPE.json"
    require(path.is_file() and not path.is_symlink(), "recipe file")
    require(path.stat().st_size < 65536, "recipe size")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_HASH, "source bytes")
    data = json.loads(raw)
    require(data["native_event_index"] == 24472, "source event")
    require(data["side"] == "right", "source side")
    require(data["event"] == ["MOVE", 415, 3, 99, False], "source occurrence")
    require(data["recipe"] == data["lowered_recipe"]["right"], "source lowering")
    return data["recipe"]


def literal_phase(address, recipe):
    """Strict-upper polynomial oracle, without the contracted formula."""
    require(type(address) is int and 0 <= address < 512, "address domain")
    bits = tuple((address >> i) & 1 for i in range(9))
    value = recipe["phase"]
    for i in range(9):
        value += recipe["linear_Z4"][i] * bits[i]
        for j in range(i + 1, 9):
            value += 2 * bits[i] * bits[j] * ((recipe["quadratic_rows"][i] >> j) & 1)
    return value % 4


def observations(columns):
    require(type(columns) is tuple and 1 <= len(columns) <= 64, "column domain")
    require(all(type(x) is int and 0 <= x < 512 for x in columns), "column value")
    parities = tuple(sum((x >> i) & 1 for i in SUPPORT) % 2 for x in columns)
    sign = sum((x >> 7) & 1 for x in columns) % 2
    return parities, sign


def compressed_phase(columns):
    parities, sign = observations(columns)
    return (len(columns) + 3 * sum(parities) + 2 * sign) % 4


def primary_period(columns):
    parities, sign = observations(columns)
    return not any(parities) and sign == 0


def constant_derivatives(table):
    """All 512 truth-table translates, checked on every base point."""
    constants = []
    comparisons = 0
    for shift in range(512):
        differences = set()
        for x in range(512):
            differences.add((table[x ^ shift] - table[x]) % 4)
            comparisons += 1
        constants.append(next(iter(differences)) if len(differences) == 1 else None)
    return tuple(constants), comparisons


def one_column(recipe):
    table = tuple(literal_phase(x, recipe) for x in range(512))
    for x in range(512):
        require(table[x] == compressed_phase((x,)), "one-column identity")
    constants, comparisons = constant_derivatives(table)
    periods = 0
    for shift in range(512):
        require((constants[shift] == 0) == primary_period((shift,)), "one-column period")
        periods += constants[shift] == 0
    # Exhaust every one-bit linear observation, including the zero map.
    rejected_maps = 0
    for mask in range(512):
        fibers = (set(), set())
        for x in range(512):
            fibers[(mask & x).bit_count() % 2].add(table[x])
        require(any(len(fiber) > 1 for fiber in fibers), "false one-bit statistic")
        rejected_maps += 1
    require(periods == 128, "one-column kernel size")
    return table, constants, comparisons, periods, rejected_maps


def two_columns(table, constants):
    phases = periods = 0
    digest = hashlib.sha256()
    for left, right in itertools.product(range(512), repeat=2):
        literal = (table[left] + table[right]) % 4
        contracted = compressed_phase((left, right))
        require(literal == contracted, "two-column identity")
        digest.update(bytes((literal,)))
        phases += 1
        a, b = constants[left], constants[right]
        oracle = a is not None and b is not None and (a + b) % 4 == 0
        require(oracle == primary_period((left, right)), "two-column period")
        periods += oracle
    require(periods == 32768, "two-column kernel size")
    return phases, periods, digest.hexdigest()


def rotate(pair, phase):
    real, imag = pair
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[phase % 4]


def tensor_fixtures(recipe):
    # Fixed fixtures at larger f are not an exhaustive address census.
    fixtures = rotations = 0
    for f in range(1, 65):
        for seed in range(16):
            columns = tuple((seed * 73 + j * 151 + f * j * j) % 512 for j in range(f))
            literal = sum(literal_phase(x, recipe) for x in columns) % 4
            require(literal == compressed_phase(columns), "larger tensor identity")
            for pair in ((0, 0), (2, -3), (-5, 7)):
                result = rotate(pair, literal)
                require(rotate(result, -compressed_phase(columns)) == pair, "Gaussian inverse")
                rotations += 1
            fixtures += 1
    return fixtures, rotations


def rejection_controls(recipe, table):
    controls = 0
    require(table[0] != (compressed_phase((0,)) - 1) % 4, "constant control")
    controls += 1
    changed = dict(recipe)
    changed["quadratic_rows"] = list(recipe["quadratic_rows"])
    changed["quadratic_rows"][0] ^= 1 << 1
    require(literal_phase(3, changed) != table[3], "deleted pair control")
    controls += 1
    require(compressed_phase((1,)) != (1 + 1) % 4, "odd phase sign control")
    controls += 1
    require(compressed_phase((0,)) != compressed_phase((128,)), "sign observation control")
    controls += 1
    require(compressed_phase((1, 1)) != compressed_phase((0, 0)), "parity-only weight control")
    controls += 1
    require(compressed_phase((0, 0)) != table[0], "repeated constant control")
    controls += 1
    require(not primary_period((1,)), "overlarge kernel control")
    controls += 1
    require(primary_period((128, 128)), "joint-column sign cancellation")
    controls += 1
    invalid = ((), (True,), (-1,), (512,), tuple(0 for _ in range(65)))
    for columns in invalid:
        try:
            observations(columns)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid column accepted")
    return controls


def file_hashes():
    hashes = {}
    for name in FILES:
        path = ROOT / name
        require(path.is_file() and not path.is_symlink(), "package file")
        require(path.stat().st_size <= 1048576, "package size")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    recipe = source_recipe()
    table, constants, derivatives, periods1, maps = one_column(recipe)
    phases2, periods2, digest = two_columns(table, constants)
    fixtures, rotations = tensor_fixtures(recipe)
    result = {
        "status": "PASS_SELECTED_PHASE_LINEAR_STATISTIC",
        "claim_type": "scoped written proof with exact finite corroboration",
        "one_column_addresses": len(table),
        "one_column_derivative_comparisons": derivatives,
        "one_column_periods": periods1,
        "rejected_one_bit_linear_maps": maps,
        "two_column_addresses_and_shifts": phases2,
        "two_column_periods": periods2,
        "two_column_phase_sha256": digest,
        "larger_tensor_fixtures": fixtures,
        "Gaussian_forward_inverse_pairs": rotations,
        "controls": rejection_controls(recipe, table),
        "python": platform.python_version(),
        "source_hashes": file_hashes(),
        "no_new_kappa": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
