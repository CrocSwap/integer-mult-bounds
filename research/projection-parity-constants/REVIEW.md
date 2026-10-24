# Independent mathematical and verifier review

Verdict: **scoped pass**. A separate Codex review agent found no substantive
mathematical error in the stated recurrence theorem or the finite verifier.
This is an AI review, not independent human review or proof-kernel verification.

The review started from the written proof and source recurrence, without the
solver's reasoning transcript. It checked the operator reduction, seed system,
generating equation, both q-Gauss substitutions against NIST DLMF 17.6.1,
product simplifications, meromorphic continuation, pole subtraction, index
shifts, finite-product expansions, and all three rational sums. Subtracting the
pole parts at 1, +/-2, and +/-4 leaves an analytic remainder on |z|<8, which
justifies the claimed O(4^-n) coefficient remainder for each fixed mode.

Independent Fraction calculations checked transformations for modes 1 through
9, telescoping products for modes 1 through 4 and blocks 4 through 34, the seed
system, and the three rational constants. A separately written original integer
recurrence through block 100 corroborated the two limits and remainder order.

## Verifier execution and enclosure review

CPython 3.12.14 runs with `-I -X dev -W error -B` and with the additional `-O`
both passed. Their outputs were byte-identical to the reviewed RESULT.json:
2,691 whole-profile equalities, 276 product identities, 520 transformations,
32 generating-series enclosure comparisons, 16 residue checks, and six rejected
negative controls. Checks use explicit exceptions and remain active under `-O`.

The interval tails are justified on the tested domains:

- For j>=1, the transformed recurrence has nonnegative coefficients whose sum
  is at most one. Induction gives 0<=v_n<=1 for all n, validating the ordinary
  generating-series truncation bound.
- For |z|<=1/2 and ell>=terms>=j+4, the explicit q-series term ratio has modulus
  at most 1690/6477<1/2. Twice the first omitted absolute term bounds its tail.
- For j>=1 and ell>=3, the negative-residue term ratio has modulus at most
  5/12<1/2. The helper now guards this domain; the tested truncation is 80 terms.
- The K interval follows from the product-tail inequality in the proof.
  The displayed decimal intervals were checked to contain their exact rational
  endpoints; every displayed `absolute_gap_upper` rounds upward.

The six controls fail for their intended reasons: an altered seed coefficient,
omitted second subdiagonal, altered raw seed, perturbed eigenvalue, reversed
parity, and doubled residue factor. Their failure locations/messages were
inspected separately; no incidental exception accounts for these rejections.

The terminating-series wording was clarified: all terms with ell>=j vanish.
Ordinary decimal rounding of enclosure bounds was replaced by directed rounding.
No unresolved substantive finding remains.

## Scope and exact reviewed files

Series-interval overlap is compatibility evidence, not an identity proof.
The eleven asymptotic samples and their threshold 32 do not establish a
universal numerical remainder constant. The universal theorem still relies on
the written analytic argument and classical q-Gauss summation. These six
controls are targeted perturbations, not exhaustive fault coverage. Global
novelty, engine interpretation, hook ranks, physical implementation, and any
multiplication-bound claim are outside this review.

SHA-256 hashes bind this review to these exact files:

| File | SHA-256 |
|---|---|
| PROOF.md | `ebb51aae7d58a69242c09b5334d02bd8178358cb2383ce90f38748e323e31ab0` |
| verify.py | `77a36f5a328da71153f747284d318ac12a0fb9df16ffc06cbc75de7aaa40692d` |
| RESULT.json | `cb48d1611d8f3d0ab77f084800b96881d934aca7efd11b7136f7f5196490a3e0` |

Reviewed against the source snapshot
`ff3cc58e370d0f678e529246f8c73e8094e18fcf` and
<https://dlmf.nist.gov/17.6.E1>.
