# Independent lead review of the paired-root result

Prepared for @CubeJerry with substantial OpenAI GPT-6 Astra assistance.
This is a separate AI mathematical review and separately implemented exact
finite-field check. It is not blinded discovery, human acceptance or a
proof-kernel verification. The reviewer read the author's argument and did
not import the author's or predecessor's scientific code into the new checker.

## Mathematical findings

The commutant correspondence is valid under the stated hypotheses. The
full/full Gram blocks give one common two-dimensional action, while each
thin unit imposes its two eigenline conditions. In the reverse direction,
commutation of the block-diagonal lift with the full Gram matrix preserves
its kernel. The identity `ker(YX)=ker X`, justified by injectivity of `Y`,
makes the quotient map well-defined. Surjectivity of `X` supplies the
second intertwining identity. Full span follows from the original product
being minus the identity; it is not an extra assumption.

The reflection-duality implication was checked directly from
`G K^-1 G=G`, hence `(K-G)K^-1(K-G)=K-G`. Cancelling its full-rank two-factor
decomposition gives the two-dimensional reflection product. The converse
follows from complementary projections. This verifies the dependency used
from #6888 rather than inferring validity from its open PR status.

The zero/two-thin classification uses eigenprojections over the stated field,
where two is invertible. A review correction made thin-vector rescaling
explicit before identifying scalar sign-matrix blocks. The four-thin
construction works for both parities: ABAB has the required product for even
full-stage count, while ABBA has it for odd count. Both have scalar dual
commutant. The revised proof includes these details.

The large witness's eight-dimensional full-stage commutant is exhaustive:
the span of the full columns and the common kernel of the full rows are a
direct sum because their full Gram block is invertible. Every commuting
map preserves both summands. Cross-Gram relations force a common 2 by 2
action on the first summand; the second has an arbitrary 2 by 2 action.
The subsequent thin equations therefore test the whole primal commutant.

The connectivity example distinguishes individual rank-one summands from
grouped native stages. It does not imply a prior author asserted an invalid
general theorem. Neither a dyadic basis, compatible masks nor a cheaper
caller follows from the decomposition result. The target/query cancellation
is an exact formal invoice identity. No new kappa or caller admission follows.

## Separate finite-field stress check

`independent_modular.py` constructs dual rows and columns independently,
forms their signed Gram matrix and obtains a minimal primal factorization
by modular row elimination. It multiplies every actual primal transvection
and solves all matrix-entry equations `S R = R S` directly for grouped
primal operators. It does not determine the commutant dimension from the
two-dimensional theorem being checked.

The fixed domain has 45 cases: primes 3, 5 and 7; `(full pairs, thin units)`
equal to `(3,0)`, `(2,2)`, `(3,2)`, `(2,4)` and `(3,4)`; and deterministic
seeds 78, 79 and 80. Each case uses separately selected invertible full-pair
bases, conjugated/scaled thin vectors and ordered thin placements. Exact
primal commutant dimensions are respectively 4, 2, 2, 1 and 1. The odd
four-thin case uses ABBA. Controls reject a wrong reflection product and
the explicitly excluded characteristic two.

Run this check alone with standard-library Python:

```sh
python3 -I -B research/p104-paired-root-commutant/independent_modular.py
```

Expected final line: `PASS_FINITE_FIELD_COMMUTANT_STRESS`. The registered
package command also runs it. This bounded modular domain supplements the
written proof; it is not an exhaustive field, gauge, placement or mask search.
The author's rational fixtures separately bind the retained 38-field mask
and invoice comparison. Neither check verifies inherited native, BIT,
fixed-tape, erasure or multiplication assumptions.
