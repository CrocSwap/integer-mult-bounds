# R439 block 4: 41 to 31 additions, with exact factor minima

**Finite bit-circuit construction; no new kappa.** Replace phase-B block 4 of
DreamingOfClouds' PR589 tuned R439 word on eumemic's PR555 construction. The
block uses the same twelve registers and frame 520. Its 41 additions become 31;
its required literal reverse cleanup saves ten more. Complete local additions
fall **24,305 to 24,285**. No scratch register, source-access operation, copy,
frame transition or recursive child is added.

The two fixed positive-integer factors have minimum costs **17 and 14** within
the destination-once class defined below. This does **not** prove unrestricted
XOR optimality, optimality of the factor split, or a better multiplication
exponent. It does not certify composition with another pending circuit PR.

## Reproduce

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python -I -B research/r439-block4-schedule/verify.py
```

Expected final line:

```text
PASS_R439_BLOCK4_SCHEDULE gates=41->31 ADDs=24305->24285 columns=661 factor_minima=17+14 controls=13 rank_mass=5129 kappa=not_recomputed
```

The verifier imports the pinned owning geometry/interface checker, but no
discovery code. It checks input SHA-256 pins, independently enumerates the
factor class, checks every integer transfer entry, reconstructs the word and
record stream, and compares its complete report with `CERTIFICATE.json`.
`--out NEW_DIRECTORY` additionally exports the candidate word, original and
candidate native record streams, and the report. Compressed output is compared
by canonical decompressed content, not by a regenerated gzip container hash.

For the unchanged C++ legality and five/nine/eleven-stage checkers:

```sh
python -B research/r439-block4-schedule/native.py \
  --work /absolute/fresh/output --cxx c++ --boost-include /usr/include
```

This needs C++17 and Boost. MSVC is supported with `--cxx cl.exe` from an x64
developer shell. The script checks both words, compares its independent
record emitter byte for byte with the owning exporter, checks all bridge
controls and prefix bounds, and compares the receipts with
`NATIVE-CERTIFICATE.json`. Only elapsed seconds and the output-directory path
are removed from the native receipts. See `VALIDATION.md` for actual execution.

## Exact object and source pins

Experimental base: **`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`**.
Assignment seed: **04**, drawn with Windows cryptographic OS randomness using
unbiased UInt32 rejection sampling. The seed chooses block `4 mod 10 = 4`.
The initial three candidates and scope are in `CLAIM.json`.

At that base the selected result was PR741 with PR589, conditional
`kappa = 0.001661202643272239`. During this experiment main advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting PR799 with the same PR589
bit supplier, conditional `kappa = 0.001661634653669567`. All nine consumed
source files were compared byte for byte against that updated main and are
unchanged. The moving selected record is context, not a replay dependency.

`SOURCES.json` pins every consumed repository source/checker/header by SHA-256.
The reviewed PR589 head is `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
The input is `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`;
no source package is overwritten. Neither `upstream/` nor the selected frontier
is modified.

The exact slice is `B[242:283]` (Python half-open indices). Its ordered registers
are `[21,26,36,44,51,55,64,71,80,84,94,102]`. These are all source registers in
the 111-port word. `CANDIDATE.json` gives every replacement operation as
`[destination_index, source_index]` in that order. The two original factors are
the first 20 and final 21 operations of the slice; the replacements have 17 and
14 operations. No permutation of output registers is allowed.

## Identity, restoration, and cost

Write an addition as `E(a,b) = I + e_a e_b^T`. The verifier propagates each of
the twelve integer basis columns through both old and new factors. Their two
ordered integer matrices agree in every entry. Thus the forward block has the
same output for every input over every commutative coefficient ring, and in
particular over F2, including arbitrary values inherited from dirty helpers.
There are no reads from outside the block between these consecutive operations.

Cleanup is rebuilt as the literal reverse of all source/helper writes in
`A` followed by `B`, at the full frame. Each F2 addition is its own inverse,
so the new cleanup restores exactly the same arbitrary source/helper contents.
The original owning checker separately confirms H1-H5, the raw interface's
`U`, `J`, and `K` conclusions, and `C = U^-1`. A stale-cleanup negative control
is deliberately F2-correct but rejected because it violates literal H4.

The **positive**, cancellation-free matrix for the reversed replacement is
entrywise no larger than the old reversed matrix: 33 entries decrease, its
entry sum drops 368 to 118, and its largest row sum drops 155 to 39. For any
nonnegative incoming norm vector this bounds the new reversed block by the old
one. Inside either block, positive additions only increase coordinates, so
every prefix is bounded by its endpoint. The surrounding positive operations
and copied-center operations are monotone. This proves that replacing the
forward block and its literal cleanup cannot increase the complete forward or
reverse cancellation-free prefix maximum. The exact finite replays also check
the actual resulting maxima.

This is **not** a claim that the complete positive integer word is unchanged:
the cleanup's positive matrix changes. The complete scalar endpoint replay is
over F2; the inherited signed decoder and physical lift remain separate
obligations, as in the owning checker's scope.

| Complete local quantity | Original | Candidate |
|---|---:|---:|
| Phase-B block additions | 41 | 31 |
| Required reverse block additions | 41 | 31 |
| All scalar additions, including scatter and cleanup | 24,305 | 24,285 |
| Native records | 27,234 | 27,214 |
| MOVEs | 2,911 | 2,911 |
| Helpers | 439 | 439 |
| Rank-seven COPY / ERASE pairs | 9 | 9 |
| Paid rank mass | 5,129 | 5,129 |
| Positive forward prefix | 49,347 | 49,347 |
| Positive reverse prefix | 1,113,070 | 1,084,714 |
| Local payload bits | 93 | 93 |

All 661 individual frame paths agree. The complete paid histogram remains
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`. Consequently the local
paid moment `sum_r H[r] * r^(1-a)` is identical for every exponent `a`.
Every access and restoration is included in the table. The payload check is
the inherited exact inequality `64 * forward^3 * reverse^2 < 2^104`.

This scalar saving alone does not lower the recursive moment. A new global
hosted program, physical invoice, supplier binding, or outer assembly has not
been certified here, and no transported bit saving or new kappa is asserted.
The nine-stage/eleven-stage native column checks do not replace those checks.

## Scoped minimum and completed search coverage

Fix either original positive factor `F`. A permitted schedule has these rules:

1. Wires start as the twelve standard basis vectors; no additional wires.
2. Each destination is finalized once, in one contiguous batch of additions.
3. A donor is its original unit vector if unfinalized, or its exact row of `F`
   if finalized. A finalized wire is never written again within this factor.
4. Only positive coefficient-one additions are used; exact integer equality
   to `F` is required. The two factors retain their boundary.

For a set `S` of finalized destinations, every register value is therefore
determined by `S`. To finalize `d` one must sum donor rows to `F[d]-e_d`.
These target vectors have entries zero or one. Repeated donors or overlapping
nonzero supports cannot occur in a valid positive representation. Every legal
batch is consequently a subset of at most eleven donors, and its cost is the
subset cardinality. Conversely each subset with the required exact sum is a
legal batch. Adding `d` to `S` gives an acyclic 4,096-state graph.

`factor_search.py` finds shortest paths by forward dynamic programming, using
disjoint-support cover tables. `verify.py` uses independent exhaustive integer
subset sums encoded in base 16 and backward Bellman recursion. At most eleven
binary donors are summed, so no base-16 digit carry can occur. Its terminal
cost is zero and its edge recurrence is

`D(S) = min_(d not in S) [minimum_subset_cost(S,d) + D(S union {d})]`.

An infeasible edge has infinite cost. Induction on the number of unfinalized
wires proves this recurrence covers exactly the stated class. Both complete
tables establish minima 17 and 14, attained by the frozen circuit. The replay
checks **8,192 states**, **49,152 state/destination pairs**, and **39,168 feasible
edges** (20,224 and 18,944). Hashes of the independent backward tables are in
`CERTIFICATE.json`; the tables are recomputed, not trusted as input.

```sh
python -B research/r439-block4-schedule/factor_search.py --output NEW-CANDIDATE.json
```

This deterministically regenerates `CANDIDATE.json`. There is no timeout or
random stopping condition in this exhaustive fixed-factor pass.

Before this pivot, a seed-4 randomized two-sided nonnegative factor-stripping
search completed its full **2,000-trial** budget on the same block. Each trial
stopped on identity, a stuck reduction, or the 41-step bound. Twenty trials
reached identity below that bound; none also had a dominated reverse matrix.
The result is a failed bounded search, **not an impossibility theorem**.
`search.py` reproduces that search; its stopping rule was the first dominated
candidate with at most 30 additions, or 2,000 trials. The pivot to exact fixed
factors changes the search class and yields a 31-addition witness. It does not
reopen a previously closed search with a larger random budget.

## Related work and attribution

- **eumemic**, PR543 and PR555: R420 carrier skeleton, punctured R439 word,
  low-norm block realization, and the owning interleaved interface checker.
- **DreamingOfClouds**, PR545 and PR589: punctured-star supplier and the two
  phase-A transports retained unchanged here; PR503/510 nine-stage lineage.
- **Dylan Crow** and retained contributors: bitE8 format, record exporter and
  native checker lineage; **DaysSky**: parameterized bridged-stage replay.
- **Yuzhou Wang, PR789** (`d1634f3b316f2c3a1bb5f93a6117c8ebab9ab011`): related
  exact fixed-factor scheduling on historical R420 block 7. The method here is
  an application to a distinct R439 matrix, not a priority claim for that method.
  Related positive-factor work: **commdata2338, PR790**, R420 block 9, and
  **Jerry Lin, PR810**, R420 block 8. No pending implementation is imported.
- **Sagar Thakrar, PR728**, and **Ryan Haines, PR792** optimize R439 phase-A
  mini-nodes. This slice is in phase B; their circuits are not combined here.
- **yuj1r0, PR661** fixes the R420 gate order for frame optimization;
  **Charles Bethin, PR827** bounds cleanup frame cost and explicitly leaves
  scalar savings open. Neither closes the gate-list change made here.
- **Cody Harris, PR761** concerns the fixed P111 decoder pairing floor; the
  decoder, nine retained totals, and copying cost are unchanged here.

The experiment was prepared by **Gautam Gupta (@gautamgpt1)** with substantial
**OpenAI Codex assistance** in analysis, code, verification and writing.
Apache-2.0, under the repository license. Original files/notices are retained;
no independent human peer review is claimed. The inherited all-size compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
signed decoder and analytic-transfer hypotheses remain. This finite result is
not a formal verification of the full integer multiplication theorem.
