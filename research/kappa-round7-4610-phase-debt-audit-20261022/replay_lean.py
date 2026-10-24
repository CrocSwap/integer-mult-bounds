"""Fresh pinned kernel replay for Cinna Davis's finite-list rank-debt argument.
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


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert sys.version_info[:2] == (3, 14)
    runtime = ROOT / 'research/kappa-lean-verification-20261022'
    helper = runtime / 'verify_lean.py'
    assert digest(helper) == '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
    spec = importlib.util.spec_from_file_location('rank_debt_pinned_auditor', helper)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    lean, env, versions = audit.environment(str(runtime / '.toolchain/lean-4.21.0-windows/bin/lake.exe'))
    assert digest(lean) == 'fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab'
    paths = []
    for part in env['LEAN_PATH'].split(os.pathsep):
        if part:
            p = Path(part)
            paths.append(str(p if p.is_absolute() else (runtime / p).resolve()))
    env['LEAN_PATH'] = os.pathsep.join([str(HERE), *paths])
    source = HERE / 'RankDebt.lean'
    source_hash = digest(source)
    expected = audit.audit_source(source)
    assert len(expected) == 5
    obj, log = source.with_suffix('.olean'), source.with_suffix('.log')
    command = [lean, '--root=' + str(HERE), '-o', str(obj), str(source)]
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=HERE, env=env, stdout=output,
                                stderr=subprocess.STDOUT, timeout=120)
    assert result.returncode == 0, log.read_text(encoding='utf-8').encode('ascii', 'backslashreplace').decode()
    assert digest(source) == source_hash
    axioms = audit.parse_axioms(log, expected)
    receipt = dict(status='PASS_LEAN_SCOPED_FINITE_LIST_RANK_DEBT', author='Cao Yifan',
                   argument_credit='Cinna Davis, PR4696 def829364e8e53a74eac7997b49b5366afd5bc29',
                   source=source.name, source_sha256=source_hash,
                   object_sha256=digest(obj), log=log.name, log_sha256=digest(log),
                   axiom_reports=axioms, allowed_axioms=sorted(audit.ALLOW),
                   expected_reports=expected, exit_code=0, command=command,
                   runtime=versions, auditor_sha256=digest(helper), replay_sha256=digest(__file__),
                   scope='Generic concave-increment and arbitrary finite-list rank-debt inequality. '
                         'Native symmetric-form rank grammar, source-specific block hypotheses, '
                         'zero-rank job counting at t=0, physical execution and full compiler remain separate.')
    (HERE / 'LEAN-VERIFICATION.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(receipt['status'], len(expected), 'reports')


if __name__ == '__main__':
    main()
