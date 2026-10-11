# A scoped ceiling for the current whole-hosted architecture

This is a limit of the declared finite moment and outer-assembly format,
not a lower bound for integer multiplication or for other constructions.

Let m be the parent dimension, W the live-family count and n_r the paid
child counts. Suppose every child has `1 <= r <= m-g`, with g>0, and set

```
D = (mW - sum_r r*n_r) / W,       0 < D < g.
```

The good-branch normalized moment at a candidate saving a is

```
F(a) = sum_r [r*n_r/(mW)] * (m/r)^a.
```

Any retained bad-branch term is nonnegative, so admission requires F(a)<1.
For a>0, monotonicity in r gives

```
F(a) >= (1-D/m) * (m/(m-g))^a.
```

Put theta=D/g in (0,1). Strict weighted arithmetic-geometric mean gives

```
1-D/m = (1-theta)*1 + theta*(1-g/m) > (1-g/m)^theta.
```

Therefore F(D/g)>1. F is increasing, so **every admitted saving is strictly
less than D/g**. This holds regardless of the number of children or their
individual packing, and remains valid with any nonnegative bad-branch bill.
It is not an optimality claim for a realizable circuit.

## The fixed 120-port, copied-rank72 stage family

Assume the current whole-hosted format, with no helper banks or padding:

- K data pairs, L=2K+1 stages, T replicas, V=120 ports;
- W=2KVT live data families;
- dimension m=h+2K(h-1);
- the unchanged copied-rank charge 72 per invocation;
- the checked deficit identity `mW-sum r*n_r = [2KV-72L]T`;
- local children of rank at most h and idle children of rank at most
  `2(K-1)(h-1)`.

For K>=2 and h in {8,9}, the largest allowed rank is
`m-(3h-2)`. Thus g=22 on the bit side and g=25 on the complex side, while

```
D = 1 - 72*(2K+1)/(240K) = 2/5 - 3/(10K) < 2/5.
```

Consequently the complex saving b is strictly below 2/125, uniformly over
K, T and all paid profiles obeying these hypotheses. The retained balanced
outer assembly has q<a<b and

```
kappa < (1-eta)*q/(1+q) < a/(1+a) < b/(1+b).
```

Hence **kappa < 2/127** throughout this fixed whole-hosted family. This is
stronger than the current technical guard's 1/33 ceiling. It does not assert
that 2/127 is attainable. Reducing the copied-rank charge, changing the
window geometry, introducing banks with different maximum ranks, or changing
the outer assembly falls outside the corresponding hypotheses.

## Sharper fixed eleven-stage bounds

For K=5, D=17/50. The current dimension/maximum-child pairs are (78,56)
and (89,64). Direct integer comparisons prove

```
(3883/3900)^75 * (78/56) > 1,
(4433/4450)^86 * (89/64) > 1.
```

Thus the bit saving is below 1/75 and the complex saving below 1/86, even
before the bad-branch bill. The same balanced assembly is therefore below
**kappa=1/87** for this fixed geometry and deficit. The next reciprocal
control (powers 76 and 87) reverses each comparison; that only limits this
particular coarse certificate, not the true root. The verifier recomputes
these integer signs without floating logarithms.

The example profiles are derived from the new adapted-kernel package's
frozen word/hosting selection and its inherited bit profile. Both have
D=17/50. Finite sample checks supplement the uniform inequalities above;
they do not replace that argument.

The implication for the kappa=1 goal is specific: further kernel, retiming,
replica-pooling or packing changes that preserve all these hypotheses cannot
reach it. A different architecture and ultimately a different outer
reduction are required. This is not an impossibility theorem for a different
multiplication algorithm.

Prepared by chafreaky with OpenAI Codex assistance. The moment and balanced
assembly definitions are inherited from the source-pinned project engines;
the scoped inequality and this certificate are supplied here. Apache-2.0.
