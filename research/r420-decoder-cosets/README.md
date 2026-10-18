# R420 decoder source cosets: 244 fewer local binary XORs

**Status: finite bit-circuit research construction; no new κ.**

Prepared by **Chinmay Khaladkar (@cxnmai)** with substantial OpenAI AI
assistance, including a separate source-level reviewer agent. Apache-2.0.
No independent human review or full multiplication theorem is claimed.

## Result and reproduction

Change just decoder total **index 3, host 583**, in eumemic's #543 R420 word.
Its source expression is unchanged, but its helper-dirt expression changes
in **93 columns**. Recompute frame-zero compensation D and literal cleanup C.
The complete local primitive count falls **26,916 → 26,672**, saving **244**:

| Section | Original binary XORs | Candidate |
|---|---:|---:|
| D: dirty compensation | 19,922 | 19,642 |
| A | 2,376 | 2,394 |
| scatter | 568 | 568 |
| B | 1,077 | 1,077 |
| C: restoration | 2,973 | 2,991 |

The chosen total becomes **25 → 43** XORs: minimizing its own length would
miss this improvement. Every new operand read and the extra cleanup is charged.
There are no new helpers, recursive children, copies or frame changes. All 660
register frame paths agree, including their final climbs. Rank mass remains
5,112; the local histogram is `{1:1320, 2:1440, 4:60, 5:120, 8:9}`.

Run from the repository root (Python 3.11+, standard library only):

```sh
python3 -B research/r420-decoder-cosets/verify.py
```

Expected final line:

```text
PASS_R420_DECODER_COSET total=26916->26672 saved=244 columns=660 controls=6 no_new_kappa
```

`--word /tmp/candidate.json.gz` also writes the complete candidate. Equality is
by canonical JSON payload, not a regenerated gzip container hash. `RECIPE.json`
freezes the search, operands and five accepted moves; `EXPECTED.json` freezes
verification results. `--record` deliberately rewrites that receipt for authors;
normal verification never rewrites repository files.

## Mechanism and exact cost

At the chosen gate let register r contain `X_r x + H_r s` over F2. Toggle an
operand set N with `XOR_{r in N} X_r = 0`. Its dirt change is
`d = XOR_{r in N} H_r`. Host 583 is not accessed by later A gates or B;
its only downstream target use is scatter column 3. Therefore

```
K'_t = K_t XOR (scatter[t,3] * d)
Delta = 2 (|operands'| - |operands|) + sum_t (wt(K'_t) - wt(K_t)).
```

Setting D to K' restores the same target map. C is regenerated as the literal
reverse of all A/B non-target gates, so it restores arbitrary source/helper
inputs. No target feeds a non-target. The unchanged original H1–H5 checker
accepts the candidate, including frame legality and the exact J=I, D=K, U inverse
obligations. This is a finite F2 identity, not an all-size analytic proof.

## Bounded search and useful negative evidence

Assignment seed **3** comes from OS randomness; index `3 mod 9` selects the
fourth total, rather than another frequently resynthesized block.
The 80 non-retained operands already used by the nine original totals have
**source rank 80**: this pool has no source-null toggles. The evidence-driven
expansion uses all 180 dead o2 registers from the first 180 phase-A D6 additions,
minus the nine retained hosts. The resulting **171-register pool has rank 90
and nullity 81** at the actual gate prefix. No pool register is accessed by B.

`search.py` performs 32 seed-3 shuffled Gaussian-elimination bases, each followed
by steepest strictly improving single-basis-vector descent until no such move
helps. It completes **2,997 scored candidates**, accepting five moves. Ties use
basis order. This searches neither all 2^81 null vectors nor all schedules;
no optimality or impossibility theorem follows. The complete candidate is
replayed, not trusted from the local cost formula.

## Verification and limits

- Independent set-valued replay covers all 660 dirty input columns.
- Original #543 checker covers 120 E8 lines, all 672 frames and H1–H5.
- Six negative controls reject stale D, stale C, missing D read, missing C gate,
  corrupted total with matched C, and scalar-neutral illegal frame placement.
- Original Dylan Crow exporter emits **29,874 → 29,630** records, with unchanged
  2,940 MOVEs and nine COPY/ERASE pairs. Copy-aware positive integer bounds are
  measured in both directions: forward **144,651 → 144,651**, reverse
  **2,270,064 → 2,301,524**. The stock local envelope
  `64 * forward^3 * reverse^2` remains 100 bits, below the 104-bit limit.

The reverse bound increases: fewer XORs do **not** imply coefficient domination.
The native bound calculation is Python, following `columns_k.cpp`; this package
has not run that C++ multistage checker (Boost headers are unavailable), rebuilt
the hosted parent, checked its global invoice, or assembled a changed-word κ.
No repository-wide `make verify`, selected cold replay, Lean or remote CI pass
is claimed. Only this new research package changes; therefore unrelated global
artifacts are not regenerated. All-size/compiler/common-label/mutable-basis,
whole-owner hosting, residual, precision/tape and analytic assumptions remain.
The selected composition is complex-bound; local XOR savings alone do not
change its recursive profile or imply a stronger exponent.

## Pins, predecessors and overlap

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected result at that base: #626 with #543, conditional κ
`0.001635527380375392`; it is unchanged. Supplier #543 source head:
`2065fe4f72a914d907f1046603f5a36f17018535`.
The exact compressed input SHA256 is in `RECIPE.json`; the original checker
SHA256 is enforced in `verify.py`; exporter SHA256 is in `EXPECTED.json`.
All three input paths are in those scripts and resolved relative to this repo.

Credit remains with eumemic's #543/#493 circuit, Dylan Crow's export/checker
lineage, Zhihao Chen's #425 interface, #472's common-label realization, and
all predecessors credited in `research/e8-bit-r420/README.md` and its notices.
No pending contribution is imported. In particular Sagar Thakrar's #708 shares
restored operands while preserving the full dirty operator. This construction
changes that operator and wins mainly in D, using a different search class.
#686/#694 change frame-zero bases; #710 shortens cleanup; #716 optimizes target
pairs. Final overlap refresh through #747 also checked Joshua Snider's #731
(rank/kernel of the **fixed correction matrix K**, not our decoder source map)
and Scott Woolsey Biggart's #733 (two-sided basis composition preserving K).
@ellipsi2's #742 likewise preserves K, using shared target donors.
Our construction changes K; their savings must not be added to ours without a
new composition audit. Those mechanisms are not combined here. The local claim
records the candidate selection and absence of a pinned coordination issue.
