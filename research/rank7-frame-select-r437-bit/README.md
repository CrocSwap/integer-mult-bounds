# PR3955's complex side with PR3647's R437 bit supplier: conditional κ = 0.001736646042038446578551 − 10⁻⁴⁶ − 10⁻⁷⁰ (+0.1006%)

**Author-checked conditional candidate; not maintainer-reviewed.** The selected record on
`main` is still #1094. This is a **composition** of two open lines:

- the complex side of PR3955 (hosted frame selection, stacked on PR3939 → PR3934 → … → PR3148 →
  PR3133);
- the R437 bit supplier of open PR3647 by ai-nanachi: the helper464 GL deletion composed with Ali
  Romman's PR1043 helper470 deletion, plus Sagar Thakrar's PR3700 OQ4 slot coalescing.

| | complex root lower | bit endpoint | binds | κ headline |
|---|---|---|---|---|
| PR3955 | 0.0017411725885452521674224 | pooled R438 0.001734900431583947157341 | bit | 0.001734900431583947157341 − … |
| **this** | 0.0017411725885452521674224 | **R437 0.001736646042038446578551** | **bit** | **0.001736646042038446578551 − …** |

The gain is **+0.1006% over PR3955**. PR3955 raised the complex root about 6.3e-6 above the pooled
R438 bit endpoint. PR3647's R437 endpoint lies inside that window, so κ rises to it. About 4.5e-6
of complex headroom remains.

## Verification

```sh
python3 -B research/rank7-frame-select-r437-bit/verify.py   # ~2 s, standard library only
```

The verifier is self-contained and imports no other package's code.

**Complex side.** It reads `rank7-idle-frame-select/RESULT.json`, bound to that package's committed
`AUDIT.json` receipt. It then re-derives:

- the rank mass `65088·740`;
- the halving guard;
- the 10⁻²⁵ root bracket at m = 73, W = 896·740.

It uses its own directed-rounding rational arithmetic. PR3955's own `verify.py` audits the 521,798
moves.

**Bit side.** `R437-EXPECTED.json` is PR3647's `EXPECTED.json`, copied byte for byte:

- source: `research/bit-p111-r437-gl464-470-20261018/EXPECTED.json`;
- PR3647 head `a24f9ff95c12fd0b6792e3f710569237efd72db2`, git blob
  `bc2585e1404402395a7c59ba6f6dde58b04e65a2`;
- SHA-256 `67d06bcb…2de0` as stored there with CRLF line ends. This repository commits it
  LF-normalized, so `verify.py` binds the LF bytes (SHA-256 `fa724e9a…a9f9`).

Its paid profile `{1:380160, 2:400864, 3:22176, 4:26592, 5:29376, 6:17376, 7:26496, 26:32, 42:384}`
is re-priced independently at m = 64, W = 28416, with the inherited 10⁻¹⁶·32m²·N rank-1 fallback
envelope. It is accepted at c and rejected at c + 10⁻²⁴. Rank mass is 1,808,352 and the maximum
child is 42.

**Composition.** `κ = min(floor₂₄(complex), c) − 10⁻⁴⁶ − 10⁻⁷⁰`, with the bit side binding, and
gates over PR3955 and PR3939.

**Controls.** Six mutation controls are rejected:

- the bit endpoint at the next grid point;
- a mass-preserving bit profile change;
- a bit rank-mass change;
- the complex root at the next grid point;
- a mass-preserving complex profile change;
- κ off the grid.

## Scope

The composition inherits every premise of both endpoints.

**Complex side (PR3955):**

- hosted frame selection, which is a new hypothesis;
- hosted receivers;
- hosted donors.

The native, controller and outer stages were not rerun.

**Bit side (PR3647):** its interfaces are the inherited all-size/compiler, common-label /
mutable-SOURCE / target-label, correlated-hosting, complete-stream COPY and precision/tape/analytic
interfaces. Its maintainer admission is pending. This package does not replay PR3647's word,
hosting or native checks; PR3700 independently audited the original R437 word and pricing. This
package only re-prices PR3647's declared profile.

## Open next questions

- **Can R437's own slack be pooled across the 32 replicas, as PR3939 did for R438?**
  - Today each replica keeps one two-slot family (idle 26) and 12 empty 42-copies.
  - Pooled, the 64 residuals in those two-slot families pack into 12 full families plus one
    4-residual family.
  - That raises the bit endpoint while about 4.5e-6 of complex headroom remains.
  - First step: regenerate R437's placement from PR3647's template, then apply a cross-replica owner
    map with PR3939's role audit.
- **Do both endpoints pass native and controller admission?** First step: the overlay-aware T74
  audit, and PR3647's own pending admission.

## Credit

- ai-nanachi (PR3647): the R437 composition and OQ4 hosting realization.
- Ali Romman (PR1043): helper470.
- Sagar Thakrar (PR3700 and PR2423).
- eumemic and DreamingOfClouds (PR555, PR589).
- The full PR3955 stack:
  - PR1252 (Gonzalo-Mier);
  - Guéorgui Maissouradze;
  - PR3148 (Jeremy Diviney);
  - PR3133 (dcharb78);
  - mightyOil;
  - OpenCode (Space bunny free), for ideas in the stacked complex-side predecessors.

Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
