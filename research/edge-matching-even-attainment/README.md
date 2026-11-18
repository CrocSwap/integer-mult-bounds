# Sharp even-difference image maxima

No new kappa. For irreducible binary rank-one-idempotent collections with
nonzero off-patterns, the exact maximum joint-image dimension at positive
even k-nu is `(3k+nu-2)/2`, except at `(k,nu)=(2,0)`, where it is one.
Here k is the actual pattern-span dimension and nu is the maximum matching
size of its matrix-unit graph. Coordinate projectors are excluded.

The [proof](PROOF.md) gives two fresh links to disjoint pair and triple
blocks, with complete-pool control at every parameter. The exceptional
small case has an all-width exclusion and an attaining one-dimensional
pool. At k=nu, only k=1 permits an irreducible collection, and it must
be a proper subcollection of its pool. Together with the prior odd case
in [PR #7703](https://github.com/CrocSwap/integer-mult-bounds/pull/7703),
these results give all fixed-(k,nu) maxima and existence cases.

This is a geometric capacity result. It does not classify every maximizer
or a fixed edge graph, solve a legal paid word, or provide a native supplier.
The selected value stays `363005817/100000000000` and all five assumptions
remain. Preparation, ownership, native action, restoration and the complete
recursive invoice are still separate obligations.

## Reproduce

Use CPython 3.12 and the standard library from the repository root:

```sh
python3 -B scripts/research_package.py --package research/edge-matching-even-attainment
python3 -I -O -W error -B research/edge-matching-even-attainment/verify.py
```

The direct marker is `PASS_EDGE_MATCHING_EVEN_ATTAINMENT`. The registered
hook runs normal and optimized modes. Failures raise exceptions.
The only runtime file is [RESULT.json](RESULT.json). The all-width claim
is a written proof, with the inherited matching upper bound stated explicitly.

Finite checks lift every nonzero pattern in 24 complete attaining families,
42,256 patterns in total. They check the actual ranks, matching numbers,
common-kernel condition and connected projector action. All-vector orbit
checks also run when n<=9. Four smaller families are independently checked
by raw factor enumeration. At (k,nu,n)=(4,0,5), the full pool contains six
projectors; the extra member is retained and checked.

The two-dimensional restriction census checks all 36 ordered pairs and
216 ordered triples; all 168 triples with idempotent sum have an invariant
line. The one-dimensional exception is checked with two pool algorithms.
All 126 one-per-edge choices for k=nu through six are checked. Wrong-parity
links and idempotent links with a singular fresh pairing are rejected for
the stated reasons. See [VALIDATION.md](VALIDATION.md).

## Task and overlap

Base: canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. The contextual card is `bit-helper-contract`, changed to the
remaining local image-capacity question. The selected binding-only check
passes and identifies the catalogue's historical context. It is not a
selected scientific replay.

The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19710038)
states the proof target and stop rule. The refresh on 2026-11-18 searched
1,006 open PRs and 7,650 Discussion records with complete pagination.
Reference intake and the complete 6,175-record closed cache were also
checked. The related sources are the matching upper bound, the odd
classification, and Nick Petalas's earlier one-edge upper bound. The last
source explicitly leaves its four-dimensional attainment open.
No separate even-difference classification was found. Sparse local notes,
unpublished work and semantic search limits prevent a novelty guarantee.

Final source intake also found unpaidmoon's
[PR #7094](https://github.com/CrocSwap/integer-mult-bounds/pull/7094), which
already attains (4,0,5) with a different five-member complete pool. Its
proof was read and its literal pool is checked separately. That instance
and the prior matching bound already give its maximum; no first-attainment
claim is made for the six-member fixture here. The new claim is the general
even-difference theorem. The full source suite was not rerun.

This is a bounded proof continuation, not an expansion into a native
implementation. It settles the remaining parity class but makes no claim
that a geometric maximum pays for a useful word.

## Open next questions

Which other complete pools attain the even maximum? Start with the two-unit
defect in the disjoint relation identity and account for all lifts, including
dependent-image members. The present theorem gives maxima and one family,
not the classification of all maximizers.

Can the two-link alphabet support a legal paid word that saves rank? First
state the exact integral relation lattice, full ambient endpoint and dirty
state contract. The existing one-bridge obstruction does not automatically
cover two links. No word or complete invoice is supplied. Neither question
is reserved.

## Credit

[CREDITS.md](CREDITS.md) links the consumed proofs and adapted code.
The matching theorem, old blocks, odd maxima, fiber lemma and one-edge
upper bound remain predecessor results. Prepared by Ali Romman with
substantial OpenAI Codex assistance. Apache-2.0. No independent human or
proof-kernel review is claimed.
