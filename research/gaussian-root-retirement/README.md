# Independent Gaussian retirement: conditional κ = 0.00329394

The complete caller returns one central Gaussian output before its two-stage
suffix. A fresh independent input then uses that suffix. On each of 104 ports,
this replaces one rank-17 target with independent rank-1 and rank-16 targets.
Every paid Gaussian call stays in the invoice.

The conditional claim is **κ = 0.00329394**. The increment over
[PR6529](https://github.com/CrocSwap/integer-mult-bounds/pull/6529),
κ = 0.003288299, is **0.000005641, or 0.17154766%**. This percentage excludes
all gains in the source chain. The requested 1% gain is not achieved.

| Complete invoice | PR6529 | This caller |
|---|---:|---:|
| Independent caller fields per port | 34 | 35 |
| Caller events | 570 | 609 |
| Productive fields, with native helpers | 13,652 | 13,756 |
| Paid Gaussian jobs | 67,096 | 67,096 |
| Full native calls / thin queries | 18 / 17 | 18 / 17 |
| Rank-mass surplus | 760 | 760 |

The target change is `104(H1 + H16 - H17)`, where `Hr = r^(1-κ)`.
It is positive for every exponent strictly between zero and one. The source
native word, its helper targets and its owned lifetimes stay fixed. All added
basis gates, routes, output normalizers and the additional public field enter
the complete ordinary-work allowance.

Start with [PROOF.md](PROOF.md), [retirement.py](retirement.py) and
[WITNESS.json](WITNESS.json). [RESULT.json](RESULT.json) records the exact
caller, phase, price, compiler and outer checks. [RESEARCH.md](RESEARCH.md)
states the scope of the discovery and the limit of this fixed invoice.

## Evidence

The forward polynomial replay checks all 1,225 coefficients over
`Q(i)[Q,D_1,...,D_18]/(Q^4-1)`. A separate reverse-row engine checks the same
complete map. Both dual-pair identities and both literal basis maps are checked.
The fresh input is arbitrary; it is not prepared zero storage.

The source replay regenerates PR6529 and retains its checks and controls. It
checks all 799 native columns, 2,939 native maps, 208 main adapters, and all
7,488 physical contacts. The candidate then checks all target phases, all
whole idles, both rational price engines, the uniform compiler, and all
54 strict plus four functional outer predicates. See [VALIDATION.md](VALIDATION.md)
for the executed commands and publication status.

The unique raw crossing for this fixed invoice lies in
`(0.00329394637095319036829691, 0.00329394637095319036829692)`.
The claim uses the tested saving `0.003293945`, below that interval.
This is a ceiling for this invoice, not for other words or callers.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-root-retirement
```

The package needs only the standard library. Both normal and optimized runs are
registered. The two source archives contain every runtime input, with original
paths, heads, Git blobs, SHA256 hashes and notices. The adapter checks preserve
all source checks. Explicit engine dependencies use the interfaces from PR6524;
no imported function or class is patched.

## Scope and limits

This is an author-checked conditional construction. It is not independent
scientific acceptance, a formal proof of the full multiplication theorem, or a
measured runtime gain. The five inherited framework assumptions remain:
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and
`analytic_recovery`. The large uniform word and rounded multiplier are not
materialized. The selected frontier is unchanged.

The source stack includes pending PRs. Passing the registered replay does not
admit that stack. The new result improves the caller boundary; it does not prove
optimality over other cuts, native words, target groups or query networks.

## Open next questions

- Can another caller return a larger Gaussian factor at a legal intermediate
  cut? First test exact dual pairings on a changed word and write its complete
  target and paid invoice. The present fixed word has little remaining price
  headroom. A favorable numerical screen is not a caller.
- Can a repeated Gaussian-assisted interface have a favorable complete cost?
  First supply exact transition matrices, a closed endpoint and native helper
  delivery. The current small-state searches do not supply such a cycle.
- Can an independent reviewer check the prefix identities and the 104 physical
  output normalizations? The small basis and separate reverse engine provide
  bounded entry points. Full framework admission is a separate task.

## Credit

New construction, proof and package: Ali Romman with substantial OpenAI Codex
assistance; no subagents. Apache-2.0. The independent handoff method comes from
PR5599 and the PR5602/5611/5615 line. The root comes from PR6398 and PR6348.
PR6529 supplies the complete native word; PR6524 supplies the replay engines.
Credit Cinna Davis, Jacob Alan Sussman, Rohan Arun, Erwan L., DreamingOfClouds,
David Arias, Gareth Davidson, Mason Hale, Pierre-Loic Doulcet, Chris R /
Clear1nsight, zxv, Cao Yifan, and all authors in the retained notices.
[NOTICE](NOTICE) gives the source links and attribution boundary.
