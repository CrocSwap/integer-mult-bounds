# The isolated P104 side correction has full matrix rank

**Scoped algebraic lower bound.** For the 104 P104 ports in the pinned fixture,
the correction matrix `I-G/2` is nonsingular, even though the Gram matrix `G`
has rank eight. Thus every decomposition of this isolated correction into
rank-one outer products needs at least 104 summands. This is not yet a bound
on recursive children or the completed supplier bill.

## Exact result

PR1972's channel contract, as pinned in the native realization, maps each
target row to

```text
y_t + sum_s <r_t,r_s> x_s / 2.
```

Here `G[t,s] = <r_t,r_s>` is the Gram matrix on the P104 ports. The fixture
defines P104 by removing the eight `F0` and eight `C` root lines from the 120
unoriented E8 root lines. The verifier independently enumerates those 120
lines from the doubled E8 coordinate model, removes the pinned 16, and uses
`G[t,s] = dot(r_t,r_s)/4`.

It finds `rank(G)=8`, while the exact fraction-free determinant is

```text
det(2I-G) = 8721064880344833042121878122499340763136.
```

Therefore `I-G/2 = (2I-G)/2` has rank 104 over the rationals. Any sum of `m`
rank-one matrices has rank at most `m`, giving the 104-summand lower bound;
the usual column decomposition shows this is the exact minimum for this
matrix problem.

The result rules out a *low matrix-rank* side correction at this cut. If each
summand necessarily consumed one unit of the channel's COPY-rank budget, 104
would exceed the existing COPY56 by 48. That cost correspondence has not been
proved here. A circuit may fuse the correction with the `G/2` channel or use
the existing scalar additions and carrier schedule; neither is ruled out by
matrix rank alone. No new κ or complete P104 supplier is claimed.

## Exact sparse factorization in a common chart

The root data also gives an exact factorization `G = BᵀB`, where the eight
rows of `B` are the P104 root coordinates and `B` has 568 nonzero entries.
Using the native witness's eight `Q` registers as arbitrary dirty scratch, the
following scalar word restores their initial values and applies the correction:

```text
Y += Bᵀ Q / 2
Q += B X
Y -= Bᵀ Q / 2
Q -= B X
Y += X
```

The net target map is `Y + (I-G/2)X`, and the source and scratch maps are
restored as required. Counting one scaled addition per nonzero factor entry
gives `4·568 + 104 = 2,376` scalar additions, versus 4,992 nonzero entries in
the direct correction matrix. The verifier checks the rational factorization,
the resulting matrix, and that the pinned native witness ends with `X` and `Q`
in the same rank-nine frame.

The 104 target registers end in rank-eight subframes of `F9`. A second checker
uses the pinned native compiler and independent Gaussian interpreter to compile
and verify each lift to `F9` and return, including the complete Clifford phase.
Each round trip uses two rank-one transports, for 208 extra rank mass.

This gives an explicit end-cut finite correction invoice: rank mass 208 and
2,376 scalar additions. Appended to the pinned `G/2` channel, the finite
channel-plus-correction invoice is rank mass 2,576 and 5,000 scalar additions.
All source rows and all 72 dirty helper rows remain unchanged, and the target
frames return to their required endpoints. This excludes global hosting and
idle costs and does not show whether fusion can reduce the bill or whether the
result is an admitted supplier.

## Fixed-interface moment screen

The pinned P104 word has width `m=9` and `W=280` arbitrary boundary columns:
104 sources, 104 targets, and 72 dirty helpers. Adding the correction's 208
rank-one transports changes the exact paid profile to rank mass 2,576, while
`mW=2,520`. Thus the zero-saving moment is

```text
2576 / (9 · 280) = 322/315 > 1.
```

Every child rank is below nine, so for any saving `a ≥ 0`,
`(r/9)^(1-a) ≥ r/9`. The whole fixed-interface moment therefore already
exceeds one before hosting or idle charges are added. This rules out the
appended end-cut word as a contracting supplier under the pinned 280-role
interface. It does not rule out fusion that changes the child profile or the
interface; the exact rank-104 matrix lower bound does not price such fusion.

An exact rational moment enclosure gives a role-count relaxation for a changed
interface. For both the appended round-trip profile and the direct-`F9`
endpoint profile, if the profile is held fixed and every added role is assumed
free, at least 287 roles are needed to reach the selected κ, and at least 291
to reach κ=0.01. These are optimistic thresholds only: real added roles need
their own boundary, recursive and hosting costs, and any changed profile must
be recalculated. Even with those free roles, the strict moment slack is only
about `2.2e-4` at the selected κ threshold and `1.5e-3` at κ=0.01.

One endpoint fusion was checked directly: replace each target's final
rank-`d`-to-eight transport with a rank-`d`-to-nine transport and change its
exit adapter. For all 104 targets the complete Clifford endpoint operator,
including phase, remains identical. The transport costs one extra rank per
target, and the new exit adapter costs one rank per target (the old adapter
was rank zero). This also adds 208 rank mass, so ending directly in `F9` does
not evade the fixed-interface obstruction.

## Interior retuning screen

I tested whether the existing scalar delivery schedule can be retuned without
changing its helper trajectories or adding frame transports. The verifier
replays every rational register row and, for each target `Y_t`, collects the
row of every helper and every other target register at every time its frame
spans the same underlying subspace as `Y_t`'s frame. Basis conversion within
that subspace is treated as free, and snapshots from different times are
pooled. This is a generous source set: it permits arbitrary rational
combinations of all such snapshots, beyond inserting scalar adds or retuning
the existing `Q`/`D` deliveries along one chronological path.

For all 104 targets, both the unit source row `X_t` and the actual side
correction row

```text
C_t = X_t - sum_s G[t,s] X_s / 2
```

are outside the exact rational span, even after including other target rows.
The helper-only spans have ranks 74–78; the pooled helper-plus-target spans
have ranks 177–181. The fixed witness itself never reads a `Y` row into
another register. Since the exact correction row is outside each pooled span,
no sequence of scalar additions from unchanged snapshots in the same
underlying frame subspace can supply the correction. A target carrier would
need a changed trajectory or a new frame subspace. This is not a general
fusion impossibility result.

I also relaxed the question to one arbitrary new row direction `h` shared by
all targets, allowing each target its own coefficient and any combination of
its fixed-span rows. For each target let `S_t` be its pooled fixed span and
`L_t = S_t + span(C_t)`. A usable common direction must lie in every `L_t` but
outside every `S_t`. The exact intersection `∩L_t` has dimension 72, yet is
contained in every `S_t`. Thus no single added row direction can supply any
target's correction while serving all 104 targets, even in this relaxed
algebraic model. Also, among the 104 natural candidate directions `C_j`, each
can serve only target `j` modulo its fixed span, so this basis gives no
cross-target reuse. At least two shared directions are necessary; the minimum
dimension for arbitrary added directions remains open.

As a finite candidate screen, I tested every pair from twelve natural X-space
directions: the eight root-coordinate rows and four index patterns (constant,
linear, alternating, quadratic). After reducing each direction and each
target correction modulo that target's pooled fixed span, none of the 66 pairs
spans even one correction coset. This rules out only those 66 candidate pairs;
it gives no lower bound beyond two for an arbitrary shared space.

I also exhausted all 5,356 spaces spanned by pairs of the actual correction
rows `C_j`. A modular rank screen rejects pairs that cannot span a target
coset, and every surviving incidence is confirmed over `Q`. No pair covers
more than one target. Along with the single-row result, this rules out a
two-direction space whose basis vectors are chosen from the natural correction
rows; it says nothing about pairs of arbitrary linear combinations.
I also tested all 1,248 mixed pairs with one `C_j` and one of the twelve
natural X-space directions. Exact confirmation found 80 target/pair
incidences, and no mixed pair covers more than one target. These finite
families give no two-direction supplier, but do not exclude a pair outside
them.

## Shared-space dimension is between 96 and 97

The pooled-span question now has a much sharper exact bracket. Let `X` be the
104-dimensional coordinate space of the source rows, and let `pi_X` discard
all other boundary coordinates. Any shared space `H` satisfying
`C_t in S_t + H` must satisfy

```text
C_t in pi_X(S_t) + pi_X(H),     dim(pi_X(H)) <= dim(H).
```

For an exact 96-target subset recorded in `EXISTING-DELIVERY-SPAN.json`, the
sum of the projected fixed spans has rank 8, while adjoining those 96
correction rows raises the rank to 104. Their cosets are therefore independent
modulo that sum. If `h_t` is a projected shared-space representative for each
of those targets, the `h_t` are independent too. This proves `dim(H) >= 96`
for arbitrary shared directions in the full 280-coordinate space.

An explicit 97-dimensional witness is recorded by its 97 correction-row
indices in the same artifact. It was found by checking all 686 spaces obtained
from the 98-row witness by one deletion or one deletion plus an exchange with
one omitted correction row; 121 of these spaces cover all targets. The chosen
witness was then checked directly against every original pooled span over the
rationals. Thus the fixed-span minimum lies in `[96, 97]`. This remains a
relaxed algebraic witness, not a chronological producer, and does not price a
circuit or improve the paid P104 profile. The remaining exact question is
whether dimension 96 is possible. Deleting each of the 97 witness rows in turn
gave 97 candidate 96-row spaces; the best covers 102 targets. This deletion
screen does not rule out other correction-row bases or arbitrary 96-dimensional
spaces.

## Chronological snapshot correction

Although `C_t` is outside the helper span, adjoining the single source unit
`X_t` puts it inside for every target. The exact-chart snapshot spans already
contain a representation with one `X_t` term and at most 18 helper terms. The
verifier chooses one such representation per target and inserts each helper
addition immediately after the witness event where that exact register row is
available in `Y_t`'s chart. It then routes the terminal `Y_t` transport through
the full `X_t` chart, adds the remaining `X_t` term, and returns to the original
endpoint frame.

This gives a chronological arbitrary-input correction word with 1,248 helper
snapshot additions and 104 source-unit additions, 1,352 scalar additions
total. The support histogram including the source-unit term is 7, 10, 13, 16,
or 19 per target. Exact replay restores all sources and all 72 dirty helpers,
produces `Y_t + X_t` for every target, and preserves endpoint frames. The 104
terminal detours add rank mass 208; the compiler verifier checks every full
Clifford edge composition including phase. The resulting paid profile matches
the direct-F9 endpoint profile, so at `m=9`, `W=280` the zero-saving moment is
still `46/45 > 1`. Including the original channel, the finite word uses 2,576
rank mass and 3,976 scalar additions. It improves the scalar count over the
2,376-add sparse correction word, but remains noncontracting before hosting.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/p104-side-correction-rank-obstruction/verify.py
python3 -I -O -B research/p104-side-correction-rank-obstruction/verify_transports.py
python3 -I -O -B research/p104-side-correction-rank-obstruction/verify_existing_delivery_span.py
python3 scripts/research_package.py --package research/p104-side-correction-rank-obstruction --check-only
```

The exact verifier uses only the Python standard library. It checks the pinned
channel identity, native witness and fixture hashes, reconstructs the root
lines and Gram matrix, computes exact ranks and determinant, verifies the
common-chart dirty-scratch factorization and scalar-addition count, checks
invariance under line-sign choices, and rejects a missing puncture and a wrong
Gram scaling.
`verify_transports.py` checks the 208 compiled endpoint frame transports, the
combined finite invoice, exact moment bounds and free-role thresholds, and the
direct-`F9` endpoint rewrite for all targets.
`verify_existing_delivery_span.py` exactly replays all 280 rational rows and
checks that both each unit source row and each actual `I-G/2` correction row
lie outside the pooled span of every fixed helper or other-target snapshot
that is ever available in the same underlying frame subspace, even when basis
conversion is treated as free. It also computes the common correction
extension intersection and tests every natural correction row as a shared
direction. It screens all 66 pairs from a twelve-direction natural X-space
family (maximum target coverage zero), and all 5,356 pairs of actual correction
rows (maximum target coverage one, with rational confirmation after a modular
rejection screen). These are finite candidate families, not a lower bound for
arbitrary pairs. It also screens all 1,248 mixed correction/natural pairs
(maximum target coverage one). It proves an arbitrary-H lower bound of 96 by
projecting onto X and gives a 97-row correction-space witness that serves all
targets in the fixed pooled spans. It generates `SNAPSHOT-CORRECTION.json` and replays the 1,352-add
chronological correction word using exact-chart helper snapshots plus
source-unit detours.

The package-level `--check-only` command currently needs a newer Git than the
workspace provides: its `git cat-file --batch -z` invocation is unsupported by
the installed Git 2.34.1. The exact verifier and JSON/diff checks run
independently of that package-manifest check.

## Open next questions

- **Try fusion against the obstruction.** Can the correction be fused into
  existing frame edges so the paid rank mass falls below 2,520 at the same
  width-nine, 280-role interface? Fixed helper trajectories cannot supply any
  `I-G/2` correction row, even when every helper and other-target snapshot in
  the same underlying frame subspace is pooled and basis conversion is free.
  The fixed pooled-span minimum is between 96 and 97. Try to prove or refute
  whether 96 dimensions work, then find a chronological `Q`/`D`/`G`
  producer change or transported target carrier that realizes the minimum,
  replay the exact operator and recompute the paid profile before owner
  placement.
- **Change the interface.** Could a different role inventory or width avoid
  the fixed-interface moment obstruction while retaining arbitrary dirty
  helper restoration? The unchanged profile needs at least 7 extra free roles
  for selected κ and 11 for κ=0.01; construct and fully price any such roles
  before treating the result as a candidate supplier.

## Credit

The P104 fixture is inherited from Josie Elliston / PR1071 through the pinned
PR1972 source. Rohan Arun / PR1972 supplies the complete frame-model `G/2`
channel; PR1991 supplies its concrete native Clifford realization. This
package adds the exact correction-rank certificate, common-chart scalar
factorization, endpoint transport screens, fixed-interface moment bound,
pooled correction-row obstruction, one-shared-direction lower bound, and a
lower-addition chronological snapshot correction word.
Prepared with substantial OpenAI Codex assistance; no independent human
review or proof assistant is claimed. Apache-2.0.
