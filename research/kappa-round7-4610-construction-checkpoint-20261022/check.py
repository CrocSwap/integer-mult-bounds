"""Source/log inventory seal for the round-seven research checkpoint.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
This does not replace the individual Lean or native replays.
"""
from hashlib import sha256
import argparse
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGES = [
    'kappa-round7-4610-review-20261022',
    'kappa-round7-4610-frontier-review-20261022',
    'kappa-round7-4610-scalar-contract-20261022',
    'kappa-round7-4610-independent-audit-20261022',
    'kappa-round7-4610-phase-recursion-20261022',
    'kappa-round7-4610-coupled-recursion-20261022',
    'kappa-round7-4610-phase-debt-audit-20261022',
    'kappa-round7-rankone-phase-20261022',
    HERE.name,
]
MODULES = [
    ('kappa-round7-4610-scalar-contract-20261022', 'Preprocessing', 4),
    ('kappa-round7-4610-independent-audit-20261022', 'PhasePreprocess', 3),
    ('kappa-round7-4610-phase-recursion-20261022', 'RankGate', 5),
    ('kappa-round7-4610-phase-recursion-20261022', 'ParallelControls', 2),
    ('kappa-round7-4610-phase-recursion-20261022', 'GroupedPhase', 4),
    ('kappa-round7-4610-phase-recursion-20261022', 'ActivePalette', 4),
    ('kappa-round7-4610-coupled-recursion-20261022', 'PauliHole', 2),
    ('kappa-round7-4610-phase-debt-audit-20261022', 'RankDebt', 5),
]
PRIVATE = {'.scratch', '.solver', '.lean-build', '__pycache__', '.toolchain', '.lake'}
BASELINE = [
    'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
    'research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json',
    'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json',
    'research/kappa-round6-compiler-tightening-20261022/LEAN-VERIFICATION.json',
]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def inventory():
    result = {}
    for name in PACKAGES:
        for path in sorted((ROOT/'research'/name).rglob('*')):
            if not path.is_file() or PRIVATE.intersection(path.parts):
                continue
            if path.suffix in {'.olean', '.ilean', '.pyc'} or path == HERE/'CHECKPOINT.json':
                continue
            result[path.relative_to(ROOT).as_posix()] = digest(path)
    return result


def main():
    if not __debug__:
        raise ValueError('Run integrity checks with assertions enabled')
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--objects', action='store_true')
    args = parser.parse_args()
    auditor = ROOT/'research/kappa-lean-verification-20261022/verify_lean.py'
    assert digest(auditor) == '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
    spec = importlib.util.spec_from_file_location('round7_seal_auditor', auditor)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    modules = []
    for folder, name, count in MODULES:
        path = ROOT/'research'/folder/(name+'.lean')
        log = path.with_suffix('.log')
        expected = audit.audit_source(path)
        reports = audit.parse_axioms(log, expected)
        assert len(reports) == count
        modules.append(dict(source=path.relative_to(ROOT).as_posix(),
                            source_sha256=digest(path), log_sha256=digest(log),
                            reports=reports))
    target = HERE/'CHECKPOINT.json'
    if args.freeze:
        assert not target.exists(), 'Do not overwrite a frozen checkpoint'
        frozen_modules = [{**row, 'olean_sha256':digest((ROOT/row['source']).with_suffix('.olean'))}
                          for row in modules]
        value = dict(status='FROZEN_SCOPED_PHASE_RESEARCH_CHECKPOINT', new_kappa=False,
                     claimed_kappa='0.0030217758', modules=frozen_modules,
                     fresh_modules=8, exported_axiom_reports=29,
                     files_sha256=inventory(),
                     baseline_sha256={name:digest(ROOT/name) for name in BASELINE},
                     scope='Source/log/optional-object integrity only; individual receipts '
                           'record fresh Lean runs. No new kappa or complete supplier.')
        target.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n',
                          encoding='utf-8', newline='\n')
    value = json.loads(target.read_text(encoding='utf-8'))
    assert value['files_sha256'] == inventory(), 'Checkpoint source/receipt bytes changed'
    assert all(digest(ROOT/name) == h for name, h in value['baseline_sha256'].items())
    assert len(modules) == value['fresh_modules'] == 8
    assert sum(len(row['reports']) for row in modules) == value['exported_axiom_reports'] == 29
    for current, frozen in zip(modules, value['modules']):
        assert current == {k:v for k,v in frozen.items() if k != 'olean_sha256'}
        if args.objects:
            assert digest((ROOT/current['source']).with_suffix('.olean')) == frozen['olean_sha256']
    print('PASS_ROUND7_CHECKPOINT_INTEGRITY', len(value['files_sha256']),
          'files; 8 fresh modules/29 axiom reports; kappa unchanged')


if __name__ == '__main__':
    main()
