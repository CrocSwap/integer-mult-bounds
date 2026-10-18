# Rational support descent for one added total

For a rational matrix X, every complex fixed-reader single lift has a
rational representative with identical support pairs in all its rank-one
terms. The [written proof](PROOF.md) extends @woklerx's PR998 reciprocal
projection argument to every infinite base field. A 1 by 1 F4-to-F2 example
shows that unrestricted descent over finite fields is false.

This is a research consolidation with a general field-descent statement.
It makes no new kappa claim. In the inherited P112 class, rational, real
and complex coefficients attain the same ordered nine-term support-cost
vectors. The cost floor remains 64, due to Mihir Srivastava's PR845.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
rtk proxy python3.11 -I -B research/rational-lift-descent-seed95/verify.py
rtk proxy python3.11 -I -O -B research/rational-lift-descent-seed95/test_verify.py
```

Expected output:

```text
PASS_RATIONAL_LIFT_DESCENT witnesses=9 scalar_lifts=162 controls=5 finite_field_pairs=4 new_kappa=false
PASS_RATIONAL_LIFT_CLI relocated=1 certificate_rejections=4 source_rejections=1
```

`python3` may replace `python3.11` when it meets the stated minimum. RTK is
only a command proxy. The verifier makes no network requests and executes
no predecessor module. It checks six predecessor source hashes, then
recomputes [CERTIFICATE.json](CERTIFICATE.json) exactly. `--emit` prints
the recomputed certificate for a separate comparison; it does not overwrite
any file. [SOURCES.json](SOURCES.json) records the exact Git base, dependency
hashes and historical selected context. Context hashes describe the base
and are not runtime requirements on a future selected frontier.

## Evidence and stopping rule

The certificate contains nine exact Q(sqrt(2)) or Q(i) examples. The
implementation checks all 162 scalar examples whose two coefficients each
have real and quadratic coordinates in {-1,0,1}, with X=[1]. It verifies
every entry of each complete rank-one identity and checks rational supports
directly against extension-field supports. All five attainable scalar
support patterns occur in each 81-example grid.

Five explicit controls reject direct projection of z and omission of each
of the four nonzero-value groups in the proof. A degree-two polynomial
example requires all seven trial parameters 0 through 6, checking the
N(D-1) bound rather than assuming the complex theorem's degree-one bound.
The finite-field boundary exhausts all four F2 choices for b,w. The public
CLI test relocates the minimal source closure and rejects four certificate
mutations plus one predecessor source mutation. Checks remain active with
Python optimization enabled.

These finite runs test the implementation and the displayed counterexample.
They do not prove the uniform field-descent theorem. The written proof
does that with a finite-union-of-polynomial-roots argument. The run stops
after the declared examples, controls and proof review. No rational-height
search or new P112 decoder search is attempted.

## Distinct scope

PR998 proves complex-to-real support transfer for an arbitrary real X. It
already gives an exact rational output for Gaussian rational inputs. The
new statement concerns arbitrary complex inputs when X is rational,
including irrational real and transcendental inputs, and explains the
finite-field boundary. It supplies no algorithm for discovering rational
relations among unspecified complex numbers. Effective examples require
exact coordinates in a known finite extension.

This package does not repeat PR845's 511-support geometric census, PR1098's
Gram spectra, PR1049's local-cell audit, PR1091's owner-map review, or PR1112's
selected invoice replay. No existing tracked file, `upstream/`, or selected
frontier is changed. Contributor credit and AI disclosure are in
[NOTICE.md](NOTICE.md).

The theorem only preserves support-dependent cost. Coefficient height,
precision, preparation, restoration, tape and complete hosting costs are
unchecked. There is no supplier implementation or measured runtime claim.
