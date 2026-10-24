# Independent recomputation of #4610's raw crossing

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

intqwq's #4610 (head `4b4c75bc`) inserts its changed paid list into the retained p16 controller:

```text
Pnew = 2201 H1 + 412 H2 + 506 H3 + 135 H4 + 36 H5 + 8 H8,    helpers unchanged: 28 H4 + 7 H7 + 47 H8 + 326 H9.
```

It claims a raw crossing in (0.0030215551, 0.0030215552) and selects κ = 0.00302152. My #4614 checked #4610's endpoint frames and profile arithmetic but left this crossing open.

## Method

The two histograms are rebuilt from main's pinned `research/joint-helper-lattice/CONTROLLER.json`:

| event | charge |
|---|---|
| LOCAL | adds the helper list to the targets and the local paid list to the paid histogram |
| QUERY_SHEAR | paid[1] += 112 |
| IDLE with s retained stages | paid[8s] += 224 |
| each diagonal term | targets[1 + 8·Σ term] += 112 |

The root of Σ_T n·r^(1−c) = Σ_P n·r^(1−c) is then found by bisection in **50-digit Decimal** arithmetic. This engine differs from #4610's Fraction intervals, and nothing is imported from #4610.

## Results

| profile | raw root | paid calls | rank-mass surplus |
|---|---|---|---|
| Pnew (#4610) | **0.00302155511144…** | 64,404 | 752 |
| Pold (PR4535), control | 0.00302016597701… | 64,620 | 752 |

- **The bracket holds.** The new root lies inside #4610's bracket (0.0030215551, 0.0030215552).
- **Control.** The old list reproduces PR4535's root.
- **κ selection.** κ = ⌊root·10⁸⌋ − 3 gives 302152·10⁻⁸ = 0.00302152, which matches.
- **Failure control.** Dropping the idle charges moves the root far above the bracket. The idle windows are therefore genuinely charged.

## Verify

```text
python3 -B research/pr4610-crossing-recompute/verify.py
```

The check takes under 1 s and uses the standard library only.

## Limitations

- **Arithmetic only.** This re-derives the arithmetic from root to κ selection, assuming #4610's local paid list and the retained controller semantics.
- **Not re-checked here:** the 54 strict outer-ledger inequalities, native phase lowering, the Lean certificates, and the contract admissibility of generator substitution. My #4614 covers the endpoint frames and profile.

## Open next questions

- **Outer ledger.** Re-evaluate the 54 strict outer-ledger checks with an independent engine at #4610's parameters. First step: port `compiler-refill/endpoint.py`'s inequalities to Decimal.

Credit: intqwq (#4610), Cinna Davis (#4470) and the controller lineage. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
