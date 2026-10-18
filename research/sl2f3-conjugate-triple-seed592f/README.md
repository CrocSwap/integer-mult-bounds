# Exact five-call minimum for a binary tetrahedral register endpoint

**Scoped exact negative result; no new `kappa`.** In the finite nonabelian model below, the heterogeneous target `diag([i],[w],[w^-1 i w])` has exact paid-call minimum **five**. Its direct word costs five. An exhaustive exact search excludes every word with four or fewer factors, so this target gives no paid-call saving in this model.

## Model and complete bill

Let `G = SL2(F3)`, the 24 matrices of determinant one over `F3`, and work in the full formal group algebra `R = F2[G]`. Use

```text
i = [[0, 1], [-1, 0]],    w = [[0, -1], [1, -1]]    (entries modulo 3),
c = w^-1 i w.
```

The four paid address labels are `i`, `i^-1`, `w`, and `w^-1`; they generate all of `G`. A paid factor is

```text
D_N(g) = I + ([g] + [e]) N,
```

where `N = x y^T` is a rank-one idempotent in `M3(F2)`, so `x,y` are nonzero binary three-vectors with `y^T x = 1`. There are 28 such idempotents and therefore 112 paid factors. Each costs one. The three registers are all targets; there is no extra dirty workspace, clean state, COPY/ERASE, or uncharged paid call. Free scalar `GL3(F2)` mixing is allowed.

The target is

```text
diag([i], [w], [c]).
```

The direct word applies `i` to role 0 and `w` to role 1, then applies `w^-1, i, w` in that order to role 2. This is an exact five-call word. The element `c` has order four and shortest length three in the four-label address alphabet.

## Exact coverage

The verifier stores each of the nine entries as a 24-bit coefficient support, so equality means equality of every coefficient in `F2[G]`. All four-call words are covered by a meet-in-the-middle join of two-call prefix and suffix states. There are 12,544 ordered two-call words and 8,905 distinct exact states. For each distinct suffix state `B`, the verifier computes `target * B^-1` and checks exact membership in the complete two-call prefix table. This covers all `112^4 = 157,351,936` raw four-call words, including duplicates. The same suffix set checks every three-call word as a one-plus-two split; words of length zero, one and two are checked directly. In total, every word at each length zero through four is excluded.

Each factor satisfies `D_N(g)^-1 = D_N(g^-1)`, so the suffix inverse is exact. The fast rank-one transition is independently cross-checked against full coefficient convolution for all 12,544 two-call products. The complete rank-one idempotent set absorbs arbitrary free `GL3(F2)` changes of basis: augmentation `[g] -> 1` sends each paid factor and the target to identity, forcing the net free scalar map to be identity, and pushing each free map through a factor only conjugates `N` within the enumerated set.

The exact minimum is therefore five **only for this fixed group, generator alphabet, target, three roles, and one-call factor definition**. `CERTIFICATE.json` records the two-call state count and a digest of the canonically ordered states; exact tuple equality, not the digest, decides the joins.

## Reproduce

From the repository root with Python 3.12 and the standard library:

```sh
python3.12 -I -B research/sl2f3-conjugate-triple-seed592f/verify.py
python3.12 scripts/research_package.py --package research/sl2f3-conjugate-triple-seed592f
```

Expected verifier line:

```text
PASS_SL2F3_CONJUGATE_TRIPLE group=24 calls=112 target_minimum=5 pair_words=12544 distinct_pair_states=8905 short_witness=none
```

`verify.py --write` regenerates the deterministic coverage certificate after review. Normal replay checks the regenerated result against the committed `CERTIFICATE.json`. The package pins the exact three-register predecessor source and the selected record/catalogue provenance in [SOURCES.json](SOURCES.json).

## Predecessors, relevance, and limits

The source result remains the maintainer-reviewed conditional finite construction with `kappa = 836330098538459/500000000000000000`. Its review is [`community-batch1099-review.md`](../../docs/research/community-batch1099-review.md) (SHA-256 `7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb`); the selected source manifest is `research/community-frontier1094-audit/SELECTED-SOURCE.json` (SHA-256 `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`); the assembly certificate SHA-256 is `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`; its recorded reproduction command is `make frontier1094-verify`. This experiment does not use those supplier files, change the selected construction, or alter `kappa`.

The model descends from the scoped three-register abelian bit result in PR [#468](https://github.com/CrocSwap/integer-mult-bounds/pull/468), which explicitly excludes other address groups. The closest nonabelian predecessors are PR [#1822](https://github.com/CrocSwap/integer-mult-bounds/pull/1822), a Q8 repeated central-commutator pair, and PR [#1925](https://github.com/CrocSwap/integer-mult-bounds/pull/1925), Q8 mixed targets on three and four roles. This package changes the address group to its order-three binary tetrahedral extension and tests a heterogeneous `i,w,w^-1iw` target. It imports no predecessor implementation.

An eight-call result in the opening claim was narrowed before search to this smallest decisive heterogeneous endpoint, reducing the direct bill to five and the exhaustive saving threshold to four. The updated scope and exact budget are recorded in [Discussion #1999](https://github.com/CrocSwap/integer-mult-bounds/discussions/1999); the mechanism index is [Discussion #1167 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18929640).

The group elements are treated as unit-cost address labels in this finite model. Their physical realization, source access, compiler, frame conversions, hosting, precision, restoration in a selected supplier, and recursive-moment effect are not priced. The result supplies neither a multiplication construction nor a universal impossibility theorem. It is an exact negative result for one new operation alphabet and endpoint, prepared with substantial OpenAI Codex assistance; no independent human review or proof-assistant formalization is claimed.

## Open next questions

Does one arbitrary restored dirty scalar role lower the five-call minimum for this same `SL2(F3)` endpoint? That tests whether workspace sharing helps while keeping the nonabelian target fixed. A first step is to enumerate the four-role rank-one idempotents and screen exact depth-four meet-in-the-middle coverage against the unchanged direct word. The larger `4 x 4` formal matrix states and the missing physical address-operation implementation are the blockers.
