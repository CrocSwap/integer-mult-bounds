# Independent exact review: chronological rank-2/3 majorization

Outcome: no mathematical discrepancy found in the stated cap-16 chronological
partition relaxation. The independent enumeration agrees with every primary
sorted-prefix maximum and every chronological-partition count for all twelve
observed run types. This is AI-assisted independent implementation and proof
checking, not independent human review or formal-kernel verification.

## Files reviewed and exact bindings

Worktree: `/Users/ross/git/math/donated-20261014-1656`.
Original assigned base: `1d201395e037bd3fcb0175007fdcd0154878e613`.
Final reviewed integration HEAD: `178a293edbd162fe3ce13e81a97af921366bd100`.

| File | SHA256 |
| --- | --- |
| `verify.py` | `c84a2f7c5b4d0d3b4cf11bf510eed436e75d22175c50d2de48e8c00f06ed09bb` |
| `independent.py` | `2825a48af5dc826b7be2994fa000ee9356f1bd8bb5371ec1c07b63e4a6b4d8d3` |
| `README.md` | `65dbe9892a46a5160c775d5f2d0e447ad8e1f357b6820319a10f2e2b420454b7` |
| `test_verification.py` | `20456bba700a9bea6af336d0f7e6972bb10f0e218ab2edd646ec4405b389ca36` |
| `RESULT.json` | `75fe2a0279c40f93e38b368f356af65569fc4ed7c412eb8871d44bda5e2897a8` |
| `INDEPENDENT.json` | `21ae0a97d1f23a919de3f5fbc42bd79eff13b9d0dd5dae924f6c94f00cf23dda` |
| scratch `majorization-proof.md` | `4bc48cf523a68dc9118a3d3fd56a9e3b85b687d79ea2980c4cca4031c2a85c93` |

Package file paths above are relative to
`research/chronological-rank23-majorization/`. The scratch proof is in the
same scratch directory as this review. The proof is incorporated in README.md.

Both source hashes were independently recomputed. The archive is
`research/community-frontier1094-audit/selected-replay.tar.gz`, SHA256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`;
the unique member is
`candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz`, SHA256
`241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`.
The independent oracle parses the bytes it hashes, without extraction to disk.
Predecessor PR-head attribution was supplied by the parent; this review does
not claim an independent GitHub or predecessor-code audit.

## Independent method and finite coverage

For a rank tuple r, define E(r) as a map from descending block-mass tuples to
integer presentation counts. Set E(empty)={empty:1}. For every legal nonempty
prefix p of r, recursively enumerate E(the remaining suffix). Insert sum(p)
into each descending tuple and add its multiplicity. A chronological partition
has a unique first block and suffix partition, so this recurrence enumerates
every legal cut set exactly once before sorting; sorting only coalesces equal
mass histograms. No primary or predecessor function is imported by the oracle.

For each candidate, the oracle separately checks explicit consecutive block
lengths, exact coverage, each mass <=16, and its complete sorted mass vector.
It then checks every sorted-prefix inequality for every reachable vector,
padding to the original number of calls. All arithmetic is integer arithmetic.

| Run | Multiplicity per orientation | Distinct mass vectors | Chronological partitions |
| --- | ---: | ---: | ---: |
| `(2)` | 362 | 1 | 1 |
| `(3)` | 123 | 1 | 1 |
| `(2,2)` | 16 | 2 | 2 |
| `(3,2)` | 5 | 2 | 2 |
| `(3,3)` | 124 | 2 | 2 |
| `(2,2,2)` | 3 | 3 | 4 |
| `(2,2,2,2)` | 1 | 5 | 8 |
| `3^4` | 3 | 5 | 8 |
| `(2,2,3^4)` | 1 | 24 | 32 |
| `3^8` | 1 | 18 | 120 |
| `(2,2,3^8)` | 1 | 106 | 472 |
| `(2,2,3^24)` | 1 | 2584 | 23499282 |

Totals across the twelve representative types: 2,753 type/vector pairs
(distinct mass vectors summed over types),
23,499,934 chronological partitions, 68,595 checked sorted-prefix inequalities,
and 36 cached suffix states. These totals are not a claim of separately
enumerating every combination across the whole trace. The product of per-run
partition counts, including run multiplicities, is
`497985972148699861249225869573548330083534063097079017641082880`
for each orientation. Separability of the cost handles those combinations.

Both complete literal traces independently give 24,767 events, 641 eligible
runs, 850 eligible calls, and eligible rank mass 2,132. Only `climb` events of
rank 2 or 3 are eligible, phases are transparent, and every other event is a
barrier. Each trace has 3,486 climbs and eight rank-8 centers. The optimized
complete profile has 3,291 children and mass 5,586:

`{1:2412,2:362,3:123,4:158,5:87,6:127,8:9,9:1,12:4,15:5,16:3}`.

The explicit witnesses give 162 nonsingleton blocks covering 365 source calls.
The pure `3^8` optimum has two chronological presentations, `(15,9)` and `(9,15)`;
all other listed canonical histograms have one presentation per run instance.
Thus histogram uniqueness does not assert chronological uniqueness.

## Primary recurrence and written proof review

The primary recurrence conditions on the last legal block of every prefix.
Marking it contributes its mass and uses one mark; leaving it unmarked leaves
the mark budget intact. Maximizing over all possible starts is exhaustive.
Zero values at mark budget zero are correct because all source ranks admit
singleton partitions. At most k marks select exactly the k largest masses
when there are at least k blocks, and every mass when there are fewer. This
is precisely the zero-padded sorted-prefix quantity. A separate cross-check
compared all twelve complete maximum arrays against maxima taken directly
over the independently enumerated mass vectors; every entry agrees. All
partition counts also agree.

The all-parameter proof in the README is sound under its stated model. Pure
3-runs have every block mass <=15, giving prefix bound min(T,15k). For
`(2,2,3^n)`, a mass-16 block must contain both twos, hence at most one block can
have mass 16; every other block has mass <=15. The proposed feasible partition
attains min(T,16+15(k-1)) for every positive k when n>=4. The n<4 cases are
correctly handled by one whole-word block. The integral formula for x^q is
correct for 0<q<1, including x=0. Majorization gives the correct inequality
direction, and strictness follows from differing truncated-mass functions.

No general greedy theorem for arbitrary rank-2/3 strings is asserted. The
control `(2,3,3,3,3,3)` correctly refutes that extension: `(15,2)` majorizes
greedy `(14,3)`.

## Controls and replay

Direct default replay passed under `python3 -I -O -B` for both checkers.
The independent positive controls cover transparent phase markers, six barrier
kinds, reversed optimal block order, and strict majorization. Five rejecting
controls target wrong chronological masses, cap violation, changed trace
boundary, a nonmajorizing candidate, and duplicate JSON keys.

Each of those five named predicates was individually removed in a disposable
in-memory copy. Every control then failed with `control-accepted`; unexpected
acceptance is outside the caught exception path. Five primary predicates were
also individually removed. Four yielded `unexpected acceptance`; deleting the
candidate-total check yielded `wrong rejecting predicate: missing mass`, which
correctly fails the suite instead of treating another rejection as success.

A minor receipt-schema issue was corrected during review: ordinary Python dict
equality equates integer 1 with boolean true and floating 1.0. Both checkers now
compare canonical JSON representations, preserving numeric type. Independent
checks explicitly rejected `true`, `1.0`, and `2` against expected integer 1.

Reproduce the fixed mathematical records from the repository root:

```sh
python3 -I -O -B research/chronological-rank23-majorization/verify.py
python3 -I -O -B research/chronological-rank23-majorization/independent.py
```

The separate parent-owned test harness was read and its mathematical detector
removal logic reviewed. The parent reports that the registered Python 3.12
replay passed all six test groups, including after integration onto the stated
final base. I did not independently repeat that full runner. I did repeat the
optimized independent replay after integration and reread the final README;
its source-binding clarification and type/vector-count wording are correct.
Scientific source, checker and certificate hashes were unchanged.

## Scope and unresolved obligations

The finite enumeration proves complete coverage for these twelve source-bound
run types. The written proof proves the two stated infinite run families and
all real 0<q<1 in the mathematical model. Neither result is a formal-kernel
proof. Phase transparency, contiguous blocks, cap 16, additive block mass and
zero extra physical charge are model premises.

No changed circuit was verified on arbitrary dirty input. Source gathering,
operand independence, routing, frames, hosting, restoration, precision,
realizability of a rank-sum child, recursive interfaces and the outer
multiplication recurrence remain outside this audit. No new kappa, physical
supplier, selected-record adoption, or numerical ceiling replay is established.
