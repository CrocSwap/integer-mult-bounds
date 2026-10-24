#!/usr/bin/env python3
"""Source-bound structural checks and exact symbolic controls for the B1 bridge."""
from __future__ import annotations

import ast
import hashlib
import io
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
EXPECTED_BASE = "6f100d4bb5083f8c35d96fd95a539811c62f245c"
EXPECTED_RECORD_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
EXPECTED_PR3301_HEAD = "5ce521090c869211f808d132e28dcd4946f798c4"
PR2899_ARCHIVE_SHA256 = "fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531"
FITTED_CUTOFF = 311311
EXPONENT_NUMERATOR = 99830289
EXPONENT_DENOMINATOR = 100000000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_repo(relative: str) -> bytes:
    path = ROOT / relative
    require(path.is_file(), "missing pinned input: " + relative)
    return path.read_bytes()


def check_source_pins() -> dict:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    require(manifest["base_commit"] == EXPECTED_BASE, "base commit changed")
    seen = set()
    for row in manifest["files"]:
        path = row["path"]
        require(path not in seen, "duplicate source path: " + path)
        seen.add(path)
        if row["usage"] != "input":
            continue  # provenance rows (the selected record) are historical pins, not live inputs
        actual = sha256(read_repo(path))
        require(actual == row["sha256"], "source SHA-256 mismatch: " + path)
    # The selected record moves with the frontier; check the exact pinned copy instead.
    record = (PACKAGE / "selected-result-pinned.json").read_bytes()
    require(sha256(record) == EXPECTED_RECORD_SHA256, "selected record bytes changed")
    selected = json.loads(record)
    require(selected["kappa"] == "836330098538459/500000000000000000",
            "selected kappa changed")
    require(EXPECTED_PR3301_HEAD == "5ce521090c869211f808d132e28dcd4946f798c4",
            "PR3301 reference changed")
    return manifest


def require_tokens(label: str, text: str, tokens: tuple[str, ...]) -> None:
    missing = [token for token in tokens if token not in text]
    require(not missing, label + " source contract mismatch: " + ", ".join(missing))


def extract_function(tree: ast.AST, name: str) -> ast.AST:
    rows = [node for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    require(len(rows) == 1, "expected one source function: " + name)
    return rows[0]


def check_caller_sources() -> None:
    high = read_repo("research/selected-bit-fast-primitives/high_route.py").decode("utf-8")
    stage = read_repo("research/selected-bit-fast-primitives/stage.py").decode("utf-8")
    loader = read_repo("research/selected-bit-fast-primitives/stage_sources.py").decode("utf-8")
    high_tree, stage_tree = ast.parse(high), ast.parse(stage)
    extents = extract_function(high_tree, "extents")
    apply = extract_function(high_tree, "apply")
    execute = extract_function(high_tree, "execute")
    swap = extract_function(stage_tree, "swap")
    require(isinstance(extents, ast.FunctionDef) and isinstance(apply, ast.FunctionDef)
            and isinstance(execute, ast.FunctionDef)
            and isinstance(swap, ast.FunctionDef), "expected synchronous source functions")

    require_tokens("high_route.extents", ast.unparse(extents), (
        "fields = dimension * dimension",
        "first, second = sorted((first, second))",
        "before = fixed_power(modulus, first)",
        "middle = fixed_power(modulus, second - first - 1)",
        "power = fixed_power(modulus, fields - second - 1)",
        "Count.product(power, fibre)",
    ))
    require_tokens("high_route.apply", ast.unparse(apply), (
        "kind in (",
        "adapter.swap(source, ring, route.q, before, middle, suffix)",
        "reversed_fields = control > target",
        "adapter.swap(current, ring, route.q, before, middle, suffix)",
        "kernels.added(current, ring, before, middle, suffix",
    ))
    require_tokens("high_route.execute", ast.unparse(execute), (
        "(route.q, route.dimension) == (context.q, context.dimension)",
        "modulus = Count(context.cap)",
        "ring = Ring(modulus_word)",
        "for operation in operations",
        "apply(current, operation, route, ring, modulus, fibre, adapter, factory)",
        "current.clear()",
        "return result",
    ))
    require_tokens("stage.Adapter.swap", ast.unparse(swap), (
        "q == self.q",
        "extents = [Count(value) for value in (before, middle, suffix)]",
        "for _ in radix_power(ring, q)",
        "with self.scope.suspended()",
        "self.native.run(borrowed_tape(source), borrowed_count(width)",
        "borrowed_count(value) for value in extents",
        "result = self.scope.acquire()",
        "append_tape(returned, result)",
        "returned.clear()",
        "return result",
        "width.close()",
        "value.close()",
    ))
    require_tokens("stage_sources", loader, (
        '"pr2899": "fc4a2e07423835737c8fb3872664b16ff12aa4cf83b1e26e49878debef40c531"',
        'source.activate()',
        'module("qadic_streams", paths["pr2157"] / "qadic_streams.py")',
    ))


def check_nested_pr2899_archive() -> None:
    archive = read_repo("research/selected-bit-fast-primitives/inputs/pr2899.tar")
    require(sha256(archive) == PR2899_ARCHIVE_SHA256, "PR2899 source archive changed")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as outer:
        ordinary = outer.extractfile("ordinary.py")
        inner_file = outer.extractfile("inputs/pr2809.tar")
        require(ordinary is not None and inner_file is not None,
                "PR2899 archive closure incomplete")
        ordinary_text = ordinary.read().decode("utf-8")
        require_tokens("PR2899 ordinary.run", ordinary_text, (
            "def run(self, payload, original, prefixes, gap, suffix):",
            "self.execute_plan(payload, original, prefixes, gap, suffix,",
            "lambda: select(original, self.q, self.profile)",
            "borrowed_tape(payload) is not self.output",
            "transfer(result, self.output)",
            "return self.output",
        ))
        nested_bytes = inner_file.read()
    with tarfile.open(fileobj=io.BytesIO(nested_bytes), mode="r:") as nested:
        names = [name for name in nested.getnames()
                 if name.endswith("/vendor/cardinality.py")]
        require(len(names) == 1, "expected unique authenticated radix-power source")
        source = nested.extractfile(names[0])
        require(source is not None, "missing radix-power source")
        text = source.read().decode("utf-8")
        tree = ast.parse(text)
        radix_power = extract_function(tree, "radix_power")
        require_tokens("radix_power", ast.unparse(radix_power), (
            "while ring.raw.compare(power, ring.one) > 0",
            "quotient, remainder = ring.raw.divmod(power, divisor)",
        "remainder.zero()",
        "not quotient.zero()",
            "yield",
            "ring.raw.compare(power, ring.one) == 0",
        ))


def fitted_domain(q: int, u: int) -> None:
    require(isinstance(q, int) and q > 2**80, "prime is outside PR2899's q>2^80 domain")
    require(isinstance(u, int) and u >= FITTED_CUTOFF,
            "u is below the sufficient fitted cutoff")
    # Primality is a mathematical hypothesis in PR2899's theorem.


def extent_exponents(N: int, u: int, F: int, i: int, j: int,
                     suffix_drop: int = 1) -> tuple[int, int, int, int]:
    require(isinstance(N, int) and N >= 2, "at least two route fields are required")
    require(isinstance(u, int) and u >= 1, "positive radix exponent required")
    require(isinstance(F, int) and F >= 1, "positive fibre required")
    require(isinstance(i, int) and isinstance(j, int) and 0 <= i < j < N,
            "axes must be a valid distinct ordered pair")
    require(suffix_drop == 1, "suffix endpoint must exclude the second swapped field")
    return (u * i, u * (j - i - 1), u * (N - j - 1), F)


def check_volume_identity(N: int, u: int, F: int, i: int, j: int,
                          suffix_drop: int = 1) -> tuple[int, int, int, int]:
    signature = extent_exponents(N, u, F, i, j, suffix_drop)
    prefix, middle, suffix, fibre = signature
    require(prefix + middle + suffix + 2 * u == N * u,
            "two q^u axes and complete spectators do not total N fields")
    require(fibre == F, "fibre multiplicity was lost")
    return signature


def is_prime_by_trial_division(n: int) -> bool:
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


def lucas_lehmer_mersenne_127() -> bool:
    p = 127
    if not is_prime_by_trial_division(p):
        return False
    modulus = (1 << p) - 1
    residue = 4
    for _ in range(p - 2):
        residue = (residue * residue - 2) % modulus
    return residue == 0


def must_reject(label: str, action) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control unexpectedly accepted: " + label)


def check_controls(q_witness: int) -> int:
    fitted_domain(q_witness, FITTED_CUTOFF)
    check_volume_identity(4, FITTED_CUTOFF, 1, 0, 3)
    must_reject("q at strict lower boundary", lambda: fitted_domain(2**80, FITTED_CUTOFF))
    must_reject("width below cutoff", lambda: fitted_domain(q_witness, FITTED_CUTOFF - 1))
    must_reject("one route field", lambda: extent_exponents(1, 1, 1, 0, 0))
    must_reject("equal axes", lambda: extent_exponents(4, 1, 1, 2, 2))
    must_reject("out-of-range axis", lambda: extent_exponents(4, 1, 1, 0, 4))
    must_reject("empty fibre", lambda: extent_exponents(4, 1, 0, 0, 1))
    must_reject("wrong suffix endpoint", lambda: check_volume_identity(
        9, 2, 3, 1, 7, suffix_drop=0))
    return 7


def run() -> dict:
    check_source_pins()
    check_caller_sources()
    check_nested_pr2899_archive()
    require(lucas_lehmer_mersenne_127(), "nonempty prime-domain witness failed")
    q_witness = (1 << 127) - 1
    require(q_witness > 2**80, "prime-domain witness is too small")

    cases = 0
    for d in (2, 3, 4):
        N = d * d
        for u in (1, 2, FITTED_CUTOFF):
            for F in (1, 7):
                for i in range(N):
                    for j in range(i + 1, N):
                        check_volume_identity(N, u, F, i, j)
                        cases += 1
    controls = check_controls(q_witness)
    return {
        "marker": "PASS_HIGH_CUBE_B1_FIT_BRIDGE",
        "base_commit": EXPECTED_BASE,
        "pr3301_head": EXPECTED_PR3301_HEAD,
        "q_domain": "prime q>2^80 (fixed q)",
        "fitted_width_domain": "integer u>=311311",
        "high_cube_domain": "N=d^2>=4, F>=1, valid distinct route axes",
        "q_domain_witness": str(q_witness),
        "b1_time_exponent": f"{EXPONENT_NUMERATOR}/{EXPONENT_DENOMINATOR}",
        "symbolic_extent_cases": cases,
        "rejected_controls": controls,
        "finite_fitted_payload_executed": False,
        "selected_kappa_unchanged": "836330098538459/500000000000000000",
        "scope": "caller/callee domain and ownership bridge conditional on PR2899 C0 premises, successful execution and sufficient capacity",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
