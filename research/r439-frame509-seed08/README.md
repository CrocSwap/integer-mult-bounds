# R439 frame 509: 31 additions become 21

**Finite bit-circuit construction; no new kappa.** Replace the selected PR589
word's phase-B block `B[283:314]`, at frame 509, by a 21-addition factorization
of its exact integer map. The original has 31 additions. Charging the required
literal reverse cleanup gives **24,305 -> 24,285 complete local ADDs**.
Anudeep Adiraju's earlier [PR843](https://github.com/CrocSwap/integer-mult-bounds/pull/843)
uses 26 additions for this block; this candidate saves **10 further complete
local ADDs**, independently checked against that submission's pinned recipe.

| Complete local quantity | PR589 | Candidate |
|---|---:|---:|
| Frame-509 additions | 31 | 21 |
| Corresponding cleanup additions | 31 | 21 |
| All ADD records, including D and scatter | 24,305 | 24,285 |
| All exported records | 27,234 | 27,214 |
| Frame moves | 2,911 | 2,911 |
| Helpers / rank-seven copies | 439 / 9 | 439 / 9 |
| Paid rank mass | 5,129 | 5,129 |
| Forward positive prefix | 49,347 | 49,347 |
| Reverse positive prefix | 1,113,070 | 1,106,918 |
| Native payload bits, cap 104 | 93 | 93 |

The paid histogram remains
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. Every physical register retains
its ordered frame path. No new wire, helper initialization, source-access
operation, COPY, frame change or recursive child is introduced. Restoration
is charged. The complete 5/9/11-stage words save **100 / 180 / 220 ADDs**;
bridge additions and copy counts agree with the baseline.

## Reproduce

From the repository root, Python 3.11+, C++17 and Boost headers suffice:

```sh
python3 -I -B research/r439-frame509-seed08/native.py --replay-search
```

Expected final line:

```text
PASS_R439_FRAME509_NATIVE words=2 columns=883/1327/1549 bridge_controls=96 five_stage_regression=PASS
```

This command reproduces all 12,000 search trials and compares every candidate
field, checks the integer columns and all 2,048 Boolean inputs independently of
the search, replays the original and candidate local words, runs the unchanged
E8/frame/661-column H1-H5 interface checker, and compiles fresh unchanged native
legality and 5/9/11-stage checkers. All deterministic receipt fields agree with
`EXPECTED.json` and `NATIVE.json`. The native program logs the search output in
`python.log` when an output directory is retained.

Use `--output /absolute/new/path` to retain generated words, records, native
binaries, logs and environment details. Existing destinations are refused.
`CXX` and `BOOST_INCLUDE` select the compiler and Boost include directory;
the defaults are `c++` and `/usr/include`. Regenerated gzip words are evidence
containers, while verification compares their exact maps, fields and records.
The immutable source archive is byte-pinned in `SOURCES.json`.

For the standard-library local check and package failure controls:

```sh
python3 -I -B research/r439-frame509-seed08/verify.py
python3 -I -B research/r439-frame509-seed08/test_package.py
```

Expected markers are `PASS_R439_FRAME509_FACTOR gates=31->21
ADDs=24305->24285 columns=661 controls=11 rank_mass=5129 no_new_kappa` and
`PASS_R439_FRAME509_PACKAGE relocated_optimized_replay=PASS controls=11`.
The package test uses a minimal relocated tree with spaces in its path, runs
under optimized Python, and checks source/recipe/receipt faults, typed JSON,
duplicate keys and preservation of existing output. Explicit
`--write-expected` options are for developing receipts; ordinary reproduction
does not regenerate committed files.

## Exact object and mechanism

The source word is
`research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`, SHA-256
`e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
The eleven registers, in matrix order, are
`[17,22,33,38,50,60,67,77,87,92,468]`. Register 468 is a dirty helper;
its input is arbitrary. `CANDIDATE.json` lists all 21 gates at frame 509.

The new schedule uses the existing source registers as temporary accumulated
donors while preserving every final integer output. For example, it first
adds register 67 into 50, so the update of 87 can read their sum in one gate.
Later it accumulates 87 into 33 and then 33 into 17, reusing these evolving
donors in several destinations. The independent unit-column calculation
checks the complete operator, including the helper output and repeated writes.
Equality over Z establishes equality after reduction over F2 on arbitrary
dirty inputs. No zero scratch or cancellation of positive coefficients is
assumed. [PROOF.md](PROOF.md) gives the splice and precision argument.

## Bounded experiment and prior work

Exact base: **`bbc600db2fc15007b7c914f4f2b2ed55fa909c87`**. The selected
conditional result there is **`1661960547713947/10^18`**, PR942's T37
composition, with unchanged PR589 on PR555. That selection is not edited.
OS assignment seed **8** selects this bit-supplier track and frame 509 among
the three alternatives recorded in `CLAIM.json`. There was no pinned sprint
coordination issue; the claim was recorded locally after checking open PRs.

The domain is exactly this eleven-wire integer operator. Starting from its
matrix, 12,000 seeded trajectories try diagonal-preserving nonnegative row
and column subtraction. Repeated destination writes are allowed. Each trial
stops at identity, no eligible subtraction, or the incumbent gate count.
It reaches identity in 22 trials; all 22 pass reversed positive domination.
There is one dead end and 11,977 incumbent cutoffs. Improvements to 22 and 21
additions occur at trials 0 and 44. One completed run is the stopping rule;
there is no rescan, further seed sweep or claim of an optimum.

The bidirectional factorization method follows martin Rv's PR884 frame-521
search. This is a different operator and extends the explored class beyond
PR843's single-hoist experiment (465 positions, minimum 26 in that domain).
The byte-identical PR843 recipe from head
`c99f4478156906c323b1a041f0443f76139d6b6c` is retained as
`predecessor843.json`; its full source pin is in `SOURCES.json`. The local
check independently verifies that recipe's integer map and 26-gate count.
No hosted savings from that PR are imported into this contribution.

Other reviewed block work, PR873/880/891/906/908/914/923/925, uses other
operators or fixed-factor classes. PR904/936/941 prefix and PR915/926/941
D-compensation mechanisms are related circuit improvements; composition
with their emitted candidates is not checked here. The verifier and native
harness adapt Jerry Chen's PR906 package with attribution in `NOTICE.md`.

## Scope and remaining obligations

This establishes a finite local replacement and fresh native multistage
evidence. It does not establish a minimum circuit, practical runtime gain,
new recursive moment or larger kappa. The unchanged rank profile cannot
improve the selected bit moment; the selected assembly is complex-bound.

A full hosted emitter, owner program, invoice, supplier binding and outer
assembly for this candidate remain to be built. The inherited all-size
compiler, common-label/mutable-source realization, hosting, precision/tape,
recovery and analytic assumptions remain. The native tests do not prove
the complete multiplication theorem, in Lean or otherwise. Broad `make verify`,
the selected cold complex replay and remote CI are not claimed: the contribution
changes only this research package. See `VALIDATION.md` for actual checks and
`NOTICE.md` for contributor and substantial-AI-assistance disclosure.
