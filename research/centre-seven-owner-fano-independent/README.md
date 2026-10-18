# Independent check of the seven-owner centre-repair exclusion

**Independent verification. The audited claim reproduces. No new bound, supplier or κ.**

[`centre-seven-owner-information-floor`](../centre-seven-owner-information-floor/README.md)
claims that no nonzero perturbation invisible to both the old centre
observations and the later query field has support on exactly seven owners.
With the earlier six-owner result, this keeps the repair floor at 104
observations per owner for blocks of up to seven owners. The package was
archived on 2026-10-16 with no scientific replay. This package checks that
claim with a second implementation. For the central step, it uses exhaustive
search in place of the written argument.

## What is checked, and how it differs

| Step | Audited package | This check |
|---|---|---|
| 112 routes | Primary forward interpreter (`verify.py` path) | Chart-swap derivation in the predecessor's `independent.py` |
| Matrix products | 73 columns, hash buckets plus exact comparison | Exact 17×17 active block (spectator block checked to be the identity), row-major packing, exact dict keys |
| Relation census | Reduced triples, 50 classes of size 2 | The same quantity, recomputed. Histogram `{1: 1,379,852, 2: 50}` and the 50 braid edges agree with the receipt. Every relation word is multiplied out and gives the identity. |
| Support 7 forces a Fano plane | Written counting argument | Exhaustive search: of all line families on 7 points with line size ≥ 3, pair multiplicity ≤ 1 and point degree ≥ 3, the only ones are the 30 labelled Fano planes |
| Fano plane cannot be labelled | Written braid-pair / triangle-free argument | Exhaustive backtracking over all route labels of the 21 flags. Labels at each owner and on each line must be distinct. Each of the 28 six-cycles must read as a group relation. Result: no labelling. |

The labelling search uses only the relation words. It does not use the fact
that they are braids or that the braid graph has no triangles. Two controls
show that the search is not vacuous. A Fano labelling is planted in the group
Z2^4 (label = point code XOR line code). When only its 28 cycle words are
admitted, the search recovers it. When one relation class is removed, the
search no longer accepts it.

The six-cycle condition is necessary. For a cycle g–L1–h–L3–k–L2–g with port
labels a,b (at L1), c,d (at L3), e,f (at L2), the regular action
`source = output · ρ_p` gives `ρ_a ρ_b ρ_c ρ_d ρ_e ρ_f = 1`. The word is
cyclically reduced because distinct lines at one owner use distinct ports.
Each such word occurs as two distinct equal reduced triples, so the triple
census finds all of them.

## Scope and limits

The check covers the finite premises and the support-seven implication only.
It inherits, and does not recheck, three things:

1. The predecessor's support ≥ 7 argument and its column premises.
2. The source-bound observation model (`Sx = R x`, `Tx(d) = Σ_p H[:,p] x_p(dρ_p)`).
3. The faithful matrix representation of the regular cover group.

The chart-swap route derivation and the audited forward-interpreter routes come
from the same AI-assisted contributor lineage. They are separate code paths,
not separate human review. Blocks of eight or more owners, changed query cuts,
and all physical acquisition and restoration costs are outside this check.

## Reproduce

From the repository root, standard-library Python (measured: CPython 3.12 and 3.13, about 30 s each):

```sh
python3 -I -B research/centre-seven-owner-fano-independent/verify.py
python3 scripts/research_package.py --package research/centre-seven-owner-fano-independent --check-only
```

Expected marker: `PASS_CENTRE_SEVEN_OWNER_FANO_INDEPENDENT`. On the same host,
the audited package's own `verify.py` also passed, in about 60 s.

## Open next questions

**Does open PR #3147's block floor for 8 to 12 owners survive an independent
search?** [#3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147)
(head `5cbc48b18cb05327a8dacab3f626412d3bc5e924`) claims no hidden perturbation
on blocks of up to 12 owners. It also recounts the same 50 braid relations. Its
circle-cancellation part was audited in #3149/#3151; this block-floor part has
no independent check yet. First step: list the incidence structures on 8 to 12
points with line size ≥ 3, point degree ≥ 3 and pair multiplicity ≤ 1. Then run
`labelings()` over each, adding the length-8 relations from a reduced
4-against-4 product census where a structure has 8-cycles. Blocker: none for
the check itself; its relevance to κ stays gated by the replacement-endpoint
screen in the audited package.

## Credit

The audited claim, the relation census design and the Fano argument are from
the `centre-seven-owner-information-floor` contribution. The route interface,
the support ≥ 7 theorem and the chart-swap derivation are from
`centre-block-repair-information` (Aaron Wang/navinor's PR2391, Ross
Richardson). The selected `R/H` data are from ywz65's
`centre-owner-observation-floor`. Further lineage is credited in those packages.

Prepared by Sudarsh Chaturvedi, with substantial assistance from Claude
(Anthropic). No independent human review is claimed. Apache-2.0.
