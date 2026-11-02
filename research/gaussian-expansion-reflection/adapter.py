"""Exact reflection reuse for the pinned periodic Gaussian expansion.

Produced by Nick Petalas. Apache-2.0.
"""
import ast
from contextlib import contextmanager, redirect_stdout
from fractions import Fraction
from functools import partial
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = ROOT / "research/certified-gaussian-recovery"
NAMES = ("intervals", "gaussian", "pipeline")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    require(len(rows) == 12, "exact twelve-input closure")
    captured = {}
    for row in rows:
        path = ROOT / row["path"]
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source drift: " + row["path"])
        captured[row["path"]] = data
    return captured


def reflected_expansion(module, counts, s, t, alpha, bits, radius):
    """Return the same integer interval endpoints as the complete row loop."""
    require(2 <= s < t and alpha >= 2 and bits > 0 and radius > 0,
            "positive expansion geometry")
    out = module.zeros(t, s, bits)
    pi = module.pi_interval(bits)
    for k in range(t // 2 + 1):
        center = Fraction(s * k, t)
        left = center.numerator // center.denominator - radius
        right = module.ceildiv(center.numerator, center.denominator) + radius
        for j in range(left, right + 1):
            x = pi * ((Fraction(j) - center) ** 2 / alpha ** 2)
            out[k][j % s] += module.exp_negative(x) / (2 * alpha)
            counts["expansion_terms"] += 1
        out[k] = [module.Interval(x.lo, x.hi + 1, bits) for x in out[k]]
        counts["computed_rows"] += 1
    for k in range(t // 2 + 1, t):
        out[k] = [out[t - k][(-j) % s] for j in range(s)]
        counts["reflected_rows"] += 1
    counts["constructors"] += 1
    return out


def replace_expansion(tree):
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "GaussianLine"]
    require(len(classes) == 1, "one pinned GaussianLine")
    inits = [n for n in classes[0].body if isinstance(n, ast.FunctionDef)
             and n.name == "__init__"]
    require(len(inits) == 1, "one pinned constructor")
    body = inits[0].body
    locations = [i for i, n in enumerate(body) if isinstance(n, ast.Assign)
                 and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                 and n.targets[0].id == "expansion"]
    require(len(locations) == 1, "one expansion allocation")
    index = locations[0]
    require(isinstance(body[index + 1], ast.For), "adjacent complete row loop")
    following = body[index + 2]
    require(isinstance(following, ast.Assign)
            and ast.unparse(following.targets[0]) == "self.expansion",
            "unchanged expansion consumer")
    replacement = ast.parse(
        "expansion = _reflected_expansion(s, t, alpha, bits, radius)").body[0]
    body[index:index + 2] = [ast.copy_location(replacement, body[index])]
    return ast.fix_missing_locations(tree)


def load_module(name, data, reflected, counts):
    module = ModuleType(name)
    module.__file__ = str(SOURCE / (name + ".py"))
    sys.modules[name] = module
    tree = ast.parse(data, filename=module.__file__)
    if name == "gaussian" and reflected:
        tree = replace_expansion(tree)
        module._reflected_expansion = partial(reflected_expansion, module, counts)
    exec(compile(tree, module.__file__, "exec"), module.__dict__)
    return module


@contextmanager
def runtime(mode):
    require(mode in ("baseline", "reflected"), "known execution mode")
    captured = authenticated_sources()
    saved = {name: sys.modules.get(name) for name in NAMES}
    old_path, old_argv = sys.path[:], sys.argv[:]
    counts = dict.fromkeys(("exp_negative_calls", "expansion_terms",
                           "computed_rows", "reflected_rows", "constructors"), 0)
    try:
        modules = {}
        for name in NAMES:
            path = "research/certified-gaussian-recovery/" + name + ".py"
            modules[name] = load_module(name, captured[path], mode == "reflected", counts)
        original = modules["gaussian"].exp_negative

        def counted_exponential(value):
            counts["exp_negative_calls"] += 1
            return original(value)

        modules["gaussian"].exp_negative = counted_exponential
        yield modules, captured, counts
    finally:
        sys.path[:] = old_path
        sys.argv[:] = old_argv
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def complete_replay(mode):
    with runtime(mode) as (_, captured, counts):
        path = "research/certified-gaussian-recovery/verify.py"
        verifier = ModuleType("retained_gaussian_verifier")
        verifier.__file__ = str(ROOT / path)
        exec(compile(captured[path], verifier.__file__, "exec"), verifier.__dict__)
        sys.argv[:] = [verifier.__file__]
        output = StringIO()
        with redirect_stdout(output):
            verifier.main()
        require(output.getvalue().startswith("PASS_CERTIFIED_GAUSSIAN_RECOVERY "),
                "complete retained replay succeeded")
        return output.getvalue(), dict(counts)
