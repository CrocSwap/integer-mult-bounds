#!/usr/bin/env python3
"""Integrate the controlled bulk-recursion result into the pinned manuscript.

The retained uniform-width proofs keep their original hypotheses and
exponents. Separate strengthened interfaces are appended, and consumers
are redirected to those interfaces. No producer or upstream file is edited.
"""
import argparse
import difflib
from pathlib import Path
import shutil

from make_patch import replace_once
from make_prime_field_patch import patched_files as retained_files
from batched_network import certificate


ROOT = Path(__file__).resolve().parents[1]


def note(name):
    return (ROOT / 'notes' / name).read_text()


def texq(q):
    if q.denominator == 1:
        return str(q.numerator)
    return rf'\frac{{{q.numerator}}}{{{q.denominator}}}'


def new_bit_interface():
    prefix = r'''
\subsection{Replacing the uniform recurrence by contiguous projector blocks}
The preceding power-width and arbitrary-width results are retained
baseline constructions with their stated uniform rank recurrence and
exponent $\tau_0=1-3/400000000$. We now change the recursive compilation.
The new result below does not assert the uniform inequality
$s/W<m^\tau$ at its stronger exponent.
'''
    body = '\n'.join(note(n) for n in (
        'projector-batching.tex', 'batched-bit-rank-accounting.tex',
        'controlled-projector-basis.tex', 'batched-bit-rows.tex'))
    suffix = r'''
\begin{lemma}[Batched arbitrary-width interchange]
\label{lem:batched-chunk-swap}
Put $\tau=1-246/10^9$. There is one fixed finite-alphabet multitape
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
Apply the controlled basis of
Section~\ref{sec:controlled-projector-basis} to the retained finite
ternary network. Choose the fixed prime only after the finite rational
factor tables have been formed, as in Lemma~\ref{lem:matrix-shear}.
Its controlled rank moment is strictly below one at the stated $\tau$.
The common-frame invariant of Proposition~\ref{prop:power-interchange}
still applies: the common conjugation fixes the endpoint difference $I$,
and only the compilation of individual edge shears changes.
The integer-width construction in Section~\ref{sec:mixed-width-rows}
then proves the required $O(Vu^\tau)$ bound, including self-supplied rows
and the one-time padding factor. All intermediate role values may be
arbitrary. The one-bit extension uses exactly the two layouts already
displayed after Lemma~\ref{lem:chunk-swap}, with this new equal-width
procedure substituted in their interchange step.
\end{proof}
'''
    return prefix + body + suffix


def new_layer_interface(retained):
    start = retained.index(r'\begin{proposition}[Simultaneous normalized butterfly layer]')
    active = retained[start:]
    active = replace_once(active,
        r'\begin{proposition}[Simultaneous normalized butterfly layer]',
        r'\begin{proposition}[Batched simultaneous normalized butterfly layer]')
    active = replace_once(active, r'\label{prop:simultaneous-layer}',
                          r'\label{prop:batched-simultaneous-layer}')
    active = replace_once(active,
        r'Fix $\tau=1-3/400000000$ and $\sigma=1-39/10^9$.',
        r'Fix $\tau=1-246/10^9$ and $\sigma=1-7/10^7$.')
    active = replace_once(active, r'C_1=5-4\beta+\zeta',
                          r'C_1=6/5-\beta/5+\zeta')
    active = replace_once(active, r''' C_0=\left\lceil\max\{128mB^2,18mB^2(1+1/\zeta)\}\right\rceil,
 \qquad B=s_{\rm c}+64(W_{\rm c}+m+1)^3,''', r''' E=64(W_{\rm c}+m+1)^3,\qquad
 C_{\rm dep}=1000(E+16m+1),\qquad
 C_0=\left\lceil128m(1+1/\zeta)C_{\rm dep}\right\rceil,''')
    active = replace_once(active, r'''The phase-frame construction reduces a group of $e$ selected bits to
$s_{\rm c}$ children on $e/m$ selected bits.  The row split gives
each child $1/W_{\rm c}$ of the parent's logical volume. The compact-control
selected-bit procedure supplies the binary basis changes. We verify
that its cost is uniform over the displayed bands for $d,r$.''', r'''The whole-residual construction of
Section~\ref{sec:bulk-complex-child} replaces the two selected classes
by one child per edge. Its mixed-width time moment at $\sigma$ is
strictly below one by Section~\ref{sec:batched-complex-parameters}.
For $e=mf+r_0$, $0\le r_0<m$, handle the remainder axes individually;
the true children have widths $f$, $21896f$, or $21168f$ according to
their type. Section~\ref{sec:mixed-complex-layer} supplies complete
role streams of exactly $1/W_{\rm c}$ of the parent's logical volume.
The compact-control selected-bit construction supplies each binary
basis change using Lemma~\ref{lem:batched-chunk-swap}. We verify
that its cost is uniform over the displayed bands for $d,r$.''')
    active = replace_once(active, r'''The row construction and the recurrence analysis
above give total time $O(Vd^{\lambda'})$ on fixed tapes, including
all padded and auxiliary streams.''', r'''The integer row construction and the weighted-tree analysis in
Section~\ref{sec:mixed-complex-layer} give total time
$O(Vd^{\lambda'})$ on fixed tapes, including all padded and auxiliary
streams, mixed-width children, and bounded local remainders.''')
    active = replace_once(active,
        'The guard-width calculation above bounds both denominator and magnitude',
        'The dependency-path calculation in Section~\\ref{sec:bulk-complex-guard}\n'
        'bounds both denominator and magnitude')
    prefix = r'''
\subsection{The active bulk-recursion construction}
The uniform recursion and its guard above remain a separate baseline,
with their original fixed exponents. We now use the stronger bit
interchange of Lemma~\ref{lem:batched-chunk-swap} and change the complex
children to whole residuals. The selected-bit movement lemmas and
Proposition~\ref{prop:compact-selected-addition} take the exponent of
their interchange routine as a parameter: their proofs use only its
$O(Vu^\tau)$ interface. They therefore apply with
$\tau=1-246/10^9$ in the following construction.
'''
    complex_parameters = note('batched-assembly.tex').split(
        r'\subsection{Final multiplication parameters and margins}')[0]
    body = '\n'.join(note(n) for n in (
        'batched-path-budget.tex', 'bulk-complex-guard.tex',
        'batched-complex-rows.tex'))
    return prefix + body + complex_parameters + active


def parameter_section(w):
    text = r'''\subsection{A fixed rational choice}

Use Lemma~\ref{lem:batched-chunk-swap} and
Proposition~\ref{prop:batched-simultaneous-layer}. Their rank moments,
not the retained uniform recurrences, certify the following exponents.
Choose
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-\frac{246}{10^9},\quad \sigma=1-\frac7{10^7},\quad
 \beta=\frac1{1000},\quad\zeta=\frac1{10000},\\
 C_1=\frac65-\frac\beta5+\zeta=\frac{11999}{10000},\quad
 \epsilon=\frac{7999999}{16000000},\quad c=1,\quad
 \delta=\frac1{10^{10}},\\
 \lambda=\tau+\frac1{10^{16}},\quad
 \lambda'=\tau+\frac2{10^{16}},\quad
 \kappa=\frac{6149999}{50000000000000}>2^{-23}.
\end{gathered}
\end{equation}
Since $\sigma<\tau$, the internal exponent is
$\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}=\tau$.
The leaf exponent is $\sigma+\beta(1-\sigma)=1-6993/10^{10}<\tau$.
The stopping test is $e^{1000}<d$.
Section~\ref{sec:bulk-complex-guard} proves the displayed guard exponent
and its fixed $C_0$. The reservation exponent $\max\{1-c,0\}$ is zero;
in particular $c=1$ is permitted. The integer mixed-width row depth has
size $O(\log d)$ and does not change this exponent.

Here are all twenty-nine strict parameter slacks used in the exact
certificate. Every entry in the right column is positive. In the table,
$\chi$ has the value just given and $h_{\rm leaf}=\sigma+\beta(1-\sigma)$.
\begin{longtable}{@{}ll@{}}
\toprule Condition slack & Exact value\\\midrule
\endhead
'''
    labels = {
        'tau_positive': r'\tau', 'tau_below_one': r'1-\tau',
        'sigma_positive': r'\sigma', 'sigma_below_one': r'1-\sigma',
        'c_positive': 'c', 'epsilon_positive': r'\epsilon',
        'beta_positive': r'\beta', 'beta_below_one': r'1-\beta',
        'lambda_above_tau': r'\lambda-\tau',
        'lambda_above_sigma': r'\lambda-\sigma',
        'lambda_below_one': r'1-\lambda',
        'packed_overhead': r'\lambda-\chi',
        'lambda_prime_above_lambda': r"\lambda'-\lambda",
        'leaf_cost': r"\lambda'-h_{\rm leaf}",
        'lambda_prime_below_one': r"1-\lambda'",
        'guard_width': r'1-\epsilon C_1',
        'crt_layout': r'(1-\epsilon)(1-\tau)',
        'prefix_cost': r'1-\epsilon(1+c)',
        'scalar_cost': r'1-\delta-\epsilon',
        'delta_positive': r'\delta',
        'delta_below_one_eighth': r'1/8-\delta',
        'prime_interval_growth': r'1-2\epsilon\quad\text{(prime intervals)}',
        'K_smaller_than_ell': r'1-\epsilon(1+c)\quad(K=o(\ell))',
        'K_dominates_log_p': r'\epsilon c',
        'r_superpolynomial': r'1-\epsilon',
        'kappa_positive': r'\kappa',
        'gaussian_cost': r'1-\delta-2\epsilon',
        'alpha_squared_theta_growth': r'1-2\epsilon\quad(\alpha^2\theta)',
        'reserved_axes': r"\lambda'-\max\{1-c,0\}",
    }
    assert set(labels) == set(w['constraints'])
    for name, value in w['constraints'].items():
        text += '$'+labels[name]+'$ & $'+texq(value)+r'$\\'+'\n'
    text += '\\bottomrule\n\\end{longtable}\n\n'
    return text


def assembly_changes(text, w):
    start = text.index(r'\subsection{A fixed rational choice}')
    end = text.index(r'\subsection{Input and transform sizes}', start)
    text = text[:start] + parameter_section(w) + text[end:]
    replacements = {
        r'b^{4999/10000}': r'b^{7999999/16000000}',
        r'd^{10000}\le b^{4999}': r'd^{16000000}\le b^{7999999}',
        r'$C_1=49961/10000$': r'$C_1=11999/10000$',
        r'O(d^{19601/10000})': r'O(d^{11999/10000})',
        r'p^{5001/20000}': r'p^{8000001/32000000}',
        r'p^{49985001/10^8}': r'p^{7999999/16000000}',
        r'p^{5001/10000}': r'p^{8000001/16000000}',
        r'p^{1/5000}': r'p^{1/8000000}',
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
 \epsilon C_1=\frac{95991988001}{160000000000}<1,
 \qquad 1-\epsilon C_1=\frac{64008011999}{160000000000}.
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


def active_references(text):
    return text.replace('lem:chunk-swap', 'lem:batched-chunk-swap').replace(
        'prop:simultaneous-layer', 'prop:batched-simultaneous-layer')


def patched_files():
    result = certificate()
    w = result['assembly']
    seen = set()
    for name, old, text in retained_files():
        seen.add(name)
        if name.endswith(('main.tex', '00-introduction.tex')):
            text = replace_once(text, r'\kappa=373/10^{11}>2^{-28}',
                r'\kappa=6149999/50000000000000>2^{-23}')
            if name.endswith('main.tex'):
                text = replace_once(text,
                    r'\small Ternary five-subset contribution: Zhihao Chen (jacklightChen)}',
                    r'\small Ternary five-subset contribution: Zhihao Chen (jacklightChen)\\'+'\n'+
                    r'\small Bulk recursion: icekylinx (with OpenAI GPT-6 Astra and Codex assistance)}')
                text = replace_once(text,
                    "The revised bound is conditional on the original manuscript's retained",
                    'The present extension batches controlled rational projector blocks and\n'
                    'whole complex residuals, supplies integer-width recursion with rows,\n'
                    'and uses a dependency-path precision guard. The bulk-recursion contribution\n'
                    'is by icekylinx, with substantial OpenAI GPT-6 Astra assistance;\n'
                    'review corrections and integration used OpenAI Codex assistance.\n'
                    "The revised bound is conditional on the original manuscript's retained")
        elif name.endswith('03-motifs.tex'):
            text = replace_once(text,
                'The selected exponents used from now on are',
                'The following exponents certify the retained uniform-width baseline:')
        elif name.endswith('04-swap.tex'):
            text += new_bit_interface()
        elif name.endswith('05-layers.tex'):
            text = replace_once(text, r'$m_{\rm b}=125000$', r'$m_{\rm b}=21952$')
            text += new_layer_interface(text)
        elif name.endswith('07-resampling.tex'):
            text = active_references(text)
        elif name.endswith('08-assembly.tex'):
            text = active_references(assembly_changes(text, w))
        yield name, old, text
    # The transform source was unchanged by the retained patch chain, but
    # its fixed-parameter contract must point at the new layer interface.
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
    parser.add_argument('--output', type=Path, default=ROOT/'patches/batched-23.patch')
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
    print('Wrote '+str(args.output)+'; retained uniform proofs plus active bulk interfaces.')


if __name__ == '__main__':
    main()
