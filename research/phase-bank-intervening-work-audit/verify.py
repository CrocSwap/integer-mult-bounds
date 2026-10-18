#!/usr/bin/env python3
"""Source-bound full-column audit; kumagi with OpenAI Codex assistance.

Apache-2.0. Executes Gareth Davidson's unchanged PR2850 model from authenticated
source bytes, without loading its bytecode or calling its reference routines.
All arithmetic is Gaussian integer arithmetic on a sufficiently fine grid.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType


SOURCE = "research/phase-accumulator-tensor-closure/model.py"
SOURCE_SHA256 = "78785eda409a767094381c737ee7347d2412c6a0c02779087a3d403e923a7bc1"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_model(raw):
    require(sha256(raw).hexdigest() == SOURCE_SHA256, "source digest mismatch")
    module = ModuleType("authenticated_phase_model")
    sys.modules[module.__name__] = module
    exec(compile(raw, SOURCE, "exec"), module.__dict__)
    return module


def matrix(model, word, f, grid):
    size = 1 << (3*f)
    result = []
    for column in range(size):
        real, imag = [0]*size, [0]*size
        real[column] = grid
        model.apply(word, real, imag)
        result.append(list(zip(real, imag)))
    return result  # column-major; addresses x | (y << f) | (c << 2f)


def rotate(value, power):
    return ((value, 0), (0, value), (-value, 0), (0, -value))[power % 4]


def closed_formula(f, grid, phase_power=0, phase_on_output=False, dirty=False):
    size, mask = 1 << (3*f), (1 << f)-1
    result = []
    for column in range(size):
        x, c = column & mask, column >> (2*f)
        entries = []
        for row in range(size):
            if row >> (2*f) != c:
                entries.append((0, 0))
                continue
            delta = row ^ column
            sign = -1 if ((delta & mask) & ((delta >> f) & mask)).bit_count() % 2 else 1
            value = sign * (grid >> f)
            bit = (row if phase_on_output else x) & 1
            if dirty:
                bit ^= c & 1
            entries.append(rotate(value, phase_power * bit))
        result.append(entries)
    return result


def open_formula(f, grid):
    size, mask = 1 << (3*f), (1 << f)-1
    result = []
    for column in range(size):
        x, y, c = column & mask, (column >> f) & mask, column >> (2*f)
        entries = []
        for row in range(size):
            xx, yy, cc = row & mask, (row >> f) & mask, row >> (2*f)
            exponent = ((cc ^ c) & (yy ^ y)).bit_count() % 2
            value = (-1 if exponent else 1) * (grid >> f) if xx == x ^ c else 0
            entries.append((value, 0))
        result.append(entries)
    return result


def differences(left, right):
    return sum(a != b for lc, rc in zip(left, right) for a, b in zip(lc, rc))


def bank_is_scalar_identity(mat, f):
    """Test existence of ANY data V, not merely agreement with intended UQ."""
    data_size, banks = 1 << (2*f), 1 << f
    for d in range(data_size):
        for e in range(data_size):
            wanted = mat[d][e]
            for c in range(banks):
                for cc in range(banks):
                    actual = mat[d + c*data_size][e + cc*data_size]
                    if actual != (wanted if c == cc else (0, 0)):
                        return False
    return True


def main():
    root = Path(__file__).resolve().parents[2]
    raw = (root / SOURCE).read_bytes()
    model = load_model(raw)
    controls = []
    try:
        load_model(raw + b"\n# corrupted input\n")
    except ValueError as exc:
        require(str(exc) == "source digest mismatch", "unexpected corruption error")
        controls.append("source mutation rejected before execution")
    else:
        raise ValueError("source mutation accepted")
    fixtures, total_columns, total_coefficients = [], 0, 0
    for f in (1, 2):
        x, y = tuple(range(f)), tuple(range(f, 2*f))
        p = model.accumulator_word(f, half=True)
        q = model.q_word(x, y)
        sx, zx, zc = model.phase((0,)), model.phase((0,), 2), model.phase((2*f,), 2)
        words = {
            "open": p, "closed": p+p,
            "C_data": p+model.c_word((0,))+p,
            "Q_data": p+q+p,
            "X_data": p+[model.Op("translate", (0,))]+p,
            "S_data_stale": p+sx+p, "Z_data_stale": p+zx+p,
            "Z_data_transported": p+zx+zc+p,
            "Z_data_late_repair": p+zx+p+zc,
        }
        grid = 1 << (max(model.denominator_budget(w) for w in words.values()) + 3*f + 4)
        actual = {name: matrix(model, word, f, grid) for name, word in words.items()}
        require(actual["open"] == open_formula(f, grid), "physical P kernel mismatch")
        require(actual["closed"] == closed_formula(f, grid), "P squared differs from Q")
        for name, u in (("C_data", model.c_word((0,))), ("Q_data", q),
                        ("X_data", [model.Op("translate", (0,))])):
            require(actual[name] == matrix(model, q+u, f, grid), name+" control failed")
            require(bank_is_scalar_identity(actual[name], f), name+" did not release bank")
        mismatches = {}
        for name, power in (("S_data_stale", 1), ("Z_data_stale", 2)):
            mat = actual[name]
            require(mat == closed_formula(f, grid, power, dirty=True), name+" residual formula failed")
            require(all(value == (0, 0) or row >> (2*f) == col >> (2*f)
                        for col, entries in enumerate(mat) for row, value in enumerate(entries)),
                    name+" unexpectedly moved bank addresses")
            require(not bank_is_scalar_identity(mat, f), name+" unexpectedly factors")
            target = closed_formula(f, grid, power, phase_on_output=True)
            mismatches[name] = differences(mat, target)
            require(mismatches[name] > 0, name+" stale labels accepted")
            prepared = closed_formula(f, grid, power)
            data_size = 1 << (2*f)
            require(all(mat[col] == prepared[col] for col in range(data_size)),
                    "prepared-bank illustration failed")
            require(mat != prepared, "prepared-bank false positive was not exposed")
            controls.append(f"f={f}: {name} rejects address-only and prepared-bank checks")
        target_z = closed_formula(f, grid, 2, phase_on_output=True)
        require(actual["Z_data_transported"] == target_z, "transported consumer failed")
        require(bank_is_scalar_identity(actual["Z_data_transported"], f), "transport left bank dependence")
        require(actual["Z_data_late_repair"] != target_z, "late correction falsely accepted")
        controls.append(f"f={f}: correction after consumer rejected")
        size = 1 << (3*f)
        total_columns += len(words)*size
        total_coefficients += len(words)*size*size
        fixtures.append({"f": f, "programs": len(words), "columns_per_program": size,
                         "stale_target_coefficient_mismatches": mismatches})
    print(json.dumps({"status": "PASS_PHASE_BANK_INTERVENING_WORK_SOURCE_AUDIT",
                      "source_sha256": SOURCE_SHA256, "fixtures": fixtures,
                      "fixture_columns": total_columns, "fixture_coefficients": total_coefficients,
                      "failure_controls": controls,
                      "scope": "Exact finite fixtures support PROOF.md; no native cost or full multiplication proof."},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
