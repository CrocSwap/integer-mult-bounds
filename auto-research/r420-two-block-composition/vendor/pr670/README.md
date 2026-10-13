# R420 block 3: 50 to 33 XOR gates, with unchanged paid frame paths

**Finite local circuit improvement; no new kappa or supplier certificate.**
The phase-B block-3 circuit in eumemic's [PR #543](https://github.com/CrocSwap/integer-mult-bounds/pull/543)
R420 word can use **33 binary XOR gates instead of 50**, with exactly the same
ordered output values on its original twelve registers. Replacing its literal
reverse cleanup saves **34 scalar ADDs** in the complete local word.
No helper, COPY, retained total, compensation gate, recursive child, or physical
frame path is added. Both orientations' cancellation-free transfer matrices
are entrywise no larger than the original matrices.

The selected result at base **66849e1475c930fd7732b1a0067ffee7e1e95f60** is
the conditional #626/#622/#623 construction with #543, with
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
Its [actual assembly](../community-k492-audit/pr626/replay/ASSEMBLY.json) is
complex-bound. This package leaves that selection untouched. In particular,
fewer common-frame additions with the same paid rank profile do **not** establish
an improved recursive exponent.

## Reproduce

From the repository root, with Python 3.11 or later:

```sh
python -m pip install -r research/r420-block3-xor/requirements.txt
python -B research/r420-block3-xor/verify.py
```

Expected final line:

```text
PASS_R420_BLOCK3_XOR gates=50->33 saved_with_cleanup=34 columns=660 rank_mass=5112 controls=10
```

The command verifies the frozen result without rerunning the search, and writes
`word.json.gz` plus `verification.json` to a **new, uniquely named** directory
under `build/`. `--output PATH` selects a fresh destination; existing paths are
refused. Input words, predecessor code and previous results are read-only.
The output word is compared by canonical decompressed JSON, not its gzip
container hash. `SOURCES.json` binds all consumed predecessor code/data by
SHA-256 and Git blob ID, with explicit LF normalization for text checkouts.

On Windows, install Python with its `py` launcher and the dependencies above,
then double-click `verify.cmd` for routine verification. Alternatively,
`R420_PYTHON` may select an already installed Python executable. The launcher
needs no code edits and uses the same verifier. Tested on Windows with
Python **3.12.14**, SymPy **1.14.0**, and mpmath **1.3.0**. The independent checker
and search use only the Python standard library; SymPy is used by #543's
inherited exact lattice checker. No packaged executable or GUI is needed for
this fixed mathematical certificate.

An independent invocation (no optimizer, producer or primary-checker imports):

```sh
python -B research/r420-block3-xor/independent.py research/e8-bit-r420/data/bitE8mut-r420.json.gz research/r420-block3-xor/candidate.json
```

It reports `PASS_INDEPENDENT_BLOCK_AND_ALL_DIRTY_INPUT_COLUMNS`. Its optional
`--word PATH` also checks a separately produced full word against its own
reconstruction. Both implementations are AI-assisted; “independent” describes
their algorithms and import separation, not independent human peer review.

## Exact object and evidence

The original half-open range is `B[263:313]`, frame **545** (rank 4), on physical
source registers
`[21,29,37,45,53,62,71,73,81,89,97,105]`.
There are no external reads interleaved within this contiguous block. The
replacement retains the exact physical output assignment, so downstream
needers and target reads require no relabeling or extra source access.
Every other B gate and every D/A/scatter gate is unchanged; C is rebuilt as
the literal reverse of all z-destination gates of A then B, at the full frame.

`candidate.json` contains both circuits and the twelve output row bitmasks.
`CERTIFICATE.json` contains the exact nonnegative matrices, hashes, full-word
checks, paid profile and prefix quantities, recomputed by the verifier.

| Quantity | Original | Replacement |
|---|---:|---:|
| Selected block binary XORs | 50 | 33 |
| B gate records | 837 | 820 |
| C gate records | 2661 | 2644 |
| Complete local scalar ADDs, including multisource gates and scatter | 26916 | 26882 |
| Source / target / dirty-helper columns | 120 / 120 / 420 | unchanged |
| Helpers / retained copies | 420 / 9 | unchanged |
| Local rank mass | 5112 | 5112 |
| Local block + reverse unit-weight maximum | 2431 | 587 |
| Exported local forward prefix bound F | 144651 | 144651 |
| Exported local reverse prefix bound B | 2270064 | 2185964 |
| `64 F^3 B^2` | 998206739997057013039187410944 | 925614833593522808541496863744 |
| Payload bound bits | 100 | 100 |

The last three rows use the **local cohort** convention of the pinned
`export_records.py` and `columns_k.cpp`. Baseline quantities reproduce the
archived #543 `columns_k4.json` receipt exactly. They are not the full hosted
physical invoice. No runtime speedup is inferred from the operation counts.

Every register has the same sequence of physical frames, not merely the same
aggregate rank sum. Including COPY charges, the local paid profile remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. Thus its moment remains
`1320 + 1440*2^p + 60*4^p + 120*5^p + 9*8^p` for all exponents p.
Existing #543 frame/copy/helper expenses have not been omitted or repriced.

## Why the replacement is safe for the stated finite scope

For the twelve-register block, let P and Q be its original and replacement
transfer matrices with **integer addition instead of XOR**. Exact checks give
`0 <= Q <= P` entrywise, and separately give the same inequality for the
literal reversed circuits. Their reductions modulo 2 are identical, with
unchanged row order. Consequently the block's full F2 map is identical for
arbitrary inputs, not just clean helpers or selected examples.

For any nonnegative vector x of entry bounds, `Qx <= Px`. Inside an ADD-only
block every coordinate increases monotonically, so every replacement prefix
is bounded by its replacement endpoint, hence by the original endpoint. This
is a maximum-prefix statement, not a comparison of equal-index intermediate
steps. Unchanged exterior ADD/COPY/ERASE operations are monotone maps on
nonnegative bounds, so endpoint domination propagates through the rest of the
word. Apply the argument at both changed segments, and separately in the
reversed orientation. The block has no internal COPY/ERASE or outside read.
Frame legality and all per-register frame paths are checked separately.

The primary verifier reuses #543's exact root-lattice/frame check, simultaneous
F2 replay, H1–H5 interface checks, and their decomposed conclusion. The second
implementation derives the block independently, uses active-register sets to
propagate **each of all 660 input columns separately**, computes rational frame
ranks independently, and checks its full reconstructed word against the primary
word. Both independently compute the scalar prefixes and frame-path hashes.

Ten negative controls reject: a wrong source fingerprint; a new register;
a singular self XOR; an incorrect endpoint certificate; a dropped gate;
a changed B map with matching cleanup; an F2-correct old cleanup that violates
the **literal-reversal H4 interface**; an illegal line-frame gate; missing
dirty-helper compensation; and an F2-neutral repeated-gate insertion that
increases the positive transfer. The old-cleanup control is deliberately
not described as a scalar counterexample: either equivalent inverse circuit
restores F2 values, but only the matching literal reverse satisfies H4.

## Bounded search and overlap

The operating-system assignment seed was **13**, giving the bit-supplier track;
`13 mod 10 = 3` selects this block. See `CLAIM.json` for the three candidate
tasks, local claim and timing. No pinned coordination issue existed.

The hypothesis was that changing the scalar factorization, while fixing its
ordered outputs, could reduce XOR work without worsening the positive bill.
The nomination uses commuting adjacent transvections and exact adjacent
three-gate replacement by at most two gates. The lookup covers all 132
directed non-self XORs and all 17,424 ordered two-gate pairs on twelve registers.
Each accepted shortening also has forward and reverse entrywise nonnegative
domination. The seeded outer walk completed **50 trials x 400 shuffle attempts
= 20,000 attempts**, accepting 170 shortening steps across trial paths. The
first 33-gate result occurred at zero-based trial 2, step 364. The complete
coverage and improvement trace are in `candidate.json`.

```sh
python -B research/r420-block3-xor/search.py --seed 13 --trials 50 --steps 400 --output NEW-candidate.json
```

This deterministically reproduces the frozen candidate on the tested Python.
The search is bounded and heuristic; it does not enumerate all equivalent
circuits, and 33 is **not** claimed optimal. Verification does not trust the
random walk or require its history.

[PR #661](https://github.com/CrocSwap/integer-mult-bounds/pull/661) studies
simultaneous frame reassignment with fixed scalar gates/order and explicitly
excludes resynthesis. This contribution changes that excluded mechanism;
it does not reopen the closed fixed-order frame search. #661 is not a code or
proof dependency. [PR #589](https://github.com/CrocSwap/integer-mult-bounds/pull/589)
changes frame transports on the different punctured R439 word. Decoder-floor
work in #620/#631 concerns another object. Final live overlap checks and test
outcomes are recorded in `VALIDATION.json`.

## Scope, credit and handoff

This result certifies a finite scalar circuit and local frame/prefix accounting.
It is not an integer-ring endpoint identity: XOR-circuit equivalence is over F2.
The positive matrices bound the absolute-value signed lift; they do not prove
its signed endpoint. Full five/nine/eleven-stage C++ replay, hosted physical
invoices, the supplier assembly and the repository-wide `make verify` were
not rerun for this standalone addition. No replacement is installed into the
selected supplier. Applying it there would require the corresponding full
replays and binding updates by a follow-up contribution.

Inherited all-size compiler, common-label/mutable-basis realization, pooled
hosting, normalized residual, precision/tape/exact recovery and analytic
transfer assumptions remain. This is not a complete multiplication theorem,
a Lean proof, a general lower bound, or a claim that a stronger kappa exists.

The predecessor circuit, plan, realization objective and scalar-interface lemma
are **eumemic's #543**, pinned to reviewed head
`2065fe4f72a914d907f1046603f5a36f17018535`, building on #493.
Credit is retained for Dylan Crow's #370 E8 word/exporter, DreamingOfClouds'
#503/#510 construction/pricing, Zhihao Chen's #425 interface, Chafik Boukhalfa's
#472 common-label realization/emitter, DaysSky's #381 bridged-column checker,
and the full lineage listed in
[the original README](../e8-bit-r420/README.md) and
[selected maintainer review](../../docs/research/community-k492-review.md).

Prepared for GitHub contributor **yongjae321** with substantial **OpenAI Codex**
assistance, including separate workers for nomination, independent checking and
adversarial review. New files are under the repository's **Apache-2.0** license.
