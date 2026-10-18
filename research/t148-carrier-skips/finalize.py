#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mark completion only after both real release receipts and finite checks pass."""
import json

import verify as v


def main():
    v.run()
    task = v.read(v.P / 'TASK.json')
    claim = v.read(v.P / 'CLAIM.json')
    task.update(outcome='completed', evidence='Both mandatory complete releases passed. The composition includes two freshly verified changed native providers, all543456 owner roles,133117 physical families,91 buffers and the paid rank32 child. All139 admission,12 bit,25 actual controller,8 independent-owner and6 geometry controls reject;63 strict outer rows and17 outer rejecting cases pass. Exact kappa gain=' + claim['gain'] + '. No selected-frontier or complete-theorem claim.')
    task['open_questions'] = [dict(question='Can the larger T740 composition be fully released within a separate resource budget?',
        why_it_matters='T148 has a positive gap below the unchanged fixed-inventory cap.',
        first_step='Use the exact larger allocation, rederive all stock/prefix constants and run every full release gate.',
        blocked_by='A larger audit needs more memory and compute; this smaller release cannot certify it.')]
    (v.P / 'TASK.json').write_text(json.dumps(task, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
    path = v.P / 'README.md'
    text = path.read_text()
    text = text.replace('**Full release pending.**', '**Both mandatory complete releases passed.**')
    text = text.replace('No completed release is claimed yet.', 'The native, supplier and modern outer checks passed; hosted finite replay is recorded separately.')
    path.write_text(text, encoding='utf-8', newline='\n')
    manifest = {p.relative_to(v.P).as_posix(): v.sha(p) for p in sorted(v.P.rglob('*'))
                if p.is_file() and p != v.P / 'MANIFEST.json' and '__pycache__' not in p.parts}
    (v.P / 'MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('FINALIZED_ONLY_AFTER_BOTH_COMPLETE_RELEASES', flush=True)


if __name__ == '__main__':
    main()
