# R439 block 8: ten fewer ADDs using one more payload bit

**Finite circuit construction; no new kappa.** Replacing the tuned PR589
R439 word's phase-B block 8, `B[404:449]` at frame 523, reduces **45 to 40
binary additions**. Its required literal reverse cleanup saves five more:
**24,305 to 24,295 native ADDs**. The complete forward integer transfer matrix
of the block is identical. All 661 input columns, including arbitrary helper
dirt, satisfy the unchanged endpoint contract.

There is a deliberate precision tradeoff. Unlike a reverse-dominated local
rewrite, this replacement increases 50 entries of the block's reverse positive
matrix and decreases seven. The full-word cancellation-free reverse bound grows
from **1,113,070 to 1,228,514**. The forward bound remains **49,347**. The existing
native envelope `64 F^3 B^2` increases from
`9528119495320518471870892800` (93 bits) to
`11607066161648800787038010112` (**94 bits**), still strictly below `2^104`.
No scalar precision charge is dropped or treated as free.

All 661 register frame paths, 439 helpers, 2,911 MOVEs, nine rank-seven COPYs
and nine ERASEs are unchanged. The paid local histogram remains
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, of rank mass **5,129**.
Thus the paid recursive moment is unchanged at every exponent. This saves a
finite scalar constant; it does not establish an improved supplier exponent
or multiplication exponent.

## Reproduce

From the repository root, Python 3.10+ and its standard library:

```sh
python3 -I -B research/r439-block8-integer-factor/verify.py
```

Expected final line:

```text
PASS_R439_BLOCK8_INTEGER_FACTOR gates=45->40 native_adds=24305->24295 columns=661 rank_mass=5129 payload_bits=93->94 controls=10
```

This checks source hashes; exact F2 and integer matrices; all 4,096 local
Boolean inputs; the predecessor's E8, frame, dirty-column and H1–H5 interface
checks; actual exported records with a separate set-valued symbolic interpreter;
COPY/ERASE lifecycles; full positive prefix bounds; the exact certificate; and
ten rejection controls. Acceptance checks remain active under `python3 -O`.

For fresh native C++17 and Boost checks of **both** words:

```sh
python3 -I -B research/r439-block8-integer-factor/native.py
```

Expected: `PASS_R439_BLOCK8_NATIVE words=2 stages=5,9,11 columns=883,1327,1549 bridge_controls=96`.
This compiles the unchanged legality checker and the 5/9/11-stage column checker,
checks every column and all 6/18/24 omitted-bridge controls per word, and compares
native prefix bounds and paid profiles against the Python certificate. Only
elapsed time and the local input pathname are removed from the retained native
receipts. Set `CXX` or `BOOST_INCLUDE` if necessary.

Both commands accept `--output /absolute/new/directory` to retain scratch files;
the directory must not already exist. Without it they use temporary directories.
`--write-certificate` explicitly regenerates only this package's receipt.

The bounded nomination is separately reproducible, taking approximately
30 seconds on the development environment:

```sh
python3 -I -B research/r439-block8-integer-factor/search.py
```

Expected: `PASS_R439_BLOCK8_SEARCH seed=18 trials=5000 identity=333 gates=45->40 strict_candidates=0`.
`search.py --write` regenerates only `WITNESS.json` and `SEARCH.json`.

## Substitution argument and accounting

The twelve local wires, in witness order, are source registers
`[2,4,14,16,18,20,88,90,93,95,103,109]`. Every gate in the replaced contiguous
slice has the same frame. There are no external reads interleaved in this slice.
Let `P(L)` denote the nonnegative integer transfer matrix formed by replacing
XORs by additions. The certificate proves `P(new) = P(old)`; reduction modulo
two therefore proves equality for **every incoming local state**, not only
clean inputs. Literal reversal gives the same inverse over F2. Substituting
this circuit preserves the state at the slice's end and every later target
read. We regenerate all of C as the literal full-frame reverse of z-destination
gates in A followed by B, exactly as required by H4. D, A, scatter and all
other B operations are retained, including dirty compensation and source access.

Every wire follows its original ordered frame path. Although its first touch
inside the slice can move, no earlier instruction in that slice acts on that
wire before its first touch. The incoming climb still acts on the same value,
to the same frame. The symbolic and native checkers validate nestedness and
common-frame access. No helper, frame, COPY, retained total or recursive child
is added; the restoration and access costs are present in the exported word.

A general reverse-domination argument is **not** available for this witness.
Instead we replay every native scalar instruction in both orientations with
nonnegative integer row-sum bounds, including copied-center lifecycles, and
check the predecessor's exact `64 F^3 B^2 < 2^104` obligation. This proves the
finite envelope used by the native checkers, not any unimplemented all-size
precision or tape theorem. The native 5/9/11-stage tests separately check the
signed inverse stage convention and F2 formal columns, including arbitrary dirt.

## Search class, pivot and overlap

OS assignment seed **18** selected the bit track and block `18 mod 10 = 8`.
Starting with the full block's positive matrix, the search repeatedly subtracts
one row from another only when every coordinate stays nonnegative. It chooses
uniformly among allowed ordered pairs, except every third trial first restricts
to sources with maximal row sum. Each subtraction strictly lowers total mass;
a trial ends when no subtraction is possible. A trial yields a circuit only
when the terminal matrix is the identity. Reversing its subtraction list then
constructs the original positive matrix exactly.

The stopping rule is **5,000 trials** with `random.Random(18)`. Exactly **333**
reach identity. The first strict hypothesis additionally required a shorter
circuit whose reverse positive matrix was entrywise dominated by the original;
none of the sampled trajectories met it. One evidence-driven pivot retained
the same domain and seed but admitted reverse growth when the complete native
payload still fits the existing cap. The same 5,000 trajectories produce record
lengths **44 at trial 1165** and **40 at trial 2123** (zero-based). The frozen
witness is the latter. No larger search was used. The search report establishes
sample coverage, not a minimum gate count or impossibility theorem.

This changes the **whole-block integer factorization**, without imposing the
original two-factor boundary or a destination-once restriction. Gautam Gupta's
pending **#844** shortens tuned R439 block 4 with a different, exact fixed-factor
search. Jerry Lin's **#810** changes historical R420 block 8, whose wires and
matrix differ; Yuzhou Wang's **#789** and commdata2338's **#790** are other
historical R420 block factorizations. Sagar Thakrar's **#728** and Ryan Haines'
**#792** change R439 phase-A mini-nodes. Anudeep Adiraju's **#843**
changes the distinct R439 frame-509 block; Aaron Wang's **#848** prices
restored-temporary sharing on A, D and decoder totals. Charles Bethin's **#827** excludes
smaller cleanup *frames* for a fixed prefix, not the scalar gate substitution
here. None of those pending implementations is imported or composed; their
savings are not included in ours. See `CLAIM.md` for the three candidate tasks
and final overlap check.

## Pins, scope and attribution

Base: **`f567884aeb8851b6e794af1184119a3bfbe1e631`**. The selected reviewed
result at that base is PR799 with PR589, conditional
**kappa = 0.001661634653669567**. The bit supplier's reviewed source head is
**`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`**. `SOURCES.json` records exact
SHA-256 and Git blob pins for consumed files and separately labels contextual
sources. Execution depends on the local pinned source bytes, not a live PR.

Only this isolated research package is added. No selected certificate,
existing generator, ledger or `upstream/` file is changed. No complete hosted
parent invoice, global moment/outer assembly, selected cold replay,
repository-wide `make verify`, Lean theorem or remote CI success is claimed.
The all-size compiler, common-label/mutable-source realization, whole-call
hosting, signed decoder, precision/tape and analytic obligations remain inherited.
Finite replay is not a formal proof of the multiplication theorem. Integration
into a selected supplier still requires its full downstream review and replay.

Prepared for **@zeusinsight** with substantial **OpenAI Codex assistance** in
research, implementation, verification and writing. No independent human or
subagent review is claimed. New files are Apache-2.0 under the repository license.

Credit **eumemic** (PR543/555 and the punctured word and independent interface
checker), **DreamingOfClouds** (PR545/589 and PR503/510), **Dylan Crow** (native
record format/exporter and checkers), **mtpsl** (PR691's quad verifier, from which
`verify.py` adapts the matrix, full-word, record and mutation-check structure),
and the full predecessor attribution in
[`e8-bit-p111-tuned/NOTICE.md`](../e8-bit-p111-tuned/NOTICE.md).
This includes Jacob Sussman's E8 unit, Zhihao Chen's interface work, DaysSky's
hosting, and the retained construction and accounting lineage. The current
consuming composition credits Jeremy Kothe and Chafik Boukhalfa and their
predecessors. This contribution claims only the new block witness and evidence.
