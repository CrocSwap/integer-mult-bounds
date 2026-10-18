# Historical bit R480: Q-node6 and all eight Q-node2/5/6 compositions

**Finite bit-circuit construction and composition certificate; no new κ.**
Q-node6 of the historical PR503/510 bit word has a 43-XOR replacement for
its 51-XOR program. Its eight saved operations also disappear from the required
literal reverse cleanup, saving **16 complete ADDs**. Composing it with
ToikY's PR1003 Q-node2 and martinxxx9's PR1089 Q-node5 circuits saves **54 ADDs**:
**33,958 → 33,904**. Of these, **38 belong to the predecessors**.

This is the historical **bit** R480 word, not the current complex provider
also called R480. At the exact research base
`410026dc5513b87db92ae98571d1d5984c69a983`, the selected conditional saving is
`836330098538459/500000000000000000 = 0.001672660197076918`, from PR1094,
with the unchanged PR589/555 bit supplier. The complex side binds.
This package changes neither selected supplier nor the selected exponent.

## Reproduce

From the repository root, Python 3.11+ and its standard library:

```sh
python3 -I -B research/r480-qnode6-composition/verify.py --replay-search
```

Expected last line:

```text
PASS_R480_QNODE6_COMPOSITION Q6=51->43 ADDs=33958->33904 subsets=8 columns=720 controls=179 no_new_kappa
```

The command replays all 1,000 search trajectories, all 4,096 local inputs and
inverses of each of the three replacement circuits, every complete dirty-input
column of every subset, original H1–H5 and PR425 checks, the exact unchanged
record exporter, and 5/9/11-stage Boolean schedules. It compares every field
of `CERTIFICATE.json`; source bytes and Git blob identities are checked first.
`-O` is supported: new checks use explicit exceptions and inherited
assertion-based checkers run in separate ordinary isolated interpreters.

To include unchanged C++17 legality and formal-column checkers for all eight
subsets, use:

```sh
python3 -I -B research/r480-qnode6-composition/verify.py --replay-search --native
```

This needs a C++17 compiler and Boost headers. Set `CXX` and `BOOST_INCLUDE`
when they are not in the usual locations. The additional marker is
`PASS_R480_QNODE6_NATIVE subsets=8 stages=5,9,11 bridge_controls=384`.
`NATIVE.json` retains the native receipts, excluding only timing and temporary
input path fields. With `--output /absolute/new/directory`, all constructed
words, raw records, logs and native receipts are retained. Existing output
directories are refused. Gzip output is compared by its full canonical JSON
content, not by compressor-dependent container bytes.

## Exact result and complete charge

Bits 0, 1 and 2 of the subset mask select nodes 2, 5 and 6 respectively.
Every row below is reconstructed and checked, including the empty subset.

| Nodes replaced | Complete ADDs | Reverse positive bound B |
|---|---:|---:|
| None | 33,958 | 3,751,204 |
| 2 | 33,940 | 3,682,548 |
| 5 | 33,938 | 3,714,396 |
| 2, 5 | 33,920 | 3,645,740 |
| 6 | 33,942 | 3,716,830 |
| 2, 6 | 33,924 | 3,681,010 |
| 5, 6 | 33,922 | 3,680,022 |
| 2, 5, 6 | **33,904** | **3,638,746** |

All eight have forward bound **F = 176,135**, and their exact complete local
positive-prefix bill `64 F^3 B^2` has bit length **102**, below the strict
`2^104` ceiling. The combined bill is exactly
`4630420660642035956595446624000`; the baseline is
`4921056267806722187755121024000`. No floating-point acceptance is used.
Precision effects are not additive: Q-node6 reduces B by 34,374 alone,
but only 6,994 after both predecessors. The subset certificate measures these
interactions instead of summing independent precision savings.

| Complete resource | Original | All three |
|---|---:|---:|
| A ADDs | 3,246 | 3,219 |
| B ADDs | 600 | 600 |
| Literal cleanup C ADDs | 3,246 | 3,219 |
| Dirt compensation D ADDs | 26,298 | 26,298 |
| Scatter ADDs | 568 | 568 |
| Exported records | 36,916 | 36,862 |
| Persistent registers / dirty helpers | 720 / 480 | 720 / 480 |
| Nested MOVEs | 2,940 | 2,940 |
| COPY/ERASE pairs, each of rank eight | 9 | 9 |
| Paid recursive rank mass | 5,592 | 5,592 |

Every persistent register's ordered frame path agrees. The paid histogram is
`{1:1200, 2:1440, 4:180, 6:120, 8:9}` throughout. All source access, temporary
reuse, cleanup, COPY/ERASE and frame transitions in the emitted program are
included. No helper initialization, permutation repair or restoration is free.
The complete 5/9/11-stage schedules save respectively **270/486/594 ADDs**,
with their bridge bills unchanged. This is an instruction count, not a
measured runtime improvement or a newly priced hosted supplier.

## Why the substitution and composition work

The frozen Q-node6 is phase A, frame **488**, original slice **[2460,2511)**,
on physical registers
`[11,14,34,36,41,44,83,86,91,93,113,116]`.
It and the replacement use only elementary binary additions among those
twelve registers. Exhaustively checking all `2^12` inputs establishes the
same ordered Boolean output map, including arbitrary dirty values; no output
permutation is ignored. Equivalently, the maps agree as linear maps over F2.
The source and destination frames are preserved by the actual emitted records.

The other two substitutions occupy disjoint original slices, frames and
register sets. Replacing each interval by an equal map preserves the complete
phase-A Boolean operator by ordinary composition, without assuming zero
workspace. B, D and the scatter remain unchanged. C is rebuilt as the literal
reverse of all source/helper writes of A+B at the full frame. Each elementary
binary addition is an involution, so the unchanged H1–H5 interface applies.
The exact source/helper restoration and target addition are independently
replayed on every one of the 720 persistent input columns.

Boolean equivalence does **not** imply equal positive integer transfer.
Accordingly, all eight complete chronological positive bounds are recomputed.
The stored circuit preserves the F2 map; equality to the old integer matrix
and arbitrary signed-integer endpoint equality are not claimed.
The finite frame, scalar, precision and schedule checks do not prove the
all-size multiplication theorem.

## Bounded search and predecessor relation

The OS assignment seed was **6**, drawn once. `TASK.json` records three
candidate tasks, the local claim, domain, stopping rule and overlap limits.
The experiment fixes Q-node6's twelve physical outputs and uses exactly
**1,000** trajectories with `random.Random(2026101406)`.
The unchanged synthesis algorithm is imported from **martinxxx9's PR1089**:
two-sided Boolean elimination, randomized equal-score choices and fully
charged three-XOR swaps for permutation repair. The new object binding is
explicit; no new synthesis algorithm is claimed.

Candidate order is gate count, then the largest exact complete payload over
the four Q-node2/5 backgrounds, then lexicographic gate order. Candidates
longer than the incumbent cannot win and are not fully repriced. The 1,000
trajectories yield 69 programs shorter than 51; four possible incumbents are
priced in all four backgrounds and all four pass. Trial **625** supplies the
unique 43-gate program encountered. `CANDIDATE.json` contains the full
gate-count histogram, fixed output matrix and literal winning program.
This is a bounded heuristic result, **not a minimum circuit claim**.

ToikY's **PR1003**, reviewed head
`b0eda846c34413dabd1e75402b8ad730f8940ff2`, supplies node 2 (52 → 43).
martinxxx9's **PR1089**, reviewed head
`9f33d4d10e59a7575d28378e63c033a4b0c13d3f`, supplies node 5 (51 → 41),
the search routine and the reusable finite replay functions.
`SOURCES.json` pins the exact retained dependency bytes and Git blob IDs.
Existing source packages are imported unchanged. The new evidence is the
node-6 witness and **all eight complete compositions**, including native
precision and frame admission. It does not claim priority for resynthesis,
dirty-state substitution, or complete-prefix admission.

## Controls and limits

The 179 Python controls reject every single-ADD omission from each of the
three replacements (127), missing dirt compensation, illegal frame descent,
stale cleanup and precision overflow, plus all 48 bridge omissions from the
combined 5/9/11-stage schedules. Stale cleanup and the precision-overflow word
are deliberately checked to be endpoint-valid first: their failures concern
the literal interface/accounting and the complete precision cap respectively.
The C++ runs reject 384 bridge omissions over all eight subsets.

No hosted-parent invoice or new hosting allocation is supplied. All-size
compilation, common-label/mutable-source realization, whole-call hosting,
uniform precision/tape and analytic transfer remain inherited assumptions.
No selected-frontier cold replay, Lean proof or remote CI pass is claimed.
The selected certificate, frozen predecessors and `upstream/` are unchanged.

## Open next questions

Could different fixed-output programs give a better **joint** precision bill
than selecting each node alone? The subset table shows why this matters:
precision interactions are not additive. A bounded first step would retain
the Pareto sets of existing node-2/5/6 searches and compare their combinations
under the same complete guard. This package retains one node-2 and one node-5
program, so it does not establish that wider result or global optimality.
A new hosting invoice would be required before using a changed word as a
fully adopted supplier.

## Attribution

Prepared for **@CubeJerry**, with substantial **OpenAI Codex** assistance in
research, implementation, checking and writing. No independent human or
delegated-agent review is claimed. New work is Apache-2.0.

Credit ToikY and martinxxx9 for the imported circuits and verifier/search
components; eumemic for PR493's mutable-source skeleton; DreamingOfClouds for
PR503/510 and the R480 totals/hosting; Dylan Crow / utcorvusvolat-dotcom for
the original record/export and cohort contracts; DaysSky for the bridged
schedule; Zhihao Chen for PR425's scalar interface; and the E8 lineage beginning
with Jacob Sussman. The original packages retain their notices, licenses and
AI disclosures, including Anthropic Claude assistance.
