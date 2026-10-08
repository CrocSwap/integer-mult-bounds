# Batching every complex residual

The unchanged h28 paired complex network supports complex saving
`4191487/10^12`, compared with PR #10's `7/10^7` and PR #13's `18/10^7`.
This is headroom for a stronger bit producer, not a multiplication exponent
on its own. It uses IceKylin's whole-residual identity and mixed-width
recurrence from [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10).

Each nonzero physical edge has an orthonormal residual basis and rank
`r < m = 21952`. The identity for mixed forward/inverse factors in PR #10
replaces all `r` singleton calls by one child of width `r/m`. The sign passes,
phase, and coordinate changes stay in fixed local work. Applying that
identity to every edge leaves the network, rank sum, and deficit unchanged.

The executable schedule counts 34 residual ranks. Stage one stops auxiliary
roles at dimension h; stage three begins those shared roles at dimension h,
so it counts the join exactly once. Stage two keeps its separate bank.
The summed ranks equal the inherited total `45772350635112192`; both original
bulk multiplicities also agree. Independent enumeration of the old three-bank
schedule, followed by the bank-sharing histogram substitution, agrees at
h8, h10, and h28. No assumption of a uniform edge rank enters the moment.

For each rank r with multiplicity c, set `w=cr/(Wm)`. Exact outward logarithm
enclosures give

```
sum(w) = 1−eta
sum(w/(1−a_c log_upper(m/r))) < 1
a_c = 4191487/10^12
```

The strict gap exceeds `1.34e-14`; the next `10^-12` grid point fails this
conservative comparison.

Batching additional residuals requires a new precision bound. The inherited
path argument still gives total rank at most `q=m+6h=22120`. The largest
edge is `A=m−2h=21896`. For `rho=3/2`, convexity shows that any partition
of at most q into parts at most A has normalized power sum at most

```
(A/m)^(3/2) + ((q−A)/m)^(3/2)
  < 27921787004127/28000000000000
  < 999/1000.
```

The first inequality uses exact rational upper square-root bounds. It does
not assume a path visits only one selected edge. Every edge contributes at
most four wrapper operations, and there are at most s nonzero edges, so the
existing `4s` local overhead allowance suffices. The same induction with
`E=64(W+m+1)^3` yields `C1=3/2−beta/2+zeta=3749/2500` for
`beta=1/1000`, `zeta=1/10000`. This leaves room for epsilon near one half.

The inherited coefficient/label/frame construction, PR #10 transfer, and
general path argument remain mathematical dependencies. The finite histogram
and rational inequalities are checked exactly; they are not formal proof of
the multiplication theorem.

Reproduce with:

```sh
python3 scripts/experiments/complex_all_residuals.py --output certificates/complex-all-residuals.json
python3 -m unittest discover -s tests -p test_complex_all_residuals.py -v
```
