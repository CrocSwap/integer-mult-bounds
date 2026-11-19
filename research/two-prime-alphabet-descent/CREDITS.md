# Sources and credit

Ali Romman (@aliromman) prepared the simultaneous-column descent proof,
sharp three-column family and exact controls with substantial OpenAI
Codex assistance. New material is Apache-2.0. No independent human or
formal proof-kernel acceptance is claimed.

Ali Romman's [PR #7769](https://github.com/CrocSwap/integer-mult-bounds/pull/7769)
supplied the [complete fifteenth-root capacity proof and attaining matrix](https://github.com/aliromman/integer-mult-bounds/blob/6dbe6e9503f26189833d5ef213aee708679835f2/research/fifteenth-root-column-capacity/PROOF.md),
[full finite certificate](https://github.com/aliromman/integer-mult-bounds/blob/6dbe6e9503f26189833d5ef213aee708679835f2/research/fifteenth-root-column-capacity/RESULT.json)
and [checker](https://github.com/aliromman/integer-mult-bounds/blob/6dbe6e9503f26189833d5ef213aee708679835f2/research/fifteenth-root-column-capacity/verify.py).
All 28 source package files remain byte-exact. The full verifier runs
unchanged. The source exact capacity is an input to the all-power
corollary; it is not claimed again as a new finite result.

The retained source includes Ali Romman's
[PR #7762](https://github.com/CrocSwap/integer-mult-bounds/pull/7762)
[eight-root census and projected-star proof](https://github.com/aliromman/integer-mult-bounds/blob/d33fe8562c86888307cbba4a2aa92490212c8d78/research/mixed-cycle-column-obstruction/PROOF.md),
and the motivation in
[PR #7768](https://github.com/CrocSwap/integer-mult-bounds/pull/7768)'s
[general defect bound](https://github.com/aliromman/integer-mult-bounds/blob/fefebaf8285f3c46f75a815657acbf48780763fb/research/mixed-cycle-column-defect/PROOF.md).
The new descent proof does not use the latter spectral bound.

Nick Petalas (@petalas) supplied the two-prime projection and original
completion question in
[PR #7744](https://github.com/CrocSwap/integer-mult-bounds/pull/7744).
Its [proof and question](https://github.com/petalas/integer-mult-bounds/blob/7dc85513e8ee9b771a5856f027cf199936f85af0/research/two-prime-column-completion/README.md)
and checker remain in the source closure and replay unchanged. All
predecessor notices, earlier completion credit and David Ganz's atlas
credit remain intact.

T. Y. Lam and K. H. Leung supplied the classical two-prime minimal-cycle
classification in
[On Vanishing Sums of Roots of Unity, Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=8).
It is an explicit mathematical input to the new all-power proof.
Cyclotomic polynomial arithmetic, Fourier triples and phase-gauge
invariants are also classical methods, not new general theory.

SOURCE-PINS.json authenticates the retained closure; SOURCES.json records
canonical-main provenance. Source commits are content pins, not ancestry
claims. No global literature priority is claimed.
