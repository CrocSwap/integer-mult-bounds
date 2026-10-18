# P104 Y0: 48 source-acquisition lifetimes, two final arrivals

Completing **one target, Y0**, needs exactly **48 new helper lifetimes** in
the monotone correction model below. Two geometric hyperplanes do not mean
two helpers can acquire the required sources. All 48 required source registers
leave Y0's endpoint subspace on their first frame expansion; each contributing
source read must therefore occur on its own distinct initial line.

A matching chronological word uses 48 arbitrary dirty helpers, combines them
into the two hyperplanes recorded by [PR #2353](https://github.com/CrocSwap/integer-mult-bounds/pull/2353),
and makes exactly two arrivals and two writes at Y0's endpoint. It restores
every helper's logical input and completes Y0 to `y0 <- y0 + x0`, while the
other 103 target rows retain the original `G/2` channel. The added local bill is

```
52 H1 + 46 H2 + 48 H6       (146 transports, rank mass 432)
238 rational scalar ADDs   (142 coefficients ±1, 96 coefficients ±1/2).
```

This is a **scoped written lower bound and an exact finite common-chart
construction**, author-checked with a separately written circuit replay.
The checker imports neither the builder nor a predecessor executable. There
is no independent human review or proof-assistant proof. No complete P104
supplier, global improvement or new κ is claimed.

The claim is in [discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18942786),
taking its [one-target acquisition/restoration handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18942251).
The 208 global lifetime floor and its geometric covers are predecessor results;
the new result concerns the cost of acquiring the sources for one such cover.

## Model and exact pins

Use PR #1972's 4,058-event scalar/frame word, retained by PR #1991 at
`research/p104-native-channel/inputs/LOWRANK-WITNESS.json`, SHA256
`0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e`.
The scientific base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
PR #2353's exact inspected head is
`2704eadf6b5205d4b965e9c6fc6dce28b89783cf`. It supplies the model and the
recorded cover, with no imported executable or assumed review status.

Frames are subspaces of `F2^9` in the original compressed coordinates. Let
`q_s` be the nonzero label of Xs's initial line, and let `H` be Y0's final
eight-dimensional frame. Let `C = I - G/2`, where G is the ordinary rational
Gram matrix of the 104 root lines reconstructed from the pinned fixture.

The added network reads immutable X registers only in their retained frames;
it may use rational linear mixing, copies and clears within equal frames, and
upward transports of new helpers. Coefficients are independent of input values.
Every helper lifetime starts with source-independent contents. Arbitrary
independent dirty contents are allowed; discarding and reinitializing a
physical register starts another lifetime. All transfers of source dependence
must use these operations. There are no reads of original G/Q/D/C helpers or
any Y target, no source writes, no new source-dependent descents, and no
cross-frame read hidden in a coefficient or descriptor. Target writes are
additive. This is the restriction used in the relevant PR #2353 handoff.

The lower bound permits arbitrary retiming preserving the source/target paths,
arbitrary same-frame relays and cancellation, and even ignores restoration.
The upper word instead preserves the **entire original event order** and
restores all independent dirty inputs. Each of its 48 helpers goes from ZERO
to FULL, with the same logical dirty value at exit. FULL is a changed physical
frame, not an assertion that the entry and exit physical arrays coincide.

## Source-acquisition lower bound

The checker establishes the following exact finite premises, and records one
first-expansion escape vector for each source in [RESULT.json](RESULT.json):

1. Row `C[0,:]` has 48 nonzero coefficients, all `±1/2`. Their labels are
   distinct, and all lie in H.
2. For each of these sources, the only frame on its retained path contained
   in H is its initial one-dimensional line. Its first expansion already
   contains the recorded vector outside H; all later frames contain that
   expansion.
3. Every frame on Y0's path is contained in H. None equals any of these 48
   source lines, so none of the needed inputs has a direct source-to-Y0 read.

For a fixed source with nonzero correction coefficient, expand the added
linear program as a time-ordered dependence graph. A nonzero final coefficient
requires at least one directed dependence path from that source to an added
Y0 write. Along that path, transports only enlarge the frame and mixing
preserves it. Thus every frame on the path is contained in H. Its initial
source read must, by premise 2, occur in the source's initial line. By premise
3 that read enters a new helper, not Y0 directly. Later source reads at FULL
can be used for cleanup, but cannot lie on a path ending in Y0.

Choose one such initial read for each of the 48 independent source variables.
A single monotone helper lifetime cannot perform two of these reads: two
different one-dimensional subspaces are incomparable, whereas the successive
frames of a lifetime are nested. The 48 chosen reads therefore enter distinct
lifetimes. This proves the bound for arbitrary word length, relay depth and
rational coefficients; it is not a bounded-search conclusion. Cancellation
does not invalidate the argument: an absent dependence path makes the
corresponding coefficient zero under every choice of coefficients.

The positive control that expands two source paths into a common frame shows
why these **actual paths** matter. One dirty helper then acquires both sources,
delivers their sum and restores itself. Distinct labels alone would not give
the lower bound.

This is a one-target bound. **Do not multiply 48 by 104:** an acquisition
lifetime can feed branches serving several targets. The result neither
strengthens the global 208 floor by that multiplication nor excludes shared
relay networks across targets. It also does not cover original-channel helper
reads, which can carry source combinations through the retained descents.

## Matching two-arrival word

Set `K1 = {v in H : popcount(v & 1) is even}` and
`K2 = {v in H : popcount(v & 4) is even}`. These are the predecessor's two
seven-dimensional hyperplanes. They cover **all 48** sources of this correction
row, including the three sources omitted by its favorable earlier-frame
allowance. Assign a source to K1 when possible, otherwise K2. Each group has
24 sources; choose N2 and N7 as their respective collectors. All assignments,
frames and individual operations are explicit in [CIRCUIT.json](CIRCUIT.json).

Write `c_s = C[0,s]` and `d_s` for the independent input of helper Ns.
At original cut 0:

1. Add `-d_s` to Y0 for all 48 helpers in the ZERO frame.
2. Move each Ns to Xs's initial line, perform `Ns += c_s Xs`, and move it to
   its assigned K. It now holds `d_s + c_s x_s` in that chart.
3. Add each of the other 23 helpers into its group's collector. Keep each
   feeder's contents intact and move the 46 feeders to FULL. The collectors
   stay in their respective K frames holding their group sums.

Run the unchanged original word through completed cut **3467**. Event 3466
(zero-based) is Y0's rank-four final transport. All X sources are now FULL.
For each group, move its collector `K -> H`, add it to Y0, and move it
`H -> FULL`. Subtract the group's 23 still-intact feeder values from the
collector, then subtract `c_s Xs` from every helper in that group at FULL.
Run the unchanged original suffix.

The two target writes contribute `sum_s(d_s + c_s x_s)`. The initial
compensation cancels `sum_s d_s`; the retained word contributes `(Gx/2)_0`.
The result is exactly `y0 + x0`. Unmerging returns each collector to
`d_s + c_s x_s`, so the final source cleanup restores all 48 helpers.
Original sources and helpers retain their original endpoints because no new
operation writes them, and the original word never reads any Y target.

The exact replay checks the entire resulting 4,442-event word on **328
independent input columns**: all 280 original inputs plus 48 new dirty inputs.
It also replays the original 280-column `G/2` endpoint as a positive baseline.
No scalar sample or floating-point comparison is used.

## Local cost and its limits

| Added role | Count | Frame path | Paid profile per role |
|---|---:|---|---|
| Feeder | 46 | ZERO -> line -> K -> FULL | H1 + H6 + H2 |
| Collector | 2 | ZERO -> line -> K -> H -> FULL | H1 + H6 + H1 + H1 |

The scalar invoice is 48 initial compensations, 48 captures, 46 merges,
two deliveries, 46 unmerges and 48 source cleanups: **238 ADDs**. There are
96 added source reads and no new COPY, allocation or erase events. The
48 helpers are independently dirty at the boundary; they are not free clean
ancillas.

Under the stated ZERO-to-FULL boundary and dimension-gap transport billing,
each monotone lifetime pays nine rank units. Thus 432 is also the sharp rank
mass under that **additional boundary convention**. It is not a floor if
arbitrary helper entrance/exit frames are granted for free. The ADD count and
rank profile are the bill of this explicit word, not claimed optimal.

The original rank mass 2368 becomes 2800, with profile
`1126 H1 + 104 H2 + 86 H3 + 104 H4 + 48 H5 + 72 H6 + 8 H7 + 8 H8`.
The added mass is exactly the new `48*9` boundary progress; whether it earns
useful coverage credit requires actual owners and residual children. It is
incorrect to treat 432 automatically as extra recursive deficit, or to insert
this partial one-target word into a complete-supplier moment calculator.

These are complete logical scalar and nested-transport counts for this word.
The canonical-chart rule `Gamma_B Gamma_A^-1` is inherited from the native
channel model. New Clifford recipes/global phases, scalar/address lowering,
roundoff, global chronological hosting, idle/remainder charges, a completed
104-target moment, precision/tape and all-size admission are **not** checked.
Neither a native implementation invoice nor a multiplication theorem follows
from this package.

## Reproduce

Python 3.12, standard library only; the direct replay is read-only, Git-free
and network-free (about one second in the preparation environment):

```sh
python3 -I -O -B research/p104-y0-source-acquisition/verify.py
python3 -I -O -B research/p104-y0-source-acquisition/crosscheck.py
python3 scripts/research_package.py --package research/p104-y0-source-acquisition --check-only
python3 scripts/research_package.py --package research/p104-y0-source-acquisition
```

Expected final line:

```
PASS_P104_Y0_SOURCE_ACQUISITION lifetimes=48 arrivals=2 columns=328 added_rank=432 added_ADD=238 controls=10 no_new_kappa
```

The nine rejection controls remove dirty compensation, a capture, an unmerge
or source cleanup; substitute a wrong-frame source; change a transport charge;
deliver one original event too early; invalidate the source-escape premise;
or misassign a hyperplane. The tenth is the positive changed-source-path
countermodel described above. Acceptance uses explicit checks, including
with Python assertions disabled.

The separate `crosscheck.py` uses dense integer rows scaled by eight, checks
every division is exact, and uses binary Gaussian elimination instead of
enumerated subspaces. It reconstructs all 328 endpoint columns and the 48
source-escape premises without importing the primary checker or builder, and
compares the canonical full-endpoint digest. Both implementations are
AI-assisted work in this package, not independent human reviews.

`build.py --out NEW.json` reconstructs the literal CIRCUIT payload without
overwriting an existing file. `verify.py --out NEW.json` writes the verified
RESULT payload exclusively after checking the committed receipt. Compare
parsed JSON when regenerating; no compressed container hashes are involved.
[SOURCES.json](SOURCES.json) pins the two live inputs and task provenance;
[TASK.json](TASK.json) records scope, selection, overlap and remaining work.

## Open next questions

Can several target covers share source-acquisition feeders without losing
monotone frame compatibility or dirty restoration? Start with Y0 and one
second target, enumerate their common source-frame and relay-frame contacts,
and write a complete two-target word before scaling. The 48-source injection
is reusable information, so summing separate one-target lower bounds is not
valid. The blocker is a globally compatible relay/owner schedule and its full
bill, not another geometric two-cover calculation.

For this exact finite word, native lowering can be checked separately by
compiling its 146 nested transports and verifying phases under the retained
canonical-chart contract. That would settle a local physical obligation, but
would still leave 103 correction rows and all global admission work open.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

kumagi / PR #2353 states the relay-safe monotone model, verifies the
208-lifetime floor and supplies the two-hyperplane handoff. Philippe Van
Velzen's correction screen supplies the original 208 floor and cover
calculation. Rohan Arun / PR #1972 supplies the scalar/frame channel,
Chafik Boukhalfa / PR #1991 its native realization, Adam Gall / PR #1940 the
schedule, Josie Elliston / PR #1071 the fixture, and Ali Romman / PR #1125
the delivery lineage, with PR #968/#717/#446/#595/#620 retained as credited
in the original package notices. Dirty compensation itself is inherited.

Gonzalo Mier / PR #2173, Gareth Davidson / PR #2251, and the subsequent
PR #2345/#2358 prefix work concern different pooled-space questions.
This account's PR #2172 prices cut 2429 and PR #2190 excludes a fixed-room
capture order; neither is the present source-acquisition result. The parallel
private-code relay investigation in discussion #2245 grants original private
signals, which are excluded here. Its question is distinct and its claims
are not used as evidence.

New proof, construction, implementation, checking and writing have substantial
OpenAI Codex (GPT-6 Astra) assistance. No independent human review is claimed.
Apache-2.0; existing source files and notices are unchanged.
