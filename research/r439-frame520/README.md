# R439 frame 520: a 29-ADD whole-block factorization

**Finite bit-supplier construction; no new kappa.** Replace the selected PR589
R439 word's phase-B frame-520 block, `B[242:283]`, with 29 additions instead of
41. Its mandatory literal reverse cleanup saves another 12: the complete local
word falls from **24,305 to 24,281 ADDs**. This is **four fewer complete ADDs than
Gautam Gupta's prior PR844**, which already achieved 31 additions in this block.

All 12 ordered registers, 439 dirty helpers, 661 register frame paths, nine
rank-seven copies, the D compensation, scatter and paid rank mass 5,129 remain
unchanged. No temporary, source-access operation, restoration or recursive child
is omitted. The full source H1–H5 interface passes unchanged.

## Reproduce

From the repository root, with Python 3.11+ and no external Python packages:

```sh
python3 -I -B research/r439-frame520/verify.py
```

Expected:

```text
PASS_R439_FRAME520 block=41->29 ADDs=24305->24281 columns=661 rank_mass=5129 controls=9 no_new_kappa
```

The command creates a fresh temporary output directory and prints its path. It
checks the frozen candidate without importing or running the search, recreates
both complete words, and writes the exact deterministic `receipt.json`.
Compare that JSON with [RECEIPT.json](RECEIPT.json). Compressed outputs are
compared through **all decoded fields**, not environment-dependent gzip bytes.

For the unchanged C++17/Boost native checks, run both commands using a new path:

```sh
python3 -I -B research/r439-frame520/verify.py --out /tmp/frame520-replay
BOOST_INCLUDE=/path/to/boost-headers python3 -B research/r439-frame520/native.py \
  --word /tmp/frame520-replay/replacement.json.gz --out /tmp/frame520-replay \
  --expected-saving 24
```

Expected native status: `PASS_R439_FRAME520_NATIVE_REPLAY saved=24`.
`BOOST_INCLUDE` is the directory containing `boost/`. Native checking deliberately
refuses Python `-O` because the inherited exporter uses assertions. The local
verifier and package tests also pass under optimized Python.

## Exact object, proof and complete cost

The ordered registers are
`[21,26,36,44,51,55,64,71,80,84,94,102]`, all source registers. Every replacement
gate is an in-place `destination += source` at existing frame 520. The 29 literal
operations and three exact 12-by-12 matrices are in [candidate.json](candidate.json).

Let `E_ds = I + e_ds`, with distinct destination `d` and source `s`. The verifier
independently evaluates each input column of the old and new products over the
integers and obtains the same **ordered** matrix. Consequently these products
agree over every commutative coefficient ring, including F2. This is an exact
finite matrix identity, not a finite-sampling argument about the all-size theorem.
The signed reverse products also agree, using `E_ds^-1 = I - e_ds`.

For the bit word, the entire B block acts only on source registers. Replacing
its F2 map leaves the raw target/source/helper map unchanged. C is rebuilt as
the literal reverse of **every** source/helper gate in A followed by B, at the
full frame. Thus H1, H2, H3 and H5 retain their old meaning, and H4 holds for the
new gate list. The unchanged predecessor checker verifies all hypotheses and
U/J/K/C conclusions; a separate set-valued interpreter checks every arbitrary
input column, including all dirty helpers and incoming targets.

| Complete local quantity | PR589 baseline | New word |
|---|---:|---:|
| A ADDs | 2,130 | 2,130 |
| B ADDs | 934 | 922 |
| C ADDs, including full cleanup | 2,629 | 2,617 |
| D ADDs | 18,085 | 18,085 |
| Scatter ADDs | 527 | 527 |
| Total ADDs | **24,305** | **24,281** |
| COPY / ERASE | 9 / 9 | 9 / 9 |
| Paid rank mass | 5,129 | 5,129 |
| Forward positive prefix | 49,347 | 49,347 |
| Reverse positive prefix | 1,113,070 | 1,082,278 |
| Local payload bits / cap | 93 / 104 | 93 / 104 |

The paid profile is `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` in both words.
Every register visits exactly the same frames in the same order; the global
interleaving of independent MOVE records can change. This preserves the local
recursive-call inventory. At 5/9/11 stages, the local ADD reduction is respectively
120/216/264, with bridge and copy counts unchanged. These counts are also checked
by the native receipts; they are not a reconstructed whole-hosting invoice.

The new block's **positive reversed** matrix is entrywise bounded by the original,
with 34 strict decreases. Positive additions are monotone, so intermediate
coordinates cannot exceed the terminal coordinates within such a block. Both
full-word orientations are also literally replayed, including fresh copies and
erasures. The source payload formula `64 F^3 R^2 < 2^104` gives
`9008239015450399508063048448`, still 93 bits. The checker does not infer reverse
domination from F2 or forward equality.

## Prior work and what is new

- **Gautam Gupta, PR844**, head `dee2c7d506312d2e555a59fb0916c161b4e64028`,
  previously found a 31-ADD circuit, with exact minima 17+14 for the two fixed
  factors separated after original gate 20. This closed, unmerged contribution
  remains valid predecessor evidence. Its untouched [candidate](inputs/pr844-CANDIDATE.json)
  is retained and source-pinned. We replay its identity and full prefix too.
- The new mixed left/right factorization permits partial rows to be reused
  between factor boundaries. None of its prefixes equals the original first
  factor. It saves two more B ADDs and two more C ADDs. It does **not** improve
  PR844's theorem for its fixed-factor class.
- PR844 also reported a failed 2,000-trajectory mixed-factor search before its
  fixed-factor pivot. We do not claim that the feasible mixed-factor class is new.
  The added search mechanism is an exact admissibility guard: every diagonal
  entry must remain at least one. Subtractions never increase an entry, so a
  state with a diagonal entry below one can never reach the identity. PR844's
  sampler admitted those dead branches. The new sampler removes them before
  choosing a move and uses six priority families; its successful 1,833-trajectory
  run is not merely a larger run of the earlier sampler. The new contribution
  is the checked 29-gate witness, not a claim that either search is exhaustive.
- **Aaron Wang (@navinor), PR891**, head `645fb93fcd21b86aca7e2bf81582be5c62411b27`,
  records a whole-block single-write obstruction at physical register 84. Here
  destinations can be written repeatedly, so this is a different search class.
- **Gareth Davidson, PR904**, head `883a0bdf7792693e57c16be660824b57aacfbe05`,
  supplies one overlapping three-wire rewrite (`B[278:281]`) saving one B ADD.
  It is reproduced separately in the verifier; no combined saving is claimed.
- Open proposals on frames 506/507/508/509/519/521/522/523/524 are distinct
  objects. No composition with them or with target-compensation PR915 is certified.

Versus PR844, six positive-reverse matrix entries decrease and **two increase**;
entrywise domination is only claimed against the original PR589 block. Complete
reverse bounds are 1,084,714 for PR844 and 1,082,278 here. This distinction is
retained in the machine receipt.

## Bounded search

Assignment seed **05** was drawn once using OS randomness. The nomination uses
`random.Random(5)`, at most 5,000 trajectories, six deterministic priority families,
and exact nonnegative row/column subtractions preserving positive diagonal entries.
Each step removes a left or right elementary factor; at identity the factors
reconstruct the original map. More than 40 gates is outside the search domain.

The stopping rule was the first strict original-block improvement whose reverse
positive matrix is entrywise bounded by the original. It stopped after **1,833
trajectories**, with **372** exact shorter factorizations, selecting zero-based
attempt 1,832. These are trajectories, not unique circuits or exhaustive class
coverage. No optimum, impossibility result, or search beyond that stopping point
is claimed. The search uses floating-point priorities only for nomination; all
acceptance and verification arithmetic is exact.

```sh
python3 -I -B research/r439-frame520/search.py --output /tmp/frame520-candidate.json
```

The recorded environment reproduces `candidate.json` byte-for-byte. Mathematical
verification does not depend on reproducing floating-point search ordering.

## Scope and pins

Research base: **`91a2094f2e022930069e8cfdc810a3ea1b81cd09`**. The accepted record
at this base is PR799 with PR589 on PR555, conditional
κ = **0.001661634653669567**. Its complex supplier is binding:
`b=0.001664400278850482327913 < c=0.001733427039589844234749`.
This finite ADD reduction changes neither the local paid profile nor the copied
information, so no new exponent or new selected bound is inferred.

[SOURCE.json](SOURCE.json) pins the exact supplier, original review, predecessor
certificate and relevant source files. [native-source-pins.json](native-source-pins.json)
pins the unchanged exporter/native dependency closure.
[VALIDATION.md](VALIDATION.md) records executed checks and their limits.

The full changed-word hosted reconstruction, complete recursive invoice and
outer assembly have not been rerun. Acceptance into the selected supplier remains
an integration obligation. All inherited all-size/compiler, common-label and
mutable-source realization, whole-call hosting, precision/tape and analytic
assumptions remain. This is not a formal proof of the multiplication theorem.
The repository-wide `make verify` and selected cold replay were not run for this
isolated research addition. No `upstream/` or selected-frontier file is changed.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI Codex
assistance** in search, mathematical analysis, implementation, documentation and
scoped agent review. No independent human review is claimed. New work is
Apache-2.0; see [NOTICE.md](NOTICE.md) for predecessor attribution.
