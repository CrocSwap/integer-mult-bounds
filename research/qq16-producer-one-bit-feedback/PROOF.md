# A sufficient common offset of 101

## Contract and cited premises

Fix the literal QQ16 F0 then B_1_2 words and the completed-operation
contracts in commdata2338's [PR3235 envelope](../qq16-rounded-producer-envelope/README.md).
Original data have norm at most H>0, persistent dirty helpers have norm at
most `2^delta H`, and beta, delta are nonnegative integers. The norm is the
maximum owner payload Hilbert norm, then the maximum over fields. Native
children, adapters and cover maps obey the cited isometry and destination
contracts. ADD/SCALE defects use the cited actual-operand relative bounds.
Owned private CLEARs are exact and precede every private read. Additional
inexact handoff operations are not covered by this contract.

We use the predecessor's nonnegative path-polynomial envelope and its
published ledger as premises. They are not new measurements or replays:

```text
F0: N_F = 26057,  J_F = 10632335516156845470267 / 4096
B1: N_B = 26977,  J_B = 34778728470688788237067911 / 8.
```

For an entry bound A, each initialized field has a polynomial q with
nonnegative rational coefficients and degree at most N. Its ideal/actual
error is bounded by `A [q(1+u)-q(1)]`. At every relevant cut,
`q'(1) <= J_F` or `J_B`. The same ledger bounds completed data and helper
outputs. F0's ideal data endpoint has norm at most 58H, independently of
dirty helper values, and its ideal helpers return isometrically. These are
also cited PR3235 premises. B1's ideal data endpoint is independent of its
arbitrary helper inputs. The proof below is conditional on these premises.

## Smaller feedback factor

For 1 <= n <= N and u >= 0,

```text
(1+u)^n - 1 = u sum_(j=0)^(n-1) (1+u)^j
           <= n u (1+u)^(N-1).
```

If Nu<1, the binomial theorem and `binom(N,k) <= N^k` give

```text
(1+u)^(N-1) <= (1+u)^N <= sum_(k>=0) (Nu)^k = 1/(1-Nu).
```

Multiply the monomial inequalities by q's nonnegative coefficients and sum.
The constant term contributes zero. Thus

```text
q(1+u)-q(1) <= u q'(1)/(1-Nu).
```

In particular, `Nu <= 1/17` implies an error bound `(17/16) A u J`.
This retains feedback; replacing the factor by exactly one is generally
false, as the polynomial `q(z)=z^2` shows for every u>0.

## The new common tolerance

Set `0 <= u <= 2^(-beta-delta-101)`. Since beta, delta >= 0 and
`17*26977 < 2^101`, both stages satisfy `N u < 1/17`. The improved
feedback estimate therefore applies to every permitted error pattern.

For F0 take `A_F=2^delta H`. Its all-cut error divided by
`eta_F=H 2^(-beta-8)` is at most

```text
r_F = (17/16) J_F 2^(8-101)
    = 180749703774666372994539 / 649037107316853453566312041152512
    < 1.
```

Consequently its actual completed data have norm at most `58H+eta_F` and
its helpers have norm at most `2^delta H+eta_F`. With beta, delta >= 0,
both are below `A_B=2^(delta+6)H`. This is a bound on actual B1 inputs,
so correlated F0 helper errors are carried into the second stage.

B1 is compared with its ideal map applied to that actual input. Divide
its all-cut error bound by `eta_B=H 2^(-beta-13)` to obtain

```text
r_B = (17/16) 2^6 J_B 2^(13-101)
    = 591238384001709400030154487 / 618970019642690137449562112
    < 1.
```

The strict normalized slack is
`27731635640980737419407625 / 618970019642690137449562112`.
These exact inequalities prove the stated common tolerance for every
beta, delta and H in the contract, not just the finite test parameters.
The predecessor common offset is 102; the new sufficient tolerance is
twice as large. No further guard optimization is claimed.

## Decoder consequence and limits

If the separate decoder implementation supplies
`eps_D <= H 2^(-beta-1)`, Nick Petalas's cited
[PR2965 transfer](../qq16-producer-defect-transfer/README.md) gives

```text
original-data error <= 49 eta_F + 1923 eta_B + eps_D
                    <= (7587/8192) H 2^-beta < H 2^-beta.
```

The order is unchanged: B1's completed defect is relative to its actual
F0 output. Neither cancellation of independent defects nor exact borrowed
restoration is inferred. The result is a conditional numerical interface
lemma, not an implementation of any native event, a finite register-width
minimum, a complete multiplication theorem or supplier admission.

The verifier authenticates the cited source bytes and checks the new
arithmetic and finite controls. It neither recomputes the predecessor's
path ledger nor audits its native semantics. A failed certificate at offset
100 rejects only this particular sufficient bound, not that physical
tolerance in every possible analysis or implementation.
