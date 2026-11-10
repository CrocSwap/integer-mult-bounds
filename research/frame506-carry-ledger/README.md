# Sharp carry envelope for the frame-506 matcher

**No new κ.** The selected frontier stays `781451/250000000` from PR #6030.

## Result

For the integer matcher `S` of frozen frame 506 (helper 462 in the PR #4957
bank), the carry is the source correction `(g0 A - h0) / q` from that paper's
section 3.

- Columns 4 and 6 of `S` are unit vectors, and columns 0 and 3 of `S^{-1}`
  are unit vectors. For every odd prime `q`, each route therefore has at most
  **48** nonzero carry corrections, and the pair has at most **96**. The
  published envelopes are 64 and 128. Those larger numbers remain valid upper
  bounds and are not sharp.
- For every odd prime `q ≥ 5`, both 48s are attained by one explicit low type,
  so the pair attains **96**. The argument is the closed form in
  [PROOF.md](PROOF.md), valid for every integer `q ≥ 5`.
- At `q = 3`, an exhaustive census of all `3^8 = 6561` low rows gives forward
  maximum 6, return maximum 6 and joint maximum 11. Each route, taken by
  itself, still reaches 48 by repetition. No single low type attains both
  weights together, so the joint pair maximum on eight rows is **88**.

The quotient of the cleared matrix `4 S^{-1}` is a different function. At
`q = 5` one row has eight nonzero floors of that matrix and only five nonzero
inverse corrections. This note does not use the cleared-denominator count.

This prices one line of the route ledger for that fixed invocation. It does
not allocate a new owner, discharge P1–P3, implement the native compiler, or
move the exponent gaps. PR #4957 already treats a finite carry constant as
lower order once those gaps are positive.

## Task

Catalogue card `supplier-boundary-audit`, scope **refined**. Discussion #1166
comment 19137812 asks for one literal stock/owner/route ledger of the #4957
A0→A1 edge. This note prices the carry corrections of the actual frame-506
matcher inside that ledger. The 5/5/14 elimination word and the 40/40/112
high-row counts are left as published.

Nearby work that does not state this envelope: the shorter frame-506 word in
`research/frame506-short-route` retains a `2 N^2` carry schedule, and the
helper-462 words in PRs #6947, #6950, #6954 and #7012 change the factorization.
This note does not change the word.

Base `17469fff78c22941280f04d39dc5a1faee09c840`.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/frame506-carry-ledger/verify.py
python3 -B scripts/research_package.py --package research/frame506-carry-ledger
```

The direct checker prints `PASS_FRAME506_CARRY_LEDGER`.

## Open next questions

1. Does an elimination word for `S^{-1}` emit fewer than 48 nonzero
   intermediate carries on one high row? The first step is to attach a carry
   digit to each of the 5 scales and 14 shears. The blocker is that PR #4957
   does not fix that word as the physical return; the count proved here is
   the closed-form correction.
2. Can the 32-correction gap enter a charged ordinary bill that moves an
   exponent? The predecessor states that finite carry constants are lower
   order once its gaps are positive, so a local envelope does not by itself
   change that bill.

## Credit

The matcher, the 64/128 envelope and the helper-462 endpoint are from PR #4957
(Chris R / Clear1nsight, with the retained #4760/#4814 lineage). Prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
