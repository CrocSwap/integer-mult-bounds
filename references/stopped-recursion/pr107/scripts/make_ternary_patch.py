#!/usr/bin/env python3
"""Independent ternary 2^-30 patch against the pinned original manuscript."""
import difflib
from hashlib import sha256
from pathlib import Path
import json

from certify import require
from make_complex_compression_patch import patched_files as prior_files
from make_patch import replace_once
from ternary_assembly import assembly_control

ROOT=Path(__file__).resolve().parents[1]


def verify_certificate():
    c=json.loads((ROOT/'certificates/ternary-side.json').read_text())
    require(all(sha256((ROOT/p).read_bytes()).hexdigest()==h
                for p,h in c['source_sha256'].items()),'Stale ternary construction certificate')
    return c


def construction():
    text=(ROOT/'notes/ternary-five-subsets.tex').read_text().split(
        r'\subsection{Conditional assembly witness}')[0]
    text=text.replace(r'\subsection{',r'\subsubsection{').replace(r'\section{',r'\subsection{')
    return text+r'''
\begin{proposition}\label{prop:ternary-bit-interface}
There is a fixed pointwise circuit over $\mathbb F_3$ satisfying the
rational finite-shear contract on every scalar role, with
\[
 m_{\rm b}=24389,\quad W_{\rm b}=589493540769997500,\quad
 s_{\rm b}=14377157287342062574725,
\]
and strict exponent $\tau=1-467/10^{11}$. Every auxiliary input is restored. Via
Section~\ref{sec:finite-alphabet-transfer}, it supplies the bit chunk
interchange interface with this exponent on the same fixed-tape model.
\end{proposition}
\begin{proof}
The construction above proves the scalar permutation, all rational
endpoint identities, full edge-rank accounting and the strict logarithm
comparison. The finite-alphabet extension applies to its ternary symbols
and returns the original bit payload at completed interchange boundaries.
\end{proof}
'''


def replace_all(text,old,new):
    require(old in text,'Missing ternary integration anchor: '+old)
    return text.replace(old,new)


def patched_files():
    verify_certificate();assembly_control()
    for name,old,new in prior_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_all(new,r'\kappa=2^{-31}',r'\kappa=2^{-30}')
            new=new.replace("Douglas Colkitt's compact-control and complex-network constructions",
                            "Douglas Colkitt's compact-control, complex-network and ternary constructions")
        elif name.endswith('03-motifs.tex'):
            new=replace_once(new,r'\tau=1-\frac{296}{10^{11}}',r'\tau_{\rm pair}=1-\frac{296}{10^{11}}')
            anchor='The bit network retains $m_{\\rm b}=125000$.'
            new=replace_once(new,anchor,construction()+
                '\nThe bit network used below has $m_{\\rm b}=24389$ by Proposition~\\ref{prop:ternary-bit-interface}.')
            new=replace_once(new,r'\tau=1-296/10^{11}',r'\tau=1-467/10^{11}')
        elif name.endswith('04-swap.tex'):
            new=replace_once(new,'pointwise bit gates',
                'pointwise finite-alphabet gates')
            new=new.replace('pointwise\nbit gate','pointwise\nfinite-alphabet gate')
            new=replace_once(new,
                'Proposition~\\ref{prop:paired-bit-interface}\nsupplies these conditions with $W=W_{\\rm b}^{\\rm pair}$ and $s=s_{\\rm b}^{\\rm pair}$.',
                'Proposition~\\ref{prop:ternary-bit-interface}\nsupplies these conditions over $\\mathbb F_3$, with $m=m_{\\rm b}$, $W=W_{\\rm b}$ and $s=s_{\\rm b}$.')
            new=replace_once(new,r'\tau=1-\frac{296}{10^{11}}',r'\tau=1-\frac{467}{10^{11}}')
            extension=(ROOT/'notes/finite-alphabet-transfer.tex').read_text().replace(r'\section{',r'\subsection{')
            anchor=r'\subsection{Removing width and row restrictions}'
            new=replace_once(new,anchor,extension+'\n'+anchor)
        elif name.endswith('05-layers.tex'):
            new=replace_all(new,r'm_{\rm b}=125000',r'm_{\rm b}=24389')
            new=replace_all(new,'296/10^{11}','467/10^{11}')
        elif name.endswith('08-assembly.tex'):
            for before,after in (
                ('a=296/10^{11}','a=467/10^{11}'),
                (r'\epsilon=\frac{199}{1000},\quad c=1,\quad\delta=\frac1{10000}',
                 r'\epsilon=\frac{1999}{10000},\quad c=1,\quad\delta=\frac1{10^6}'),
                (r'\lambda=1-\frac{293}{10^{11}}',r'\lambda=1-\frac{4669}{10^{12}}'),
                (r"\lambda'=1-\frac{29}{10^{10}}",r"\lambda'=1-\frac{4668}{10^{12}}"),
                (r'2^{-31}',r'2^{-30}'),
                (r'b^{199/1000}',r'b^{1999/10000}'),
                (r'd^{1000}\le b^{199}',r'd^{10000}\le b^{1999}'),
                (r'b^{1597/2000}',r'b^{15997/20000}'),
                (r'\frac{5771}{10^{13}}',r'\frac{2332833}{2500000000000000}'),
                (r'p^{1199/4000}',r'p^{11999/40000}'),
                (r'p^{1597/2000}',r'p^{15997/20000}'),
                (r'p^{199/1000}',r'p^{1999/10000}'),
                (r'p^{801/1000}',r'p^{8001/10000}'),
                (r'p^{301/500}',r'p^{3001/5000}')):
                new=replace_all(new,before,after)
        new=new.replace('% Conditional compact-control and complex-compression research draft;',
                        '% Conditional compact-control, complex-compression and ternary research draft;')
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),
        fromfile='a/'+name,tofile='b/'+name)) for name,old,new in patched_files())
    (ROOT/'patches/ternary-30.patch').write_text(patch)
    print('Wrote independent conditional ternary 2^-30 patch.')
