# Sharp historical repair bytes, with a production key proof

Source: Ali Romman's PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd`; the exact resolved
`compact_columns.py` and `spool.py` bytes are in `../SOURCE-BINDINGS.json`.
This is an independent refinement of Section 5 of `../PROOF.md`, prepared
for Jerry Chen / @CubeJerry with substantial OpenAI assistance. It changes
no source code, selected certificate, global storage allowance or kappa.

## Claim and domain

Use the original notation: `r=L-z`, `M=2^r`, one grouped payload has
`a=2*component_bytes*2^z` bytes, `t=max(1,ceil(r/8))` is the literal tag
width, and `V=Ma` is the actual field length. The callbacks are fixed pure
functions, and `0<=z<=L`. Charge the original field, the replacement field,
and the historical maxima of all four fixed repair scratch roles.

For one invocation with an injective correction key from the `M` grouped addresses to those
same addresses, preserving the grouped suffix, the charge is

\[
 H\le 4V+2Mt.                                                    \tag{1}
\]

This hypothesis holds for the actual `Columns.row` key before any final
label validation, as shown below. It also follows retrospectively for an
arbitrary generic repair call that returns successfully: its final checks
force the dirty labels to be exactly the distinct bad output labels.
That successful-call implication makes **no** allocation-safety claim for
arbitrary malformed generic keys while they are running or after rejection.

The existing production-header proof supplies `t<=a`, so the actual
production row repair satisfies

\[
 H\le 6V.                                                       \tag{2}
\]

This improves the provisional eight-volume envelope. Original/widened
entrance fields, other owners, suspended arenas and unrelated scratch
remain separately charged. This is not a complete stage-space theorem.

## Historical role maxima

Let `E` be the number of bad groups. The initial dirty role has exactly
`E(a+t)` bytes and the clean role has `(M-E)a` bytes. Every radix pass
partitions the same multiset of dirty labels by one bit, then merges it.
It neither creates nor destroys a label. With distinct labels in `[0,M)`,
at most `M/2` have either value of a fixed bit when `r>=1`. Thus each of the
zero/one bucket roles has historical maximum at most

\[
 \min(E,M/2)(a+t).
\]

This bounds each role across every pass, even when its two maxima occur at
different passes. Stale trailing bytes in an overwritten bucket are below
the same previous historical maximum. The exact returned write count, not
the physical old length, controls the merge read; `spool.scratch` later
clears the complete historical physical file length before truncation.

Consequently, for `r>=1`, the four scratch roles sum to at most

\[
 (M-E)a+[E+2\min(E,M/2)](a+t)
 \le 2Ma+2Mt.
\]

For example, the second inequality follows from
`2 min(E,M/2)<=M` and `E<=M`: the coefficient of `a` is at most `2M`
and that of `t` is at most `2M`. Adding the two actual field slots proves
(1). This addition deliberately counts both historical field maxima,
although the old field is retired when replacement completes.

For `r=0`, `M=1`, there are no radix passes and both bucket roles have zero
extent. The exact charge is `3V+Et`, with `E` either zero or one. It is at
most `4V+2Mt`; under `t<=a` it is at most `4V`, so (2) also covers this
boundary. No division by `M/2` and no nonexistent bucket pass is used.

## Role-wise historical maxima across differing calls

The six-volume consequence of (1) under only `t<=a` is a **single-call**
bound. It must not be applied after taking independent role maxima across
calls with differing bad sets. For a sequence of arbitrary calls with
`V<=V*` and only `t<=a`, the uniform safe bound is `7V*`: dirty is at most
`2V*`, each bucket at most `V*`, clean at most `V*`, and the two field
positions contribute at most `2V*`. The actual all-bad/all-good pair at
`r=9,z=0,component_bytes=1` has `a=t=2` and attains `7V*`, although each
individual call is at most `6V*`. This is a generic boundary control.

The production header is stronger than `t<=a`. It supplies `b>=5`,
`L<=2b` and record size `c>=2b`. Therefore

`t=max(1,ceil((L-z)/8)) <= b <= c/2 <= a/2`.

For the actual production path, the individual uniform role caps are thus
dirty `3V*/2`, each radix bucket `3V*/4`, clean `V*`, and the two field
positions `V*` each. Their sum is **`6V*` across arbitrary varying calls**,
provided the incoming volumes are bounded by `V*`. This is the appropriate
role-wise historical production envelope. Equation (1) also gives the
smaller `5V` bound for each individual production call; no inference from
that smaller scalar total to independent historical maxima is made.

At `r=0` there are no buckets, so these role caps remain conservative.
The generic all-bad/all-good pair at `r=4,z=0,component_bytes=1` has
`t=a/2` and exactly `6V*` across the pair, corroborating the role-wise
calculation. Neither test pair is presented as a production-header
execution; they isolate the stated local tag-ratio hypotheses.

## Why the installed correction key is injective before validation

The multi-column `Columns.row` path first validates complete, pairwise
disjoint touched bit blocks. They lie inside the ambient `L` bits and
above the grouped suffix. The source's `repair_key` then does the following:

1. It traverses the recorded operations in reverse. A `swap` exchanges two
   disjoint equally wide bit blocks, an involution. A rotation step replaces
   a target block `u` by `(u-c(prefix)) mod 2^width`. The source explicitly
   clears every bit at or below that block when forming `prefix`; the
   amount therefore does not depend on the old target value. For each fixed
   outside assignment this is a cyclic permutation of the target block.
2. The final XOR flips distinct `y` bits. With source controls, every control
   is an `x` bit in the separately validated disjoint source block, so those
   controls are unchanged by the flips. Without source controls the flips
   are constants. In either case the final map is an involution.

Every step stays within the validated ambient field and preserves the low
`z` suffix bits. Their composition is therefore a permutation of the `L`-bit
field preserving each suffix. Restriction to addresses with zero suffix
is a permutation of the `M` group indices. In particular, the labels of the
bad input subset are distinct and in range before the source executes any
radix pass. The actual `good` predicate and coefficient closures are pure
functions of their integer argument.

This argument establishes the storage premise; it does not re-prove the
separate numerical assertion that the bad set maps onto exactly the bad
output holes. That assertion belongs to the retained native operator
correctness. The byte cap already holds even if that later hole-coverage
check were to fail for an otherwise validated row key.

For the generic successful-call implication, the source's final loop reads
exactly `E` dirty records and compares their labels with each bad output
index. Since each radix pass preserves the multiset and the pure `good`
predicate defines the same bad set at both traversals, successful return
forces the initial labels to be those distinct indices. Generic rejected
calls have no such retrospective premise.

## Exact family and the corrected counterexample boundary

Take `good` constantly false and the correction key to be the identity.
For `r>=1`, all `M` labels occur and exactly half enter each bucket at every
bit. All four scratch maxima are therefore exactly

\[
 (M(a+t),\; M(a+t)/2,\; M(a+t)/2,\;0),
\]

and the total including both fields is exactly `4V+2Mt`. The payload is
unchanged by the complete repair. This proves that (1) is sharp for the
stated generic class.

The prior executed example `L=17,z=0,component_bytes=1` has `a=2,t=3` and
total `7V`. It disproves `t<=a` and the dirty-role cap `2V`, **not** the
complete eight-volume cap. With `L=33,z=0,component_bytes=1`, the same
family has `a=2,t=5` and exact total `9V`, disproving an unqualified generic
eight-volume claim. The latter is a symbolic source-family calculation;
no 33-bit field was allocated or executed. Neither example satisfies the
production-header premise, so neither is a counterexample to (2).

## Evidence and limitations

`check_review.py` imports no author checker or byte meter. Its transparent
actual-file observer applies no predicted capacity during the call; a
separate label-set count computes exact historical endpoints afterward.
It executes 59 valid repairs covering `r=0`, empty/all/mixed bad sets, grouped
suffixes, multiple component widths, and the 17-bit boundary. It also checks
5,216 exact rational/integer bound cases. A duplicate-zero generic key is
rejected by the real final hole check and exceeds the distinct-label bucket
cap before rejection, demonstrating why the theorem's domain matters.
An additional 18 complete small address-map enumerations capture the actual
`Columns.row` correction callback, with payload methods deliberately stubbed;
they cover constant controls and both source/target orderings. These check
callback injectivity and suffix preservation, not numerical row execution.

The universal proof above rests on permutations and the literal source
loops, not extrapolation from those cases. The checker authenticates all
26 retained module digests and records the unexecuted status of the
33-bit family explicitly. It does not establish movement time, control
storage, the remaining ordinary/outer site census or an unconditional
multiplication theorem.
