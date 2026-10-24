"""Source-specific audit of PR4696 and the inert-adapter relaxation.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
Analytic argument and upstream checker credited to Cinna Davis.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    need(sys.version_info[:2] == (3, 14), 'Global Python 3.14')
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['files']:
        need(digest(HERE / row['copy']) == row['sha256'], 'Pinned upstream bytes: ' + row['copy'])
    upstream = load('phase_rank_debt_upstream_exact', HERE / 'upstream/verify.py')
    run = subprocess.run([sys.executable, '-I', '-B', 'verify.py'], cwd=HERE / 'upstream',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    need(run.returncode == 0, run.stdout.decode(errors='replace'))
    payload = json.loads(gzip.decompress((HERE / 'upstream/inputs/round3-native.json.gz').read_bytes()))
    original = upstream.audit(payload)
    without = deepcopy(payload)
    markers = {}
    for direction, word in without['programs'].items():
        adapters = [e for e in word if e[0] == 'adapter']
        roles = sorted({e[2] for e in adapters})
        need(len(adapters) == 448 and roles == list(range(224)), 'Adapters are exclusively main-field markers')
        markers[direction] = dict(count=len(adapters), main_roles=roles, helper_roles=[])
        without['programs'][direction] = [e for e in word if e[0] != 'adapter']
    relaxed = upstream.audit(without)
    for direction in original:
        before, after = deepcopy(original[direction]), deepcopy(relaxed[direction])
        need(before['events'].pop('adapter') == 448, 'Original marker count')
        need(before == after, 'Deleting inert markers altered a rank-debt hypothesis')
        need(before['helper_contact_blocks_by_original_paid_calls'] == {'0': 19817, '1': 2208}
             or before['helper_contact_blocks_by_original_paid_calls'] == {0: 19817, 1: 2208},
             'Exact helper block counts')
    # The formal receipt is checked from actual source/log/object bytes.
    receipt = json.loads((HERE / 'LEAN-VERIFICATION.json').read_text(encoding='utf-8'))
    for key, name in [('source_sha256', 'RankDebt.lean'), ('object_sha256', 'RankDebt.olean'),
                      ('log_sha256', 'RankDebt.log'), ('replay_sha256', 'replay_lean.py')]:
        need(digest(HERE / name) == receipt[key], 'Fresh scoped Lean binding: ' + name)
    auditor = ROOT / 'research/kappa-lean-verification-20261022/verify_lean.py'
    need(digest(auditor) == receipt['auditor_sha256'] == '6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895',
         'Pinned Lean auditor')
    audit = load('phase_rank_debt_axiom_auditor', auditor)
    expected = audit.audit_source(HERE / 'RankDebt.lean')
    actual = audit.parse_axioms(HERE / 'RankDebt.log', expected)
    need(len(actual) == 5 and actual == receipt['axiom_reports'], 'Actual five kernel reports')
    result = dict(status='PASS_SCOPED_PHASE_RANK_DEBT_SOURCE_AUDIT', author='Cao Yifan', new_kappa=False,
                  upstream_commit='def829364e8e53a74eac7997b49b5366afd5bc29',
                  upstream_stdout=run.stdout.decode().strip(),
                  upstream_stdout_sha256=sha256(run.stdout).hexdigest(),
                  source_manifest_sha256=digest(HERE / 'SOURCES.json'),
                  script_sha256=digest(__file__), lean_receipt_sha256=digest(HERE / 'LEAN-VERIFICATION.json'),
                  adapter_markers=markers, original_hypotheses=original,
                  inert_marker_removal_preserves_all_other_hypotheses=True,
                  allowed_axioms=sorted(audit.ALLOW), actual_lean_reports=5,
                  scope='Source-specific path hypotheses plus generic finite-list analytic Lean proof. '
                        'Native phase rank grammar remains conditional. No fixed-subspace obstruction '
                        'is claimed for rank-changing active-mask frames, shared paid operations, '
                        'fusion across scalar contacts, changed main contracts or new center protocols.')
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print(result['status'], 'both orientations; inert markers main-only; 5 Lean reports; no new kappa')


if __name__ == '__main__':
    main()
