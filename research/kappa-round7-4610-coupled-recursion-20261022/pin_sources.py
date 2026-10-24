"""Pin the changed native and Pauli interfaces without modifying predecessors.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATHS = [
    'research/kappa-round5-coupled-main-20261022/README.md',
    'research/kappa-round5-coupled-main-20261022/caller_probe.py',
    'research/kappa-round5-coupled-main-20261022/CALLER-PROBES.json.gz',
    'research/kappa-round5-coupled-main-20261022/lift_native.py',
    'research/kappa-round5-coupled-main-20261022/involutive_lift.py',
    'research/kappa-round5-coupled-main-20261022/INVOLUTIVE-LIFT.json',
    'research/kappa-round5-coupled-main-20261022/INVOLUTIVE-WORD.json.gz',
    'research/kappa-round5-coupled-main-20261022/InvolutiveLift.lean',
    'research/kappa-round6-query-normalizer-20261022/README.md',
    'research/kappa-round6-query-normalizer-20261022/PauliPair.lean',
    'research/kappa-round6-query-normalizer-20261022/REAL-GAUGE.json',
    'research/kappa-round6-query-normalizer-20261022/layout-audit/README.md',
    'research/kappa-round6-query-normalizer-20261022/layout-audit/Fanout.lean',
    'research/kappa-round6-query-normalizer-20261022/layout-audit/LAYOUT-AUDIT.json',
    'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/native_common.py',
    'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/certificate.json.gz',
    'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json',
    'research/kappa-rebuild/controller/frame_exchange.py',
    'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
    'research/warp-interface-20261022/verify_candidate.py',
    'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
]


def main():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    rows = []
    for name in PATHS:
        raw = (ROOT / name).read_bytes()
        old = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
        if raw != old:
            raise ValueError('Predecessor has uncommitted bytes: ' + name)
        target = HERE / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        blob = subprocess.check_output(['git', 'rev-parse', commit + ':' + name], cwd=ROOT, text=True).strip()
        rows.append(dict(path=name, copy=target.relative_to(HERE).as_posix(),
                         git_commit=commit, git_blob=blob, sha256=sha256(raw).hexdigest()))
    (HERE / 'SOURCES.json').write_text(json.dumps(dict(files=rows), indent=2) + '\n', encoding='utf-8')
    print('PINNED_COUPLED_PAULI_INPUTS', len(rows), commit)


if __name__ == '__main__':
    main()
