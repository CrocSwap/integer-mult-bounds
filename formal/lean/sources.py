#!/usr/bin/env python3
"""Pairs every Lean declaration with the source lines it formalizes.

The table below is the single source of `SOURCES.md`. `check()` verifies that

* every theorem and definition in `KappaCheck/*.lean` appears in the table, and
  every name in the table exists in the Lean files;
* every cited line range exists and still contains its quoted anchor text;
* every cited certificate value equals the literal written in the Lean
  declaration, and that literal occurs in the declaration.

Run `python3 formal/lean/sources.py` to check, `--write` to regenerate SOURCES.md.
"""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
LEAN = Path(__file__).resolve().parent
COMMIT = '6e564879f51ae16f23d392e9e196c605f36d90df'


@dataclass(frozen=True)
class Line:
    """Lines `first..last` of `path` contain `anchor` (whitespace-normalized)."""
    path: str
    first: int
    last: int
    anchor: str


@dataclass(frozen=True)
class Key:
    """Certificate value at `keys` equals the Lean literal `lean`."""
    path: str
    keys: tuple
    lean: str


NC = 'notes/compact-control-note.tex'
NI = 'notes/independent-complex.tex'
NG = 'notes/compact-control-guard.tex'
NL = 'notes/compact-control-layout.tex'
NM = 'notes/compact-control-movement.tex'
NPC = 'notes/paired-construction.tex'
NPP = 'notes/parameter-note.tex'
NNA = 'notes/nonadjacent-axis-note.tex'
NPN = 'notes/paired-note.tex'
P3 = 'upstream/build/sections/03-motifs.tex'
P5 = 'upstream/build/sections/05-layers.tex'
P8 = 'upstream/build/sections/08-assembly.tex'
CJ = 'certificates/compact-control-layer.json'
PJ = 'certificates/paired-network.json'
QJ = 'certificates/parameters.json'


def main_(*k):
    return ('main',)+k


ROWS = [
    # -- Network.lean: the paper's count formulas ---------------------------
    ('Network', ['v', 'N', 'm'], 'v = C(h,3), N = v³, m = h³',
     [Line(P3, 16, 17, r'v=\binom h3'), Line(P3, 16, 17, r'N=v^3'),
      Line(P3, 16, 17, r'm=h^3'), Line(NI, 8, 8, r'm_{\rm c}=15625')], ''),
    ('Network', ['I'], 'I = 3v² invocations',
     [Line(P3, 31, 37, r'there are $v^2$ separate invocations at each stage'),
      Line(P3, 37, 37, r'I=3v^2')], ''),
    ('Network', ['zb', 'zc'], 'z_b = 3·C(h−3,2), z_c = C(h−3,3) + 3(h−3)',
     [Line(P3, 130, 131, r'z_{\rm b}=3\binom{97}{2}'),
      Line(P3, 130, 131, r'z_{\rm c}=\binom{97}{3}+3\cdot97'),
      Line(NI, 15, 15, r'z_{\rm c}=\binom{22}{3}+66')],
     'The paper and the note give only the h = 100 and h = 25 instances (97 = h−3, 22 = h−3); '
     'the general-h form is inferred and cross-checked at h = 25, 46, 100.'),
    ('Network', ['Wb', 'Wc'], 'W = 2N + I(vz + c), c_b = h, c_c = h + 1',
     [Line(P3, 136, 136, r'$c_{\rm b}=100$ and $c_{\rm c}=101$'),
      Line(P3, 139, 141, r'W_{\rm b}&=2N+I(vz_{\rm b}+c_{\rm b})'),
      Line(P3, 139, 141, r'W_{\rm c}&=2N+I(vz_{\rm c}+c_{\rm c})'),
      Line(NI, 14, 14, r'W_{\rm c}=2v_{\rm c}^3+3v_{\rm c}^2(v_{\rm c}z_{\rm c}+26)')],
     'c_b = h, c_c = h + 1 inferred from 100/101 at h = 100 and 26 at h = 25.'),
    ('Network', ['Lb', 'Lc'], 'L = I·c·h',
     [Line(P3, 354, 357, r'L=Ich'), Line(NI, 15, 15, r'L_{\rm c}=3v_{\rm c}^2\cdot25\cdot26')], ''),
    ('Network', ['sb', 'sc'], 's_b = W m − N + 2L, s_c = W m − 2N + 2L',
     [Line(P3, 505, 505, r'=W_{\rm b}m-N+2L_{\rm b}'),
      Line(P3, 576, 576, r's_{\rm c}=W_{\rm c}m-2N+2L_{\rm c}'),
      Line(NI, 42, 42, r's_{\rm c}=W_{\rm c}m_{\rm c}-2N_{\rm c}+2L_{\rm c}')],
     'Written as W m + 2L − N in ℕ; `sb_eq`/`sc_eq` prove it equals the ℤ form.'),
    ('Network', ['paper_h100'], 'the paper\'s h = 100 counts',
     [Line(P3, 16, 16, r'v=\binom h3=161700'), Line(P3, 37, 37, '78440670000'),
      Line(P3, 130, 131, '13968'), Line(P3, 130, 131, '147731'),
      Line(P3, 139, 142, '177176569091445000000'),
      Line(P3, 139, 142, '1873807244643542670000'),
      Line(P3, 505, 506, '177176569088785861287000000'),
      Line(P3, 576, 577, '1873807244636671267308000000')], ''),
    ('Network', ['paper_h100_deficits'], 'the paper\'s η_b, η_c at h = 100',
     [Line(P3, 673, 678, r'\frac{339}{22587335000000}'),
      Line(P3, 673, 678, r'\frac{73}{19906842167500}')], ''),
    ('Network', ['parameter_note_h46'], 'the h = 46 counts',
     [Line(NPP, 216, 218, 'm=97336'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'Wb'), '28434979789999200'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'Wc'), '130865855373752400'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'sb'), '2767747192266968049600'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'sc'), '12737958894652805035200'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'Lb'), '1462784875200'),
      Key(QJ, ('networks', 'improved_h46', 'counts', 'Lc'), '1494584546400')],
     'Not used by the κ = 83/10¹² chain; a third data point for the formulas.'),
    ('Network', ['parameter_note_h46_deficits'], 'η_b = 9/43518487588, η_c = 7/22253827054',
     [Line(NPP, 218, 219, r'\eta_b=\frac9{43518487588}'),
      Line(NPP, 218, 219, r'\eta_c=\frac7{22253827054}')], ''),
    ('Network', ['costX', 'costY'], 'data-wire residual dimensions per stage',
     [Line(P3, 378, 379, r'X:\ 2\to3&P\otimes t_X^\perp&h-1'),
      Line(P3, 382, 384, r'Y:\ 4\to5&P\otimes t_Y^\perp&h-1')],
     'Rows X: in→2, 2→3 and Y: 0→1, 4→5 of the residual table; other data edges have residual 0.'),
    ('Network', ['costCenter', 'costSide'], 'central- and side-wire residual dimensions',
     [Line(P3, 385, 388, r'\mathrm{center}:\ 3\to4&P\otimes F&h'),
      Line(P3, 389, 393, r'\mathrm{side}:\ 2\to5&P\otimes\langle t_X,t_Y\rangle^\perp&h-2'),
      Line(P3, 394, 395, r'ah(f-1)')], ''),
    ('Network', ['data_wires'], 'X grows 1 → h³ (+1 source projection); Y grows 0 → h³ − 1',
     [Line(P3, 289, 291, r'At stage 1 they start at $U_a$ on $X_a$'),
      Line(P3, 367, 367, r'Write $a=\dim A=h^{j-1}$ and $f=h^{3-j}$')], ''),
    ('Network', ['scratch_wires'], 'a central wire costs m + 2h, a side wire m',
     [Line(P3, 385, 395, r'\mathrm{center}:\ \mathrm{source}\to1&B\otimes F&(a-1)h'),
      Line(P3, 415, 416, r'Label dimension is nondecreasing along every edge except center $3\to4$')], ''),
    ('Network', ['rank_sums'], 'summing per-wire costs gives W m − N + 2L and W m − 2N + 2L',
     [Line(P3, 356, 360, r'=Wm-2N+2L'),
      Line(P3, 420, 425, r'replacing signed changes by absolute changes adds $2L$'),
      Line(P3, 500, 505, r'=W_{\rm b}m-N+2L_{\rm b}')], ''),
    ('Network', ['sb_eq', 'sc_eq'], 'the ℕ closed forms equal the paper\'s',
     [Line(P3, 505, 505, r'=W_{\rm b}m-N+2L_{\rm b}'),
      Line(P3, 576, 576, r's_{\rm c}=W_{\rm c}m-2N+2L_{\rm c}')], ''),
    # -- Certificates.lean ------------------------------------------------
    ('Certificates', ['exponent_certificate'], 'x·L ≤ η, log m < L ⇒ m(1 − η) < m^(1−x)',
     [Line(P3, 686, 691, r'm\exp(-2^{-50}\log m)'),
      Line(NI, 50, 51, r'The inequality $e^{-x}>1-x$ then yields'),
      Line(NPC, 164, 164, r'The inequality $e^{-x}>1-x$ therefore proves')], ''),
    # -- CrocSwap.lean A: complex network h = 25 ---------------------------
    ('CrocSwap', ['log_le_of_pow', 'log_split', 'L25', 'log_15625'],
     'helper: log 15625 < L25 ≈ 9.6566', [], 'Helper, sharper than the note; no source line.'),
    ('CrocSwap', ['log_15625_note'], 'log m_c < 966/100',
     [Line(NI, 49, 49, r'\log m_{\rm c}<966/100')], ''),
    ('CrocSwap', ['complex25_counts'], 'h = 25 counts and L_c < N_c',
     [Line(NI, 8, 8, r'N_{\rm c}=12167000000'), Line(NI, 11, 11, r'W_{\rm c}=58645352620000'),
      Line(NI, 11, 12, r's_{\rm c}=916333630984500000'),
      Line(NI, 11, 11, r'L_{\rm c}=10315500000'), Line(NI, 46, 46, r'$L_{\rm c}<N_{\rm c}$'),
      Key(CJ, ('complex_counts', 'Wc'), '58645352620000'),
      Key(CJ, ('complex_counts', 'sc'), '916333630984500000'),
      Key(CJ, ('complex_counts', 'Lc'), '10315500000'),
      Key(CJ, ('complex_counts', 'N'), '12167000000')], ''),
    ('CrocSwap', ['complex25_eta'], 'η_c = 14/3464399375',
     [Line(NI, 42, 44, r'=\frac{14}{3464399375}>0'),
      Key(CJ, ('complex_counts', 'eta_c'), '14 / 3464399375')], ''),
    ('CrocSwap', ['complex25_exponent'], 's_c/W_c < 15625^σ, 1 − σ = 418/10¹²',
     [Line(NI, 20, 21, r'$\sigma=1-418/10^{12}$'),
      Line(NI, 49, 51, r'$\eta_{\rm c}>(418/10^{12})(966/100)$')], ''),
    # -- B: paired bit network h = 50 ---------------------------------------
    ('CrocSwap', ['log_125000'], 'log 125000 < L₀ = 11737/1000',
     [Line(NPC, 151, 151, r'$L_0=11737/1000$'), Line(NPC, 162, 162, r'<L_0'),
      Key(PJ, ('log_m_upper',), '11737 / 1000')],
     'Proved with log 2 and log y ≤ y − 1 rather than the note\'s series S(x).'),
    ('CrocSwap', ['R50'], 'R = 509194 side roles per invocation',
     [Line(NPC, 63, 63, r'c+q=509194'),
      Key(PJ, ('bit_counts', 'side_roles_per_invocation'), '509194')],
     'Taken as given: produced by the circuit, not re-derived in Lean.'),
    ('CrocSwap', ['Wp', 'Lp', 'Dp', 'sp'], 'W = 2N + 2v²(R + h), L = 3v²h², s = W m − N + 6v²h²',
     [Line(NPC, 134, 134, r'=2N+2v^2(R+h)'),
      Line(NPC, 135, 135, r'=W_{\rm b}^{\rm pair}m-N+6v^2h^2'),
      Line(NPC, 141, 142, r'The total decreasing dimension is $3v^2h^2$')],
     'Lean writes s = W m − D with D = N − 2L, the same as line 135.'),
    ('CrocSwap', ['bit50_counts'], 'h = 50 counts',
     [Line(NPC, 3, 3, r'v=\binom h3=19600'), Line(NPC, 3, 3, r'm=h^3=125000'),
      Line(NPC, 134, 134, '406321422080000'), Line(NPC, 136, 136, '50790175992864000000'),
      Line(NPC, 137, 137, '1767136000000'),
      Key(PJ, ('bit_counts', 'W'), '406321422080000'),
      Key(PJ, ('bit_counts', 's'), '50790175992864000000'),
      Key(PJ, ('bit_counts', 'D'), '1767136000000')], ''),
    ('CrocSwap', ['bit50_eta'], 'η_b = 23/661055000',
     [Line(NPC, 154, 154, r'\frac{23}{661055000}>aL_0'),
      Key(PJ, ('bit_counts', 'eta'), '23 / 661055000')], ''),
    ('CrocSwap', ['bit50_exponent'], 's_b/W_b < 125000^τ, 1 − τ = 296/10¹¹',
     [Line(NPC, 151, 154, r'\frac{23}{661055000}>aL_0'),
      Line(NPC, 166, 166, r'\tau=1-\frac{296}{10^{11}}')], ''),
    # -- C: guard ---------------------------------------------------------
    ('CrocSwap', ['Eg', 'Bg', 'βq', 'ζq', 'C1q', 'C0n'], 'E, B, β, ζ, C₁, C₀',
     [Line(NG, 7, 7, r'E=64(W+m+1)^3,\quad B=s+E,\quad C_1=5-4\beta+\zeta'),
      Line(NG, 10, 10, r'C_0=\left\lceil\max\{128mB^2,18mB^2(1+1/\zeta)\}\right\rceil'),
      Line(NC, 69, 69, r'\beta=\frac1{1000},\quad\zeta=\frac1{10000}'),
      Line(P5, 697, 697, r'E=64(W+m+1)^3,\qquad B=s+E'),
      Key(CJ, main_('guard', 'C0'),
          '468702768364541266454706053568350325710944743089798636762052552973306387134258934583461152000000'),
      Key(CJ, main_('guard', 'zeta'), '1 / 10000'), Key(CJ, main_('guard', 'beta'), '1 / 1000')], ''),
    ('CrocSwap', ['guard_constants'], 'E, B values; 2 ≤ s < m⁵; s(8+E) ≤ 9B²; C₀ and the layer inequality',
     [Line(NG, 4, 4, r'$2\le s<m^5$'),
      Line(NG, 27, 27, r'A(e)\le s(8+E)d^{5-4\beta}\le9B^2d^{5-4\beta}'),
      Line(NG, 36, 37, r'A_{\rm layer}\le9mB^2(1+1/\zeta)d^{C_1}+18d'),
      Line(NI, 52, 52, r'$2\le s_{\rm c}<m_{\rm c}^5$'),
      Key(CJ, main_('guard', 'E'), '12908648646364723556470023518520280006040064'),
      Key(CJ, main_('guard', 'B'), '12908648646364723556470024434853910990540064'),
      Key(CJ, main_('guard', 'C1'), '49961 / 10000')],
     'Constant inequalities only; the depth recursion for A(e) is the written proof.'),
    # -- Guard.lean: the depth recursion of the guard note ---------------------
    ('Guard', ['geom_le', 'unroll', 'one_lt_log_three'], 'helpers: Σ s^i ≤ s^k, unrolling k levels, log 3 > 1',
     [Line(NG, 13, 18, r'A(e)\le sA(e/m)+E\quad\hbox{internally},\qquad A(e)\le8e')],
     'The recursion itself is the note\'s assumption, carried as hypotheses.'),
    ('Guard', ['root_bound'], 'every root e ≤ d has A(e) ≤ s(8+E)d^(5−4β)',
     [Line(NG, 23, 24, r'the number of internal levels is at most $(1-\beta)\log_m d+1$'),
      Line(NG, 26, 27, r's^j\le s d^{5(1-\beta)}'),
      Line(NG, 27, 27, r'A(e)\le s(8+E)d^{5-4\beta}'),
      Line(NG, 29, 29, r'A root that is already a leaf also satisfies this bound')],
     'For every A satisfying the two recursion hypotheses; uses 2 ≤ s < m⁵.'),
    ('Guard', ['pieces_le'], '(m−1)(1+⌊log_m d⌋) ≤ m(1+1/ζ)d^ζ',
     [Line(NG, 29, 31, r'$m(1+1/\zeta)d^\zeta$ base-$m$ pieces'),
      Line(NG, 31, 31, r'$\log d\le d^\zeta/\zeta$ and $\log m>1$'),
      Line(P5, 673, 673, r'There are at most \((m-1)(1+\lfloor\log_m d\rfloor)\) pieces')], ''),
    ('Guard', ['layer_bound'], 'A_layer ≤ 9mB²(1+1/ζ)d^C₁ + 18d ≤ C₀d^C₁',
     [Line(NG, 32, 34, r'so their depth is at most $8d$'),
      Line(NG, 33, 34, r'add at most $\lfloor D/2\rfloor+9$ units'),
      Line(NG, 36, 37, r'A_{\rm layer}\le9mB^2(1+1/\zeta)d^{C_1}+18d \le C_0d^{C_1}')],
     'Pieces, individual axes and outer phases are composed sequentially, so depths add.'),
    ('Guard', ['guard_instance'], 'the h = 25, β = 1/1000, ζ = 1/10000 instance',
     [Line(NG, 4, 4, r'Assume $m\ge3$ and $2\le s<m^5$'),
      Line(NC, 69, 69, r'\beta=\frac1{1000},\quad\zeta=\frac1{10000}')],
     'All constant hypotheses discharged by `guard_constants`.'),
    # -- Frames.lean: the paired circuit's label algebra --------------------
    ('Frames', ['form', 'ind', 'sum_ind', 'sum_ind_mul'], 'the form I − J/9 and triple indicators',
     [Line(NPC, 88, 88, r'Use the original rational form $I-J/9$ on $F=\mathbb Q^{50}$')],
     'Stated for every h.'),
    ('Frames', ['form_ind', 'neighbors_orthogonal'], 'B(t_S, t_T) = |S ∩ T| − 1, so neighbors are orthogonal',
     [Line(NPC, 101, 102, r'has $U_z\subset t_T^\perp$, because every contributing triple is a neighbor')],
     'With the checker\'s exact output supports, this gives U_z ⊂ t_T^⊥.'),
    ('Frames', ['common', 'span_le_common', 'form_self_common', 'form_pos_common', 'label_anisotropic'],
     'spans through a common point satisfy Σu = 3uᵢ and B(u,u) = Σ_{j≠i} uⱼ² > 0',
     [Line(NPC, 93, 94, r'Every retained node is a sum from an original common-point group'),
      Line(NPC, 96, 97, r'\sum_j u_j=3u_i,\qquad \langle u,u\rangle=\sum_{j\ne i}u_j^2>0\quad(u\ne0)'),
      Line(NPC, 99, 99, r'Thus $U_z$ is nondegenerate')],
     'The common point of every node is checked on the exported circuit (rcheck).'),
    # -- Movement.lean: the compact-control address algebra -------------------
    ('Movement', ['bxor', 'four_step', 'four_step_parity'], 'the four-step update toggles the parity by z and restores w',
     [Line(NM, 47, 52, r'v\gets v+2zw,\qquad w\gets w+(v\bmod2),\qquad v\gets v+z(1-2w),\qquad w\gets w-((v\bmod2)\mathbin\oplus z)'),
      Line(NM, 53, 55, r'The final values are $v+z(1-2a)$ and the original $w$')], ''),
    ('Movement', ['later_source'], 'two passes with parities u mod 2 and (u+x) mod 2 toggle by x',
     [Line(NM, 72, 78, r'the two control parities differ by exactly $x_{j_i}$')], ''),
    ('Movement', ['guard_no_carry'], 'the guard interval keeps a displaced segment in [0, 2^K)',
     [Line(NM, 86, 89, r'2B\le g_i<2^{K-1}-2B'),
      Line(NM, 91, 94, r'The conservative guard interval therefore prevents every carry or borrow')], ''),
    ('Movement', ['digits_lt', 'digit_extract', 'packed_rotation'],
     'under the guard, one packed rotation updates each segment independently',
     [Line(NM, 57, 63, r'A target-slot update is one modular rotation of $y$'),
      Line(NM, 91, 94, r'prevents every carry or borrow between the wide segments')],
     'Digit-level arithmetic only; the streaming rotation itself is not modelled.'),
    ('Movement', ['repair_permutation'], 'S = T off a T-invariant bad set ⇒ TS⁻¹ fixes good addresses and permutes the bad set',
     [Line(NM, 104, 108, r'Since $S=T$ off the bad set, $S$ preserves that set too'),
      Line(NM, 118, 119, r'because $TS^{-1}$ permutes the bad set')], ''),
    # -- Layout.lean: row arithmetic -------------------------------------------
    ('Layout', ['row_range'], 'R_row = 2^(q₀K) ≥ W^k₀',
     [Line(NL, 10, 11, r'q_0=\lceil\log_2W\rceil\lceil\log_m(2d)\rceil, \quad k_0=\lceil\log_m d\rceil'),
      Line(NL, 30, 30, r'$R_{\rm row}=2^{q_0K}\ge W^{k_0}$')],
     'Hypotheses W ≤ 2^⌈log₂W⌉ and ⌈log_m d⌉ ≤ ⌈log_m 2d⌉ are left to the caller.'),
    ('Layout', ['pad'], 'padding to a multiple of W^k₀ at most doubles the rows',
     [Line(NL, 31, 35, r'increases total volume by at most two')], ''),
    ('Layout', ['role_rows', 'split_invariant'], 'u = Wg + w gives each role 1/W of the rows; divisibility survives',
     [Line(NL, 37, 37, r'write the row index as $u=Wg+w$, $0\le w<W$'),
      Line(NL, 40, 41, r'exactly $1/W$ of the parent volume'),
      Line(NL, 41, 41, r'At depth $j$ the remaining row count is divisible by $W^{k_0-j}$')], ''),
    ('Layout', ['reserved_axes'], 'q_F + q_B ≤ 3dG/K + 2 ≤ 6d^(1−c)G + 2',
     [Line(NL, 5, 7, r'H=dG'), Line(NL, 65, 67, r'q_F+q_B\le\frac{3dG}{K}+2\le6d^{1-c}G+2')], ''),
    # -- D: parameters, slacks, margins ------------------------------------
    ('CrocSwap', ['τ', 'σ', 'ε', 'c', 'lam', 'lamp', 'κ', 'β', 'δ', 'C1'], 'the chosen parameters',
     [Line(NC, 68, 68, r'\epsilon=\frac{1999}{10000},\quad c=\frac15'),
      Line(NC, 69, 69, r'\delta=\frac1{10^6}'), Line(NC, 70, 70, r'C_1=\frac{49961}{10000}'),
      Line(NC, 71, 71, r'\lambda=1-\frac{1671}{4\cdot10^{12}}'),
      Line(NC, 72, 72, r"\lambda'=1-\frac{167}{4\cdot10^{11}}"),
      Line(NC, 73, 73, r'\kappa=\frac{83}{10^{12}}'),
      Key(CJ, main_('parameters', 'tau'), '12499999963 / 12500000000'),
      Key(CJ, main_('parameters', 'sigma'), '499999999791 / 500000000000'),
      Key(CJ, main_('parameters', 'epsilon'), '1999 / 10000'),
      Key(CJ, main_('parameters', 'c'), '1 / 5'),
      Key(CJ, main_('parameters', 'lam'), '3999999998329 / 4000000000000'),
      Key(CJ, main_('parameters', 'lamp'), '399999999833 / 400000000000'),
      Key(CJ, main_('parameters', 'kappa'), '83 / 1000000000000'),
      Key(CJ, main_('parameters', 'beta'), '1 / 1000'),
      Key(CJ, main_('parameters', 'delta'), '1 / 1000000'),
      Key(CJ, main_('parameters', 'C1'), '49961 / 10000')], ''),
    ('CrocSwap', ['parameter_origin'], 'τ = 1 − a, σ = 1 − a_c, C₁ from the guard',
     [Line(NC, 65, 65, r'Put $a=296/10^{11}$ and $a_{\rm c}=418/10^{12}$'),
      Line(NC, 67, 67, r'\tau=1-a,\quad\sigma=1-a_{\rm c}')], ''),
    ('CrocSwap', ['internal', 'leaf', 'prep', 'layer'], 'the layer exponents χ, χ_leaf, χ_reserve',
     [Line(NC, 77, 79, r'\chi=\tau+(1-\beta)(\sigma-\tau)'),
      Line(NC, 78, 78, r'\chi_{\rm leaf}=\sigma+\beta(1-\sigma)'),
      Line(NC, 79, 79, r'\chi_{\rm reserve}=1-c=\frac45'),
      Line(NL, 94, 94, r'\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}'),
      Line(NL, 71, 71, r'd^{\max\{1-c,0\}}')],
     'Lean keeps the layout note\'s max; the main note drops it because σ > τ (`exponents_below_layer`).'),
    ('CrocSwap', ['recurrence_values'], 'exact recurrence exponents',
     [Key(CJ, main_('recurrence', 'internal'), '499999999789729 / 500000000000000'),
      Key(CJ, main_('recurrence', 'leaf'), '499999999791209 / 500000000000000'),
      Key(CJ, main_('recurrence', 'preprocessing'), '4 / 5'),
      Key(CJ, main_('recurrence', 'layer'), '499999999791209 / 500000000000000')], ''),
    ('CrocSwap', ['constraint_slacks'], 'all 31 constraint slacks are positive',
     [Line(NC, 81, 84, r'$\max\{\tau,\sigma,\chi\}<\lambda<\lambda\'<1$'.replace("\\'", "'")),
      Line('scripts/certify.py', 94, 94, 'def constraints('),
      Line('scripts/compact_control_layer.py', 86, 87, "slacks['reserved_axes']=p.lamp-e['preprocessing']")],
     'The 31-entry list is the script\'s `constraints(...)`, not a note display.'),
    ('CrocSwap', ['slack_values'], 'the certificate\'s slack values are exact',
     [Key(CJ, main_('constraint_slacks', 'packed_overhead'), '349 / 125000000000000'),
      Key(CJ, main_('constraint_slacks', 'reserved_axes'), '79999999833 / 400000000000'),
      Key(CJ, main_('constraint_slacks', 'guard_width'), '127961 / 100000000'),
      Key(CJ, main_('constraint_slacks', 'leaf_cost'), '41 / 500000000000000'),
      Key(CJ, main_('constraint_slacks', 'lambda_prime_above_lambda'), '1 / 4000000000000'),
      Key(CJ, main_('constraint_slacks', 'lambda_above_sigma'), '1 / 4000000000000'),
      Key(CJ, main_('constraint_slacks', 'lambda_above_tau'), '10169 / 4000000000000'),
      Key(CJ, main_('constraint_slacks', 'gaussian_cost'), '31 / 250000'),
      Key(CJ, main_('constraint_slacks', 'lambda_below_one'), '1671 / 4000000000000'),
      Key(CJ, main_('constraint_slacks', 'lambda_prime_below_one'), '167 / 400000000000'),
      Key(CJ, main_('constraint_slacks', 'dimension_upper_bound'), '4003 / 30000'),
      Key(CJ, main_('constraint_slacks', 'crt_layout'), '296037 / 125000000000000'),
      Key(CJ, main_('constraint_slacks', 'prefix_cost'), '19003 / 25000'),
      Key(CJ, main_('constraint_slacks', 'scalar_cost'), '800099 / 1000000'),
      Key(CJ, main_('constraint_slacks', 'delta_below_one_eighth'), '124999 / 1000000'),
      Key(CJ, main_('constraint_slacks', 'prime_interval_growth'), '3001 / 5000'),
      Key(CJ, main_('constraint_slacks', 'alpha_below_sqrt_p'), '8001 / 40000'),
      Key(CJ, main_('constraint_slacks', 'gamma_sublinear'), '4003 / 20000'),
      Key(CJ, main_('constraint_slacks', 'K_smaller_than_ell'), '19003 / 25000'),
      Key(CJ, main_('constraint_slacks', 'K_dominates_log_p'), '1999 / 50000'),
      Key(CJ, main_('constraint_slacks', 'r_superpolynomial'), '8001 / 10000'),
      Key(CJ, main_('constraint_slacks', 'tau_below_one'), '37 / 12500000000'),
      Key(CJ, main_('constraint_slacks', 'sigma_below_one'), '209 / 500000000000'),
      Key(CJ, main_('constraint_slacks', 'beta_below_one'), '999 / 1000')], ''),
    ('CrocSwap', ['g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7'], 'the seven margins',
     [Line(NC, 104, 104, r'g_1&=1-\epsilon(1+c),&g_2&=\epsilon c(1-\tau)'),
      Line(NC, 105, 105, r"g_3&=\epsilon(1-\lambda'),&g_4&=(1-\tau)(1-\epsilon)"),
      Line(NC, 106, 106, r'g_5&=1/4-\delta-5\epsilon/4,&g_6&=1-\delta-\epsilon,\qquad g_7=\epsilon'),
      Line(P8, 856, 857, r'g_4&=1-\tau-\epsilon(2-\tau)'),
      Line(P8, 856, 857, r'g_5=1/4-\delta-3\epsilon/2'),
      Line(NNA, 124, 124, r'g_4=(1-\tau)(1-\epsilon)'),
      Line(NPN, 55, 56, r'normalized exponent $3/4+\delta+5\epsilon/4$')],
     'g₄ and g₅ differ from the paper on purpose: nonadjacent routing (g₄) and the smaller Gaussian width (g₅).'),
    ('CrocSwap', ['margin_values'], 'exact margin values',
     [Key(CJ, main_('margins', 'g1'), '19003 / 25000'),
      Key(CJ, main_('margins', 'g2'), '73963 / 625000000000000'),
      Key(CJ, main_('margins', 'g3'), '333833 / 4000000000000000'),
      Key(CJ, main_('margins', 'g4'), '296037 / 125000000000000'),
      Key(CJ, main_('margins', 'g5'), '31 / 250000'),
      Key(CJ, main_('margins', 'g6'), '800099 / 1000000'),
      Key(CJ, main_('margins', 'g7'), '1999 / 10000')], ''),
    ('CrocSwap', ['kappa_witness'], 'min g = g₃ > κ, gap 1833/(4·10¹⁵), 2⁻³⁴ < κ < 2⁻³³',
     [Line(NC, 111, 111, r'G_*:=\min_i g_i=g_3=\frac{333833}{4\cdot10^{15}}'),
      Line(NC, 112, 112, r'G_*-\kappa=\frac{1833}{4\cdot10^{15}}>0'),
      Line(NC, 118, 118, r'2^{-34}<\frac{83}{10^{12}}<2^{-33}'),
      Key(CJ, main_('absorption_gap'), '1833 / 4000000000000000')], ''),
    # -- E: repair ----------------------------------------------------------
    ('CrocSwap', ['repair_bound'], 'n(2·2⁻ᴳ + 8·2ᴳ⁻ᴷ) ≤ 5/(128p³) for every p ≥ 2',
     [Line(NM, 101, 101, r'\delta=\min\{1,n(2\cdot2^{-G}+8\cdot2^{G-K})\}'),
      Line(NM, 149, 150, r'$K\ge G+4\ell_p+10$'),
      Line(NM, 152, 152, r'\delta\le \frac{5}{128p^3}'),
      Line(NL, 5, 5, r'G=4\lceil\log_2p\rceil+6'),
      Line(NL, 24, 24, r'nG=(f-1)G\le H')],
     'ℓ_p = Nat.size(p − 1) = ⌈log₂p⌉ for p ≥ 2. Bounds the second argument of the min. '
     'n ≤ p follows from n ≤ d (layout line 24, H = dG).'),
    # -- F: recurrence levels -------------------------------------------------
    ('CrocSwap', ['internal_level'], 'level i costs at most d^χ',
     [Line(NL, 90, 91, r'O(G^\tau e^\tau(b/m^\tau)^j)'),
      Line(NL, 93, 98, r'otherwise the'),
      Line(P5, 654, 657, r'Since \(a\le m^\sigma<m^\lambda\)')], ''),
    ('CrocSwap', ['leaf_level'], 'leaves cost at most d^(σ + β(1−σ))',
     [Line(NL, 99, 100, r'$O(d^{\sigma+\beta(1-\sigma)})$'),
      Line(P5, 663, 667, r'\(a^j\le m^{j\sigma}=(e/u)^\sigma\)')], ''),
    ('CrocSwap', ['exponents_below_layer'], 'τ < σ, χ < λ, χ_leaf < λ′, λ < λ′',
     [Line(NC, 82, 83, r"$\max\{\chi_{\rm leaf},\chi_{\rm reserve}\}<\lambda'$"),
      Line(NL, 112, 113, r"\max\{\sigma+\beta(1-\sigma),1-c,0\}<\lambda'")], ''),
    ('CrocSwap', ['note_parameter_lines'], 'the note\'s displayed parameter comparisons',
     [Line(NC, 79, 79, r'\chi_{\rm reserve}=1-c=\frac45'),
      Line(NC, 82, 82, r"$\max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1$"),
      Line(NC, 84, 84, r'$\epsilon C_1=99872039/10^8<1$'),
      Line(NC, 91, 92, r'\alpha=\Theta(p^{11999/40000})'),
      Line(NC, 91, 92, r'\gamma=O(p^{15997/20000})'),
      Line(NC, 95, 95, r'indeed $184<2^8$'),
      Line(NC, 96, 96, r'$1-2\epsilon=3001/5000>0$'),
      Line(NC, 98, 98, r'$\epsilon(1+c)<1$')], ''),
    ('CrocSwap', ['gaussian_cutoff'], 'b ≥ 2⁴⁰ ⇒ 46 b^((1+3ε)/2) ≤ b/4',
     [Line(NC, 94, 95, r'Since $\epsilon<1/5$, $b\ge2^{40}$ implies $46b^{(1+3\epsilon)/2}\le b/4$')], ''),
    # -- G, H: the scoped ceiling ----------------------------------------------
    ('CrocSwap', ['kappa_lt_fifth'], 'Gaussian and leaf margins force κ < (1 − σ)/5',
     [Line(NC, 140, 142, r'Gaussian margin forces $\epsilon<1/5$'),
      Line(NC, 142, 142, r"$1-\lambda'<(1-\beta)(1-\sigma)<1-\sigma$"),
      Line(NC, 145, 145, r'\kappa<\frac{a_{\rm c}^{\rm actual}}5')], ''),
    ('CrocSwap', ['certified_saving_le', 'log_15625_gt', 'scoped_ceiling'],
     'coarse form: κ < 2⁻³³ for every admissible choice',
     [Line(NC, 143, 146, r'<8.369598075\cdot10^{-11}<2^{-33}')],
     'Superseded by `scoped_ceiling_exact`; kept as an independent coarse check.'),
    ('CrocSwap', ['ps', 'neglog_bounds', 'log5_identity', 'Llo', 'log_15625_ge', 'Nhi',
                  'neglog_eta_le', 'enclosure_le_U', 'certified_saving_log'],
     'helpers: 26-digit enclosures of log 15625 and −log(1 − η_c)',
     [Line(NC, 139, 140, r'approximately $4.1847990372\cdot10^{-10}$')],
     'Helpers; Nhi/Llo is the note\'s saving enclosure.'),
    ('CrocSwap', ['enclosure_gt_U_shrunk'], 'negative control: the enclosure exceeds U·(1 − 10⁻²⁴)',
     [], 'Shows the check against U is tight; no source line.'),
    ('CrocSwap', ['ηc'], 'η_c as a real', [Line(NI, 44, 44, r'=\frac{14}{3464399375}>0')], ''),
    ('CrocSwap', ['Uceil'], 'the certificate\'s exact ceiling U',
     [Key(CJ, ('scoped_ceiling', 'upper'), '__UCEIL__')], ''),
    ('CrocSwap', ['scoped_ceiling_exact'], 'κ < U for every admissible choice with this motif',
     [Line(NC, 143, 146, r'\kappa<\frac{a_{\rm c}^{\rm actual}}5'),
      Line(NC, 146, 146, r'<8.369598075\cdot10^{-11}')], ''),
    ('CrocSwap', ['ceiling_facts'], 'U < 8.369598075·10⁻¹¹ < 2⁻³³; κ > 0.99 U',
     [Line(NC, 146, 146, r'<8.369598075\cdot10^{-11}<2^{-33}'),
      Line(NC, 148, 148, r'The displayed witness exceeds 99\% of this upper enclosure')], ''),
    ('CrocSwap', ['witness_meets_ceiling'], 'their witness satisfies every hypothesis',
     [], 'Non-vacuity check for `scoped_ceiling_exact`; no source line.'),
]

DECL = re.compile(r'^(?:noncomputable )?(?:theorem|def) (\S+)', re.M)
STOP = re.compile(r'^(?:theorem|def|noncomputable|/-|end |namespace|section)', re.M)


# Scoped rational arithmetic for the selected portable composition.
ROWS.append(('ShrunkBirthTerminal', ['h', 'm', 'v', 'n', 'virtualRoles', 'births', 'terminals', 'roles', 'width', 'forwardHistogram', 'initialDimensionHistogram', 'counts', 'count', 'mass', 'network_counts', 'initial_dimension_count', 'rank_mass', 'count_1', 'count_2', 'count_3', 'count_4', 'count_5', 'count_6', 'count_7', 'count_8', 'count_9', 'count_10', 'count_11', 'count_12', 'count_13', 'count_14', 'count_15', 'count_16', 'count_17', 'count_18', 'count_19', 'count_20', 'count_21', 'count_22', 'count_23', 'count_529', 'count_552', 'count_554', 'count_556', 'count_558', 'count_560', 'count_562', 'count_571', 'count_572', 'count_573', 'count_574', 'childSizes', 'complete_child_support', 'strict_child_contraction'], 'Complete physical-count arrays and paid histogram', [Line('research/shrunk-birth-terminal/lean/generate.py', 34, 56, 'complete_child_support')], 'Exact input derivation and full generated-byte linkage are checked by research/shrunk-birth-terminal/audit_lean.py; general analytic and physical interfaces remain external.'))
ROWS.append(('ShrunkBirthTerminal', ['a', 'b', 'kappa', 'eta', 'beta', 'backoff', 'actualBitSaving', 'tau', 'sigma', 'qParam', 'lp', 'c', 'epsilon', 'lam', 'g', 'r', 'delta', 'internal', 'leaf', 'scalar', 'guardE', 'guardB', 'literal', 'guardC', 'literalGap', 'rowCoefficient', 'rowGap', 'margins', 'slack_a_positive', 'slack_a_below_b', 'slack_b_below_one_over32', 'slack_beta_positive', 'slack_beta_below_one', 'slack_phase_leaf_above_bit', 'slack_q_positive', 'slack_q_below_internal', 'slack_q_below_leaf', 'slack_c_positive', 'slack_c_below_one', 'slack_q_below_reservations', 'slack_lambda_above_tau', 'slack_lambda_above_sigma', 'slack_lambda_above_internal', 'slack_lambda_prime_above_lambda', 'slack_compact_leaf', 'slack_compact_reservations', 'slack_lambda_prime_below_one', 'slack_epsilon_positive', 'slack_epsilon_below_one', 'slack_guard_width', 'slack_K_geometry', 'slack_K_dominates_log', 'slack_record_suffix', 'slack_phase_local', 'slack_phase_boundary', 'slack_gamma_sublinear', 'slack_cell_above_band', 'slack_prime_interval_packing', 'slack_alpha_positive', 'slack_alpha_below_one', 'slack_alpha_below_one_fourth', 'slack_delta_positive', 'slack_delta_below_one_eighth', 'slack_short_record_fallback', 'slack_small_field_exposure', 'slack_artificial_boundary', 'slack_literal_scalar_guard', 'slack_row_product_gap', 'slack_g1_above_kappa', 'slack_g2_above_kappa', 'slack_g3_above_kappa', 'slack_g4_above_kappa', 'slack_g5_above_kappa', 'slack_g6_above_kappa', 'slack_g7_above_kappa', 'margins_strict', 'balanced_identities', 'stopped_parameter_choice', 'controlling_margin', 'fixed_profile_grid_exclusion', 'gain_over_pinned_bounds', 'stock_bit_coarse', 'stock_complex', 'stock_ordinary_leaf', 'row_stock', 'semantic_constants', 'finite_bridge'], 'Exact transfer parameters, all 47 inequalities, seven margins and three row stocks', [Line('research/shrunk-birth-terminal/lean/generate.py', 57, 101, 'slacks')], 'Exact input derivation and full generated-byte linkage are checked by research/shrunk-birth-terminal/audit_lean.py; general analytic and physical interfaces remain external.'))
ROWS.append(('ShrunkBirthTerminal', ['taylor8', 'expUpper', 'accepted_1', 'accepted_interval_1', 'accepted_taylor_1', 'accepted_2', 'accepted_interval_2', 'accepted_taylor_2', 'accepted_3', 'accepted_interval_3', 'accepted_taylor_3', 'accepted_4', 'accepted_interval_4', 'accepted_taylor_4', 'accepted_5', 'accepted_interval_5', 'accepted_taylor_5', 'accepted_6', 'accepted_interval_6', 'accepted_taylor_6', 'accepted_7', 'accepted_interval_7', 'accepted_taylor_7', 'accepted_8', 'accepted_interval_8', 'accepted_taylor_8', 'accepted_9', 'accepted_interval_9', 'accepted_taylor_9', 'accepted_10', 'accepted_interval_10', 'accepted_taylor_10', 'accepted_11', 'accepted_interval_11', 'accepted_taylor_11', 'accepted_12', 'accepted_interval_12', 'accepted_taylor_12', 'accepted_13', 'accepted_interval_13', 'accepted_taylor_13', 'accepted_14', 'accepted_interval_14', 'accepted_taylor_14', 'accepted_15', 'accepted_interval_15', 'accepted_taylor_15', 'accepted_16', 'accepted_interval_16', 'accepted_taylor_16', 'accepted_17', 'accepted_interval_17', 'accepted_taylor_17', 'accepted_18', 'accepted_interval_18', 'accepted_taylor_18', 'accepted_19', 'accepted_interval_19', 'accepted_taylor_19', 'accepted_20', 'accepted_interval_20', 'accepted_taylor_20', 'accepted_21', 'accepted_interval_21', 'accepted_taylor_21', 'accepted_22', 'accepted_interval_22', 'accepted_taylor_22', 'accepted_23', 'accepted_interval_23', 'accepted_taylor_23', 'accepted_529', 'accepted_interval_529', 'accepted_taylor_529', 'accepted_552', 'accepted_interval_552', 'accepted_taylor_552', 'accepted_554', 'accepted_interval_554', 'accepted_taylor_554', 'accepted_556', 'accepted_interval_556', 'accepted_taylor_556', 'accepted_558', 'accepted_interval_558', 'accepted_taylor_558', 'accepted_560', 'accepted_interval_560', 'accepted_taylor_560', 'accepted_562', 'accepted_interval_562', 'accepted_taylor_562', 'accepted_571', 'accepted_interval_571', 'accepted_taylor_571', 'accepted_572', 'accepted_interval_572', 'accepted_taylor_572', 'accepted_573', 'accepted_interval_573', 'accepted_taylor_573', 'accepted_574', 'accepted_interval_574', 'accepted_taylor_574', 'acceptedMoment', 'acceptedFromCounts', 'accepted_profile_link', 'accepted_moment', 'accepted_paid_moment', 'rejected_1', 'rejected_interval_1', 'rejected_taylor_1', 'rejected_2', 'rejected_interval_2', 'rejected_taylor_2', 'rejected_3', 'rejected_interval_3', 'rejected_taylor_3', 'rejected_4', 'rejected_interval_4', 'rejected_taylor_4', 'rejected_5', 'rejected_interval_5', 'rejected_taylor_5', 'rejected_6', 'rejected_interval_6', 'rejected_taylor_6', 'rejected_7', 'rejected_interval_7', 'rejected_taylor_7', 'rejected_8', 'rejected_interval_8', 'rejected_taylor_8', 'rejected_9', 'rejected_interval_9', 'rejected_taylor_9', 'rejected_10', 'rejected_interval_10', 'rejected_taylor_10', 'rejected_11', 'rejected_interval_11', 'rejected_taylor_11', 'rejected_12', 'rejected_interval_12', 'rejected_taylor_12', 'rejected_13', 'rejected_interval_13', 'rejected_taylor_13', 'rejected_14', 'rejected_interval_14', 'rejected_taylor_14', 'rejected_15', 'rejected_interval_15', 'rejected_taylor_15', 'rejected_16', 'rejected_interval_16', 'rejected_taylor_16', 'rejected_17', 'rejected_interval_17', 'rejected_taylor_17', 'rejected_18', 'rejected_interval_18', 'rejected_taylor_18', 'rejected_19', 'rejected_interval_19', 'rejected_taylor_19', 'rejected_20', 'rejected_interval_20', 'rejected_taylor_20', 'rejected_21', 'rejected_interval_21', 'rejected_taylor_21', 'rejected_22', 'rejected_interval_22', 'rejected_taylor_22', 'rejected_23', 'rejected_interval_23', 'rejected_taylor_23', 'rejected_529', 'rejected_interval_529', 'rejected_taylor_529', 'rejected_552', 'rejected_interval_552', 'rejected_taylor_552', 'rejected_554', 'rejected_interval_554', 'rejected_taylor_554', 'rejected_556', 'rejected_interval_556', 'rejected_taylor_556', 'rejected_558', 'rejected_interval_558', 'rejected_taylor_558', 'rejected_560', 'rejected_interval_560', 'rejected_taylor_560', 'rejected_562', 'rejected_interval_562', 'rejected_taylor_562', 'rejected_571', 'rejected_interval_571', 'rejected_taylor_571', 'rejected_572', 'rejected_interval_572', 'rejected_taylor_572', 'rejected_573', 'rejected_interval_573', 'rejected_taylor_573', 'rejected_574', 'rejected_interval_574', 'rejected_taylor_574', 'rejectedMoment', 'rejectedFromCounts', 'rejected_profile_link', 'rejected_moment', 'rejected_paid_moment'], 'Independent rational Taylor enclosure arithmetic', [Line('research/shrunk-birth-terminal/lean/generate.py', 102, 125, 'taylor8')], 'Exact input derivation and full generated-byte linkage are checked by research/shrunk-birth-terminal/audit_lean.py; general analytic and physical interfaces remain external.'))


def lean_decls():
    out = {}
    for f in sorted((LEAN/'KappaCheck').glob('*.lean')):
        text = f.read_text()
        for match in DECL.finditer(text):
            rest = text[match.end():]
            stop = STOP.search(rest)
            out[(f.stem, match.group(1))] = (f, text.count('\n', 0, match.start())+1,
                                             match.group(0)+(rest[:stop.start()] if stop else rest))
    return out


def norm(s):
    return ' '.join(s.split())


def lean_value(literal):
    if not re.fullmatch(r'[0-9 /^]+', literal):
        raise ValueError(literal)
    a, _, b = literal.partition('/')
    ev = lambda t: eval(t.replace('^', '**')) if t.strip() else 1
    return Fraction(ev(a))/Fraction(ev(b))


def json_at(path, keys):
    x = json.loads((ROOT/path).read_text())
    for k in keys:
        x = x[k]
    return x


def check():
    errors = []
    decls = lean_decls()
    named = set()
    for module, names, _, refs, _ in ROWS:
        for name in names:
            key = (module, name)
            named.add(key)
            if key not in decls:
                errors.append(f'{module}.{name}: not found in Lean sources')
        for ref in refs:
            if isinstance(ref, Line):
                lines = (ROOT/ref.path).read_text().split('\n')
                if not 1 <= ref.first <= ref.last <= len(lines):
                    errors.append(f'{ref.path}:{ref.first}-{ref.last}: out of range')
                elif norm(ref.anchor) not in norm(' '.join(lines[ref.first-1:ref.last])):
                    errors.append(f'{ref.path}:{ref.first}-{ref.last}: anchor {ref.anchor!r} missing')
            else:
                value = Fraction(str(json_at(ref.path, ref.keys)))
                body = ' '.join(decls[(module, n)][2] for n in names if (module, n) in decls)
                literal = ref.lean
                if literal == '__UCEIL__':
                    literal = re.search(r':= ([0-9]+ / [0-9]+)', body).group(1)
                if lean_value(literal) != value:
                    errors.append(f'{ref.path} {".".join(ref.keys)}: {value} != Lean {literal}')
                elif norm(literal) not in norm(body):
                    errors.append(f'{module}.{"/".join(names)}: literal {literal} not in declaration')
    for key in sorted(set(decls)-named):
        errors.append(f'{key[0]}.{key[1]}: declaration missing from the table')
    return errors


def link(ref):
    if isinstance(ref, Key):
        return f'`{Path(ref.path).name}` `{".".join(ref.keys)}`'
    span = f'L{ref.first}' if ref.first == ref.last else f'L{ref.first}-L{ref.last}'
    label = f'{Path(ref.path).name}:{ref.first}' + ('' if ref.first == ref.last else f'–{ref.last}')
    return f'[{label}](../../{ref.path}#{span})'


def render():
    decls = lean_decls()
    out = ['# Lean declarations and the lines they formalize', '',
           'Generated by `sources.py` from its `ROWS` table; do not edit by hand.',
           '`python3 formal/lean/sources.py` (also run by `tests/test_lean_sources.py`) checks that',
           'every declaration is listed, every cited line still contains its quoted text, and every',
           'cited certificate value equals the literal in the Lean declaration.',
           f'Line numbers refer to this branch, based on `{COMMIT[:7]}`.', '',
           '| Lean | Claim | Doug\'s notes | Paper (pinned upstream) | Certificate / script | Remark |',
           '|---|---|---|---|---|---|']
    for module, names, claim, refs, remark in ROWS:
        lean = ', '.join(f'[`{n}`](KappaCheck/{module}.lean#L{decls[(module, n)][1]})'
                         for n in names)
        cols = {'notes': [], 'upstream': [], 'other': []}
        for ref in refs:
            top = ref.path.split('/')[0]
            cols[top if top in cols else 'other'].append(link(ref))
        cell = lambda xs: '<br>'.join(dict.fromkeys(xs)) or '—'
        out.append(f'| {lean} | {claim} | {cell(cols["notes"])} | {cell(cols["upstream"])} '
                   f'| {cell(cols["other"])} | {remark} |')
    return '\n'.join(out)+'\n'


if __name__ == '__main__':
    errs = check()
    target = LEAN/'SOURCES.md'
    if '--write' in sys.argv and not errs:
        target.write_text(render())
    elif not errs and target.read_text() != render():
        errs.append('SOURCES.md is stale: run sources.py --write')
    print('\n'.join(errs) or f'OK: {sum(len(r[1]) for r in ROWS)} declarations, '
          f'{sum(len(r[3]) for r in ROWS)} source references')
    sys.exit(1 if errs else 0)
