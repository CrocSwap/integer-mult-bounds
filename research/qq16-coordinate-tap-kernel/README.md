# QQ16: a coordinate tap does not close the selected-input kernel

**Scoped obstruction, with an exact finite certificate; no new supplier or κ.**
The shear and `U2 -> T21` tap in
[PR2268](https://github.com/CrocSwap/integer-mult-bounds/pull/2268) detect the
particular three-port witness from PR2093. A different three-port input,
supported on **1, 16, 88**, remains invisible through the complete retained
QQ16 schedule, although its original selected A input is nonzero.

The result is stronger than this one counterexample:

- Every one of the **96 × 8 = 768** ordinary-source-to-T paired taps fails to
  recover all original selected inputs, even with the A-to-T shear.
- For each of the 96 possible source ports, an invisible input family spans
  **all eight original A values at the identity owner**. This is an
  eight-dimensional image at one owner, not eight dimensions per owner.
- If a boundary controller can read only a fixed set of `1 <= k <= 8` ordinary
  source ports, a family of dimension at least `9-k` in those A values remains
  invisible. Thus **at least nine distinct source ports are necessary in
  this coordinate-access model**. Nine are not proved sufficient.

The positive PR2268 result is preserved: on its old witness, the same tap
still gives final `X_(0,21) = 11 f_37`, with 34 nonzero selected observations,
four forward-history rows and 65 completed-X rows. Detecting that input does
not establish injectivity on the expanded input space.

## Contract and changed premise

Keep the local maps, port partition and complete 19-event ordinary recipe
from [Ali Romman's QQ16 package](../joint-query/README.md). Its first calls
are `F0` and `B_1_2` on pair 0. The allowed outputs are the final selected
A/T fields, all completed-X descendants and all five forward-query histories.
Granting the selected values at every complete-event cut also does not help
the counterexamples below. The required result includes the original
individual selected A inputs; recovering only selected pair sums is different.

After the complete F0 and before B1, permit the logical shear

```text
X_T += X_A
Y_T -= X_A
```

with the A/T lists paired in their displayed order, followed by

```text
X_t += X_u
Y_t -= X_u                 u in U96, t in T.
```

The ordinary source is unchanged. These equations are granted their intended
logical action for free. They are not a claim that the X and Y physical
frames permit bare scalar additions. PR2252's native-frame objection remains
separate, and is not needed for the information obstruction here.

For the `k`-port corollary, the controller may make any homogeneous linear
updates to selected fields using those fixed ordinary ports, including
owner mixing, and may retain their complete arrays as observations. It
leaves ordinary fields unchanged. Selected-only homogeneous controls may
also run at subsequent complete-event boundaries. There is no additional
input-dependent pre-F0 record, no change inside F0/B1, no ordinary-source
mixing before these reads, and no access to other ordinary ports. A dense
query such as `B0 X_U` is **not** one source-coordinate read in this model.
The proof does not equate source-port count with recursive rank or cost.

## Source-bound family and proof

Let `r_p` be column p of the actual centre matrix R. Write
`b_p = b_(p,0)` for the first local chart axis, and

```text
f_v(d) = bit_0(d v), interpreted as the rational integer 0 or 1.
h_p(d) = c_p f_(b_p)(d), p in U96.
```

The fields are constant in every tensor payload coordinate, but may vary
with owner d. The actual owner routes satisfy

```text
rho_s(p) b_p = e_(9+8(s-1)),      1 <= s <= 8.
```

Consequently, if `R_U c = 0`, then for every owner and every nonzero chart,

```text
(B_s h)(d) = (sum_p r_p c_p) f_(e_(9+8(s-1)))(d) = 0.
```

This uses an exact route identity, not a sampling claim about the owner
group. The verifier reconstructs R from the frozen scalar operations,
compares it with the QQ16 packet, and checks the actual orthonormal axes,
involutions and common-axis images for all 112 ports and nine stages. All 1,008
reconstructed route matrices must also occur in the actual QQ16 map registry.
These reconstruction and local-map routines are credited, pinned PR2093
code, not a new independent implementation of its source binder.

Initialize every other pair to zero, and pair 0 to

```text
X_U = h,                  Y_U = 0,
X_A = -P_(0,A) B0 h,       Y_A = -X_A,
X_T = Y_T = 0.
```

Then `f0 = B0 h + ell_(0,A) X_A = 0`. The ordered F0 formulas give
`X_U = Y_U = h` and every selected field zero. If all accessed source
coordinates satisfy `c_u = 0`, their entire owner arrays are zero. The
shear, all such taps and the more general permitted homogeneous boundary
controller therefore leave this state unchanged.

At B1, the future logger sees `B2 h = 0`, the old selected T driver is
zero, and the current query is `B1 h = 0`. Thus the complete B1 output is
`Y_(0,U) = h`, with every other field zero. The first ordinary bridge puts
`-h` in `Y_(1,U)`. F2 acts on pair 0 with zero X source; its history is zero.
The negative bridge cancels the extra `-h` before B3. Every subsequent local
call has zero active-pair input. The remaining bridges and terminal leave
only named final `X_(0,U) = h`, carrying the **former-Y native type**.
It is not a completed-X descendant. All selected cuts, all completed-X
descendants and all five histories are zero. Homogeneous selected-only
controls preserve this trajectory.

This is an exact indistinguishability argument: zero input has the same
allowed observations, while `B0 h != 0` implies a different original A
input because `P_(0,A)` is a selected section. No decoder, linear or
otherwise, can restore both inputs. Rational scaling clears the displayed
denominators if integer input representatives are desired.

### An explicit witness against U2 -> T21

The new source columns and axes obey

```text
r_1 = r_16 + r_88,
b_1 = 21, b_16 = 50, b_88 = 478,
c_1 = 1, c_16 = -1, c_88 = -1; all other c_p = 0.
```

Thus port 2 is identically zero. At the identity owner,

```text
B0 h = (0, 1, 1, 0, -1, 0, 0, -1),
X_A  = (-1/2, 1/2, 0, 0, 1/2, 1/2, 0, 0).
```

This supports a complete tail counterexample to PR2268's proposed full
restoration extension. It does not contradict that PR's stated repair of
one witness. Its support is disjoint from PR2093's `{2,8,85}`. Hence for
any single tapped source port, at least one of these two witnesses has
zero at that source, irrespective of the selected destination. The checker
executes all 768 interface cases and reuses the two checked tails only
after verifying that the full post-interface state is unchanged.

### Eight invisible A dimensions after any one source tap

Let `epsilon_p = bit_0(b_p)` and `D = R_U diag(epsilon)`. The value of
`B0 h` at the identity owner is `D c`. The exact source certificate gives

```text
rank(R_U) = 8,             rank([R_U; D]) = 16.
```

Therefore `dim D(ker R_U) = 8`. More constructively, for each excluded
source u, both parity classes of columns, excluding u, span all of `Q^8`.
The receipt gives two nonsingular 8-by-8 minors for each of the 96 sources.
For example, excluding source 2:

```text
epsilon=0: [6,8,9,10,11,12,16,44], determinant -16,
epsilon=1: [1,3,4,5,25,26,31,35],  determinant  32.
```

Call these column matrices E and O. For any `z in Q^8`, assign
`c_even = -E^-1 z`, `c_odd = O^-1 z`, and zero elsewhere. Then

```text
R_U c = -z + z = 0,        c_u = 0,        D c = z.
```

The original A value at identity is `-R_A^-1 z`, which spans all eight
coordinates. Fraction row reduction, integer Bareiss determinants and
explicit inverse products cross-check each minor. The checker synthesizes
all 96 × 8 basis vectors and checks both equations exactly. The eight
source-2-hidden basis inputs also run through the complete F0/interface/B1
and 17-event tail; the written ordered argument covers every linear
combination and the other 95 sources.

### Any fixed set of at most eight source ports

Let `S` contain k source ports, with `1 <= k <= 8`, and choose any `u in S`.
On `V_u = ker R_U intersect {c_u = 0}`, the preceding 96-case certificate
proves `dim D(V_u) = 8`. Impose the remaining `k-1` equations `c_s = 0`,
`s in S minus {u}`. These are at most `k-1` scalar equations, even though
each read returns an entire owner array: `h_s = c_s f_(b_s)`. Let their
common kernel in `V_u` be W. Then `codim_(V_u) W <= k-1`, so

```text
dim D(W) >= dim D(V_u) - codim_(V_u) W >= 9-k.
```

For `k <= 8` some original A value is still lost. The case `k=0` has
dimension eight already. The inequality follows by choosing a complement
of W in `V_u` and using `D(V_u) = D(W) + D(complement)`.
No independence of the functions `f_v`
on the cover group is presumed: nonzeroness is established at the identity
owner alone. The certificate also includes an explicit eight-port example
constructed from the displayed parity bases: sources `[2,1,3,4,5,25,26,31]`.

This is a necessary support bound, not a sharp minimum for full recovery.
It does not exclude dense ordinary queries, an earlier retained record,
a different first local map, changed ordinary mixing, or a different final
observation contract.

## Reproduction and evidence

From the repository root, standard-library Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-coordinate-tap-kernel
```

The direct replay is

```sh
python3 -I -O -B research/qq16-coordinate-tap-kernel/verify.py
```

Expected direct output:

```text
PASS_QQ16_COORDINATE_TAP_KERNEL single_taps=768 A_defect=8 ports<=8_excluded controls=13 no_new_kappa
```

`RESULT.json` contains the complete deterministic receipt, including all
192 parity minors, the new and credited disjoint witnesses, the source-2
kernel basis, the eight-port example and source hashes. Replay is read-only;
`--emit-result NEW_PATH` explicitly creates a new receipt without overwrite.
All proof-relevant fields and JSON scalar types are compared.

The 13 rejecting controls cover a dependency sign, omitted initial
cancellation, a tap moved onto the new witness's support, tap sign,
omitted negative bridge, final native-type confusion, an added detecting
B0 read, a changed chart axis, an absent packet route, wrong F2 pair binding, a singular parity
minor, changed inherited source bytes and receipt type corruption. The
PR2268 positive control checks its exact full-tail observation census and
`11 f_37` endpoint. The generic registered replay also runs focused artifact
integrity tests and optimized Python execution.

## Cost screen, limits and predecessors

Even granting every proposed operation, source read, frame conversion,
helper, retention, restoration, hosting and precision step zero cost, the
specified recovery contract fails. There is no successful completed
supplier bill or moment to price for this failed interface. No lower bound
on physical native calls, general transcript width or multiplication is
asserted. No full supplier cold replay, native implementation, all-size
precision argument, proof-assistant check, independent human review or
hosted-CI pass is claimed.

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
`SOURCES.json` pins the main inputs; `PREDECESSORS.json` pins exact pending
heads and the unmodified source code retained under `references/pr2093/`.
The claim is in [discussion #2205](https://github.com/CrocSwap/integer-mult-bounds/discussions/2205#discussioncomment-18941101).

- **Ali Romman / PR1969** supplies the ordered local maps, native contract,
  route data, retained tail and original selected-output witness.
- **Adam Gall / PR2093** supplies the common-axis bit-function construction,
  old `{2,8,85}` witness, source reconstruction and logical F/B interpreter.
  Its verifier and README are retained byte-for-byte with their attribution.
- **Cinna Davis / PR2216 and PR2268** supplies the changed selected shear,
  ordinary tap and witness-separation results. This package answers their
  full-kernel follow-up while reproducing PR2268's positive result.
- **@CubeJerry / PR2306** proves that selected-only interventions, including
  a larger deterministic class, cannot repair the credited old witness.
  Its model excludes ordinary reads. Here ordinary coordinate reads are
  explicitly allowed, and the witness is chosen to vanish at those ports.
- **Charles Bethin / PR2252** identifies the native frame mismatch, a
  separate implementation issue. This account's **PR2153, PR2174 and
  PR2189** concern read-only transcripts and recorded-cut recovery, not this
  in-place source-support restriction.
- Rohan Arun, Jeremy Kothe, Hao Yan, Zhihao Chen, DreamingOfClouds and the
  remaining supplier/compiler lineage retain credit through the unchanged
  [QQ16 source notices](../joint-query/NOTICE.md).

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New material is Apache-2.0. The new evidence is author-checked; source reuse
is stated explicitly and is not described as an independent local-map audit.

## Open next questions

1. **Which priced ordinary observation removes the complete kernel?** A
   dense old-chart query is outside this coordinate-support bound. First
   specify the actual observation and test the ordered full kernel, including
   the unknown final-cut retention premise of PR2174. Native access and a
   favorable complete bill remain blockers.
2. **What is the sharp source-support threshold for this restricted family?**
   Nine is only necessary. A first step is to characterize fixed S for which
   `D(ker R_U intersect ker pi_S)` vanishes, then test owner functions beyond
   identity. Eliminating this particular family still would not prove full
   controller recovery; further support census alone does not merit a
   supplier claim.
