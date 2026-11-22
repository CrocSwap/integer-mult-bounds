# Fixed-clock paired-move screens for the 111-port BIT source

This package is a scoped negative result, not a new supplier or a κ improvement. It
screens a particular replacement of two paid rank-one MOVEs by one rank-two
MOVE, and gives a stronger ancestry obstruction for 10 of those replacements.

## Source and case set

The literal 39,600-instruction, 630-public-owner source is Ali Romman's
[#8027 BIT candidate at `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`](https://github.com/aliromman/integer-mult-bounds/blob/fb9b6a7b0d27da1cf98430893a3016bf811e2aa4/research/p104-live-relative-gain/BINARY-CANDIDATE.json.gz).
Its compressed SHA-256 is
`74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`.
This is the same byte-pinned graph named by the #8035 standalone supplier.
The byte-identical source gzip is included as `BINARY-CANDIDATE.json.gz`; the
original source, contributors, notices and license retain their existing attribution.

For each chronological pair of paid MOVEs `a → h` at clock `i` and `h → b`
at clock `j > i`, retain only paths with ranks 1 and 1 and a monotone rank-2
direct difference. Delete the first MOVE and replace the second at clock `j`
by `a → b`. All other MOVE incidences and times, all starting and final owner
charts and all public outputs remain fixed. There are **1,557** such paths.
The replacement retains rank two; the verifier checks exact two-sided projector
nesting for its endpoints, as well as for the original contacts. Clocks are
zero-based native instruction indices, not wall-clock timestamps. This case
set does not include timing changes, other endpoint exchanges, extra moves,
nonmonotone paths or changes to the initial/final port charts.

## Original-receipt preservation

Each surviving native receipt, including the receipt at the replaced egress,
must reproduce its original normalized linear form at its destination by the
same clock. Senders and receivers are granted complete local historical stock,
free storage and arbitrary linear XOR recoding. If the original receipt is
already in receiver stock, the checker grants that receiver the **entire**
sender stock for that one contact. If not, it tests whether the receipt lies
in the sum of source and receiver spaces, then adds it to receiver stock.
Every possible one-scalar encoding satisfies this optimistic recurrence.

All 1,557 cases fail this contract. The first obstruction is a missing receipt
before the replacement in **616**, at the replacement in **619**, and after
the replacement in **18**; **304** instead reach a missing terminal output.
The raw receipt was independent of the receiver's previous stock at every
original event. No redundant-receipt full-stock overgrant actually triggered
in these tests. The result says nothing definitive about a word that changes
original intermediate receipt demands and later jointly decodes its targets.

`RECEIPT-RESULTS.json.gz` names each ingress, egress, first failed receipt and
terminal mismatch. Its full chronological control replays every case from
initial stock; it shares the same binary basis routines and primitive parser
with the faster incremental algorithm, so it is a control of the incremental
bookkeeping rather than an independent implementation.

## Final-target cuts with native exterior histories

Of the 1,557 paths, **854** have a public output at their hinge, covering all
111 such hinge charts. For each, delete the first ingress and grant the hinge
the *entire original preclock sender span* at every remaining ingress. Also
grant its initial fields and free local history. The required final target is
outside this union in all **854** cases. They share **304** distinct
hinge-and-deleted-ingress cuts. Each cut has a binary dual witness; adding the
deleted native ingress form to the overgranted union restores the target. All
304 distinct positive controls are checked. This
scope allows changed intermediate receipts and unlimited capacity on the other
incoming contacts; it assumes those senders do not gain information outside
their original native preclock spans. Altered exterior producers are open.

For example, remove `344 → 525` at clock 8243 and send its original receipt
directly `344 → 1` at clock 10093. Output 111 at chart 525 must equal
`e0 + e111`. The difference `e111 + e589` annihilates the full original
source history for every remaining ingress to 525, while flipping both the
missing ingress value and the required target. Thus no local recoding from
those frozen source spans can repair that output. `TARGET-CUT-RESULTS.json.gz`
contains a checked witness and positive control for each case.

## The nine two-ingress, three-exit charts

These are the nine hinges with exactly two incoming and three outgoing MOVEs.
Only monotone two-hop paths appear in the table; the third exit may reverse
rank and therefore fall outside this particular direct rank-two exchange.
All listed cases fail original-receipt preservation. The last column is the
number already ruled out even with unlimited information per remaining MOVE.

| Hinge | Eligible ingress clocks | Eligible egress clocks | Paths | First receipt failure clocks | Ancestry exclusions |
|---:|---|---|---:|---|---:|
| 510 | 8105, 8113 | 10036, 10039 | 4 | 10036, 11017 | 0 |
| 511 | 8277, 8288 | 10042, 10045 | 4 | 10042, 11030 | 0 |
| 512 | 8129, 8162 | 10048, 10051 | 4 | 10048, 11043 | 0 |
| 513 | 8761, 8772 | 10054, 10057 | 4 | 10054, 11056 | 0 |
| 514 | 9157, 18859 | 10060, 18862 | 3 | 10060, 18866 | 0 |
| 515 | 8312, 8327 | 10063, 10066 | 4 | 10063, 11069 | 2 |
| 516 | 8375, 8423 | 10069, 10072 | 4 | 10069, 11082 | 0 |
| 517 | 8722, 8753 | 10075, 10078 | 4 | 10075, 10997 | 0 |
| 518 | 9052, 9067 | 10081, 10084 | 4 | 10081, 11095 | 0 |

Only three chart-514 paths are chronological: its second ingress at 18859
cannot be paired with the earlier egress at 10060. The 35 listed cases
therefore comprise 33 ancestry-only passes and two ancestry exclusions.

## Unrestricted causal ancestry

In the second screen, dispense with all original-receipt requirements and
grant every remaining MOVE the entire source history of independent public
inputs. This strictly exceeds the single-field bandwidth. If an input label
still cannot reach a required output's chart, no causal recoding of that fixed
contact schedule can make the output depend on it. **10** of the 1,557 paths
fail this test; **1,547** pass this necessary test only, with no construction
or one-scalar sufficiency implied. `ANCESTRY-RESULTS.json.gz` includes every case
and every missing input/output pair.

For example, remove `351 → 515` at clock 8312 and replace either `515 → 1`
at clock 10063 or at clock 10066 by `351 → 1`. The first input of main pair
80 begins at chart 82 and the required output 191, whose form is `e191 + e80`,
ends at chart 605. The original contact schedule contains the causal path

`82 → 171 → 280 → 351 → 515 → 350 → 71 → 0 → 86 → 605`.

With either named bypass, `e80` cannot reach chart 515 or chart 605, even when
every remaining contact carries every reachable input at zero extra cost.
The other two chart-515 bypasses, and every case at the other eight hinges,
pass ancestry only; no conclusion about their feasibility follows.

## Replay

Requires Python 3.12 and only the standard library. From this directory run:

```sh
python3.12 -I -B verify.py
```

The verifier checks the compressed and expanded source hashes and Git blob,
the retained notices and results, all 630 public images, 2,803 MOVEs,
3,433 dirty private clears, 859 distinct original endpoint pairs and 333
direct endpoint pairs. It runs all 1,557 cases in each screen and compares
every incremental result with a full chronological replay from scratch. It
also checks the 304 distinct target-cut witnesses and positive controls that
cover 854 paths. A separate parser with low-pivot elimination replays the
source and independently checks every target-cut certificate, its restored-row
control and a corrupted witness.
Recomputed results are written to temporary files and compared to the retained
compressed receipts; the checked-in receipts are not rewritten. A corrupted
source-byte control must be rejected. The three receipt files contain every case.
The check does not establish a physical replacement program, priced outer
supplier, finite application or new κ result.

## Open next questions

- Can a surviving fixed-clock bypass deliver the actual public outputs using
  changed intermediate receipts? Start with one of the 1,547 ancestry
  survivors and solve the source-side and joint terminal coding conditions;
  ancestry alone grants unlimited bandwidth and does not supply the code.
- Can a multi-edge exchange produce a complete physical saving? Begin with a
  literal changed word, then verify all 630 images, nesting, dirty-bank
  accounting, the 36-call invoice and the finite caller. A moment saving
  without those checks is not a qualified supplier.

## Credit

Ali Romman supplied the literal #8027 binary graph. Clear1nsight supplied the
predecessor mixed-rank compiler. The exact retained upstream attribution is in
[PARENT-NOTICE](PARENT-NOTICE); the source is Apache-2.0, with its unchanged
[license](LICENSE). This screening and its verification were prepared for
Clear1nsight with substantial OpenAI Codex assistance. Independent scientific
review remains open.
