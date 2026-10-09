# Dual-suffix pair stars in the rational-center producer

Under **all of PR104's inherited and newly proposed interfaces** (as used by PR107),
this finite replacement gives conditional
**κ = 7988289348441/10^17 = 7.988289348441×10⁻⁵**, about **2.4348% above PR107**
(7798412662809/10^17) and 2.483% above PR104.

## What changes

PR104/PR107 bind on the **complex** (h=24, all-disjoint rational-center) producer:
its strict saving 7799647191/10^14 sits below the stopped bit saving
803380799/10^13. Each pair star `(a,b)` of that producer computes all 22
leave-one-out sums of `v_i = x_{a,b,i}` with the ordinary layout
`s_j = A_{j-1} + B_{j+1}` (prefix A, suffix B).

We replace only that block by the dual-suffix identity from the h23/h25 bit
strips of PR55 (credited there):

    s_j = (A_{j-1} + v_{j+1}) + B_{j+2}   (j < k),     s_k = A_{k-1}.

Each prefix `A_{j-1}` now feeds `A_j` and `A_{j-1}+v_{j+1}` whose covers nest,
so the unchanged legal carrier matcher (`scripts/endpoint_gauge/match_complex_general.cpp`)
joins far more additions. The coordinate order, center trees, rational divisor 21,
scatter, copied-center corrections, stopped bit axis and assembly are unchanged.

| h24 complex producer | PR107 | This |
|---|---:|---:|
| additions c | 45,548 | 50,572 |
| matched carriers | 8,750 | 15,422 |
| roles R = c + q − matched | 44,918 | **43,270** |
| strict complex saving | 7799647191/10^14 | **7989584037/10^14** |
| κ | 7798412662809/10^17 | **7988289348441/10^17** |

The bit parameter is min(stopped bit saving, (1−10⁻⁶)·b − 10⁻¹⁰) exactly as in
PR107, so the new binding is still the complex leaf, with 0.57% headroom left
below the bit axis.

## Checks

```sh
python3 research/dual-suffix-centers/verify.py
python3 research/dual-suffix-centers/test_controls.py
make verify
```

The verifier reproduces PR104's certificate, regenerates the PR104, PR107 and
new scalar/frame producers (every exact support, center, rational scatter and
binary frame nesting assertion is retained), recompiles the inherited matcher,
checks every histogram entry, then all 47 strict constraints, seven margins and
both next-grid exclusions (complex 7989584038/10^14 and κ 7988289348442/10^17).
Controls reject unpaid cleanup, omitted retained loss, and both the PR104 and
PR107 producer histograms at the new bound. Full repository verification passed on `e72978fa40fa01e23583c58d40e42dab316ddc1a` in 2436.677 seconds, completed 2026-10-09T00:35:17.720947+00:00: `make -j1 verify` (78 isolated test modules, 20 historical patch checks), fresh producer/certificate regeneration and six adversarial controls. All 39 research-head GitHub checks passed, with no source drift. See [validation.json](validation.json) for evidence hashes.

Scope: a finite conditional witness. The opposite-bank factorization, stopped
atom streaming and odd-denominator grid interfaces of PR104 remain written proof
dependencies, as in PR107. No global optimality or practical speedup is claimed.

Credit icekylinx (PR104 stopped product-ring / rational centers), the PR55
dual-suffix strip authors, Avi Eisenberg (PR53 skip-prefix strips), PR107, and
all predecessors credited in PR104's NOTICE and SOURCES. Prepared by Rohan Arun
with Anthropic Claude assistance, Apache-2.0.
