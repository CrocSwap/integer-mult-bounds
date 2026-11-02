"""Assertion-preserving execution of one authenticated bounded-kernel package."""
import ast
import contextlib
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "wordram-ntt-kernel"
PREFIX = "research/wordram-ntt-kernel/"
ERROR_NAME = "_imb_certificate_assertion_error"
MAX_BYTES, MAX_NODES, MAX_DEPTH = 1_048_576, 30_000, 64


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, digest, label):
    need(len(raw) <= MAX_BYTES, "source size: " + label)
    need(hashlib.sha256(raw).hexdigest() == digest, "source hash: " + label)
    return raw


def read_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    need(1 <= len(rows) <= 64, "bounded source inventory")
    files = {}
    for row in rows:
        path = row["path"]
        need(path.startswith(PREFIX), "source package boundary")
        name = path.removeprefix(PREFIX)
        need(name not in files and ".." not in Path(name).parts, "source spelling")
        with (SOURCE / name).open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        files[name] = authenticate(raw, row["sha256"], name)
    need("MANIFEST.json" in files and "verify.py" in files, "source roots")
    inventory = json.loads(files["MANIFEST.json"])["files"]
    need(set(files) == set(inventory) | {"MANIFEST.json"}, "complete source closure")
    for name, digest in inventory.items():
        authenticate(files[name], digest, name)
    return files


def bounded_tree(raw, name):
    need(len(raw) <= MAX_BYTES and ERROR_NAME.encode() not in raw, "source boundary")
    tree = ast.parse(raw, filename=name)
    pending, count = [(tree, 0)], 0
    for _ in range(MAX_NODES + 1):
        if not pending:
            return tree
        node, depth = pending.pop()
        count += 1
        need(count <= MAX_NODES and depth <= MAX_DEPTH, "AST capacity")
        pending.extend((child, depth + 1) for child in ast.iter_child_nodes(node))
    raise ValueError("AST capacity")


def failure_branch(statement):
    args = [] if statement.msg is None else [statement.msg]
    error = ast.Call(ast.Name(ERROR_NAME, ast.Load()), args, [])
    replacement = ast.If(ast.UnaryOp(ast.Not(), statement.test),
                         [ast.Raise(error, None)], [])
    return ast.copy_location(replacement, statement)


def lower(raw, name, entry=False, optimize=None):
    tree = bounded_tree(raw, name)
    nodes = list(ast.walk(tree))
    assertions = [(node.lineno, node.col_offset) for node in nodes
                  if isinstance(node, ast.Assert)]
    need(sum(isinstance(node, ast.Name) and node.id == "__debug__" for node in nodes)
         == int(entry), "optimization guard inventory")
    guards = 0
    for node in nodes:
        if isinstance(node, ast.Name) and node.id == "__debug__":
            need(entry, "unexpected optimization guard")
        if isinstance(node, ast.If) and ast.dump(node.test) == (
                "UnaryOp(op=Not(), operand=Name(id='__debug__', ctx=Load()))"):
            need(entry and len(node.body) == 1 and not node.orelse, "entry guard shape")
            need(ast.unparse(node.body[0]) == "raise SystemExit(" + repr(
                "Run without Python -O: certificate assertions must be enabled.") + ")",
                "entry guard message")
            node.test = ast.copy_location(ast.Constant(False), node.test)
            guards += 1
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                setattr(node, field, [failure_branch(child) if isinstance(child, ast.Assert)
                                     else child for child in value])
    need(guards == int(entry), "entry guard count")
    need(not any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
         "no optimizer-removable certificate checks")
    ast.fix_missing_locations(tree)
    level = sys.flags.optimize if optimize is None else optimize
    return compile(tree, name, "exec", dont_inherit=True, optimize=level), assertions


class CheckedLoader(importlib.abc.Loader):
    def __init__(self, finder, name):
        self.finder, self.name = finder, name

    def create_module(self, spec):
        return None  # Use the standard module allocation.

    def exec_module(self, module):
        code, checks = lower(self.finder.files[self.name], str(SOURCE / self.name))
        module.__dict__[ERROR_NAME] = AssertionError
        exec(code, module.__dict__)
        self.finder.loaded[self.name] = module
        self.finder.checks[self.name] = checks


class CheckedFinder(importlib.abc.MetaPathFinder):
    def __init__(self, files):
        self.files, self.loaded, self.checks = files, {}, {}

    def find_spec(self, fullname, path=None, target=None):
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.origin is None:
            return None
        origin = Path(spec.origin).resolve()
        if not origin.is_relative_to(SOURCE):
            return None
        name = origin.relative_to(SOURCE).as_posix()
        need(name in self.files and name.endswith(".py"), "authenticated import")
        loader = CheckedLoader(self, name)
        return importlib.util.spec_from_file_location(fullname, origin, loader=loader)


def ntt_runner(records, scratch):
    def run(argv, cwd, check):
        expected = [sys.executable, "-B", "-m", "unittest", "discover",
                    "-s", "ntt", "-p", "test_*.py"]
        need(argv == expected and Path(cwd) == SOURCE and check is True, "NTT child ABI")
        env = dict(os.environ)
        env.pop("PYTHONOPTIMIZE", None)
        env.pop("PYTHONPATH", None)
        with tempfile.TemporaryDirectory(prefix="ntt-bytecode-", dir=scratch) as cache:
            flags = ["-O"] * sys.flags.optimize
            command = argv[:1] + flags + ["-X", "pycache_prefix=" + cache] + argv[1:]
            result = subprocess.run(command, cwd=cwd, check=True, env=env,
                                    capture_output=True, text=True, timeout=180)
        need("Ran 8 tests" in result.stderr and result.stderr.rstrip().endswith("OK"),
             "complete NTT unittest checklist")
        records.append({"tests": 8, "optimized": sys.flags.optimize,
                        "stdout": result.stdout})
        return result
    return run


def replay(files, scratch):
    finder, child_records = CheckedFinder(files), []
    code, checks = lower(files["verify.py"], str(SOURCE / "verify.py"), entry=True)
    module = types.ModuleType("_imb_bounded_entry")
    module.__file__ = str(SOURCE / "verify.py")
    module.__dict__[ERROR_NAME] = AssertionError
    old_path, old_modules = list(sys.path), set(sys.modules)
    need(len(old_modules) <= 2048, "bounded clean interpreter")
    for name in old_modules:
        filename = getattr(sys.modules[name], "__file__", None)
        need(not filename or not Path(filename).resolve().is_relative_to(SOURCE),
             "source modules must not be preloaded")
    sys.path.insert(0, str(SOURCE))
    sys.meta_path.insert(0, finder)
    try:
        exec(code, module.__dict__)
        module.subprocess = types.SimpleNamespace(run=ntt_runner(child_records, scratch))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.main()
        result = json.loads(output.getvalue())
        need(len(child_records) == 1, "one complete NTT subprocess")
        finder.checks["verify.py"] = checks
        expected = {name for name in files if name.endswith(".py")}
        expected.remove("ntt/test_exact_ntt.py")
        need(set(finder.checks) == expected, "complete adapted module inventory")
        need(sum(map(len, finder.checks.values())) == 55, "complete assertion inventory")
        return result, finder, child_records
    finally:
        sys.path[:] = old_path
        sys.meta_path.remove(finder)
        for name in set(sys.modules) - old_modules:
            loaded = sys.modules[name]
            filename = getattr(loaded, "__file__", None)
            if filename and Path(filename).resolve().is_relative_to(SOURCE):
                del sys.modules[name]


def reference(scratch):
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory(prefix="wordram-reference-", dir=scratch) as cache:
        env["PYTHONPYCACHEPREFIX"] = cache
        command = [sys.executable, "-B", "-X", "pycache_prefix=" + cache,
                   str(SOURCE / "verify.py")]
        result = subprocess.run(command, cwd=SOURCE, env=env, capture_output=True,
                                text=True, check=True, timeout=180)
    need("Ran 8 tests" in result.stderr and result.stderr.rstrip().endswith("OK"),
         "reference NTT checklist")
    output = json.loads(result.stdout)
    output.pop("seconds")
    return output
