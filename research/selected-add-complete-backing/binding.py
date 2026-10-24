"""Authenticate retained sources and extract the unchanged Consumer closure."""
import ast
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MANIFEST_SHA = '709790f4ac61ee08d0c82d8ef423cf5233ed0221aaabbc55b4d602a5ffe36258'
CONSUMER = 'research/selected-packet-backing-envelope/sources/pr2697/consumer.py'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def authenticate(root=ROOT):
    raw = (PACKAGE/'SOURCES.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'manifest identity')
    manifest = json.loads(raw)
    data = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        content = (root/row['path']).read_bytes()
        need(hashlib.sha256(content).hexdigest() == row['sha256'], 'source SHA256')
        blob = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        need(blob == row['git_blob'], 'source blob')
        data[row['path']] = content
    return manifest, data


@contextmanager
def loaded(root=ROOT):
    manifest, data = authenticate(root)
    missing = object()
    old = {name: sys.modules.get(name, missing) for name in manifest['modules']}
    modules = {}
    try:
        for name, path in manifest['modules'].items():
            module = ModuleType(name)
            module.__file__ = str(root/path)
            sys.modules[name] = module
            exec(compile(data[path], module.__file__, 'exec'), module.__dict__)
            modules[name] = module
        yield SimpleNamespace(**modules), data
    finally:
        for name, prior in old.items():
            if prior is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = prior


def consumer_coefficient(m, data, case):
    tree = ast.parse(data[CONSUMER])
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Consumer')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'apply')
    candidates = [n for n in ast.walk(method) if isinstance(n, ast.FunctionDef) and n.name == 'coefficient']
    need(len(candidates) == 1, 'unique original Consumer coefficient closure')
    closure = candidates[0]
    skeleton = ast.parse('def bind(context, indices, plan, self, spec):\n pass\n return coefficient').body[0]
    skeleton.body[0] = closure
    module = ast.fix_missing_locations(ast.Module(body=[skeleton], type_ignores=[]))
    namespace = {'Fields':m.records.Fields, 'selected_coefficient':m.numeric.selected_coefficient}
    exec(compile(module, '<unchanged Consumer.apply coefficient AST>', 'exec'), namespace)
    owner = SimpleNamespace(program=case.program, specifications=case.specs)
    context = SimpleNamespace(ring=case.ring, arena=case.r, codes=SimpleNamespace(bits=case.program.code_bits))
    result = namespace['bind'](context, case.ix, case.plan, owner, SimpleNamespace(code=case.code))
    need(set(result.__code__.co_freevars) == {'context','indices','plan','self','spec'}, 'complete original closure environment')
    digest = hashlib.sha256(ast.dump(closure, include_attributes=False).encode()).hexdigest()
    return result, digest


def action(m, data):
    path = 'research/selected-adapter-caller-entry/vendor/stream_runner.py'
    node = next(n for n in ast.parse(data[path]).body if isinstance(n, ast.FunctionDef) and n.name == 'action')
    namespace = {'need':m.words.need,'add_pass':m.stream.add_pass}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<unchanged stream_runner.action AST>', 'exec'), namespace)
    return namespace['action']
