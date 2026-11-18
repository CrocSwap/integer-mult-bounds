# Direct canonical switch queries for padded rotations

This scoped written proof gives a new arithmetic construction of the precise
deterministic tables in Cinna Davis's #4100 `check_batched_crt.py:benes`.
The source is pinned at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57` in SOURCES.json. Its generic
permutation-routing theorem is a cited premise. No predecessor replay is a
deliverable of this package. This contribution was produced by Nick Petalas.

## 1. Domain and result

Let `N=2^h`, `h>=1`, `1<=s<=N`, and `0<=a<s`. Write

```
P(x) = (x+a) mod s   for 0<=x<s,
P(x) = x             for s<=x<N.
```

There are `2h-1` canonical switch rows, numbered from zero. A row at index
`j` flips axis `min(j,2h-2-j)` when its table bit at the *current wire*
address is one. This is a table query, not a query indexed by the original
input token's address.

For `h>1`, the first row is

```
F(x) = [s and a are odd] [floor(x/2)=floor(s/2)].                 (1)
```

The last row is

```
L(x) = [a is odd] [x<s]                     if s is even;
L(x) = [x<a]                                if s is odd, a even;
L(x) = [a-1 <= x <= s]                       if s and a are odd. (2)
```

Brackets denote the indicator of a condition. For branch `c` in `{0,1}`,
put

```
s_c = floor(s/2) + [s odd and c=(a mod 2)],
b_c = floor(a/2) + c(a mod 2),
a_c = b_c mod s_c.                                             (3)
```

The child on that branch is exactly the padded rotation with parameters
`(N/2,s_c,a_c)`. An empty child is identity and needs no modular division.
In every nonempty child `0<=b_c<=s_c`, so reduction in (3) is just replacing
`b_c=s_c` by zero. Thus no general integer division is necessary.

For an interior row `0<j<2h-2`, its bit is the child's bit at

```
(h,s,a,j,x) -> (h-1,s_(x mod 2),a_(x mod 2),j-1,floor(x/2)).      (4)
```

At `h=1`, the only row has constant bit `a`. If `a=0`, the entire network
is identity. Equations (1)-(4) compute one canonical bit by at most `h`
iterations, with `O(h^2)` elementary bit operations and `O(h)` working bits.
These are bounds for bounded-integer arithmetic, not a physical tape bill.

## 2. Canonical component colors

The source colors the graph with the two perfect matchings

```
A(x)=x xor 1,             B(x)=P^{-1}(P(x) xor 1).
```

It starts each uncolored component at its least vertex with color zero.
For an even-cycle component, fixing that first color uniquely determines
all colors. DFS neighbor order therefore does not affect the result. The
source's endpoint rows are

```
F(x)=color(x) xor (x mod 2),
L(y)=color(P^{-1}(y)) xor (y mod 2).                             (5)
```

Call `A` pairs with coincident `B` edges doubled pairs. Every doubled pair
whose least endpoint is even has colors equal to address parity.
Write `s=2m+epsilon`, `a=2b+delta`.

If `s` and `a` are both even, all components are doubled pairs. If `s` is
even and `a` is odd, the active interval `[0,s-1]` forms one alternating
cycle: its `B` edges are `(1,2),(3,4),...,(s-3,s-2),(s-1,0)`.
All remaining components are doubled pairs. Both cases give
`color(x)=x mod 2` everywhere. The size-two cycle may itself be doubled.

Suppose `s` is odd and `a` is even. The component containing the first
padded vertex `s` is the interval `[s-a-1,s]`. Its edges alternate along
successive vertices, with one closing `B` edge between the interval's
endpoints. Its least vertex `s-a-1` is even. Every other component is a
doubled pair. Again `color(x)=x mod 2` everywhere. For `a=0` the named
interval is just the doubled pair `(s-1,s)`.

Finally suppose `s` and `a` are odd. Put `t=s-a`, which is even and at
least two. The exceptional component has vertices

```
0,1,...,t-1, s, s-1.
```

There are alternating consecutive edges on `[0,t-1]`, the `B` edges
`(t-1,s)` and `(s-1,0)`, and the `A` edge `(s-1,s)`.
Starting at zero gives parity colors on `[0,t-1]`, color zero at `s`,
and color one at `s-1`. All other components are doubled pairs. Hence

```
color(x) = (x mod 2) xor [x in {s-1,s}].                        (6)
```

These descriptions follow directly by substituting the rotation and its
inverse into `B`; they list all edges because each vertex has one `A`
neighbor and one `B` neighbor. In particular they also identify each
component's least vertex and settle the source's orientation convention.
Substitution in the first equation of (5) proves (1).

## 3. The last row

For `y<s`, the inverse is `y-a` when `y>=a`, and `y+s-a` when `y<a`.
For `y>=s` the inverse is `y`.

When `s` is even, the active inverse changes parity exactly when `a` is
odd, giving the first line of (2). When `s` is odd and `a` even, precisely
`y<a` changes parity, giving the second line. When both are odd, the
inverse changes parity on `[a,s-1]`. The two exceptional colors in (6)
occur at inverse addresses `s-1` and `s`, corresponding to `y=a-1` and
`y=s`. Neither is in `[a,s-1]`; adding both gives `[a-1,s]` and proves
the third line. The first padded wire can have a nonzero switch even
though the completed permutation fixes every padded wire.

## 4. Child closure

The source defines child `c` at index `floor(x/2)` to have value
`floor(P(x)/2)` for the unique `x` of color `c` in that input pair.
The parity cases give the following complete table. A zero modulus is
the empty identity child.

| s | a | child 0 modulus, offset | child 1 modulus, offset |
| --- | --- | --- | --- |
| 2m | 2b | m, b mod m | m, b mod m |
| 2m | 2b+1 | m, b mod m | m, (b+1) mod m |
| 2m+1 | 2b | m+1, b mod (m+1) | m, b mod m |
| 2m+1 | 2b+1 | m, b mod m | m+1, (b+1) mod (m+1) |

For the first three rows, colors are parity, so substituting `x=2z+c`
into the two branches of `P` gives the displayed rotation. At any input
pair entirely beyond the active range, `P` fixes both addresses and the
child fixes its index.

For the last row, child zero uses `x=2z` for `z<m`, and uses the padded
`x=s` at `z=m`; child one uses `x=2z+1` for `z<m`, and uses `x=s-1` at
`z=m`. For child zero, the active values are

```
z+b             when z<m-b,
z+b-m           when m-b<=z<m;
```

the index `m` is fixed. Thus its modulus is `m` and its offset is `b`.
For child one the values are

```
z+b+1           when z<m-b,
z+b-m           when m-b<=z<m,
b               when z=m.
```

This is the rotation modulo `m+1` by `b+1`. All larger indices are fixed.
The table is exactly (3), including its padding behavior. Induction on
`h`, using the source's interleaving of the two child tables, proves (4)
and equality of every directly computed bit to its canonical source bit.

## 5. Arithmetic cost and scope

Keep four records for `s,a,x,j` and a record for the current height. At
most the initial `h+1` bits are needed by any of `s,a,x`; the row and
height records need `O(log(h+1))` bits. Each descent requires parity
tests, halving, a constant number of comparisons, additions and
subtractions, and the equality reduction in (3). Scanning their binary
records implements each operation in `O(h+1)` bit operations. Height
decreases at every descent, so total work is `O(h^2)` and working storage
is `O(h)`. No recursion stack, permutation, component graph or row ROM is
part of the new evaluator. The Python implementation bounds `h<=4096`;
the written recurrence and proof apply to every positive `h`.

This is not a shortest-switch circuit or a claim that physical repeated
queries are always cheaper than a retained ROM. It gives the exact same
Boolean table predicate, a useful prerequisite for replacing the whole-ROM
producer in the current-state key boundary. Producing the current CRT
offset, serializing descriptors, returning an owned predicate, disposing
of work, physical tape access, malformed-stream recovery and a complete
caller bill remain separate. No supplier admission, new kappa, or complete
multiplication theorem follows.

## 6. Verification and bounded-resource implementation

The verifier compares the new evaluator with the pinned canonical
definition for every modulus and offset at heights one through five. It
also extracts the two actual child permutations and checks (3), then
routes every address using only the new point queries. These are finite
checks of the new construction, not a re-execution of #4100's research
verification or a substitute for the proof above. It hashes the 544
bit-bytes at `h=5,s=17,j=6`, the key's table geometry, without importing a
predecessor receipt. Domain, semantic and large-width checks are explicit
exceptions and remain active under Python optimization.

Power of Ten inspection: all new functions fit within 60 physical lines;
the evaluator has one loop bounded by 4096 and no recursion. Verification
heights are bounded by five and each network has at most 32 addresses and
nine rows. The imported canonical comparison function recursively
constructs only these small networks, with depth at most five. This is a
rule-1 deviation for an immutable source oracle; the new evaluator and
new verification loops are iterative. Replacing that oracle would remove
the exact-source comparison this package needs. Follow-up: retain the
depth cap whenever increasing finite coverage.

Python's managed runtime allocates integers and small containers during
execution, a rule-3 deviation. The public height cap bounds the live
evaluator integers by 4097 bits and the fixed census bounds its live
network storage. The inherited comparison oracle allocates at most five
levels with 32 wires at the top. No asynchronous work, open file resource,
dynamic code generation or newly shared mutable state is introduced.
The sole import through a file loader has a fixed SHA256-authenticated
target and is a rule-9 deviation for the comparison oracle, not a dynamic
production dispatch. Normal and optimized warning-strict runs, source
authentication and the finite rejection controls are the compensating
checks. Follow-up: changing that target requires a new source pin and
review of this proof's orientation convention.

No project Python linter or installed `ruff`, `mypy` or `pyright` was
available. Warning-strict normal and optimized execution, AST parsing,
registered package metadata/source checks and committed-byte checks are
the available diagnostics. The two warning-strict commands are registered
in VERIFY.json for recurring CI replay; no shared diagnostic configuration
is changed.
