"""Fresh scoped row/query producer proof replay. intqwq; Codex assistance.
Apache-2.0. No physical query invoice or increased kappa is formalized.
"""
from hashlib import sha256
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert sys.version_info[:2] == (3, 14)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',type=Path,default=HERE/'lean-runtime')
    parser.add_argument('--lake',type=Path)
    args=parser.parse_args()
    runtime=args.runtime.resolve()
    helper = HERE / 'inputs/verify_lean.py'
    assert digest(helper) == '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
    spec = importlib.util.spec_from_file_location('round8_query_auditor', helper)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.HERE=runtime
    original_capture=audit.capture
    audit.capture=lambda argv,**kw: original_capture(argv,cwd=kw.pop('cwd',runtime),**kw)
    configurations={name:digest(HERE/'lean-runtime'/name) for name in ['lean-toolchain','lakefile.toml','lake-manifest.json']}
    assert all(digest(runtime/name)==pin for name,pin in configurations.items())
    bundled=runtime/'.toolchain/lean-4.21.0-windows/bin/lake.exe'
    lake=args.lake or (bundled if bundled.exists() else shutil.which('lake'))
    assert lake, 'Install Lean4.21.0 lake or specify --lake'
    lean, env, versions = audit.environment(str(lake))
    assert digest(lean) == 'fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
    paths = []
    for entry in env['LEAN_PATH'].split(os.pathsep):
        if entry:
            p = Path(entry)
            paths.append(str(p if p.is_absolute() else (runtime / p).resolve()))
    env['LEAN_PATH'] = os.pathsep.join([str(HERE), *paths])
    source = HERE / 'QueryProducer.lean'
    source_hash = digest(source)
    expected = audit.audit_source(source)
    assert len(expected) == 5
    obj, log = source.with_suffix('.olean'), source.with_suffix('.log')
    command = [lean, '--root=' + str(HERE), '-o', str(obj), str(source)]
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=HERE, env=env, stdout=output,
                                stderr=subprocess.STDOUT, timeout=90)
    assert result.returncode == 0, log.read_text(encoding='utf-8').encode('ascii', 'backslashreplace').decode()
    assert digest(source) == source_hash
    axioms = audit.parse_axioms(log, expected)
    receipt = dict(status='PASS_LEAN_SCOPED_RECURSIVE_QUERY_PRODUCER', author='intqwq', new_kappa=False,
                   source=source.name, source_sha256=source_hash, object_sha256=digest(obj),
                   log_sha256=digest(log), actual_reports=axioms, allowed_axioms=sorted(audit.ALLOW),
                   exit_code=0, command=command, runtime=versions, auditor_sha256=digest(helper),
                   runtime_configurations_sha256=configurations,
                   replay_sha256=digest(__file__),
                   scope='All-input additive row/column producer identity, dirty return and exact split algebra. '
                         'No new row-query price, full physical recurrence, rounded implementation or kappa proof.')
    (HERE / 'LEAN-VERIFICATION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n',
                                               encoding='utf-8', newline='\n')
    print(receipt['status'], len(axioms), 'reports')


if __name__ == '__main__':
    main()
