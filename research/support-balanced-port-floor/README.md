# A matching cost floor for k-port scalar decoders

**Scoped obstruction; no new kappa.** Even denominators and signed Gram
weights cannot rescue the exact PR2297/PR2041 covers when each scalar term
has the same source and target **span of complete port spaces**. Supports and
coefficients may differ; any finite term count and arbitrary rational weights
are allowed. Identical-support and Gram factors are included.

A nonsingular principal decoder block forces a matching of its ports to
separate scalar terms. Each matched term pays at least the complete dimension
of that port. [PROOF.md](PROOF.md) gives the determinant and binary Gram-minor
argument, the exact hypotheses, and a quantitative condition for escaping it.

| Literal cover | Rational cost floor in this class | Favorable unpaid budget | Deficit upper bound |
|---|---:|---:|---:|
| PR2297: 22 five-frames and one pair | **554, attained by the direct identity** | 4432/9 | -554/9 |
| PR2041: 37 three-frames and one line | **297**, not claimed sharp | 2672/9 | -1/9 |

These budgets use the retained nine-stage portwise coverage law, before
additional native costs. Both already fail at zero saving. The three-port
bound uses an explicit 99-port nonfree principal set and the **actual mixed
cover**; it does not reject a separately completed uniform-three contract.

For PR2297, any arbitrary asymmetric decoder with positive saving must have
at least **16 terms** whose pairing rank is smaller than a source port's
complete dimension. Such terms necessarily have unequal complete port spans.
This is only a necessary condition; it supplies no feasible decoder at 16 terms.

## What this adds

Sagar Thakrar's [PR2532 audit](../kport-group-scalar-endpoint-audit/README.md)
provides the masks, the 554/334 floors for 2-integral decoders and the
99-port clique lead, leaving even-denominator cancellation open. Here the
matched-span restriction replaces the arithmetic restriction. The five-frame floor
remains 554 for all rational denominators, and the weaker three-frame floor
297 still suffices to reject its literal coverage budget. Tekalign's
[PR2782 Gram gate](../c5-dyadic-decoder-gate/README.md) treats arbitrary masks
but assumes positive half-integral weights and integral factors; this result
uses a nonsingular principal block and neither of those coefficient premises.
No original binary factorization, 2-integral theorem or scalar mask is claimed
as new. General unmatched-span factors and other masks remain open. Adam Gall's
[P112 matched-frame bound](../p112-matched-frame-copy-floor/README.md) concerns
a different line mask and requires paid term ranks at most four. This principal-set
argument has no term-rank cap, but relies on the named k-port masks.

## Reproduce

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 -I -B scripts/research_package.py --package research/support-balanced-port-floor
```

The registered normal and optimized verifier checks exact source SHA256/Git
blob pins before parsing scientific data, selected archive-member binding,
both partitions, every group-pair tariff with separate packed and dense binary
rank engines, explicit principal-set witnesses, direct identity charges and
exact rational budgets. It imports no predecessor executable. The full
[RESULT.json](RESULT.json) is compared byte-for-byte, including JSON types.

Four rational positive fixtures include half-weight Gram terms, unequal
factors with equal supports, different supports with equal complete spans,
and quarter/third weights with signed cancellation. All 512 binary 3-by-3 matrices exercise the rank-to-matching
implementation (174 have full rational rank). Seven semantic failure controls
and four CLI integrity tests check the stated hypotheses, source corruption,
read-only Git-free export, typed receipt corruption and overwrite refusal.
Default replay writes nothing; `verify.py --write /new/path.json` creates a
fresh receipt and refuses to overwrite an existing file. The universal claim
comes from the written proof; finite fixtures do not exhaust rational factors.

## Scope and continuation decision

Base canonical main: `4b82082f901945f8d0314f143576c7ad31e021fc`, priority
revision 5. The selected-source baseline and card's ceiling positive control
pass. [TASK.json](TASK.json) records nonce `67b7fb0263f430b685f40f33ee0c7b12`,
the changed `coverage-law-change` scope, live overlap and the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18965662).
Exact retained sources and predecessor heads are in [SOURCES.json](SOURCES.json).
Before submission the isolated branch was rebased onto refreshed canonical main
`c7df0bb890cae0cc393cdd32dad19c3facc80992`; guidance, catalogue, selected record
and scientific inputs were unchanged. Final complete overlap covered 491 open
PR bodies and 1,522 Discussion/comment records at 06:32/06:35 UTC, plus local
notes/ledger and targeted all-state PR queries. No code-diff or novelty guarantee
is implied. Registered replay and selected-record integrity pass on CPython
3.12.14 / Darwin arm64.

Decision: **stop this matched-span construction class under the named covers
and coverage law**. No native implementation, full supplier replay, hosting,
precision, physical tape/compiler admission, outer analytic proof, formal-kernel
check or independent human review is claimed. Other scalar masks, degenerate
port spaces, unmatched spans and different call contracts are outside the
floor. No frozen source, selected record, review ledger or existing verifier
is changed. Unknown physical charges are not treated as zero in an adoption
claim; the unfavorable calculation simply grants them zero as a relaxation.

## Open next questions

Can unequal complete port spans provide enough actual rank relief? For the exact
five-frame cover, first give a rational masked identity with at least 62 units
of the asymmetry credit defined in PROOF.md, from at least 16 qualifying
terms, and price all complete port spaces. This changes the decision only if
its full bill is favorable; no such identity is supplied. A positive scalar
fit would still require native frames, restoration, hosting, precision and a
complete consumer. The structured question and blockers are in TASK.json.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in proof, source
inspection, implementation, checking and writing. No subagents or independent
human review. Apache-2.0.

Credit Sagar Thakrar/PR2532; Cinna Davis/PR2297 and PR2041; Adam Gall/PR1889;
Philippe Van Velzen's masked-identity/full-port tariff and 2-integral arguments;
Tekalign/PR2782; ctoth's port endpoint and rank-count lead; and the retained
selected E8 geometry/supplier lineage. All predecessor files and notices are
unchanged. The proof uses the elementary determinant matching argument; the
contribution is its scoped full-port application and exact budget consequence.
