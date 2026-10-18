# Portable reconciliation of the archived R715 cancellations

**Research consolidation and independent finite verification; no new kappa.**
The historical 40-addition reduction is reproduced from retained, byte-identical
parent sources with a standalone standard-library checker. The new evidence
also accounts for **425 empty-source frame visits** removed by the historical
flattening step. All 955 register frame itineraries, the nine copied values,
the arbitrary-dirty binary maps and the local paid histogram are preserved.

The archive's discovery/native scripts name an old local workspace. Its
[integration review](../../docs/research/research-notes-20261011.md) explicitly
checked archive integrity and navigation, without independently rerunning the
historical mathematical claims. This companion closes the **portable local
replay and source-location gap for this one result**. It does not dispute the
original author's successful native receipt, and it is not a new discovery of
the cancellations.

## Reproduce

From the repository root, using Python 3.9 or later, offline:

```sh
python3 -I -O -B research/r715-cancellation-reconciliation/verify.py
```

Expected:

```text
PASS_R715_CANCELLATION_RECONCILIATION aliases=4 pairs=20 ADDs=15014->14974 columns=955 profile=unchanged
```

The command verifies source hashes, reconstructs the entire deterministic
[RESULT.json](RESULT.json), and compares every field. It neither imports the
historical engine nor writes into the source tree. To create another receipt,
add `--write /absolute/new-file.json`; an existing output file is rejected.
The package and the inputs named in `SOURCE-PINS.json`, together with the
archive manifest, suffice for a relocated replay without Git or network.

The independent dense rational-frame oracle and mutation controls run with:

```sh
python3 -I -O -B research/r715-cancellation-reconciliation/test_package.py
```

Expected: **15 tests pass**, including 16 deliberate rejection mutations and
a scalar-preserving change that alters the price. The source manifest check
permits unrelated new archive entries while rejecting changes to the four
parent aliases. A focused Linux workflow is supplied; its hosted result is
separate from local validation in [VALIDATION.md](VALIDATION.md).

## Sources and the recovered dependency

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. The selected conditional
result at that base is PR942's T37 construction, kappa
`1661960547713947/10^18`, with PR589 on PR555 on the bit side. This historical
R715 word is **not** the selected bit supplier.

The cancellation archive was last changed by
`196fac3d94198422939b021e93512020a543d339`. Its source field names the SHA256
`7721fa65c554b99e739b775e0015a46bb31d9afedd2172b0ad807e7cbf160757`.
Four files in the archived nested-donor trials, **16, 17, 18 and 19**, each
match that hash exactly. They are aliases of one parent, not four independent
experiments. Trial 16 is the canonical replay input. No inference from the old
workspace directory's name to a particular PR head is required.

The retained cancellation word has SHA256
`64e0796232c5ce0a06f7f9f685474dc9e4fb6e7e0368a8b24250d20bf0e280b7`.
[SOURCE-PINS.json](SOURCE-PINS.json) records exact Git blob IDs and SHA256 values
for the four aliases, result, changed word, original scripts and scope records,
and the historical frame-model source. The checker validates both kinds of
file identity without invoking Git. The global archive manifest and integration
notes have separately identified **context-at-base** pins; those are historical
references, not locks on later unrelated archive/documentation additions.

## Completed finite coverage

| Obligation | Coverage and result |
|---|---|
| Parent identity | Four exact aliases, bound to the archive manifest |
| Claimed deletions | All 20 pairs, 40 distinct original indices, all 688 crossed scalar occurrences |
| Unchanged data | Every non-phase word field; complete retained scalar subsequence |
| Frame algebra | All 963 frames, exact subspaces of Q^8; independent Fraction Gauss-Jordan oracle |
| Frame schedule | All 955 compressed register itineraries, including 425 parent empty-source records |
| Binary maps | All 955 abstract input columns, all four phase boundaries, both words, forward and literal inverse |
| Copies/restoration | Nine frozen retained values, all 120 target outputs, all 715 arbitrary-dirty helpers restored |
| Positive support | Every required source/helper support contained in its gate frame; after-support dominated at each phase boundary |
| Cost | Exact local rank histogram, 4,140 paid children, rank mass 7,353 |

The historical addition counts become:

| Phase | Parent | Retained word | Removed additions |
|---|---:|---:|---:|
| D | 8,690 | 8,690 | 0 |
| A | 2,915 | 2,895 | 20 |
| B | 494 | 494 | 0 |
| C | 2,915 | 2,895 | 20 |
| Total | 15,014 | 14,974 | 40 |

The common local paid histogram is
`{1:2386, 2:1034, 3:256, 4:279, 5:114, 6:61, 7:1, 8:9}`.
The nine rank-eight children are the retained copies. The remaining 4,131
charges come from strict frame climbs. Scalar additions and empty-source
records are distinct from those recursive charges.

## Why the checks establish the stated identity and price

For the abstract binary register model, write `T(d,s)` for `r_d ^= r_s`.
It is an involution when `d != s`. Two elementary updates `T(d,s)` and
`T(e,t)` commute if `e != s` and `t != d`. Each recorded pair has identical
ordered endpoints and the same frame; every gate strictly between its two
indices in the **original** scalar word satisfies these conditions. This is
stronger than testing only the final retained middle. Thus each pair cancels,
and the argument survives deletion of any of the other disjoint pairs.

The checker independently applies every addition to a 955-column binary
matrix represented by integer row masks. Initial helper and target columns
are independent input variables, not zeroed scratch. At the A/B boundary it
freezes the nine copied helper values before scattering them. It verifies
`x -> x`, `y_t -> y_t + x_t`, and `z -> z`, and runs the literal reverse
operation sequence. Linearity extends these exact basis checks to every state
in this finite binary model. This is not a claim about all multiplication
sizes, signed Clifford lifts or rounded physical arithmetic.

Flattening a multiple-source addition preserves its binary action, but an
empty-source record may still move a register to a new frame. Therefore the
geometric replay reads the **unflattened parent**. Frame spans are computed
with fraction-free integer elimination; a separate dense Fraction algorithm
checks all 963 results. Every move must be a proper rational-subspace inclusion.
For each register, consecutive equal subspaces are suppressed and the complete
remaining itinerary is compared between the two words. The same itineraries
give the same dimension differences, and hence the same paid climb multiset.
The identical copied helpers at the same boundary add identical copy charges.

The positive source-support replay uses union, not binary XOR, including the
scatter. Thus it does not falsely erase a clean source due to F2 cancellation.
This establishes source-span admission in the stated coordinate model; it
does **not** establish equal positive integer coefficients or an unchanged
physical precision envelope.

## Controls and the empty-record accounting boundary

Sixteen changes are rejected: missing/duplicate pairs, wrong framed witness,
a noncommuting middle gate, an incorrect paid count, a Boolean used as a count,
one unpaired addition, omitted helper restoration, omitted scatter use, an
empty-source frame descent, a Boolean frame index, three changed input files,
a changed manifest alias, and a changed expected receipt. Mathematical controls
call the replay directly, bypassing byte hashes, so they test the claimed
failure modes rather than only checksum failure. The suite runs under `-O`;
validation does not depend on removable Python assertions.

A separate valid perturbation inserts `[6,709,[]]` immediately before original
phase A record **4** (zero-based). It splits a rank-two climb `0 -> 2` into
`0 -> 1 -> 2`. The scalar maps, restoration, rank mass and legality still pass,
but the histogram changes to `H_1=2388, H_2=1033` and **4,141** children. This
is concrete evidence that binary-map equality alone does not establish the
archived unchanged-price claim. The 425 actually removed empty records pass
the stronger complete-itinerary check.

## Scope, stopped work and attribution

This is a finite witness audit, not a search. It exhausts exactly the 20
retained pairs and the two specified words. The original 39,889,440-comparison
search and later no-gain retiming neighborhoods were not repeated; their counts
remain historical reports. No new construction, optimum, impossibility result,
runtime speedup or kappa improvement is claimed.

The native receipt is retained context, not newly executed evidence. Native
signed/formal H/K columns, labels, mutation and Gram tests were not rerun here.
The global emitted physical program, whole supplier invoice, precision/tape,
all-size/common-label/mutable-source interface and analytic transfer are outside
this replay. Inherited proof obligations and the selected frontier are unchanged.

Credit for the cancellation discovery, archive and recorded native checks
belongs to **Rohan Arun**, whose substantial AI-assistance disclosure remains
in the original archive. Credit for the R715/frame machinery belongs to
**Chafik Boukhalfa**, with his disclosed Claude assistance, and the predecessor
bit-supplier contributors retained in the source notices. The source history
includes PR472, PR473/PR477 and the PR436/PR454 engine lineage; this companion
does not claim to resolve the whole scope or current head of any of those PRs.
Douglas Colkitt's integration review correctly limited its original coverage
to archive integrity. Related PR719 by Sagar Thakrar concerns a different,
rational CK cleanup obstruction and is not a dependency.

Concurrent [PR1024](https://github.com/CrocSwap/integer-mult-bounds/pull/1024)
by Hanson Sun (`bbMisk`), inspected at
`86a21357eb64d154f1b641c720c73627df68d71b`, reconciles the separate R714
candidate-201 hierarchy/retiming records and its 954-input map. This R715
contribution adds the 20-pair cancellation proof, four exact parent aliases,
955-input map and empty-frame accounting evidence. No PR1024 code or result is
imported or assumed.

Prepared for **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex** assistance, under the repository's **Apache-2.0** license. This is
independent software verification, not independent human peer review.
[CLAIM.md](CLAIM.md) records assignment, candidates, overlap and timing.
