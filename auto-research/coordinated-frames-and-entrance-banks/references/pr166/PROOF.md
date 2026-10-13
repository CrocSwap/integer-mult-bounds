# Dirty-target accumulation removes terminal producer rows

Status: author-checked finite compiler lemma and 67-row substitution on the
current PR163 complex word. This is not a new assembled multiplication bound.
Independent review and any advertised supplier/assembly update remain separate.

Scientific inputs are the selected complex files introduced at
15c702a929b7d640107a95e196186ad74e876c82. They are unchanged at publication
base e1813796ef5c3ca38c5dd7b9e8d81b3908ff5997; that later commit changes only
attribution NOTICE and its SOURCE digest. The checker verifies the existing
result.json SHA256 pins for every finite input it consumes.

## Relation to earlier constructions

Dumas and Grenet's *In-place accumulation of fast multiplication formulae*
(https://arxiv.org/pdf/2307.12712) motivates using arbitrary-valued output
storage. Its RAM results do not establish this frame-constrained compiler.
No novelty claim is made for the scalar pre/post cancellation identity.

PR161's P±Q merge and PR163's singleton-channel fusion create internal producer
sums. This substitution instead removes independent auxiliary coordinates by
using existing independently valued data targets. The paired-cube identity,
Clifford representatives, physical reuse, copied-center interfaces and all-size
compiler assumptions retain their upstream attribution and proof obligations.

## Local lemma with chronological hypotheses

Let z_s be an independently dirty, zero-entrance-gauge producer role. Assume:

1. It is neither a source-injection role nor an aliased recipient/donor.
2. Its only producer incidences are additive destination writes
   z_s <- z_s + b_j a_j, with b_j in {1,-1}. It never controls another
   producer role. It has exactly one root read, uniformly z_s/2 into a
   target group T.
3. Its literal write-frame chain is 0 <= U_1 <= ... <= U_k <= U,
   where U is the common root read frame. Every write uses the identical
   exact T_(U_j) on its control and destination.
4. All these writes occur after the copied-center phase. Before the first
   deferred target corrections, the targets in T are at frame0.
5. Some pivot c in T receives no target correction between that common-zero
   point and the last write/post-read. Other targets may receive corrections
   during this interval, provided those corrections do not depend on target
   contents and their existing frames are contained in U.
6. Later target reads continue their old nested chains from U. No other
   target-controlled producer operation is introduced.

All targets and retained dirty roles have arbitrary independent initial values.
No target is assumed clean, and the deleted dirty variable is not set to zero:
the new construction has one fewer independent auxiliary input coordinate.

Keep the ORIGINAL initial and deferred old-response coefficient columns for
EVERY retained role. Omit only the deleted role's column. In particular, do
not recompute the old correction from a decoder which simply drops its root;
that would omit the root response of its retained ancestors. The inherited
expanded scalar old-response implementation and its conservative charge remain
available. The sink's own old-response column is exactly the uniform1/2
column on T because it never controls another producer row.

At the common-zero point, after the copied-center contribution and before
its deferred corrections, perform

    y_t -= y_c                 for t in T minus {c}.

At the original time of each write, raise the pivot along the deleted role's
actual chain and replace that write by

    y_c += (b_j/2) a_j.

Immediately after the last such write, raise the pivot and the other targets
to the original U and perform

    y_t += y_c                 for t in T minus {c}.

Delete the old positive root read, all writes and inverse-cleanup writes on
z_s, its initial old-response column, its physical stream and its full-frame
ending. Every retained producer operation, original source operation, source
return, copied-center step and old-response column stays in its original order.

Write f=sum_j b_j a_j for the ACTUAL current controls, including all their
retained dirty dependence. The sandwich adds f/2 to all targets and preserves
every old target value. Any intervening correction e_t on a non-pivot is
unchanged:

    (y_t-y_c+e_t) + (y_c+f/2) = y_t+e_t+f/2.

An intervening correction to the pivot would be broadcast to every target;
this is why the pivot chronology condition is essential. The test does not
incorrectly require every non-pivot correction to wait.

The retained producer is the same invertible word with destination-only sink
writes omitted. It contains no reference to the deleted coordinate, so its
literal inverse restores every retained dirty input. Its response from each
retained source/dirty column is unchanged at the targets, and the retained
old-response columns cancel those dirty parts as before. Earlier target data,
center contributions and later target contributions are all preserved.

## Exact frames, inverse and simultaneous use

The pre-shears use T_0 on both targets. Each accumulating write uses the
original exact T_(U_j) on pivot and control. Every post-shear uses one
identical T_U on its two operands. Rank-zero reconciliation is actual inherited
scalar/movement work, not equality up to phase.

Reverse the COMPLETE literal new word and invert every shear. Use
D_U=T_U F^(-1) in the reverse/complement orientation. Then

    D_U D_V^(-1) = T_U T_V^(-1)

exactly. All reversed gate incidences are still identical, all transition
ranks are preserved, and sources/retained dirty values are restored. This is
the chronological inverse, not the invalid source/target-swapped transpose.
The data-bank and rank-zero endpoint conventions remain the inherited ones.

For sinks with disjoint target groups, perform each pre-sandwich at the same
common-zero cut and each post-sandwich at its own last-write time. There is
no target collision or producer feedback, so all substitutions coexist.

## Paid ledger

Let r=dim(U) and let P be the complete positive-width prefix of the deleted
role from0 through every write to U. Its old local row bill is P+[h-r].
The pivot's old first target child [r] is replaced by P. Other target paths
and all retained row paths are unchanged. Hence the EXACT local child change is

    -[r] -[h-r],

with one independent row removed. This accounts for every prefix, endpoint and
full-frame cleanup; fragmentation inside P cancels rather than disappearing
without payment. The same delta holds for the complete inverse orientation.

In the existing three completed orthogonal cores, for each zero-gauge sink:

    delta W = -1;
    delta children = -3*[r] -3*[h-r];
    delta rank = -3h;
    delta deficit = 0.

There is no exterior tail for a zero-gauge physical row. The full group factor
and retained routing/row reserves are not reduced by fiat. For moment exponent
p in (0,1), the unnormalized slack improvement is

    3 r^p + 3(h-r)^p - (3h)^p > 0,

because the six positive pieces sum to3h. This is a strict finite-profile
improvement, not a newly certified assembled kappa.

For k writes and n targets, the old affected scalar gates are k forward
writes, k inverse writes, n initial dirty reads and n positive root reads.
The new ones are k accumulating writes and2(n-1) target shears. Thus the
scalar-gate count decreases by k+2. All new coefficients already belong to
the Gaussian-dyadic alphabet; no odd divisor is introduced. Keep the original
conservative virtual R, M, expanded-correction scalar charge, full finite
stock and precision/routing reserves rather than shrinking them without proof.

## Exact current finite instance

The checker examines ONLY the165 all-eight disjoint roots of the selected
PR163 word. It finds67 eligible roots on disjoint target cubes. The other98
have retained producer consumers; two of those also touch the center phase.
It does not search arbitrary face, singleton or cross-cube combinations.

For example, root0 uses unaliased role12354. Its only incidences are additive
writes21902 and24308, at ranks15 and18. Target0 can be the pivot. Targets6
and7 receive early compensation, but their independent additive corrections
are valid while encoded. The pivot's first compensation occurs after the
post-read. This concrete distinction is verified in the actual target-event
replay rather than inferred from a scalar channel formula.

The selected simultaneous change is:

    physical R: 13041 -> 12974
    W per vertex: 15681 -> 15614
    rank per vertex: 1033626 -> 1029204
    deficit: 1320 -> 1320
    child multiplicity18: -201
    child multiplicity4: -201
    scalar gates: -300

selected.json contains every selected role, its original writes, pivot and
chronological boundary, as well as the complete new local/target/shared
histograms and source pins. Its decimal runtime is a diagnostic, not a
mathematical certificate input.

## What the author check actually establishes

check_sink_accumulator.py performs these exact checks from existing frozen
inputs, without importing an upstream executable or rebuilding a producer:

- original source pins and full positive physical histogram equality;
- all role classifications, aliases, source injections, literal consumers,
  write-frame chains and original root destinations;
- an available late-corrected pivot for every selected group;
- every new target event interleaved with all original deadline reads and
  retained root reads, including all endpoint changes;
- exact adjoint pullbacks through the actual aliased producer for every
  selected sink, covering all1320 original source columns and all13041
  original dirty columns, including zero columns;
- each fresh disjoint channel has exactly its448 required source terms;
- arbitrary target and intervening non-pivot corrections, both signs, and
  actual reversal of each scalar sandwich;
- retained source/dirty identity by destination-only deletion and literal
  inverse cancellation; no Monte Carlo or injective-digit assumption;
- disjoint simultaneous support and complete child/row deltas.

Together with the unchanged inherited complete word, this covers its15681
original source/target/dirty coordinates and the15614-coordinate new word.
The original saved full proof contracts remain dependencies. The package does
not update the bit supplier, balance parameters, all47 assembly inequalities,
precision constants or advertised multiplication exponent.

## Reproduce

From the repository root:

    python research/paired-cube-target-accumulator/check_sink_accumulator.py \
      --candidate research/paired-cube-balanced-161/selected/complex \
      --output /tmp/target-accumulator-check.json

The standard-library checker has60-second CPU/wall and768MiB address-space
caps. The author run completed in approximately5.5seconds and85MiB. Compare
mathematical fields, not runtime/RSS, with selected.json.
