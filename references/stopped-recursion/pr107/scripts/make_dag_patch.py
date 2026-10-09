#!/usr/bin/env python3
"""Independent upstream patch for shared intermediate sums and kappa=2^-63."""
import difflib
from pathlib import Path
from make_patch import replace_once
from make_incidence_patch import patched_files as rectangle_files
from dag_network import certificate

ROOT=Path(__file__).resolve().parents[1]


def patched_files():
    certificate()
    proof=(ROOT/'notes/dag-construction.tex').read_text()
    for name,old,new in rectangle_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-67}',r'\kappa=2^{-63}')
        elif name.endswith('03-motifs.tex'):
            # Retain the preceding rectangle construction as a proved special
            # case, but replace its final primitive-exponent selection.
            start=new.index(r'\subsection{Explicit rational bounds for the two recurrences}')
            logproof=r'''
For reference, the retained logarithm enclosure uses
$S(x)=2\sum_{j=0}^{23}z^{2j+1}/(2j+1)$ and
$E(x)=2z^{49}/(49(1-z^2))$, where $z=(x-1)/(x+1)$ and $1\le x\le2$.
Then $S(x)\le\log x\le S(x)+E(x)$, and exact comparison gives
$\log m\le16(S(2)+E(2))+S(m/2^{16})+E(m/2^{16})<5743/500$.
'''
            new=new[:start]+logproof+proof
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:incidence-bit-interface','prop:dag-bit-interface')
            new=new.replace(r'W_{\rm b}^{\rm rect}',r'W_{\rm b}^{\rm dag}')
            new=new.replace(r's_{\rm b}^{\rm rect}',r's_{\rm b}^{\rm dag}')
            new=replace_once(new,r'1-\frac{46}{10^{11}}',r'1-\frac{187}{10^{11}}')
        elif name.endswith('05-layers.tex'):
            new=replace_once(new,r'\tau=1-\frac{46}{10^{11}}',r'\tau=1-\frac{187}{10^{11}}')
        elif name.endswith('08-assembly.tex'):
            new=replace_once(new,r'Put $a=46/10^{11}$',r'Put $a=187/10^{11}$')
            new=new.replace(r'\kappa=2^{-67}',r'\kappa=2^{-63}')
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/h46-dag-63.patch').write_text(patch)
    print('Wrote independent conditional h46-dag-63.patch')
