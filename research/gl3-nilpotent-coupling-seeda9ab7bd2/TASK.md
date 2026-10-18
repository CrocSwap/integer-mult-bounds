# Cycle 46 task card: expanded rank-one couplings

## Assignment pins

- Track `bit-mechanisms`; accepted OS seed `a9ab7bd2bdc2d83089d7ee5ca0948454`.
- Selector task `bit-new-register-model`, first suggested method: construct/test the smallest exact identity in a newly specified legal operation alphabet.
- Selector scope key `7f5f4426ef796683c485`; priority revision 4; catalogue SHA-256 `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- Exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Canonical claim: [Discussion #2285](https://github.com/CrocSwap/integer-mult-bounds/discussions/2285), expires 2026-10-15 05:29 UTC. Hub pointer: [#1167 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18939789).
- Selected conditional result: `836330098538459/500000000000000000`, binding side complex. Review `docs/research/community-batch1099-review.md` (SHA-256 `7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb`); source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json` (SHA-256 `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`, 1,579 entries); certificate `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`). Reproduction command is `make frontier1094-verify`, which runs `selected-record-check` then `scripts/verify_frontier1094.py --work <temporary-dir>/replay`. The selected cold replay was not run in this sparse worktree.

## Refined object and changed premise

Scope status: **changed**. The catalogue points toward another larger-register/nonabelian target family. The live board and open PRs show dense coverage of small finite-group target searches. This experiment instead changes the excluded register-coupling restriction and asks whether the added operations enable sharing in the already-specified GL3 CNOT address group.

Let `G = GL3(F2)`, with the six coordinate transvections `g_ij = I + E_ij` as paid labels. There are two arbitrary dirty scalar roles. A paid factor is

```text
D_N(g) = I + ([g] + [e]) N
```

where `N` is any nonzero rank-one matrix in `M2(F2)`: six rank-one idempotents and three rank-one nilpotents. Every such factor is an involution because `g^2=e` and the group-algebra characteristic is two. The changed operation assumption is that every rank-one conditional register update has equal one-call cost; no nilpotent helper or clean state is introduced.

For every ordered endpoint pair `(p,q)` whose coordinate-CNOT distances satisfy `d(p) <= 2`, `d(q) <= 2`, and `d(p)+d(q) <= 4`, test whether `diag([p],[q])` has a full-coefficient word shorter than its independent direct bill `d(p)+d(q)`. There are at most 31 endpoints per role (961 pairs total). A strict saving of one call is the experiment's target.

## Optimistic complete cost and stop rule

The direct bill is at most four charged rank-one calls. The optimistic candidate bill charges every expanded-alphabet factor exactly one call, all two roles are outputs, and no helper, copy, source-access, frame-transition, restoration, precision, or recursive-child expense is omitted inside this declared finite word model. A candidate with three or fewer factors saves at least one call. External supplier placement and any implementation cost beyond the stipulated rank-one primitive are not included; no `kappa` claim can follow from this package.

The alphabet has `6 * 9 = 54` factors. Exhaust all words through length three (at most `1 + 54 + 54^2 + 54^3 = 160,435` words) and compare exact coefficients in all 168 elements of `F2[G]`. Stop after this complete boundary: report a verified witness if one exists, or only the scoped floor over the declared endpoint set if none exists. Do not expand to longer targets or other groups this cycle.

## Predecessors and overlap

- PR #1974 (Josie Elliston), head `a4992da8e4e81a74cf1fd2b2d3af948662476d6e`, supplies the two-role GL3 mixed-target census and bounded three-register probe. Its relevant packages are `research/bit-gl3-mixed-targets-length10/README.md` (SHA-256 `f1f88a618fa998baa2bb5e8bc69c225405b6106b4c0a5646d84c42166cd4aff5`) and `research/bit-three-register-lower-bound/README.md` (SHA-256 `c12b33ef388deece0cbf891505a2ce2c0779a0c3a6cf1f0f7f7039bab59cbebd`); the scalar couplings are idempotent. This experiment adds the three nilpotent rank-one couplings and restricts endpoints to direct cost at most four.
- PR #2027 (Gareth Davidson), head `cd37822ee3523e53b645848644e0dae42d47abe7`, uses all nonzero rank-one couplings in a UT4(F2) mixed-root tariff. Its group, targets, register dimension, and proof obligation differ; it is the closest precedent for charging nilpotent couplings as native factors.
- PR #2167 (Wayne Nilsen), head `cea5d7be431b09877848354f04d5f2ba512339fd`, treats clean ancillas in the two-register `m=3` model, not this all-dirty expanded alphabet. Other close open PRs include #2246 (A5 conjugate 5-cycles), #2248 (Q8 three-role minima), #2261 (UT3(F4) commutator), and #2187 (C4 root lift); none matches this GL3/nilpotent-coupling endpoint domain.
- The latest complete cached overlap snapshot used 505 open PRs (fetched 2026-10-15 03:22:59 UTC) and 990 Discussions/comments (fetched 2026-10-15 03:26:31 UTC). A live GraphQL `gh pr list` immediately before submission returned 508 open PRs; title/body search found no GL3 nilpotent-coupling target match. A live Discussion search for `GL3 nilpotent` found this claim #2285, the UT4 tariff thread #1647, and the hub #1167. The fresh `find_overlap --refresh` process did not return within 78 seconds and was stopped; an earlier refresh had reported the REST API limit response. Cached helper results are labelled as potentially stale. The recent A5 claim in Discussion #2242 subsequently posted a FINDING/HANDOFF releasing its claim and is a different group/target.

## Evidence plan

- Enumerate the full 54-factor alphabet and all target pairs in the stated endpoint domain using packed exact coefficient states.
- Recheck the certificate with a separately written full-coefficient evaluator, including the direct positive witnesses, chronological-order negative control, and a control that removes nilpotent factors from the alphabet.
- Run the package check and the relevant repository metadata/certificate checks. Report the exact finite coverage, environment, selected-source limits, and any unproved native-supplier mapping.
- Any resulting contribution will disclose substantial OpenAI Codex assistance and preserve predecessor attribution.
