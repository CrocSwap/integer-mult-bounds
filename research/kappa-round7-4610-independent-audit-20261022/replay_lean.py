"""Fresh pinned Lean replay for the independent moment lemma only.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def main():
    runtime = ROOT/'research/kappa-lean-verification-20261022'
    helper = runtime/'verify_lean.py'
    assert digest(helper) == '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
    spec = importlib.util.spec_from_file_location('independent_lean_auditor', helper)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    lake = runtime/'.toolchain/lean-4.21.0-windows/bin/lake.exe'
    lean, env, versions = audit.environment(str(lake))
    assert digest(lean) == 'fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
    paths = []
    for part in env['LEAN_PATH'].split(os.pathsep):
        if part:
            path = Path(part)
            paths.append(str(path if path.is_absolute() else (runtime/path).resolve()))
    env['LEAN_PATH'] = os.pathsep.join([str(HERE), *paths])
    source = HERE/'PhasePreprocess.lean'
    source_hash = digest(source)
    expected = audit.audit_source(source)
    assert len(expected) == 3
    obj = HERE/'PhasePreprocess.olean'
    log = HERE/'PhasePreprocess.log'
    command = [lean, '--root='+str(HERE), '-o', str(obj), str(source)]
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=HERE, env=env, stdout=output,
                                stderr=subprocess.STDOUT, timeout=180)
    assert result.returncode == 0, log.read_text(encoding='utf-8').encode('ascii', 'backslashreplace').decode()
    assert digest(source) == source_hash
    axioms = audit.parse_axioms(log, expected)
    receipt = dict(status='PASS_LEAN_SCOPED_HELPER_PREPROCESSING_LOSS',
                   source=source.name, source_sha256=source_hash,
                   object_sha256=digest(obj), log=log.name, log_sha256=digest(log),
                   axiom_reports=axioms, allowed_axioms=sorted(audit.ALLOW),
                   expected_reports=expected, exit_code=0, command=command,
                   runtime=versions, auditor_sha256=digest(helper),
                   replay_sha256=digest(__file__),
                   scope='Strict concavity proves no gain from one isolated helper '
                         'preprocessing charge. Native support classification, absolute '
                         'phase, full compiler and kappa remain separate obligations.')
    (HERE/'LEAN-VERIFICATION.json').write_text(json.dumps(receipt, indent=2)+'\n',
                                            encoding='utf-8', newline='\n')
    print(receipt['status'], len(expected), 'reports')


if __name__ == '__main__':
    main()
