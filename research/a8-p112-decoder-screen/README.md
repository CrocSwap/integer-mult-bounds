# A8 simplex P112 decoder: sharp copy cost 71 on matching-frame punctures

**Scoped proof with exhaustive finite lemmas; no new kappa or physical supplier.**
For the fixed A8 simplex nine-term all-pairs decoder, removing the specified
orthogonal eight-frame gives exact minimum copy cost **71**, even with arbitrary
complex per-root shifts. A witness with all nine terms active has term costs
`(1,8,8,9,9,9,9,9,9)`. Coordinate permutations extend the result to the **945
matching-frame punctures** in this orbit. Other frame orbits are unclaimed.

[PR1248](https://github.com/CrocSwap/integer-mult-bounds/pull/1248) proved the
fixed-simplex P120 floor 72 and explicitly left a P112 frame puncture as its
first open question. This package answers that question for one orbit. Since
`71/112 > 64/112`, the family cannot improve the standard P112 copied-information
bill, even before extra physical costs. This is a copy-cost rejection of one
route, not a completed recurrence calculation or a bound for arbitrary decoders.

## Exact scope and evidence

The roots are `e_a-e_b` and `1_S-(1/3)1` in the sum-zero subspace of Q^9. The
fixed column normals are `b_k=e_k-(1/9)1`. On live roots, `T_ik=r_ik` and every
exact decoder is `D_ik=2r_ik+t_i`, with arbitrary `t_i` in C and ordinary
transpose. The puncture is

```text
F = {e_(2j)-e_(2j+1), e_(2j)+e_(2j+1)+e_8-(1/3)1 : j=0,1,2,3}
```

It has indices `[0,15,26,33,42,89,112,119]` in the pair-then-triple lexicographic
root order. Terms are billed separately by binary pairing rank. Masked
identities and shared-copy pricing are excluded.

All nine column-label spans still have rank nine, so the copy cost is
`81 - sum(delta_k)`. However, puncturing creates two-dimensional partner
deficiency spaces: the P120 dimension-one lemma is false here. Enumerating all
subspaces of these enlarged spaces and imposing their mutual compatibility
proves `sum(delta_k) <= 10`.

- Primary replay: all nine anchors, 390,915 binary planes, 19,299 distinct
  ordered partner-space tuples, and 462,141 compatible subspace choices.
- Separate replay: labels reconstructed from the Gram pairing matrix,
  annihilator row reduction, direct Cartesian-product enumeration, and a
  checked stabilizer transporting two anchor representatives to all nine.
- Both check all 12,544 entries of the active witness. The primary also checks
  the zero-term witness; the separate checker prices actual pairing submatrices.
- Eight semantic controls include a coefficient error, a deleted term, corrupt
  labels, a nonorthogonal puncture, the false inherited dimension-one lemma,
  missing mutual compatibility, a false cost of 70, and a valid non-real shift.
- Six package tests exercise optimized relocated/read-only replay, the separate
  checker without the primary file, and changed, incomplete, missing or
  malformed receipts.

The argument covering every complex shift is in [PROOF.md](PROOF.md). The
deterministic finite evidence is [CERTIFICATE.json](CERTIFICATE.json). The
second implementation is by the same AI assistant, not independent human review.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3 -I -B research/a8-p112-decoder-screen/verify.py
python3 -I -B research/a8-p112-decoder-screen/independent.py
python3 scripts/research_package.py --package research/a8-p112-decoder-screen --check-only
python3 scripts/research_package.py --package research/a8-p112-decoder-screen
```

The last command runs both checkers and the six package tests. Expected markers:

```text
PASS_A8_P112_DECODER_FLOOR planes=390915 configurations=19299 compatible_leaves=462141 cost=71 controls=8
PASS_A8_P112_INDEPENDENT anchors=2 transported=9 planes=86870 compatible_leaves=92317 cost=71
PASS_REGISTERED_RESEARCH_PACKAGE research/a8-p112-decoder-screen outcome=negative-result
```

`verify.py --write` explicitly regenerates the certificate. Normal replay is
read-only. Source pins and exact predecessor heads are in [SOURCES.json](SOURCES.json);
the pending predecessors are attribution/context, not imported code or assumed
finite lemmas. [TASK.json](TASK.json) records the chooser, scope and next questions.
See [VALIDATION.md](VALIDATION.md) for measured checks and limits.

No supplier word, delivery/frame/restoration/hosting invoice, new moment,
selected cold replay, Lean proof, or complete multiplication theorem is supplied.
The selected frontier and all inherited all-size/compiler, common-label and
mutable-source, hosting, precision/tape, recovery, analytic-transfer and bit
H1-H5 obligations remain unchanged. Hosted CI and human review are unclaimed.

## Coordination

Base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; chooser nonce
`a57142e8e77d6c0af036ca35809daf69`, track `complex-mechanisms`, revision 2,
card `complex-masked-decoder`, scope key `2a6f2c726b78f9ae7d26`. This refines
the card's overcomplete-family branch to PR1248's explicit puncture question.

Nearest predecessors are PR1248 (P120 optimum) and PR1224 (normal form and
bounded searches). PR1212/1213 and discussion #1275 concern eight-term masked
rigidity; PR1236 and discussion #1267 concern masked root-star/co-star supports.
These are distinct hypotheses. Two parallel sessions from the same account
study bit-side zero-frame feedback (discussion #1290) and selected bit hosting
(discussion #1289); this package does neither. The original claim is in
[discussion #1241](https://github.com/CrocSwap/integer-mult-bounds/discussions/1241#discussioncomment-18909913).
The final overlap check used a shared snapshot of 788 open PRs and 40
discussion records with complete pagination, fetched at 21:54:03 and 21:54:12
UTC on 2026-10-13. It may miss later changes.

## Open next questions

- **Other frame punctures relative to the fixed simplex.** Do they also have
  minimum cost at least 64? Enumerate orthogonal frames and their S9 orbits,
  then recompute column ranks and partner dimensions for a representative
  outside the matching-frame orbit. This tests whether the remaining P112
  part of PR1248's question can improve copy cost. The present enumerator
  deliberately rejects partner dimensions above two and may need extension.
- **Another specified nine-normal frame.** Can the A7+A1 or A2+E6 family in
  PR1224 admit copy cost below 64 on a named P112 puncture? First establish its
  exact ratio classes, column spans and a favorable complete cost budget.
  The simplex's common kernel vector and compatibility census do not transfer
  automatically; physical realization would remain an additional obligation.

## Credit and disclosure

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit Philipp / **mightyOil**, PR1248, for the deficiency-space method, P120
floor and explicit P112 follow-up; **joaqcoo**, PR1224, for the nine-term normal
form, A8 frame and ratio-class viewpoint; **DreamingOfClouds**, PR717/595/446,
for the decoder and pairing-rank cost model; **themilkman216**, PR968, and
**woklerx**, PR1077/1180, for surrounding floor results; and the classical
E8/A8 geometry. The selected supplier lineage retains its existing credit.
No predecessor file is changed. New work is Apache-2.0, the repository license.
