#!/usr/bin/env python3
"""Independent upstream patch for the cross-group sharing refinement."""
import difflib
from pathlib import Path
from make_patch import replace_once
from make_dag_patch import patched_files as dag_files
from shared_point_network import certificate
ROOT=Path(__file__).resolve().parents[1]


def patched_files():
    certificate()
    proof=(ROOT/'notes/shared-point-construction.tex').read_text()
    for name,old,new in dag_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-63}',r'\kappa=13\cdot2^{-66}')
        elif name.endswith('03-motifs.tex'):
            start=new.index(r'\subsection{Explicit rational bounds for the two recurrences}')
            new=new[:start]+proof
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:dag-bit-interface','prop:shared-point-bit-interface')
            new=new.replace(r'W_{\rm b}^{\rm dag}',r'W_{\rm b}^{\rm shared}')
            new=new.replace(r's_{\rm b}^{\rm dag}',r's_{\rm b}^{\rm shared}')
            new=replace_once(new,r'1-\frac{187}{10^{11}}',r'1-\frac{203}{10^{11}}')
        elif name.endswith('05-layers.tex'):
            new=replace_once(new,r'\tau=1-\frac{187}{10^{11}}',r'\tau=1-\frac{203}{10^{11}}')
        elif name.endswith('08-assembly.tex'):
            new=replace_once(new,r'Put $a=187/10^{11}$',r'Put $a=203/10^{11}$')
            new=new.replace(r'\kappa=2^{-63}',r'\kappa=13\cdot2^{-66}')
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/h46-shared-point.patch').write_text(patch)
    print('Wrote independent conditional h46-shared-point.patch')
