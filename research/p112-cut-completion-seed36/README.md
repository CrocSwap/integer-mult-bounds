# Complete copied-information bills for a P112 rank-five cut

**Scoped information-rank audit and literal binary fork construction; no new κ.**
For the exact cost-seven P112 parent tagged `[7,0]`, splitting a rectangular
part K of rank r from M and retaining the full remainder M+K increases the
symmetric binary copy-channel information bill from14 to at least **14+r**,
for every r=1,...,6. Each bound is attained. Joint encoding of the two packets
is already allowed in this lower bound.

The best frame-coverage rank-five cuts have a larger bill: all384 canonical
cuts covering1060 of1260 frames require a **rank12 remainder**, shared copy
rank12 on each source direction, and symmetric information rank **24**.
A separately copied cut plus remainder costs17 on one orientation. This
prices an expense absent from a selected-part rank-five capacity screen.

The audited contract is explicit: two independent source families must emit
both `(Kx,(M+K)x)` and `(K^Tz,(M^T+K^T)z)`, with no source-dependent side
information outside the counted cut. The old two parent packets have rank14.
These are standalone F2 copy channels based on the pinned pairing matrix.
Their admission as complex decoder records is an open interface obligation;
this result does not supply a complex circuit, native helper profile or moment.

The proof also gives a directly related operand-compression corollary: linear
preprocessing that preserves both bilinear kernels `x^T K z` and
`x^T (M+K) z` needs the same total dimensions, even with an arbitrary receiver
decoder or a joint linear encoder. Computing only their sum, or performing
unpriced nonlinear work at the source, changes that contract.

## New evidence and proof

[PROOF.md](PROOF.md) gives the all-support argument. Every nonzero dual
codeword support on each parent axis spans the full rank seven. Consequently
a rank-lowering restriction leaves full-rank complementary data, and at least
one shared encoding direction gains r information dimensions. The proof covers
all arbitrary rectangular supports, not a random subset search.

The primary engine checks all127 nonzero supports on each axis. The independent
engine checks the equivalent pairwise-intersection premise on all **32,258**
codeword pairs: minimum overlaps are six/eight roots. Both reconstruct the
entire **21,463** canonical candidate domain, including8128 rejected rank-six
joint cuts, and agree on every admitted bill and the complete stream digest.

The exact capacity threshold is also proved: among rank-at-most-five cuts,
a symmetric information budget19 through23 has maximum1020 frames; a budget
at least24 has maximum1060. No complete budget frontier below19 is claimed.
The canonical coverage domination proof is used only for coverage, with no
assumption that completion costs are monotone under support expansion.

[EXPECTED.json](EXPECTED.json) contains the full92-entry bill spectrum,
all sharp rank1–6 witnesses, capacity witnesses and seed-selected maximizer.
The rank-seven identity control shows why parent rank alone is insufficient:
a five-coordinate cut of I7 has a rank-two remainder and no information penalty.
The intersecting-code premise is specific to this pinned P112 geometry.

## Complete dirty bit-channel witness and its priced limits

[GATES.json.gz](GATES.json.gz) gives a rank-factorized implementation of both
maximum-cut forks. Each uses12 arbitrary dirty helper bits and preserves all
source bits. The two words have1200 and1196 XORs. A pre-read and a post-read
cancel helper dirt, and every encoding operation is repeated to restore the
helper. No helper is assumed clean or discarded. Literal reverse execution
undoes the complete operation. Independent scalar replay checks all **348**
source/helper/output columns and rejects omitted erasure words.

For bit-array length L the same identity acts lane by lane, with arithmetic
counts1200L and1196L. This is a uniform linear identity, not finite random
validation of a multiplication algorithm.

The L=1 invoice includes one source read, one target read, one target write,
one XOR and one decode/dispatch per gate. A data head visits source, target
and returns to origin, costing `2 max(source,target)` movements. The instruction
head reads two fixed eight-bit addresses per gate, then rewinds; this prices
16 instruction-bit reads and32 instruction-head steps. Matrices are fixed
compiled coefficients. The two declared unit bills are325320 and329832.
They are operation counts in this fixed-cell pilot, not bit-complexity results
for a complex supplier. Arbitrary-L placement/control, physical allocations,
complex frames, private native scratch, helper calls, precision and hosting
still need a whole-call invoice. Matching copy/erase charges, when required
by a proposed interface, add to the information-only lower bound.

## Reproduce

From repository root, Python3.12 and standard library only:

```sh
python3.12 scripts/research_package.py --package research/p112-cut-completion-seed36
```

Expected: `PASS_P112_CUT_COMPLETION`, `PASS_INDEPENDENT_P112_COMPLETION` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. The independent
compact-column census took about4.5 seconds on the development host.
Both commands run with assertions disabled and use explicit failure checks.
`verify.py --write` rebuilds only this package's EXPECTED.json and GATES.json.gz.
Regenerated compression bytes may differ; decoded proof-relevant content is
compared exactly. MODEL.json is an immutable source input with an exact hash.

## Scope, assignment and source pins

OS assignment seed **36**, complex-supplier track. Exact base:
`55a02580ce1b283026e9d3b3510b218f8c93a4de`. The seed chooses maximum-coverage
witness36 in the sorted384-cut set. The scope differs through the completion
and shared-encoding obligation, not merely a different optimizer seed.
The [claim](CLAIM.md) is Discussion1555.

The data and capacity predecessor is woklerx's
[PR1445](https://github.com/CrocSwap/integer-mult-bounds/pull/1445), head
`7af6f56bf9ed58eacb3164d7b87b1c92716d8f07`. Its model retains the root order
from Cinna Davis's PR1347 at`64fd5f9e91961dedc16118fcc7ad71ee82efe28f`.
[Sources](SOURCES.json) pin those references and the actual copied data bytes.
No predecessor executable implementation is imported. This is a different
completion audit, not a challenge to PR1445's partial-cut capacity theorem.

The selected #1094 frontier, PR589 bit supplier and `upstream/` are unchanged.
No selected cold replay, native complex/bit compiler, supplier admission or
new κ is claimed. All-size/compiler, common-label/mutable-source, whole-call
hosting, precision/tape, analytic and bit-interface obligations remain inherited.
Changing other decoder terms or sharing with other parent data can avoid this
isolated full-parent contract and needs a separate cost analysis.

The adjacent PR1447 at `5f784a84bbe80879b5bd7ae9b48dd28a5765863d` studies
complex sparse completions `2G+Q` and counts rank-one factors. Its support
intersection method is related. This package independently studies the binary
rank-seven parent, shared operand information and the frame-capacity budget
step; no field transfer or dependency on that complex-rank conclusion is used.

## Open next questions

Determine which actual complex-call boundary would require these two packets.
First map each information channel to the pinned native data/copy records and
check source independence and side information before applying the lower bound.
Then test sharing with one other explicitly pinned parent: stack all available
source maps and compute the added rank of K. Such sharing may change the
isolated-parent information bill; its frames, chronology and restoration must
be realized before any moment claim. Structured questions are in TASK.json.

## Credit and license

Prepared by Cinna Davis (`1337isnot1337`) with substantial OpenAI Codex assistance
in proof, implementation, exact verification and writing. New work is Apache-2.0.
Credit woklerx / PR1445 for the joint rank-five capacity theorem and its next
questions; Cinna Davis / PR1347 for the rank-six support reduction and root
order; and the underlying DreamingOfClouds PR717, themilkman216 PR968, Navinor
PR1226, David Arias PR1236, Hanson Sun PR1242 and PR1323 copied-cost lineage.
No independent human or Lean review is claimed.
