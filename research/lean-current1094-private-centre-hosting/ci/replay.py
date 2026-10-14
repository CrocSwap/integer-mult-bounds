"""Exact Hosting replay from pinned public inputs. No installation or network here.
Reuse the unchanged native raw serial runner; a compact aggregate locks every
transitive source/object pair and ordered first match without copying its catalogue.
OpenAI assistance; Apache-2.0. This proposal still requires its candidate-bound test.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, datetime

HERE = Path(__file__).resolve().parent

def pin(path):
    p = Path(path)
    with p.open('rb') as f:
        h = hashlib.file_digest(f, 'sha256').hexdigest()
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': h}

def checked(path, expected):
    actual = pin(path)
    assert (actual['bytes'], actual['sha256']) == (expected['bytes'], expected['sha256']), str(path)
    return actual

def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args],
        env={**os.environ, 'GIT_NO_LAZY_FETCH': '1', 'GIT_TERMINAL_PROMPT': '0'}, timeout=20).decode().strip()

def imports(s):
 i=0
 def skip(i):
  while i<len(s):
   if s[i].isspace():i+=1
   elif s.startswith('--',i):
    j=s.find('\n',i);i=len(s) if j<0 else j+1
   elif s.startswith('/-',i):
    depth=1;i+=2
    while depth:
     assert i<len(s)
     if s.startswith('/-',i):depth+=1;i+=2
     elif s.startswith('-/',i):depth-=1;i+=2
     else:i+=1
   else:break
  return i
 i=skip(i);pre=False;im=[]
 if re.match(r'module\b',s[i:]):i=skip(i+6)
 if re.match(r'prelude\b',s[i:]):pre=True;i=skip(i+7)
 while (prefix:=re.match(r'(?:(?:public|private)\s+)?import\b',s[i:])):
  i=skip(i+len(prefix[0]))
  if re.match(r'all\b',s[i:]):i=skip(i+3)
  while True:
   m=re.match(r'[A-Za-z_][\w.]*',s[i:]);assert m
   im.append(m[0]);i+=len(m[0]);j=i
   while j<len(s) and s[j] in ' \t':j+=1
   if j<len(s) and s[j]!='\n' and not s.startswith('--',j) and not s.startswith('/-',j):i=j;continue
   i=skip(i);break
 return im,pre

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--package', type=Path, default=HERE.parent)
    ap.add_argument('--lean-root', type=Path, required=True)
    ap.add_argument('--mathlib', type=Path, required=True)
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--compiler-lock', type=Path, required=True)
    ap.add_argument('--run', action='store_true', help='Actually run the bounded compiler after exact preparation')
    a = ap.parse_args()
    repo, package, lean, mathlib, prepared, output = [p.resolve() for p in
        [a.repo, a.package, a.lean_root, a.mathlib, a.prepared, a.output]]
    assert not output.exists(), 'Output exists: preserve it and diagnose; never overwrite.'
    lock = json.loads((HERE / 'LOCK.json').read_text())
    assert pin(HERE / 'run_native.py')['sha256'] == lock['runner_sha256']
    package_pins = [checked(package / name, expected) for name, expected in lock['package_inputs'].items()]
    manifest = json.loads((package / 'SOURCE_MANIFEST.json').read_text())
    reference = json.loads((package / 'ACCEPTED_CHECKS.json').read_text())
    assert [r['module'] for r in reference['modules']] == manifest['compile_order']
    local = {r['module']: r for r in manifest['modules']}
    local_sources = {n: checked(prepared / 'sources' / (n + '.lean'), r) for n, r in local.items()}
    assert not any((prepared / 'objects').iterdir()) and not any((prepared / 'logs').iterdir())
    head = git(repo, 'rev-parse', 'HEAD')
    def expand(s):
        return Path(s.replace('${LEAN}', str(lean)).replace('${MATHLIB}', str(mathlib)))
    def virtual(p):
        p = Path(p)
        if p.is_relative_to(lean): return '${LEAN}/' + str(p.relative_to(lean))
        if p.is_relative_to(mathlib): return '${MATHLIB}/' + str(p.relative_to(mathlib))
        raise AssertionError(str(p))
    source_roots = [expand(s) for s in lock['ordered_source_roots']]
    object_roots = [expand(s) for s in lock['ordered_object_roots']]
    def direct(path):
        names, prelude = imports(Path(path).read_text())
        return names if prelude else ['Init'] + names
    direct_local = {n: direct(r['path']) for n, r in local_sources.items()}
    def alignment():
        assert git(repo, 'rev-parse', 'HEAD') == head
        for p in package_pins: checked(p['path'], p)
        for p in local_sources.values(): checked(p['path'], p)
        binary = pin(lean / 'bin/lean')
        assert binary['sha256'] == lock['lean_binary_sha256']
        for library in lock['compiler_shared_libraries']:
            checked(expand(library['path']), library)
        assert git(mathlib, 'rev-parse', 'HEAD') == lock['mathlib_head']
        assert not git(mathlib, 'status', '--porcelain')
        for row in lock['packages']:
            path = mathlib / '.lake/packages' / row['name']
            assert git(path, 'rev-parse', 'HEAD') == row['commit']
            assert not git(path, 'status', '--porcelain')
        configs = {n: checked(expand(r['path']), r) for n, r in lock['source_config_pins'].items()}
        done, active, rows = {}, set(), []
        def visit(n):
            if n in done: return
            assert n not in active, 'Import cycle: ' + n
            active.add(n)
            if n in local:
                for dependency in direct_local[n]: visit(dependency)
                active.remove(n); done[n] = None; return
            rel = Path(*n.split('.'))
            sources = [p / rel.with_suffix('.lean') for p in source_roots if (p / rel.with_suffix('.lean')).is_file()]
            objects = [p / rel.with_suffix('.olean') for p in object_roots if (p / rel.with_suffix('.olean')).is_file()]
            assert sources and objects, 'Missing dependency: ' + n
            sp, op = pin(sources[0]), pin(objects[0]); im = direct(sources[0])
            for dependency in im: visit(dependency)
            done[n] = {'module': n, 'source': sp, 'object': op}
            rows.append([n, im, [virtual(sp['path']), sp['bytes'], sp['sha256']],
                [virtual(op['path']), op['bytes'], op['sha256']], [virtual(p) for p in objects]])
            active.remove(n)
        for n in manifest['compile_order']: visit(n)
        rows.sort(key=lambda r: r[0])
        b = json.dumps(rows, separators=(',', ':'), ensure_ascii=False).encode()
        expected = lock['closure']
        assert len(rows) == expected['nodes'] and sum(len(r[1]) for r in rows) == expected['ordered_edges']
        assert len(b) == expected['canonical_bytes'] and hashlib.sha256(b).hexdigest() == expected['sha256']
        return binary, configs, [r for r in done.values() if r is not None]
    binary, configs, external = alignment()
    output.mkdir()
    def write(name, data):
        p = output / name
        with p.open('x') as f: json.dump(data, f, indent=2); f.write('\n')
        return pin(p)
    origin = write('INPUT_ALIGNMENT.json', {'schema': 'portable-hosting-input-alignment-v1',
        'status': 'EXACT_PINNED_INPUTS_NO_COMPILER_YET', 'candidate_head': head,
        'candidate_tree': git(repo, 'rev-parse', 'HEAD^{tree}'), 'mathlib_head': lock['mathlib_head'],
        'packages': lock['packages'], 'source_config_pins': configs, 'closure': lock['closure'],
        'scientific_scope': lock['scientific_scope']})
    execution = output / 'execution'
    sources = []
    for n in manifest['compile_order']:
        op = execution / (n + '.olean')
        sources.append({'module': n, 'source': local_sources[n], 'direct_imports': direct_local[n],
            'output': str(op), 'cwd': str(prepared / 'sources'),
            'command': [str(lean / 'bin/lean'), '-s65536', '-j1', '-o', str(op), local_sources[n]['path']]})
    plan = {'schema': 'portable-hosting-raw-runner-plan-v1', 'owner_worktree': str(repo),
        'owner_source_head': head, 'stage': str(execution), 'compiler_lock': str(a.compiler_lock.resolve()),
        'runtime': {'binary': binary, 'installed_receipt': origin, 'import_receipt': origin,
                    'external_direct_roots': external}, 'sources': sources, 'retained_roots': [],
        'retained_evidence': package_pins + [pin(HERE / n) for n in ['LOCK.json', 'replay.py', 'run_native.py']]
            + [{**r, 'path': str(expand(r['path']))} for r in lock['compiler_shared_libraries']],
        'source_reviews': [], 'environment': {'LEAN_SYSROOT': str(lean),
            'LEAN_PATH': ':'.join(map(str, [execution] + object_roots)), 'LEAN_NUM_THREADS': '1',
            'MIMALLOC_ARENA_RESERVE': '64MiB'}, 'limits': lock['limits'],
        'qualification': 'Input alignment is a source/object/hash guard, not a fabricated smoke-compile receipt.'}
    pp = write('PLAN.json', plan)
    print(json.dumps({'status': 'EXACT_PLAN_PREPARED', 'plan': pp, 'compiler_requested': a.run}), flush=True)
    if not a.run: return
    env = {k: v for k, v in os.environ.items() if not k.startswith('LEAN_')}
    env.update({'GIT_NO_LAZY_FETCH': '1', 'GIT_TERMINAL_PROMPT': '0'})
    code = subprocess.run([sys.executable, str(HERE / 'run_native.py'), pp['path'], pp['sha256']], env=env).returncode
    assert code == 0
    raw = json.loads((execution / 'RECEIPT.json').read_text())
    assert raw['status'] == 'RAW_COMPILERS_COMPLETE' and len(raw['roots']) == 3
    alignment()  # Independent complete path/import/hash readback; no second compiler.
    for expected, actual in zip(reference['modules'], raw['roots']):
        assert actual['module'] == expected['module'] and actual['exit_code'] == 0 and actual['limit_failure'] is None
        for k in ['source', 'object', 'stdout', 'stderr']: checked(actual[k]['path'], expected[k])
        text = Path(actual['stdout']['path']).read_text()
        print(text, end='', flush=True)
        for probe in expected['ordered_probes']:
            expected_line = "'" + probe['declaration'] + "'" + (" depends on axioms: [" + ", ".join(probe['axioms']) + "]" if probe['axioms'] else " does not depend on any axioms")
            assert expected_line in text
        for typ in expected['printed_types']: assert typ['raw_type'] in text
    accepted = write('ACCEPTANCE.json', {'status': 'PASS_EXACT_HOSTING_REPLAY', 'candidate_head': head,
        'candidate_tree': git(repo, 'rev-parse', 'HEAD^{tree}'), 'plan': pp,
        'raw_receipt': pin(execution / 'RECEIPT.json'), 'expected_reference': pin(package / 'ACCEPTED_CHECKS.json'),
        'closure': lock['closure'], 'source_scope': lock['scientific_scope'],
        'compiler_phase_seconds': raw['resource_phase_seconds'], 'independent_human_review': 'Still separate.'})
    print(json.dumps(accepted), flush=True)

if __name__ == '__main__':
    main()
