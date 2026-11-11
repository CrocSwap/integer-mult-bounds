# Endpoint maximum for one zero-to-D helper split

**Proof, with a finite exact corroboration. Selected κ stays `363005817/100000000000`.**

On a helper boundary from the zero subspace to a `D`-dimensional space, the contact-free rank bill `G` of `m ≥ 1` paths is convex in the intermediate dimension. Its maximum on every closed feasible interval `[A, B]` is `max(G(A), G(B))`, including when `A = 0` or `B = D`. An interior dimension, including a join or meet of three or four paths, cannot raise that bill. The argument is [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `p104-side-correction`. Scope status: **changed**. The card asks whether a legal causal split improves the complete productive/paid invoice. This package prices only the rank-bill factor in `research/p104-shared-native-helper-splits/EXPLORATION.md` and closes the sentence that an extremum at `0` or `D` still needs a separate integer search. A positive value of `G` is a rank-bill signal under the stated charge. Legality, ownership, ordinary cost and the selected exponent stay where the selected record left them. The actual question, the reason for the scope change and the stop rule are in [TASK.json](TASK.json). Pins are in [SOURCES.json](SOURCES.json). Base commit `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8.

Evidence classes:

1. **Proof.** Lemmas 1 and 2 and the theorem in [PROOF.md](PROOF.md), for every real exponent `0 < t < 1`, every `D ≥ 1` and every constant old charges `c_i`. The one-path sign corollary uses the charge `c = (b - a)^t`.
2. **Exhaustive finite census**, only on the domains named here. At `t = 1/2`, integer square roots are compared with a certified `isqrt` truncation whose error is strictly less than one unit per combined term. The domains are every `1 ≤ D ≤ 12` and every one-path window `0 ≤ a ≤ b ≤ D`; every ordered pair of windows for `1 ≤ D ≤ 6`; and every integer power `u^s` with `s = 2q - p`, `2 ≤ q ≤ 5`, `1 ≤ p < q` and `1 ≤ u ≤ v ≤ 40`.
3. The predecessor new-frame screens in `EXPLORATION.md` are a different, incomplete search. This package does not rerun them and does not use them as evidence.

`EXPLORATION.md` is cited, not vendored. Its bytes are outside [VERIFY.json](VERIFY.json) inputs.

This is session r271, item 4 of the ordered eligible list read on 2026-11-11. Open handoffs whose later post completes them, whose canonical artifact is an open pull request, or which say that no target was taken, are dropped, as are the delivered 19 October index, the H25 chain, and the 2 November review artifacts. Updated notes are one request. Three open handoffs remain, then the revision-8 next-decision rows, then unnamed catalogue cards:

1. Three signed added frames at seven calls (discussion comment 19377832, updating 19377345). The 11 November record still leaves the other profiles open. #6942 character-excludes only the all-old-once profile.
2. Eight-source singleton existence (comment 19537798, updating 19377982). The 11 November search is still inconclusive, and `28 ≤ f(8) ≤ 32` is unchanged.
3. Six-source depth-two block at `c = 7` (comment 19537594, updating 19384981). The 11 November search still leaves `c = 7` open.
4. **This package.** Complex helpers (`p104-side-correction`, `coverage-law-change`): the endpoint rank bill.
5. BIT (`bit-helper-contract`).
6. New decoders and interfaces.
7. Supplier audit (`supplier-boundary-audit`).
8. All-size audit (`uniform-transfer-audit`).
9. Verification tooling (`replay-runtime`).
10. `bit-new-register-model`.

Later conditional-κ review requests on #1166, including #7148, #7158, #7161 and #7244, ask maintainers to select a new exponent. Their canonical artifacts are open pull requests, so they are outside this list. Overlap search on 2026-11-11, with complete pagination of 566 open upstream PR records and 7234 discussion records, found no match for `contact-free transport` or `endpoint rank bill`. Closed work was searched through local notes and ledgers only. That report is a lead, not a novelty certificate.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/helper-split-endpoint-rank-bill/verify.py
python3 -O -B research/helper-split-endpoint-rank-bill/verify.py
python3 -I -B research/helper-split-endpoint-rank-bill/verify.py
python3 -B scripts/research_package.py --package research/helper-split-endpoint-rank-bill --check-only
python3 -B scripts/research_package.py --package research/helper-split-endpoint-rank-bill
```

Expected direct marker:

```text
PASS_HELPER_SPLIT_ENDPOINT_RANK_BILL powers=8200 half_rows=1729 positive_boundary_paths=132 full_span_zeros=90 two_path_rows=2057 two_path_strict_interior=406 kappa=363005817/100000000000 no_new_kappa=true
```

The registered replay is the first command. `make frontier7000-verify`, Lean, Docker and the 68-split discovery screens were not run.

## Open next questions

1. **Proper boundaries.** Does the same endpoint maximum survive when a paid path extends outside a helper boundary whose terminal dimension lies strictly between `0` and `D`? The curvature comparison in the proof uses both helper legs against the full dimension `D`. The smallest next step is one proper terminal together with one path whose upper end passes that terminal, then a direct comparison of `G` at the allowed endpoints and at one interior dimension. The zero-to-`D` formula does not apply.
2. **Published charges.** For the published 68-split word, is every remaining unsplit helper's feasible interval already nonpositive at both endpoints under its actual old charges `c_i`? The smallest next step is to evaluate `G(A)` and `G(B)` from the pinned witnesses, without a new geometry search. That payload is outside this package. A positive rank bill would still leave legality and the paid profile open.

## Credit

The rank-bill formula and the open endpoint sentence are from @CubeJerry's shared-native helper-split exploration, on the shared two-chain word from DreamingOfClouds in #6902. The basis-splitting lineage is Ali Romman's #5599. Retained native and compiler authors of that construction stay credited there. Prepared by unpaidmoon with substantial Cursor Grok assistance. No formal-kernel review and no independent human review are claimed. New work is Apache-2.0.
