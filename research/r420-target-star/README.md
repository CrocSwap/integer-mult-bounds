# R420 compensation through restored target stars

**Finite bit-circuit improvement; no new κ.** On eumemic's accepted #543 R420
word, a forest of target stars shares 16 nominated donors among 100 receivers
during the frame-zero dirt-compensation stage D. This saves **3,288 binary XOR additions**,
including every preparation and restoration operation. Helpers remain unchanged
throughout D, including its intermediate states.

| Quantity | Pinned #543 | This word |
|---|---:|---:|
| D binary additions | 19,922 | 16,634 |
| Complete native binary additions | 26,916 | 23,628 |
| Native records | 29,874 | 26,586 |
| Helpers / copied totals | 420 / 9 | 420 / 9 |
| Paid local rank mass | 5,112 | 5,112 |
| Forward positive-prefix bound | 144,651 | 144,651 |
| Inverse positive-prefix bound | 2,270,064 | 3,798,646 |
| Native payload bound, bits | 100 | 102 |

The inverse prefix **increases**, despite the smaller instruction count. Both
words satisfy the inherited strict native bound `payload < 2^104`; no old prefix
receipt is reused. Every register's ordered frame path and the complete
MOVE/COPY/ERASE subsequence are identical. The profile remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`. Only D changes.

## Reproduce

From the repository root, with Python 3.9 or newer and its standard library:

```sh
python3 -B research/r420-target-star/verify.py
```

Expected final line:

```text
PASS_R420_TARGET_STAR receivers=100 D=19922->16634 native_ADDs=26916->23628 saved=3288 columns=660 rank_mass=5112
```

The same command works under `python3 -I -O -B`. To materialize the exact word,
add `--write-word /absolute/new/path.json.gz`; existing outputs are not overwritten.
Equality is checked on canonical decompressed JSON, not gzip container bytes.
`CERTIFICATE.json` includes the complete 1,680-candidate donor-set trace, final
receiver costs, the selected 100 target/donor pairs,
the canonical word hash, complete native invoices and exact prefix integers.
`--check PATH` allows an independently supplied certificate to be checked.

An additional native replay uses the unchanged repository C++17 checkers and
requires Boost headers (tested with 1.85.0):

```sh
python3 -B research/r420-target-star/native_verify.py \
  --boost-include /path/to/boost_1_85_0 \
  --output /absolute/new/replay-directory \
  --check research/r420-target-star/NATIVE.json
```

Expected: `PASS_R420_TARGET_STAR_NATIVE both_words=5/9/11 columns=900/1380/1620 missing_preparation=rejected`.
It compiles fresh binaries, checks both words, compares every native invoice and
directional prefix with the Python certificate, and rejects the actual missing
preparation instruction at all three stage counts. `NATIVE.json` records the
normalized mathematical receipts separately from compiler/platform metadata.

The checker reuses **unchanged, pinned** #543 `xcheck.py` for the E8 lattice,
all 672 closed frames, legal native paths, arbitrary-dirty 660-column replay and
interface diagnostics. It reuses Dylan Crow's record exporter, then executes
those actual records using a separately written set-valued interpreter, checks
the forward and inverse maps and COPY lifecycle, and counts all instructions.
This reuse is not called a wholly independent reimplementation of the E8 audit.

A Python implementation of DaysSky's #381 bridged schedule replays both actual
words at 5/9/11 stages on 900/1,380/1,620 independent physical columns. Each of
the 6/18/24 omitted-bridge controls replays the full changed record stream.
Nine additional controls cover missing preparation, restoration, donor
compensation, a receiver correction, a helper read, a previously modified receiver used as donor, an illegal frame, an
F2-neutral but paid pair and an omitted exported instruction. In particular,
omitting one preparation passes on **zero-initialized targets** and fails on
arbitrary targets. Zero-target tests alone would miss this error.

## Interface and scope

See [PROOF.md](PROOF.md) for the exact identity and complete cost. The inherited
syntactic H2 rule requires D to read helpers only and therefore **rejects** this
word. The inherited literal `K_equals_D` extractor also returns false: it does
not follow target values through D. These failures are expected and explicitly
required by the new verifier; the old checker is not patched or bypassed.
The replacement condition proves and checks that D still implements exactly
`(x,s,y) -> (x,s,y+K*s)` and keeps every operation at frame zero. All other
inherited hypotheses and conclusions pass on the actual changed word.

This is a complete finite native circuit, with a scoped interface extension.
It is not a new accepted supplier or a multiplication theorem. Hosted-parent
reconstruction, literal whole-owner emission, finite global invoices, global
prefix bounds and a changed-word outer assembly remain integration obligations.
The standard-library command does not invoke the C++ binaries. The optional
native command above is a separate replay. Full repository `make verify`,
remote CI and Lean are not claimed by either command.

The original all-size compiler, common-label/mutable-basis realization, pooled
hosting, normalized residual, precision/tape/exact recovery and analytic
assumptions remain. Local F2 equality is not equality of the two unsigned
integer transfer matrices. The positive bounds account for the actual integer
lift, but do not establish the full precision theorem. There is no measured
runtime claim or global circuit optimum.

## Assignment, current state and overlap

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Reviewed bit source #543: `2065fe4f72a914d907f1046603f5a36f17018535`.
Selected complex source #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
`SOURCES.json` binds every consumed source and the selected review/assembly by
SHA-256 and Git blob. The accepted baseline is
`κ = 51110230636731/31250000000000000 = 0.001635527380375392`, with
bit `c = 0.001653826988146798944268` and complex
`b = 0.001638206712308086862575`; the selected assembly is complex-limited.
These values identify the baseline, not a changed-word certification.

The assignment seed was **0**, drawn once with OS randomness through
`secrets.randbelow(100)`. It selects the bit track and fixes the first donor to
target 0 (register 120). After the initial single-star experiment, an overlap
refresh found #713/#716's stronger disjoint-pair constructions. The one bounded
extension permits **shared donors** while retaining disjoint donor/receiver sets.
It scores all 14,280 ordered target pairs, then greedily adds the donor producing
the best complete saving, recomputing each receiver's best donor. Smaller register
IDs break ties. The limit of **16 donors** was fixed before the extension ran.
All **1,680** candidate donor sets in the 15 addition steps were evaluated; the
run stopped at the limit, not at an asserted optimum. The first trace entry
preserves the original target-0 result (892 additions saved).

For any fixed donor set the best receiver assignment is proved by independent
per-row maximization. The greedy choice of the donor set has **no optimality
claim**. No alternative initial donor, removal/swap, layered target basis, helper
basis or composition with pending circuits was searched. This extends the
**disjoint-pair** class to a star forest, rather than repeating a matching with
a different seed.

`CLAIM.json` records the three candidates and the local claim. GitHub returned
no pinned coordination issue, so no reservation issue was opened. `OVERLAP.json`
records the checked related PR heads and later refresh.

- **#476/#478 (Dugongue)** already use reversible target-interval factoring on
  historical R715 phase-B words. The elementary identity is predecessor work;
  this contribution instantiates a target-only star in the accepted R420 D
  stage and checks the arbitrary-target interface and full native cost.
- **#686 / #694** factor the R420 D matrix using a temporarily changed helper
  basis; #694 saves more native additions. Here no helper is ever written in D.
  This is distinct evidence for a different restriction, not a stronger record
  or a claim of priority for reversible factoring. No concurrent code is imported
  and no combined gain is claimed.
- **#713 (Scott Woolsey Biggart) / #716 (Sagar Thakrar)** independently construct
  57 disjoint target pairs and report saving 3,150 additions. This star forest permits
  donor reuse, saves **138 more additions** than their reported count on the same
  baseline, and checks the
  entire 48 omitted-bridge family against the actual changed record stream in
  Python in addition to the unchanged native checkers. Their target-basis result
  is credited and has not been independently replayed here; no code or recipe is imported, and no priority for that mechanism
  is claimed. The stronger helper-basis #694 remains distinct and is not beaten.
- **#731 (Joshua Snider)** independently audits baseline compensation rank and
  kernel structure. **#733 (Scott Woolsey Biggart)** reports a larger 8,368 saving
  by combining helper and target bases. It changes helper values during D; this
  construction retains immutable helpers and shares target donors. Neither is
  imported or independently replayed here; no overall saving record is claimed.
- **#708** shares full-frame decoder operands; **#710** changes cleanup;
  **#711/#718** give scoped frame obstructions. None changes this D star-forest
  construction or is composed here.
- **#670/#674/#688/#691** shorten or compose phase-A/B circuits. **#661** bounds
  fixed-order phase-B frame changes and explicitly excludes changes of circuit
  or D. **#612** concerns a formalization of the prior scalar interface.

## Attribution and license

Prepared for **@ellipsi2 with substantial OpenAI Codex assistance** in the
construction, mathematical argument, implementation, checks and packaging.
No independent human review is claimed. New work is Apache-2.0 under the root
license. [NOTICE.md](NOTICE.md) retains the direct and cumulative predecessors;
their original notices and files remain unchanged. Neither `upstream/` nor the
selected-frontier pointer is modified.
