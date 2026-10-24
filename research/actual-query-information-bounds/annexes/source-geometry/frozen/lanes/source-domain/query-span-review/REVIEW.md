# Independent review of the query-span certificate

The frozen source theorem and its exact certificate pass this review.
No material finding remains. The accepted conclusion is a payload-query
count in the stated scalar gate grammar. It is not a lower bound on
native children or native rank in the supplier.

The reviewed proof has SHA-256
`785e27fdc6f2bcd83318afee14103f3e021065d32be2265b8afdec3fea3e1081`.
The reviewed producer and receipt have SHA-256
`bcc8bb5482c76578014512d51dd5d650d4bf13d6546b29e355ae01bec8a07811`
and `a06939cba2c937f452027ee4a1f20b31121a70b7fc7393d9ccad091817ee448e`.
Those files were not changed or executed by this review.

## Independent source and finite checks

The review checker reads the pinned original selected archive. It
propagates the 112 data columns through 10,851 original scalar events
up to the centre boundary. It reconstructs all eight R rows and compares
them with the interface receipt. This check does not import the
producer or the interface reconstruction code.

The reconstructed matrix has `R R^T=56I`. Each of its 112 columns has
four nonzero entries. The original canonical word and original complex
phase ledger give the same 112 distinct odd labels. Every displayed
line pivot is an actual entry equal to 1 or -1. The line functionals
therefore give the stated diagonal minor of rank 112.

For each of the 56 matched planes, the checker builds all 512 Fourier
columns directly from `C_q C_r^-1 P_(q+r)`. It verifies the involution,
the fixed constant character, and trace 256. It then applies every one
of the 56 functionals to every plane column on its full 256-character
support. All 802,816 contributions are checked. The full functional
matrix is the identity, including the repeated directions. There are
41 directions, and the 56 pairs partition all 112 actual ports.

All 56 two-column Gram determinants are 12. The certificate's selected
two-row minors are nonzero, and their product in matching order is
exactly 8. This proves the second source rank is also 112. Reversing
one plane orientation changes the exact moved-character sign; the
checker verifies this control.

## Proof checks and scope

Both factorization inductions are valid for singular scalar gates,
private CLEAR, and arbitrary query order. For the source factorization,
`L M = A + (L W) Z + u Q v A` adds the scalar row `v A`. For the response
factorization, it adds the scalar column `u`. These equations do not
move one payload operator past another. Applying a functional that
kills the identity proves the simultaneous row and column span bounds.
Arbitrary borrowed inputs can be included as separate initial scalar
columns. Restricting those inputs is a scalar input map and does not
invalidate the bound.

The tensor compression also holds. Every line phase and every matched
plane fixes the constant character. Compressing all but one tensor
factor to that character retains each single-factor operator. The
same exact minors therefore work at every positive tensor depth.
For the endpoint theorem, normalized trace minus the constant-character
expectation gives `2^(-lambda)-1` on every plane and zero on the identity.
It does not require a common negative eigenspace.

The two main scope objections are resolved by explicit hypotheses in
the proof. First, a rank-zero address permutation is a counted payload
query here; it is not a free scalar role map. At depth one, a line phase
is a scalar combination of the identity and a rank-zero translation.
Thus a query lower bound is not a native-child lower bound. Second, a
port-dependent phase already present in a productive input is a changed
input contract. It can supply the 112 source directions before this
grammar starts. The theorem does not charge that encoding a second
time. The accepted result excludes neither mechanism.

Reproduction:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/source-domain/query-span-review/review_query_span.py

The run passed with status `PASS_INDEPENDENT_QUERY_SPAN_SOURCE_AND_CERTIFICATE`.
The checker, receipt, and this note are new review artifacts. They do
not certify a native implementation, a complete supplier, or a kappa
improvement. The work used OpenAI Codex assistance under the user's
direction.
