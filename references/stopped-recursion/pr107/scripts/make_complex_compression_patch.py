#!/usr/bin/env python3
"""Independent 2^-31 patch against the pinned original manuscript.

Retains the published compact-control proofs verbatim; changes the complex
finite interface and its explicit downstream constants and parameter witness.
"""
import difflib
from pathlib import Path

from complex_compression import assembly_control
from make_compact_control_patch import patched_files as compact_files
from make_patch import replace_once

ROOT = Path(__file__).resolve().parents[1]


def construction():
    source = (ROOT/'notes/complex-compression.tex').read_text()
    text = source.split(r'\section{Conditional assembly and precision}')[0]
    # Embed the construction within the original motif section.
    text = text.replace(r'\subsection{', r'\subsubsection{')
    text = text.replace(r'\section{', r'\subsection{')
    return text + r'''
\begin{proposition}\label{prop:compressed-complex-interface}
The complex motif interface holds with
$m_{\rm c}=17576$, $W_{\rm c}=7082222160000$ and
$s_{\rm c}=124477130005280000$, and strict exponent $\sigma=1-5/10^9$.
Its scalar circuit restores arbitrary auxiliary inputs; after phase-frame
telescoping and endpoint corrections, the network implements the normalized
$C^{\otimes m_{\rm c}}$ operator on every role, for any number of columns,
using $s_{\rm c}$ forward or inverse translation kernels.
\end{proposition}
\begin{proof}
The construction above supplies the signed scalar exchange, nested binary
frames with orthonormal residual bases, shared-bank joins and unchanged
endpoint corrections. Its displayed residual accounting and logarithm
inequality give the claimed constants and strict exponent.
\end{proof}

The bit network retains $m_{\rm b}=125000$. Its swap interface works at
arbitrary binary widths; the complex recursion uses that interface's
exponent and fixed tape guarantee, not its arity. The complex recursion's
branching, role split and depth use $m_{\rm c},W_{\rm c},s_{\rm c}$.
No equality of bit and complex dimensions is required by the assembly.
'''


def guard_accounting():
    source = (ROOT/'notes/complex-compression.tex').read_text()
    start = source.index('The new scalar mixers use only')
    end = source.index('This conditional construction is integrated', start)
    return (r'\paragraph{Node charge for the compressed complex motif.}'+'\n'
            +r'\label{par:compressed-complex-node-charge}'+'\n'
            +source[start:end])


def assembly(text):
    changes = {
        r'a_{\rm c}=418/10^{12}': r'a_{\rm c}=5/10^9',
        r'\beta=\frac1{1000},\quad\zeta=\frac1{10000}':
            r'\beta=\frac1{100},\quad\zeta=\frac1{1000}',
        r'C_1=\frac{49961}{10000}': r'C_1=\frac{4961}{1000}',
        r'\epsilon=\frac{1999}{10000},\quad c=\frac15,\quad\delta=\frac1{10^6}':
            r'\epsilon=\frac{199}{1000},\quad c=1,\quad\delta=\frac1{10000}',
        r'\lambda=1-\frac{1671}{4\cdot10^{12}}': r'\lambda=1-\frac{293}{10^{11}}',
        r"\lambda'=1-\frac{167}{4\cdot10^{11}}": r"\lambda'=1-\frac{29}{10^{10}}",
        r'\kappa=\frac{83}{10^{12}}>2^{-34}': r'\kappa=2^{-31}',
        r'$\chi=\tau+(1-\beta)(\sigma-\tau)$':
            r'$\chi=\tau$, because $\sigma<\tau$',
        r'e^{1000}<d': r'e^{100}<d',
        r'b^{1999/10000}': r'b^{199/1000}',
        r'd^{10000}\le b^{1999}': r'd^{1000}\le b^{199}',
        r'b^{15997/20000}': r'b^{1597/2000}',
        r'$C_1=49961/10000$': r'$C_1=4961/1000$',
        r'\frac{333833}{4\cdot10^{15}}>\frac{83}{10^{12}}=\kappa':
            r'\frac{5771}{10^{13}}>2^{-31}=\kappa',
        r'd^{49961/10000}': r'd^{4961/1000}',
        r'p^{11999/40000}': r'p^{1199/4000}',
        r'p^{15997/20000}': r'p^{1597/2000}',
        r'p^{1999/50000}': r'p^{199/1000}',
        r'p^{8001/10000}': r'p^{801/1000}',
        r'p^{3001/5000}': r'p^{301/500}',
    }
    for old, new in changes.items():
        text = replace_once(text, old, new)
    return text


def patched_files():
    assembly_control()
    for name, old, new in compact_files():
        if name.endswith(('main.tex', '00-introduction.tex')):
            new = replace_once(new, r'\kappa=83/10^{12}', r'\kappa=2^{-31}')
            if name.endswith('main.tex'):
                new = new.replace('Compact-control modifications:', 'Research modifications:')
                new = replace_once(new, "Douglas Colkitt's compact-control construction",
                                   "Douglas Colkitt's compact-control and complex-network constructions")
        elif name.endswith('03-motifs.tex'):
            new = replace_once(new, (ROOT/'notes/independent-complex.tex').read_text(), construction())
            new = replace_once(new, r'\sigma=1-418/10^{12}', r'\sigma=1-5/10^9')
        elif name.endswith('05-layers.tex'):
            for before, after in (
                ('15625', '17576'), ('58645352620000', '7082222160000'),
                ('916333630984500000', '124477130005280000'),
                (r'\sigma=1-418/10^{12}', r'\sigma=1-5/10^9'),
            ):
                new = replace_once(new, before, after)
            new = new.replace('prop:compact-complex-interface', 'prop:compressed-complex-interface')
            anchor = r'\subsection{A generalized stopped-depth guard}'
            new = replace_once(new, anchor, guard_accounting() + anchor)
        elif name.endswith('08-assembly.tex'):
            new = assembly(new)
        new = new.replace('% Conditional compact-control research draft;',
                          '% Conditional compact-control and complex-compression research draft;')
        yield name, old, new


if __name__ == '__main__':
    patch = ''.join(''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f'a/{name}', tofile=f'b/{name}'))
        for name, old, new in patched_files())
    (ROOT/'patches/complex-compression-31.patch').write_text(patch)
    print('Wrote independent complex-compression patch; conditional kappa=2^-31.')
