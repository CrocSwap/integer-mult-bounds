# Exact comparison with the already published four-query branch

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. **No new κ.** This note restricts the novelty of this package after
a publication-stage overlap check identified an existing result on the fork.

## Existing result and priority

The fork branch
[research/20261106d-four-query-ceiling](https://github.com/CubeJerry/integer-mult-bounds/tree/research/20261106d-four-query-ceiling)
already contains `research/four-query-fragmentation-ceiling` at exact commit
`d87e4a38890f6962162d00a68031ab2476f58f6e`. The publication checkpoint confirms
that this exact head is open as CrocSwap/integer-mult-bounds#6766. Its GitHub
status is distinct from mathematical acceptance. The following pinned files
were read through targeted GitHub file access:

- [CONSTRUCTION.md](https://github.com/CubeJerry/integer-mult-bounds/blob/d87e4a38890f6962162d00a68031ab2476f58f6e/research/four-query-fragmentation-ceiling/CONSTRUCTION.md)
  already proves the same six-input four-query endpoint, including exact
  central-phase normalization and the complete local invoice.
- [ECONOMICS.md](https://github.com/CubeJerry/integer-mult-bounds/blob/d87e4a38890f6962162d00a68031ab2476f58f6e/research/four-query-fragmentation-ceiling/ECONOMICS.md)
  already proves the mixed old/new-node all-size ceiling for both COMPLEX and
  BIT. Its COMPLEX endpoint is `0.0033072446849`; its BIT endpoint is
  `0.0037667234776`. This package's economic replay covers COMPLEX only.
- [construct.py](https://github.com/CubeJerry/integer-mult-bounds/blob/d87e4a38890f6962162d00a68031ab2476f58f6e/research/four-query-fragmentation-ceiling/construct.py)
  supplies the literal word used in the exact comparison below. Its complete
  5,996-byte source is retained unchanged as `frozen/concurrent-construct.py`.
  Git blob: `45a6fb02d5b002a5694923d6071e4a1c43666316`; SHA256:
  `9fb33c8902a2ef8c603c342cc9c32da8d0aad3108df85bf536d77194a6513296`.

Accordingly this package does **not** claim first attainment of the four-query
endpoint, first resolution of the equal-orientation exception, first proof of
the complete mixed-tree ceiling, or a new BIT ceiling. The common local invoice
and the cancellation of complete independently paid suffix jobs are also
already in the existing branch. The comparison does not independently replay
that branch's entire economic package or its BIT certificate.

## Same source, phase convention and interface

Both constructions bind the exact caller from CrocSwap/integer-mult-bounds#6726,
head `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`, with SHA256
`e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c`.
Both use

    q⁴ = 1,
    λ = (1+i)/2 + (1−i)q²/2,
    S = λ q^−1,

and the same `LAMBDA(dst,−1); QUERY(dst,src,−1); LAMBDA(dst,+1)`
normalization, replacing QUERY by LOCAL for a native body call. Relabelling
the two native stages as L and R is the only stage-name change in the
comparison. All six input fields are independent in both words, and all
36 entries agree in the full Gaussian coefficient ring:

    (X,Y,A,B,E,F) ↦ (LR(X+SY), LRY, SLA, SLB, RE, RF).

The existing word's auxiliary module uses three ADD operations and two SCALE
operations around its queries. Our distinct three-shear realization uses
three SCALE operations and one SWAP. All of these ordinary operations occur
in the retained #6726 source alphabet. The exact counts are:

| Literal event | Existing six fields | This six fields | This four fields |
|---|---:|---:|---:|
| LAMBDA | 8 | 8 | 8 |
| LOCAL | 2 | 2 | 2 |
| QUERY | 2 | 2 | 2 |
| IDLE_ONE | 4 | 4 | 2 |
| ADD | 3 | 0 | 0 |
| SCALE | 2 | 3 | 3 |
| SWAP | 0 | 1 | 1 |
| **Bare total** | **21** | **20** | **18** |
| Two final auxiliary LAMBDA normalizers | 2 | 2 | 2 |
| **Normalized total** | **23** | **22** | **20** |

The two final normalizers act on A and B only and give auxiliary outputs
`q^−1 LA` and `q^−1 LB`. Both six-field maps retain the two R-only outputs
unchanged. Any enclosing tail that also normalizes those R-only outputs must
cancel that additional action; neither count silently includes such a tail.

The four-field form drops the complete independent E,F jobs and their paid
R idles. It is an explicit smaller interface, not a reduction from six required
arbitrary inputs to four while preserving the six-input contract. Its signed
target/paid invoice agrees with the six-field form because those whole jobs
cancel. The one-event reduction at the same six-field boundary is exact;
it is **not** a weighted physical-cost comparison or a shortest-word theorem.
ADD and SWAP need not have equal implementation costs. The query count,
native calls, body-idle inventory and complete exponent bill are unchanged.

## What remains distinct and independently reviewable

1. The explicit 20-event six-register word, with an 18-event four-register
   realization, differs from the already published 21-event construction.
   The full-phase comparison makes that limited improvement reviewable.
2. `verify_economics.py` uses a separately written directed-integer-square-root
   power enclosure. It reconstructs the native histogram, checks every finite
   split and total used in the COMPLEX exclusion, and certifies the unbounded
   tail. This provides a distinct exact arithmetic method for the already
   established scoped ceiling; the theorem and ceiling are not claimed new.
3. `independent_economics.py` separately checks the arbitrary-size root support
   invoice and both new-node orientations using rational logarithm/exponential
   enclosures. Its mathematical review is retained in ECONOMICS-REVIEW.md.
   Independence here concerns the implementation and reasoning used to check
   this package, not independent human acceptance or priority for the result.

## Reproduce this comparison

```sh
python3 -I -B research/binary-equal-orientation-fragments/compare_callers.py
```

Expected last line: `PASS_SOURCE_BOUND_CONCURRENT_CALLER_COMPARISON`.
The registered package wrapper runs this comparison normally and under `-O`.
It authenticates both sources, parses the existing `construct()` literal using
the Python AST without importing or executing predecessor code, and translates
its documented wrappers into the common exact interpreter. It checks both
six-field endpoints, the four-field variant, the three final-normalization
maps, all event counts, and characteristic-two specialization. Missing final
normalizers and reversed query phase exponents are rejected; the latter fault
would be missed by a q=1-only test. No scan over a wider construction class is
claimed.

The existing branch and its predecessors receive full credit for the shared
endpoint and broader all-size result. This package preserves the original
scope and inherited framework assumptions, and supplies no new supplier
admission or selected-frontier change.
