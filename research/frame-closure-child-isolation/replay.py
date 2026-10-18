"""Source-bound opt-in replay of one frozen caller and its Python children."""
import argparse
import ast
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/bit-frame-closure-basis'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    runtime = [row for row in manifest['files'] if row['usage'] == 'input']
    for row in runtime + manifest['retained_documents']:
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: '+row['path'])


def program(name):
    """Compile exact source, changing only declared call and path anchors."""
    path = SOURCE/name
    tree = ast.parse(path.read_bytes(), filename=str(path))
    calls = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == 'subprocess' and node.func.attr == 'run'):
            calls.append(node)
    expected = {'verify.py': 2, 'test_closure.py': 1, 'run.py': 0}
    need(name in expected and len(calls) == expected[name], 'exact subprocess anchors')
    for node in calls:
        node.func = ast.copy_location(ast.Name(id='_isolated_child', ctx=ast.Load()), node.func)
    if name == 'run.py':
        # The frozen checker extracts its display basename with rsplit('/').
        # Only this input argv spelling changes; its source and reports do not.
        anchor = ast.dump(ast.parse('str(ROOT / path)', mode='eval').body)
        matches = [node for node in ast.walk(tree)
                   if isinstance(node, ast.Call) and ast.dump(node) == anchor]
        need(len(matches) == 1, 'exact input path spelling anchor')
        node = matches[0]
        node.func = ast.Attribute(value=node.args[0], attr='as_posix', ctx=ast.Load())
        node.args = []
    return compile(ast.fix_missing_locations(tree), str(path), 'exec', optimize=0)


def child_command(argv, cache, trace):
    """Accept only the three authenticated caller forms; preserve every flag."""
    need(isinstance(argv, list) and argv and argv[0] == sys.executable, 'child interpreter')
    index = next((i for i in range(1, len(argv)) if not argv[i].startswith('-')), len(argv))
    flags = argv[1:index]
    need(flags in (['-I', '-B'], ['-I', '-O', '-B']), 'exact child flags')
    need(index < len(argv), 'child entry')
    target = Path(argv[index])
    need(target in (SOURCE/'run.py', SOURCE/'test_closure.py'), 'exact child target')
    return [sys.executable, *flags, '-X', 'pycache_prefix='+str(cache),
            str(HERE/'replay.py'), '--trace-dir', str(trace), '--child', target.name,
            '--', *argv[index+1:]]


def execute(name, arguments, trace):
    authenticate()

    def isolated_child(argv, **kwargs):
        # Exactly the original subprocess kwargs are passed on. In particular,
        # optimization rejection, timeouts and output comparison are retained.
        with tempfile.TemporaryDirectory(prefix='frame-child-cache-') as temp:
            cache = Path(temp)
            record = {'target': Path(next(x for x in argv[1:] if not x.startswith('-'))).name,
                      'cache': str(cache), 'pid': os.getpid(), 'status': 'exception'}
            try:
                process = subprocess.run(child_command(argv, cache, trace), **kwargs)
                record.update(status='returned', returncode=process.returncode)
                return process
            finally:
                # The record is written after context cleanup by the outer
                # finally below; this inner finally preserves exceptional status.
                pending.append(record)

    # A module is required: unittest.main discovers __main__ through sys.modules.
    module = types.ModuleType('__main__')
    module.__file__ = str(SOURCE/name)
    module._isolated_child = isolated_child
    previous_main, previous_argv = sys.modules['__main__'], sys.argv
    old_path = list(sys.path)
    pending = []
    try:
        sys.modules['__main__'] = module
        sys.argv = [str(SOURCE/name), *arguments]
        sys.path.insert(0, str(SOURCE))
        exec(program(name), module.__dict__)
    finally:
        imported = sys.modules.get('closure')
        if imported is not None:
            observation = {'entry': name, 'prime': imported.PRIME,
                           'cache_prefix': sys.pycache_prefix}
            (trace/('import-'+Path(sys.pycache_prefix).name+'.json')).write_text(
                json.dumps(observation, sort_keys=True), encoding='utf-8')
        for record in pending:
            record['cache_removed'] = not Path(record['cache']).exists()
            name_out = Path(record['cache']).name+'.json'
            (trace/name_out).write_text(json.dumps(record, sort_keys=True), encoding='utf-8')
        sys.modules['__main__'], sys.argv = previous_main, previous_argv
        sys.path[:] = old_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child', choices=('run.py', 'test_closure.py'))
    parser.add_argument('--trace-dir', type=Path)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    if args.child:
        need(args.trace_dir is not None and args.trace_dir.is_dir(), 'trace directory')
        need(sys.pycache_prefix is not None, 'explicit child cache prefix')
        sys.dont_write_bytecode = True
        execute(args.child, arguments, args.trace_dir)
        return
    need(not arguments and args.trace_dir is None, 'parent arguments')
    # Parent imports also need a fresh namespace even when called directly.
    old_prefix, old_write = sys.pycache_prefix, sys.dont_write_bytecode
    with tempfile.TemporaryDirectory(prefix='frame-parent-cache-') as parent_cache:
        with tempfile.TemporaryDirectory(prefix='frame-child-traces-') as temp:
            trace = Path(temp)
            try:
                sys.pycache_prefix, sys.dont_write_bytecode = parent_cache, True
                output = io.StringIO()
                with redirect_stdout(output):
                    execute('verify.py', [], trace)
                caller = json.loads(output.getvalue())
                records = [json.loads(path.read_text()) for path in trace.glob('frame-child-cache-*.json')]
                observations = [json.loads(path.read_text()) for path in trace.glob('import-*.json')]
                need(len(records) == 8, 'all eight nested calls')
                need(len(observations) == 9, 'parent and eight imported source values')
                need(all(r['prime'] == 2147483647 for r in observations), 'current source numeric value')
                need(len({r['cache_prefix'] for r in observations}) == 9, 'all nine import namespaces')
                need(len({r['cache'] for r in records}) == 8, 'fresh per-child namespace')
                need(all(r['cache_removed'] for r in records), 'child cache cleanup')
                need(sum(r.get('returncode') == 0 for r in records) == 7, 'seven successful children')
                need(sum(r.get('returncode') != 0 for r in records) == 1, 'optimized rejection retained')
                result = {'status': 'PASS_FRAME_CLOSURE_CHILD_ISOLATION', 'caller': caller,
                          'nested_calls': 8, 'unique_child_caches': 8,
                          'removed_child_caches': 8, 'optimized_rejections': 1,
                          'path_spelling_anchors': 1, 'subprocess_anchors': 3,
                          'current_source_imports': 9, 'observed_prime': 2147483647}
            finally:
                sys.pycache_prefix, sys.dont_write_bytecode = old_prefix, old_write
    need(not Path(parent_cache).exists(), 'parent cache cleanup')
    result['parent_cache_removed'] = True
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
