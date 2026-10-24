# Strict pair correlation over every finite field

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let K be a finite field of order q and m >= 2. Let U,V be rank-one
idempotents on K^m with UV=VU=0. Set P=I-U and Q=I-V. Choose G uniformly
from the complete group GL_m(K). Let A and B be the events that every
leading principal minor, through rank m-1, of GPG^-1 and GQG^-1,
respectively, is nonzero. Write p=Pr(A)=Pr(B) and J=Pr(A and B).

Then

```text
J < (1 - q^(-m)) p^2 < p^2.
```

In particular the two indicator variables have strictly negative covariance,
with Cov(1_A,1_B) < -q^(-m) p^2. This is a scoped algebraic proof using
the cited counting laws. It answers Open next question 1 of #4747. The
binary and ternary strict-correlation results were already proved in #4261
and #4273, respectively. The all-field conclusion is the new result.

## Cited formulas and their normalization

Use Nick Petalas's marginal theorem in #4227 and joint theorem in #4747,
the latter pinned at f51dcebce79b8b8958427a9a9b7bc8feca352c9d. We use these
as predecessor results, without auditing or replaying their counting proofs.
Put n=m-1 >= 1 and

```text
s = q^2-q+1,  alpha=s^2,  beta=q^3-q+1,  gamma=q^3-q^2+1.

p = (q-1) s^n / [q^n (q^(n+1)-1)],

J = (q-1)^2 (alpha^n - 2 beta^n + gamma^n)
    / [q^(2n) (q^(n+1)-1)(q^(n+1)-q)].
```

All denominators are positive, and p>0. Division gives

```text
J/p^2 = [(q^(n+1)-1)/(q^(n+1)-q)]
        * [1 - (2 beta^n - gamma^n)/alpha^n].                 (1)
```

## The comparison

For every real q >= 2, the following factorizations are positive:

```text
beta - gamma = q(q-1) > 0,
q beta - alpha = (q-1)(2q^2-2q+1) > 0.
```

Also gamma=q^2(q-1)+1>0 and alpha>0. Since n is a positive integer,

```text
2 beta^n - gamma^n > beta^n > alpha^n/q^n.                  (2)
```

Insert (2) into (1), multiplying only by positive quantities:

```text
J/p^2 < [(q^(n+1)-1)/(q^(n+1)-q)] (1-q^(-n))
      = (q^(n+1)-1)/q^(n+1)
      = 1-q^(-m).
```

This proves the quantitative bound in every characteristic, including
nonprime fields. No finite cutoff, estimate of a remainder, or untested
interval is used. The algebraic comparison itself holds for every integer
q >= 2, while its probability interpretation requires q to be a prime power.

At q=2,m=2 the cited joint fraction is zero, which satisfies the strict
bound because p>0. No positive-common-header assumption is needed.

## Scope

Uniform sampling from the complete GL group is essential. For example,
over F_3 with m=2, take U=diag(1,0), V=diag(0,1), and the single header
G=[[1,1],[1,2]]. Its inverse is [[2,2],[2,1]]. Both conjugated requests
have first diagonal entry 2, so both pass. Restricting the domain to this
one header gives J=p=1, violating the displayed bound. Thus this theorem
cannot price an arbitrary restricted header catalogue.

Nothing here supplies header selection, emission, dispatch, dirty
restoration, stock, precision or a complete physical caller. Those costs
remain unknown. No new kappa, supplier admission, selected-frontier change
or complete multiplication theorem is claimed. Independent human and
formal proof-kernel review are unclaimed.
