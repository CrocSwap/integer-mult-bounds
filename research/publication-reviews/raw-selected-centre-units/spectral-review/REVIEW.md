# Independent review of the fixed-baseline spectral annex

The annex passes for the fixed A,T source interface that it states.
Every admissible selected set in this class has at least 27 ports.
Sizes 28, 29, 30, and 31 are also excluded. Size 27 is open and needs
det(-4D)=2^42. This is a necessary condition, not an existence result.
The review does not prove a global selected-set minimum or a native
cost bound. The complete kappa calculation does not change.

This is a fresh review by a separate OpenAI Codex agent. It does not
claim independent human review or a formal-kernel proof. The earlier
raw-selected package review remains unchanged.

The [annex](../../../raw-selected-centre-units/annex/fixed-baseline-spectral-gap/README.md)
states the class. S contains the two fixed disjoint eight-port minors.
The source unit must preserve the specified selected source rows and
give the ordinary identity output on U. The
[necessity lemma](../../../raw-selected-centre-units/annex/fixed-baseline-spectral-gap/frozen/work/centre-encoding-campaign-20261014/lanes/cover-algebra/SELECTED-BLOCK-NECESSITY.md)
then requires a unit D=I-R_U K_U. The ordered block argument is valid:
C=F E^-1 has identity selected rows, its U diagonal block is a unit,
and J_UU C_UU=I. The ordered unit identities give the condition on D.
The lemma does not apply when the selected source baselines may change.

For this fixed A,T and actual R, D=-11I+M/4 and B=-4D=44I-M.
The determinant lemma supplies the uncancelled factor of 11 for fewer
than eight additional columns. This excludes all selected sizes below
24 in the stated class. The
[spectral proof](../../../raw-selected-centre-units/annex/fixed-baseline-spectral-gap/frozen/work/centre-encoding-campaign-20261014/lanes/schur-selection/SPECTRAL-BOUND.md)
excludes sizes 24 through 26 and 28 through 31 by strict determinant
intervals between adjacent powers of two.

The graph proof covers every clique case. A clique of at least four
roots can be changed by signs to Gram matrix 2I+2J. Its rank bounds
the clique size by eight. The weighted graph inequality is valid.
For fifteen roots, the clique cases up to six, seven, and eight give
at most 93 edges. The seven-clique residual cases are complete. In
particular, h=2 and z=2 require the t+2 term in max(7,t+2). Averaging
over fifteen-root subsets gives the stated larger-set edge bound.

The three eigenvalue caps follow from row sums, the weighted graph
bound, and the second moment. Each cap is below 44 in the checked
range. The extreme-spectrum determinant bound follows from concavity.
The second-moment logarithm bound uses a positive series with an
increasing quotient. All interval endpoints have the correct direction.
The exact rational tail bounds justify the strict comparisons.

The [source and adapter check](SOURCE-ADAPTER-CLOSURE.json) verifies all
21 source records. Every copied original path has the same bytes. A
fresh read of the full local historical archive reproduces its pinned
hash and both compressed members. The member payload hashes also match.
The earlier exact Git readback is retained as provenance. This review
did not repeat a Git or network source fetch.

The portable adapter changes only file input and removes unused input
imports. Its patch was regenerated exactly. All seven other function
ASTs and the full reconstruction and mathematics suffix are unchanged.
The original 256 main files and their manifest remain unchanged. The
new annex manifest covers all 41 other annex files. All 20 links in
the new README, notice, and validation note resolve locally. This
review uses the public research/publication-reviews layout for its
relative package links. The
[notice](../../../raw-selected-centre-units/annex/fixed-baseline-spectral-gap/NOTICE.md)
retains the source lanes, contributor evidence, license, and AI credit.

The [cold replay](COLD-REPLAY.json) ran from a copy outside the workspace:

```sh
python3 -I -O -B /private/tmp/fixed-baseline-spectral-review-20261022/annex/replay.py --optimized --out /private/tmp/fixed-baseline-spectral-review-20261022/output
```

It printed `PASS_FIXED_BASELINE_SPECTRAL_GAP`. The wrapper ran the
producer with assertions enabled and the separate checker with -O.
Both complete receipts match the historical bytes exactly:
[producer](REPLAY-PRODUCER.json) and [independent](REPLAY-INDEPENDENT.json).
The portable run reads only the two pinned members, not Git or the
full archive. It propagates eight forms backward through the 12,550
event prefix and checks all 112 columns, all 6,216 root pairs, the
residual cases, 2,248 degree inequalities, and all 16 size intervals.
A same-size change to the interface file is rejected by its hash
before the wrapper creates an output directory.

The separate [arithmetic audit](INDEPENDENT-AUDIT.json) imports no source
checker. It checks all root pairs and repeats all 16 exponent profiles
with 96-term rational logarithm intervals. The exact size-31 margin is
greater than 1/1250. Three controls check critical proof assumptions:
the constant-seven degree bound fails a permitted residual case; the
weaker 98-edge bound cannot certify the size-31 logarithmic gap; and
downward square-root rounding is invalid there. The audit also confirms
that size 27 still permits exponent 42.

The main S38 witness is in a different class. Its selected set omits
four ports of this fixed A and all eight ports of this fixed T. Its raw
unit tests also differ from this selected-baseline contract. This annex
does not prove that S38 is optimal. It does not adopt the separate
lower-twelve producer claim or later separator claims. The fixed-pair
40-port result has additional restrictions, and its large enumeration
was not repeated.

No native word, phase or ownership schedule, routed caller, recursive
invoice, current selected supplier, or complete kappa calculation ran
for this annex. The factor-11 and necessity arguments are proof steps;
the finite replay does not enumerate all selected sets. The source
normalization note is retained for its ordered identities; its scalar
invoice is not newly validated. Final GitHub objects, links, rendering,
and published-body readback remain with the coordinating publisher.
