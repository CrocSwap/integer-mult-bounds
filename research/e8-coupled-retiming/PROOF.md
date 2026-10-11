# Four E8 frame changes

All gate and register indices below are zero-based indices in the original
certificate. Binary frames are given by integer bit masks. The new certificate
has uncompressed SHA-256
`3191011e0cb189665c8e0a9b97137dbed50241a0704c8be01c11b1b5a9518fc2`.

## Circuit changes

1. Remove `helper388 -= source64` and `helper771 += source64` from A65.
   Insert those two additions just before A187, at frame 285 with basis
   `[196,56]`. No gate A66 through A186 touches any of these three registers.
   Source 64 has label 56.
2. Remove `helper693 += source98` and `helper839 -= source98` from A100.
   Insert those two additions just before A198, at frame 296 with basis
   `[257,243,14]`. No gate A101 through A197 touches any of these three
   registers. Source 98 has label 253, and `253 = 243 XOR 14`.
3. In B193, B916, and B917, replace frame 599, with basis
   `F=[276,148,84,51,15]`, by `G=[256,128,64,39,20,15]`.
   These gates add helper807 to helper766, distribute plus or minus half of
   helper807 to targets149 and155, and add helper766 to helper807.
4. In B873 and B874, replace frame 585, with basis `[161,81,9,5,3]`,
   by `[305,161,81,9,5,3]`. The first gate adds half of helper550 to target198
   and subtracts half of helper550 from target202. The second gate adds
   helper521 to helper550.

The first two changes move additions only across gates that touch disjoint
registers. Such scalar operations commute, for all initial register values.
Neither change crosses the scatter. The last two changes keep all scalar
operations and their order. Thus the complete scalar operator and the retained
totals at scatter stay the same. The verifier also compares the complete
1023-by-1023 rational scalar matrices.

All paths remain nested. The verifier checks actual binary subspace inclusion,
not only dimensions. For the third change, `G=F+span(256)` has dimension six.
The identities

```
276 = 256 XOR 20
148 = 128 XOR 20
84  = 64 XOR 20
51  = 39 XOR 20
```

show that F is contained in G. The preceding helper frames are contained in F.
The next helper frames are

```
helper766: [256,128,64,37,20,13,2]
helper807: [256,128,64,38,20,14,1]
```

They contain G because `39=37 XOR 2=38 XOR 1` and
`15=13 XOR 2=14 XOR 1`. The final target frames also contain G:

```
target149: [256,128,64,32,18,8,6,1]
target155: [256,128,64,34,16,10,4,1]
```

For target149, use `39=32 XOR 6 XOR 1`, `20=18 XOR 6`, and
`15=8 XOR 6 XOR 1`. For target155, use `39=34 XOR 4 XOR 1`,
`20=16 XOR 4`, and `15=10 XOR 4 XOR 1`.

For the fourth change, let `F=span(161,81,9,5,3)` and
`G=F+span(305)`. These frames have dimensions five and six. All preceding
frames are contained in F. The next frame of helper521 is
`span(257,145,81,48,9,5,3)`. The next frame of helper550 and both targets is
`span(304,160,80,8,4,2,1)`. Both contain F. They contain the added vector
because `305=257 XOR 48=304 XOR 1`. Thus both contain G, and the paths
remain nested.

## Child ranks

Each climb contributes a child whose rank is the increase in frame dimension.
The four changes affect disjoint sets of registers. Thus their histogram
differences add.

| Change | Register | Old child ranks | New child ranks |
| --- | --- | --- | --- |
| 1 | source64 | 5,3 | 1,4,3 |
| 1 | helper388 | 1,1,2,2,3 | 2,2,2,3 |
| 1 | helper771 | 1,1,1,3,1,2 | 2,1,3,1,2 |
| 2 | source98 | 5,3 | 2,3,3 |
| 2 | helper693 | 1,2,1,5 | 3,1,5 |
| 2 | helper839 | 1,2,1,2,1,1,1 | 3,1,2,1,1,1 |
| 3 | helper766 and helper807, each | 3,2,2,1,1 | 3,3,1,1,1 |
| 3 | target149 and target155, each | 5,3 | 6,2 |
| 4 | target198 and target202, each | 5,2,1 | 6,1,1 |
| 4 | helper521 | 2,1,2,2,1,1 | 2,1,2,1,1,1,1 |
| 4 | helper550 | 2,1,2,2,2 | 2,1,3,1,2 |

The combined invocation histogram difference is

```
rank:     1   2   3   4   5   6
change:  +2  -6  +4  +1  -6  +4
```

Its rank mass is zero and its child count is minus one. Copy cost remains 72.
The five-stage histogram is five times the invocation histogram, plus 240
children at each rank 4, 8, 16, and 20. Therefore its rank mass remains 56,715,
with dimension m=45, stock W=1263, and deficit mW-56715=120.

## Strict cost inequality

Let a be a saving, with 0<a<1, and put p=1-a. A rank-r child costs r^p, apart
from the common factor 1/(W m^p). Put `s_r=r^p`, with `s_0=0`. The combined
invocation price difference is

```
D(p) = 2*s_1 - 6*s_2 + 4*s_3 + s_4 - 6*s_5 + 4*s_6
     = sum_{k=1}^5 c_k*(s_{k-1} - 2*s_k + s_{k+1}),
c = [1,4,1,2,4].
```

For `0<p<1`, the function `x^p` is strictly concave on `[0,6]`.
Each second difference is strictly negative. All five weights are positive,
so `D(p)<0`. The verifier checks the coefficient identity against the actual
histogram difference. The raw five-stage moment decreases by
`5*D(p)/(W*m^p)<0`. This is a proof for the combined changes. It does not
claim that each separate change improves the cost for every saving.

## Fallback and exact savings

Use the [PR352 moment convention](https://github.com/DaysSky/integer-mult-bounds/blob/04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2/research/w3-p10b-e8-complex/code/pricing/moment.py#L55)
at commit `04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2`. Its
[E8 application](https://github.com/DaysSky/integer-mult-bounds/blob/04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2/research/w3-p10b-e8-complex/code/complex/certify_complex.py#L34)
and both source hashes are recorded in `sources.json`. If H is the five-stage
histogram, the moment is

```
M(a) = (1/W) sum_r H_r (r/m)^(1-a)
       + (32*m*sum_r H_r)/(10^16*W) * m^a.
```

The second term charges the rare bad classes. The candidate removes five
five-stage children, so this term also strictly decreases. The improved
moment is smaller for every 0<a<1, independently of any decimal estimate.

`reconstruct.py` uses rational logarithm and exponential enclosures to prove

```
M_original(876248285600677 / 10^18) < 1
M_original(876248285600678 / 10^18) > 1
M_candidate(876412559609473 / 10^18) < 1
M_candidate(876412559609474 / 10^18) > 1.
```

The logarithm uses the atanh series with a positive geometric tail bound.
Arguments are reduced to [1,2]. The exponential uses a Taylor polynomial of degree 20 with
a geometric tail bound. All arithmetic in these enclosures is rational.
Decimals in the saved result are only displays of the proved margins.

## Limits

This proves the finite circuit and recursive-cost improvement under the
stated convention. The general frame-transfer and recursion theorems remain
dependencies. A complete scalar identity is not a proof of the tape compiler
or the integer-multiplication assembly. No global optimum or larger final
integer-multiplication saving is claimed.
