"""Check a terminal full PR236 build and emit an integrity/axiom receipt.

Does not run Lean or turn partial receipts into a full result. The build lock
must be released and the original driver must report the complete accepted set.
Uses that audited driver's source-plan and axiom parsers, then independently
reconstructs the complete receipt/dependency/hash accounting.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--map', required=True, type=Path)
    parser.add_argument('--driver', required=True, type=Path)
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    build = args.build.resolve()
    with (build/'build.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('BUILD_STILL_RUNNING: no final receipt written')
            return 3
        summary = json.loads((build/'SUMMARY.json').read_text())
        check(summary.get('status') == 'FULL_ACCEPTED_SET_COMPILED', 'No completed full build')
        check(summary.get('kernel_compiled') is True and summary.get('full_accepted_set') is True,
              'Summary does not assert a full kernel build')
        spec = importlib.util.spec_from_file_location('pr236_audited_driver', args.driver)
        driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(driver)
        plan, modules, dependencies, order, map_hash = driver.load_plan(args.map, args.source_root)
        compiler = driver.toolchain_identity(args.lean.resolve())
        check(summary['map_sha256'] == map_hash, 'Map changed')
        check(summary['source_commit'] == plan['target_commit'], 'Wrong scientific target')
        check(summary['compiler'] == compiler, 'Compiler identity changed')
        check(summary['accepted_modules'] == summary['selected_modules'] == len(modules), 'Module coverage')
        check(summary['selected_declarations'] == plan['accepted_declarations'], 'Declaration coverage')
        check(set(summary['receipts']) == set(modules), 'Summary receipt coverage')
        visited = summary['rebuilt'] + summary['reused']
        check(len(visited) == len(set(visited)) == len(modules) and set(visited) == set(modules),
              'Rebuilt/reused coverage')
        check({p.stem for p in (build/'receipts').glob('*.json')} == set(modules), 'On-disk receipt coverage')
        done = {}
        declarations = axiom_free = 0
        used_axioms = set()
        for name in order:
            m = modules[name]
            receipt = json.loads((build/'receipts'/f'{name}.json').read_text())
            check(receipt['status'] == 'PASS' and receipt['compiler_exit'] == 0, f'Compiler failure: {name}')
            check(receipt['module'] == name and receipt['map_sha256_when_built'] == map_hash,
                  f'Receipt identity: {name}')
            object_path = build/'objects'/(name.replace('.', '/')+'.olean')
            source_path = build/'sources'/(name.replace('.', '/')+'.lean')
            log_path = build/'logs'/f'{name}.log'
            check(sha(source_path) == m['source_sha256'], f'Compiled source changed: {name}')
            check(sha(object_path) == receipt['object_sha256'], f'Object changed: {name}')
            check(sha(log_path) == receipt['log_sha256'], f'Log changed: {name}')
            expected_key = dict(policy=driver.POLICY, compiler=compiler,
                source_sha256=m['source_sha256'], imports=m['imports'],
                expected_axiom_commands=m['expected_axiom_commands'],
                dependencies={n:done[n]['object_sha256'] for n in dependencies[name]},
                timeout_seconds=m.get('timeout_seconds',60), address_space_bytes=None,
                lean_jobs=1, lean_stack_kib=65536, allowed_axioms=sorted(driver.ALLOWED_AXIOMS))
            check(receipt['build_key'] == expected_key, f'Build/dependency policy changed: {name}')
            audit = driver.audit_output(log_path.read_text(), m['expected_axiom_commands'])
            check(receipt['audit'] == audit, f'Axiom receipt changed: {name}')
            check(hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
                  == summary['receipts'][name], f'Summary binding changed: {name}')
            declarations += audit['declarations']
            axiom_free += audit['axiom_free']
            used_axioms.update(audit['axioms'])
            done[name] = receipt
        check(declarations == plan['accepted_declarations'], 'Audited declaration coverage')
        result = dict(status='FULL_KERNEL_RECEIPTS_REVALIDATED', accepted_modules=len(done),
            audited_declarations=declarations, axiom_free_declarations=axiom_free,
            allowed_axioms=sorted(driver.ALLOWED_AXIOMS), observed_axioms=sorted(used_axioms),
            source_commit=plan['target_commit'], map_sha256=map_hash,
            summary_sha256=sha(build/'SUMMARY.json'), driver_sha256=sha(args.driver),
            compiler=compiler, address_space_bytes=None,
            resource_policy='Darwin audit adapter; no address-space cap; original per-module timeouts',
            reused_modules=summary['reused'], rebuilt_modules=len(summary['rebuilt']),
            scope=plan['scope'], installed_standard_library_rebuilt=False)
        args.receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(result,indent=2,sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
