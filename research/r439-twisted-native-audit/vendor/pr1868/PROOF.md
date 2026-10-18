# Twisted helper contract and single-edge absorption: proofs

This note proves four statements:

1. the scalar twisted-contract lemma;
2. uniqueness of the substitute register set;
3. the single-edge absorption criterion;
4. the chronological per-cut comparison for the two instances.

It also names the inherited physical premise that the instances use for helpers. Item 4 and that
premise are confined to the two fixed words. The scalar lemma does not by itself give a
chronological bridge for an arbitrary word that satisfies the twisted contract. `verify.py` checks
every finite fact used here.

## Notation

A word has `n = 2v + R` registers: sources `x` (v of them), targets `y` (v) and helpers `h` (R).
Write `z = (x, h)`. Here `v = 111`, `R = 439` and `n = 661`. The word runs D, then A, then the
scatter, then B, then C. The scatter is realised literally: COPY one retained helper into a clean
temporary, ADD that temporary into the listed targets, then ERASE it. Each ADD `d ^= s` is an
elementary transvection over F2.

Let M be any F2-module. This includes arbitrary F2-valued streams under pointwise addition. A
finite product of elementary transvections has coefficients in F2 and acts on `M^n` through those
coefficients. Two such programs therefore agree on every M exactly when their coefficient matrices
agree, and the n unit columns over F2 determine a coefficient matrix. "Boundary" below always means
the complete coefficient matrix on all 661 columns. Helper inputs are arbitrary ("dirty"), never
assumed to be zero.

The raw word is `W0' = (A, scatter, B)`, without D and without C. Its block form is described below.
The inherited checker conditions (eumemic's PR555 adaptation, `xcheck_p.py`) are:

- **H1**: no gate anywhere whose destination is a z register reads a target.
- **H3**: A writes only z registers. The scatter reads only retained helpers and writes only targets.
  Each B gate either writes a z register from z registers, or writes a target.
- **H5**: the target-to-target block V of `W0'` is the identity.
- **J**: the raw source response J is the identity. As PR1194 noted, H1–H5 alone do not imply this
  for an arbitrary word, so it is checked separately.

## 1. The twisted contract

The contract keeps H1, H3, H5 and `J = I`, and replaces H2, H4 and the K check by:

- **H2-tw.** Every D gate is at the zero frame. Its operands are distinct targets and helpers only,
  so D is source-free. D contains no COPY, ERASE or climb: targets and helpers enter D at the zero
  frame and stay there. D's complete operator is
  `(x, y, h) -> (x, y + N h, T h)`
  for a binary v-by-R matrix N and an invertible binary R-by-R matrix T. T acts on helpers only.
- **H4-tw.** Every C gate has a z destination, reads only z registers and runs at the full frame.
  All z registers end at the full frame. On z, C satisfies
  `C · U' · (I_x ⊕ T) = I`.
- **K-tw.** `N = K' T`, where K' is the helper block of the raw target response of `W0'`.

**Lemma.** Under H1, H2-tw, H3, H4-tw, H5, `J = I` and K-tw, the complete word maps
`(x, y, h) -> (x, y + x, h)` on every F2-module M. Assume the kept conditions and the structural
clauses of H2-tw (D's operator form) and of H4-tw (C z-only at the full frame). Then the equations
`C U' (I ⊕ T) = I` and `N = K'T` are also necessary for this boundary.

*Proof.* By H1 and H3, no z register is ever written from a target in A or B, and the scatter
writes only targets. By induction over the gates, every z output of `W0'` is a combination of z
inputs. This gives the block form

    z' = U' z,      y' = V y + J x + K' h.

D sends `(x, y, h)` to `(x, y + N h, T h)`. Applying `W0'` to that state gives

    z' = U' (x, T h) = U' (I ⊕ T) z,
    y' = V (y + N h) + J x + K' T h = y + x + (N + K' T) h,

using `V = J = I`. C writes and reads only z registers, so it leaves y unchanged. It sends z' to
`C U' (I ⊕ T) z = z`. The final state is `(x, y + x + (N + K'T) h, h)`, and `N + K'T = 0` by K-tw.
Every coefficient lies in F2, so the identity holds on every M.

For necessity, assume the kept conditions and the boundary `(x, y + x, h)`. On the z unit columns
in F2 the z rows give `C U' (I ⊕ T) = I`, and on the helper unit columns the target rows give
`N + K'T = 0`. ∎

**Strict weakening.** Setting `T = I` turns H2-tw into PR1194's H2-sem condition 3,
`(x, y, h) -> (x, y + N h, h)`. H4-tw becomes `C U' = I`, the `C = U^-1` conclusion that PR1194
draws from the literal-reverse H4. K-tw becomes `N = K`. Every word meeting PR1194's contract
therefore meets the twisted contract with `T = I`. The two instances below meet the twisted contract
with `T ≠ I`. They fail H2-sem because D leaves three helpers unrestored. They also fail `C U' = I`
and the literal H4. The weakening is therefore strict.

**The cleanup is weakened even at `T = I`.** The converse of the containment above fails already
at `T = I`. There, H4-tw is the semantic `C U' = I`, whereas PR1194 keeps the literal-reverse H4.
PR1311's stale-cleanup control (PR1122's word with PR589's C) satisfies every twisted condition
with `T = I` and the dirty boundary, yet the lineage rejects it. Endpoint success alone does not give
a chronological bridge for a non-literal full-frame cleanup.

The instances avoid this: their C is byte-identical to the base word's literal C, and section 4
bridges them cut by cut. Adopting H4-tw as a general interface would need such a bridge for
non-literal cleanups.

## 2. The substitute set is unique

Start the replay from the identity state. The state at a cut is the 661-by-661 matrix whose rows
are the current register values as vectors over the input columns. No temporary is live inside D
or A. Each ADD multiplies this matrix by an elementary transvection. The state is therefore
invertible over F2 at every D/A cut.

For any vector δ there is then exactly one register set S whose current values XOR to δ. Its
indicator is `δ^T` times the inverse state matrix. `verify.py` maintains the inverse column by
column: `d ^= s` maps inverse column s to `col_s + col_d`. It then checks every computed S by
direct summation.

## 3. Single-edge absorption criterion

Let `e` be a trailing D restoration `a ^= b`. Let δ be b's value just before e; on all four lineage
words this is b's own input column. Let g be a later gate writing a, with source set Sg, such that
no gate strictly between e and g reads a. Let S be the unique set with value sum δ at the cut just
before g in the original word W. Suppose a is not in S.

**Criterion.** Delete e and change only g's source set to some S' with a not in S'. The resulting
word W'' has W's complete boundary (forward literal COPY/ERASE replay, all 661 dirty columns) if
and only if

    S' = Sg ⊕ S.

The ADD saving is `1 + |Sg| − |Sg ⊕ S|`. If `Sg ⊕ S` is empty, g is deleted as well.

*Proof.* The two replays agree up to e. Between e and g, induction over the gates shows that W''
differs from W only in register a, by exactly δ. No gate in that window reads a. A gate writing a
uses identical source values in both words, and every other gate sees identical operands. At g,
all registers other than a agree, so the S' sum is the same in both replays. After g,

    a_W   = a + Σ Sg,      a_W'' = a + δ + Σ S'.

These are equal exactly when `Σ (S' ⊕ Sg) = δ` in W's state. By uniqueness this holds exactly when
`S' ⊕ Sg = S`.

After g, W and W'' execute the same instruction sequence. If their states agree after g, their
complete boundaries agree, including the clean-temporary conditions. Conversely, the common suffix
is injective on states where those conditions hold. An ADD is invertible on rows. A COPY into a
zero temporary and the matching ERASE are mutually inverse on that domain. Equal final boundaries
therefore force equal states after g. The reverse replay is the inverse program, so the forward
statement transfers to it. ∎

Frame legality is a separate constraint. The new operands of g must be able to climb monotonically
to g's frame, and the ordered frame paths must stay unchanged. The census therefore classifies each
move twice: by its F2 boundary (always exact under the criterion) and by its frame legality.

**Census class.** For each trailing restoration of a lineage word, the census considers every A
gate g that writes the centre a before a's first read. On all four words, each centre is first
read in A or by the scatter COPY, so no B or C gate can precede that read. The only other writers
of a before the read are the other restorations of the same centre in the D tail. Leaves are never
written in D, so for those pairs `S = {b}` and the saving is `1 + 1 − 2 = 0`. The census replays and
counts these pairs separately. Preparations of a are separated from e by target-block reads of a.
`verify.py` checks every part of this case analysis.

**Joint moves.** Several moves with distinct centres and distinct gates compose provided every
`S_i` avoids the other centres whose differences are still pending at `g_i`. The two instances
satisfy this. The lockstep replay in Section 4 checks it directly.

## 4. Chronological per-cut comparison for the instances

Let W be the PR1062 or PR1188 word and W' its absorbed word. W' deletes three restorations and
edits A gates 288, 290 and 304. `verify.py` replays the D and A prefixes of W and W' in lockstep,
with frames, and checks the following at every cut (3,270 cuts for PR1062 and 2,821 for PR1188):

- The registers that differ are exactly the centres whose restoration has been deleted and whose
  absorbing gate has not yet run. Each differs by exactly its leaf's input column. At most three
  registers differ, at 459 cuts.
- Every register is at the same frame in W and W' at every cut. This is stronger than equal ordered
  frame paths, and the exporter's ordered per-register MOVE records also agree.
- Every differing centre stays at the zero frame until its absorbing gate. Each absorbing gate is
  the first A gate that touches its centre.
- After A[304] the full states are equal. The remaining scatter, B and C instructions are
  identical.

**Physical reading.** For W, the chronological realization comes from PR1194. A proof-only word
with W's A/scatter/B/C and PR589's target-only D passes every inherited owner flag. Its zero-frame D
and W's D have the same complete operator, values and frames, so they give pointwise identical
states before the unchanged continuation. `verify.py` re-checks this splice and the D-operator
equality for both base words. PR1311 did the same for PR1122.

W' and W agree in logical value and frame at every cut except the three pending centres. Each of
those centres sits at the zero frame holding `a + b` (its own input column plus the leaf's input
column). It then climbs to its absorbing gate's frame f, and at that frame immediately receives the
compensating ADD from registers already at f.

The step from equal logical states to equal physical states after that gate uses one inherited
premise:

> **Common-frame / climb additivity.** Identical ordered per-register frame paths plus identical
> logical values give identical physical states, across nonzero frames. Equivalently, the physical
> climb of a sum is the sum of the climbs, and additions at a common frame are additive.

Targets already rely on this premise: after D they climb holding the dirty combination `y + N h`.
PR1194 deliberately restricted its own substitution to frame-zero prefixes and did not apply the
premise to helpers. This package newly uses it for helpers. The verifier's first-climb census
locates the use exactly. On both base words, every helper's first climb out of the zero frame
carries its own input column. On both absorbed words, exactly helpers 506, 507 and 514 first climb
carrying a non-own value, and none of them climbs again before its compensation.

Nothing more is claimed physically. The verifier does not evaluate the premise numerically. Native
5/9/11-stage replay, hosted emission, all-size compiler, rounding/tape and analytic obligations
remain inherited and unexecuted here.

## Accounting consequence

Only three D ADDs disappear, so the D ADDs fall from 5,548 to 5,545. The three absorbing A gates
keep one source each, and C is byte-identical to the base word's C. That C is the literal reverse
of the original A/B z-gates, which is why the inherited literal H4 and `C_is_U_inverse` flags are
false.

The following are all unchanged:

- frames and climbs;
- COPY ranks;
- the paid profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, rank mass 5,129;
- 2,911 MOVE records.

The forward positive bound F is unchanged and the reverse bound B falls slightly. Both strict
precision guards keep their bit lengths. Exact values are in `EXPECTED.json` and `README.md`.
