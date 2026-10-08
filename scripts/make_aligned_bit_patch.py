#!/usr/bin/env python3
"""Independent pinned-source patch for the aligned bit circuit witness.

Builds on the fast-Gaussian patch. Adds the aligned bit circuit and the
cheaper center frames, switches the swap contract to the new bit interface,
and updates the bit exponent and assembly parameters.
"""
import difflib
from pathlib import Path

from aligned_bit_network import witness_only
from make_patch import replace_once
from make_fast_gaussian_patch import patched_files as fast_files

ROOT = Path(__file__).resolve().parents[1]


def note(name): return (ROOT/'notes'/name).read_text()


def motifs(text):
    return replace_once(text, r'''The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-296/10^{11},\qquad\sigma=1-14/10^9.
\end{equation}''', note('aligned-bit-construction.tex')+r'''
The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-325/10^{11},\qquad\sigma=1-14/10^9.
\end{equation}''')


def swap(text):
    text = replace_once(text, r'''All these data are finite and fixed. Proposition~\ref{prop:paired-bit-interface}
supplies these conditions with $W=W_{\rm b}^{\rm pair}$ and $s=s_{\rm b}^{\rm pair}$.''',
        r'''All these data are finite and fixed. Proposition~\ref{prop:aligned-bit-interface}
supplies these conditions with $W=W_{\rm b}^{\rm al}$ and $s=s_{\rm b}^{\rm al}$.''')
    return replace_once(text, r'We use the rational value $\tau=1-\frac{296}{10^{11}}$ established in',
                        r'We use the rational value $\tau=1-\frac{325}{10^{11}}$ established in')


def layers(text):
    text = replace_once(text, r'''retains its separate arity $m_{\rm b}=125000$ and exponent
$\tau=1-296/10^{11}$.''', r'''retains its separate arity $m_{\rm b}=125000$ and exponent
$\tau=1-325/10^{11}$.''')
    return replace_once(text, r'Fix $\tau=1-296/10^{11}$ and $\sigma=1-14/10^9$.',
                        r'Fix $\tau=1-325/10^{11}$ and $\sigma=1-14/10^9$.')


def assembly(text):
    text = replace_once(text, r'Put $a=296/10^{11}$ and $a_{\rm c}=14/10^9$.',
                        r'Put $a=325/10^{11}$ and $a_{\rm c}=14/10^9$.')
    text = replace_once(text, r''' \lambda=1-\frac{29595}{10^{13}},\quad
 \lambda'=1-\frac{2959}{10^{12}},\quad
 \kappa=\frac{1479}{10^{12}}>2^{-30}.''', r''' \lambda=1-\frac{32495}{10^{13}},\quad
 \lambda'=1-\frac{3249}{10^{12}},\quad
 \kappa=\frac{1624}{10^{12}}>2^{-30}.''')
    return replace_once(text, r'''       =\frac{147947041}{10^{17}}>\frac{1479}{10^{12}}=\kappa.''',
                        r'''       =\frac{162446751}{10^{17}}>\frac{1624}{10^{12}}=\kappa.''')


def patched_files():
    witness_only()  # full checks run in aligned_bit_network.py and the tests
    for name, old, new in fast_files():
        if name.endswith(('main.tex', '00-introduction.tex')):
            new = replace_once(new, r'\kappa=1479/10^{12}', r'\kappa=1624/10^{12}')
            if name.endswith('main.tex'):
                new = replace_once(new, r'''\small Compressed complex network and fast resampling: eumemic}''',
                                   r'''\small Compressed complex network, fast resampling and aligned bit circuit: eumemic}''')
                new = replace_once(new, r'''and a compressed complex network and faster Gaussian resampling prepared
with assistance from Claude (Anthropic).''', r'''and a compressed complex network, faster Gaussian resampling and an
aligned bit circuit prepared with assistance from Claude (Anthropic).''')
        elif name.endswith('03-motifs.tex'): new = motifs(new)
        elif name.endswith('04-swap.tex'): new = swap(new)
        elif name.endswith('05-layers.tex'): new = layers(new)
        elif name.endswith('08-assembly.tex'): new = assembly(new)
        new = new.replace('% Fast Gaussian resampling added October 8, 2026.\n',
                          '% Fast Gaussian resampling added October 8, 2026.\n'
                          '% Aligned bit circuit added October 8, 2026.\n')
        yield name, old, new


if __name__ == '__main__':
    patch = ''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True), fromfile=f'a/{name}', tofile=f'b/{name}'))
        for name, old, new in patched_files())
    (ROOT/'patches/aligned-bit-30.patch').write_text(patch)
    print('Wrote independent aligned-bit patch; conditional kappa=1624/10^12 > 2^-30.')
