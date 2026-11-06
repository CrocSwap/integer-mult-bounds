# Sharp inverse norms with fractional column capacities

For every integer n>=1, real beta>=1 and 0<rho<1, [PROOF.md](PROOF.md)
gives the exact maximum of ||(I-E)^-1||_1 over complex n-by-n matrices with
absolute row sums at most rho and column sums at most beta*rho. One matrix
attains all the transport bounds simultaneously:

    G[i,j] = rho * length([i-1,i] intersect [beta*(j-1),beta*j]).

Its first inverse column supplies the sharp norm. A triangular partial-sum
recurrence computes it, including the self-referential terms that occur near
beta=1. At n=3, rho=1/2, beta=5/4 the exact value is 38/15.

This answers Nick Petalas's fractional-capacity question in
[PR #6788](https://github.com/CrocSwap/integer-mult-bounds/pull/6788).
His integer-ratio theorem and sorted transport method retain their credit.
The original [proof](vendor/PR6788-PROOF.md) and
[README](vendor/PR6788-README.md) are retained unchanged and authenticated by
[SOURCE-PINS.json](SOURCE-PINS.json). No predecessor scientific code is imported
or replayed. [CREDITS.md](CREDITS.md) describes source exposure and assistance.

## Evidence and reproduction

The standalone CPython 3.12 standard-library verifier uses exact Fraction
Gauss-Jordan inversion, both inverse-composition identities, literal interval
intersections, a direct triangular solve and the partial-sum recurrence.
Direct normal and optimized commands passed with identical generated receipts:

- 3,117 exhaustive half-row-unit matrices through dimension three; 21,921
  admitted cap cases, 64,731 inverse columns and 192,291 partial-sum comparisons.
- 729 attaining fixtures at n=1..24,32,64,128; 216 full dense inverses through
  n=8, 14,148 attained partial sums, 243 credited integer-formula comparisons,
  and six checks of the new three-coordinate piecewise formula.
- 72 real sign-conjugate fixtures and 12 semantic/domain/parser rejections.
  The finite phase fixtures use +1 and -1; the complex theorem uses the written
  Neumann comparison, rather than an unreported complex census.

```sh
python3.12 -B scripts/research_package.py --package research/fractional-column-resolvent
python3.12 -I -W error -B research/fractional-column-resolvent/verify.py
python3.12 -I -O -W error -B research/fractional-column-resolvent/verify.py
```

[VERIFY.json](VERIFY.json) registers both finite commands, each with a 180-second
cap and no external runtime inputs. The verifier writes no files and prints
`PASS_FRACTIONAL_COLUMN_RESOLVENT` inside a receipt with all package file hashes.
Full publication, export and hosted receipts are recorded in the PR handoff.
Source authentication, finite execution, written proof, AI review and human or
proof-kernel acceptance are distinct kinds of evidence.

## Scope

[TASK.json](TASK.json) retains the complete original `uniform-transfer-audit`
card with explicitly changed scope. Its actual-caller gate remains unmet: this
is a completed abstract conditioning result, with partial progress on that card.
No actual emitted Gaussian matrix is admitted to these caps. Physical preparation,
rounding, tapes, stock, native operations, ownership/restoration, compiler,
analytic recovery and the complete supplier invoice remain separate. All five
selected assumptions and the selected frontier remain unchanged. No new kappa,
independent human review or formal proof-kernel acceptance is claimed.

## Open next questions

- Bind both caps to one exact emitted Gaussian matrix and caller, then price
  every preparation and restoration cost. Those missing bindings prevent a
  physical precision improvement from following here.
- For heterogeneous caps or a prescribed support, first specify the different
  optimization problem and a discriminating example. This theorem does not
  solve those domains, and no follow-on search is reserved.
