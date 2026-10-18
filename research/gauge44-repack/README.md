# Gauge44 repack with the merged #589 bit supplier: conditional κ = 0.001651390457077212

**This revision changes only the cited bit supplier.** #648's complex side (icekylinx's #645 gauge44 construction with jeremykothe2's repacked owner map) certifies b = 0.001654122058459393176396, above #543's bit c = 0.001653826988146798944268, so #648's κ was the #543 cap. Merged main already contains a stronger bit supplier: DreamingOfClouds' [#589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) (two A-section transports on eumemic's [#555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) punctured R439 word), c = 0.001733427039589844234749, preserved on main at `research/e8-bit-p111-tuned/tune/EXPECTED.json`.

- **κ = 412847614269303/250000000000000000 = 0.001651390457077212**, +0.01781% over #648 (0.001651096360425895). The complex side binds again. The conservative (pre-#559) complex charge passes at 0.00165139045419947.
- **What changed.** `inputs/PR589-EXPECTED.json` is main's #589 receipt, byte for byte (git blob e293ddc5…, identical at #589's head a5afc8c and on main 17ce0c79). `code/assemble.py` reads it instead of #543's receipt, checks its blob id, word parameters (v = 111, R = 439, decoder constant 63) and the nine-stage deficit identity T(8v − 9·cst) = 32·321 = 10,272 (it was the literal 9,984 = #543's v = 120 value), computes the binding side, and records the new supplier. `verify_global.py` asserts the vendored receipt equals main's copy; `data/UPSTREAM-PINS.json` pins main's copy by sha256. `data/SPEC.json` κ fields were re-derived by the package's discovery → `code/freeze_spec.py` → strict chain. The owner map, PLAN, construction, invoice, both exact moment engines (bit bad-residue surcharge retained), the 47-inequality outer assembly and all 69 admission controls are unchanged.
- **Retained assumptions added by the swap**: those #555/#545 retain for the bit side: a v = 111 bit supplier in the outer assembly, and pooled-cell bit hosting (as for #543, not #458's stricter one-helper-per-family rule).

Everything below is #648's README, unchanged.

# Gauge44 with a repacked owner map: conditional κ = 0.001651096360425895

**The construction is icekylinx's [#645](https://github.com/CrocSwap/integer-mult-bounds/pull/645) (`research/gauge44-global`), unchanged.** This package changes only the literal owner map and its PLAN: `data/OWNERS.json.gz` (sha256 1a7438f32d25f028…) and `data/PLAN.json` (064d05a8b1f48542…), plus the expected values in `data/SPEC.json` re-derived for that map by #645's own discovery/freeze/strict chain (`verify_global.py`, `code/freeze_spec.py`). Every construction file, code file, recipe and the supplier word are #645's, byte for byte. We claim only the owner map.

- **κ = 0.001651096360425895**, +0.0978% over #645 (0.001649483702558979). The complex side now certifies 0.001654122058459393176396, above the unchanged [#543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) bit supplier 0.001653826988146798944268, so **the bit cap binds**.
- **Owner map.** #645's map (`data/OWNERS.json.gz`/`data/PLAN.json` of #645) repacked by one round of Mine636's gap-merge search (`gapmerge.py`, run by G44Pack through `ceiling_pack.py`, 150 s round, maxdepth 8, b 0.001636; deterministic but wall-time bounded). gapmerge generalises vectorsss/Chi Zhao's [#638](https://github.com/CrocSwap/integer-mult-bounds/pull/638) `relocate_two.py` (Apache-2.0) with width-shift swap chains and empty-bin migrations; #638's own relocation found no move on this map. Every accepted step strictly improves the exact κ of the paid profile. Only PLAN's `profile` and `assignment_sha256` change; windows, order and dispatch are #645's. The map is admitted by #645's verifier chain, not by the search.
- **Evidence.** The strict replay with `verify_global.py` on this package (`--local` = #645's frozen `evidence/local`; the discovery → `code/freeze_spec.py` → strict chain re-derived `data/SPEC.json` `data`/`expected`, with `providers`, `dispatch` and `call_order` unchanged) passes: `PASS_GAUGE44_STRICT_GLOBAL_REPLAY`, κ 0.001651096360425895. The files under `hosting/`, `evidence/` and `independent/`, and `RESULT.json`, `LOCAL-VALIDATION.json` and `CONSTRUCTION.md`, are #645's and describe #645's owner map and κ. They are retained unchanged as #645's evidence. For this package, `data/SPEC.json` and a fresh `verify_global.py` replay are the binding record.
- **Line endings.** `data/SPEC.json` was written with CRLF by the freeze step and is committed as LF. The content is identical (`crlf.replace(b'\r\n', b'\n') == lf`, same JSON); no verifier pins its bytes except `MANIFEST.json`, which is regenerated here.

Clean-clone verification (from the repository root, Python 3.11+, assertions on; pinned #635 supplier prepared as in the #645 section below):

```sh
python -B research/gauge44-repack/verify_manifest.py
python -B research/gauge44-repack/construction/reproduce.py \
  --main . --pr635 /tmp/gauge44-pr635 --out /tmp/gauge44-repack-local --until phases
python -B research/gauge44-repack/verify_global.py \
  --main . --local /tmp/gauge44-repack-local/local --work /tmp/gauge44-repack-global
# kappa 0.001651096360425895
```

## Predecessor: #645's README (unchanged below; paths read `research/gauge44-global`)

### Gauge44: conditional κ = 0.001649483702558979

New contributions by **icekylinx**, with **OpenAI GPT-6 Astra** assistance.
Local review and packaging used OpenAI Codex. Original notices and Apache-2.0 licenses are retained.

Under the retained all-size compiler, common-label/mutable-source realization,
whole-call hosting, precision/tape, exact-recovery, analytic-transfer and bit
H1–H5 interfaces,

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{1649483702558979}{10^{18}}=0.001649483702558979.
$$

The certified complex saving is `0.001652208994368411824947`. The unchanged
[#543](https://github.com/CrocSwap/integer-mult-bounds/pull/543) bit supplier gives
`0.001653826988146798944268`, so the complex side binds. The conservative complex
model separately certifies κ `0.001649483699681650`.

### Construction

This replaces the local supplier and all 72 owner assignments of pinned
[#635](https://github.com/CrocSwap/integer-mult-bounds/pull/635). Source/copy exchanges
at equal rank-one frames alter the factory's arbitrary-helper-input propagation.
An invertible completion of the retired rows and source-carried coordinate totals
then expose 44 rank-four cold endpoints. Exact input premixes, low-frame tails
and a recomputed full inverse realize them.

| Per-invocation quantity | Complete #635 JP8 | Gauge44 |
| --- | ---: | ---: |
| Source / target ports | 112 / 112 | 112 / 112 |
| Helpers | 492 | 492 |
| Rank-four cold endpoints | 22 | 44 |
| Helper residual width | 3,894 | 3,794 |
| Paid local rank mass | 5,750 | 5,650 |

The new paid local profile is `{1:2514, 2:404, 3:448, 4:160, 5:56, 8:8}`.
The explicit whole-family assignment covers 35,424 helper roles on 7,168 live
and 7,670 physical families. It retains the rank deficit 2,560 and charges every
idle remainder. Exact integer majorization certificates justify the owner
updates; the resulting map is a coordinate fixed point, with no claim of joint
optimality.

The assembled κ is 0.809306% above #635. `data/FRONTIER.json` records Pro's dated
comparison snapshot; it is not a live ranking of community results.

### Proof and evidence

- `CONSTRUCTION.md`: exact cold-space calculation, dyadic realization and attribution.
- `hosting/PROOF.md`: capacity, exchange and majorization arguments.
- `independent/CENTRE-GUARD-REVIEW.md`: ordered center-frame interface and source carriers.
- `data/SPEC.json`, `evidence/ASSEMBLY.json`: strict component moments and outer parameters.
- `evidence/audit/`: actual controller, physical charts and finite invoice.
- `construction/INPUTS.json`, `data/UPSTREAM-PINS.json`: inherited input hashes.
- `MANIFEST.json`, `SOURCES.json`, `LOCAL-VALIDATION.json`: submitted bytes, provenance and local checks.

Original Pro run receipts are retained as evidence; their raw logs remain in
the original archive outside the submission. Fresh replay writes new logs to
the selected output directory.

### Incremental reproduction

Use Python 3.11 or newer with assertions enabled. The required replay uses only
the standard library. The optional historical seed-discovery optimizer is not
part of admission.

Prepare the pinned #635 supplier in a separate directory (the main dependencies
are already present in this repository):

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git a6895a69f8ad98ab45777b03e9e6f48888c39f6f
mkdir -p /tmp/gauge44-pr635
git archive FETCH_HEAD research/complex-571-cold14-st2 | tar -x -C /tmp/gauge44-pr635
```

From the repository root, with fresh output directories:

```sh
python -B research/gauge44-global/verify_manifest.py
python -B research/gauge44-global/construction/reproduce.py \
  --main . --pr635 /tmp/gauge44-pr635 \
  --out /tmp/gauge44-local --until phases
python -B research/gauge44-global/verify_global.py \
  --main . --local /tmp/gauge44-local/local --work /tmp/gauge44-global
```

The dedicated workflow also runs the independent literal-word audit, exact owner
reproduction, preserved-assertion comparison and independent pricing on Python
3.11 and 3.14. `hosting/README.md` and `independent/README.md` give those commands.
No ancestral full replay, optimizer search or PDF generation is required.

The result remains a finite conditional witness. It does not establish an
unconditional multiplication theorem or a complete Lean formalization.
