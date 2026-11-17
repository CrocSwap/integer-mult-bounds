# An exact three-term Gram-class design on the A_3 line system

This contribution was produced by Nick Petalas. Apache-2.0.

DreamingOfClouds' [P104 duality and Gram-floor note](../../research/p104-duality-ceiling-flag-note/README.md)
defines a Gram-class price model on line systems and shows at A_2 that the
naive transfer "Gram price at least the identity-decoder price" is false: the
Gram value there is 4 (section 4 of [THEOREM.md](../../research/p104-duality-ceiling-flag-note/THEOREM.md)).
That note states A_4 and every n >= 3 as outside its scope. This package adds
the next explicit data point.

**Result.** On the A_3 line system (four coordinates, six lines, mask N = I)
there is an exact three-term Gram-class design

```text
u_1 = (0, 0, 1, -1)        w_1 = (-1/2,  1/2,  1/2, -1/2)
u_2 = (0, 1, -1, 0)        w_2 = ( 1/2,  1/2, -1/2, -1/2)
u_3 = (1, -1, 1, -1)       w_3 = ( 3/4, -1/4, -1/4, -1/4)
```

with `sum_k u_k w_k^T = Pi_4 = I - J/4` over the rationals and term prices
**3, 3, 2**, for a total price **8**. The natural dual-basis design of the same
shape, `u_k = e_k - e_4` with `w_k = e_k - (1/4) 1`, is exact and costs
**3 + 3 + 3 = 9**, so the written design is strictly cheaper inside the same
model.

The declared finite family of three-term designs whose carriers are the 14
canonical representatives of the equality patterns on four coordinates (1812
full-rank triples) has minimum price **8**, attained by the written design. This
is a bounded enumeration, not a lower bound over all designs.

Claim type: exact finite certificate (a written design with exact rational
identity and prices) plus a bounded exhaustive enumeration of a declared finite
family. **Not** claimed: the exact minimum over all Gram-class designs, any
lower bound beyond the trivial three terms forced by rank, a new kappa, or a
supplier admission.

## Why the price rule is the predecessor's

For the A_n line system the even-inner-product mask is `N = I`, so the F2
mask-rank price of a term collapses to the number of lines on which both
carriers are non-constant. See section 4 of the predecessor's `THEOREM.md`,
which fixes this rule and the A_2 example; this package uses that rule only and
does not re-check the predecessor's proofs. The A_2 value 4 is reproduced here
as a control, not claimed as new.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gram-class-a3-three-term-design/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/gram-class-a3-three-term-design/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gram-class-a3-three-term-design
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gram-class-a3-three-term-design --check-source-history
```

The verifier checks the written identity over the rationals, the three term
prices, the dual-basis comparison, the A_2 control, the 1812-design enumeration
and three rejection controls. It prints a JSON receipt bound to the package
file hashes.

## Limitations

The enumeration is over one canonical representative per equality pattern, not
over all rational carriers. The exact Gram-class minimum on A_3 is therefore
open; 8 is an upper bound. The model is the scalar Gram price model with the
F2 mask-rank rule and says nothing about a physical word, caller, compiler,
native implementation, precision or restoration. No kappa changes.

## Open next questions

1. What is the exact Gram-class minimum on A_3? A lower-bound technique must
   handle arbitrary rational carriers, not equality patterns. Start with the
   four-term case, where the W factor has a one-parameter freedom
   `W = W_0 + q r^T`; a useful first step is an exhaustive price-multiset case
   analysis for totals below 8. Blocked by: no continuous lower-bound argument
   is known for this cost.
2. Is the A_n Gram-class cost `n^2` for every n, or does the A_3 value 8
   (against the dual-basis 9) start a systematic `n^2 - 1` family? Start by
   generalising the written pattern to n >= 4 and pricing it. Blocked by: the
   general pattern is not constructed.
3. Does the A_2 gap (Gram 4 against identity decoder 3) persist for some
   n >= 3, and at which n does a Gram design match the identity decoder? Start
   with n = 3 and the identity decoder cost 4. Blocked by: question 1.

## Related open work

No open PR is known to study the A_n Gram-class cost for n >= 3. The
predecessor's package is merged with its own A_4 note left open; this package
does not audit it.

## Credit

The model, the A_2 value 4 and the F2 mask-rank price rule are
DreamingOfClouds' (`research/p104-duality-ceiling-flag-note`). The A_2 control
reproduces their number. The explicit A_3 design, the dual-basis price
comparison and the bounded enumeration are new. Independent human or formal
review is unclaimed.
