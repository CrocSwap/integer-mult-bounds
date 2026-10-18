# An invariant guard envelope for the eight packed additions

**Research audit; no new multiplication exponent.** The original packed
selected-bit primitive permits a substantially smaller exceptional set while
retaining its eight rotations and its existing correction procedure. For
`n = f-1` used segments of width `K`, the new set has exact density

\[
\delta_* = 1-\left(1-2^{1-K}+2^{1-2K}\right)^n
\leq \min\{1,2n2^{-K}\}.
\]

The original sufficient bound is `min(1,80n 2^-K)`. The union-bound coefficient
is reduced by a factor of 40; this is not a measured runtime speedup or an
improvement to the selected conditional kappa. The exact density describes
our **chosen repair envelope**, not the exact set on which the uncorrected
operation is wrong.

This note proves the address-map refinement. The independent integer checker
corroborates it on declared finite domains, checks maximality in a restricted
local guard class, and supplies counterexamples to four weakened guards,
two broken rotation programs, and a reversed correction order.

## Source and scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The source is
[`05-layers.tex`](../../upstream/build/sections/05-layers.tex), specifically
`eq:eight-packed-additions`, `eq:packed-cyclic-shift`,
`eq:packed-guard-interval`, and `lem:packed-selected-bit-rectangle`.
[`CLAIM.json`](CLAIM.json) pins the source bytes, related audits, assignment
seed 62, alternatives considered, and the locally recorded sprint scope.
No pinned coordination issue was present when the claim was made.

The accepted frontier at this base is #626 with #543,
`kappa = 51110230636731/31250000000000000`. It is context for this audit,
not an output of it. The object audited here is the original packed primitive,
also used by the historical short-working-guard reduction. This result does
not automatically tighten the different compact-control primitive or the
selected supplier's current surcharge.

## 1. Four exact local trajectories

Write `B=2^K`, `G=B/2`, and a segment pair as
`u=2g+a`, `w=2h+b`, with `a,b` Boolean and `0<=g,h<G`.
The control bit is `c`. When `c=0`, all eight operations are identities.
For `c=1`, subtracting the fixed translation `(2g,2h)` gives these extrema
over the input and all eight intermediate states:

| Initial `(a,b)` | Range of `u-2g` | Range of `w-2h` | Final pair |
|---|---|---|---|
| `(0,0)` | `[-1,1]` | `[0,1]` | `(2g+1,2h)` |
| `(0,1)` | `[0,2]` | `[0,1]` | `(2g+1,2h+1)` |
| `(1,0)` | `[0,1]` | `[-1,0]` | `(2g,2h)` |
| `(1,1)` | `[0,1]` | `[1,2]` | `(2g,2h+1)` |

Each row follows by substituting its parity pair into the eight specified
updates. Adding even translations does not change any parity predicate,
so these four trajectories establish the table for every integer `g,h`.
The complete trajectories are retained in [`RESULT.json`](RESULT.json).

In particular, the final map is `(u,w) -> (u XOR c,w)`. No assumption that
the scratch value is zero is used.

## 2. A sufficient invariant good set

Use the original positions `j_i=rho+iK`, `0<=i<n`; the highest selected
position remains reserved for the existing elementary XOR. At each used
position require:

- If `c_i=0`, impose no guard restriction.
- If `c_i=1` and `b_i=0`, require `g_i>=1` and `h_i>=1`.
- If `c_i=1` and `b_i=1`, require `g_i<=G-2` and `h_i<=G-2`.

Let `E` be the set of addresses failing at least one requirement. The table
proves that, outside `E`, both local coordinates stay in `[0,B-1]` at every
step, for either value of `a_i`. Therefore every packed whole-slot addition
equals the parallel collection of local additions: no segment emits a carry
or borrow into another segment. This is an induction on the eight updates.
At each update the previously established independent local states supply
the correct parity predicates; their next states remain in range. Bits
below `j_0` and above the used segments remain unchanged.

Thus the eight-rotation permutation `S` agrees off `E` with the ideal
selected-XOR permutation `T`. The conditions for `E` depend on
`c_i,b_i,g_i,h_i`, but not on `a_i`. The ideal map only flips `a_i`, so
`T(E)=E`. Each rotation is a bijection because its offset does not depend
on its target slot. Hence `S` is a bijection as well, and on the finite
complete rectangle

\[
S(E^c)=T(E^c)=E^c,\qquad S(E)=E.
\]

The correction `T composed with S^-1` is therefore supported on `E`.
The original extract, attach destination rank, radix-sort, and reinsert
argument applies to this smaller set. Testing its predicate needs the
current `x,y,z` addresses and a scan of the used segments, all already
within the original `O(A_rect^3)` per-record allowance. Under the original
streaming-operation assumptions, the explicit bound can replace
`delta_bad` by `delta_*`:

\[
O\left(V(L^\tau+1)+M A_{\rm rect}^3+
\delta_* M A_{\rm rect}(R+A_{\rm rect})\right).
\]

The full arbitrary scratch slot is restored. The highest selected bit is
still supplied separately. For `f=1`, `E` is empty and the eight-rotation
part is the identity. The original lemma's `K>=6` is sufficient; the
address-map argument itself works for every integer `K>=1`.

## 3. Exact count of this envelope

At one segment, the complete rectangle makes `c,b,g,h` independent and
uniform over their respective ranges. The bit `a` does not affect admission.
Half of control values have `c=0` and are always good. Conditional on
`c=1`, either scratch parity permits exactly `(G-1)^2` of the `G^2`
guard pairs. Thus

\[
\Pr(\text{good segment})
=\tfrac12+\tfrac12\left(\frac{G-1}{G}\right)^2
=1-\frac2B+\frac2{B^2}.
\]

The used segments are disjoint and the source slot ranges over all its
addresses, giving independent local conditions. Taking the product gives
the displayed formula for `delta_*`. The union bound yields
`delta_* <= n(2/B-2/B^2) <= 2n/B`; cap it at one.
These counts also hold at each fixed spectator coordinate, so payloads
and spectator lengths do not affect them.

For a **fixed source address** with `r` active used control bits, the
conditional envelope density is instead
`1-(1-1/G)^(2r)`. The smaller average formula must not be asserted for
every fixed source fiber. Averaging over the complete source range gives
`delta_*`, which is the domain of the original rectangle lemma.

For example, `K=10,f=5` gives the simple bound `1/128`, compared with
the original `5/16`. These are bounds on the correction fraction under
the same original streaming cost model.

## 4. What is maximal, and what is not

Within local predicates depending only on `(c,b,g,h)`, require that **both**
initial y parities stay inside the segment at every intermediate step.
The conditions above are necessary and sufficient for this property:

- `c=1,b=0,g=0`: parity `a=0` makes y negative at step 1.
- `c=1,b=0,h=0`: parity `a=1` makes z negative at step 2.
- `c=1,b=1,g=G-1`: parity `a=0` makes y equal to `B` at step 6.
- `c=1,b=1,h=G-1`: parity `a=1` makes z equal to `B` at step 5.

The trajectory table proves sufficiency and these witnesses prove necessity
for all K. This is the largest good set in that specified local no-escape
class. It does not minimize the repair set among all possible predicates,
correlated guards, or methods allowing intermediate carries.

In fact, with at most one active used control, the complete scalar identity
descends to the full higher-bit slot modulo a power of two, so `S=T`
everywhere. The `f=2` exhaustive checks find zero actual disagreements
although the envelope has positive density. This illustrates why its exact
count must not be called the exact failure probability.

## 5. Concrete failure witnesses

All four boundary requirements matter once two selected positions are
active. At `K=6,f=3,rho=0,x=65`, deleting the named guard admits each
following address as good under the weakened predicate:

| Deleted condition | Input `(y,z)` | Actual `(y',z')` | Ideal `(y',z')` |
|---|---|---|---|
| y lower boundary | `(0,66)` | `(1,130)` | `(65,66)` |
| z lower boundary | `(3,64)` | `(66,0)` | `(66,64)` |
| y upper boundary | `(62,65)` | `(191,1)` | `(127,65)` |
| z upper boundary | `(1,127)` | `(64,63)` | `(64,127)` |

The checker searches a fixed boundary domain and reproduces these witnesses.
Each has only the deleted guard category triggered. Additional controls
change the sign of line 7, omit line 1, and incorrectly reverse the
composition order in the correction. All seven changes are detected.

## Reproduction and coverage

From the repository root, using only the Python standard library:

```sh
python3 -B research/packed-guard-envelope-audit/verify.py
```

Expected first two lines:

```text
PASS_PACKED_GUARD_ENVELOPE_AUDIT
581888 exhaustive packed states; 37760 boundary/seeded states; 7 negative controls
```

The command checks source hashes, rebuilds all evidence, and compares every
result field against the committed receipt. `--write` regenerates that receipt.
There is no solver, network access, floating-point arithmetic, or imported
repository verification engine.

Completed finite coverage:

- Every local quotient class `(c,b,g,h)` for `K=1,...,7`, testing both y
  parities and all intermediate states.
- Every used-control mask, every full y/z slot value, and every `rho` for
  `(K,f)=(1,3),(2,3),(3,2),(4,2)`: 581,888 states. Unused x bits are fixed
  to zero because neither the rotations nor the predicate reads them.
- Boundary segment values `{0,1,2,3,B-4,B-3,B-2,B-1}` at both extreme
  offsets for `K=6,7,10,16`, with two active controls: 32,768 states.
- 4,992 full-width pseudorandom triples, seed 62, for `K=6,7,10,16`,
  `f=1,2,3,5`, every offset, 32 triples per layout.

The fixed domains are the stopping rule; no unfinished search is hidden.
Each packed case checks the inverse, both ideal and actual exceptional-set
invariance, equality off the envelope, and exact repaired output. The
small exhaustive domains check the density directly. They stress carries
at widths below the original lemma's K>=6; the symbolic proof covers
that lemma's full range and the larger checks exercise it explicitly.

Related baseline checks: the four tests in `test_finite_identities.py`,
the short-guard tests, and the packed-movement tests. The selected supplier
and its certificate are unchanged; no cold replay of that separate
construction is claimed. The written proof is not a Lean formalization,
and the checker is not a fixed-tape implementation. All inherited
streaming, recursion, precision, and analytic hypotheses remain.

## Attribution

Aryan Sudhir (`AryanSudhirDev`), with substantial OpenAI Codex assistance,
2026-10-12 Pacific. New material is Apache-2.0, as required by the repository.
The original eight-operation construction and repair method belong to the
retained OpenAI #109 manuscript and its source license; no upstream file
is modified or re-licensed here. Douglas Colkitt's repository audits,
[`test_finite_identities.py`](../../tests/test_finite_identities.py),
the [packed movement audit](../../docs/packed-movement-audit.md), and the
[short guard reduction](../../docs/research/short-guard-audit.md) are
predecessors. The separate [compact-control audit](../../docs/research/compact-control-audit.md)
is acknowledged as related work with a different primitive.
