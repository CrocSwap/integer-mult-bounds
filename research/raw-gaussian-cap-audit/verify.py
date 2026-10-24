"""Uniform raw-cap audit: independent inequalities around actual source allocation."""
import ast
import copy
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "research/rational-unitary-fft"
INTERVALS = "research/certified-gaussian-recovery/intervals.py"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def ceilq(q):
    return -(-q.numerator // q.denominator)


def logceil(q):
    q = Q(q)
    out = q.numerator.bit_length()-q.denominator.bit_length()
    return out + int(Q(2)**out < q)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def source_modules():
    exact = load("exact", DIRECTORY / "exact.py")
    gaussian = ModuleType("gaussian")
    sys.modules["gaussian"] = gaussian
    # Unchanged source scalar conditioning prefix; stop before coefficient/circuit preparation.
    tree = ast.parse((DIRECTORY / "gaussian.py").read_bytes())
    names = {"rational", "load_intervals", "Specification"}
    selected = [copy.deepcopy(node) for node in tree.body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Gaussian")
    init = next(copy.deepcopy(node) for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    stop = next(i for i, node in enumerate(init.body) if isinstance(node, ast.Assign)
                and any(ast.unparse(target) == "self.error_bits" for target in node.targets))
    init.body = init.body[:stop]
    exp = next(copy.deepcopy(node) for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "exponential")
    selected.append(ast.ClassDef(name="Gaussian", bases=[], keywords=[], body=[init, exp], decorator_list=[]))
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    from dataclasses import dataclass
    from hashlib import sha256
    gaussian.__dict__.update(Q=Q, need=exact.need, sys=sys, ModuleType=ModuleType,
                             dataclass=dataclass, sha256=sha256, INTERVALS=INTERVALS)
    exec(compile(module, "<retained conditioning prefix>", "exec", optimize=0), gaussian.__dict__)
    reference = load("audited_reference", DIRECTORY / "gaussian_reference.py")
    raw_tree = ast.parse((DIRECTORY / "raw_gaussian.py").read_bytes())
    raw_cls = next(node for node in raw_tree.body if isinstance(node, ast.ClassDef) and node.name == "RawGaussian")
    raw_init = next(copy.deepcopy(node) for node in raw_cls.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    boundary = next(i for i, node in enumerate(raw_init.body) if isinstance(node, ast.Expr)
                    and isinstance(node.value, ast.Call)
                    and any(isinstance(arg, ast.Constant) and arg.value == "common reference accuracy at this raw inverse caller"
                            for arg in node.value.args))
    raw_init.body = raw_init.body[:boundary+1]
    probe = ast.Module(body=[ast.ClassDef(name="Probe", bases=[], keywords=[], body=[raw_init], decorator_list=[])], type_ignores=[])
    ast.fix_missing_locations(probe)
    namespace = dict(Q=Q, need=exact.need, rational=gaussian.rational,
                     Gaussian=gaussian.Gaussian, ceiling=reference.ceiling)
    exec(compile(probe, "<retained raw admission prefix>", "exec", optimize=0), namespace)
    return reference, namespace["Probe"], gaussian.Gaussian


def rejection(call, fragment):
    try:
        call()
    except (ValueError, AssertionError, SystemExit) as exc:
        need(fragment in str(exc), "wrong failure control: " + str(exc))
    else:
        raise ValueError("unrejected mutation " + fragment)


def tail_oracle(first, step, scale, width_error):
    # pi>3 and e>2 imply exp(-pi*x) < 2^(-floor(3*x)).
    # Integer floor must be taken before negation, retaining a safe upper bound.
    upper_first = Q(2)**(-((3*first).numerator // (3*first).denominator))
    upper_ratio = Q(2)**(-((3*step).numerator // (3*step).denominator))
    need(upper_ratio + width_error < 1, "independent tail denominator")
    return scale*(upper_first+width_error)/(1-upper_ratio-width_error)


def check_reference(reference, raw, Probe, Gaussian, args):
    size, excess, alpha, cap, radius, target = args
    ref = reference.Reference.for_cap(raw, *args)
    alloc = ref.allocation
    theta, rho = Q(excess, size), Q(size+excess, size)
    exponent = 1+alpha**2*theta*(cap**2+cap+1)
    gauge = alpha*2**ceilq(8*exponent)
    qbar = Gaussian(raw, cap, 1/(alpha**2*rho), 0, 1, 1).qbar
    envelope = gauge**2*2*qbar
    e = target+logceil(8*(radius+1)*envelope**2)
    need(alloc == dict(cap=cap, radius=str(Q(radius)), target_bits=target,
                      gauge_exponent_bound=str(exponent), gauge_bound=str(gauge),
                      normalized_bound=str(2*qbar), inverse_bound=str(envelope), error_bits=e),
         "independent allocation arithmetic")
    w, W, be = ref.spec.source_halfwidth, ref.spec.target_halfwidth, ref.spec.entry_bits
    a = alpha**2*rho**2
    J = 2*(be+ceilq(8*a)+16)+32
    sigma = 512*J*J*Q(1, 1<<J)
    need(sigma <= Q(1, 1<<(be+23)), "tail interval width margin")
    narrow = tail_oracle(Q(alpha**2*w*(w+1)), Q(2*alpha**2*(w+1)), Q(2), sigma)
    broad = tail_oracle((Q(W)+Q(1,2))**2/a, Q(2*(W+1))/a, Q(2,alpha), sigma)
    threshold = Q(1,1<<e)
    need(ref.narrow_tail <= narrow < threshold/4 and ref.broad_tail <= broad < threshold/4,
         "independent global tail upper bounds")
    for count in (2*w+1, 2*W+1):
        need(count*Q(1,1<<be) <= threshold/8, "coefficient row budget")
    need(max(ref.errors.values()) < 3*threshold/8, "uniform residual margin")

    # At most eight positions per size, selected from cell beginnings/ends/midpoints.
    cells = []
    start = 0
    for j in range(1, size+1):
        if j == size or ref.phases[j] != ref.phases[start]:
            cells.append((start, j)); start = j
    probes = []
    for n in (1,2,4,8):
        if n > cap: continue
        starts = set()
        for lo, hi in cells:
            if hi-lo >= n:
                starts.update((lo, hi-n, (lo+hi-n)//2))
        for start in sorted(starts)[:8]:
            for kind in ("narrow", "broad"):
                local = Probe(raw, ref, kind, start, n, radius, target)
                need(local.gauge_exponent_bound <= exponent, "cap-wide exponent dominance")
                need(local.gauge_bound <= gauge and local.raw_inverse_bound <= envelope,
                     "same-reference local inverse admission")
                need(local.reference_error <= Q(1,1<<target)/(8*(radius+1)*local.raw_inverse_bound**2),
                     "caller reference threshold")
                # Recompute exact centered factor bounds without reading the source factors.
                r = Q(n-1,2)
                majorant = max(alpha**2*theta*r*r,
                               Q(1,4*alpha**2*rho*rho)+theta/alpha**2*(r*r+r),
                               theta/alpha**2*(r*r+2*r))
                need(local.gauge_exponent_bound <= majorant <= exponent, "independent raw gauge majorant")
                probes.append((kind,start,n))
    need(probes, "nonempty legal block coverage")
    lo, hi = next((lo, hi) for lo, hi in cells if hi-lo >= 2)
    i, j = lo, lo+1
    entry = ref.entry("narrow", ref.selected[i], ref.selected[j])
    need(entry.kind == "shared-weight-ratio", "actual within-cell ratio route")
    need(entry.value == ref.weights[i]["value"]*ref.kernel[1][0]/ref.weights[j]["value"],
         "one shared weight/kernel reference")
    for k in (i,j):
        receipt = ref.weights[k]
        need(receipt["value"] > 0 and receipt["relative_error"] <= Q(1,1<<(be+6)),
             "positive relative weight margin")
    factor = alpha**2*((rho+ref.betas[i])**2-ref.betas[j]**2)
    need(factor >= 0, "normalized ideal entry at most one")
    box = ref.exp.decay_box(factor,2*be+128)
    enclosure_error = max(abs(entry.value-Q(box.lo,box.scale)),abs(entry.value-Q(box.hi,box.scale)))
    need(enclosure_error <= Q(1,1<<be), "independently formed raw-entry enclosure")
    return ref, dict(geometry=list(args), blocks=len(probes), error_bits=e,
                     residual_strict_upper_ratio="3/8", shared_weight_entry_checks=1)


def main():
    reference, Probe, Gaussian = source_modules()
    raw = {INTERVALS:(ROOT/INTERVALS).read_bytes()}
    cases = [(97,1,1,8,1,4), (129,3,2,4,2,3), (257,2,1,8,3,5)]
    results, retained = [], []
    for args in cases:
        ref, result = check_reference(reference, raw, Probe, Gaussian, args)
        results.append(result); retained.append(ref)
    # The retained caller must reject the same geometry with an underfunded reference.
    good = retained[0]
    bad = reference.Reference(raw,97,1,1,good.spec.source_halfwidth,good.spec.target_halfwidth,8)
    rejection(lambda: Probe(raw,bad,"narrow",0,8,1,4), "common reference accuracy")
    rejection(lambda: reference.Reference.for_cap(raw,8,1,1,4,1,4), "unique retained periodic lifts")
    rejection(lambda: good.exp.relative(Q(1,16),good.weight_exponent_bound,good.weight_relative_bits,
                                        good.weight_precision-1), "positive weight setup precision")
    # Abstract valid qbar certificates show why the global margin cannot be silently omitted.
    qglobal, qlocal = Q(1), Q(4,3)
    need(qlocal <= 2*qglobal and qlocal > qglobal, "conditioning-certificate inflation control")
    # An inverse perturbation cannot be charged as only a forward operator defect.
    x, defect = Q(1,16), Q(1,512)
    inverse_error = abs(1/(x+defect)-1/x)
    need(inverse_error > defect and inverse_error <= 2*defect/x**2, "inverse sensitivity control")
    print(json.dumps(results, sort_keys=True))
    print("PASS_RAW_GAUSSIAN_CAP_AUDIT geometries=3 controls=5 admission_only no_new_kappa")


if __name__ == "__main__":
    main()
