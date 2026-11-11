"""Pair-consistent carried-frame model. New work produced by Nick Petalas.

The authenticated construction and frame graph are credited to Cinna Davis;
only their definitions run, without any predecessor scientific replay.
"""
import ast
import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    normalized = json.loads(json.dumps(value))
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    paths = [row for row in manifest["files"] if row["usage"] == "input"]
    need(len(paths) == 8, "Declared input inventory")
    result = {}
    for row in paths:
        payload = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(payload).hexdigest() == row["sha256"], "Input hash")
        result[row["path"]] = payload
    return result


def load_graph(inputs):
    prefix = "research/native-frame-carrying-swaps/"
    data = json.loads(gzip.decompress(inputs[prefix + "SOURCE-WORD.json.gz"]))
    need(data["canonical"]["h"] == 9, "Fixed nine-dimensional source")
    need(len(data["programs"]["forward"]) <= 100000, "Source event bound")
    frame = ModuleType("authenticated_frame_definitions")
    source = inputs["research/carried-warp-frame-intervals/frame_dag.py"]
    exec(compile(source, "authenticated_frame_dag.py", "exec"), frame.__dict__)
    tree = ast.parse(inputs[prefix + "verify.py"])
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name == "construct"]
    need(len(definitions) == 1, "Unique retained constructor")
    canonical = data["canonical"]
    need(len(canonical["frames"]) <= 5000, "Source frame inventory bound")
    masks = [frame.space(vectors) for vectors in canonical["frames"]]
    spaces = [{x for x in range(512) if mask >> x & 1} for mask in masks]
    namespace = {"c": canonical, "spaces": spaces, "Q": Fraction,
                 "copy": copy, "V": SimpleNamespace(need=need)}
    exec(compile(ast.Module(body=definitions, type_ignores=[]),
                 "authenticated_construct.py", "exec"), namespace)
    program, _, _ = namespace["construct"](data["programs"]["forward"])
    schedule = frame.NativeSchedule(canonical, program)
    return frame, schedule


def domain(frame, lower, upper, cache):
    complement, generated = [], lower
    for vector in frame.basis(upper):
        if not generated >> vector & 1:
            complement.append(vector)
            generated = frame.join(generated, frame.space([vector]))
    gap = len(complement)
    need(gap <= 5, "Fixed-source quotient bound")
    if gap not in cache:
        values = {1}
        for vector in range(1, 1 << gap):
            values |= {frame.join(value, frame.space([vector])) for value in tuple(values)}
        cache[gap] = sorted(values)
    return sorted({frame.join(lower, frame.space(
        [frame.linear(complement, v) for v in frame.basis(value)]))
        for value in cache[gap]})


def compatible_pairs(frame, left, right, columns):
    result = []
    for a, av in enumerate(left):
        moved = frame.image(columns, av)
        for b, bv in enumerate(right):
            if moved & bv == moved:
                result.append((a, b, frame.dimension(bv) - frame.dimension(av)))
    return result


def build_model(frame, schedule):
    graph = schedule.graph
    lower, upper = graph.bounds()
    need(len(lower) <= 16000, "Graph node bound")
    cache = {}
    domains = {i: domain(frame, a, b, cache)
               for i, (a, b) in enumerate(zip(lower, upper)) if a != b}
    need(sum(map(len, domains.values())) <= 5000, "Marginal domain bound")
    counts, rows, rhs, variables = [], [], [], {}
    for i, values in domains.items():
        variables[i] = list(range(len(counts), len(counts) + len(values)))
        counts.extend({} for _ in values)
        rows.append(dict.fromkeys(variables[i], 1))
        rhs.append(1)
    edges = Counter((a, b, m) for b, parents in enumerate(graph.parents) for a, m in parents)
    need(sum(edges.values()) <= 30000, "Mapped edge bound")
    constant = Counter({8: 8})
    for (a, b, columns), multiplicity in sorted(edges.items()):
        if a not in domains and b not in domains:
            constant[frame.dimension(lower[b]) - frame.dimension(lower[a])] += multiplicity
        elif a not in domains or b not in domains:
            i = b if b in domains else a
            for j, value in zip(variables[i], domains[i]):
                rank = (frame.dimension(value) - frame.dimension(lower[a]) if i == b
                        else frame.dimension(lower[b]) - frame.dimension(value))
                counts[j][rank] = counts[j].get(rank, 0) + multiplicity
        else:
            pairs = []
            for ia, ib, rank in compatible_pairs(frame, domains[a], domains[b], columns):
                pairs.append((ia, ib, len(counts)))
                counts.append({rank: multiplicity})
            for side, i in ((0, a), (1, b)):
                for k, variable in enumerate(variables[i]):
                    row = {j: 1 for ia, ib, j in pairs if (ia if side == 0 else ib) == k}
                    row[variable] = -1
                    rows.append(row)
                    rhs.append(0)
    source = Counter({8: 8})
    for (a, b, _), multiplicity in edges.items():
        rank = frame.dimension(schedule.original_values[b]) - frame.dimension(schedule.original_values[a])
        source[rank] += multiplicity
    need(len(counts) <= 25000 and len(rows) <= 16000, "LP size bound")
    return {"rows": rows, "rhs": rhs, "counts": counts, "constant": dict(constant),
            "source": dict(source), "domains": domains, "variables": variables,
            "mapped_edges": sum(edges.values())}


def mathematical_digest(model):
    keys = ("rows", "rhs", "counts", "constant", "source", "domains", "variables", "mapped_edges")
    return digest({key: model[key] for key in keys})
