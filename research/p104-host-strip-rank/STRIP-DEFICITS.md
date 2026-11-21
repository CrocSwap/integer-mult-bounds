# Excess-thin host-strip transition

Status: paper proof plus exact rational checks, **not kernel-checked** and **not a legal-caller or kappa claim**. The branch is independent of the `e=0, k=76` pricing work, as confirmed with that lane. All source excerpts are read-only copies of PR [#7852](https://github.com/CrocSwap/integer-mult-bounds/pull/7852), prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code, pinned to `41beda1d6435760dc99e38bd7e65f36798aad212`. They are credited with the signed-frame, set-RC2, and conditional deficit lemmas below. This note derives a small consequence and gives new examples; it makes no claim of global novelty against unindexed work.

## Published scope and chosen branch

* [`CallerSGram.sgForward`](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerSGram.lean#L246) derives `rank K + n <= |iota|` from the signed-frame product `P=-I` and characteristic different from 2. It is not a word-level theorem by itself; a legal odd-target word supplies this frame via the other source bridges.
* [`CallerExtraThin.deficit`](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerExtraThin.lean#L229) already proves `sum d_s + 2 <= rank Kh` when it is **given** `t0` with `d_t0=0`. [`rc2_set`](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/CallerExtraThin.lean#L95) already handles arbitrary partner sets and a supplied strip rank. These statements do not by themselves assert an e>=1 crossing.
* The pinned PR labels K15/K16 retain nondegenerate host blocks (`lambda != -1`); K16 additionally assumes `e=0`, tightness and degree at least one. Its own gap list states there is no proven k-crossing for `e>=1`, with direct-sum obstructions for `e>=2`. This result stays in the nondegenerate-host branch, including `e=1`; it does not resolve `lambda=-1`.

## Rank result

Let `K` be the signed-frame matrix, let `Kh` be its 2k-by-2k submatrix on k distinct two-column host slots, and assume every diagonal `Kh[s,s]` is invertible. Let `n` be the frame dimension, let `T` be the number of all other columns, and write

`e = (2k + T) - n - 2 >= 0`.

For stage s define `d_s = 2 - rank Kh[s, all host columns outside s]`. Since off-diagonal K blocks differ from the Gram G blocks only by a sign depending on the partner slot, this is also the deficiency of the corresponding combined G strip.

For **each** t,

`2 + sum_{s != t} d_s <= rank Kh <= rank K <= 2 + e`.                 (1)

Consequently, if `k >= e + 2`, at least one strip has full row rank and

`sum_s d_s <= e`.                                                     (2)

In particular, for **e=1, k>=3**, at most one stage has a deficient combined off-diagonal strip, and a deficient strip has rank one. Moreover each individual distinct-stage block has rank at least `max(0,2-e)`; for e=1 every pair block has rank at least one. For e=0, the pair-block statement reduces to the already published `thin_G_blk_unit`, so it is a control, not a new e=0 claim.

Proof of (1): choose d_s independent left-null vectors of each off-diagonal strip. Applying each vector to the two s-rows of Kh gives a row supported only on s; invertibility of `Kh[s,s]` makes these independent within s, and disjoint support makes them independent across different s. Include the two uncombined t-rows and only the supported vectors for `s!=t`. Projection onto the t block forces both t-row coefficients to vanish, then disjoint support forces the others to vanish. Thus their number is at most rank Kh. If all k deficiencies were positive, (1) would imply `k-1<=e`, contradicting `k>=e+2`; an index t0 with d=0 therefore exists, after which either (1) or the published `deficit` gives (2). For a pair block B=Kh[s,t], take the 4-by-4 submatrix with diagonal blocks A,D invertible and off-diagonals B,C. Its rank is `2 + rank(D - C A^-1 B) >= 4 - rank B`; bounding it by `2+e` proves the pair statement.

## Conditional role/piece consequence

Assume the mask support and `Pieces` hypotheses of `CallerExtraThin.rc2_set` as well as the frame hypotheses above. For each s take partner set T=all stages except s, and `l=2`. The shallow count is zero. Each counted deep role touches s and at least one other host stage and has the singleton piece `pc(r,s)={s}`. Applying `rc2_set` with a basis of the strip's column space gives at least `2-d_s` distinct such roles at s. Hence for `k>=e+2`, summing (2) gives at least `2k-e` qualifying **(stage, role) incidences**; in particular `2k-1` for e=1. This is a constraint on the stipulated piece model, not yet a caller-cost bound: roles can recur across stages and the matching from these pieces to actual priced records and correction terms remains to be proved.

The additional two-hub packing argument, including the e=0 and e=1 graph consequences and a three-host e=1 boundary frame, is documented in [TWO-HUB.md](TWO-HUB.md).

## Controls and exact frame separator

`check_transition.py` checks the actual `sgG`, `sgK` and stage-product formulas over rationals, pins five source blobs with `git hash-object`, and transcribes the source A3/B3 example. It also replays the set-RC2 count for every partner subset with the source's all-singleton `singP`; no general finite test is offered as proof of (1) or (2).

* A new three-host e=1 signed-frame boundary control is described in `TWO-HUB.md`; it has two universal hub roles and five local roles.
* Published e=0 control: n=4,k=3,T=0, `P=-I`, `(rank G,rank K)=(4,2)`, all six ordered pair Gram blocks have rank 2, and all strip deficiencies are zero.
* Exact e=1 frame: n=3,k=2,T=2,Q=1, `P=-I`, `(rank G,rank K,rank Kh)=(3,3,3)`. Both diagonal host K blocks are `[[1,-1],[1,1]]`, agreeing with the source type-B `a=-1,b=1/2` gauge (determinant 2), and each host's A and B column pairs have rank 2. Both off-diagonal Gram blocks have rank 1; both strip deficiencies equal one. The two thin stage transfers are respectively unipotent rank one and involutory reflection rank one, matching the separate algebraic kinds of QUERY and IDLE_ODD. With singleton pieces the host masks are `{0}`, `{0,1}`, `{1}` and each strip's set-RC2 count at l=2 is exactly one. These conditions do **not** prove that a single verifier-legal word realizes the frame: exact q^4=1 identities, inter-stage prefix, HOST contacts, stage D masks, bounds, and every priced correction remain unchecked. This witness refutes only the stronger *frame-level* assertion that e=1 alone forces a full-rank strip at k=2.
* Additional host-matrix-only examples show the `k>=e+2` threshold cannot be improved using just the matrix hypotheses: for k=2..6 and e=k-1, every diagonal block is invertible, every d_s=1, and rank Kh=k+1=2+e. Another rank-3 host matrix with k=3 attains `sum d=1`. Neither family is asserted to arise from signed frames or legal words.
* `--mutate` changes one QUERY-like column. The exact `P=-I` check then fails and the script exits 1, as intended. This is a transfer perturbation, not a comprehensive verifier mutation suite.

Reproduce (Python 3, SymPy 1.12, git):

```sh
cd .
python3 check_transition.py
python3 check_transition.py --mutate   # expected exit 1
```

The pinned package plain-Python static/data check also passed: 488 pinned files, 452 modules, 417 headline names, byte-identical FrameCert regeneration and five regenerated DRAT CNFs; see `pinned-package-python-check.log`. These checks mirror the published formulas and verify fetched Git blob identities. They do **not** invoke Lean or reproduce the 452-module kernel build: no Lean executable was found in this session. Advancing the result would require formalizing (1) and the set-RC2 corollary in the pinned Lean package, proving or disproving verifier-legal word realizability with all algebraic/D-mask constraints, and connecting the incidence law to an actual signed invoice. No complete caller has been repriced, and no conditional kappa gain is established.
