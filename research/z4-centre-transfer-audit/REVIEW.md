# Independent interface audit: typed echoes and recursive centre charges

This note audits one implication in PR2464 at commit
`f364b97ff4700147fc06e622b79952b9fe6c4fa8`, against repository base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The reviewed
[README](inputs/pr2464/README.md) and [verifier](inputs/pr2464/verify.py) are
preserved with [external source pins](EXTERNAL-SOURCE.json):

> Does removing one same-source order-four echo wrapper imply removing eight
> rank-8 recursive children from the selected complex supplier?

**No such implication follows from the certified typed interface.** The
scalar saving is compatible with an unchanged recursive histogram. The
shared-centre histogram remains a conditional planning ledger until a native
compiler/refinement identifies the removed recursive calls. This is a scoped
non-entailment result, not a counterexample to the echo identity or a lower
bound against other implementations.

PR2464 explicitly disclaims supplier admission and a new kappa, and leaves
the required native child intertwiner unestablished. Those qualifications are
correct and material. The issue is the stronger identification in its
Delta-H discussion, `one wrapper = 8 rank-8 children`, and the description of
the shared ledger as reached by a concrete mechanism. The exact moment of a
postulated histogram cannot establish that identification.

## 1. Complete arbitrary-input contract

Let the output and work spaces be modules, and let `P`, `Q` be invertible
linear maps with `P^4 = Q^4 = I`. Each fixed indivisible child has the map

```
C_i(D,W) = (D + R_i W, P W),       R_i P = Q R_i.
```

Its literal inverse is

```
C_i^-1(D,W) = (D - R_i P^-1 W, P^-1 W).
```

Replacing that inverse by another forward child is not licensed. Roles `D`,
`X`, and `W` are disjoint; `X` is unchanged throughout a call. The word uses
exact additive operations and paid powers of the two frames. It promises
canonical output and restored workspace at its declared endpoint, with no
canonical observation required at the internal phase cuts.

For a child list `L`, write `A_L = sum_(i in L) R_i`, with multiplicities.
The aligned-frame invariant immediately before a child is

```
(D_current,W_current) = (Q^t (D_0 + A_prefix W_0), P^t W_0).
```

Intertwining gives `R_i P^t = Q^t R_i`. After the child, the workspace phase
is `t+1` and the output phase is `t`. Applying `P^(s-t-1)` to work and
`Q^(s-t)` to output restores alignment at `s`. With terminal phase zero, the
complete batch is therefore

```
B_L(D,W) = (D + A_L W, W).
```

Let `J_X` mean `W += X`. Reading the following word chronologically, the
root echo is

```
E_L = [J_X, B_L, J_X^-1, B_L^-1].
```

For every input `(D,X,W)`, its intermediate output increments are
`A_L(W+X)` and `-A_L W`, so

```
E_L(D,X,W) = (D + A_L X, X, W).
```

This holds for arbitrary, possibly correlated, input dirt. It uses neither
zero workspace nor a probabilistic independence assumption. Two lists using
the same source and output give

```
E_M after E_L = E_(L concatenated with M)
```

as endpoint maps. Equality of endpoints does not assert equality at a
caller's intermediate delivery cut.

The pinned PR1391 fixture specializes this to `D` of width 8 and `X,W` each
of width 24. `P` rotates the two four-cycles in each of three work octets;
`Q` rotates the output's two four-cycles; `R_i` selects one work octet.
Its 56-column exact integer check covers every dirty state in these roles.
The written argument above also holds for arbitrary list lengths and any
exact intertwiners satisfying the stated hypotheses. It says nothing about
rounding, fixed-precision admission, or native host/address realization.

## 2. What the scalar saving removes

In the pinned scalar emitter a forward child has 62 ADDs and 6 NEGs: eight
reader ADDs followed by the workspace frame. Its inverse has the same
primitive count, 68. Each source shear `J_X` or `J_X^-1` has 24 ADDs. If
`g(k)` is the paid frame-boundary cost of a `k`-child batch, a complete echo
has

```
scalar_cost(E_k) = 136 k + 48 + 2 g(k).
```

Using `g(1)=60` and `g(2)=88`, the smallest pair has

```
two separate echoes:  2 (136 + 48 + 120) = 608,
one joint echo:       272 + 48 + 176     = 496,
saving:               48 + 2(120-88)     = 112.
```

Thus 48 of the saved primitives are the removed 24-row in/out source
shears; 64 are the reduction in paid frame boundaries. The separate and
joint words both retain two forward children and two literal inverse
children. The analogous five-plus-five comparison also retains every
forward/inverse child occurrence.

The count 8 in the fixture's output width, the ordinary matrix rank of its
reader, and a native complex child's Fourier rank are different quantities.
Their numerical coincidence supplies no cost correspondence.

## 3. Exact tariff countermodel

Let `H` take values in nonnegative finite recursive-rank histograms, with
additive composition. Give each fixed indivisible child and inverse an
arbitrary tariff `h_i^+`, `h_i^-`. Assign zero recursive tariff to the
explicit source shears and frame ADD/NEG words. These operations still pay
their positive scalar costs from section 2; zero recursive tariff does not
mean zero physical work.

If child `i` appears `m_i(L)` times in list `L`, then the literal words give

```
H(E_L) = sum_i m_i(L) (h_i^+ + h_i^-).
```

Consequently,

```
H(E_L) + H(E_M) = H(E_(L concatenated with M)).
```

This equality holds for every choice of nonnegative child tariffs, including
different forward and inverse tariffs. It does not rely on equality of
child matrix ranks, phase choices, or an assumed optimal schedule.

For a concrete nonzero countermodel, let `e_8` denote one rank-8 call, and
attach `h_0^+ = h_0^- = h_1^+ = h_1^- = 4 e_8` to the two distinct one-child
lists. Each separate echo then has tariff `8 e_8`; both the separate pair
and the joint echo have tariff `16 e_8`. They retain the exact endpoint
identity and the 112-primitive scalar saving, but save no rank-8 calls.
This is a formal tariff extension of the typed interface, not a claim that
these hypothetical child tariffs have a native selected-supplier compiler.
At the concrete scalar level actually emitted by PR1391, the entire word
uses ADD/NEG and has no identified recursive children at all.

The countermodel disproves only derivation of `-8 e_8` from the typed
identity alone. A different native decomposition might allow such a saving;
its exact map and complete invoice would be additional evidence.

## 4. The missing cost-preserving host refinement

The selected complex local profile has eight rank-8 centre transports per
call. The historical complex construction in
[`split-centres-global/PROOF.md`](../split-centres-global/PROOF.md) explains
their semantic origin: a centre total is copied in its rank-eight
hyperplane, its private copy is lowered by the exact frame-change operator,
then scattered and erased. Scalar operations occur at equal labels. The
frame-changing transport is an additional operation beyond the scalar
copy. PR1391's `J_X` is instead the dirty shear `W -> W+X`, with no native
frame-changing child in its emitted word.

The immutable-window sentence quoted by PR2464 is in the historical
**bit** geometry, whose address operators are involutions. The companion
complex proof separately preserves sequential private-work lifetimes.
Neither historical lifetime statement provides the absent identification
of a PR1391 wrapper with eight complex rank-8 transports.

A transfer certificate needs at least the following concrete data:

1. A named pair of native calls and the complete source/target/workspace
   owner and chart maps at the actual cuts. Explain how one fixed typed
   source `X` represents both calls and how the typed output represents all
   their demanded totals or target increments.
2. Exact native realizations of the child readers and `P,Q`, including
   `R_i P = Q R_i`, scalar phases, and the adapters into and out of the typed
   roles. Preserve arbitrary ordinary helper dirt and the actual private-work
   initialization/restoration contract.
3. A complete emitted replacement whose public endpoint is the composition
   of the original native calls, whose scratch is restored, and whose
   intermediate observations and work lifetimes meet the amended caller
   contract. All active ancestor rows and other reserved outputs remain
   excluded from child scratch.
4. A literal correspondence between the deleted native operations and
   eight rank-8 children, together with every replacement child, source
   access, owner/chart transport, scalar operation, and changed live family.
   Derive the full histogram and stock from this word; do not supply the
   new histogram as an independent premise.
5. Precision and tape admission for that word. The exact integer identity
   does not absorb the known persistent-pair row-L1 increase from 30 to 42.

These obligations may be grouped under a broad hosting workstream. Merely
widening a COPY/ERASE window, however, proves none of items 1, 2, or 4.
Likewise, assigning zero recursive overhead to the typed scalar word does
not assign zero cost to its missing native adapters.

PR2464's verifier independently checks the supplied histograms' arithmetic,
but obtains the changed count by the literal assignment
`hist_shared[8] = 576`, and the eliminated mass by
`eliminated_units_per_pair = 64`. The controls using these constants verify
their arithmetic consequences. They do not supply a native rewrite or the
refinement above. This note does not dispute the conditional moment
arithmetic, and does not independently certify its transcendental enclosures.

## 5. Prior boundaries and exact scope

The existing
[`selected-centre-adjacent-pair-seed01fcb1`](../selected-centre-adjacent-pair-seed01fcb1/README.md)
census rules out direct owner-identical adjacent source boundaries in its
fixed 144-call schedule. It leaves transported sources and changed schedules
open. The distinct
[`selected-centre-composed-source-rank`](../selected-centre-composed-source-rank/README.md)
package supplies a rank-16 scalar-projection witness for the particular
time-0/time-1 pair, including the complete first scalar call. Its own limits
explicitly prevent promoting that witness to a native recursive-call lower
bound. Neither result is reproved or strengthened here.

This note contributes the additive-tariff non-entailment and the explicit
missing refinement for the order-four echo. The proof is valid for all exact
typed lists with the stated disjoint roles, fixed same source, intertwining,
literal inverses, and endpoint-only observation contract. The finite fixture
is the 8+24+24 scalar interface. No result is claimed for rounded maps,
arbitrary scalar interleavings, a changed child decomposition, an all-size
compiler, a precision-admitted supplier, or a new multiplication exponent.
This is a written mathematical proof, with a finite replay supplied elsewhere
in this package; it is not a formal-kernel proof.

An accurate transfer statement is: *the typed scalar saving is certified;
the shared-centre histogram is a favorable conditional ledger whose native
realization and full charge remain open.* This retains PR2464's useful
scalar and conditional pricing results and its explicit no-admission status.

## Open next question

Can one actual native centre episode expose the required order-four reader
and identify its frame-changing charge with the typed wrapper? The smallest
useful next artifact is an explicit native boundary map and charged compiler
for one episode, followed by one pair. A successful map alone is insufficient:
the corresponding child ledger must show where the eight purported deletions
occur. Until that artifact exists, the budget calculation remains conditional.

## Attribution

PR2464 is by Aaron Wang with opencode assistance. The pinned typed mechanism
and persistent pair are from Cinna Davis's PR1391/PR1410 with OpenAI Codex
assistance, extending the credited cyclic/output-frame predecessors. The
centre-sharing overhead relaxation and its limits are from
[`centre-sharing-overhead-budget`](../centre-sharing-overhead-budget/README.md).
The selected geometry and adjacent/composed-source predecessor packages
retain their own authorship and licenses. This independent interface note
was prepared with OpenAI Codex assistance, separately from this package's
replay implementation, without independent human or proof-assistant review.
New material is Apache-2.0.
