#!/usr/bin/env python3
"""Recheck the pinned PR442 source and bit-window fixture, entirely offline.

This is a Python source-binding check, not a kernel verification of JSON
parsing, the complete template, or the inherited physical compiler interface.
The Lean replay separately checks the literal interval/operator theorems.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent
PIN = '4e16d001d505d4f21dd2bcfc44591f9be4c279bd'
SOURCE_FILES = {
    'research/idle-axis-hosting/PROOF.md',
    'research/idle-axis-hosting/hosting_core.py',
    'research/idle-axis-hosting/bit_hosted.py',
    'research/idle-axis-hosting/SELECTION.json',
    'research/e8-early-reset-kernel/bit_global.py',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def check_lean_intervals(selected, slots):
    """Bind the literal masks; theorem checking remains the Lean replay's job."""
    text = ' '.join((ROOT / 'PinnedWindow.lean').read_text().split())
    pending = re.search(
        r'def pending : Mask \(Fin (\d+)\) := interval (\d+) (\d+)', text)
    require(pending is not None, 'Cannot locate the literal pending mask')
    require(tuple(map(int, pending.groups())) ==
            (selected['ambient_dimension'], 0, selected['pending_rank']),
            'Lean pending mask differs from the selected source window')
    residuals = re.search(
        r'def residualMasks : List \(Mask \(Fin (\d+)\)\) := \[(.*?)\]', text)
    require(residuals is not None, 'Cannot locate the literal residual masks')
    require(int(residuals.group(1)) == selected['ambient_dimension'],
            'Lean residual ambient dimension differs')
    intervals = []
    for item in residuals.group(2).split(','):
        interval = re.fullmatch(r'\s*interval (\d+) (\d+)\s*', item)
        require(interval is not None, 'Residual mask is not a literal interval')
        intervals.append(tuple(map(int, interval.groups())))
    expected = [(row['offset'], row['offset'] + row['width']) for row in slots]
    require(intervals == expected,
            'Lean residual intervals differ from representative source order')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path,
                        help='PR442 checkout or source tree at the pinned revision')
    parser.add_argument('--template', required=True, type=Path,
                        help='freshly replayed bit/GLOBAL-TEMPLATE.json.gz')
    parser.add_argument('--receipt', type=Path, default=ROOT / 'pinned-window.json',
                        help='extraction receipt (default: bundled pinned-window.json)')
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_bytes())
    require(receipt['source_pr'] == 442 and receipt['source_commit'] == PIN,
            'Unexpected source revision in extraction receipt')
    require(set(receipt['source_sha256']) == SOURCE_FILES,
            'The receipt must pin exactly the five inspected source files')
    for relative, expected_hash in receipt['source_sha256'].items():
        data = (args.source_root / relative).read_bytes()
        require(sha256(data) == expected_hash, 'Source hash mismatch: ' + relative)

    compressed = args.template.read_bytes()
    # The raw JSON is the source identity. Gzip metadata/encoders can differ
    # across Python versions while decompressing to exactly those pinned bytes.
    same_gzip = sha256(compressed) == receipt['template_gzip_sha256']
    raw = gzip.decompress(compressed)
    require(sha256(raw) == receipt['template_json_sha256'],
            'Raw template JSON hash mismatch')
    template = json.loads(raw)
    selected = receipt['selected']
    require(selected == {
        'child': 2, 'copy': 27, 'replica': 0, 'pair': 2, 'side': 0,
        'port': 27, 'family': 507, 'ambient_dimension': 64,
        'pending_rank': 28, 'source_level': -1, 'target_level': 3,
        'remainder_rank': 0, 'window_stages': [0, 1, 2, 3],
        'child_schedule_position': 8,
    }, 'Unexpected selected fixture')
    child, copy, pair = selected['child'], selected['copy'], selected['pair']
    require(template['m'] == selected['ambient_dimension'], 'Ambient dimension differs')
    require(template['hosting']['windows'][str(child)] ==
            [pair, selected['pending_rank'], selected['window_stages']],
            'Stored hosting window differs')
    rows = [row for row in template['hosting']['slots']
            if row[0] == child and row[1] == copy]
    require(rows == receipt['slots_in_source_order'], 'Selected slot rows differ')
    ordered = sorted(rows, key=lambda row: (row[4], row[2]))
    witnesses = receipt['slots_in_representative_stage_order']
    require(len(ordered) == len(witnesses) == 4, 'Four whole residuals required')
    covered = set()
    for row, witness in zip(ordered, witnesses):
        _, _, offset, width, stage, helper = row
        require((stage, helper, offset, width) ==
                (witness['stage'], witness['helper'], witness['offset'], witness['width']),
                'Representative slot descriptor differs')
        require(witness['local_register'] == 240 + helper,
                'Helper/local-register numbering differs')
        require(width == 8 - witness['entrance_rank'],
                'Residual width differs from the receipt entrance rank')
        calls = [call for call in template['calls']
                 if call['stage'] == stage and call['replica'] == selected['replica']]
        require(len(calls) == 1, 'Selected invocation is missing or duplicated')
        call = calls[0]
        require(call['pair'] == witness['active_pair'] != pair and
                call['orientation'] == witness['orientation'],
                'Invocation pair/orientation differs or touches the host pair')
        expected_owner = [selected['family'], ['hosted', child, offset, width]]
        require(call['owners'][240 + helper] == witness['owner'] == expected_owner,
                'Whole single-family owner descriptor differs')
        cells = set(range(offset, offset + width))
        require(width > 0 and offset >= 0 and not (covered & cells),
                'Empty, negative, or overlapping residual interval')
        require(cells <= set(range(selected['pending_rank'])),
                'Residual extends outside the pending child')
        covered.update(cells)
    require(covered == set(range(selected['pending_rank'])),
            'Residuals do not exactly cover the pending child')

    schedule = template['schedule']
    position = selected['child_schedule_position']
    require(schedule[:position] == receipt['schedule_before_child'] and
            schedule[position] == receipt['child_event'],
            'Selected source schedule differs')
    require(schedule[position] == {
        'idx': child, 'kind': 'idle', 'pair': pair,
        'rank': selected['pending_rank'],
        'source_level': selected['source_level'],
        'target_level': selected['target_level'],
    }, 'Selected child event differs')
    stages = []
    for event in schedule[:position]:
        if event['kind'] == 'local_cover_sweep':
            require(event['pair'] != pair, 'Intervening local invocation touches host pair')
            stages.append(event['stage'])
        elif event['kind'] == 'bridge':
            require(pair not in (event['src'], event['dst']),
                    'Intervening bridge touches host pair')
        elif event['kind'] == 'idle':
            require(event['pair'] != pair,
                    'This fixture requires intervening idle events on other pairs')
        else:
            raise ValueError('Unexpected intervening schedule event')
    require(stages == selected['window_stages'], 'Re-derived window stages differ')
    for key, receipt_key in [('bit_operator', 'operator_description'),
                             ('cover', 'cover_description'), ('loop_order', 'loop_order')]:
        require(template[key] == receipt[receipt_key], 'Source interface text differs: ' + key)
    check_lean_intervals(selected, witnesses)
    print(json.dumps({
        'status': 'PASS_PINNED_SOURCE_WINDOW', 'source_commit': PIN,
        'source_files_checked': len(SOURCE_FILES),
        'template_json_sha256': sha256(raw), 'child': child,
        'matches_recorded_gzip_bytes': same_gzip,
        'family': selected['family'], 'whole_residuals_checked': len(rows),
        'scope': 'Offline Python source binding; Lean checks the literal mask theorems separately.',
    }, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, IndexError, OSError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        sys.exit(1)
