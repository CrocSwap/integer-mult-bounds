# Current contracts and research status

Updated October 8, 2026. The latest conditional witness is
**kappa = 373/10^11 = 3.73e-9 > 2^-28**, contributed by Zhihao Chen
(jacklightChen), with GPT-6 Astra (OpenAI Codex) assistance as identified by
the contributor. The [review guide](prime-field28.md) records the construction,
verification boundary, prior contributions and requested research attribution.

The ternary five-subset interchange has `a_b = 3/400000000`, and the paired
complex producer has `a_c = 39/10^9`. Both use h=28. The exact assembly witness
uses epsilon=4999/10000, c=9999/10000, beta=19/25, delta=1/10^6,
zeta=1/10000, C1=19601/10000, lambda=1-749/10^11 and
lambda'=1-748/10^11. All 29 constraints and seven final margins are strict.
The minimum margin is 934813/250000000000000, exceeding kappa by
2313/250000000000000.

Reproduce with `make verify` and `make prime-field-note`.
See the [certificate](../../certificates/prime-field28.json),
[proof note](../../artifacts/prime-field28-note.pdf), and
[independent source patch](../../patches/prime-field28.patch).
The pinned upstream theorem and retained interfaces remain assumed; these
checks do not constitute independent review or formal verification.

The earlier status below is retained as historical context. Its statements
about a ceiling apply only to its fixed older networks and inequalities.

---

## Historical compact-control status

Updated October 7, 2026. Author: Douglas Colkitt. All results remain conditional
on the pinned upstream algorithmic interfaces and the identified written
extensions. Nothing in this page asserts formal or independent verification.

## Current and earlier results

| State | Exponent saving kappa | Artifacts |
| --- | --- | --- |
| Published baseline | `2^-59` | [paired note](../../artifacts/paired-note.pdf), [certificate](../../certificates/paired-network.json), [patch](../../patches/h50-paired-59.patch) |
| Current conditional research draft | `83/10^12 = 8.3e-11 > 2^-34` | [proof note](../../artifacts/compact-control-note.pdf), [source](../../notes/compact-control-note.tex), [certificate](../../certificates/compact-control-layer.json), [patch](../../patches/compact-control-34.patch) |

The new witness increases kappa by approximately 47,846,242 times over the
published `2^-59`. This compares asymptotic exponent savings, not practical
runtime. The dyadic statement `kappa=2^-34` is a weaker convenient corollary.
The witness remains below `2^-33`. The earlier published artifacts and pinned
source remain unchanged.

## What changed

The finite bit network is unchanged: `h_b=50`, `m_b=125000`, with
`a_b=1-tau=296/10^11`. The new movement construction swaps compact dirty
control fields, rather than the full spaced slots. For f selected axes it
costs `O(V*((f log p)^tau+1))`, including deterministic repair, under the
layer's record regime and the supplied reservation layout.

Two front fields and one back field are carved out of already existing
address chunks. Their selected kernels are processed individually first.
They remain outside the row index divided among roles, so each child retains
the complete compact ranges and still receives exactly `V/W` volume. The
extra preprocessing is `O(V*(log d+d^(1-c) log p+1))` for the chosen `c<1`.
No independent address coordinates, zero-temporary assumption, or free
gathering operation are used.

The complex network uses its original construction independently at `h_c=25`,
`m_c=15625`, supporting `a_c=1-sigma=418/10^12`. The separate-arity proof is
now integrated into the source patch. The generalized stopped-depth guard
has `C1=5-4 beta+zeta`. Compact operations only permute complete coefficient
encodings, so they do not increase the coefficient arithmetic depth.

## Exact current parameters and bottleneck

The certificate uses

    epsilon = 1999/10000, c = 1/5,
    beta = 1/1000, zeta = 1/10000, delta = 1/10^6,
    C1 = 49961/10000,
    lambda = 1-1671/(4*10^12),
    lambda' = 1-167/(4*10^11),
    kappa = 83/10^12.

The internal, leaf and reservation exponents are respectively

    chi = tau+(1-beta)*max(sigma-tau,0),
    leaf = sigma+beta*(1-sigma),
    reserve = max(1-c,0).

All lie strictly below lambda' after the stated intermediate-lambda checks.
All seven final margins exceed kappa. Their minimum is

    G = g3 = 333833/(4*10^15),
    G-kappa = 1833/(4*10^15) > 0.

The former quadratic restriction from `K^tau` has been removed by this
construction. The remaining limiting margin is the completed layer's saving,
controlled here by the complex network's stopped leaves. The unchanged h=25
complex motif and retained Gaussian/leaf inequalities have the scoped upper
bound `kappa < 8.369598075e-11 < 2^-33`. Our simple rational witness is above
99% of that upper enclosure. It is not an unrestricted algorithmic ceiling.

## Verification boundary

The general proofs are in the four included construction sources:

- [movement and deterministic repair](../../notes/compact-control-movement.tex);
- [reservations, row splitting and recurrence](../../notes/compact-control-layout.tex);
- [generalized guard](../../notes/compact-control-guard.tex);
- [independent complex interface](../../notes/independent-complex.tex).

The [publication review guide](compact-control-review.md) maps each new
obligation to its proof and tests. Release copy and citation metadata have
been updated for this draft. This preparation is not independent review.

The certificate stores their SHA-256 hashes. The standalone note supplies
the complete assembly comparison and scope. The combined patch also updates
the old global exceptional-stream paragraph: a `p^-3` bad fraction is charged
locally through the volume-weighted recurrence, rather than incorrectly
reusing its old global `o(V)` argument based on `2^-K`.

Finite tests cover dirty address algebra, both slot orders, modular inverses,
bad-set invariance, exceptional repair, actual two-piece stream rotation,
complete-field preservation through padding and recursive row splits,
recurrence summation for all exponent orderings, and negative parameter cases.
Source integration checks preserve legacy appendix references and distinguish
the bit and complex arities. These checks support the written conditional
proof; they do not prove the upstream theorem or replace mathematical review.

Completion checks passed: all 163 tests, all 17 patch-application checks,
the nine-page standalone note build, and the combined manuscript build.
Publication preparation also ran the full suite in a separate snapshot with
all proposed files and confirmed exact regeneration against its Git index.
These are reproducibility and consistency checks, not independent proof review.

Reproduce with `make verify` and `make compact-note`. The combined manuscript
can be materialized with `make_compact_control_patch.patched_files()` into a
copy of `upstream/build`, then compiled with Tectonic after omitting the three
original pdfTeX-only metadata commands in that disposable copy, as described
in [the reproduction instructions](../reproducibility.md). The pinned source
itself must remain unchanged.

## Next research priority

First seek independent review of the new primitive, especially the temporary
layout invariant, local repair summation and uniform tape bounds. A substantive
flaw in one of those steps would revoke the new headline.

If the proof survives, improving the complex finite network is the next route
to a stronger dyadic bound. The incidence/shared-sum/paired bit constructions
cannot simply be copied into it: the scalar coefficients, binary phase labels,
residual orthonormal bases and signed endpoint corrections require a new audit.

The previous [joint-frame obstruction](joint-frame-audit.md) remains valid
within its fixed-boundary, grouped-gate scope. Splitting central gates or
changing boundaries between invocations are still possible finite-network
experiments, but the compact-control movement goal has succeeded conditionally
without needing that fallback. Older research pages retain their chronology;
use this page when interpreting their stale numerical targets or priorities.
