# Released two-FULL invoice: optimistic additional recursive-control budget

**Exact arithmetic result under an unproved complete operator/inventory premise:** at most **44 additional H1 calls** can be allowed while retaining strict raw moment positivity uniformly for `C in [0.0030217758,0.00339999]`. Forty-four succeeds uniformly; forty-five fails at the upper endpoint. This is an optimistic arithmetic grant for that declared invoice, not actual caller funding, compiler reserve or κ admission.

The stock is Dillon's released [Discussion4930 comment19143357](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19143357), as authenticated in `coded-port-adapter-ceiling-20261023/outputs/released-operator-inventory-20261023`. Its scientific source pin is `4c0a359d88f22f05189d51f48387750b801a45d4`; public scoped theorem pin is `0e8a13c251a9be1029114cda8b4194f05f3a23ec`. The checker authenticates all eleven files listed by that frozen inventory's FILES.json, records their hashes and manifest hash, and checks its release receipt's exact T/P. It imports no source/native/operator/compiler code.

## Complete promised invoice, including every helper

```
T = 224 H17 + 816 H9
P = 4608 H1 + 838 H2 + 1020 H3 + 254 H4 + 136 H5
```

There are 224 original main inputs and exactly 816 original helper inputs, for 1,040 productive owners. Each of the two FULLs has native profile `P0={1:2201,2:412,3:510,4:127,5:40}` and helper profile `H={4:28,7:7,8:47,9:326}`. The accounting is

```
P = 2 P0 + 112 H1 + (94 H1 + 14 H2 + 56 H5).
```

The query bank costs 112 H1. The final bracket pays complements for the 94 rank-eight, 14 rank-seven and 56 rank-four helper jobs across both FULLs, completing each to rank nine; 652 helpers already have rank nine. All 816 original helper owners are credited once. Their old lower-rank outputs are not also retained as extra targets. The complement rank mass is 402. Total target and paid rank masses are respectively **11,152** and **11,040**, a raw rank-mass difference of **112**. That difference is not the extra-control budget at positive C.

## Declared comparison interval and exact bounds

Write `a=0.0030217758`, `b=0.00339999` and

```
M(C) = 224*17^(1-C) + 816*9^(1-C)
     - 4608 - 838*2^(1-C) - 1020*3^(1-C)
     - 254*4^(1-C) - 136*5^(1-C).
```

Exact rational outward enclosures give:

| Quantity | Lower bound | Upper bound |
|---|---:|---:|
| M(a) | 52.133114229301600459209653 | 52.133114229301600459209654 |
| M(b) | 44.676959553589208855078743 | 44.676959553589208855078744 |
| M'(C), uniformly on [a,b] | −19728.040142366829130975258373 | −19700.174693469327002916426638 |

The exact Fraction endpoints are retained in RESULT.json. For the derivative, define `L_T(C)=sum T_r*r^(1-C)*log r` and likewise `L_P`. Both are nonincreasing positive sums. Therefore

```
L_P(b)-L_T(a) <= M'(C) <= L_P(a)-L_T(b) < 0.
```

This proves strict decrease of M throughout the interval. Its minimum occurs at b; the endpoint enclosure proves `44<M(b)<45`. An extra rank-one call costs exactly one in this moment for every C. Consequently:

* `M(C)-44 > 0.676959553589208855078743` uniformly on [a,b].
* At b, `M(b)-45 < -0.323040446410791144921256`, so no integer grant of 45 or more is uniformly compatible with strict positivity.
* One **additional complete 112-query bank** gives a negative margin everywhere in the interval: its uniform upper bound is below `-59.866885770698399540790346`. This prices that fixed extra-query policy; it is not a universal query lower bound on other operator implementations.

Thus **44 is maximal**, rather than merely a sufficient rounded allowance, for additional H1 jobs under this exact unchanged T/P and the requested uniform interval. The reported raw surplus 112 cannot be substituted for it.

For a different finite nonnegative additional paid profile E, the relevant condition is `sum E_r*r^(1-C)<M(C)` at every C. One convenient conservative sufficient test is `sum E_r*r^(1-a)<=44`: the extra paid moment is at most that quantity throughout the interval, while M is strictly above 44. This test can overcharge higher-rank jobs; it is not a maximal general mixed-profile characterization. New productive credit or a changed base invoice requires a fresh calculation.

No root or extra root digits were extracted, no full compiler constants were retuned, and no extension to an ordinary BIT limit was attempted. All claims use precisely the declared closed comparison interval.

## Exact engine and semantic controls

The standard-library checker independently evaluates `r^(1-C)=r*exp(-C log r)`. Binary reduction gives logarithm arguments `0<=z<=1/3`; forty positive atanh terms and the geometric tail `2z^81/[81(1-z²)]` enclose each reduced log. Log endpoints are rounded outward on a rational 10^-50 grid. Since `0<=C log r<1/50`, odd/even alternating exponential truncations of degrees 17/18 bound exp(-x) below/above. Monotonicity of exp(-x) selects the correct log endpoints; each final power is rounded outward on a rational 10^-40 grid. Every acceptance test uses integers/Fractions. No floating-point sign, native execution or formal proof-kernel acceptance is claimed.

The checker rejects five stock mutations: omitting one helper; omitting the original 112 query calls; omitting paid helper complements while retaining completed H9 credit; retaining original helper rewards in addition to completed H9 rewards; and crediting the owned query bank as independent inputs. The rejection invariants are original-owner count, one completed transform per owner, exact source complement multiplicities and the full two-FULL/query/complement paid bill. The grant boundary itself is controlled by the strict tests for 44 and 45; the extra-112 query policy is independently rejected by its moment bound.

Normal and optimized Python runs passed and produced byte-identical JSON, using explicit checks that remain active under `-O`:

```
python3 -B outputs/released-operator-optimistic-budget-20261023/check_budget.py --out outputs/released-operator-optimistic-budget-20261023/RESULT.json
python3 -O -B outputs/released-operator-optimistic-budget-20261023/check_budget.py --out outputs/released-operator-optimistic-budget-20261023/RESULT-OPTIMIZED.json
cmp outputs/released-operator-optimistic-budget-20261023/RESULT.json outputs/released-operator-optimistic-budget-20261023/RESULT-OPTIMIZED.json
```

## Necessary gates before using the grant

The released handoff has no complete t0 implementation. An actual changed-information-boundary caller must prove the full ordered operator identity, explicit physically allowed programs and inverses for all four released controls, safe old-input read order, query ownership/cleanup, autonomous helper returns and valid paid helper-complement contacts over all column widths. An algebraic inverse or even Gaussian parity does not supply these programs.

If a control needs paid recursive operations, its **complete** extra Gaussian profile—including implementation, inverse, resets and any new boundary corrections—must fit a newly proved full word and the unchanged independent targets before this arithmetic applies. The number 44 does not prove that the missing controls can be implemented with 44 calls. Correlated query buffers, erased scratch and returned helper copies do not earn new productive credit. A full additional 112H1 query bank fails this optimistic fixed invoice; cheaper sharing or a different complete invoice remains a separate question.

Fixed physical costs remain separate nonzero bills: source native work, normalizer/Pauli maps, scalar recodings and odd-denominator rounding, COPY/reset/clear, movement, live storage, descriptor setup and tape/precision implementation. No such cost is converted into an H1 reward or declared absorbed here.

Finally, a positive raw moment is only the first arithmetic prerequisite. Paid completion/splitting, finite integer compilation and uniform exponent gaps, implementation/precision constants, ordinary BIT binding, all outer cost rows and analytic/recovery premises still require explicit admission. This task proves none of them, and the 44-call grant is not a funded complete outer budget. No κ improvement is established.

Credit Dillon's released operator template and source theorem; Dugongue/mdumitrean's native profile; the PR4933 normalizer authors; Cinna Davis, Cao Yifan, zxv, Jacob Sussman and retained native/helper/query/compiler/precision contributors; and the independent source-inventory author. Prepared with substantial OpenAI Codex assistance. All work is local; other agents' files and frozen sources were preserved.
