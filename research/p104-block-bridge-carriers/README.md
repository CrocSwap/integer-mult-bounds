# Whole-bridge carriers and their complete invoice

**No new κ.** The three thin queries in the pending chain root preserve a larger
idle carrier space collectively than they preserve one at a time. We determine
that space exactly, prove why ordinary moving frames do not enlarge it, and show
that two specified target-mask families repay the apparent saving under
complete accounting.

This extends the structural question behind
CrocSwap/integer-mult-bounds#6833,
CrocSwap/integer-mult-bounds#6841, and
CrocSwap/integer-mult-bounds#6845 by replacing pointwise thin-query annihilation
with commutation through the entire three-query bridge. The target masks and
complete native invoice are retained and charged. Disjoint-time packets need
not be globally orthogonal; simultaneous packets must represent independent
field directions. It is a changed carrier contract, rather than another seed
for the previous two-mask static search.

## Results

1. **Exact bridge decomposition.** For every positive odd arm pair, the bridge
   is `B=I-2(EE*+vz*)-2uw*`, where the two projector summands are orthogonal,
   `uw*` is rank-one square-zero, and all cross-products vanish. The entire
   common native idle plane is the bridge's minus-one eigenspace. A packet may
   commute with this block while failing individual thin-query annihilation.
2. **Precise ordinary-frame limitation.** Transparent relocation of the same
   fresh-address job through a normalized source block has identical endpoint
   projectors in a common ordinary chart. Both neutral and minus sectors, and
   both column and row data, matter. Sector-dependent recursive adapters remain
   outside this result.
3. **Uniform full-span accounting obstruction.** Activating the empty field
   alone loses for power tariffs r^(1−κ), with 0<κ<1. Making all nonempty fields productive
   at every full site has a worse complete invoice than the source, even with
   unrestricted favorable idle pooling, for
   every positive odd arm pair and every `0<κ<1`. The per-port source advantage
   is at least `1-((8m+1)^(1-κ)-(8m)^(1-κ))>0`.
4. **Exact finite partial-span certificate.** All 81 central dense-mask choices
   on the fixed `9|9` root have negative complete optimistic signed gain at the
   pending benchmark `κ=.00337180`. The best certified complete upper bound is
   `-42.130440268650981066`. This is a fixed-benchmark statement, without an
   assumed monotonicity theorem in κ.
5. **A useful quotient and a concrete unresolved obligation.** The common idle
   plane can be removed algebraically, turning the three-query bridge into one
   query on 18 dimensions. The original productive masks do not descend:
   all 18 direct compressions have a rank-one idempotence defect and all 153
   pairs have rank-two commutators. Local rank-two repairs exist, but an independently reproduced known support cap
   excludes **every** commuting rank-two supporting family for this quotient.
   Larger or noncommuting productive interfaces remain open.

The complete proofs, model assumptions, quotient limitation, and exact LP-dual
argument are in [PROOF.md](PROOF.md). The [independent review](review/REVIEW.md)
derives capacities from eigenspace nullspaces and agrees with all 13,851
interval-capacity entries. Its separate rational arithmetic also verifies all
81 complete dual prices; neither checker imports the author's model.

The [quotient support corollary](QUOTIENT-SUPPORT-COROLLARY.md) proves that
Ali Romman's known theorem permits at most two commuting rank-two supports
for a defect-one rank-one root in dimension at least four. The quotient needs eighteen.
This closes the minimal common-stage branch, independently of pricing or
actual-prefix commutation, and makes the remaining interface question precise.

The [source-bound prefix audit](QUOTIENT-PREFIX-FLOOR.md) transfers the known
even-interior stage floors from CrocSwap/integer-mult-bounds#6717 to this exact
quotient. It checks all eight affected full positions and excludes both
uniform rank-three stages and the proposed balanced 54-incidence census.
This is an applicability check of predecessor geometry, not a new general
prefix theorem or a claim that the displayed necessary floor is sharp.

## Source pins and relationship to the selected result

The upstream base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The selected record at that base has κ `.003125804`; it is not edited here.
The experiment uses the pending source in
CrocSwap/integer-mult-bounds#6833 at exact head
`51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`, whose stated benchmark is `.00337180`.
The retained source formulas, complete local profiles, proof and licenses have
SHA-256 and Git-blob pins in `retained/SOURCE-PINS.json`.

The comparison with CrocSwap/integer-mult-bounds#6845 uses its scoped research
result at `1b3f081debf631b690f56a2f67645984a5c70fe4` as background; no unmerged
code from that package is a replay dependency. Earlier whole-idle and pure-hub
limitations in CrocSwap/integer-mult-bounds#6841 and
CrocSwap/integer-mult-bounds#6840 motivate the changed block premise. This
package does not repeat the fixed-native-word hub-gauge pairing result in
CrocSwap/integer-mult-bounds#6844.

The outer comparison retains all 18 native signed profiles and all 104 ports.
It does not prove or remove the inherited `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, or `analytic_recovery` assumptions. It makes no
source admission, selected-frontier, or unconditional multiplication claim.

## Reproduction

From the repository root, Python 3.12 and its standard library suffice:

```sh
python3 -B research/p104-block-bridge-carriers/verify.py
```

Expected: JSON with `"status": "PASS"`, `"claim": "No new kappa"`, 25 odd/odd
source shapes, 81 dense-mask cases, 13,851 checked dual columns, the exact
negative complete upper bound above, and eight contract/failure controls.
The full deterministic report is [EXPECTED.json](EXPECTED.json).
The same checks survive `python3 -O -B`. To run both these checks and the
independent geometry and pricing replays through the registered package runner:

```sh
python3 scripts/research_package.py --package research/p104-block-bridge-carriers
```

Expected final line: `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome
`negative-result`. The independent replays report
`PASS_INDEPENDENT_EIGENSPACE_CAPACITY_REVIEW` and
`PASS_INDEPENDENT_81_DUAL_COMPLETE_PRICES`.

The replay verifies the actual retained source bytes, independently constructed
query formulas, all finite algebraic and quotient identities, every capacity
and rational dual inequality, the complete fixed native profile, and report
consistency. Rational logarithm and alternating-exponential enclosures are used
for all proof-relevant powers. There is no floating feasibility decision.

The optional discovery command regenerates candidate duals using
`numpy==2.3.5`, `scipy==1.17.0` and HiGHS:

```sh
python3 -B research/p104-block-bridge-carriers/discover.py --output /tmp/p104-block-bridge-duals.json
```

Solver output is a candidate only; the standard-library replay is decisive.
Alternative valid duals need not have identical floating solver provenance.
The scientific search domain was exactly all `p=0..8,q=9..17` central dense
masks, every contiguous packet interval, and the declared real-rank LP
relaxation. There was no randomized search and no early stop; all 81 cases were
completed. Other mask patterns, noncontiguous packets, changed native words,
and new recursive representations were not searched.

## Negative controls and proof boundaries

The verifier distinguishes block commutation from pointwise annihilation by a
legal positive fixture. It also checks reversed bridge order, a false
minus-sector-only relocation, image-only preservation with a changed dual row,
misleading separate nullspace dimensions, a native-idle projector that fails
bridge covariance, and corrupted dual multipliers/overstated prices.

The packet tariff counts one paid address copy for each field direction. It
does not silently combine field rank and Gaussian address rank into one call.
Ordinary adapter prices are relaxed to zero only for an upper bound on possible
gain. A different recursive interface or a different productive target basis
needs a new complete invoice and is not excluded by this package.

## Open next questions

- **Can the 18-dimensional quotient support a useful larger or noncommuting
  productive interface?** Root closure and local rank-two projector repairs are explicit
  in Section 7 of [PROOF.md](PROOF.md). The corollary excludes every commuting rank-two supporting family,
  beyond the first repaired pair's rank-two commutator. The known prefix floors
  also block uniform rank three and balanced total incidence 54. A larger-stage
  candidate must satisfy all these geometry constraints and have a favorable
  complete target/paid profile; a noncommuting representation needs an explicit
  recursive boundary with all induced source, adapter and restoration costs.
- **Can a recursive, sector-dependent carrier adapter beat the ordinary-frame
  limitation?** Such an adapter is not covered by neutral-sector rigidity. A
  first step is a single explicit two-site intertwiner with its own Gaussian
  recurrence and all inherited costs. The blocker is a favorable complete
  invoice, not merely an algebraic change of basis.
- **Can other mask patterns use the extra bridge eigendirection economically?**
  The 81 central dense cases and full-span theorem leave other patterns and
  packet organizations open. Begin with a new target geometry whose optimistic
  complete price is positive; do not repeat the certified finite family.

## Attribution

Contribution by Jerry Chen / **@CubeJerry**, with substantial assistance from
**OpenAI GPT-6 Astra Pro** for derivations, code, bounded experiments, and
independent cross-review. The exact source root is by DreamingOfClouds with
Claude Opus 5.5 via Claude Code; the retained notice preserves its lineage to
thu-nmrc, zxv, Ali Romman, and the native/helper work. The independent eigenspace
review was performed by a separate concurrent reasoning agent without importing
this model's capacity implementation. All new material is Apache-2.0; retained
source notices and licenses are unchanged.
