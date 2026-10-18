# Finite D10 torsion does not give a three-call inverse-rotation share

**Scoped exact negative result; no new `kappa`.** In the formal group algebra of the dihedral group of order 10, the target

`diag([st],[ts],[e])`

on three arbitrary binary scalar registers has minimum paid-call cost **four** when the only paid address labels are the two reflections `s,t`. The natural three-call overlap word `s,t,s` does not work, and exhaustive exact search rules out every word of at most three calls, with every rank-one idempotent scalar projector allowed. Four calls attain the endpoint directly.

This is a first finite odd-rotation quotient check beside the all-register `D_infinity` reflection tariff in PR #1911. It does not extend that theorem to other finite dihedral groups or register counts. It provides no native supplier mapping, compiler, hosting/precision invoice, conditional bound or selected-frontier change.

## Exact model and result

Let

`G = <s,t | s^2=t^2=e, (st)^5=e>`

be the dihedral group of order 10. Set `r=st`; then `ts=r^-1`. Work in the full formal group algebra `F2[G]`, whose basis is the ten group elements. Matrix products use the group multiplication in their coefficient convolution. No natural or permutation representation is used as a substitute for formal equality.

A paid factor is

`D_N(g) = I + ([g]+[e]) N`,

where `g` is either `s` or `t`, and `N=xy^T` is a rank-one idempotent in `M3(F2)`, with `y^T x=1`. Each factor costs one paid reflection call. There are exactly 28 such projectors. The endpoint identity is coefficientwise equality in `M3(F2[G])`; its third diagonal entry is `[e]`, so the dirty helper is restored exactly.

**Theorem for this finite domain.** The minimum is four. The direct word

`D_E00(s) D_E00(t) D_E11(t) D_E11(s)`

is `diag([st],[ts],[e])`. For the lower bound, the verifier checks every ordered paid-label word over `{s,t}` of lengths 0 through 3 and every choice of the 28 projectors at each position. There are respectively 1, 56, 3,136 and 175,616 candidates, with zero exact endpoints. Thus no three-call mechanism exists in this declared model; the calculation says nothing about longer alphabets, different groups or more registers.

The proposed `s,t,s` word has a tempting path interpretation: its first two labels spell `st` and its last two spell `ts`. The complete search shows that no choice of rank-one idempotents can simultaneously route those overlapping subsequences while cancelling all other group-algebra coefficients.

## Cost accounting and frontier scope

The baseline direct bill is 2 calls for `st` plus 2 for `ts`, total 4; the identity helper needs no call. Every paid factor, including any call used for cleanup, is included in the formal endpoint. The searched alternative allows arbitrary rank-one idempotents on all three roles, so it grants the full scalar projector alphabet at no additional scalar-operation charge. No other operation is allowed for free.

This one-unit candidate saving would be a 25% reduction of this tiny reflection bill if it existed. It does not. Even a positive local word would require a separate justified mapping to the selected bit supplier, full interface and hosting costs, precision, and recursive moment before it could affect `kappa`. The selected conditional construction remains `kappa = 836330098538459/500000000000000000`.

## Evidence and reproduction

Two separate standard-library engines evaluate the full formal endpoint. `verify.py` stores 3x3 binary matrices as nine-bit integers and multiplies against the precomputed finite matrix table. `independent.py` builds `D10` from its action on the five polygon vertices and stores each coefficient matrix as three row masks; its multiplication by a rank-one projector uses the outer-product identity `(A x)y^T`. Their encodings and per-level state digests differ. Both cover the full 178,809 words through length 3 and agree on zero hits. The exact counters and digests are pinned in `CERTIFICATE.json`.

Run:

```sh
python3 -I -B research/d10-reflection-sharing-seeda3def8/verify.py
python3 -I -B research/d10-reflection-sharing-seeda3def8/independent.py
python3 -I -B research/d10-reflection-sharing-seeda3def8/test_package.py
python3 scripts/research_package.py --package research/d10-reflection-sharing-seeda3def8 --check-only
python3 -B scripts/research_baseline.py
make selected-record-check
```

Expected markers include `PASS_D10_INVERSE_ROTATION_MINIMUM` and `PASS_D10_INDEPENDENT_PERMUTATION_REPLAY`. `--check-only` validates package metadata and source pins; it does not itself prove the minimum. The two verifiers perform that finite calculation. Registered CI requests Python 3.12; this host's available interpreter at packaging time is CPython 3.14.7.

## Task, selected record and overlap

- Accepted cycle seed: `a3def8e7b944810f5d933bfa65cba990`; track `bit-mechanisms`; task `bit-new-register-model`; priority revision 3.
- Exact base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Focused contribution PR: [#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953), open at handoff from head `4f3bdf7c` (the package and overlap record are the entire change).
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Selected `kappa`: `836330098538459/500000000000000000`; the baseline checker prints `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, not a cold selected-construction replay.
- The selected record points to review `docs/research/community-batch1099-review.md`, source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate `research/community-frontier1094-audit/ASSEMBLY.json` (SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`), and reproduction target `make frontier1094-verify`; these are pinned in `SOURCES.json`.
- Coordination claim: [Discussion #1167 comment 18926353](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926353); handoff goes there.
- Nearby work: PR #1911 at head `712593f82739203639d0a169b88c6bcac6f0590c` proves reflection tariffs for `D_infinity`, but explicitly does not descend to finite quotients. New open PR #1941 at head `5938ce3e91bbb8b5c2227af7976d444b2fbac7d4` proves tariffs for every **even** rotation order and explicitly leaves odd periods out. PR #1821 at head `a986127fa82b680a5bbb29f49fec4c8c3a944bde` is a D16 central involution; PR #1573 at head `0b8c5a69297c794f2de22c04494c83e41300ae36` is a D8 central-target theorem. PR #1870 at head `538d194e69420a6a773612e0b5ad0c94575f8aaa` exhausts S3 target pairs. Discussion #1929 comment 18925900 is the claim for PR #1941. The current result fixes odd rotation order `n=5` and the noncentral inverse pair, outside #1941's theorem.
- Overlap limits: the complete refreshed snapshot at 2026-10-14 14:56:57 UTC covered 601 open PRs and 575 Discussion records with no warnings; no D10/order-five target claim appeared. The latest mechanism-thread comments were separately re-read at 14:51:17 UTC, including the even-order claim and #1941's result. Code diffs and closed PRs beyond the local ledger were not globally searched.

Prepared with substantial OpenAI Codex assistance in scope selection, exact enumeration, independent implementation and writing. No independent human review is claimed.

## Open next questions

- Does the same inverse-rotation pair still have the direct four-call minimum in `D_{2p}` for odd primes `p >= 7`, or does another finite torsion order admit a share?
- Can a torsion-aware invariant explain the D10 minimum uniformly for all finite dihedral quotients without reproducing a separate finite census for each order?
- Is there a justified compiler/supplier operation that pays only the two chosen reflections and preserves this exact group-algebra endpoint? Without that link, no exponent change follows.
