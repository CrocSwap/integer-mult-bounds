#!/usr/bin/env python3
"""Independent upstream patch for the aligned paired-network witness."""
import difflib
from pathlib import Path

from aligned_paired_network import certificate
from make_paired_patch import patched_files as paired_files
from make_patch import replace_once

ROOT = Path(__file__).resolve().parents[1]


def patched_files():
    certificate()
    replacements = {
        '296/10': '305/10',
        '{296}': '{305}',
        r'\kappa=2^{-59}': r'\kappa=17\cdot2^{-63}',
        '>2^{-59}=\\kappa': '>17\\cdot2^{-63}=\\kappa',
        '272158569': '739738521',
        '156250000000000000000000000': '400000000000000000000000000',
        '450394': '435450',
        '509194': '494250',
        '40256': '55200',
        '406321422080000': '394839648000000',
        '50790175992864000000': '49354954232864000000',
        '661055000': '642375000',
    }
    for name, old, new in paired_files():
        if name.endswith('03-motifs.tex'):
            new = replace_once(new,
                'Group the ordered vertices consecutively into pairs, with a final singleton\n'
                'when necessary.',
                'Fix the global pairs $\\{0,1\\},\\{2,3\\},\\ldots,\\{48,49\\}$.\n'
                'For common point $i$, order the other points increasingly after removing\n'
                '$i$ and its partner $i\\mathbin{\\oplus}1$, then append that partner.\n'
                'Relabel the local inputs and outputs by this permutation. Group these\n'
                'ordered vertices consecutively into pairs, with a final singleton.\n'
                'Thus all complete root pairs agree across common-point groups;\n'
                'the weighted recursion itself is unchanged.')
        for before, after in replacements.items():
            new = new.replace(before, after)
        yield name, old, new


if __name__ == '__main__':
    patch = ''.join(''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f'a/{name}', tofile=f'b/{name}')) for name, old, new in patched_files())
    (ROOT / 'patches/h50-aligned-paired.patch').write_text(patch, newline='\n')
    print('Wrote independent conditional h50-aligned-paired.patch')
