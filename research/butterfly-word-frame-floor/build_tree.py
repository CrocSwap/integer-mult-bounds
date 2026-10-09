#!/usr/bin/env python3
"""Assemble a PR212-shaped `--tree` input for PR217's changed bit word.

The tree is a faithful shim: the word, frames and graph are PR217's emitted payloads
(their hashes were checked against the package's `expected-bit.json` by
`rebuild_word.py`), the partner chronology, sinks, base profile and the vendored
PR168-v4 checker come from the pinned PR202 checkout, and `certificate.json['bit']`
carries PR217's own post-terminal profile plus the pre-sink profile restored by the
terminal record (`{3, 21} x -102`, exactly as PR200's certificate records it, i.e. +34
children of width 3 and +34 of width 21 and +34 roles).

Every field of that shim is re-derived by `ceiling.py`'s own self-tests: it rebuilds the
children multiset from the word and requires it to equal the shim's pre-sink histogram,
requires the sink record to be one width-3 and one width-21 child per sink and stage, and
requires `2v + roles - pairs` and the rank mass to match.  A wrong shim fails loudly
instead of quietly lowering the floor.

    python3 build_tree.py --emit <dir from rebuild_word.py> --bit-root <pr202 checkout> \
                          --package <checkout>/research/butterfly-coordinated-bit-211 \
                          --tree <fresh tree dir>
"""
import argparse
import gzip
import json
import shutil
import sys
from pathlib import Path

PKG_REL = Path('research/paired-cube-diagonal-bit-168')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--emit', type=Path, required=True, help='directory written by rebuild_word.py')
    ap.add_argument('--bit-root', type=Path, required=True, help='the #202 checkout used for the rebuild')
    ap.add_argument('--package', type=Path, required=True, help='the butterfly package directory')
    ap.add_argument('--tree', type=Path, required=True, help='fresh tree directory to create')
    args = ap.parse_args()
    sys.set_int_max_str_digits(0)
    pr202 = (args.bit_root.resolve() / PKG_REL)
    package = args.package.resolve()
    tree = args.tree.resolve() / PKG_REL
    bit = tree / 'selected' / 'bit'
    if tree.exists():
        shutil.rmtree(tree)
    bit.mkdir(parents=True)
    shutil.copytree(pr202 / 'references', tree / 'references')
    for name in ('kchron_p12.json', 'sinks.json', 'profile_p12.json'):
        shutil.copy2(pr202 / 'selected' / 'bit' / name, bit / name)
    for name in ('graph_p12.json', 'word_p12.json', 'frames_p12.json'):
        payload = (args.emit.resolve() / name).read_bytes()
        (bit / name).write_bytes(payload)
        (bit / (name + '.gz')).write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    post = json.loads((package / 'expected-bit.json').read_text())['profile']
    pre = dict(post)
    pre['child_histogram'] = dict(post['child_histogram'])
    pre['child_histogram']['3'] = pre['child_histogram'].get('3', 0) + 102
    pre['child_histogram']['21'] = pre['child_histogram'].get('21', 0) + 102
    pre['rank_per_vertex'] = sum(int(r) * n for r, n in pre['child_histogram'].items())
    pre['W_per_vertex'] = post['W_per_vertex'] + 34
    pre['physical_target_histogram'] = dict(post['physical_target_histogram'])
    pre['physical_target_histogram']['21'] = pre['physical_target_histogram'].get('21', 0) + 34
    cert = json.loads((package / 'certificate.json').read_text())
    shim = {'bit': {
        'overridden_profile': pre,
        'profile': post,
        'terminal': {'child_delta': {'3': -102, '21': -102}},
        'coarse': {'coarse_saving': cert['bit_coarse']},
        'kappa': cert['kappa'],
        'packed_profile': cert['packed_profile'],
        'shim_note': 'pre-sink profile restored from the post-terminal profile by the {3,21} x -102 sink record',
    }}
    (tree / 'certificate.json').write_text(json.dumps(shim, indent=1, sort_keys=True) + '\n')
    print('tree:', tree)
    print('pre-sink W %s rank %s deficit %s'
          % (pre['W_per_vertex'], pre['rank_per_vertex'], pre['deficit_per_vertex']))
    print('post-terminal W %s rank %s deficit %s'
          % (post['W_per_vertex'], post['rank_per_vertex'], post['deficit_per_vertex']))


if __name__ == '__main__':
    main()
