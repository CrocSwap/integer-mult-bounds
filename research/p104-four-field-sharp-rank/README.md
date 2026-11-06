# Sharp n=4 four-stage rank: ceil(21q/2)

Under the actual-prefix/full-query commuting-projector hypotheses of
[CubeJerry #6773](https://github.com/CrocSwap/integer-mult-bounds/pull/6773),
the minimum total stage rank for a four-field shortest root is
**ceil(21q/2)**. This resolves its quantitative n=4 gap: a uniform 11q floor
is false, and the independently constructed q=2 rank 21 word is optimal.

The new analytic argument bounds the combined AB,BC,CD joint sectors by 5q/2.
It permits arbitrary coupled matrices and uses no search-completeness premise.
At exact 21q/2 equality, q is even and the complete incidence inventory is:

| Output stage product | Coordinates |
|---|---:|
| ABCD | q |
| AB | q |
| CD | q |
| BC | q/2 |
| ABC | h |
| BCD | j |

Here h+j=q/2, and the stage ranks are(2q+h,3q,3q,2q+j). Each output also
receives the central involution S. Direct sums of the q=2 word and its
reflection realize every integer h,j split. A scalar rank 11 word supplies
the odd-q rounding case. No odd-q inventory classification is claimed.

[SHARP-BOUND.md](SHARP-BOUND.md) gives the proof, all-q construction argument,
source attribution, and limitations. It also proves the stronger n=4 odd-pair
bound rank(B)+rank(C)>=6q. Combining the retained even-interior 4q and
three-stage 7q bounds with the new extreme-site result gives the minimum over
all four-of-five stage placements at n=4. At the minimum it also excludes
rank-one retirement within a fixed joint sector when the coordinate is idle
on both sides of its query and has matching actual-prefix eigenvalues. This
corollary does not exclude arbitrary native splits or paid modifications.

## Exact reproduction

Python 3.12, standard library only. Registered command from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-four-field-sharp-rank
# Standalone source-export replay:
python3.12 -I -B research/p104-four-field-sharp-rank/check.py
python3.12 -I -O -B research/p104-four-field-sharp-rank/check.py
python3.12 -I -B research/p104-four-field-sharp-rank/check_rank21.py
python3.12 -I -B research/p104-four-field-sharp-rank/check_reduction.py
```

The B checker imports no predecessor executable. It authenticates the frozen
#6773 note and provenance manifest, reads the pinned q=2 fixture, and rebuilds
the scalar fixture. It checks five fixtures at q=1,q=2,q=2 reflected,q=3,q=4:
query ranks and all 125 ordered Gram blocks, square-zero queries, the full−I endpoint,
actual chronological prefixes, stage compatibility and commutation, integral
invertibility of the input bases, all 160 complete formal coefficient matrices,
and the ordered projection reduction used in the proof. Fourteen controls
include all five query omissions and all four stage omissions; a query-supporting
idempotent that fails actual-prefix commutation; a rank 19 tuple satisfying
query support and actual prefixes but failing pairwise stage commutation; and
two reduced systems violating the capacity when either directed separated-pair
identity is omitted; and a local rank-one trim showing that one-sided query
idleness does not preserve support. The prefix control establishes that query support alone
does not imply prefix commutation; it is not claimed to isolate that one
hypothesis in a complete commuting root. The finite checks support the written
universal proof; they do not replace it.

The D checker independently reconstructs the q=2 word and verifies its 32 direct
integral formal coefficient matrices in addition to both-character checks. Its
default mode is read-only and five corruption controls authenticate the exact
fixture. The independent reduction audit and source-aware proof review are
recorded in [REVIEW.md](REVIEW.md). [RANK21-NOTE.md](RANK21-NOTE.md) preserves
the construction history: its all-q open question is resolved by SHARP-BOUND.md,
and its final appendix records the completed integral formal verification.

[ROOT-RANK21.json](ROOT-RANK21.json) is the exact independently constructed q=2
word. [CHECK-RESULT.json](CHECK-RESULT.json) is a regenerated check receipt.
The base matrices and their input-basis inverses are integral. Together with
the exact unit Gram blocks and diagonal stage masks, this transfers the
construction to every allowed ground field, not just the rational checker.

## Scope and credit

This is a coefficient-space theorem and exact abstract word. It supplies no
native phase, physical ports, ownership discharge, profitable complete paid
invoice, all-size compiler/precision/analytic discharge, selected-frontier
change, or new kappa. All five selected framework assumptions remain.

The coupled normal form and prior rank tools retain Ali Romman's, thu-nmrc's,
ToikY's, Cinna Davis's, and the original query/controller contributors' credit,
as recorded in the frozen #6773 note and its ORIGINS manifest. Worker B derived
the analytic capacity bound independently before opening worker D's files.
Worker D supplied the rank 21 witness; the lead supplied the scalar rank 11
word and independently audited the ordered reduction. These are separate AI
work streams in the same research session, not independent human review.
Prepared for Jerry Chen (@CubeJerry) with substantial OpenAI Codex assistance;
Apache-2.0. No proof-kernel acceptance is
claimed. Exact pins and attribution are in [ORIGINS.json](ORIGINS.json).
SOURCES.json pins the originating main catalogue, selected record and license.
The frozen #6773 files are authenticated locally by SHA256; their fetched
Git-blob hashes are recorded in ORIGINS.json. Their foreign pending head is
provenance, not a generic Git-history dependency.
The registered replay has no external live inputs. The successful local registered
replay is recorded in [REPLAY-RECEIPT.json](REPLAY-RECEIPT.json). Metadata success or archive
publication does not imply scientific acceptance or supplier admission.

## Open next questions

- Can this inventory produce a profitable changed native boundary? First price
  the complete output masks, recursive calls and ordinary charges against the
  strongest located root. The coefficient rank itself does not answer this.
- Which odd-q ceiling-equality inventories are attainable? Start from the
  integer slack in the two sector-capacity inequalities; the even-q result
  does not classify odd-q equality.
- Is every even-q equality word equivalent to a direct sum of the two reflected
  q=2 atoms? Start with the common-image/common-row equality conditions. Only
  the incidence inventory, not internal block decomposition, is proved here.
