# Forty-PR batch: circuit constructions and scoped bounds

This second checkpoint completes sixteen further scoped reviews and local
executions. Together with the [first nine](community-batch970-review.md),
25 of the frozen 40 have completed substantive review. Publication state is
tracked individually in the [ledger](pr-ledger.md). The selected conditional
**κ remains 0.001661960547713947**; none of these packages is a new admitted supplier.

## Individual contributions

| PR | Contributor | Accepted scope |
|---|---|---|
| [#965](https://github.com/CrocSwap/integer-mult-bounds/pull/965) | [Ross Richardson](https://github.com/RossRichardson) | Coupled helper triples reduce the alternative R439 word from 11980 to 11840 ADDs; exhaustive 168-map component scores, greedy census, arbitrary-dirty endpoints and full native replay. Nine-stage precision uses 99.6193% of allowance. Not a new supplier or global optimum. |
| [#967](https://github.com/CrocSwap/integer-mult-bounds/pull/967) | [Sricharan Vagvala](https://github.com/theon199) | Disjoint one/two-leaf helper stars reduce the alternative word to 11783 ADDs; full native 5/9/11-stage replay and exact 192-bit inequality pass at 99.996316% usage. Semantic D substitution; original gate-local H2 remains false. No kappa change. |
| [#937](https://github.com/CrocSwap/integer-mult-bounds/pull/937) | [Ross Richardson](https://github.com/RossRichardson) | Historical rank-h central factor with two commuting basis shears reduces h26 gather/scatter bill to 42600. Complete dirty restoration and unchanged grouped-frame/rank invoice checked; improvement over Curtis Dransfield #809 credited separately. |
| [#945](https://github.com/CrocSwap/integer-mult-bounds/pull/945) | [Ross Richardson](https://github.com/RossRichardson) | Joint same-target two-source Horner blocks save 13072 backward primitives with complete 737-column replay and fixed-class disjoint-pair optimum. Conservative max-orientation invoice improves only by 16; no new exponent. |
| [#917](https://github.com/CrocSwap/integer-mult-bounds/pull/917) | [Ross Richardson](https://github.com/RossRichardson) | Joint target forest and helper pairs reduce historical CK compensation by 75318 real primitives per orientation, including 8798 beyond the target forest. Arbitrary inputs, both orientations, native wrappers and precision charged; not joint optimality. |
| [#919](https://github.com/CrocSwap/integer-mult-bounds/pull/919) | [Ross Richardson](https://github.com/RossRichardson) | Boundary-local sign normalization saves 224 CK primitives per orientation. Signs flushed before every opaque/frame boundary; source-dependent norms preserved. Historical finite scalar scope. |
| [#839](https://github.com/CrocSwap/integer-mult-bounds/pull/839) | [faw](https://github.com/faw01) | Known-zero coefficient work removes 9228 historical JP8 primitives per orientation beyond #696, forgetting knowledge at every opaque/frame boundary and preserving addition exit obligations. |
| [#969](https://github.com/CrocSwap/integer-mult-bounds/pull/969) | [ToikY](https://github.com/ToikY) | Deferred exact swaps with paid cycle materialization save 560 primitives per historical CK/JP8 orientation after identical clear elision on both comparators. Complete dirty/private inputs and prefixes checked; physical/global adoption open. |
| [#947](https://github.com/CrocSwap/integer-mult-bounds/pull/947) | [Ross Richardson](https://github.com/RossRichardson) | Exact constant-row integral-shear optimum in the stated signed alphabet: #937 attains unique fixed-pivot 42600 at h26 and all even h>=10; h8 has a different optimum. Other row mixing and rational bases excluded. |
| [#949](https://github.com/CrocSwap/integer-mult-bounds/pull/949) | [Ross Richardson](https://github.com/RossRichardson) | Exact 73-primitive optimum over diagonal signed-dyadic scale placements for the fixed 26-ADD factory. Complete 315392-tuple domain and higher-macro exclusion under the retained adapter invoice. CubeJerry #922/#924 supplied the attaining construction. |
| [#961](https://github.com/CrocSwap/integer-mult-bounds/pull/961) | [woklerx](https://github.com/woklerx) | Historical X4 single-parent forest floor 10883 extends from signed units to all dyadics via finite coefficient domination plus proved infinite tails. Multiple parents, helper changes and shared work excluded. |
| [#964](https://github.com/CrocSwap/integer-mult-bounds/pull/964) | [Gareth Davidson](https://github.com/bitplane) | Historical CK signed-power-of-two parent forests retain floor 16364; each nonunit edge adds at least 10. Exact finite census plus infinite-tail proof; does not cover all dyadic numerators. |
| [#954](https://github.com/CrocSwap/integer-mult-bounds/pull/954) | [Ross Richardson](https://github.com/RossRichardson) | Classifies all 255 first E8 reader-code rank drops at 56 deletions, correctly separating available and required code dimensions. Exact star costs 50/57; through-56 fixed-star ratio exclusion inherits PR939 coverage. |
| [#958](https://github.com/CrocSwap/integer-mult-bounds/pull/958) | [Ross Richardson](https://github.com/RossRichardson) | Natural five-port quadratic Gram decoder has supplier saving below 125/76433 under separate-star drop-free compressed-window premises. Seventeen exact rational-rank witnesses and all-p tail; no unrestricted decoder barrier. |
| [#963](https://github.com/CrocSwap/integer-mult-bounds/pull/963) | [ToikY](https://github.com/ToikY) | Complete 19683 receiver assignments in the frozen P111 generator cannot beat 439 helpers; 2646 minimizers. Fixed punctures, keeper plan and closure convention; not unrestricted helper/circuit optimality. |
| [#968](https://github.com/CrocSwap/integer-mult-bounds/pull/968) | [themilkman216](https://github.com/themilkman216) | Exact eight-term complex frame-pair decoder analysis and finite census: copy floor max(72-p,56) through 24 punctures; best copy ratio 7/13 at p16. Uses stated E8 hyperplane-flat coverage premise. Favorable pricing only, no built supplier or new kappa. |

## Review findings and limits

The helper constructions use `(E,H)` conjugation of the same compensation map:
prepare helpers and targets, inject `E K H^-1`, then undo both preparations.
This establishes the correct boundary on arbitrary dirty targets and helpers.
#965 allows general three-coordinate words, so reverse order matters; #967 uses
stars with square-zero off-diagonal part. Both explicitly pay preparation and
restoration. Full all-column and native 5/9/11-stage replays pass. Their original
syntactic H2/K predicates remain false, as expected under the semantic-D interface.
They are alternative candidates; adding their savings would be incorrect.

#967's complete positive envelope satisfies
`2^18 F^5 B^4 < 2^192` with F=72847 and B=10394084, at 99.996316% of the cap.
We accept that exact inequality, without inferring spare precision for later
changes. Hosted supplier emission, full invoices and assembly admission remain open.

For #917 the helper residual is recomputed *after* the target transform. The
inverse-transposed logical gates retain chronological order; private CLEARs are
lowered afterward and are not claimed invertible. #945 preserves all private input
columns and charges coefficient work; its large one-direction saving becomes only
16 in the max-orientation invoice. #839 forgets zero-state knowledge at every opaque
boundary. #919 flushes register signs at each such boundary. #969 pays the complete
cycle materialization and final private-work clear, and compares against the same
clear-elided baseline. All these checks include arbitrary dirty inputs and restoration.

The negative results have specific search classes. #961 first replaces nonunit
edges by same-parent unit edges or roots, preserving forest topology, before using
an undirected minimum-spanning-tree certificate. It does not incorrectly treat
general dyadic edges as symmetric. #964 proves a narrower power-of-two CK statement.
#949's extra-macro exclusion relies on the retained conservative adapter invoice,
not an intrinsic cost lower bound. #947 proves polynomial coefficient inequalities
for the infinite h tail, separately from its finite enumeration.

#954 prices both possible spans containing the seven-dimensional target code at
the first rank drop; it does not force every reader into that target code. #958 uses
nonzero integer minors modulo primes only as rational-rank lower bounds, including
the exceptional p=11/12 values, then embeds the p=13 witness for the infinite tail.
#963 separates local generator choices only under the stated frozen allocation and
elimination policy. None is a barrier for arbitrary multiplication algorithms.

#968's exact eight-term normal form reduces to dual bases. Its finite checker
covers the 511 binary functionals, the eight root-hyperplane types, the D7 orbit,
all 1260 disjoint frames and the attaining puncture chain. The written universal
argument uses the stated E8 hyperplane-flat classification. That standard coverage
step can be read as the Weyl-chamber/parabolic reduction: a root-spanned hyperplane
normal can be moved to the closed chamber, where its orthogonal roots form a
rank-seven standard parabolic subsystem. The finite census alone is not a proof
of that coverage. Asymmetric centers are not implemented here; the pricing is an
optimistic budget and must not be announced as a new multiplication witness.

## Evidence, integration and credit

All sixteen submitted packages are retained byte-for-byte. Each primary verifier
and every supplied package test used in its documented acceptance route ran locally;
separate independent implementations ran where provided. Both helper candidates'
complete native outputs are archived in the batch audit. Execution logs are pinned
per PR. The preceding original/candidate supplier records remain unchanged.

The original notices retain the construction lineage: eumemic, DreamingOfClouds,
Jeremy Kothe, Chafik Boukhalfa, icekylinx, Rohan Arun and Sagar Thakrar; Curtis
Dransfield's center shear; dd-hemant's CK forest; CubeJerry's factory; Chi Zhao's
E8 geometry and the related star-decoder work. Parallel contributions are credited
individually. No new human-review, full-theorem formalization, asymptotic improvement,
measured runtime improvement or hosted Linux CI pass is inferred from local checks.
