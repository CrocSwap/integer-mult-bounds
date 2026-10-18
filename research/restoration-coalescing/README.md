# Restoration coalescing across a recursion batch

Research note: one explicit way to eliminate restoration work, with a complete
cost recurrence, a sufficient correctness condition (and the exact defect
criterion behind it), and a sharp cost boundary. Navinor, with help from
opencode. Apache-2.0. **No new multiplication exponent.**

## Summary

Every recursive child that borrows a dirty workspace stream must return it, and
the inherited contract restores it **after every child** so that the next child
sees the node-entry state. When a node issues `r` children this pays `r`
restoration passes. This note prices a single operator-level change: let the
workspace drift across the batch and replace the `r` restorations by the **one**
composed restoration `(G_r...G_1)^{-1}` at the node exit. The question is not
what a particular assembly does with that slack (that is assembly pricing), but
when this rewrite is even a *valid and pass-reducing identity on the restored
operator*. Two independent questions decide it, both decidable exactly: the
summed-defect criterion (exactness) and closure under cheap composition (pass
reduction).

* **Correctness (vanishing defect; read-free is sufficient, not necessary).**
  The deferred single restoration returns the identical observables (final data
  and final workspace) exactly when the summed defect vanishes,
  `sum_i B_i (G_{i-1}...G_1 - I) = 0` (diagonal readers here; `P_0 = I`). A
  batch in which no child reads the workspace's intermediate value into an
  observable makes every term vanish separately, so read-free is a clean
  **sufficient** condition — but it is **not necessary**: nonzero readers can
  cancel. The note's own reader example only shows one reader child *can* break
  deferral. Exact nonzero-reader counterexamples where deferral is valid are in
  [#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199) (five
  children reading and negating the workspace with coefficients `[1,1,1,-1,1]`,
  restoration `5 -> 1`),
  [#1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203) (distinct
  outputs: per-reader condition `H_i(P_{i-1} - I) = 0`; one shared output at
  batch exit: only the summed defect must vanish), and
  [#1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205) (the
  terminal summed-defect theorem and the prefix theorem `B_i(P_{i-1} - I) = 0`
  per child, which still does not require `B_i = 0`).

* **Cost (composable family; density is not application cost).** Deferral
  removes restoration passes when the individual restoration operators are
  closed under a composition that stays cheap to apply: unit phases -> one phase
  pass, permutations -> one routing pass (`r -> 1`). The pass statement is
  priced under an explicit descriptor hypothesis in the recurrence below:
  composing `r` descriptors is charged `r * c_desc` (`c_desc = O(1)` for the
  succinct parameter-tuple descriptors, `c_desc = Theta(N)` for full length-`N`
  descriptor tables). Matrix density of the
  composed product is **not** an application-cost statement: the composed
  restoration retains its factorization into its cheap factors, and applying
  those factors sequentially costs exactly the eager sum. For the heterogeneous
  mix (a phase, a Walsh transform, a permutation) the composed restoration is
  dense, yet its retained factorization is verified to cost the same `16`
  multiplications as the three structured eager restorations at `N = 8`;
  deferral costs *more* only when no cheap factorization is retained and the
  dense product must be applied directly (`64` vs `16` multiplications at
  `N = 8` — a statement about direct dense application). Structure, not the
  number of restorations alone, decides.

Both facts are checked by one exact stdlib program over Gaussian rationals.
Nothing here changes the selected frontier, `upstream/`, or the assembly.

## Reproduce

From the repository root, Python 3.10+, standard library only:

```sh
python3 -I -O -B research/restoration-coalescing/verify.py
```

Expected first line:

```
PASS_RESTORATION_COALESCING phase=3->1(x3) perm=3->1 hetero_dense=True reader_diverges=True reader_cancels_5to1=True hetero_mults=eager16|factorized16|dense64
```

The command recomputes the certificate and compares every field with
[CERTIFICATE.json](CERTIFICATE.json), failing on any drift. `--json` prints the
full certificate; `--write PATH` writes the same deterministic result elsewhere.
There is no floating point, no random tolerance, and no imported supplier
verifier. Coefficients are exact Gaussian rationals (`Fraction` real and
imaginary parts); the checker builds every operator explicitly at `N = 8`.

## Starting point and scope selection

Base commit `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08` (current `origin/main`).
At this base the selected conditional result is the
`CrocSwap/integer-mult-bounds#1094`-on-`CrocSwap/integer-mult-bounds#1087`
assembly,
`kappa = 836330098538459/500000000000000000 = 0.001672660197076918`; see the
[selected record](../../certificates/selected-result.json) and
[current status](../../docs/research/current-status.md). This note does not
adopt any larger number from a pending pull request.

The OS-generated assignment seed was **53**, assigning the recursive-interface
track (one explicit way to eliminate boundary or restoration work, with a
complete cost recurrence). The three candidates I weighed were: coalescing
per-child dirty-workspace restoration (chosen); deferring the compact-control
"exceptional-address repair charged at every node"; and eliminating the Walsh
entrance/exit boundary between same-subset children. The seed selected
restoration coalescing because it is the one whose correctness and cost
conditions can both be decided exactly and independently, without re-opening a
closed supplier search.

There was no pinned sprint coordination issue reachable here. The local
[claim](CLAIM.json) records the three candidates, the overlap check against
`research/seed51-clean-residual-dilation` (seed 51, recursive-interface track:
a spectral-split residual encoder, a different object), and the scope.
Exact source and dependency heads are in [SOURCE-PINS.json](SOURCE-PINS.json).

## The model

State is a data stream `D` and a borrowed dirty workspace stream `W`, each of
`N` Gaussian-rational positions, plus a read-only source vector `s`. A node
issues `r` children. Child `i` applies an invertible workspace operator `G_i`
(as scratch) and contributes a data increment:

```
scratch-only child i :  D' = D + B_i s ,  W' = G_i W
reader child i       :  D' = D + B_i W ,  W' = G_i W      (reads W)
```

The inherited **eager** rule restores `W` to its node-entry value `w0` after
every child, i.e. it applies `G_i^{-1}` immediately. The **deferred** rule lets
`W` drift and applies the single composed restoration
`(G_r ... G_1)^{-1} = G_1^{-1} ... G_r^{-1}` at the node exit. Observables are
the final `D` and final `W`. The child data work `sum_i B_i(·)` is identical in
both schemes and cancels from the comparison; only restoration is priced.

This is the same restoration invariant the repository already charges: dirty
connectors and private child scratch are restored
(`CrocSwap/integer-mult-bounds#905`, `CrocSwap/integer-mult-bounds#929`,
`CrocSwap/integer-mult-bounds#951`;
[universal-connector-boundary](../universal-connector-boundary/README.md)), and
the compact-control construction "restores arbitrary values ... and charges
exceptional-address repair at every node" ([current status](../../docs/research/current-status.md)).

## Complete cost recurrence

Write `Restore(N)` for one restoration pass over `N` coefficient positions. In
the repository's additive accounting a coefficient pass is a `Scan(N,p)`; a
diagonal unit-phase restoration is exactly one such pass, and a permutation
restoration is one routing pass. Let `r` be the children per node. The node's
restoration term is

```
eager   :  r * Restore(N)
deferred:  1 * Restore_composed(N)
```

**Composable family (phases, or permutations).** The composition stays in the
family: the composed restoration is again one phase descriptor (one `Scan(N, p)`)
or one permutation descriptor (one routing pass), so the applied restoration is
one pass once the composed descriptor exists. Forming that descriptor is the
composition step, and its cost depends on how a descriptor is represented; the
recurrence below states the representation it prices.

**Descriptor hypothesis (the representation behind the `O(r)` term).** A
restoration descriptor is a fixed-size parameter tuple, not an arbitrary
`N`-entry table:

* phase: `G = diag(omega^(a * chi(x)))` for a per-node character
  `chi : {0..N-1} -> Z/q` fixed once (the checker's shape is
  `chi(x) = popcount(x)`, `q = 4`), with one stored exponent `a`;
* permutation: a rotation `x -> x + s (mod N)` (the checker's shape), or any
  dihedral map `x -> +-x + s (mod N)` with a constant-size tuple.

Composing `r` descriptors in either family then combines `r` tuples
(`a <- sum_i a_i`; `s <- sum_i s_i` mod `N`): `O(r)` tuple operations,
`c_desc = O(1)` per descriptor, and the product stays in the family. Applying
the composed descriptor is exactly one pass, `Scan(N, p)` (`N` phase
multiplications) or one routing pass (`N` moves, `0` multiplications), each pass
priced as `Restore(N)`. The node pays

```
eager   :  r * Restore(N)  +  0
deferred:  1 * Restore(N)  +  r * c_desc
```

and saves

```
(r - 1) * Restore(N)  -  r * c_desc  =  (r - 1) * Scan(N, p)  -  r * c_desc
```

so composition is charged, not absorbed. Over a recursion with `r` children per
node and `d` levels, the restoration *pass* overhead falls by the same factor `r`
(`sum_nodes r*Scan -> sum_nodes 1*Scan`) plus the added composition charge
`sum_nodes r * c_desc`, while every child term `(k/m)^sigma / W` is untouched.
The full node recurrence, restoring only the changed term and charging
composition, is

```
R(N, {k_i}) =  sum_i  (k_i/m)^sigma / W   +  Restore(N)  +  r * c_desc  +  unchanged
                                 ^ was r * Restore(N) in the inherited rule
```

with `c_desc = O(1)` under the descriptor hypothesis.

**Outside the hypothesis (general descriptors).** For arbitrary per-position
unit phases or arbitrary permutations stored as full length-`N` tables there is
no succinct composition: forming the composed descriptor must read `r` tables of
`N` entries, so the composition bill is `Theta(r * N)` (and `N` storage), not
`O(r)`; the applied restoration is still one pass. The recurrence holds there
with `r * c_desc` replaced by `Theta(r * N)`. The `O(r)` term is claimed only
under the descriptor hypothesis; the general descriptor case is recorded at its
`Theta(r * N)` charge, not as `O(r)`.

**Heterogeneous family.** The composed restoration `G_1^{-1}...G_r^{-1}` is a
dense matrix here (64 of 64 entries nonzero at `N = 8`), but density of the
matrix is not a statement about application cost. The composed operator
*retains its factorization* into the three cheap structured inverses; applying
them sequentially costs exactly the eager sum — `16` multiplications at
`N = 8`, verified against the exact dense product on every basis column — so
with the factorization retained deferral is multiplication-neutral (`16` vs
`16`) and pass-neutral (three factor applications, nothing collapses to one
pass). Deferral costs *more* only when no cheap factorization is retained and
the dense product must be applied directly: `64` vs `16` multiplications at
`N = 8`, `4x`. In this example deferral is therefore rejected as a pass
reduction (nothing to save), not because dense entries imply quadratic
application cost; the `64` vs `16` pair is a statement about **direct dense
application** only.

This is a complete invoice for the restoration term only. It is not a transfer
into the tight fixed-tape overhead allowance, and it makes no claim that the
restoration term is binding in the selected assembly. If restoration is a
lower-order term beside the child recursion, the induced change to `kappa` is
zero. **No stronger bound is claimed.**

## Exact evidence and limits

`verify.py` builds every operator explicitly at `N = 8` over Gaussian rationals
and checks, on the actual vectors:

1. **Phase batch (3 children, read-free).** Deferred equals eager on both
   observables; the composed restoration is verified to be diagonal and applied
   as one pass. Restoration passes `3 -> 1`; multiplications `24 -> 8`.
2. **Permutation batch (3 children, read-free).** Deferred equals eager; the
   composed restoration is verified to be a permutation and applied as one
   routing pass. Restoration passes `3 -> 1`; moves `24 -> 8`; multiplications
   `0 -> 0`.
3. **Reader example (sufficiency, not necessity).** A single reader child is
   inserted. The final workspace is still restored to `w0`, but the data output
   of the deferred scheme differs from eager by an explicit nonzero
   Gaussian-rational vector, and the exact summed defect is nonzero. This is a
   concrete counterexample to *unrestricted* deferral — one reader child **can**
   break it, so read-free is sufficient. It is **not** evidence that read-free is
   necessary.
4. **Nonzero-reader cancellation (necessity fails).** Five reader children, each
   reading and negating the workspace with coefficients `[1,1,1,-1,1]` (the
   counterexample shape of
   [#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199)). Every
   child reads `W`, four of them after nonidentity drift, yet the exact summed
   defect `sum_i B_i (G_{i-1}...G_1 - I)` is verified to be the zero matrix and
   deferred equals eager on both observables for the tested `w0`. The
   restoration bill falls from five negations to one (`5 -> 1`). The
   checker computes the defect matrix as exact Gaussian rationals and asserts
   it vanishes, so the cancellation is an algebraic identity on all workspace
   coordinates, not a coincidence on one vector.
5. **Heterogeneous composition (cost; density is not application cost).** A
   phase, a Walsh transform and a permutation compose to a dense operator (64 of
   64 entries nonzero). The structured-form detector self-checks each cheap
   application against the exact dense product on the standard basis before
   using it, so the low cost figures are certified against the exact operator
   rather than assumed. Direct dense application of the composed product is `64`
   multiplications against the eager structured sum `16`: the `64` vs `16` pair
   is a statement about **direct dense application**. Applying the same exact
   composed restoration through its **retained factorization** (the three
   structured inverses in sequence, self-checked against the dense product on
   every basis column) costs exactly `16` — the eager sum — so deferral with the
   factorization retained is multiplication-neutral here, and costs more only
   when no cheap factorization is retained.

For each batch the composed restoration is *derived* from the exact dense
product `G_1^{-1} ... G_r^{-1}` and then checked to agree with it, so a
composition-order bug cannot silently flatter the result. What this establishes
is instance-level: exact observables and exact costs at `N = 8` for `r = 3`
(phase batch, rotation batch, heterogeneous mix), `r = 2` (single reader) and
`r = 5` (cancellation batch), with every composition performed as an exact
dense product. It does not establish the recurrence for arbitrary `r` and `N`:
the `O(r)` descriptor composition and the one-pass composed application are the
charges of the descriptor hypothesis above (an implementation hypothesis about
a succinct descriptor representation, not a tested identity), and outside that
hypothesis the recorded charge is `Theta(r * N)`. Controls that must
fail do fail: no "no candidate" claim, no impossibility theorem, no optimality
claim for the eager rule.

The scope is a restoration-elimination mechanism, its recurrence, and its exact
applicability boundary. It is **not** an all-size physical compiler, a numerical
precision contract, a common tape, an analytic transfer, a full owner schedule,
or the integer-multiplication theorem. The finite checks are exact algebraic
identities and exact cost counts; they do not certify a whole E8 word or the
selected `kappa`. Neither the selected frontier nor `upstream/` changes. Inherited
all-size/compiler, hosting, precision/tape and analytic assumptions remain with
their existing constructions.

## Relation to concurrent and prior work

Two concurrent, same-track contributions already price *restoration deferral* at
the assembly level, and this note is deliberately narrower and complementary,
not a replacement or a re-derivation of either.

* **[CrocSwap/integer-mult-bounds#1012](https://github.com/CrocSwap/integer-mult-bounds/pull/1012)**
  (thakrarsagar, seed 57) prices restoration deferral of the U8 helper
  rank/frame *climbs* inside the hosted T37 recurrence, using the hosting lemma
  and the `8k+1+hosted+idle=73` coverage identity, and reports exact kappa
  ceilings. Its conclusion is that deferral is *mass-neutral* there and its value
  is consolidation inside shared hosting windows. That is a statement about rank
  mass and window capacity in one frozen assembly.

* **[CrocSwap/integer-mult-bounds#974](https://github.com/CrocSwap/integer-mult-bounds/pull/974)**
  (avirazza, same track) prices the same boundary classes with zero parent cost;
  thakrarsagar's note independently reproduces its T37 one-unit value.

This note asks a different question at a different layer: **as an operator
identity, when does replacing `r` restorations by one composed restoration
preserve the observables and actually remove passes?** Its two answers — the
summed-defect criterion (correctness; read-free is one sufficient case) and the
composable-family condition (cost) — are exact algebraic facts about the
restored operator, independent of any assembly, kappa ceiling, hosting lemma, or
T37 payload. The cost unit here is a
coefficient/routing pass (a diagonal unit phase is one `Scan`, a permutation is
one `Route`, per the retained recurrence vocabulary), not the rank mass those
assembly notes count. So there is no contradiction with the "mass-neutral"
finding there: helper climbs are rank-advancing frame work whose mass is
coverage-productive, whereas the restoration passes coalesced here are
phase/routing passes whose operators compose. This note gives the
operator-level preconditions and a standalone sub-second exact verifier (no T37
archives, no pinned engines); those notes give the assembly-level ceiling
effect. Both are needed before deferral can be placed in a real supplier call.
Where thakrarsagar's note shows the T37 slack is consolidation in shared
windows, this note shows exactly which restoration families admit a genuine
`r -> 1` pass reduction at all, and which (heterogeneous) leave nothing to
collapse — costing more only under direct dense application of the product.

This is a second, independent treatment of the restoration question using a
meaningfully different method (exact Gaussian-rational operator algebra and
structure detection, versus assembly-level pricing on frozen payloads), as the
sprint invites. It does not claim priority on "restoration deferral" and does not
reproduce either note's numbers.

## Correction after review (read-free is sufficient, not necessary)

The original version of this note claimed the read-free condition was
*necessary and sufficient*, and treated density of the composed heterogeneous
product as proof that deferred application costs more. Both claims were wrong;
the corrected statements are the ones above. The evidence:

* **[CrocSwap/integer-mult-bounds#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199)**
  (thakrarsagar) gives an exact nonzero-reader counterexample in the shape the
  checker now replays: five children that each read and negate the workspace
  with reader coefficients `[1,1,1,-1,1]` share one final restoration
  (five negations -> one) with identical observables. Its exact interval
  criterion `E_ab = sum_{i=a}^{b-1} b_i (p_i - 1)` (and the general linear form
  `sum B_i (P_i - I) = 0`) replaces the iff, and its checkpoint planner shows
  intermediate observation points can force the restoration bill back up.
* **[CrocSwap/integer-mult-bounds#1203](https://github.com/CrocSwap/integer-mult-bounds/pull/1203)**
  (mightyOil) separates the two observation contracts: with distinct outputs
  the exact all-input condition is `H_i (P_{i-1} - I) = 0` per reader; with one
  shared output observed only at batch exit only the summed defect must vanish.
  Its example `G_1 = swap(0,1)`, `G_2 = G_3 = I`, readers `0, e_0, e_1` has
  nonzero readers whose defects cancel exactly.
* **[CrocSwap/integer-mult-bounds#1205](https://github.com/CrocSwap/integer-mult-bounds/pull/1205)**
  (adamgall) states the terminal theorem for the additive model exactly —
  agreement for every dirty input iff `sum_i B_i (P_{i-1} - I) = 0`, with
  `P_j = G_j ... G_1`, `P_0 = I` — and the prefix theorem
  `B_i (P_{i-1} - I) = 0` per child, which still does not require `B_i = 0`.
  Its census of 46,656 three-child tuples finds 7,712 terminal-safe tuples
  containing a nonzero reader.

The correction was requested in the batch review comment on this pull request
([comment](https://github.com/CrocSwap/integer-mult-bounds/pull/1155#issuecomment-6161612247),
[batch review record](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient300-review.md)).
The original evidence is untouched and still runs: the reader example shows
only that one reader *can* break deferral, and the `64` vs `16` pair counts
**direct dense application**. The checker now additionally verifies the exact
summed-defect criterion on both reader examples and the retained-factorization
cost of the heterogeneous composition (`16` factorized = eager `16` against
`64` direct dense at `N = 8`). Remaining open: the checkpoint/partition
optimum over intermediate observation points (priced by
[CrocSwap/integer-mult-bounds#1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199)
for its own model, not derived here), and the question of when a dense
composition whose factors are *discarded* must be paid as `N^2` — this note
answers only that direct dense application is the expensive case.

## Correction after review (composition and routing are charged)

A second review pass
([comment](https://github.com/CrocSwap/integer-mult-bounds/pull/1155#issuecomment-6197859152),
[batch review record](https://github.com/CrocSwap/integer-mult-bounds/blob/main/docs/research/community-efficient1100-review.md))
found the cost recurrence pricing `r`-descriptor composition at `O(r)` and the
composed restoration at one `Scan`/routing pass with no descriptor
representation behind those terms, and the explicit `N = 8` matrix tests as the
only evidence. The recurrence now states the descriptor hypothesis (fixed-size
parameter tuples; `O(r)` tuple composition; one-pass application once the
composed descriptor is formed) and charges composition explicitly as
`r * c_desc`; the general full-length-descriptor case is recorded at its
`Theta(r * N)` composition bill instead of `O(r)`; and the evidence section
separates what the `N = 8` checker establishes from the priced general
recurrence. No verified algebraic content or cost number from the first
correction or from the original cases changed.

## Attribution

The eager per-child restoration contract and the dirty-connector model are
repository-wide: `CrocSwap/integer-mult-bounds#905`/
`CrocSwap/integer-mult-bounds#929`/ `CrocSwap/integer-mult-bounds#951` (Chafik
Boukhalfa), `CrocSwap/integer-mult-bounds#877`/
`CrocSwap/integer-mult-bounds#896` (Gareth Davidson),
`CrocSwap/integer-mult-bounds#934`/ `CrocSwap/integer-mult-bounds#943`/
`CrocSwap/integer-mult-bounds#944`/ `CrocSwap/integer-mult-bounds#953` (Ross
Richardson), and
[universal-connector-boundary](../universal-connector-boundary/README.md). The
compact-control per-node restoration/repair charge is credited to Douglas
Colkitt's retained construction ([current status](../../docs/research/current-status.md)).
The unequal-width child recurrence `(k/m)^sigma / W` is from the retained
[complex batching note](../../notes/batched-complex-rows.tex).

The sibling recursive-interface note
[research/clean-residual-dilation](../clean-residual-dilation/README.md) (seed 51,
Douglas R. Colkitt with Codex) prices a *spectral-split residual encoder* and its
own per-stream dirty restoration. This note is a different object (restoration
coalescing across a batch, not encoded hosting), reaches a different and
independent boundary (vanishing summed defect + composable family), and does not
rely on its
conclusions. Where both charge a "restoration" pass, the accounting vocabulary is
shared but the mechanisms are distinct. This encoder-free coalescing result,
exact checker and scoped recurrence were developed by Navinor with help from
opencode, under the repository's Apache-2.0 license.
