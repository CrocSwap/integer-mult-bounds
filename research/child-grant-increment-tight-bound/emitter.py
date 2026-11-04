"""Narrow, source-authenticated emission; never runs source Machine/Tape.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The increment is thu-nmrc's; assembler/rewind are David Arias PR2776 work.
"""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    'producer.py': 'dbd58802087ce10e39a72202960dbb5d4aa5ce50dc1b99b7ec98e07273c292b6',
    'machine.py': '04b7b76b9f06653d94d2158196cdd1bed7883dd1f59fcbc81a486e3ffb248681',
    'counters.py': '2b51181a3efd403be14111ed2d556ba10e63a8939756e69d488d12344d5a7ad1',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, 'source loader')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def emit_table():
    """Execute only the pinned increment definition and its emission deps.

    Original producer module imports/builds are not executed. The exact AST
    FunctionDef is extracted intact; it calls only m constants, asm methods
    and c.emit_rewind. All three complete source bytes authenticate first.
    The wrapper HALT is a continuation boundary, not a counted macro step.
    """
    paths = {name: HERE / 'inputs' / name for name in PINS}
    for name, path in paths.items():
        need(hashlib.sha256(path.read_bytes()).hexdigest() == PINS[name],
             'emitter source byte drift: ' + name)
    parsed = ast.parse(paths['producer.py'].read_text(encoding='utf-8'))
    nodes = [node for node in parsed.body
             if isinstance(node, ast.FunctionDef) and node.name == 'increment']
    need(len(nodes) == 1, 'exact increment definition')
    node = nodes[0]
    need(not node.decorator_list and not node.args.defaults
         and not node.args.kw_defaults and not node.args.kwonlyargs
         and node.args.vararg is None and node.args.kwarg is None
         and not node.args.posonlyargs
         and [arg.arg for arg in node.args.args] == ['asm', 'tape', 'fail', 'prefix'],
         'increment extraction signature')
    module_ast = ast.Module(body=[node], type_ignores=[])
    machine = load_source('_s7_pinned_machine', paths['machine.py'])
    old_machine = sys.modules.get('machine')
    sys.modules['machine'] = machine
    try:
        counters = load_source('_s7_pinned_counters', paths['counters.py'])
        namespace = {'m': machine, 'c': counters}
        exec(compile(module_ast, str(paths['producer.py']), 'exec'), namespace)
        asm = machine.Assembler(2)
        fail = asm.fresh('isolated_increment_failure')
        namespace['increment'](asm, 0, fail, 'isolated_increment')
        stop_pc = len(asm.instructions)
        asm.halt()
        asm.label(fail)
        fail_pc = len(asm.instructions)
        asm.reject('invalid isolated increment symbol')
        program = asm.finish(entry=0)
        table = {'schema_version': 1, 'tapes': program.tapes,
                 'entry': program.entry, 'stop_pc': stop_pc, 'fail_pc': fail_pc,
                 'instructions': program.instructions}
        return json.loads(json.dumps(table, sort_keys=True))
    finally:
        if old_machine is None:
            sys.modules.pop('machine', None)
        else:
            sys.modules['machine'] = old_machine
