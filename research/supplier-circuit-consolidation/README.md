# Consolidated supplier circuits: checked composition and integration batch

**Finite circuit integration; no new κ.** This batch brings six pending research
packages into one tested integration, incorporates two earlier bit circuits
through their retained PR688 certificates, and composes PR681 with PR696. It
adds an opt-in executable path, exact receipts, a sufficient semantic D-boundary
proof, and a disposition table. It does not merely collect independent savings.

| Measured operation bill | Before | Consolidated | Reduction |
|---|---:|---:|---:|
| Bit ADDs per local invocation | 26,916 | **18,378** | **31.72%** |
| Complete hosted bit instructions, 288 invocations | 8,603,712 | **6,144,768** | **28.58%** |
| Selected CK forward real-component primitives | 224,938 | **169,618** | **24.59%** |
| Selected CK inverse-transpose primitives | 224,986 | **169,634** | **24.60%** |
| Selected JP8 forward real-component primitives | 257,232 | **200,380** | **22.10%** |
| Selected JP8 inverse-transpose primitives | 257,280 | **200,396** | **22.11%** |
| Raw complex factory forward primitives, PR681 + PR696 | 170,488 | **123,768** | **27.40%** |
| Raw factory inverse-transpose primitives | 170,536 | **123,784** | **27.41%** |

These rows are distinct bills and must not be summed into a runtime claim.
The selected conditional κ stays **0.001635527380375392**, exactly
`51110230636731/31250000000000000`. Scalar work decreases; recursive child
profiles remain unchanged. Raw factory improvements are not transported through
selected optimized provider recipes. Only PR696's lowering is used for the
selected CK/JP8 primitive rows.

## Reproduce and use

From the repository root, Python 3.11+:

```sh
python3 -B research/supplier-circuit-consolidation/verify.py
```

The local command uses the standard library. It rebuilds and checks the combined
bit word, every scalar column and precision bound, both raw complex words, the
four selected complex programs, and the complete frozen receipt. It refuses
optimized Python because inherited auditors require assertions.

For the complete native, whole-owner and invoice check, install NumPy, SciPy,
SymPy and a C++17 compiler with Boost headers, then run:

```sh
python3 -B research/supplier-circuit-consolidation/verify.py --hosted --out /path/to/new-directory
```

Set `CXX` and `BOOST_INCLUDE` if needed. Expected final marker:

```text
PASS_SUPPLIER_CIRCUIT_CONSOLIDATION bit_ADDs=26916->18378 saved=8538 hosted=True kappa=unchanged
```

Omitting `--out` uses a temporary directory. A named output directory must be
new; it retains baseline/replacement bit words, compiled-checker receipts,
whole-owner templates and invoices, and four `*-PRIMITIVES.json.gz` artifacts.
Those artifacts preserve all non-scalar events and replace scalar macros with
explicit real-component primitive instructions, carrying the macro's frame.
The complex bill charges two components. Primitive counts and sequence digests
are bound to the streams independently replayed by PR696's verifier.

Normal commands compare `EXPECTED.json` or `HOSTED.json` exactly; `--write PATH`
is a development-only receipt regeneration mode. Package integrity checks:

```sh
python3 -B research/supplier-circuit-consolidation/test_package.py
```

This tests a minimal source closure in a path with spaces, no Git metadata or
cached outputs, and five meaningful rejection/output-preservation controls.
The template `ci/supplier-circuit-consolidation.yml` defines Python 3.11/3.14
local checks and a full Linux hosted replay. To activate it, copy it to
`.github/workflows/` using workflow-authorized access. GitHub rejected the
connected OAuth token's attempt to publish an active workflow because it lacks
`workflow` scope. No remote CI pass is claimed.

## What actually composes

- **PR694, Greer Guthrie:** all 201 helper-basis pairs are retained.
- **PR713, Scott Woolsey Biggart:** the target-row method is rerun on the new
  helper-transformed matrix, yielding 56 pairs. The old 57-pair recipe and its
  3,150-ADD headline are not reused or added to PR694's saving.
- **PR691, mtpsl:** the complete 19-to-12-operation phase-A quad is retained.
- **PR670, yongjae321, and PR674, x0hu, via PR688, Ali Romman:** both smaller
  phase-B circuits and their exact original certificates are retained.
- **PR708, Sagar Thakrar:** 23 of 27 decoder-sharing pairs fit the combined
  precision budget. All 27 would save eight further ADDs but require 105 bits;
  that version is an explicit rejection control. All leave-one-out variants
  also fail. The finite compatibility pass is reproducible (372 extensions).
- **PR696, Sagar Thakrar:** the full selected complex lowering is retained and
  additionally checked on the freshly rebuilt PR681 raw factory words.
- **PR681, Alluri:** all fourteen exact factory replacements are retained.

PR686 is credited for the earlier one-pair compensation idea and semantic
D-prefix contract; its code is not imported. See `PROOF.md` for complete-map,
frame, restoration, composition and precision arguments. The bit substitutions
use the original geometry, helper inventory, nine COPYs and 5,112 rank mass.

## Precision is repriced, not hidden

| Precision quantity | Before | Consolidated |
|---|---:|---:|
| Local bit payload bound, bits | 100 | 104 (within strict `< 2^104`) |
| Raw hosted positive-prefix bound, bits | 189 | 196 |
| Charged hosted prefix allocation, bits | 192 | 256 |
| Two-level coefficient bound, bits | 416 | 432 |
| Charged two-level allocation, bits | 512 | 512 |

The actual changed stream passes unchanged C++ 5/9/11-stage formal-column
checks and both inherited parent/whole-owner auditors. All 120,960 helper
invocations remain hosted without zero-bank allocation. The unchanged exact
moment engines reproduce bit saving `0.001653826988146798944268`. The hosted
invoice's cited PR484 outer calculation is a historical arithmetic control,
not a new selected assembly.

The original literal H2 and K extractor cannot admit a temporary helper/target
basis. They are not patched or relabelled. The integration proves the exact
frame-zero D boundary and checks original H1-H5 on the canonical D with the
changed A/B/C. Native geometry and complete actual-word replay check the new
syntax separately. This semantic extension is explicit and independently
reviewable, not an ignored checker failure.

## Maintainer handoff and attribution

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. `SOURCES.json` pins 235 consumed
source files and the exact imported heads. The six packages remain byte for
byte under their original research paths; their two standalone workflows are
represented by the broader activation-ready consolidation template. Their original validation
claims remain historical; `VALIDATION.md` records this integration's own runs.

`DISPOSITIONS.json` separates retained source, composed scope and proposed
post-merge action. The linked central review-ledger supplement does not mark
these proposals published or change historical dispositions. After merge and
a fresh head check, a maintainer can resolve the six imported research PRs
with their preserved credit and remaining scope linked. PR670/674 have only
the cited circuit subset imported through PR688; full-PR closure is not claimed.
No other PR is merged, closed or modified by this batch.

Prepared for **Alluri (@alluri-ritual)** with substantial **OpenAI Codex**
assistance in integration, code, proof analysis, verification and writing.
No independent human or delegated-agent review is claimed. Apache-2.0.
Credit remains with all component authors listed above and with eumemic,
Dylan Crow / DreamingOfClouds, Jeremy Kothe, icekylinx, Chafik Boukhalfa,
Dugongue, Zhihao Chen, DaysSky and the complete supplier/compiler/hosting
lineage in the original notices. Imported packages preserve their AI disclosures.

Inherited all-size compiler, common-label/mutable-basis realization, physical
hosting, uniform precision/tape and analytic assumptions remain. This is a
finite integration candidate, not a formal multiplication theorem, optimal
circuit claim, new κ or measured practical runtime speedup. `upstream/` and
the selected certificate remain unchanged.

Later arrivals #716 (optimal target pairs on the original matrix), #722
(shared JP8 coefficient work) and #723 (signed-digit lowering) are credited
as related work outside this frozen batch. Their different matrix or work/prefix
boundaries require another composed recount. `OVERLAP.json` records the refreshed
549-PR queue through #730 and confirms unchanged imported heads.
