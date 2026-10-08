#!/usr/bin/env python3
"""Independent pinned-source patch for the compressed complex network witness.

Builds on the compact-control patch: the movement, reservation, repair, guard
and bit network are unchanged. The complex motif receives the shared-sum side
circuit, and the layer constants and assembly parameters are updated.
"""
import difflib
from pathlib import Path

from complex_network import witness_only
from make_patch import replace_once
from make_compact_control_patch import patched_files as compact_files

ROOT = Path(__file__).resolve().parents[1]


def note(name): return (ROOT/'notes'/name).read_text()


def motifs(text):
    text = replace_once(text, r'''The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-296/10^{11},\qquad\sigma=1-418/10^{12}.
\end{equation}
''', r'''With the original side wires these exponents would be
\begin{equation}\label{eq:compact-intermediate-exponents}
 \tau=1-296/10^{11},\qquad\sigma_{\rm orig}=1-418/10^{12}.
\end{equation}
We replace the side wires by a shared-sum circuit.

'''+note('complex-circuit-construction.tex')+r'''
The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-296/10^{11},\qquad\sigma=1-14/10^9.
\end{equation}
''')
    return text


def layers(text):
    text = replace_once(text, r'''$m=m_{\rm c}=15625$, $W=W_{\rm c}=58645352620000$ and
$s=s_{\rm c}=916333630984500000$ from''', r'''$m=m_{\rm c}=15625$, $W=W_{\rm c}=1741801270000$ and
$s=s_{\rm c}=27215641140750000$ from''')
    text = text.replace('prop:compact-complex-interface', 'prop:compressed-complex-interface')
    text = replace_once(text, r'Fix $\tau=1-296/10^{11}$ and $\sigma=1-418/10^{12}$.',
                        r'Fix $\tau=1-296/10^{11}$ and $\sigma=1-14/10^9$.')
    return text


def assembly(text):
    start = text.index('Put $a=296/10^{11}$')
    end = text.index(r'\subsection{Input and transform sizes}', start)
    text = text[:start]+r'''Put $a=296/10^{11}$ and $a_{\rm c}=14/10^9$.
Choose
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-a,\quad\sigma=1-a_{\rm c},\quad
 \beta=\frac1{1000},\quad\zeta=\frac1{10000},\quad
 C_1=\frac{49961}{10000},\\
 \epsilon=\frac{19999}{100000},\quad c=\frac{999}{1000},\quad\delta=\frac1{10^6},\\
 \lambda=1-\frac{2958}{10^{12}},\quad
 \lambda'=1-\frac{2956}{10^{12}},\quad
 \kappa=\frac{59}{10^{11}}>2^{-31}.
\end{gathered}
\end{equation}
Since $\sigma<\tau$, the compact-control recurrence has
$\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}=\tau$, and exact rational
comparisons give
\[
 \max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1,\quad
 \sigma+\beta(1-\sigma)<\lambda',\quad 1-c<\lambda'.
\]
The stopping test is $e^{1000}<d$. Section~\ref{sec:compact-stopped-guard}
proves the displayed $C_1$, with $\epsilon C_1<1$.
The retained Gaussian choice gives the remaining comparisons
\[
 \epsilon<\tfrac13,\quad 2\epsilon<1,\quad
 \epsilon(1-\tau)<1-\tau,\quad
 \tfrac34+\delta+\tfrac54\epsilon<1,\quad
 \epsilon(1+c)<1,\quad \epsilon+\delta<1.
\]

'''+text[end:]
    text = replace_once(text, r'b^{15997/20000}', r'b^{159997/200000}')
    text = replace_once(text, r'$d=\lfloor b^{1999/10000}\rfloor$', r'$d=\lfloor b^{19999/100000}\rfloor$')
    text = replace_once(text, r'd^{10000}\le b^{1999}', r'd^{100000}\le b^{19999}')
    text = replace_once(text, r'''       =\frac{333833}{4\cdot10^{15}}>\frac{83}{10^{12}}=\kappa.''',
                        r'''       =\frac{14779261}{25\cdot10^{15}}>\frac{59}{10^{11}}=\kappa.''')
    text = replace_once(text, r'''$\alpha=\Theta(p^{11999/40000})$ and
$\gamma=O(p^{15997/20000})=o(p)$. Also
$K=\Theta(p^{1999/50000})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{8001/10000})$. The prime-interval ratio grows as
$p^{3001/5000}$.''', r'''$\alpha=\Theta(p^{119999/400000})$ and
$\gamma=O(p^{159997/200000})=o(p)$. Also
$K=\Theta(p^{19979001/10^8})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{80001/100000})$. The prime-interval ratio grows as
$p^{30001/50000}$.''')
    return text


def patched_files():
    witness_only()  # full checks run in complex_network.py and the tests
    for name, old, new in compact_files():
        if name.endswith(('main.tex', '00-introduction.tex')):
            new = replace_once(new, r'\kappa=83/10^{12}', r'\kappa=59/10^{11}')
            if name.endswith('main.tex'):
                new = replace_once(new, r'''\small Compact-control modifications: Douglas Colkitt}''',
                                   r'''\small Compact-control modifications: Douglas Colkitt\\
\small Compressed complex network: eumemic}''')
                new = replace_once(new, r'''and retained project refinements, prepared with assistance from OpenAI Codex.''',
                                   r'''and retained project refinements, prepared with assistance from OpenAI Codex,
and a compressed complex network prepared with assistance from Claude
(Anthropic).''')
                new = replace_once(new, 'no endorsement by OpenAI is implied.',
                                   'no endorsement by OpenAI or Anthropic is implied.')
        elif name.endswith('03-motifs.tex'): new = motifs(new)
        elif name.endswith('05-layers.tex'): new = layers(new)
        elif name.endswith('08-assembly.tex'): new = assembly(new)
        new = new.replace('% Conditional compact-control research draft; see main.tex for scope.\n',
                          '% Conditional compact-control research draft; see main.tex for scope.\n'
                          '% Compressed complex network added October 7, 2026.\n')
        yield name, old, new


if __name__ == '__main__':
    patch = ''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True), fromfile=f'a/{name}', tofile=f'b/{name}'))
        for name, old, new in patched_files())
    (ROOT/'patches/complex-circuit-31.patch').write_text(patch)
    print('Wrote independent compressed-complex patch; conditional kappa=59/10^11 > 2^-31.')
