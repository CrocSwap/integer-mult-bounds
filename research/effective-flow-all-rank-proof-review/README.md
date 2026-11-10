# External written review of the effective all-rank flow bound

This package reviews the complete analytic propagation in [alephnan's PR6713](https://github.com/CrocSwap/integer-mult-bounds/pull/6713), pinned at `cd666f05c4e9006025b634687cc493911c8371c8`. The source already proves its theorem. This contribution is a conditional external written audit of its mixed-layer normalization, kernel transfer, geometric and leaf tails, symbolic onset and final induction. It claims no new exponent, onset, source program or flow construction.

The reviewed theorem concerns the historical raw-p7 scalar recurrence at the original default height base five with extra height zero, retaining all source multiplicities, unmatched boundary exits and terminal paid leaf ranks. For s=99739/100000 and

```
n_LLT = 2^(10^12),
G_0   = 2*n_LLT+2,
N_0   = 121*5^G_0,
```

the source concludes L(n)<=N_0^(1-s)*n^s for every integer n>=1. These are exact symbolic expressions; no giant integer or associated flow is materialized in this review.

[PROOF-REVIEW.md](PROOF-REVIEW.md) integrates three separately prepared written checks: [MIXED-REVIEW.md](MIXED-REVIEW.md), [ONSET-KERNEL-REVIEW.md](ONSET-KERNEL-REVIEW.md) and [TAIL-INDUCTION-REVIEW.md](TAIL-INDUCTION-REVIEW.md). A separate [ADVERSARIAL-REVIEW.md](ADVERSARIAL-REVIEW.md) checks the assembled interfaces and written scope controls. The result is conditional on the exact finite flow identities, positive inventory and numerical premises named in the source. Agreement among review roles is not a replacement for the displayed mathematical derivations.

The audit retains the tilted multiplier (1-q)q^h after normalization, the full leaf coefficient, every boundary term and the nonnegative root capacity that may safely be discarded in a lower bound. The first 3001 mixed layers use a controlled conditional shift; middle layers use location-uniform interval probability bounds; the end layers, including zero paid letters, use a trivial supremum bound and geometric weights. Leaf integration charges both a finite window and the entire remaining half-line. The initial-range induction uses the inherited conservation identity to obtain L(n)<=n before the power majorant is applied.

The kernel review preserves all interval endpoint conventions. Capacity derivatives may be singular at x=1, but continuity and bounded variation suffice for Stieltjes integration. Window kernels are decreasing on their own windows; their zero extensions and signed sum need not be globally decreasing. The local-limit Gaussian comparison is shift uniform, while its later flat-density approximation has an explicit shift-dependent error. No tail or endpoint mass is silently discarded.

## Premises and evidence boundary

The complete finite source/mirror decomposition, recurrence identity, inventories, strict q/J and complement-capacity margin, and their source bindings are inherited premises here. No original scientific program or checker was read, imported, executed or reimplemented for this review. The previous [PR6723](https://github.com/CrocSwap/integer-mult-bounds/pull/6723) supplied scoped external finite-H and local-limit review; [PR6728](https://github.com/CrocSwap/integer-mult-bounds/pull/6728) supplied the exact tilt-root/actual-mean bridge. Their limited scopes remain separate and do not independently admit the finite flow census or all numerical premises of this full recurrence.

The five inert inputs and their exact Git/SHA256 provenance are in [SOURCE-PINS.json](SOURCE-PINS.json). Prior source-aware review exposure is disclosed. This package's evidence is written algebra and analysis with unexecuted written controls. There is no scientific replay or proof-kernel run. Subsequent byte, source-history, archive, publication and CI controls can establish integrity or workflow behavior; they cannot turn this written review into executed scientific validation. [VALIDATION.md](VALIDATION.md) records that distinction.

## Open next questions

1. Can the complete finite census and mirror/conservation identities be externally admitted against the actual pinned flow? Start with an independent check of all source and boundary multiplicities at the exact default height, including cap endpoints and unconditioned terminal ranks. This review inherits those identities, so a complete source-to-recurrence binding remains a separate obligation.
2. Can the exact tilted law and every numerical q/J/capacity premise be bound to the intended caller? Start with one explicit caller contract and a complete outward-rational certificate of its law, normalization and strict margin. The existing root and H audits cover only their stated historical premises, and a different law or caller needs its own binding.
3. Can a physical supplier fund this complete recurrence? Start with an actual native/source execution and a ledger for access, restoration, payload, compiler, precision, tape and recovery costs. The scalar all-rank majorant supplies none of those physical bills or the selected result's five assumptions.

The reviewed construction is historical raw-p7, not admission of the selected P104 caller. No selected analytic-recovery condition, full physical supplier, paid profile, kappa/frontier, scientific adoption or merge changes.

## Credit

alephnan/PR6713 supplies the effective all-rank proof and onset. CubeJerry/PR6329, zxv/PR4436/4483, Ryanson Jonathan and pinterbanget/PR4459/4467, DLamdata/PR6118, Nick Petalas/PR6125/6128, Cinna Davis/1337isnot1337, Jacob Alan Sussman and retained native, precision and analytic contributors retain their source lineage. Beurling, Selberg and Vaaler supply the classical Fourier approximation; Laura Shou supplies the inspected primary statement used by the source. PR6723 and PR6728 retain their scoped external-review credit. ToikY with substantial OpenAI Codex assistance supplies this separately prepared source-aware written audit, not human or proof-kernel acceptance. Original notices are retained in [inputs/NOTICE](inputs/NOTICE) and [NOTICE](NOTICE).
