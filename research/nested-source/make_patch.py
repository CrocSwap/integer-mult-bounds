#!/usr/bin/env python3
"""Build a nested-source manuscript patch against the pinned upstream.

The uniform and PR10 statements remain intact; new named interfaces are
appended, and the final consumers/parameters use the certified expansion.
"""
import argparse
from functools import lru_cache
from pathlib import Path
import difflib
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Load the historical generator while scripts precedes this file's directory;
# both generators deliberately have the basename make_patch.py.
sys.path.insert(0, str(ROOT/'scripts'))
import make_source_frame_patch as previous
from source_frame_network import assembly as previous_assembly
from make_patch import replace_once
sys.path.insert(0, str(HERE))
import verify


def texq(q):
    return str(q.numerator) if q.denominator == 1 else rf'\frac{{{q.numerator}}}{{{q.denominator}}}'


def exponent(q):
    return str(q.numerator) if q.denominator == 1 else f'{q.numerator}/{q.denominator}'


def active_references(text):
    return text.replace('lem:batched-chunk-swap', 'lem:nested-chunk-swap').replace(
        'prop:batched-simultaneous-layer', 'prop:nested-simultaneous-layer')


def bit_interface():
    body = (ROOT/'notes/nested-bit.tex').read_text()
    tau = '1-'+texq(verify.BIT_SAVING)
    return body + r'''
\begin{lemma}[Nested-source arbitrary-width interchange]
\label{lem:nested-chunk-swap}
Put $\tau='''+tau+r'''$. There is one fixed finite-alphabet multitape
procedure which, for every $P,G,B\ge1$ and $u\ge1$, transforms an
arbitrary bit array on
\[
 [P]\times[2^u]\times[G]\times[2^u]\times[B]
\]
by $(p,h,g,d,z)\mapsto(p,d,g,h,z)$ in $O(Vu^\tau)$ steps, where
$V=PGB\,2^{2u}$. Shape processing, row padding and removal, address
radix padding and removal, and fixed-tape workspace cleanup are included.
The constant is independent of all lengths and all payload values.
Widths differing by one bit cost $O(V(1+u^\tau))$, where $u$ is the
smaller width, with the same arbitrary spectator gap.
\end{lemma}
\begin{proof}
Use the dimension-32 producer of Section~\ref{sec:nested-bit-producer},
the one simultaneous rational basis and the contiguous pivot profiles
of Sections~\ref{sec:nested-source-basis} and
\ref{sec:nested-bit-moment}. Their exact mixed-width moment is strictly
below one at the displayed exponent. The scalar producer and all dirty
auxiliary restoration are unchanged. Conjugate every gate and terminal
matrix by this same basis and choose the address prime after the fixed
rational factors, preserving the endpoint difference and common-frame
invariant of Proposition~\ref{prop:power-interchange}.
The general integer-width recurrence and self-supplied rows of
Section~\ref{sec:mixed-width-rows} apply to this new finite list of
strictly smaller contiguous children. They prove the stated bound,
including every padding and cleanup operation. The one-bit extension
uses the same two layouts as Lemma~\ref{lem:batched-chunk-swap}, with
the new equal-width procedure in its interchange step.
\end{proof}
'''


def layer_interface(text):
    marker = r'\begin{proposition}[Batched simultaneous normalized butterfly layer]'
    start = text.index(marker)
    active = text[start:]
    active = replace_once(active, marker,
        r'\begin{proposition}[Nested-source simultaneous normalized butterfly layer]')
    active = active_references(active)
    active = replace_once(active,
        r'Fix $\tau=1-154/10^8$ and $\sigma=1-18/10^7$.',
        'Fix $\\tau=1-'+texq(verify.BIT_SAVING)+'$ and $\\sigma=1-'+texq(verify.COMPLEX_SAVING)+'$.')
    active = replace_once(active, r'C_1=6/5-\beta/5+\zeta',r'C_1=3/2-\beta/2+\zeta')
    begin = active.index('The whole-residual construction of')
    end = active.index(r'Put $\Delta=', begin)
    active = active[:begin] + r'''Section~\ref{sec:nested-complex} compiles every nonzero physical
complex residual as one child. Its full edge histogram and exact moment
certify the displayed $\sigma$. At width $e=mf+r_0$, handle the fewer
than $m$ remainder axes individually; each true child has width $af$
for its physical residual rank $1\le a\le21896<m$.
The complete-row construction and weighted-tree argument in
Section~\ref{sec:mixed-complex-layer} apply to this nested finite
child list. Each role stream has exactly $1/W_{\rm c}$ of the parent's
logical volume. Compact-control basis changes now use
Lemma~\ref{lem:nested-chunk-swap}. The selected-bit movement lemmas
and Proposition~\ref{prop:compact-selected-addition} require only the
interchange exponent as an interface parameter, so their proofs apply
with this new $\tau$. Here the interchange arity is $m_{\rm b}=32768$,
whereas the complex arity remains $m_{\rm c}=21952$. Their independence
is permitted by the arbitrary-width interchange interface. The following
uniformity estimates are unchanged.
''' + active[end:]
    active = active.replace('sec:bulk-complex-guard','sec:nested-complex-guard')
    prefix = r'''
\subsection{The nested residual interfaces}
The earlier uniform and two-class batched constructions retain their
original fixed exponents and hypotheses. We now use the stronger bit
interface of Lemma~\ref{lem:nested-chunk-swap} and the complete
complex residual list. The following proof and statement are the
interfaces used by the final transform and multiplication construction.
'''
    return prefix + (ROOT/'notes/nested-complex.tex').read_text() + '\n' + active


def parameter_section(w):
    p = w['parameters']
    text = active_references(previous.parameter_section(w))
    start = text.index(r'\begin{equation}\label{eq:fixed-parameters}')
    end = text.index(r'\end{equation}', start)+len(r'\end{equation}')
    block = r'''\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-'''+texq(1-p['tau'])+r''',\quad\sigma=1-'''+texq(1-p['sigma'])+r''',\quad
 \beta='''+texq(p['beta'])+r''',\quad\zeta=\frac1{10000},\\
 C_1=\frac32-\frac\beta2+\zeta='''+texq(p['C1'])+r''',\quad
 \epsilon='''+texq(p['epsilon'])+r''',\quad c='''+texq(p['c'])+r''',\quad
 \delta='''+texq(p['delta'])+r''',\\
 \lambda=\tau+'''+texq(p['lam']-p['tau'])+r''',\quad
 \lambda'=\tau+'''+texq(p['lamp']-p['tau'])+r''',\quad
 \kappa='''+texq(p['kappa'])+r'''>2^{-20}.
\end{gathered}
\end{equation}'''
    text = text[:start]+block+text[end:]
    text = replace_once(text, r'1-17982/10^{10}',
        '1-'+texq(1-w['recurrence']['leaf']))
    return text.replace('sec:bulk-complex-guard','sec:nested-complex-guard')


def assembly_changes(text, w):
    p = w['parameters']; old = previous_assembly(); op = old['parameters']
    start = text.index(r'\subsection{A fixed rational choice}')
    end = text.index(r'\subsection{Input and transform sizes}',start)
    text = text[:start]+parameter_section(w)+text[end:]
    replacements = {
        'b^{'+exponent(op['epsilon'])+'}': 'b^{'+exponent(p['epsilon'])+'}',
        rf'd^{{{op["epsilon"].denominator}}}\le b^{{{op["epsilon"].numerator}}}':
            rf'd^{{{p["epsilon"].denominator}}}\le b^{{{p["epsilon"].numerator}}}',
        '$C_1='+exponent(op['C1'])+'$': '$C_1='+exponent(p['C1'])+'$',
        'O(d^{'+exponent(op['C1'])+'})':'O(d^{'+exponent(p['C1'])+'})',
        'p^{'+exponent((1-op['epsilon'])/2)+'}':'p^{'+exponent((1-p['epsilon'])/2)+'}',
        'p^{'+exponent(op['epsilon'])+'}':'p^{'+exponent(p['epsilon'])+'}',
        'p^{'+exponent(1-op['epsilon'])+'}':'p^{'+exponent(1-p['epsilon'])+'}',
        'p^{'+exponent(1-2*op['epsilon'])+'}':'p^{'+exponent(1-2*p['epsilon'])+'}',
        texq(old['minimum_margin'])+'>'+texq(op['kappa'])+r'=\kappa':
            texq(w['minimum_margin'])+'>'+texq(p['kappa'])+r'=\kappa',
        'G_*-\\kappa='+texq(old['absorption_gap']):'G_*-\\kappa='+texq(w['absorption_gap']),
        r'\epsilon C_1='+texq(op['epsilon']*op['C1']):
            r'\epsilon C_1='+texq(p['epsilon']*p['C1']),
        r'1-\epsilon C_1='+texq(1-op['epsilon']*op['C1']):
            r'1-\epsilon C_1='+texq(1-p['epsilon']*p['C1']),
    }
    for a,b in replacements.items(): text=replace_once(text,a,b)
    marker='The seven margins have the following exact values:'
    start=text.index(marker);end=text.index('Exact substitution',start)
    table=marker+'\n\\[\n\\begin{array}{c|c}\n'
    for i,value in enumerate(w['margins'].values(),1):
        table+=f'g_{i}&'+texq(value)+r'\\'+'\n'
    table+='\\end{array}\n\\]\n'
    return active_references(text[:start]+table+text[end:])


@lru_cache(maxsize=1)
def patched_files():
    w=verify.assembly(); p=w['parameters']; files=[]
    for name,old,text in previous.patched_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            text=replace_once(text,r'\kappa=7699/10^{10}>2^{-21}',
                r'\kappa='+exponent(p['kappa'])+r'>2^{-20}')
            if name.endswith('main.tex'):
                marker="The revised bound is conditional on the original manuscript's retained"
                text=replace_once(text,marker,
                    'This further expansion uses the dimension-32 finite producer, a nested\n'
                    'controlled basis for the reframed exits, additional data-corner blocks,\n'
                    'and every proper complex residual with the corresponding\n'
                    'path guard. Its contribution is by Zhihao Chen (jacklightChen),\n'
                    'with AI assistance recorded in the accompanying contribution statement.\n'+marker)
        elif name.endswith('04-swap.tex'):
            text+='\n'+bit_interface()
        elif name.endswith('05-layers.tex'):
            text+='\n'+layer_interface(text)
        elif name.endswith(('06-transforms.tex','07-resampling.tex')):
            text=active_references(text)
        elif name.endswith('08-assembly.tex'):
            text=assembly_changes(text,w)
        files.append((name,old,text))
    return tuple(files)


def all_sources(files=None):
    sources={str(p.relative_to(ROOT/'upstream')):p.read_text()
             for p in (ROOT/'upstream').rglob('*.tex')}
    sources.update({name:new for name,old,new in (patched_files() if files is None else files)})
    return sources


def audit(files=None):
    files=patched_files() if files is None else files
    names=[n for n,old,new in files]
    if len(names)!=len(set(names)): raise ValueError('Duplicate patched file')
    for name,old,new in files:
        if old!=(ROOT/'upstream'/name).read_text():
            raise ValueError('Patch is not based on pinned upstream: '+name)
    sources=all_sources(files); text='\n'.join(sources.values())
    labels=re.findall(r'\\label\{([^}]+)\}',text)
    if len(labels)!=len(set(labels)):
        raise ValueError('Duplicate labels: '+str(sorted({x for x in labels if labels.count(x)>1})))
    missing=set(re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',text))-set(labels)
    if missing: raise ValueError('Undefined internal references: '+str(sorted(missing)))
    for name in ('06-transforms.tex','08-assembly.tex'):
        t=sources['build/sections/'+name]
        if 'prop:nested-simultaneous-layer' not in t: raise ValueError('Stale active layer consumer: '+name)
    for name in ('06-transforms.tex','07-resampling.tex','08-assembly.tex'):
        t=sources['build/sections/'+name]
        if 'lem:batched-chunk-swap' in t or 'prop:batched-simultaneous-layer' in t:
            raise ValueError('Stale batched consumer: '+name)
    return dict(files=len(files),tex_sources=len(sources),unique_labels=len(labels),missing_references=0)


def patch_text(files=None):
    files=patched_files() if files is None else files
    return ''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),
        fromfile='a/'+name,tofile='b/'+name)) for name,old,new in files)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'patches/nested-source.patch')
    p.add_argument('--materialize',type=Path)
    args=p.parse_args();files=patched_files();result=audit(files)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(patch_text(files))
    if args.materialize:
        if args.materialize.resolve() in (ROOT.resolve(),(ROOT/'upstream').resolve()):
            raise ValueError('Materialization must use a separate directory')
        shutil.copytree(ROOT/'upstream',args.materialize,dirs_exist_ok=True)
        for name,old,new in files:
            dest=args.materialize/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(new)
    print('PASS nested patch: '+str(result))
    print('Wrote '+str(args.output))


if __name__=='__main__':main()
