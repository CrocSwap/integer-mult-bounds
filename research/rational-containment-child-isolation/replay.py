"""Run one authenticated historical customer with fresh child import namespaces.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
The retained containment implementation and all its scientific checks are unchanged.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
RETAINED = HERE / 'retained'
PACKAGE = RETAINED / 'research/rational-containment-performance'
EXPECTED_PAYLOAD = 'faa0f9c0159a6e70d4e2cfcdb4012ea62ef350bd26b81312d11da4a770f8b218'
MUTATIONS = (
    ('return tuple(checks)', 'return ()'),
    ('-row[free] * (scale // row[p])', 'row[free] * (scale // row[p])'),
    ('(scale // row[p])', 'scale'),
    ('if equations is None:\n', 'if equations is None:\n            return True\n'),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate():
    rows = json.loads((HERE / 'ORIGINAL.json').read_text())['files']
    need(len(rows) == 17 and len({r['path'] for r in rows}) == 17,
         'complete retained inventory')
    for row in rows:
        path = RETAINED / row['path']
        need(path.is_file() and not path.is_symlink() and
             path.resolve().is_relative_to(RETAINED), 'regular retained source')
        raw = path.read_bytes()
        need(sha(raw) == row['sha256'], 'retained source SHA256: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == row['git_blob'], 'retained source Git blob: ' + row['path'])
    return rows


def program(path):
    """Replace only the three fixed subprocess.run call expressions."""
    tree = ast.parse(path.read_bytes(), filename=str(path))
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute)
             and isinstance(node.func.value, ast.Name)
             and node.func.value.id == 'subprocess' and node.func.attr == 'run']
    expected = {'verify.py': 1, 'benchmark.py': 1, 'test_kernel.py': 1, 'adapter.py': 0}
    need(path.name in expected and len(calls) == expected[path.name],
         'exact subprocess anchors: ' + path.name)
    for node in calls:
        node.func = ast.copy_location(ast.Name(id='_isolated_child', ctx=ast.Load()), node.func)
    # Retain the actual child's optimization flag, including original -O controls.
    return compile(ast.fix_missing_locations(tree), str(path), 'exec')


def child_target(argv):
    need(isinstance(argv, list) and argv and argv[0] == sys.executable,
         'exact child interpreter')
    index = next((i for i in range(1, len(argv)) if not argv[i].startswith('-')), len(argv))
    flags = argv[1:index]
    need(flags in (['-I', '-B'], ['-I', '-B', '-O']), 'exact child flags')
    need(index < len(argv), 'child entry')
    path = Path(argv[index]).resolve()
    if path not in (PACKAGE / 'adapter.py', PACKAGE / 'test_kernel.py'):
        # The original test creates four arithmetic mutants in one private folder.
        # Keep that actual test and changed kernel, never substitute a good kernel.
        need(path.name == 'test_kernel.py' and path.is_file() and not path.is_symlink(),
             'exact child target')
        need(path.read_bytes() == (PACKAGE / 'test_kernel.py').read_bytes(),
             'original mutant test source')
        kernel = (path.parent / 'kernel.py').read_text()
        source = (PACKAGE / 'kernel.py').read_text()
        variants = []
        for before, after in MUTATIONS:
            need(source.count(before) == 1, 'original arithmetic mutation anchor')
            variants.append(source.replace(before, after))
        need(kernel in variants, 'original arithmetic mutant kernel')
        need(flags == ['-I', '-B'], 'original mutant flags')
    return index, path


def child_command(argv, cache, trace):
    index, path = child_target(argv)
    return [*argv[:index], '-X', 'pycache_prefix=' + str(cache), str(HERE / 'replay.py'),
            '--entry', str(path), '--trace', str(trace), '--', *argv[index + 1:]]


def execute(path, arguments, trace):
    authenticate()
    need(sys.pycache_prefix is not None, 'explicit fresh interpreter cache')
    sys.dont_write_bytecode = True

    def isolated_child(argv, **kwargs):
        # Exact original kwargs retain cwd, capture, timeouts and acceptance rules.
        record = {'target': child_target(argv)[1].name, 'status': 'exception'}
        try:
            with tempfile.TemporaryDirectory(prefix='containment-child-cache-') as temp:
                record['cache'] = temp
                result = subprocess.run(child_command(argv, Path(temp), trace), **kwargs)
                record.update(status='returned', returncode=result.returncode)
                return result
        finally:
            if 'cache' in record:
                record['cache_removed'] = not Path(record['cache']).exists()
                (trace / (Path(record['cache']).name + '.json')).write_text(json.dumps(record))

    if path == PACKAGE / 'verify.py':
        # Its ordinary import of benchmark must use the same one-call adapter.
        module = types.ModuleType('benchmark')
        module.__file__ = str(PACKAGE / 'benchmark.py')
        module._isolated_child = isolated_child
        exec(program(PACKAGE / 'benchmark.py'), module.__dict__)
        sys.modules['benchmark'] = module
    module = types.ModuleType('__main__')
    module.__file__ = str(path)
    module._isolated_child = isolated_child
    previous_main, previous_argv = sys.modules['__main__'], sys.argv
    try:
        sys.modules['__main__'] = module
        sys.argv = [str(path), *arguments]
        exec(program(path), module.__dict__)
    finally:
        observed = sys.modules.get('rational_span_frames')
        record = {'entry': path.name, 'cache': sys.pycache_prefix,
                  'dot_unit': observed.dot((1,), (1,)) if observed is not None else None}
        (trace / ('entry-' + Path(sys.pycache_prefix).name + '.json')).write_text(json.dumps(record))
        sys.modules['__main__'], sys.argv = previous_main, previous_argv


def replay():
    before = authenticate()
    with tempfile.TemporaryDirectory(prefix='containment-isolation-') as temp:
        work = Path(temp).resolve()
        trace = work / 'trace'
        trace.mkdir()
        output = work / 'output'
        with tempfile.TemporaryDirectory(prefix='containment-parent-cache-') as cache:
            command = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + cache,
                       str(HERE / 'replay.py'), '--entry', str(PACKAGE / 'verify.py'),
                       '--trace', str(trace), '--', '--output', str(output)]
            result = subprocess.run(command, cwd=RETAINED, capture_output=True, text=True, timeout=180)
            need(result.returncode == 0, 'original complete replay failed:\n' + result.stdout + result.stderr)
            need(result.stdout.strip().endswith('PASS_RATIONAL_CONTAINMENT calls=42860 kernel_mutants=4 '
                                               'source_mutants=6 frame_mutants=2 adapter_controls=2'),
                 'original complete replay marker')
        need(not Path(cache).exists(), 'parent cache cleanup')
        scientific = json.loads((output / 'RESULT.json').read_text())
        reference = json.loads((PACKAGE / 'VALIDATION.json').read_text())
        # Only host/timing metadata are excluded. Every original scientific field
        # is compared, including all child arithmetic failures and source controls.
        metadata = {'benchmark_process_wall_ratio', 'python', 'platform', 'base_commit',
                    'source_sha256', 'not_run', 'additional_checks'}
        expected = {k: v for k, v in reference.items() if k not in metadata}
        actual = {k: v for k, v in scientific.items() if k != 'benchmark_process_wall_ratio'}
        need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
             'complete original scientific receipt')
        calls = [json.loads(p.read_text()) for p in trace.glob('containment-child-cache-*.json')]
        entries = [json.loads(p.read_text()) for p in trace.glob('entry-*.json')]
        need(len(calls) == 13 and len(entries) == 14, 'complete fixed interpreter tree')
        need(len({r['cache'] for r in entries}) == 14, 'distinct interpreter namespaces')
        need(all(r['cache_removed'] for r in calls), 'all child cache cleanup')
        need(sum(r.get('returncode') == 0 for r in calls) == 7 and
             sum(r.get('returncode') != 0 for r in calls) == 6, 'original child decisions')
        values = [r['dot_unit'] for r in entries if r['dot_unit'] is not None]
        need(values == [8] * 6, 'authenticated numerical source in parent and five adapters')
        need(authenticate() == before, 'source inventory changed')
        return dict(status='PASS_CONTAINMENT_CHILD_ISOLATION', scientific=expected,
                    child_calls=13, interpreter_namespaces=14, observed_dot_unit=8,
                    numerical_observations=len(values), successful_children=7,
                    expected_child_rejections=6, all_caches_removed=True,
                    retained_files=len(before))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entry', type=Path)
    parser.add_argument('--trace', type=Path)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.entry is not None:
        need(args.trace is not None and args.trace.is_dir(), 'trace directory')
        path = args.entry.resolve()
        if path != PACKAGE / 'verify.py':
            child_target([sys.executable, '-I', '-B', str(path)])
        arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
        execute(path, arguments, args.trace)
    else:
        need(args.trace is None and not args.arguments, 'parent arguments')
        print(json.dumps(replay(), sort_keys=True))


if __name__ == '__main__':
    main()
