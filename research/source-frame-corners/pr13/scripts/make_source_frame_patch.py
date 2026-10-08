#!/usr/bin/env python3
"""Integrate auxiliary source frames into the bulk-recursion manuscript patch.

Starts from the PR #10 integration (make_batched_patch.py), adds the
source-frame interchange sections and the third complex residual class, and
replaces the final parameters. No producer or upstream file is edited.
"""
import argparse
import difflib
from pathlib import Path
import shutil

from make_patch import replace_once
from make_prime_field_patch import patched_files as retained_files
from make_batched_patch import (active_references, new_bit_interface, new_layer_interface,
                                parameter_section as batched_parameter_section, texq)
from source_frame_network import certificate

ROOT = Path(__file__).resolve().parents[1]
KAPPA_TEX = r'\kappa=7699/10^{10}>2^{-21}'


def note(name):
    return (ROOT / 'notes' / name).read_text()


def bit_changes(text):
    marker = r'\begin{lemma}[Batched arbitrary-width interchange]'
    text = replace_once(text, marker, note('source-frame-bit.tex') + '\n' + marker)
    text = replace_once(text, r'Put $\tau=1-246/10^9$. There is one fixed finite-alphabet multitape',
                        r'Put $\tau=1-154/10^8$. There is one fixed finite-alphabet multitape')
    text = replace_once(text, r'''$246/10^9$, which is the value used in the final assembly.''',
                        r'''$246/10^9$. Section~\ref{sec:source-frame-bit-moment} raises it
further to $154/10^8$, which is the value used in the final assembly.''')
    text = replace_once(text, r'''Apply the controlled basis of
Section~\ref{sec:controlled-projector-basis} to the retained finite
ternary network.''', r'''Give the stage-two auxiliary roles of the retained finite ternary
network the source frames of Section~\ref{sec:scratch-source-frames},
and apply the common basis of Lemma~\ref{lem:source-frame-basis}.''')
    text = replace_once(text, r'Its controlled rank moment is strictly below one at the stated $\tau$.',
                        r'''Its rank moment, computed in Section~\ref{sec:source-frame-bit-moment},
is strictly below one at the stated $\tau$.''')
    text = replace_once(text, r'''and only the compilation of individual edge shears changes.''',
                        r'''and only the compilation of individual edge shears changes.
Lemma~\ref{lem:scratch-source-frames} shows that the new auxiliary source
and sink matrices preserve every endpoint difference.''')
    return text


def layer_changes(text):
    text = replace_once(text, r'''They therefore apply with
$\tau=1-246/10^9$ in the following construction.''', r'''They therefore apply with
$\tau=1-154/10^8$ in the following construction.''')
    text = replace_once(text, 'All other edges continue to use their old one-direction children.',
                        r'Section~\ref{sec:source-frame-complex} adds a third class. All other edges'
                        '\ncontinue to use their old one-direction children.')
    text = replace_once(text, r''' 1-\frac{7999999}{16000000}C_1
   =\frac{64008011999}{160000000000}>0.''', r''' 1-\frac{499999}{10^6}C_1
   =\frac{4000511999}{10^{10}}>0.''')
    marker = r'\begin{proposition}[Batched simultaneous normalized butterfly layer]'
    text = replace_once(text, marker, note('source-frame-complex.tex') + '\n' + marker)
    text = replace_once(text, r'Fix $\tau=1-246/10^9$ and $\sigma=1-7/10^7$.',
                        r'Fix $\tau=1-154/10^8$ and $\sigma=1-18/10^7$.')
    text = replace_once(text, r'''replaces the two selected classes
by one child per edge. Its mixed-width time moment at $\sigma$ is
strictly below one by Section~\ref{sec:batched-complex-parameters}.''', r'''replaces the three selected classes
by one child per edge. Its mixed-width time moment at $\sigma$ is
strictly below one by Section~\ref{sec:source-frame-complex}.''')
    text = replace_once(text, r'the true children have widths $f$, $21896f$, or $21168f$ according to',
                        r'the true children have widths $f$, $21896f$, $21168f$, or $21141f$ according to')
    return text


def parameter_section(w):
    text = batched_parameter_section(w)
    old_display = text[text.index(r'\begin{equation}\label{eq:fixed-parameters}'):
                       text.index(r'\end{equation}')+len(r'\end{equation}')]
    new_display = r'''\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-\frac{154}{10^8},\quad \sigma=1-\frac{18}{10^7},\quad
 \beta=\frac1{1000},\quad\zeta=\frac1{10000},\\
 C_1=\frac65-\frac\beta5+\zeta=\frac{11999}{10000},\quad
 \epsilon=\frac{499999}{10^6},\quad c=1,\quad
 \delta=\frac1{10^{10}},\\
 \lambda=\tau+\frac1{10^{16}},\quad
 \lambda'=\tau+\frac2{10^{16}},\quad
 \kappa=\frac{7699}{10^{10}}>2^{-21}.
\end{gathered}
\end{equation}'''
    text = text.replace(old_display, new_display)
    text = replace_once(text, r'Use Lemma~\ref{lem:batched-chunk-swap} and',
                        r'Use Lemma~\ref{lem:batched-chunk-swap}, with the auxiliary source frames of'
                        '\nSection~\\ref{sec:scratch-source-frames}, and')
    text = replace_once(text, r'1-6993/10^{10}<\tau', r'1-17982/10^{10}<\tau')
    return text


def assembly_changes(text, w):
    start = text.index(r'\subsection{A fixed rational choice}')
    end = text.index(r'\subsection{Input and transform sizes}', start)
    text = text[:start] + parameter_section(w) + text[end:]
    replacements = {
        r'b^{4999/10000}': r'b^{499999/1000000}',
        r'd^{10000}\le b^{4999}': r'd^{1000000}\le b^{499999}',
        r'$C_1=49961/10000$': r'$C_1=11999/10000$',
        r'O(d^{19601/10000})': r'O(d^{11999/10000})',
        r'p^{5001/20000}': r'p^{500001/2000000}',
        r'p^{49985001/10^8}': r'p^{499999/1000000}',
        r'p^{5001/10000}': r'p^{500001/1000000}',
        r'p^{1/5000}': r'p^{1/500000}',
        r'\frac{934813}{250000000000000}>\frac{373}{10^{11}}=\kappa':
            texq(w['minimum_margin'])+'>'+texq(w['parameters']['kappa'])+r'=\kappa',
    }
    for old, new in replacements.items():
        text = replace_once(text, old, new)
    text = replace_once(text, r'\quad K=\lfloor d^c\rfloor.', r'\quad K=\lfloor d^c\rfloor=d.')
    text = replace_once(text,
        r'The same procedure computes $K$ and all other fixed rational powers.',
        r'Here $K=d$ exactly; the same comparison method computes all other fixed rational powers.')
    text = replace_once(text,
        'deterministic repair, row padding and removal, all base-$m$ groups,',
        'deterministic repair, row padding and removal, all mixed-width children,')
    text = replace_once(text,
        'depth $O(\\log p)$, and the number of their rounds and base-$m$ groups',
        'depth $O(\\log p)$, and the number of their rounds and root invocations')
    text = replace_once(text,
        'Proposition~\\ref{prop:power-interchange} gives',
        'Section~\\ref{sec:mixed-width-rows} gives')
    text = replace_once(text,
        r'The guard is $O(d^{11999/10000})=o(p)$, while',
        r'''The guard is $O(d^{11999/10000})=o(p)$ because
\[
 \epsilon C_1=\frac{5999488001}{10000000000}<1,
 \qquad 1-\epsilon C_1=\frac{4000511999}{10000000000}.
\]
Furthermore,''')
    margin_table = '\nThe seven margins have the following exact values:\n\\[\n\\begin{array}{c|c}\n'
    for index, (name, value) in enumerate(w['margins'].items(), start=1):
        margin_table += rf'g_{index}&'+texq(value)+r'\\'+'\n'
    margin_table += '\\end{array}\n\\]\n'
    marker = 'Exact substitution in the unchanged seven-term assembly accounting gives'
    text = replace_once(text, marker, margin_table+marker)
    text = replace_once(text,
        'The new reservation, compact movement and repair costs are all included',
        'The final strict absorption gap is\n\\[\n G_*-\\kappa='
        +texq(w['absorption_gap'])+'>0.\n\\]\n'
        'The new reservation, compact movement and repair costs are all included')
    return text


def patched_files():
    result = certificate()
    w = result['assembly']
    seen = set()
    for name, old, text in retained_files():
        seen.add(name)
        if name.endswith(('main.tex', '00-introduction.tex')):
            text = replace_once(text, r'\kappa=373/10^{11}>2^{-28}', KAPPA_TEX)
            if name.endswith('main.tex'):
                text = replace_once(text,
                    r'\small Ternary five-subset contribution: Zhihao Chen (jacklightChen)}',
                    r'\small Ternary five-subset contribution: Zhihao Chen (jacklightChen)\\'+'\n'+
                    r'\small Bulk recursion: icekylinx (with OpenAI GPT-6 Astra and Codex assistance)\\'+'\n'+
                    r'\small Auxiliary source frames: eumemic (with Claude, Anthropic)}')
                text = replace_once(text,
                    "The revised bound is conditional on the original manuscript's retained",
                    'The present extension batches controlled rational projector blocks and\n'
                    'whole complex residuals, supplies integer-width recursion with rows,\n'
                    'and uses a dependency-path precision guard. The bulk-recursion contribution\n'
                    'is by icekylinx, with substantial OpenAI GPT-6 Astra assistance;\n'
                    'review corrections and integration used OpenAI Codex assistance.\n'
                    'Stage-two auxiliary roles then start in the frame of their first gate,\n'
                    'which concentrates their rank in one batched exit edge, and the complex\n'
                    'network applies a third residual class whole. That contribution is by\n'
                    'eumemic, with substantial assistance from Claude (Anthropic).\n'
                    "The revised bound is conditional on the original manuscript's retained")
        elif name.endswith('03-motifs.tex'):
            text = replace_once(text,
                'The selected exponents used from now on are',
                'The following exponents certify the retained uniform-width baseline:')
        elif name.endswith('04-swap.tex'):
            text = bit_changes(text + new_bit_interface())
        elif name.endswith('05-layers.tex'):
            text = replace_once(text, r'$m_{\rm b}=125000$', r'$m_{\rm b}=21952$')
            text = layer_changes(text + new_layer_interface(text))
        elif name.endswith('07-resampling.tex'):
            text = active_references(text)
        elif name.endswith('08-assembly.tex'):
            text = active_references(assembly_changes(text, w))
        yield name, old, text
    name = 'build/sections/06-transforms.tex'
    if name in seen:
        raise ValueError('Unexpected retained transform patch; integrate explicitly')
    old = (ROOT / 'upstream' / name).read_text()
    yield name, old, active_references(old)


def patch_text(files=None):
    files = list(patched_files()) if files is None else files
    return ''.join(''.join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile='a/'+name, tofile='b/'+name)) for name, old, new in files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'patches/source-frame-21.patch')
    parser.add_argument('--materialize', type=Path,
                        help='Copy the complete pinned source and apply the generated changes here')
    args = parser.parse_args()
    files = list(patched_files())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(patch_text(files))
    if args.materialize:
        if args.materialize.resolve() in (ROOT.resolve(), (ROOT/'upstream').resolve()):
            raise ValueError('Materialization must use a separate directory')
        shutil.copytree(ROOT/'upstream', args.materialize, dirs_exist_ok=True)
        for name, old, new in files:
            path = args.materialize/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new)
    print('Wrote '+str(args.output)+'; batched interfaces plus auxiliary source frames.')


if __name__ == '__main__':
    main()
