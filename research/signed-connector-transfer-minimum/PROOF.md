# Four one-way transfers are necessary and sufficient at twelve child queries

This is a written, scoped circuit theorem with exact finite certificates. It is
not a proof-assistant theorem or a full integer-multiplication result.

## 1. Interface and quantifiers

Work over K = Q or C, with distinct arbitrary-dirty arrays
`x0,x1,x2,y0,y1,y2,z,w` of any common positive length. The six fixed K-linear
operators Ai, Bj need not commute or be invertible. A word must work uniformly
for every such choice and every input. Allowed ordinary queries are

`root += s Bj xj` and `yi += s Ai root`, with `s = +/-1` and root z or w.

Every complete query preserves its source, other rows, private scratch, and
required head positions. No output is read. Sources and coefficients are fixed.
The only additional operations are paid one-way root shears `z += a w`, for
fixed arbitrary `a in K`, with no effect on w. Zero shears can be removed.
No opposite-direction transfer, root scaling, copy, combined query, source
mutation, extra root, or arbitrary query coefficient is in this theorem.

Required output: `yi += sum_j Mij Ai Bj xj`, with

```
M = [1  1  1]
    [1  1 -1]
    [1 -1  0].
```

Sources and both roots restore. Restrict to exactly twelve ordinary queries.
The minimum number of nonzero root shears is **four**. This is lexicographic
optimality at twelve queries, not a global optimum with arbitrary tariffs or
with more queries. Characteristic two and special operator identities are
excluded. The original one-root result is Ross Richardson's PR944; the
twelve-query two-root construction and query lower bound are Charles Bethin's
PR1637. The new result concerns its paid transfer count.

## 2. A four-transfer witness

The literal word in CERTIFICATE.json is:

```
y0 += A0 z
z  -= w
w  -= B0 x0
y2 -= A2 w
w  -= B1 x1
z  += w
y1 -= A1 z
z  -= B2 x2
y0 -= A0 z
z  -= w
w  += B0 x0
y2 += A2 w
w  += B1 x1
z  += w
y1 += A1 z
z  += B2 x2
```

Write `u=B0 x0`, `v=B1 x1`, `t=B2 x2`, with initial roots z0,w0.
At the two A0 reads, z is z0 and z0-u-v-t, giving A0(u+v+t).
At the two A1 reads, z is z0-u-v and z0-t, with signs minus then plus,
giving A1(u+v-t). At the two A2 reads, w is w0-u and w0-v, with signs
minus then plus, giving A2(u-v). Final roots are exactly z0,w0.
This proves the all-input identity without interchanging any Ai with any Bj.
The inverse reverses the entire word and negates every query/shear.

## 3. Consequences of twelve queries

For completeness, specialize the operators to identities and consider one
coordinate, with independent input symbols. A nonzero target column needs its
Bj, and a single Bj occurrence cannot be restored through invertible root
shears. A nonzero row needs its Ai, and a single Ai read leaves a nonzero
coefficient of the arbitrary initial root dirt. Therefore all six operators
occur at least twice; twelve forces exactly two each. This is PR1637's query
bound in the present narrower root alphabet.

Let h be the sum of root-shear coefficients so far. The dirty-root matrix is
`U(h) = [[1,h],[0,1]]`. Restoration requires final h=0. Normalize the roots by
U(h)^(-1). A source query into z injects direction `(1,0)`; one into w injects
`(-h,1)`. Two occurrences can cancel only if they use the same root and
opposite signs. For a w-bound Bj, their h values must additionally agree.

Likewise a read of z sees dirty row `(1,h)`, and one of w sees `(0,1)`.
Two Ai queries cancel dirt only when they read the same root with opposite
signs; a z-bound Ai must read at the same h on both occurrences. These
necessities include every port/sign choice. They do not assume a chosen
schedule or that intermediate source values vanish.

## 4. At most three restored shears cannot transmit a cross-root product

This extends woklerx's PR1438 source-port/dirty-column argument for two
characteristic-two XOR transfers. Here the coefficients are arbitrary in
characteristic zero, three nonzero shears may restore, and the three-height
case must be handled. The partition method and earlier four-transfer mixed
fixture are predecessor contributions, not new ideas claimed here.

With at most three nonzero shears and final h=0, the complete sequence of
constant-height segments is one of

```
0                    (zero shears),
0, a, 0              (two shears; a != 0),
0, a, b, 0           (three shears; a,b != 0 and a != b).
```

One nonzero shear cannot restore. Crucially, each nonzero height occupies just
one uninterrupted segment. These are symbolic cases over K, not bounded
integer choices of a,b.

Consider a w-bound Bj with its two queries at common height hj. Its coefficient
in w is a signed interval indicator I, and its coefficient in z is
`s (h-hj) I`. If hj is nonzero, both queries lie in the single segment hj, so
there is no intervening root shear and this z coefficient is always zero.
If hj=0, a paired z-bound Ai either reads at height zero, where the cross
coefficient is zero, or reads twice in one nonzero segment. In the latter case
I is constant between those reads because both Bj calls occur at height zero;
the two opposite reads cancel. Thus every w-source/z-output product is zero.
A z-source/w-output product is always zero because the allowed shears never
move z into w.

The support graph of M is connected: either of its first two rows touches all
three columns, and the third row touches the first two. Since a nonzero entry
now requires its Ai and Bj to bind to the same root, all six operators must
bind to one root. Removing the root shears yields a one-root paired-query word
with the same source-product coefficients. Root dirt already cancels by the
equal-height condition. Hence a twelve-query realization would contradict the
one-root obstruction below.

`short_transfer_lemma()` also checks every relative order of the two source
calls, two reader calls and the ordered shear events using formal coefficient
pairs for a,b. It examines 6,90,210 event orders in the three cases, with
6,42,56 admitted by both restoration conditions; every admitted cross
coefficient is identically zero. The four-transfer shape 0,a,0,a,0 has four
admitted nonzero cross-couplings, so this checker can detect the changed
mechanism. Dropping either restoration condition also produces nonzero
counterexamples. The written case classification is essential to interpreting
this finite symbolic check as evidence for arbitrary coefficients.

## 5. The finite one-root obstruction

Exactly two queries for each source force one +ej and one -ej step in a
closed three-coordinate source walk. Each output uses two opposite reads,
so its desired row must be a difference of two visited vertices. Conversely,
such read pairs can be inserted independently at those boundaries.
Every possible six-step source walk is a permutation of six distinct signed
moves, so there are exactly 6! = 720. No restriction on integer intermediate
values is imposed. Their target-row coverage masks have counts

| Mask | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Walks | 72 | 84 | 84 | 48 | 264 | 84 | 84 | 0 |

Bit i means row i is available; none has all three. The permutation checker
and a separately written signed-pair DFS reproduce this table. This is a
fresh finite replay of PR944's obstruction, credited to that predecessor,
used to close the new short-transfer reduction. It is not a newly discovered
one-root lower bound. Together with sections 2–4 it establishes the scoped
four-transfer minimum.

## 6. Limits

Bidirectional root shears, arbitrary query scalings, more ordinary queries,
extra rows, mutable sources, and restricted operators can evade steps in this
proof. No exclusion for those classes follows. The signed query coefficient
condition and arbitrary independent dirt are material. The exact all-size
linear identity requires the stated restored child interfaces. Physical
supplier ports, frames, owner admission, precision and outer assembly have
not been instantiated in the selected multiplication construction.
