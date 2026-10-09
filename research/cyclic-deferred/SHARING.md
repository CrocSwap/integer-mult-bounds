# Shared completed cores with physical source gauges

Completed-core sharing with deferred starts: construction check

Let sigma_s be the initial inner frame of physical scratch slot s and let
E_s = sigma_s^perp in F_2^24. A completed scalar core restores every physical
scratch slot individually and has no data/scratch off-diagonal block.
Frame telescoping therefore gives actual scratch map C_end C_start^-1.
In stage one this is C_F24 C_sigma^-1 = C_E. The reflected stage starts at
zero and ends at E; after the retained outer background source is inverted,
stage two has the same C_E residual. The inverse scalar word does not change
this sign. Arbitrary physical input a is interpreted as C_start^-1 a; no
unpaid entrance conversion or clean-value hypothesis is introduced.

At outer triple t_b, the residual is C_(E_s tensor <t_b>), or its transpose.
For an orthonormal outer group J the subspaces for distinct b are orthogonal,
so exact weight modulo four gives product residual C_(E_s tensor span J).
Its required complement has explicit orthogonal decomposition

 D_(s,J) = (sigma_s tensor span J) + (F_2^24 tensor (span J)^perp),

of dimension 576 - |J| (24 - dim sigma_s). Thus full groups of 24 pay
24 dim sigma_s; groups of 8 pay 384 + 8 dim sigma_s. The unchanged exterior
of rank 384 is correct only when sigma_s=0.

Each triple basis vector of J has weight 3, so its quadratic form contributes
one copy of -q_sigma. For the four partial groups, PR128 supplies 8 negative
triple axes and 8 positive unit axes in the outer complement. Tensoring these
with 24 unit inner axes adds 192 negative and 192 positive axes. The retained
endpoint-gauge-complex normal form applies to every nondegenerate quadratic
module, including alternating planes, as one child of the full residual
rank with paid binary address changes and quadratic unit-phase passes.
Its normalized scalar for each sigma block is a fourth root of unity.
There are 8 or 24 identical blocks, so that scalar cancels exactly. The 192
additional negative-axis phases also cancel. Tensor transposition preserves
all weights and hence the stage-two signed conclusion.

The companion `gauge_phase.py` checks all 470 distinct physical source frames, covering
26597 live slots after compensated reuse: orthogonal decomposition into odd lines and hyperbolic
planes, projector symmetry/idempotence, actual mod4 weights on all 301
quadratic coefficient points, exact small-block Gauss sums, all 87 outer
bases and full 2,024-label coverage. It verifies the complement ranks and
unit scalar cancellation. It is a finite algebraic audit, not execution
of the enormous expanded Gaussian word; individually restored core validity
and the stated residual-to-child/all-size interfaces remain prerequisites.

Compensated birth-cut slot reuse composes by applying this formula to each
remaining PHYSICAL slot's initial frame. A donor starting at zero and ending
at full inner frame has sigma=0; its aliased recipient contributes no separate
slot or exterior. Literal inverse chronology and birth-cut frame containment
must first establish the individually restored physical-core interface.

The literal scalar word first subtracts the exact old response from each
nondeferred slot, injects the fresh sources and completes the center closure.
At the birth cut each deferred read subtracts its exact future response.
For a reused recipient this read uses the donor's actual current value,
including any fresh-source component. The recipient had no earlier use and
the donor has no later use under its old role; the compensating response
therefore cancels the entire substituted value. Side roots are then completed
and read. Every physical source injection and workspace shear is undone in
true reverse chronological order. This restores each live original scratch
coordinate individually for arbitrary correlated inputs. Treating cleanup
as an unqualified virtual `M^-1; -V` after aliasing would be incorrect.

The producer has 28,705 virtual roles and 2,108 disjoint birth-cut pairs.
Removing the recipients leaves 26,597 original physical slots. A donor's
initial frame is zero even when its aliased recipient had nonzero sigma;
the actual final forward frame is full dimension 24. For an unpaired deferred
slot the initial frame is its recorded sigma and the final frame is also
full. The reflected scan starts at zero and ends at sigma-perp on that same
physical role. Both orientations consequently have the active residual used
above, and their complete paid rank histograms agree.

The independent reflection audit expands every exact old-readout numerator
n/42 into signed unit chunks plus a remainder of absolute value at most one.
It checks the integer coefficient sum, reverses chunk order and signs under
reflection, and rejects oversize chunks, wrong sums, wrong signs, changed
complements and incorrect signed root readouts. Birth-cut controls reject
nondead donors, unavailable births, overlapping pairs and omitted compensation.
The new sharing checker requires the complete local exterior inventory:
for each physical source frame sigma there are exactly 2v children of rank
552+dim(sigma). Replacing these by an ungauged rank-552 inventory, omitting a
physical slot or dropping a paid group correction cannot satisfy its profile
binding. The Gauss checker also detects the wrong reflected residual sign.

Sharing retains all core gates and their actual scalar costs. In particular,
the bounded direct old-readout compiler has a larger G than PR128's transparent
PR117 word; its own audited scalar count and semantic guard must be retained. The core
scalar bound uses the 28,705 virtual roles, since aliased recipient readouts
still occur; the new group-wrapper reserve uses the 26,597 physical roles.
For every group-role and both orientations, 64*m^2 paid adapter atoms cover
binary basis maps and inverse maps plus quadratic unit-phase wrappers. These
are paid bit-interface calls with width-dependent costs, not constant-time
tape instructions. Sequential calls reuse restored row stock.
Completed blocks remain Gaussian dyadic, so their local odd 21 denominators
cancel at each core boundary even when incoming dirty values are correlated.

Provenance: completed-core sharing and signed outer partition are PR128
(an664), whose partition implementation cites Xiande Zhang and Gennian Ge.
The one-child arbitrary nondegenerate Gauss normal form is retained PR104
lineage; the underlying carrier DAG is eumemic's PR117. Physical-frame descent,
deferral saturation and this exact composition check were developed with
OpenAI Codex assistance. This note does not assert priority over concurrent work.

Package binding: `complex_deferred.py` emits the canonical `physical_auxiliary_source_frames` inventory of live slots only. `reflection_audit.py` independently rebuilds it from the literal starting physical ports and binds it to the full forward/reflected scan. `gauge_phase.py` verifies exactly those frames and their multiplicities, then `sharing.py` removes all local auxiliary exteriors and inserts the resulting signed group complements. `complex-profile.json` remains the complete unshared profile; `shared-complex-profile.json` is the combined profile. The root certificate and verifier must consume the latter and retain the actual local scalar and paid group-wrapper charges.
