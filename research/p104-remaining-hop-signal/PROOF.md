# Main-signal obstruction for three paid-hop bypasses

## Fixed word and allowed corrections

Let W be the exact PR6621 native word retained in `PR6621-WORD.json.gz`.
Its identity and provenance are in `INPUT.json`. Its logical scalar operations
are ADD, COPY, SCALE, INIT and CLEAR. MOVE changes the chart of a logical
value. The inherited interpretation of those instructions is cited from
PR6621; no new physical interpretation is asserted here.

The 104 main input roles are `W.live`. Write X for their coordinate space
with all other initial coordinates zero. Write Y for the 104 output roles
`r+112`, in the same order. Let M be W's X-to-Y matrix over Q.

The following three edits bypass whole intermediate owned stops. Event
indices refer to the retained word, before splicing.

| Edit | Owned path | Bypassed frame | Deleted outgoing reads |
| --- | --- | --- | --- |
| A | 772: 529 -> 520 -> 595 | 520 | 9013: `497 += -4*772` |
| B | 771: 541 -> 534 -> 117 -> 594 | 534 | 9162: `231 += 4*771` |
| C | the same 771 path | 117 | 9164: `629 += 2*771`; 9165: `732 += 771` |

For each nonempty subset S of {A,B,C}, delete its reads and replace each
affected path by its subsequence of retained frames. Preserve every other
instruction and every public endpoint. Call the result W_S and its main
matrix M_S. The verifier checks each entire modified path and every scalar
common-chart condition. These bypasses preserve total paid rank mass, but
they change the scalar map.

We allow arbitrary linear preparation before W_S using only fields at
frame 3 and arbitrary linear cleanup after W_S using only fields at frame
127. The correction phases contain no chart changes, address operations or
access to a field in another chart. They may mix any fields available in
their chart, use constant coefficients, and allocate zero scratch there.
Their ordinary cost is unrestricted. All main endpoints remain fixed.

## Exact defects and sharp ranks

**Finite certificate.** There are two rational row functionals v and w on X,
each supported on 52 main coordinates. In the source word v is the content
of owned register 772 just before event 9013, restricted to X. The functional
w is the content of owned register 771 just before each of 9162, 9164 and
9165, restricted to X. They satisfy

```text
v(e_0) = 1/4,   v(e_2) = 0,
w(e_0) = 0,     w(e_2) = -1/4.
```

With e_j now denoting output coordinate j, define output columns

```text
a = -2(e_145 + e_161),
b =  2(e_131 + e_152),
c =  2(e_130 - e_166 - e_214).
```

If alpha, beta, gamma are the indicators of A, B, C, respectively, then

```text
D_S = M_S - M = alpha*a*v + (beta*b + gamma*c)*w.             (1)
```

The verifier establishes (1) in two ways. The first propagates every main
coordinate symbolically through the source and each modified word. The
second pulls the four removed source functionals backward and propagates
four single-destination perturbations forward. For an ADD of coefficient q
the removed contribution is `-q*u*v`. Every perturbation has zero value in
the source of every later removed read, which eliminates all interaction
terms. The two calculations compare every one of the 10,816 coefficients
for each of the seven modifications. The source endpoint is used only as
the predecessor contract being preserved, not as an audit deliverable.

The supports of a, b, c are disjoint. The displayed values on e_0 and e_2
make v and w independent. Thus (1) gives the exact formula

```text
rank_Q D_S = 1[A in S] + 1[S intersects {B,C}].               (2)
```

For the lower bound, use row 145 and column 0 when A is present. Use row 131
and column 2 when B is present, otherwise row 130 and column 2 when C is
present. Each relevant diagonal entry is -1/2, with zero cross entries.
For the upper bound use the one or two outer products in (1). In particular,
the minimum number of arbitrary rank-one additive corrections to the main
matrix is exactly (2). This is an algebraic correction count, not a native
implementation or recursive price for acquiring v and w.

| S | Defect rank | Changed Y rows | Changed X-to-Y entries |
| --- | ---: | ---: | ---: |
| A | 1 | 2 | 104 |
| B | 1 | 2 | 104 |
| A,B | 2 | 4 | 208 |
| C | 1 | 3 | 156 |
| A,C | 2 | 5 | 260 |
| B,C | 1 | 5 | 260 |
| A,B,C | 2 | 7 | 364 |

## Preparation and cleanup cannot repair any bypass

**Scoped theorem.** No nonempty S preserves W's main map after any allowed
preparation and cleanup.

Every main input starts in a one-dimensional chart. Frame 3 is the zero
subspace. Consequently preparation cannot read or write a main input.
On a pure X input every field preparation can access is zero. Any allowed
linear preparation therefore fixes that input, including zero scratch.

Every main output ends in an eight-dimensional hyperplane. Frame 127 is
the full nine-dimensional space. Consequently cleanup cannot write a main
output. It leaves the Y projection unchanged, even when it reads main
inputs that have reached frame 127.

Thus for all allowed P and Q,

```text
projection_Y * Q * W_S * P * inclusion_X = M_S.
```

Equation (2) says M_S differs from M for every nonempty S. This proves the
theorem. A failing pure main input is enough to refute an arbitrary-input
identity. No assumption that dirty inputs are always zero is made.

## Available moment saving is less than one paid rank-one job

Write H_r = r^t with t=1-C and 0<C<=1/32. The largest saving among these
bypasses comes from removing all three stops. Strict subadditivity makes
each additional merge strictly beneficial before corrections. The maximum is

```text
G(C) = 3 + 4^(1-C) + 5^(1-C) - 2*6^(1-C).
```

Since ln(6)<2 and exp(-x)>1-x for x>0,

```text
6^(1-C) > 6(1-2C),
0 < G(C) < 12 - 12(1-2C) = 24C <= 3/4 < H_1.
```

For example ln(6)<2 follows from
`exp(2) > 1+2+2+8/6 = 19/3 > 6`. This proof needs no floating-point powers.
With all other paid work and productive targets fixed, a repair that adds
even one paid job of positive integer rank per native call therefore loses
the entire local gain. This conditional price statement does not assert
that every possible changed acquisition must use such a job. A free repair
at a different chronological chart, changed productive targets or changes
to other paid work are outside the theorem.

## Limits and next decision

This settles seven specified bypasses under the stated prefix/suffix
correction contract. It does not exclude any fourth stop, retimed reads,
interior compensation, a changed source graph, modified caller trees or
arbitrary P104 words. It supplies no new kappa, native supplier, all-size
compiler, precision bound or complete multiplication theorem. Independent
human and formal proof-kernel review are unclaimed.

The useful next construction must change how the main functionals v or w
are acquired or delivered, or change other target/paid work. More frame-3
preparation and terminal frame-127 cleanup alone cannot restore them.
