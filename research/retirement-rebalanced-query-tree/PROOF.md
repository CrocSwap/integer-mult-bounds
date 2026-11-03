# A strict concave gain from a different child allocation

## 1. Exact source and change

Use PR6545 at `775722aa94a5e85b05d1d704d7dca10cbf016f0c` as the comparison.
It uses the PR6398 mixed root and the exact PR6529 native word. Its four
binary children have 7, 2, 2 and 7 leaves. Each leaf consumes one native call.
The source package, proof and executable checks are retained without change.

Replace only the last two trees. The new four trees are

```text
A = [[1,[1,1]],[[1,1],[1,1]]]       (7 leaves)
B = [1,1]                         (2 leaves)
C = [[1,1],[1,[1,1]]]              (5 leaves)
D = [[1,1],[1,1]]                  (4 leaves).
```

The symbols A, B, C and D also denote the products of the fresh stage
variables of these children. All 18 variables are distinct. The six-field
root, its scalar bases and its stage masks are unchanged. The retained binary
identity supplies each child. Full polynomial replay also checks the emitted
34-field word directly, for every input coefficient.

## 2. The same independent retirement still applies

Number events from zero. The prefix through event 328, `QUERY 20 21 -1`, is
byte-for-byte the same event list as in the old caller. The first two children
are unchanged. At that cut, the third child has not started its stage calls.
Its first binary query has the same operands and sign.

Fields 4, 20 and 21 still have the same complete stage product C. Here

```text
C = D10 D11 D12 D13 D14.
```

Their central signs normalize exactly as in PR6545. Put

```text
lambda = (1+i)/2 + (1-i)q^2/2,
S = lambda q^(-1),              S^2 = 1.
```

The old dual pairs and ordinary bases G and J depend only on the unchanged
prefix and the three field labels. Their identities remain

```text
ab = cd = 1,       aP = Sc,       Pd = Sb,
e4^T G = c,        Gd = e4,       e4^T J = a,       Jb = e4.
```

The verifier checks all these identities over the full central polynomial
ring. It does not set `q^2=1` or specialize the stage variables.

The proof in PR6545 now applies with this five-stage C. G mixes only three
equal normalized targets SC, so it commutes with the complete target map.
At the cut, the pivot row and column are S and have no coupling to the other
fields. The matching suffix block is C. Return the completed pivot input
with output S; give the suffix a fresh independent input. Rename its pivot
to field 34. The final ordinary normalizer gives outputs `q^(-1)` and C.
All other independent inputs keep their prescribed outputs.

Thus the retirement replaces one rank-41 target by independent rank-1 and
rank-40 targets on each of 104 ports. It does not copy one input into two
productive targets. The complete 35-field word has 611 events. Forward and
reverse checks independently cover all 1,225 coefficient positions.

At positive tensor width f, use the retained factorwise native convention.
The ordinary scalar coefficients stay outside tensor powers. The new two
target ranks are f and 40f. The physical checker verifies the central signs,
fresh orthogonal axes and all port maps. The inherited all-width and
precision contracts remain assumptions of the conditional result.

## 3. Complete signed invoice

Let H_r denote one Gaussian target or paid job of rank r. A binary node with
k leaves adds 208 targets of rank `8k+1` and pays 208 jobs of rank `8k`.
The four old trees have internal-node counts

```text
{2:8, 3:2, 4:2, 7:2}.
```

The new counts are

```text
{2:8, 3:2, 4:2, 5:1, 7:1}.
```

Hence one seven-leaf node becomes a five-leaf node in the complete count.
All 18 native calls, their helper targets and their paid jobs remain. All
17 thin queries remain. The sums A+B and C+D both stay at nine leaves, and
the second child stays at two leaves.

The complete target and paid changes from PR6545 are

```text
Delta T = 208 H41 - 208 H57 + 104 H40 - 104 H16,
Delta P = 312 H40 - 208 H56 - 104 H16.
```

The first two target terms come from the binary node. The last two target
terms replace the old retired suffix by the new suffix. The paid terms
include both the changed node idles and the third child's extra root idle.
No idle is omitted. Subtract to obtain

```text
Delta(T-P) = 208 [(H41-H40) - (H57-H56)].
```

For `H_r=r^t`, `0<t<1`, the derivative `t r^(t-1)` strictly decreases.
Integrating on [40,41] and [56,57] proves the stated gain is strictly positive.
This is an exact all-exponent invoice comparison within the stated domain.

Both target and paid rank mass decrease by 832. Their difference remains
760. Productive fields remain 13,756 and paid jobs remain 67,096. The largest
target rank is 145 and the largest paid rank is 56.

The new word adds two ordinary Q_POWER operations relative to PR6545. They
are included in the literal event count and the complete ordinary allowance.
The native owned inventory remains 29 labels, 45 lifetimes and peak 13.
The full ordinary-work upper bound is 254,932,208, below the retained 10^9
allowance. Scalar coefficients, routes, storage and growth checks remain in
the complete price calculation. The change introduces no unpaid channel,
helper, copy, clear or restoration.

## 4. Conditional numerical result

The new claimed saving is 0.00329492. The tested saving is 0.003294925.
Two rational engines certify a positive complete moment at the tested
saving. They also certify both signs of the raw root enclosure in RESULT.json.
A negative derivative bound establishes a unique crossing below the retained
BIT cap. Both engines reject the full PR6545 invoice at the new claim.

The retained completion tails, integer compiler threshold and all 54 strict
plus four functional outer predicates are evaluated with the new profiles.
The completion ratio is approximately 0.96892102. It exceeds the source
decay 31/32. Use decay 97/100 and reserve 10^(-27) at the same power 1920.
The exact moment gap funds this reserve, and `4*(97/100)^1920` satisfies
the complete tail test. The old decay is an explicit rejection control.
They imply the same conditional bound form `O(n (log n)^(1-kappa))` with
`kappa=0.00329492` under the five source framework assumptions.

This small increase follows from a changed tree and the exact positive
invoice difference. No global caller optimum, unconditional multiplication
theorem, independent review or selected-frontier change is claimed.
