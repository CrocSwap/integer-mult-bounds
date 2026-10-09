#!/usr/bin/env python3
"""Independent upstream patch for rectangle incidence circuits and kappa=2^-67."""
import difflib
from pathlib import Path
from make_patch import replace_once
from tune_routing import patched_files as tuned_files
from incidence_network import certificate

ROOT=Path(__file__).resolve().parents[1]


def patched_files():
    certificate()
    proof=(ROOT/'notes/incidence-construction.tex').read_text()
    for name,old,new in tuned_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-76}',r'\kappa=2^{-67}')
        elif name.endswith('03-motifs.tex'):
            start=new.index(r'\subsection{Explicit rational bounds for the two recurrences}')
            new=new[:start]+proof
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:bit-motif-interface','prop:incidence-bit-interface')
            new=replace_once(new,r'$W=W_{\rm b}$ and $s=s_{\rm b}$',
                             r'$W=W_{\rm b}^{\rm rect}$ and $s=s_{\rm b}^{\rm rect}$')
            new=replace_once(new,r'1-\frac{9}{500000000000}',r'1-\frac{46}{10^{11}}')
        elif name.endswith('05-layers.tex'):
            new=replace_once(new,r'\tau=\sigma=1-\frac{9}{500000000000}',
                r'\tau=1-\frac{46}{10^{11}},\qquad \sigma=1-\frac9{500000000000}')
        elif name.endswith('08-assembly.tex'):
            new=replace_once(new,'Put $a=9/500000000000$ and choose',
                             r'Put $a=46/10^{11}$ and $a_{\rm c}=9/500000000000$ and choose')
            new=replace_once(new,r'\tau=\sigma=1-a',r'\tau=1-a,\quad \sigma=1-a_{\rm c}')
            new=new.replace(r'\kappa=2^{-76}',r'\kappa=2^{-67}')
            new=replace_once(new,r'\sigma+\beta(1-\sigma)=1-a/10',
                             r'\sigma+\beta(1-\sigma)=1-a_{\rm c}/10')
            new=replace_once(new,'The rational stopping comparison',
                r'The separate layer requirement $\sigma<\lambda$ follows from '
                r'$19a^2/20<a_{\rm c}$; the leaf comparison follows from '
                r'$9a^2<a_{\rm c}$. The rational stopping comparison')
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/h46-incidence-67.patch').write_text(patch)
    print('Wrote independent conditional h46-incidence-67.patch')
