"""Authenticated source partition, before any online payload exists.
The original carve and Core.partition bodies are executed unchanged. Their
sequential setup simulation is charged separately in PROOF.md.
"""
import ast
from hashlib import sha256
from types import SimpleNamespace
CARVE = 'research/capped-phase-fusion/evidence/gaussian_fast_ultra/check_capped_gauges.py'
CORE = 'research/rational-unitary-fft/core.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def partition(raw, reference, origin, length, cap, band=None):
    minimum = 2 * reference.spec.source_halfwidth + 2
    band = minimum if band is None else band
    need(type(origin) is int and type(length) is int and type(cap) is int
         and 0 <= origin < origin + length <= reference.target_size
         and reference.target_size-length >= band >= minimum
         and cap > 0 and cap & (cap-1) == 0 and 2*cap <= reference.spec.source_size,
         'source core carve domain')
    carve_tree = ast.parse(raw[CARVE])
    carve_nodes = [node for node in carve_tree.body if isinstance(node, ast.FunctionDef)
                   and node.name == 'carve']
    core_tree = ast.parse(raw[CORE])
    classes = [node for node in core_tree.body if isinstance(node, ast.ClassDef) and node.name == 'Core']
    need(len(carve_nodes) == len(classes) == 1, 'unique retained carve/Core source')
    partitions = [node for node in classes[0].body if isinstance(node, ast.FunctionDef)
                  and node.name == 'partition']
    need(len(partitions) == 1, 'unique unchanged source partition body')
    module = ast.Module(body=carve_nodes + partitions, type_ignores=[])
    namespace = {'need': need}
    exec(compile(module, '<authenticated carve and Core.partition>', 'exec', optimize=0), namespace)
    state = SimpleNamespace(reference=reference, n=length, coordinates=tuple(range(origin, origin+length)),
                            width=band, cap=cap, carve=namespace['carve'])
    pieces, cells = namespace['partition'](state)
    blocks = tuple(tuple(cell['indices']) for cell in cells)
    return blocks, dict(origin=origin, length=length, band=band, cap=cap,
                       pieces=pieces, interior_blocks=blocks,
                       carve_ast_sha256=sha256(ast.dump(carve_nodes[0]).encode()).hexdigest(),
                       partition_ast_sha256=sha256(ast.dump(partitions[0]).encode()).hexdigest())
