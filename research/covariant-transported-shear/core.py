"""Read-only transported shears for the pinned covariant native action.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
The source extractor, helper basis and native binding remain PR2742's work.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 704


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def source_module(name, path, authenticated_bytes):
    need(name not in sys.modules, "preloaded predecessor module: " + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    # Execute the bytes checked above, not a potentially timestamp-valid pyc.
    # Retain predecessor assertions even when this verifier runs under -O.
    exec(compile(authenticated_bytes, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


@lru_cache(None)
def load():
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            need(sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                 "changed input: " + item["path"])
    manifest = json.loads((HERE / "VENDOR.json").read_text())
    vendor = HERE / "vendor/pr2742"
    authenticated = {}
    for name, item in manifest["files"].items():
        payload = (vendor / name).read_bytes()
        need(sha256(payload).hexdigest() == item["sha256"],
             "changed predecessor: " + name)
        need(sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest() == item["git_blob"],
             "predecessor Git blob: " + name)
        authenticated[name] = payload
    modules = {}
    for name in ("source", "circuit", "algebra", "native_check"):
        module = source_module(name, vendor / (name + ".py"), authenticated[name + ".py"])
        if name == "source":
            module.ROOT = ROOT
        modules[name] = module
    @lru_cache(None)
    def native_import(name):
        path = ROOT / "research/involutive-walsh-lift" / name
        payload = path.read_bytes()
        need(sha256(payload).hexdigest() == modules["native_check"].MODULES[name],
             "changed native execution source")
        return source_module("transported_" + path.stem, path, payload)
    # Adapter only: every retained predecessor file remains byte-identical.
    modules["native_check"].imported = native_import
    data = modules["source"].load()
    parts = modules["circuit"].construct(data)
    return modules, data, parts


def permutation_power(permutation, phase):
    result = list(range(len(permutation)))
    for _ in range(phase % 4):
        result = [result[i] for i in permutation]
    return result


def signed_power(data, phase):
    result = [(i, 1) for i in range(112)]
    for _ in range(phase % 4):
        result = [(data["permutation"][i][0], sign * data["permutation"][i][1])
                  for i, sign in result]
    return result


def monomials(fields, phase):
    return [("z", i, phase % 4) for i in fields] if phase % 4 else []


def relocate(word, offset):
    return [(e[0], e[1] + offset, e[2] + offset, e[3]) if e[0] == "add"
            else (e[0], e[1] + offset, e[2]) for e in word]


def cycle(phase):
    modules, _, _ = load()
    pivots = modules["source"].PIVOTS
    order = permutation_power(modules["source"].Q, phase)
    return modules["circuit"].permute(pivots, [pivots[i] for i in order])


def helper_action(phase):
    if phase % 4 == 0:
        return []
    modules, _, parts = load()
    return (parts["chart"] + cycle(phase)
            + monomials(modules["source"].PIVOTS, phase)
            + modules["circuit"].invert(parts["chart"]))


def action(phase):
    if phase % 4 == 0:
        return []
    modules, data, _ = load()
    circuit = modules["circuit"]
    wanted = [None] * 112
    permutation = signed_power(data, phase)
    for j, (i, _) in enumerate(permutation):
        wanted[i] = j
    word = circuit.permute(tuple(range(112)), wanted)
    for _, (i, sign) in enumerate(permutation):
        if sign < 0:
            word += circuit.scale(i, F(-1))
    return word + monomials(range(112), phase) + helper_action(phase)


def data_shear(phase, sign):
    _, data, _ = load()
    word = []
    for j, (i, coefficient) in enumerate(signed_power(data, phase)):
        word += (monomials([N + i], -phase)
                 + [("add", N + i, j, sign * coefficient)]
                 + monomials([N + i], phase))
    return word


def compile_shear(phase, sign=1, mode="new"):
    need(type(phase) is int and 0 <= phase < 4, "phase must be 0..3")
    need(type(sign) is int and sign in (-1, 1), "sign must be +/-1")
    need(mode in ("new", "full", "factored"), "closed compiler mode")
    if phase == 0:
        return [("add", N + j, j, sign) for j in range(N)]
    modules, data, parts = load()
    circuit = modules["circuit"]
    pivots = modules["source"].PIVOTS
    if mode == "full":
        return action(phase) + compile_shear(0, sign) + action(-phase)
    word = data_shear(phase, sign)
    unchanged = [("add", N + j, j, sign) for j in range(112, N) if j not in pivots]
    if mode == "factored":
        return (word + helper_action(phase)
                + [("add", N + j, j, sign) for j in pivots]
                + helper_action(-phase) + unchanged)
    # Conjugate the accumulator, not its read-only source. The two C loads
    # replace four loads in the helper-only unphase/shear/rephase sandwich.
    word += (relocate(parts["basis"], N) + relocate(cycle(-phase), N)
             + monomials([N + j for j in pivots], -phase))
    for i, target in enumerate(pivots):
        for source, value in sorted(data["reader"][i].items()):
            if source < 224:
                continue
            need(value.denominator == 1, "integral B/C injection")
            word += [("add", N + target, source, sign * (1 if value > 0 else -1))] * abs(value.numerator)
    word += relocate(cycle(phase), N) + monomials([N + j for j in pivots], phase)
    for e in circuit.invert(parts["load"]):
        word.append(("add", N + e[1], e[2], sign * e[3]))
    word += relocate(circuit.invert(parts["basis"]), N)
    return word + unchanged


def replay(word, initial=None, metrics=False, readonly=False):
    modules, _, _ = load()
    algebra = modules["algebra"]
    rows = algebra.identity(2 * N) if initial is None else [row.copy() for row in initial]
    peak = F(1)
    denominator = 1
    for event in word:
        opcode, target = event[:2]
        need(type(target) is int and 0 <= target < 2 * N, "field destination")
        if readonly:
            need(target >= N, "write into read-only source")
        if opcode == "add":
            source, sign = event[2:]
            need(type(source) is int and 0 <= source < 2 * N and source != target,
                 "distinct valid ADD source")
            need(type(sign) is int and sign in (-1, 1), "unit signed ADD")
            rows[target] = algebra.add(rows[target], rows[source], F(sign))
        elif opcode == "scale":
            value = F(event[2])
            need(value in (F(-1), F(2), F(1, 2)), "dyadic scale alphabet")
            rows[target] = {j: tuple(value * x for x in p) for j, p in rows[target].items()}
        else:
            need(opcode == "z" and type(event[2]) is int and 1 <= event[2] <= 3,
                 "native monomial power")
            rows[target] = {j: algebra.shift(p, event[2]) for j, p in rows[target].items()}
        if metrics:
            values = [x for p in rows[target].values() for x in p]
            peak = max(peak, sum(map(abs, values)))
            denominator = max(denominator, max((x.denominator for x in values), default=1))
    return rows, {"formal_row_l1": str(peak), "max_denominator": denominator}


def invoice(word):
    counts = Counter(e[0] for e in word)
    need(set(counts) <= {"add", "scale", "z"}, "all invoice opcodes priced")
    source_reads = sum(e[0] == "add" and e[2] < N for e in word)
    writes_to_source = sum(e[1] < N for e in word)
    scalar = counts["add"] + counts["scale"]
    return {
        "events": len(word), "unit_ADD": counts["add"], "scales": counts["scale"],
        "scalar_operations": scalar, "payload_monomials": counts["z"],
        "real_scalar_primitives": 8 * counts["add"] + 2 * counts["scale"],
        "logical_payload_reads_per_site": 2 * counts["add"] + counts["scale"] + counts["z"],
        "logical_payload_writes_per_site": len(word),
        "source_ADD_reads_per_site": source_reads,
        "source_writing_events": writes_to_source,
        "positive_rank_children": 0, "extra_algebraic_fields": 0, "CLEAR": 0,
    }


def encoded(rows):
    return [{str(j): [str(x) for x in p] for j, p in sorted(row.items())} for row in rows]
