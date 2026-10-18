# Restoration coalescing across a recursion batch

Research note: one explicit way to eliminate restoration work, with a complete
cost recurrence, a sharp correctness boundary, and a sharp cost boundary.
Navinor, with help from opencode. Apache-2.0. **No new multiplication exponent.**

## Summary

Every recursive child that borrows a dirty workspace stream must return it, and
the inherited contract restores it **after every child** so that the next child
sees the node-entry state. When a node issues `r` children this pays `r`
restoration passes. This note prices a single operator-level change: let the
workspace drift across the batch and replace the `r` restorations by the **one**
composed restoration `(G_r...G_1)^{-1}` at the node exit. The question is not
what a particular assembly does with that slack (that is assembly pricing), but
when this rewrite is even a *valid and pass-reducing identity on the restored
operator*. Two independent conditions decide it, both decidable exactly.

* **Correctness (read-free batch).** The deferred single restoration returns the
  identical observables (final data and final workspace) if and only if no child
  reads the workspace's intermediate value to build an observable output. If the
  workspace is write-only scratch across the batch, deferral is exact. One reader
  child breaks it; the note gives a concrete counterexample over Gaussian
  rationals.

* **Cost (composable family).** Deferral removes restoration work only when the
  individual restoration operators are closed under a composition that stays
  cheap to apply. Diagonal unit phases compose to a diagonal unit phase and
  permutations compose to a permutation, so a batch of `r` such restorations
  collapses from `r` passes to `1` pass. When the restorations are a *mixture*
  (a phase, a Walsh transform, a permutation), the composed restoration is a
  dense linear map; applying it once costs `N^2` scalar multiplications against
  `16` for the three structured eager restorations in the tested batch, so
  deferral *loses*. Structure, not the number of restorations alone, decides.

Both facts are checked by one exact stdlib program over Gaussian rationals.
Nothing here changes the selected frontier, `upstream/`, or the assembly.

## Reproduce

From the repository root, Python 3.10+, standard library only:

```sh
python3 -I -O -B research/restoration-coalescing/verify.py
```

Expected first line:

```
PASS_RESTORATION_COALESCING phase=3->1(x3) perm=3->1 hetero_dense=True reader_diverges=True
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

**Composable family (phases, or permutations).** `Restore_composed(N) =
Restore(N)`, because the composition stays in the family. The node saves

```
(r - 1) * Restore(N)  =  (r - 1) * Scan(N, p)
```

plus the `O(r)` bookkeeping of composing `r` phase/permutation descriptors,
which is not an `N`-volume pass. Over a recursion with `r` children per node and
`d` levels, the total restoration overhead falls by the same factor `r`
(`sum_nodes r*Scan -> sum_nodes 1*Scan`), while every child term
`(k/m)^sigma / W` is untouched. The full node recurrence, restoring only the
changed term, is

```
R(N, {k_i}) =  sum_i  (k_i/m)^sigma / W   +  Restore(N)  +  O(r)  +  unchanged
                                 ^ was r * Restore(N) in the inherited rule
```

**Heterogeneous family.** `Restore_composed(N) = Theta(N^2)` (a dense
matrix-vector product), against `sum_i` of the structured eager restorations.
At `N = 8` the exact counts are `64` dense multiplications versus `16` across
the three structured restorations, so the deferred rule is `4x` more expensive
and is rejected. The obstruction is structural: composing a phase with a Walsh
transform with a permutation destroys the structure that made each individual
restoration cheap. Deferral does **not** remove work here.

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
3. **Reader negative control (correctness).** A single reader child is inserted.
   The final workspace is still restored to `w0`, but the data output of the
   deferred scheme differs from eager by an explicit nonzero Gaussian-rational
   vector. This is a concrete counterexample: the read-free condition is
   necessary, not a stylistic choice.
4. **Heterogeneous negative control (cost).** A phase, a Walsh transform and a
   permutation compose to a dense operator (64 of 64 entries nonzero). The
   structured-form detector self-checks each cheap application against the exact
   dense product on the standard basis before using it, so the low cost figures
   are certified against the exact operator rather than assumed. Deferred `64`
   multiplications beat nothing: the eager structured sum is `16`.

For each batch the composed restoration is *derived* from the exact dense
product `G_1^{-1} ... G_r^{-1}` and then checked to agree with it, so a
composition-order bug cannot silently flatter the result. Controls that must
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
read-free condition (correctness) and the composable-family condition (cost) —
are exact algebraic facts about the restored operator, independent of any
assembly, kappa ceiling, hosting lemma, or T37 payload. The cost unit here is a
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
`r -> 1` pass reduction at all, and which (heterogeneous) make it worse.

This is a second, independent treatment of the restoration question using a
meaningfully different method (exact Gaussian-rational operator algebra and
structure detection, versus assembly-level pricing on frozen payloads), as the
sprint invites. It does not claim priority on "restoration deferral" and does not
reproduce either note's numbers.

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
independent boundary (read-free + composable family), and does not rely on its
conclusions. Where both charge a "restoration" pass, the accounting vocabulary is
shared but the mechanisms are distinct. This encoder-free coalescing result,
exact checker and scoped recurrence were developed by Navinor with help from
opencode, under the repository's Apache-2.0 license.
