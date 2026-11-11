# Intermediate carries on one row of the frame-506 inverse elimination

**Proof, plus three exhaustive finite censuses. No new κ.** The selected
frontier stays `363005817/100000000000`.

## Result

The published frame-506 elimination has 5 swaps, 5 scales and 14 shears. Its
inverse is an elimination word for `S^{-1}`. PR #4957 does not fix that word
as the physical return. Each scale and each shear emits one carry digit on a
low row, under the quotient `(z - h) / q` from PR #4957, section 3. A swap
emits none.

- On every low row, and for every odd integer `q`, at most **19** of those
  digits are nonzero. Nineteen is strictly less than 48.
- On the #7104 return row `u(q) = (q-2, q-2, q-5, q-5, 0, q-1, 0, 0)`, exactly
  **13** digits are nonzero for every odd integer `q ≥ 5`. The digits are
  constant for every odd integer `q ≥ 7`, and the single row `q = 5` differs
  in two sites while keeping the same count. The digits are attached to the
  19 factors in [PROOF.md](PROOF.md).
- Those 13 quotients compose to the 6-nonzero closed-form correction of #7104.
  The closed-form route envelope remains 48. This note counts one row of one
  word.
- Exhaustive base-`q` censuses give maximum 18 at `q = 3` (domain 6561),
  maximum 18 at `q = 5` (domain 390625) and maximum 19 at `q = 7` (domain
  5764801). The bound 19 is attained, and every row in those domains is still
  below 48.

## Task

Catalogue card `supplier-boundary-audit`, scope **refined**. The open question
answered here is question 1 of PR #7104: the intermediate digits of an
elimination word for `S^{-1}` on one high row. The 48/96 closed form and the
published 64/128 envelope are left as proved. Question 2 of #7104, a charged
bill that moves an exponent, is not taken.

Base `e54523517d0f03e58352e647c403a5af3e525a57`.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/frame506-inverse-row-carries/verify.py
python3 -B scripts/research_package.py --package research/frame506-inverse-row-carries
```

The direct checker prints `PASS_FRAME506_INVERSE_ROW_CARRIES`.

## Open next questions

1. For which odd primes is the one-row maximum exactly 19? The censuses give
   18 at `q = 3` and `q = 5`, and 19 at `q = 7`. The next finite domain is
   `q = 9`, with `9^8 = 43046721` rows, under the same base-`q` scan. No
   algebraic blocker is known; this package stops after the three recorded
   domains.
2. Does some other elimination word for `S^{-1}` emit 48 or more nonzero
   intermediate digits on one row? The 19-site bound uses this inverse of the
   published 5/5/14 word. A longer factorization has more sites. PR #4957
   does not designate another return word, and this package does not search
   one.

## Credit

The matcher, the 5/5/14 elimination and the carry formula are from PR #4957
(Chris R / Clear1nsight, with the retained #4760/#4814 lineage). The named
row and the closed-form correction it composes to are from PR #7104.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
