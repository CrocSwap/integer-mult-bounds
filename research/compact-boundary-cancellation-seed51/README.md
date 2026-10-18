# Compact boundary cancellation requires completed repair

**Research note / scoped negative result. No new kappa.** Assignment seed 51
(Windows OS CSPRNG), recursive interfaces. Analysis base
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`; its selected conditional kappa was
`1661960547713947/10^18` (#942). Submission base
`ba82555c64e1879e4b7decce28186f208fcb8262` selects #1042 at
`1672188119205421/10^18`. This package changes neither construction.

The explicit proposed mechanism was to keep a compact parity operation open
across a recursive boundary and replace its return by the same forward word,
using the ideal operation's involution. The raw four-rotation implementation
is not an involution.
This note gives the exact one-digit obstruction, its complete support and
order, and the remaining cost recurrence. It does not identify a defect in the
existing repaired construction.

## Precise statement and proof

Use one compact digit (`n=1`, `f=2`, offset `rho=0`). Let `B=2^G`, let
`Q=2^N` be the whole target-slot modulus, and assume `G>=1`, `N>=G+2`.
In the retained physical implementation `N=2K`. A control bit `z` is fixed;
the other source bits and the arbitrary back digit are spectators. The
earlier-source sequence S is, in execution order,

```
y <- y + 2*z*t                 mod Q
t <- t + (y mod 2)             mod B
y <- y + z*(1-2*t)             mod Q
t <- t - ((y mod 2) XOR z)     mod B
```

Each temporal update is physically swap/rotate/swap. These swaps restore the
back field exactly. The ideal T is `(y,t) -> (y XOR z,t)`.

If `z=0`, both y updates vanish and the temporary load/unload cancel. If
`z=1`, write the incoming parity as a. For a=0 there is no temporary load,
and the net target displacement is 1. For a=1 and `t<B-1`, the temporary
becomes t+1 and the net displacement is -1. For a=1 and `t=B-1`, the
temporary wraps to 0; the target displacement is `2B-1`. In every case the
last update restores t. Since Q and 2B are even, these parity statements
remain true at target wraparound. Thus, on the entire rectangle,

```
S(y,t,z) = ((y XOR z) + 2B*[z=1, y odd, t=B-1] mod Q, t, z).
S^2(y,t,z) = (y + 2B*[z=1, t=B-1] mod Q, t, z).
```

The single-word disagreement fraction is `1/(4B)` over z,y,t. The repeated
boundary's disagreement fraction is **`1/(2B)`**, or **`1/B` conditional on
z=1**. This is an exact support, not the sufficient guard envelope from the
original note. All values of the unused back field multiply numerator and
denominator equally. On the exceptional z=1, t=B-1 fibre, the exact order of
S is `Q/B=2^(N-G)`: its even powers translate by 2B, whose additive order is
Q/(2B), and its odd powers flip parity and cannot fix a point. Consequently
no fixed even repetition count cancels all widths.

A production-domain witness has `G=2,K=6,x=1,y=33,t=3,b=2`:
S sends y to 40, then 41; x,t,b remain unchanged. The target guard alone is
safe (`8 <= floor(y/2) < 24`). Saturation of t is the missing condition.
This scales to every `K>=G+4` with `y=8B+1,t=B-1`: the target guard is safe,
but S^2 shifts y by 2B. It is not a phenomenon restricted to tiny empty
guard intervals. The omitted highest selected bit is zero in these witnesses.

## What the boundary optimization can actually do

Let E be the **completed, repaired** earlier-source operation controlled by
the parity of a compact front digit u. It preserves u,t,b and is exactly an
involution. Write L_x for the raw modular compact load from x. A later-source
word has the pattern `E L_x E L_x^-1` in execution order, followed by its
outer exceptional repair and highest-bit operation. Two adjacent E's cancel
only when those E's are actually adjacent in the complete program. Moving
outer repair or a recursive child across that boundary needs a separate
commutation/changed-layout proof. This note supplies neither.

Even granting those adjacencies, using raw S instead of E leaves the
translation above. For an isolated repeated raw pair, its exact correction
is a translation by -2B on `z=1,t=B-1`. The predicate is invariant under S^2;
the correction therefore restores the identity on every address. The
verifier checks this constructive correction, but does not claim a physical
fixed-tape implementation saving.

In particular, two later-source blocks concatenate as
`E L_x E L_x^-1 E L_z E L_z^-1`. There are no adjacent E's: the inverse
load intervenes. Equal E labels alone do not permit cancellation. No
commutation with L is assumed.

Price the favorable boundary mechanism before implementation. One isolated
forward/return pair of earlier-source raw words uses eight compact swaps and
eight rotations. A complete ideal E pair can be deleted entirely if adjacent;
a raw S pair left in place needs the correction above. A literal S inverse
already provides an exact alternative return with the original eight swaps
and eight rotations. With an intervening child H, `S^-1 H S` remains the
appropriate conjugated program (composition notation); replacing the inverse
by S needs additional proof, even for the identity child. This optimistic
fixed number of eliminated pairs changes only a node constant. Repair,
highest-bit operations, source/control arithmetic and tape transport must
still be billed. It is not a supplier invoice or an attained construction.

For a new isolated raw-pair repair, delta=`1/(2B)` over the full complete
rectangle. Under the retained fixed-tape repair interface, extraction,
inverse address calculation, sorting and reinsertion cost

```
O(V + M*A^3 + delta*M*A*(R+A)),  V=M*R.
```

With `G=4*ceil(log2 p)+6`, `A=O(p)` and superpolynomial record width R,
the extra term is O(V). It cannot be silently deleted, even though it is
asymptotically absorbed. Retain source access, rewinds, parking, clearing,
row splits, reservations and every recursive child. Granting a fixed number
of admissible cancellations changes a node constant, not the recurrence

```
F(e) <= (s/W)*F(e/m) + O(G^tau*e^tau + 1),
F(e) = O(e) for e < d^beta.
```

The child multiplier s/W, chi and leaf exponent are unchanged. This scoped
mechanism alone establishes no improved conditional kappa. Growing batches,
changed rank profiles, multi-digit repair support and transporting children
in a permuted layout are separate problems.

## Reproduction and evidence

From the repository root, Python 3.9+ and standard library only:

```sh
python3 -B research/compact-boundary-cancellation-seed51/verify.py
```

Expected: `PASS_COMPACT_BOUNDARY_CANCELLATION states=40800 production=1176 controls=8 no_new_kappa`.
Exact per-domain counts are in RESULT.json. `python3 -O -B .../verify.py` checks the same obligations
with Python assertions disabled. The checker uses explicit failures.

Sixteen complete one-digit domains have G=1..4 and N=G+2..G+5; every z,y,t
is checked for the parity formula, bijection, literal inverse, repeated-pair
support, exact exceptional order and constructive pair repair. A separate
retained physical interpreter checks targeted two-slot cases including every
back digit in each fixture. Those comparisons are not exhaustive over the
whole source-slot rectangle. Eight negative controls distinguish restoration,
inversion, pair support, guard admission and repair sign. The universal
statement rests on the written parity proof, not a finite or formal theorem
claim. No search or optimality assertion is made.

Run `python3 -B research/compact-boundary-cancellation-seed51/test_package.py`
for a clean relocated replay under `-I -O -B` and four deliberately injected
faults: source drift, receipt drift, formula sign and repair sign. Expected:
`PASS_COMPACT_BOUNDARY_PACKAGE relocated_isolated_optimized=PASS faults=4`.
VALIDATION.json records the local environment and affected existing tests.

SOURCES.json pins the consumed sources and the historical #942 construction/review
chain using Git blob SHA1 and SHA256 of LF-normalized text. The original selected
record now lives at `certificates/checkpoints/frontier942.json`, with an identical
Git blob, so the verifier does not freeze the mutable current-selection pointer.
All other pinned inputs are unchanged between analysis and submission bases.
CRLF-to-LF is the
only permitted normalization; both hashes are checked. No archives or frozen
supplier payloads are regenerated. CLAIM.json records selection and overlap.

## Scope and attribution

Credit Douglas Colkitt's compact-control movement/layout construction and
retained simulator, OpenAI's upstream multiplication framework, and the
selected #942 lineage credited in the maintainer review. John-Michael
Smith's #763 compact-carry audit studies later-source interior digit carries;
Precious Oyetunji's #773 and Aryan Sudhir's #735 study the distinct wide-slot
gadget. Their existing guard/repair conclusions are respected. This note adds
an exact **repeated earlier-source boundary** law, support and order, rather
than reopening their carry searches. #1012 studies hosted T37 restoration
mass; #1057 studies additive echo memory. Neither result is imported here.

Prepared for @martinxxx9 with substantial OpenAI Codex
assistance in derivation, implementation, verification and writing; no human
identity beyond the authenticated GitHub account is inferred. New material is Apache-2.0 under the repository license.
All-size/compiler, common-label/mutable-source, hosting, fixed-tape,
precision and analytic obligations remain inherited. No full multiplication
proof, current supplier improvement or hosted CI result is claimed.
