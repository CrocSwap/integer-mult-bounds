#!/usr/bin/env python3
"""Replay Chafik's T21 composition with the strengthened ancestor admission.

Credits: PR890 Chafik Boukhalfa; PR869/870 Jeremy Kothe; PR858 Hao Yan;
PR838/847/851/865 evidence coverage contributors. Maintainer adapter by
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_replay_coverage import check_selected, require


def check(work, baseline, ancestor):
    parent = check_selected(baseline, ancestor)
    package = ROOT / 'research/complex-t21-owners'
    sys.path.insert(0, str(package))
    spec = importlib.util.spec_from_file_location('frontier890_supplier', package / 'verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    recorded = module.read(work / 'RESULT.json')
    require(recorded['baseline_mode'] in ('explicit_checked_reuse', 'cold_rebuilt'), 'Invalid baseline reuse mode')
    result = module.final_binding(work, module.read(work / 'STAGES.json'),
                                  module.validate_pins(), recorded['baseline_mode'] == 'explicit_checked_reuse',
                                  baseline, ancestor)
    require(json.dumps(result, sort_keys=True) == json.dumps(recorded, sort_keys=True),
            'Stored T21 result differs from its checked evidence')
    return dict(status='PASS_COMPLETE_PR890_COMPOSITION', kappa=result['kappa'],
                decimal=result['kappa_decimal'], selected_binding=result,
                ancestor_coverage=parent,
                scope='Finite construction and evidence admission; inherited all-size/compiler, '
                      'realization, hosting, precision/tape and analytic assumptions remain.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--baseline799', type=Path)
    p.add_argument('--ancestor741', type=Path)
    p.add_argument('--check-only', action='store_true', help='Check an existing raw T21 replay; do not execute suppliers')
    p.add_argument('--out', type=Path, help='Optional check-only receipt')
    a = p.parse_args()
    require(not sys.flags.optimize, 'Supplier workers require assertions')
    require((a.baseline799 is None) == (a.ancestor741 is None), 'Provide both reuse paths or neither')
    work = a.work.resolve()
    raw = work if a.check_only else work / 'replay'
    baseline = a.baseline799.resolve() if a.baseline799 else raw / 'baseline799'
    ancestor = a.ancestor741.resolve() if a.ancestor741 else baseline / 'ancestor'
    if not a.check_only:
        require(not work.exists() and not work.is_relative_to(ROOT), 'Use fresh external output')
        if a.baseline799:
            check_selected(baseline, ancestor)
        work.mkdir(parents=True)
        command = [sys.executable, '-B', str(ROOT / 'research/complex-t21-owners/verify.py'),
                   '--work', str(raw)]
        if a.baseline799:
            command += ['--baseline799', str(baseline), '--ancestor741', str(ancestor)]
        subprocess.run(command, check=True, cwd=ROOT)
    result = check(raw, baseline, ancestor)
    output = a.out if a.check_only else work / 'RESULT.json'
    if output:
        temporary = output.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(result, indent=2) + '\n')
        temporary.replace(output)
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()
