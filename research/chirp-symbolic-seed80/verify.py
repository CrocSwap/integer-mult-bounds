#!/usr/bin/env python3
"""Independent polynomial certificates for the pinned PR479 transition.

Only the implementation under examination is imported. No predecessor checker,
direct-phase oracle, symbolic algebra package, or floating arithmetic is used.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import sys
import types

HERE = Path(__file__).resolve().parent
BASE = "47481c89fd30a43f8f882eb4b391e89c29273fd0"
HEAD = "40dd01058439cdffae3e3b41c4fe52edaccf5f91"
SEED = 80


class Failure(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise Failure(message)


class Modulus:
    """An arbitrary positive Q: reduction is invisible in Z[variables]/(Q)."""
    def __init__(self):
        self.reductions = 0
        self.guards = {}
        self.used_guards = []


class Poly:
    """Sparse integer polynomials; a monomial is a sorted tuple of names."""
    context = None

    def __init__(self, terms=None):
        self.terms = {tuple(k): v for k, v in (terms or {}).items() if v}

    @staticmethod
    def cast(value):
        if isinstance(value, Poly):
            return value
        if type(value) is int:
            return Poly({(): value})
        raise Failure("unsupported symbolic operand: " + type(value).__name__)

    @staticmethod
    def var(name):
        return Poly({(name,): 1})

    def __add__(self, other):
        terms = dict(self.terms)
        for key, value in self.cast(other).terms.items():
            terms[key] = terms.get(key, 0) + value
        return Poly(terms)

    __radd__ = __add__

    def __neg__(self):
        return Poly({key: -value for key, value in self.terms.items()})

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        terms = {}
        for a, x in self.terms.items():
            for b, y in self.cast(other).terms.items():
                key = tuple(sorted(a + b))
                terms[key] = terms.get(key, 0) + x*y
        return Poly(terms)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        require(type(exponent) is int and exponent >= 0, "invalid exponent")
        result = Poly.cast(1)
        for _ in range(exponent):
            result = result*self
        return result

    def __mod__(self, modulus):
        require(modulus is self.context, "changed symbolic modulus")
        modulus.reductions += 1
        return self

    def __lt__(self, other):
        difference = self - other
        if not difference.terms:
            return False  # Wrapped branch: T < T.
        key = difference.key()
        require(key in self.context.guards, "unproved branch guard")
        self.context.used_guards.append(difference.record())
        return self.context.guards[key]

    def bit_length(self):
        # Instrumentation only. Concrete checks separately validate this metric.
        return 0

    def key(self):
        return tuple(sorted(self.terms.items()))

    def record(self):
        return [{"monomial": list(key), "coefficient": value}
                for key, value in sorted(self.terms.items())]

    def evaluate(self, values):
        return sum(coefficient*math.prod(values[name] for name in monomial)
                   for monomial, coefficient in self.terms.items())


def source_bytes(root=HERE):
    pins = json.loads((root / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE and pins["source_head"] == HEAD,
            "unexpected source/base commit")
    require(pins["assignment_seed"] == SEED and pins["source_pr"] == 479,
            "unexpected assignment")
    expected_names = {"vendor/" + name for name in
                      ("stream.py", "PROOF.md", "NOTICE.md", "LICENSE", "SOURCE.json")}
    require(set(pins["files"]) == expected_names, "incomplete source closure")
    for path, pin in pins["files"].items():
        data = (root / path).read_bytes()
        require(pin["commit"] == HEAD, "inconsistent dependency head")
        filename = Path(path).name
        source_path = "research/streamed-chirp-phases/" + (
            "code/stream.py" if filename == "stream.py" else filename)
        require(pin["source_path"] == source_path, "unexpected source path")
        require(hashlib.sha256(data).hexdigest() == pin["sha256"],
                "source SHA-256 mismatch: " + path)
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == pin["git_blob"],
                "source Git blob mismatch: " + path)
    return (root / "vendor/stream.py").read_text(), pins


def implementation(source):
    # Register the transient module because dataclasses resolves its namespace.
    name = "_seed80_pinned_target"
    module = types.ModuleType(name)
    sys.modules[name] = module
    try:
        exec(compile(source, str(HERE / "vendor/stream.py"), "exec"), module.__dict__)
    finally:
        del sys.modules[name]
    return module.ChirpStream


def symbolic_case(target, dimensions, suffix):
    """suffix is the number of trailing axes at their final index."""
    q = Modulus()
    Poly.context = q
    stream = target(8, [8]*dimensions, [1]*dimensions)
    stream.modulus = q
    expected = []
    phase = Poly.cast(0)
    next_phase = Poly.cast(0)
    increment = dimensions-suffix-1
    for axis, x in enumerate(stream.axes):
        a, t = Poly.var("A"+str(axis)), Poly.var("T"+str(axis))
        j = t-1 if axis > increment else Poly.var("J"+str(axis))
        x.radix, x.coefficient, x.index = t, a, j
        x.value, x.difference = a*j*j, a*(2*j+1)
        phase += x.value
        if axis > increment:
            k = Poly.cast(0)
        elif axis == increment:
            k = j+1
            q.guards[(j+1-t).key()] = True
        else:
            k = j
        expected.append((t, a, k, a*k*k, a*(2*k+1)))
        next_phase += a*k*k
    stream.phase = phase
    continued = stream.advance()
    differences = []
    for i, (axis, values) in enumerate(zip(stream.axes, expected)):
        for field, expected_value in zip(
                ("radix", "coefficient", "index", "value", "difference"), values):
            delta = Poly.cast(getattr(axis, field))-expected_value
            differences.append((str(i)+"."+field, delta))
    differences.append(("phase", Poly.cast(stream.phase)-next_phase))
    failures = {label: delta.record() for label, delta in differences if delta.terms}
    require(not failures, "symbolic d="+str(dimensions)+" suffix="+str(suffix)+
            " defects="+json.dumps(failures, sort_keys=True))
    require(continued is (suffix < dimensions), "wrong continuation flag")
    require(len(q.used_guards) == int(suffix < dimensions), "wrong guarded path")
    visits = min(suffix+1, dimensions)
    require((stream.visits, stream.wraps, stream.rewinds) ==
            (visits, suffix, max(0, visits-1)), "wrong transition accounting")
    return {
        "dimensions": dimensions, "wrapped_suffix": suffix,
        "regular_guard": q.used_guards,
        "phase_before": phase.record(), "phase_expected": next_phase.record(),
        "zero_coefficient_obligations": len(differences),
        "modular_reductions": q.reductions, "continues": continued,
        "axis_visits": visits, "wraps": suffix,
    }


def symbolic_checks(target):
    return [symbolic_case(target, d, suffix)
            for d in range(1, 7) for suffix in range(d+1)]


def rank_of(coordinates, radices):
    rank = 0
    for j, t in zip(coordinates, radices):
        rank = rank*t+j
    return rank


def unrank(rank, radices):
    result = []
    for t in reversed(radices):
        rank, digit = divmod(rank, t)
        result.append(digit)
    require(rank == 0, "rank exceeds box")
    return tuple(reversed(result))


def closed_state(r, radices, sources, coordinates):
    """Original integer quadratic formula, with no incremental recurrence."""
    q = 2*r
    axes = [(t, (-s*(r//t)) % q, j,
             (-s*j*j*(r//t)) % q, (-s*(2*j+1)*(r//t)) % q)
            for t, s, j in zip(radices, sources, coordinates)]
    phase = (-sum(s*j*j*(r//t)
                  for t, s, j in zip(radices, sources, coordinates))) % q
    return {"modulus": q, "phase": phase, "axes": axes}


def snapshot(stream):
    return {"modulus": stream.modulus, "phase": stream.phase,
            "axes": [(x.radix, x.coefficient, x.index, x.value, x.difference)
                     for x in stream.axes]}


def small_boxes():
    rng = random.Random(SEED)
    yield 2, (), ()  # Accepted zero-axis implementation edge, not a padded box.
    for r in (2, 4, 8):
        options = sorted({t for t in (r//2, r) if t >= 2})
        for d in range(1, 4):
            for radices in itertools.product(options, repeat=d):
                if r <= 4:
                    sources = itertools.product(*(range(1, t) for t in radices))
                else:
                    sources = sorted({tuple(1 for _ in radices),
                                      tuple(t-1 for t in radices),
                                      tuple(rng.randrange(1, t) for t in radices)})
                for source in sources:
                    yield r, radices, source


def transition(target, r, radices, sources, coordinates):
    stream = target(r, radices, sources)
    initial = closed_state(r, radices, sources, (0,)*len(radices))
    if snapshot(stream) != initial:
        return {"stage": "initialization", "r": r, "radices": radices,
                "sources": sources, "expected": initial, "actual": snapshot(stream)}
    before = closed_state(r, radices, sources, coordinates)
    stream.phase = before["phase"]
    for axis, values in zip(stream.axes, before["axes"]):
        (axis.radix, axis.coefficient, axis.index, axis.value, axis.difference) = values
    total = math.prod(radices)
    rank = rank_of(coordinates, radices)
    expected_coordinates = unrank((rank+1) % total, radices)
    expected = closed_state(r, radices, sources, expected_coordinates)
    suffix = 0
    for j, t in reversed(list(zip(coordinates, radices))):
        if j != t-1:
            break
        suffix += 1
    visits = min(suffix+1, len(radices))
    flag = stream.advance()
    metrics = (stream.visits, stream.wraps, stream.rewinds)
    want_metrics = (visits, suffix, max(0, visits-1))
    if snapshot(stream) != expected or flag is not (rank+1 < total) or metrics != want_metrics:
        return {"stage": "advance", "r": r, "radices": radices,
                "sources": sources, "coordinates": coordinates,
                "expected_coordinates": expected_coordinates,
                "before": before, "expected": expected, "actual": snapshot(stream),
                "continues": flag, "expected_continues": rank+1 < total,
                "metrics": metrics, "expected_metrics": want_metrics}
    require(stream.max_residue_bits <= (2*r-1).bit_length(), "residue width overflow")
    return None


def finite_checks(target):
    digest = hashlib.sha256()
    boxes = transitions = final_rollovers = 0
    total_visits = 0
    for r, radices, sources in small_boxes():
        boxes += 1
        actual_visits = 0
        for coordinates in itertools.product(*(range(t) for t in radices)):
            defect = transition(target, r, radices, sources, coordinates)
            require(defect is None, "finite defect: "+json.dumps(defect, sort_keys=True))
            transitions += 1
            suffix = 0
            for j, t in reversed(list(zip(coordinates, radices))):
                if j != t-1:
                    break
                suffix += 1
            actual_visits += min(suffix+1, len(radices))
            digest.update(json.dumps([r, radices, sources, coordinates],
                                     separators=(",", ":")).encode()+b"\n")
        # Independent closed-form count; includes the last full rollover.
        expected_visits = sum(math.prod(radices[:i+1]) for i in range(len(radices)))
        require(actual_visits == expected_visits, "period visit total mismatch")
        require(actual_visits < 2*math.prod(radices), "period visit bound failed")
        total_visits += actual_visits
        final_rollovers += 1
    wide = 0
    r = 1 << SEED
    for d in (1, 2, 5, 9):
        radices = tuple(r//2 if i % 2 else r for i in range(d))
        sources = tuple((SEED+17*i) % (t-1)+1 for i, t in enumerate(radices))
        for suffix in range(d+1):
            coordinates = tuple(t-1 if i >= d-suffix else (SEED+3*i) % (t-1)
                                for i, t in enumerate(radices))
            defect = transition(target, r, radices, sources, coordinates)
            require(defect is None, "wide transition defect: "+json.dumps(defect))
            wide += 1
    return {"small_boxes": boxes, "exact_state_transitions": transitions,
            "complete_rollovers": final_rollovers, "period_axis_visits": total_visits,
            "transition_domain_sha256": digest.hexdigest(), "wide_transitions": wide,
            "wide_r": str(r), "wide_dimensions": [1, 2, 5, 9]}


MUTATIONS = {
    "wrong_second_difference": ("else 2*x.coefficient", "else x.coefficient"),
    "omitted_carry_subtraction": ("self.phase-x.value", "self.phase"),
    "zero_wrap_difference": ("else x.coefficient\n", "else 0\n"),
    "stopped_carry": ("if mutation == 'stopped carry':", "if True:"),
    "positive_initial_phase": ("a = (-s*(r//t))", "a = (s*(r//t))"),
    "half_modulus": ("self.r, self.modulus = r, 2*r", "self.r, self.modulus = r, r"),
    "value_uses_next_difference": ("x.value+x.difference", "x.value+x.difference+2*x.coefficient"),
    "phase_uses_coefficient": ("self.phase+x.difference", "self.phase+x.coefficient"),
    "nonzero_wrap_index": ("x.index = x.value = 0", "x.index = 1\n            x.value = 0"),
    "terminal_continues": ("        return False\n", "        return True\n"),
    "wrong_axis_order": ("i = len(self.axes)-1", "i = 0"),
    "unchanged_value": ("x.value = (x.value+x.difference)", "x.value = (x.value)"),
    "zero_initial_difference": ("Axis(t, a, difference=a)", "Axis(t, a, difference=0)"),
    "unreduced_phase": ("self.phase = (self.phase+x.difference) % self.modulus",
                        "self.phase = self.phase+x.difference"),
    "unreduced_value": ("x.value = (x.value+x.difference) % self.modulus",
                        "x.value = x.value+x.difference"),
    "unreduced_difference": ("else 2*x.coefficient)) % self.modulus",
                             "else 2*x.coefficient))"),
}


def mutate(source, name):
    old, new = MUTATIONS[name]
    require(source.count(old) == 1, "mutation anchor not unique: "+name)
    return source.replace(old, new)


def controls(source):
    result = []
    for name in MUTATIONS:
        target = implementation(mutate(source, name))
        symbolic_failure = None
        try:
            symbolic_checks(target)
        except Failure as exc:
            symbolic_failure = str(exc)
        witness = None
        for r, radices, sources in small_boxes():
            if not radices:
                continue  # Controls report mathematical defects, not empty-list errors.
            for coordinates in itertools.product(*(range(t) for t in radices)):
                witness = transition(target, r, radices, sources, coordinates)
                if witness is not None:
                    break
            if witness is not None:
                break
        require(witness is not None, "mutation had no exact counterexample: "+name)
        result.append({"mutation": name, "symbolic_rejection": symbolic_failure,
                       "concrete_witness": witness})
    return result


def equivalent_controls(source):
    """Accept algebraically equivalent target rewrites, not just exact text."""
    variants = {
        "closed_form_next_value": (
            "x.value = (x.value+x.difference) % self.modulus",
            "x.value = (x.coefficient*(x.index+1)**2) % self.modulus"),
        "commuted_phase_addition": (
            "self.phase+x.difference", "x.difference+self.phase"),
    }
    rows = []
    for name, (old, new) in variants.items():
        require(source.count(old) == 1, "positive anchor not unique")
        target = implementation(source.replace(old, new))
        patterns = symbolic_checks(target)
        finite = finite_checks(target)
        rows.append({"rewrite": name, "symbolic_patterns": len(patterns),
                     "exact_state_transitions": finite["exact_state_transitions"],
                     "wide_transitions": finite["wide_transitions"]})
    return rows


def certificate(root=HERE):
    source, pins = source_bytes(root)
    target = implementation(source)
    symbolic = symbolic_checks(target)
    return {
        "status": "PASS_CHIRP_SYMBOLIC_INVARIANTS", "base_commit": BASE,
        "assignment_seed": SEED, "source_head": HEAD,
        "source_sha256": {p: v["sha256"] for p, v in pins["files"].items()},
        "symbolic": symbolic,
        "zero_coefficient_obligations": sum(x["zero_coefficient_obligations"] for x in symbolic),
        "finite": finite_checks(target), "negative_controls": controls(source),
        "positive_controls": equivalent_controls(source),
        "scope": "Exact source-bound symbolic polynomial identities and finite state transitions; "
                 "not a Lean proof, full tape-cost audit, numerical exponential replay, "
                 "supplier certificate, or new kappa.",
    }


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True)+"\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    result = certificate()
    payload = canonical(result)
    if args.write:
        with args.write.open("x") as handle:
            handle.write(payload)
    else:
        require(payload == (HERE / "EXPECTED.json").read_text(), "expected receipt mismatch")
    print(result["status"], "symbolic="+str(len(result["symbolic"])),
          "identities="+str(result["zero_coefficient_obligations"]),
          "transitions="+str(result["finite"]["exact_state_transitions"]),
          "controls="+str(len(result["negative_controls"])))


if __name__ == "__main__":
    try:
        main()
    except (Failure, OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_CHIRP_SYMBOLIC_INVARIANTS:", exc, file=sys.stderr)
        sys.exit(1)
