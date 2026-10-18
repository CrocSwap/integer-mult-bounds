# Two fewer XORs in the R420 cleanup

This finite bit-circuit construction replaces five cleanup XORs by three in
eumemic's PR543 R420 word. The complete local scalar ADD count falls from
26,916 to 26,914. Every source and dirty helper is restored, all register frame
paths are unchanged, and the reverse positive-prefix bound decreases.
There is no new supplier exponent or integer-multiplication kappa claim.

The accompanying negative result closes commutation-only cancellation on this
specific cleanup: all 18 repeated-gate pairs have a noncommuting blocker.
The improvement uses an additional F2 conjugation identity.

## Reproduce

From the repository root, with Python 3.11 or later and its standard library:

```sh
python3 -B research/r420-cleanup-commutation/verify.py
```

Expected final line:

```text
PASS_R420_CLEANUP_CONJUGATION C=2973->2971 native_adds=26916->26914 columns=660 kappa=unchanged
```

The verifier checks the pinned baseline, reconstructs the candidate from
`certificate.json`, checks all 672 frames and 660 symbolic input columns, and
rejects six negative controls. It also exhausts the four-register identity on
all 16 Boolean inputs. These finite checks do not formalize the multiplication
theorem. All substantive checks remain active under `python3 -O`.

To export the exact candidate as uncompressed JSON for downstream replay:

```sh
python3 -B research/r420-cleanup-commutation/verify.py --emit-word /tmp/r420-cleanup.json
python3 -B research/e8-bit-carrier-skeleton/code/bit/export_records.py /tmp/r420-cleanup.json /tmp/r420-cleanup-records
```

The existing exporter reports 29,872 records. The candidate's canonical JSON
SHA-256 is `f87e4574addee69e4c9387f0d7139138454cf24e78e2c1358f239a52546b0abd`.
Source archive hashes are checked separately from canonical payload equality.

## Object and exact substitution

The base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Its accepted conditional
result is kappa `51110230636731/31250000000000000`, or
`0.001635527380375392`, from #626 with #543. The construction and its remaining
assumptions are described in the [selected review](../../docs/research/community-k492-review.md).
This experiment uses the selected bit word from #543 at
`2065fe4f72a914d907f1046603f5a36f17018535`, not a larger pending PR claim.

Expand each C gate's source list in its stored order into binary gates
`(destination, source)`. Indices below are zero-based in that original stream.
Every C gate has full-frame id 1.

| Gate | Positions | Operation |
|---|---|---|
| A1 | 714, 1321 | helper 616 ^= helper 530 |
| A2 | 718, 1320 | helper 616 ^= helper 540 |
| B | 1071 | helper 466 ^= helper 616 |

For each Ai, B is the only noncommuting gate strictly between its two copies.
A1 and A2 commute with each other. Commute the Ai copies toward B to obtain
`A1 A2 B A2 A1`. On the four registers this sequence leaves 616, 530 and 540
unchanged and sends 466 to `466 + 616 + 530 + 540` over F2. It therefore equals
the three gates `B`, `(466,530)`, `(466,540)`.

Delete original offsets 714, 718, 1320 and 1321. Insert the two correction gates
immediately after original offset 1071. All other binary gates retain their
order. The certificate records this complete construction. Expanding
multi-source gates changes the number of JSON records; counts here always
refer to binary XORs or exported native records, not JSON gate records.

## Interface and complete local cost

The historical [PR543 checker](../e8-bit-r420/code/xcheck.py) requires C to be
the literal reverse of the non-target gates in A and B. This candidate fails
that structural H4 check as expected. The original checker is unchanged.

Use H4-prime instead: C touches only source/helper registers at the full frame,
each such register finishes at the full frame, and C induces the inverse of
the raw source/helper map U. The [PR543 interface proof](../e8-bit-r420/README.md)
then applies directly: the raw word sends `(z,y)` to `(Uz,y+Jx+Ks)`, and C sends
that to `(z,y+Jx+Ks)`. D, J, K and the target map are unchanged. Exact matrix
equality to the original cleanup establishes H4-prime for arbitrary helper
contents. The verifier reports the original H4 failure and checks H4-prime;
it does not weaken or patch the predecessor checker.

| Complete local charge | Original | Candidate |
|---|---:|---:|
| Binary cleanup ADDs | 2,973 | 2,971 |
| All binary ADDs, including D and scatter | 26,916 | 26,914 |
| MOVE records | 2,940 | 2,940 |
| COPY / ERASE records | 9 / 9 | 9 / 9 |
| Helpers | 420 | 420 |
| Forward positive-prefix row bound | 144,651 | 144,651 |
| Reverse positive-prefix row bound | 2,270,064 | 2,266,968 |

The four removed reads and two new reads are charged. All helpers already
exist; there is no scratch allocation, extra copy or omitted restoration.
Each register has exactly its original sequence of frame transitions,
including its final climb. Thus all recursive child ranks are unchanged.
The paid histogram, including the nine rank-8 copies, is
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, with rank mass 5,112. MOVE timing can
change; the claim is equality of each register's path, not of the global event
order. In the inherited local recurrence the child terms are identical and
the scalar ADD component of the node toll decreases by two. No new complete
hosted recurrence or assembled bound is asserted.

The circuit identity is over F2, not equality of positive integer shears.
The cancellation-free bounds are checked separately on the actual forward
and reverse streams, including COPY/ERASE. The commutations are also valid
for the positive envelope, and replacing the joint sandwich lowers the
envelope on helper 616 while preserving the envelope on 466. This explains
why fewer gates do not hide a larger local coefficient bill.

## Search coverage and controls

The OS assignment seed was 10. Three candidates and the overlap decision are
recorded in `CLAIM.json`. The finite scan starts at binary cleanup offset 10
and wraps once. It covers all 2,973 original gates, all 2,955 distinct binary
gates, and all 18 duplicate pairs. Each repeated gate occurs twice.
The stopping rule was one complete census, followed by testing every
one-blocker pair, with no further circuit resynthesis. Exactly two pairs
have one blocker and both are used in the joint substitution.

Commuting swaps preserve the relative order of a gate and any noncommuting
blocker. If a first cancellation were possible after commuting swaps, its
two equal gates could not still have such a blocker between them. Every
duplicate pair has one, and none has yet been deleted before the hypothetical
first cancellation. Hence no first cancellation exists. This is an exact
obstruction for commuting swaps and pair deletion on the fixed word. It
does not exclude conjugation, insertion of neutral pairs, general linear
synthesis, changed forward circuits, or other cleanup words.

Controls omit each correction separately, supply the wrong correction
source, introduce a second noncommuting blocker, try the uncorrected
three-to-one deletion, and put cleanup at an illegal lower frame. The first
two omissions and the uncorrected deletion fail exact F2 equality; the extra
blocker fails the rewrite premise. These are distinct from a failed search.

## Validation boundary and attribution

`VALIDATION.json` records the checks performed locally. A separate Codex
worker independently replayed the candidate using no repository optimizer
or checking imports and obtained the same columns, paths and prefix bounds.
The existing native exporter was also run on both words; its binary records
confirm the table above and identical frame/state descriptions.

No C++ cohort replay was run because Boost headers were unavailable in this
environment. The recursive hosted-parent reconstruction, renamed-instruction
audits, residual-host checks and full invoice/outer assembly remain integration
work. The full `make verify` suite and selected cold replay were not run for
this standalone addition; no selected source, generator, certificate or
`upstream/` file changes. Uniform/compiler/common-label/mutable-basis,
hosting, signed-lift, precision/tape and analytic obligations remain inherited.

Credit belongs to eumemic's #543 word and checker, the #493 carrier-skeleton
lineage, Dylan Crow's record exporter and original bit circuit, Zhihao Chen's
#425 cleanup interface, the #472 common-label realization, and the cumulative
contributors credited in those packages. Concurrent #670 by yongjae321,
#674 by x0hu, #688 by Ali Romman and #691 by mtpsl change forward blocks and
their literal reverse cleanup. #686 by Mikhail R. Gadelha and #694 by Greer
Guthrie change frame-zero compensation. Tuomo Kiiskinen's #661 fixes the
phase-B gate word and excludes cleanup synthesis. This result instead keeps
D/A/scatter/B fixed and changes only C. None of those pending patches is a
dependency, and compatibility with their changed cleanup words is untested.

The final refresh through #709 also found [#708](https://github.com/CrocSwap/integer-mult-bounds/pull/708)
by @thakrarsagar at `2ec522a466ec448f148d4355dc43b51c0ef1e0b5`. It shares
phase-A decoder operands and regenerates literal reverse cleanup, saving 114
ADDs while raising the measured prefix bounds. The present result uses a
different algebraic rewrite, changes C alone and lowers the reverse prefix
bound. It neither imports nor composes #708. #709 caches geometry checking;
it changes no circuit and is not used here.

Prepared for GitHub account **@thakrarsagar** with substantial OpenAI Codex
assistance, including the separate audit worker. No independent human review
is claimed. New files are under the repository's Apache-2.0 license.
