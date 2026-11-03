# Sharp backward precision for the Newton bulk

The high-degree Gaussian Newton bulk has an exact per-addition precision law.
This answers [PR5900](https://github.com/CrocSwap/integer-mult-bounds/pull/5900)'s
second open question for the literal PR5825 falling-factor graph under an
explicit independent residue-lift error contract. The old uniform-precision
premise is unnecessary in this contract.

Let pi=1+i, R be the polynomial degree, p the required output precision and
h a pass number. The [proof](PROOF.md) gives the exact minimum at every one
of the n*2^n neighbor additions in that pass:

    D_h = max_(h<=k<=R) [k-2h+2+2 v_2(h binom(k,h))]
    q_h = max(0,p+D_h)
    exact minimum neighbor-ADD precision mass = n*2^n sum_h q_h

These minima are simultaneously sufficient. If q_h>0, one fewer digit at any
one addition has an explicit failing output coordinate. The largest maximizing
k supplies that coordinate. The formula includes factorial valuations and
cancellation; using only k=R can underestimate the exact demand.

For n=p=8,R=7, both offsets have q=(16,15,14,13,8,7,3) and exact mass 155648.
For n=p=16,R=15 the exact mass is 310378496. For every p>=R-1, the mass is at
least n*2^n*R*(p+1). Thus high degree remains expensive even with heterogeneous
precision. This is a scoped sharp cost result, not a new kappa or a universal
Gaussian lower bound.

## Error and source boundary

The graph forms F_h=(W-a-h+1)F_(h-1)/h and accumulates
`i^a sum_h (i-1)^h F_h`, with W=(nI-sum X_j)/2. An error after a neighbor ADD
may be any independent Gaussian-integer multiple of pi^q. Other operations
are exact. The proof tracks rational Gaussian denominators and the source's
final pi^n numerator normalization. It covers R<=n; the retained residual
caller uses R<n.

A deterministic rounding rule on an actual reachable lattice can have fewer
errors than this contract permits. No claim transfers to that smaller error
set without proof. Changed graphs, correlated errors, shared bulk/residual
work, physical routing, cleanup, complete bit-time tariffs and native/compiler
admission remain outside scope. The five selected assumptions remain.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -I -O -Werror -B research/newton-backward-precision/verify.py
python3.12 -B scripts/research_package.py --package research/newton-backward-precision
```

`precision.py` supplies `plan(n,a,degree,digits)`. It returns every exact demand,
an attaining displacement weight and the complete neighbor-ADD precision mass.
The executable domain is 1<=n<=128, 1<=R<=n and 0<=p<=10000. The proof covers
all stated integer sizes. The plan uses exact binomial integers; it needs no
2^n array or floating logarithm.

The verifier checks 1323 exact radial suffix stages against the closed law,
including dimensions through 128. A separate literal forward interpreter
checks 70 complete error columns and all 48 internal neighbor additions of a
signed complex fixture. It checks 196 one-digit failure witnesses, 20 words
with simultaneous permitted errors, eight invalid plans, and three exact
retained source pins. Gaussian valuation is checked by repeated integer
pi-division, separately from the norm formula. Ordinary and optimized outputs
must agree. These finite checks support the written theorem; they are not
independent human or formal proof-kernel acceptance.

## Provenance and overlap

Canonical base: 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority 8, selected
PR6030. The selected source-binding example passes. The changed card scope is
in TASK.json and the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19363141).
Live Discussion2750, current handoffs, open PRs and targeted all-state searches
were checked. The cached matches are PR5900's released high-degree question.
Sparse notes, arbitrary diffs and unpublished work remain coverage limits.

Exact attributed source excerpts are retained under source/. ORIGINS.json and
SOURCES.json record each original head, path, Git blob and SHA256. They are
contract and attribution inputs; no predecessor scientific replay is imported.
All runtime inputs are package-local, so no side-branch Git object is needed
in a clean checkout or export.

## Open next questions

TASK.json records concrete next steps. Supply a complete reachable-lattice or
dependent-error encoding if it permits fewer digits. Alternatively, change the
bulk graph and share work with the residual, with all source lifetimes,
denominators, operations and restoration costs charged. A new seed or interval
in this fixed error model cannot change the proved optimum.

## Attribution

Ali Romman, with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
David Ganz / Dugongue PR5813 and PR5815 retain the Gaussian/Newton construction.
Ali Romman PR5825 retains the graph and earlier uniform-precision boundary.
Nick Petalas PR5900 retains the sharp residual-prefix result and open question;
PR5890's endpoint denominator debt remains separate. All retained native,
precision, ownership and compiler credit applies. Boolean expansion,
Vandermonde's identity and valuation arithmetic are classical. New work is the
exact backward demand law, its attaining errors and complete neighbor-ADD bill.
