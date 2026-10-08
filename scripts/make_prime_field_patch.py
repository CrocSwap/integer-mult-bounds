#!/usr/bin/env python3
"""Pinned-source patch for the conditional 373/10^11 > 2^-28 construction."""
import difflib
from pathlib import Path
from make_patch import replace_once
from make_fast_gaussian_patch import patched_files as retained_files
from prime_field_network import witness
ROOT=Path(__file__).resolve().parents[1]


def patched_files():
    result=witness();cn=result['complex']
    for name,old,new in retained_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=1479/10^{12}',r'\kappa=373/10^{11}>2^{-28}')
            if name.endswith('main.tex'):
                new=replace_once(new,r'\small Compressed complex network and fast resampling: eumemic}',
                    r'\small Compressed complex network and fast resampling: eumemic\\'+ '\n'+
                    r'\small Ternary five-subset contribution: Zhihao Chen (jacklightChen)}')
                new=new.replace('with assistance from Claude (Anthropic).',
                    'with assistance from Claude (Anthropic). The ternary five-subset construction, '
                    'star resynthesis and paired complex producer are contributed by Zhihao Chen '
                    '(jacklightChen), with substantial GPT-6 Astra assistance (as identified by the contributor).')
        elif name.endswith('03-motifs.tex'):
            marker=r'''The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-296/10^{11},\qquad\sigma=1-14/10^9.
\end{equation}
'''
            replacement='The preceding constructions provide the retained interfaces and comparison witnesses.\n'+(ROOT/'notes/prime-field28-construction.tex').read_text()+r'''
The selected exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-3/400000000,\qquad\sigma=1-39/10^9.
\end{equation}
'''
            new=replace_once(new,marker,replacement)
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:paired-bit-interface','prop:prime-field-bit-interface')
            new=new.replace(r'W=W_{\rm b}^{\rm pair}',r'W=W_{\rm b}').replace(r's=s_{\rm b}^{\rm pair}',r's=s_{\rm b}')
            new=new.replace(r'\tau=1-\frac{296}{10^{11}}',r'\tau=1-\frac3{400000000}')
            new=new.replace('pointwise bit gates','pointwise finite-alphabet gates').replace('pointwise\nbit gate','pointwise\nfinite-alphabet gate')
        elif name.endswith('05-layers.tex'):
            new=new.replace('prop:compressed-complex-interface','prop:prime-field-complex-interface')
            new=replace_once(new,r'$m=m_{\rm c}=15625$, $W=W_{\rm c}=1741801270000$ and',
                '$m=m_{\\rm c}='+str(cn['m'])+'$, $W=W_{\\rm c}='+str(cn['W'])+'$ and')
            new=replace_once(new,r'$s=s_{\rm c}=27215641140750000$ from',
                '$s=s_{\\rm c}='+str(cn['s'])+'$ from')
            new=new.replace('296/10^{11}','3/400000000').replace('14/10^9','39/10^9')
        elif name.endswith('08-assembly.tex'):
            replacements={r'a=296/10^{11}':r'a=3/400000000',r'a_{\rm c}=14/10^9':r'a_{\rm c}=39/10^9',
                r'\epsilon=\frac{49999}{100000}':r'\epsilon=\frac{4999}{10000}',
                r'\lambda=1-\frac{29595}{10^{13}}':r'\lambda=1-\frac{749}{10^{11}}',
                r"\lambda'=1-\frac{2959}{10^{12}}":r"\lambda'=1-\frac{748}{10^{11}}",
                r'\kappa=\frac{1479}{10^{12}}>2^{-30}':r'\kappa=\frac{373}{10^{11}}>2^{-28}',
                r'b^{19999/100000}':r'b^{4999/10000}',r'd^{100000}\le b^{19999}':r'd^{10000}\le b^{4999}',
                r'\frac{147947041}{10^{17}}>\frac{1479}{10^{12}}=\kappa':r'\frac{934813}{250000000000000}>\frac{373}{10^{11}}=\kappa',
                r'p^{50001/200000}':r'p^{5001/20000}',r'p^{499940001/10^9}':r'p^{49985001/10^8}',
                r'p^{50001/100000}':r'p^{5001/10000}',r'p^{1/50000}':r'p^{1/5000}'}
            for a,b in replacements.items():new=replace_once(new,a,b)
        yield name,old,new


def patch_text():
    return ''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),
        fromfile=f'a/{name}',tofile=f'b/{name}')) for name,old,new in patched_files())

if __name__=='__main__':
    (ROOT/'patches/prime-field28.patch').write_text(patch_text())
    print('Wrote pinned-source patch; conditional 373/10^11 > 2^-28.')
