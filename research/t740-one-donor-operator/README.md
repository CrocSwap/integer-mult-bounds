# One partially hosted donor does not permit rank redistribution

On the pinned T740 owner-0/port-0 word, an operator-preserving replacement at
children **8, 10, 12, 13 and 14** preserves each residual phase function and,
for independent replacement axes, each residual rank separately. Their
source-bound residual ranks are **48, 48, 48, 48 and 1**. Child 14 has 31
unchanged hosted axes and one residual axis; its full basis has rank 32.

This closes the one-donor case proposed in
[PR3263](https://github.com/CrocSwap/integer-mult-bounds/pull/3263).
PR3199/PR3204 cover the four fully idle sites; the new calculation includes
the partially hosted child 14 in the complete eight-stream word. It is a
scoped operator theorem, not a universal prohibition on idle-axis exchanges.
The selected frontier is unchanged.

## Exact matrix certificate

Keep the compiled data schedule, hosted prefixes, translations and all
unchanged child phases fixed. For each changed child j and character
`x in F2^73`, write `z_j(x)` for its replacement residual phase divided by
the original residual phase. All five are fourth roots of unity for the
inherited independent-axis completed-call contract.

After dividing the output by the baseline scalar `i^popcount(x)`, exact
symbolic replay of the whole word gives

```text
[ z13,       0, z13-1,     0, 0, 0,  0,   0 ]
[   0,     z12,     0,     0, 0, 0,  0,   0 ]
[   0,       0,     1,     0, 0, 0,  0,   0 ]
[   0, z12-z14,     0,   z14, 0, 0,  0,   0 ]
[   0,       0,     0,     0, 1, 0,  0,   0 ]
[   0,   1-z14,     0, z14-1, 0, 1,  0,   0 ]
[   0,       0,     0,     0, 0, 0, z8,   0 ]
[   0,       0,     0,     0, 0, 0,  0, z10 ]
```

Every dependence on the 73 character bits cancels from this normalized
matrix. Its diagonal forces each `z_j=1` if the matrix is identity; that
condition also suffices. The exact matrix has 16 nonzero formal summands.

The cancellation is symbolic. For a binary vector v, parity has the exact
Boolean-polynomial representation

```text
<v,x> mod 2 = sum_i v_i*x_i - 2 sum_(i<k) v_i*v_k*x_i*x_k   (mod 4).
```

The checker carries these quadratic exponents modulo four through every
hosted phase, local event, bridge and terminal operation, with separate
formal variables for the five inserted phases. It then removes the common
baseline phase. Equality in this formal calculation implies equality for
every character; no finite collection of sampled characters substitutes
for that argument. [PROOF.md](PROOF.md) gives the source binding and proof.

If a child has r independent binary axes, its parity map on a uniformly
chosen character is uniform on `F2^r`. The average of its residual phase is
`((1+i)/2)^r`, whose magnitude is `2^(-r/2)`. Identical phase functions
therefore have identical r. This proves the rank consequence without
enumerating candidate bases. Rank-preserving replacements are not excluded.

## Source boundary and independent checking

The physical operator inputs are the unchanged canonical
`idle-star-paired-axis-census` source, the retained PR3148 fill and exchange
journal, provider widths, complete order/dispatch, plan/template and port
recipes. [SOURCES.json](SOURCES.json) records the full closure and retained
notices. The first implementation uses authenticated predecessor helpers to
verify the full lifted fill digest and obtain the context; its symbolic
matrix arithmetic is new.

The independent implementation imports neither the primary verifier nor a
predecessor executable. It reconstructs the owner-0/port-0 context directly
from authenticated JSON and performs its own exact symbolic replay. Both
implementations must obtain the displayed matrix and the same source ranks.

This theorem holds under the inherited completed-call phase model and
unchanged hosted-prefix chronology. It does not re-prove physical/native
realization of those completed calls. It covers neither other owners/ports
nor changes at child 15 or earlier hosted sites. It does not by itself
classify PR3200/PR3251's full allocations, which can change additional sites;
PR3263's candidate-specific rejections retain their separate scope and credit.

## Reproduce and verification limits

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/t740-one-donor-operator
```

[RESULT.json](RESULT.json) retains the exact certificate; [VERIFY.json](VERIFY.json)
declares the primary, independent and behavioral checks. The 1,024 possible
five-phase specializations are useful finite controls, while the symbolic
source calculation proves the all-character statement. Source corruption
and semantic mutations must be rejected rather than silently changing the
certificate's premises.

The complete registered replay passes on CPython 3.12.15 / Linux x86_64.
Primary and independent implementations agree on the retained certificate.
Six isolated optimized control groups cover a quadratic phase error invisible
on every coordinate character, a different orthonormal basis with the same
phase, a nontrivial Gaussian specialization, removal of the actual donor axis
`2^72` against numerical source replay, missing hosted/bridge operations and
changed source bytes. All requirements use the standard library.

No rank-only optimization, new moment headline, all-eight-site/all-port
theorem, native replay, selected cold replay, supplier admission, independent
human review or formal-kernel proof is claimed. No frozen input or selected
result is changed.

## Open next questions

Can coupled changes including child 15 or another hosted site preserve the
operator while redistributing rank? First reconstruct the exact enlarged
insertion-to-insertion word and retain all hosted phases. The present
five-variable identity cannot be transferred to a different set of sites
without that calculation.

Can a rank-preserving phase-equivalent replacement reduce a fully paid frame
or consumer cost? First exhibit the unchanged phase function and price both
the producer and consumer, including restoration and hosting. Phase/rank
admissibility alone does not demonstrate a supplier improvement.

## Attribution and coordination

The canonical investigation is
[Discussion2612 comment19003626](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19003626).
Base canonical main/fork is `463113d675af7410ac91d53a4fed51ec6494eb9a`,
priority revision 6. [TASK.json](TASK.json) retains the original independent
audit card, scoped handoff, exact heads and overlap evidence.

Gonzalo Mier's PR3263 (`91faeaa09667bf20fd2ba6307a173400e8ad876a`) supplies
the one-donor handoff and the two frozen counterexamples. His PR3199 and
Tekalign's PR3204 supply the prior four-idle-site scope. Rohan Arun's
PR3200/3251 supply the rank-only candidates; their numerical acceptance
does not establish operator equality.

Retain Nick Petalas/PR3187's physical-stream criterion, Jeremy Diviney/PR3148's
T740 fill and 145-row journal, dcharb78/PR3133's providers and notices, Gonzalo
Mier/PR1252, Guéorgui Maissouradze's star construction, Marius-Paul Dumitrean/
PR2979, Ali Romman/PR1043, Sagar Thakrar/PR2423 and the selected-supplier
source lineage. The predecessor notices remain unchanged.

Prepared by thakrarsagar with substantial OpenAI Codex assistance in
derivation, implementation, independent reconstruction, controls and review.
Separate AI executions are not independent human review. Apache-2.0.
