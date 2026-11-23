"""Load only named immutable definitions; never bootstrap a predecessor tree."""
import ast
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import chain
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'sources'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    record = json.loads((ROOT/'SOURCE-BINDINGS.json').read_text())
    for name, entry in record['files'].items():
        need(sha256((SRC/name).read_bytes()).hexdigest() == entry['sha256'], 'source hash: '+name)
    return record


def extract(name, selected, ns, *, strip_inner_imports=False):
    tree = ast.parse((SRC/name).read_text())
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in selected]
    need({node.name for node in nodes} == set(selected), 'missing source definitions')
    if strip_inner_imports:
        class Imports(ast.NodeTransformer):
            def visit_Import(self, node): return None
            def visit_ImportFrom(self, node): return None
        nodes = [Imports().visit(node) for node in nodes]
    exec(compile(ast.Module(nodes, type_ignores=[]), name, 'exec'), ns)


@cache
def load():
    authenticate()
    ns = dict(Fraction=Fraction, F=Fraction, dataclass=dataclass, cache=cache, chain=chain)
    from collections import defaultdict
    from math import isqrt
    ns.update(defaultdict=defaultdict, isqrt=isqrt)
    extract('ternary_frames.py', ['identity','transpose','multiply','residue','inverse','projector','frame_at_three','covered_factors'], ns)
    extract('cover.py', ['require','row_program'], ns)
    extract('factored_frames.py', ['inverse_word','coordinate_word','apply_row','Frame'], ns)
    extract('periodic.py', ['Job'], ns)
    extract('raw_binary.py', ['Axis','placed_job','job_frame','Catalogue','BinarySource'], ns)
    graph = json.loads((SRC/'graph.json').read_text())
    caller = json.loads((SRC/'caller.json').read_text())
    ns.update(graph=lambda:graph, caller=lambda:caller)
    extract('strong_binary.py', ['fixed_binary_charts','ActiveCatalogue','active_catalogue','StrongBinarySource'], ns, strip_inner_imports=True)
    extract('transport.py', ['ceil','Measure','Link','Source','axes','Plan','Recipe'], ns)
    @dataclass(frozen=True)
    class Port:
        tag: tuple
        rank: int
    @dataclass(frozen=True)
    class Word:
        targets: tuple
        paid: tuple
    ns.update(Port=Port, bit_word=lambda targets, paid:Word(tuple(targets),tuple(paid)))
    extract('tagged_sources.py',['binary_ports'],ns)
    ns['raw_word'] = ns['binary_ports'](graph,caller)
    return ns


def word_json(word):
    rows=[]
    for op in word:
        row=[]
        for value in op:
            if isinstance(value,Fraction): row.append([value.numerator,value.denominator])
            else: row.append(value)
        rows.append(row)
    return rows


@cache
def library():
    ns=load(); differences,joints=ns['fixed_binary_charts']()
    unique={tuple(word) for word,rank in differences.values()}
    unique.update(joints); unique.discard(())
    words=((),*sorted(unique,key=lambda w:json.dumps(word_json(w),separators=(',',':'))))
    data=json.dumps([word_json(w) for w in words],separators=(',',':'),sort_keys=True).encode()
    return words, data
