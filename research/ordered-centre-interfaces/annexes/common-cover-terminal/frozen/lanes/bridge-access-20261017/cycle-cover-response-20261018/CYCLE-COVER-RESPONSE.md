# One cover response at all nine pure-line cuts

This packet gives one unitary response E on the actual 73-axis cover.
The same E has a physical monomial transfer at all nine cuts of the
fresh three-child template. The transfer needs no native child and no
temporary array. It applies to arbitrary cover contents. It does not
assume that different cover classes contain the same data.

The result removes a stage-transport obstacle for a changed local
template. It does not improve the complete supplier exponent by itself.
The direct terminal decoder has rank mass 896 per four-pair replica.
Together with the productive advances, that decoder exhausts the rank
budget. A cheaper decoder or a fusion with productive advances is still
needed for a supplier gain.

## Sources and conventions

The source archive is
`worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz`,
SHA-256 `f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
The checker reads its member
`candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json`,
SHA-256 `c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa`.
The imported phase and route code is `../check_bridge_access.py`,
SHA-256 `9510c5624dfb51d98767728084851e4ee75a135e6d7b546569a47fe458485111`.

Use the full cover G=O(73,2). This is the selected cover; no larger cover
is used. Its elements act on column vectors on the left. A cover label
h is independent of a payload address. The route rho_(s,p) exchanges
the eight root complement axes with the eight axes of stage s. It is
the identity at stage zero. All these routes are orthogonal
involutions.

C_w is the pure directional complex transform. On a Fourier character
chi it has eigenvalue i raised to the bit w.chi. For an ordered list A,
write C_A for the product of its C_w factors. T_d is the payload
translation by d. Its Fourier eigenvalue is (-1) raised to d.chi.
All these transforms commute. The statements hold on every coordinate
copy. For width f, apply each translation on all f copies.

The fresh local word is in
`../../history-encoding/independent-skeleton-20261018/fresh-three-child/`.
Its exact transfer frames are C_q and C_v. They are not the compiler's
`canonical_frame([q])` and `canonical_frame([v])`. The native child
recipes are a separate dependency. This packet proves their global
transfer-slot condition, including the exterior frames.

## The common response

Fix a port p. Let q be its actual odd port vector, and let v_0 be the
first complement vector in its actual orthogonal chart. For 1<=s<=8,
let v_s be the first coordinate axis of the stage-s block. The ten
vectors

    q, v_0, v_1, ..., v_8

are orthonormal. Define L_p to cycle these vectors in the displayed
order and fix their orthogonal complement. Then L_p is orthogonal,
has order ten, and has inverse L_p^T. Its literal 73 columns and inverse
columns are in `CYCLE-COVER-PROGRAMS.json` for every port.

Define E on the complete cover family by

    (E f)_p(h) = f_p(h L_p).
    (E^-1 f)_p(h) = f_p(h L_p^-1).

E acts only on the cover label. It does not change a payload address.
It is a permutation and therefore a unitary map. It is independent of
the stage. No commutation with the intrinsic Q operator is assumed.

In the forward direction, source class h sends its content to target
class h L_p^-1. Both classes are in the original cover. This orientation
fixes the order of every route and phase below.

## Exact physical transfer at every cut

At stage zero, the source and target cut frames in owner coordinates
are C_q and C_v0. At stage s>0, define A_s as the ordered coordinate
axes of the first 9+8(s-1) coordinates. The two frames are

    source: C_A_s,
    target: C_A_s C_q^-1 C_v_s.

Write U_s and V_s for these two frame products. The target is at
h L_p^-1 when the source is at h. The required physical block is

    V_(s,h L_p^-1) U_(s,h)^-1.

The cycle maps the source polar subspace onto the target polar
subspace. More is needed for the pure-C phases. Let phi_A(chi) be the
sum modulo four of the bits w.chi for the factors C_w in A, with the
stated signs. The checker expands this as a full quadratic polynomial
over binary coordinates, with coefficients modulo four. For every
port and stage it proves

    phi_V_s(L_p chi) - phi_U_s(chi) = 2 delta_(p,s).chi.

Equivalently, it substitutes L_p^-1 into the target factor vectors.
Thus the complete physical block is exactly

    T_(h delta_(p,s)).                              (1)

There is no missing constant phase: all frame products have value one
on the zero character. The checker proves (1) by coefficient equality,
not by a finite sample of characters. Omitting delta fails in 896 of
the 1,008 cut cases. At stage zero the phase correction is zero.

One forward transfer can therefore use the following exact word:

1. Use the cover map h -> h L_p^-1 and the translation in (1) as a
   temporary view of X.
2. Add that X view into Y with coefficient one.
3. Restore the original X view.

The source is unchanged. The target content becomes y+E x in its
correct frame. In the reverse word, use the inverse matching and
translation, subtract Y from X, and restore the Y view. Since E is
unitary, this is the required reciprocal response E^-1. The result is
an operator identity on both arbitrary banks; no zero-input premise
is used.

## Literal body routes and whole-cover sweeps

For source owner h, the current source invocation body is

    d_x = h rho_(s,p).

For its matching target owner h L_p^-1, the target body is

    d_y = h L_p^-1 rho_(s,p)
        = d_x rho_(s,p) L_p^-1 rho_(s,p).           (2)

The payload stores the literal columns of (2). The checker verifies
both the body equation and its inverse. In general d_x and d_y are
different. A same-body transfer is not used.

The old DATA entry translations are also retained. The checker proves
that the actual entry view converts U_s to the common exterior times
C_q, and converts V_s to the same exterior times C_v0. It uses the
literal DATA entry_X and entry_Y values and verifies that they agree.
The owner-coordinate transfer (1) must be composed with these entry
views. Undoing an entry view, applying (1), and restoring the view is
one valid finite monomial implementation. Adjacent maps can instead
be composed. This is scalar and address work, not a free omitted cost.

The three-child word must run in three complete cover sweeps. First,
prepare all target C_v0 lines. Second, run all matched transfers (2).
Third, run all productive completions. This order is legal for the
following reasons. Each child is an operation on one productive data
field and returns its own recursive workspace. Each transfer has one
unchanged source and one target. The matching in (2) is a bijection,
so each target is written once for this port. Different ports use
different fields. No private or helper value has to survive between
two bodies. Consequently the order within each sweep is arbitrary,
and the sweep boundary creates no additional storage obligation.

This argument supplies a rescheduling of the helper-free word. It
does not authorize such a rescheduling for an old word with live
private or helper state across its body boundaries.

## Native profile and FULL code

The fresh native children on each port are

    C_v0,                         rank 1;
    F_9 C_q^-1,                   rank 8;
    F_9 C_q^-1 C_v0^-1,            rank 7.

There are 112 of each. The profile is {1:112,7:112,8:112}, with 336
children and rank mass 1,792. The transfers add 112 unit complex ADDs
and no native child. The separate native emitter gives the exact
monomial side maps and scalar price. Whole-cover routing and its finite
address price must also be included in the complete supplier invoice.

Let F be the full 73-axis pure-C frame. The physical FULL codes
M_E=F E F^-1 and M_Einv=F E^-1 F^-1 are monomial. At output class h,
their literal forms are

    (M_E z)_p(h) = T_(h delta_E,p) z_p(h L_p),
    (M_Einv z)_p(h) = T_(h delta_Einv,p) z_p(h L_p^-1).

The two delta values are stored as `FULL_E_output_translation` and
`FULL_E_inverse_output_translation`. The checker proves both complete
phase equations and both orientation conventions for every port.

The common-response controller algebra is a separate dependency. Its
raw endpoint after the old terminal has code

    diag(Q E Q^-1, E^-1).

The direct correction is Q^-1, M_Einv, Q on the first bank, and M_E
on the second. Since L_p^-1 q=v_8, the two line directions at the first
bank output are h q and h v_8. They are distinct and orthogonal. This
uses two rank-one children per port, or one rank-two child. For four
pairs the rank mass is 896. This proof does not remove either line.

The total productive rank is 64,512 before that correction. The direct
correction brings it to 65,408=896*73. Thus this direct completion has
no positive native-moment margin. A local admission result must not be
reported as a complete exponent improvement.

## Verification and status

Run one process:

    python3 -I -B work/centre-encoding-campaign-20261014/lanes/bridge-access-20261017/cycle-cover-response-20261018/check_cycle_cover.py

Expected output: `PASS_COMMON_CYCLE_COVER_RESPONSE`.
The normal and `-O` runs produced identical program and receipt bytes.
The receipt records 1,008 complete transfer phase checks, 2,016 entry
frame checks, 1,008 body bijections, and 224 FULL code phase checks.
All arithmetic is exact. These checks do not replay the full supplier
or its recursive hosting. Independent review is recorded separately.

This work uses the selected native geometry, the helper-free template
from the history-encoding lane, and the common-response controller
algebra from the encoded-controller lane. OpenAI Codex supplied the
research and verification under the user's direction. No PR, push, or
publication is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
