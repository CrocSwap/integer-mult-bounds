# One-way coupled full guards have strictly negative correlation

This scoped algebraic proof was produced by Nick Petalas. Apache-2.0.

## Statement and cited inputs

Let K be a finite field of order q, let m>=2, and let U,V be rank-one
idempotents on K^m with UV nonzero and VU=0. Set P=I-U and Q=I-V.
Choose G uniformly from the complete group GL_m(K). Let A and B be the
events that every leading principal minor through order m-1 of GPG^-1
and GQG^-1, respectively, is nonzero. Write p=Pr(A)=Pr(B) and
J=Pr(A and B). Then

```text
J < (1-q^(-m)) p^2 < p^2.
```

Consequently Cov(1_A,1_B) < -q^(-m) p^2. This answers Open next question 1
of [#4769](https://github.com/CrocSwap/integer-mult-bounds/pull/4769).
It is a new inequality for the one-way coupling, using the counting laws
as cited dependencies. The binary strict-correlation result is already in
#4274; the all-field quantitative bound is new here. This is not a replay
or audit of the predecessor proofs.

Use Nick Petalas's marginal law in
[#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227) and
one-way joint law in #4769. Their exact retained proof blobs are pinned
as historical provenance in SOURCES.json. Put

```text
n=m-1 >= 1,  t=q^m,  s=q^2-q+1,
alpha=s^2,  beta=q^3-q+1,  gamma=q^3-q^2+1.
```

The cited formulas, with the latter's rational normalization cancelled, are

```text
p = (q-1)s^n / [q^n(t-1)],

J = (q-1)[(q-1)alpha^n-(q-2)beta^n-gamma^n]
    / [q^(2n)(t-1)(t-q)].                                  (1)
```

All denominators are positive and p>0. Dividing gives

```text
J/p^2 = (t-1)/(t-q) * (1-D),
D = [(q-2)beta^n+gamma^n] / [(q-1)alpha^n].                  (2)
```

## The new comparison

The following identities hold for every real q>=2:

```text
beta-gamma = q(q-1) > 0,
q*gamma-alpha = (q-1)^3 > 0.                                (3)
```

Also gamma=q^2(q-1)+1>0 and alpha>0. The nonnegative weights q-2 and 1
sum to q-1, so (3) and the positive integer n give

```text
D >= gamma^n/alpha^n > q^(-n).                              (4)
```

The first inequality is equality at q=2, but the second is always strict.
Insert (4) into (2), multiplying only by positive quantities:

```text
J/p^2 < (t-1)/(t-q) * (1-q^(-n))
      = (t-1)/t
      = 1-q^(-m).
```

This proves the claim in every characteristic, including extension fields.
There is no finite cutoff or untested tail. The polynomial comparison
holds for every real q>=2; the header probability interpretation requires
q to be a prime power.

Nick Petalas's orthogonal-kernel comparison in
[#4767](https://github.com/CrocSwap/integer-mult-bounds/pull/4767)
uses 2*beta^n-gamma^n and q*beta-alpha. Here the joint law has a different
weighted correction, and its least base gamma suffices through the second
identity in (3). That proof pattern is predecessor credit. Only the
one-way correlation statement and its comparison are claimed here.

## Complete-header hypothesis and limits

A literal binary example shows why a restricted header catalogue does
not inherit the inequality. Take

```text
U=[[1,1],[0,0]],  V=[[0,0],[0,1]],  G=[[1,0],[1,1]].
```

Here UV is nonzero, VU=0, and G^-1=G. Both conjugated requests have first
diagonal entry 1, so both pass. If the header domain consists only of G,
then J=p=1, which violates the displayed bound. Thus a physical caller's
restricted catalogue needs a separate theorem.

The argument supplies no header selection, emission, dispatch, dirty
restoration, precision, stock or complete physical invoice. Those costs
remain unknown. Two-way coupling and larger request families are outside
the claim. No new kappa, supplier admission, selected-frontier change or
complete multiplication theorem follows. Independent human and formal
proof-kernel review are unclaimed.
