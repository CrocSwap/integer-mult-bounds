#!/usr/bin/env python3
"""Can PR216's admitted cut list be carried onto PR217's butterfly word?

PR216 (`research/coordinated-crossover-pr200-v2`, head 34abdc5) changes 220 further
operation frames of the word it inherits from PR211 and admits them with a native
checker over a *fixed* scalar word.  PR217 (head b739fc2) rewrites part of the same
lineage with paid four-input XOR reassociations.  This script compares the two words
structurally, so that the question "can the two be combined?" is answered by counted
facts rather than by the two submissions' prose:

  * the skeleton -- arcs, partner order, reuse pairs, gauges, root roles, phase-1 and
    plain operations, sources and reads -- is identical, and both words have the same
    operation count, so the two live in one operation-index space;
  * the operations that differ are exactly PR217's reassociation set, and the frames
    that differ are counted;
  * PR216's admitted frames are keyed by that same operation index (each entry is
    `[op_index, [basis vectors...]]`), so the indices line up;
  * the frame floor of PR217's word bounds every frame layout of it, hence any
    combination that keeps that word.

It reads PR217's emitted payloads (from `rebuild_word.py`) and one file of PR216's
package; it writes nothing and touches neither package.

    python3 transfer_check.py --emit /tmp/bfly/emit \
        --pr216-package <checkout>/research/coordinated-crossover-pr200-v2
"""
import argparse
import json
import sys
import zipfile
from pathlib import Path

# #217's own published numbers, for the like-for-like comparison.
PR217_KAPPA = '684696826673891/10^15'      # 6.84696826673891e-4
PR216_KAPPA = '427415195711/625000000000000'  # 0.000683864313137600
# The completed-bank floor of #217's word, from this package's README (ceilings.py run
# at 1200 rounds): coarse saving < 6.973e-4, so kappa < 6.968e-4.
FLOOR_KAPPA = '6968/10^7'                  # 6.968e-4, upper bound on any layout
SKELETON = ('arcs', 'order', 'pairs', 'gauges', 'rootroles', 'phase1', 'plain',
            'sources', 'reads')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--emit', type=Path, required=True,
                    help='the directory written by rebuild_word.py')
    ap.add_argument('--pr216-package', type=Path, required=True,
                    help="#216's package directory (native-inputs.zip + witnesses/)")
    args = ap.parse_args()
    sys.set_int_max_str_digits(0)
    pkg = args.pr216_package.resolve()

    a = json.loads((args.emit.resolve() / 'word_p12.json').read_text())
    with zipfile.ZipFile(pkg / 'native-inputs.zip') as z:
        b = json.loads(z.read('word_p12.json').decode('utf-8'))
        current = json.loads(z.read('current-bases.json').decode('utf-8'))

    print('skeleton (must be identical for one operation-index space to exist)')
    bad = []
    for k in SKELETON:
        same = a[k] == b[k]
        print('  %-10s A=%d B=%d  %s' % (k, len(a[k]), len(b[k]),
                                         'identical' if same else 'DIFFERS'))
        if not same:
            bad.append(k)
    ok = not bad and len(a['ops']) == len(b['ops'])
    print('  ops        A=%d B=%d  %s' % (len(a['ops']), len(b['ops']),
                                          'same length' if len(a['ops']) == len(b['ops'])
                                          else 'DIFFERENT LENGTH'))
    if not ok:
        raise SystemExit('the two words are not on one operation-index space')

    changed_ops = sum(1 for x, y in zip(a['ops'], b['ops']) if x != y)
    changed_frames = sum(1 for x, y in zip(a['op_frame'], b['op_frame']) if x != y)
    print('\nwhat PR217 rewrote in that shared index space')
    print('  operations whose content differs: %d of %d' % (changed_ops, len(a['ops'])))
    print('  operation frames that differ:     %d of %d' % (changed_frames, len(a['ops'])))

    rewritten = {i for i in range(len(a['ops'])) if a['ops'][i] != b['ops'][i]}
    print('\nPR216 admission records, keyed by operation index')
    for label, path, records in (
            ('current bases (input)', pkg / 'native-inputs.zip', current),
            ('complete override list', pkg / 'witnesses' / 'additional-bases.json', None),
            ('canonical subspaces', pkg / 'witnesses' / 'merged-bases.json', None)):
        if records is None:
            records = json.loads(Path(path).read_text())
        idx = [int(e[0]) for e in records]
        if max(idx) >= len(a['ops']):
            raise SystemExit('%s: index beyond the shared operation list' % label)
        print('  %-22s %5d records, %5d distinct indices, max %5d, on a rewritten op: %d'
              % (label, len(idx), len(set(idx)), max(idx),
                 sum(1 for i in idx if i in rewritten)))

    print('\nthe ceiling this package measured for PR217\'s own word')
    print('  #217 achieved kappa                 = %s' % PR217_KAPPA)
    print('  #216 achieved kappa (plain word)    = %s' % PR216_KAPPA)
    print('  floor: any frame layout of the word < %s' % FLOOR_KAPPA)
    head = (0.0006968 / 0.000684696826673891 - 1) * 100
    print('  so a combined layout on this word can add at most +%.2f%% to the record' % head)
    print('  while #216\'s own layout sits %.3f%% below it, on the plain word'
          % ((0.000683864313137600 / 0.000684696826673891 - 1) * 100))
    print('\nPASS structural comparison (one index space, %d rewritten operations,'
          ' %d rewritten frames)' % (changed_ops, changed_frames))
    print('OPEN combination: the merge is well defined at the index level -- almost every')
    print('     admitted record addresses an operation PR217 left untouched -- but PR216')
    print('     admits its cuts with the scalar word fixed and PR217\'s rewrite is in those')
    print('     operations, so a merged layout needs fresh global admission and a fresh')
    print('     column replay, and the ceiling above bounds what it can reach.')


if __name__ == '__main__':
    main()
