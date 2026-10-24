"""Transport-only loader; frozen scientific expressions remain unchanged.

Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import ast
import contextlib
import hashlib
import io
import json
import runpy
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
B_MANIFEST = '3fa257834ba6635cadc8b1df4c6dfadd602dba99111ce4fc56926829ac8cb58e'
A_MANIFEST = 'a7d684b92f2bc54ac2a201dcabdc52c549dba8089a1141bb54167806a92d6deb'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked_files(root, rows):
    for name, expected in rows.items():
        path = root / name
        need(path.is_file() and not path.is_symlink(), 'Missing/nonregular frozen file: ' + name)
        need(digest(path.read_bytes()) == expected, 'Frozen byte mismatch: ' + name)


def integrity():
    package_rows = json.loads((HERE / 'PACKAGE-FILES.json').read_text())
    checked_files(HERE, package_rows)
    package_actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts}
    need(package_actual == set(package_rows) | {'PACKAGE-FILES.json'}, 'Exact package file inventory')
    evidence = HERE / 'evidence'
    manifest = evidence / 'FILES.json'
    need(digest(manifest.read_bytes()) == B_MANIFEST, 'Independent 28-file manifest')
    rows = json.loads(manifest.read_text())
    need(len(rows) == 28, 'Exact independent archive inventory')
    actual = {p.relative_to(evidence).as_posix() for p in evidence.rglob('*') if p.is_file()}
    need(actual == set(rows) | {'FILES.json'}, 'Exact retained evidence inventory')
    checked_files(evidence, rows)
    author = evidence / 'frozen/pr4948-saved-query-macro-gate'
    need(digest((author / 'FILES.json').read_bytes()) == A_MANIFEST, 'Original six-file author manifest')
    checked_files(author, json.loads((author / 'FILES.json').read_text()))
    config = json.loads((HERE / 'INPUTS.json').read_text())
    checked_files(author, config['mandatory_addenda'])
    requests = {}
    for row in config['requests']:
        data = (HERE / row['local']).read_bytes()
        need(digest(data) == row['sha256'], 'Ancestor-bound source input: ' + row['local'])
        key = (row['head'], row['path'])
        need(key not in requests, 'Duplicate original source request')
        requests[key] = data
    return requests


class Loader:
    def __init__(self, stage, requests):
        self.stage = stage
        self.requests = requests
        self.mixed = stage / 'frozen/pr4948-mixed-thin-gate/check.py'
        self.author = stage / 'frozen/pr4948-saved-query-macro-gate'
        self.allowed = {self.mixed.resolve(), (self.author / 'bank_span.py').resolve(),
                        (self.author / 'grade_gate.py').resolve()}

    def fetch(self, head, path):
        key = (head, path)
        need(key in self.requests, 'Unretained original Git request: ' + repr(key))
        return self.requests[key]

    def run(self, path):
        path = Path(path).resolve()
        need(path in self.allowed, 'Undeclared frozen dependency path')
        tree = ast.parse(path.read_bytes(), filename=str(path))
        replacements = 0
        if path == self.mixed.resolve():
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == 'fetch':
                    need([a.arg for a in node.args.args] == ['head', 'path'], 'Original fetch signature')
                    node.body = [ast.Return(value=ast.Call(func=ast.Name(id='_retained_fetch', ctx=ast.Load()),
                                 args=[ast.Name(id='head', ctx=ast.Load()), ast.Name(id='path', ctx=ast.Load())], keywords=[]))]
                    replacements += 1
            need(replacements == 1, 'Exactly one Git-byte reader adaptation')
        else:
            class Dispatch(ast.NodeTransformer):
                def visit_Call(self, node):
                    nonlocal replacements
                    self.generic_visit(node)
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and \
                            node.func.value.id == 'runpy' and node.func.attr == 'run_path':
                        node.func = ast.Name(id='_portable_run_path', ctx=ast.Load())
                        replacements += 1
                    return node
            tree = Dispatch().visit(tree)
            need(replacements == 1, 'Exactly one retained relative dependency dispatch')
        ast.fix_missing_locations(tree)
        env = {'__name__': '<run_path>', '__file__': str(path),
               '_retained_fetch': self.fetch, '_portable_run_path': self.run}
        exec(compile(tree, str(path), 'exec'), env)
        return env


def capture(path, action, expected):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        result = action()
    data = stream.getvalue().encode('utf-8')
    path.write_bytes(data)
    need(data == expected.read_bytes(), 'Fresh stdout differs from frozen receipt: ' + expected.name)
    return result, {'receipt': expected.name, 'sha256': digest(data), 'bytes': len(data)}


def author_replay(stage, requests, work):
    loader = Loader(stage, requests)
    reports = []
    for script, receipt in [('bank_span.py', 'BANK-SPAN.json'), ('grade_gate.py', 'GRADE-GATE.json')]:
        _, report = capture(work / (script + '.stdout.json'),
                            lambda script=script: loader.run(loader.author / script), loader.author / receipt)
        reports.append(report)
    return reports


def independent_replay(stage, work):
    # Already Git-free; no AST adaptation of the independent science.
    with contextlib.redirect_stdout(io.StringIO()):
        env = runpy.run_path(str(stage / 'independent.py'), run_name='retained_independent')
    _, report = capture(work / 'independent.stdout.json', env['main'], stage / 'INDEPENDENT.json')
    return report


@contextlib.contextmanager
def private_stage():
    requests = integrity()
    with tempfile.TemporaryDirectory(prefix='passive-saved-cut-') as directory:
        work = Path(directory)
        stage = work / 'evidence'
        # Private mutation fixtures need writable copies even when the exported
        # publication files themselves are mounted/read-protected.
        shutil.copytree(HERE / 'evidence', stage, copy_function=shutil.copyfile)
        yield stage, requests, work


def controls(stage, requests, work):
    passed = []

    def rejects(label, action):
        try:
            action()
        except ValueError:
            passed.append(label)
        else:
            raise ValueError('Mutation accepted: ' + label)

    loader = Loader(stage, requests)
    rejects('unretained Git source request', lambda: loader.fetch('0' * 40, 'unretained.py'))
    rejects('undeclared dependency dispatch', lambda: loader.run(work / 'unretained.py'))
    frozen = stage / 'frozen/pr4948-saved-query-macro-gate'
    rows = json.loads((stage / 'FILES.json').read_text())
    clarify = frozen / 'OWNED-RESET-CLARIFICATION.md'
    original = clarify.read_bytes()
    clarify.write_bytes(original + b'\nchanged')
    rejects('altered mandatory reset clarification', lambda: checked_files(stage, rows))
    clarify.write_bytes(original)
    source = stage / 'inputs/NORMALIZERS.json'
    original = source.read_bytes()
    source.write_bytes(original + b'\nchanged')
    rejects('altered scientific input bytes', lambda: checked_files(stage, rows))
    source.write_bytes(original)
    mismatch = work / 'wrong-receipt.json'
    mismatch.write_text('{"target_grade":7}\n')
    rejects('wrong scientific receipt', lambda: capture(work / 'wrong.stdout', lambda: print('{"target_grade":9}'), mismatch))
    checked_files(stage, rows)
    return passed
