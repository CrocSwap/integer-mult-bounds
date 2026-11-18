# Three rectangles describe a canonical rotation row

This is a row-description theorem and an arithmetic generation algorithm.
It uses the closed descent in Ali Romman's PR7734 and the canonical endpoint
formulas of Nick Petalas. Cinna Davis's canonical Beneš compiler defines the
table. Exact source files and credit are in [CREDITS.md](CREDITS.md) and
[SOURCE-PINS.json](SOURCE-PINS.json). The canonical routing choices do not change.

## 1. Contract and result

Let `h>=1`, `N=2^h`, `1<=s<=N`, `0<=a<s`, and `0<=j<2h-1`.
The permutation is rotation by `a` on the first `s` addresses and identity
on padding. The row uses current-wire addresses. Set

```text
d = min(j,2h-2-j),    D = 2^d,    H = h-d,
x = Dy+t,            0<=t<D,     0<=y<2^H.
```

The set of wires whose canonical row bit is one is the union of at most
three rectangles `I x J` in `(t,y)` coordinates. Their `t` intervals are
disjoint. First rows (`j<h-1`) and the center row need at most one.
Three is necessary in general, even if the covering rectangles can overlap.

The descriptor needs `O(h)` bits and `O(h)` arithmetic bit work to construct.
One can emit the complete row in current-wire order with `Theta(N)` bit
work and `O(h)` temporary bits, excluding the output. This is a bit-work
algorithm. No fixed tape graph, owner restoration, actual CRT producer,
complete caller cost or new kappa is supplied.

## 2. Two thresholds suffice

Write `a=pD+u` and `s-a=qD+v`, with `0<=u,v<D`. The retained closed
descent gives the two interval lengths at depth `d`:

```text
A = floor((a+t)/D)       = p + [t>=D-u],
B = floor((s-a+D-1-t)/D) = q + [t<v].
```

The second identity follows because `0<=v<D` and `0<=t<D`.
The zero-remainder cases are included: the first threshold is then `D`,
and the second is `0`. Split `[0,D)` at `D-u` and `v`. There are at most
three nonempty intervals. On each interval, `A` and `B` are constant.

If either length is zero, every row bit is zero on this interval. This
uses the identity absorption proved in the retained closed-descent proof.
Otherwise let `S=A+B`. The source endpoint rule becomes this table of
half-open quotient intervals:

| Endpoint condition | Quotient interval where the bit is one |
|---|---|
| `H=1` | `[0,2)` |
| First, `S` odd and `A` odd | `[S-1,S+1)` |
| First, other parity | Empty |
| Last, `S` even and `A` odd | `[0,S)` |
| Last, `S` even and `A` even | Empty |
| Last, `S` odd and `A` even | `[0,A)` |
| Last, `S` odd and `A` odd | `[A-1,S+1)` |

These intervals lie in `[0,2^H)`. In fact `S<=2^H`, and an odd `S`
is at most `2^H-1`. When `H=1`, positivity forces `A=B=1`.
All nonempty interval endpoints are even. Each nonempty remainder strip
therefore gives one rectangle. Adjacent strips with the same quotient
interval can be merged. The total is at most three.

The descriptor stores at most twelve interval endpoints, the height and
the depth. Each endpoint needs at most `h+1` bits. Its construction uses
a constant number of additions, subtractions, comparisons and power-of-two
quotients or remainders. Sorting at most four cuts costs `O(h)` bit work.
Binary scans implement these operations in `O(h)` work. This does not
treat arbitrary integer multiplication as constant time.

## 3. First and center rows need only one rectangle

For a noncentral first row, the parity condition is exactly `A` odd and
`B` even, with both positive. If `v<=D-u`, the three possible pairs are

```text
(p,q+1), (p,q), (p+1,q).
```

Their respective qualifying parity pairs for `(p,q)` are `(odd,odd)`,
`(odd,even)`, and `(even,even)`. They are disjoint. If `v>=D-u`, the
possible pairs are `(p,q+1)`, `(p+1,q+1)`, and `(p+1,q)`; their qualifying
parities are `(odd,odd)`, `(even,odd)`, and `(even,even)`. Again, at most
one strip qualifies. Equal cuts and zero lengths only remove strips.

At the center, `H=1`. The condition that both lengths are positive is

```text
max(0,D-a) <= t < min(D,s-a).
```

It is one interval, possibly empty. The quotient interval is `[0,2)`.
Thus the center also needs at most one rectangle. For `h=1`, this is the
only row.

## 4. The three-rectangle bound is sharp

Take `(h,s,a,j)=(6,53,25,7)`, so `d=3` and `D=8`. Direct substitution gives

| Remainder interval | Quotient interval |
|---|---|
| `[0,4)` | `[2,8)` |
| `[4,7)` | `[0,6)` |
| `[7,8)` | `[0,4)` |

The one entries at `(t,y)=(0,6),(4,4),(7,0)` form a three-point fooling
set. A Cartesian rectangle that contains two points must contain both
cross points. For the three pairs, respectively, `(4,6)`, `(0,0)`, and
`(7,4)` are zero entries. Thus no all-one rectangle contains two witness
points. Every exact rectangle cover has at least three members. This
argument even allows arbitrary Cartesian subsets, not only intervals.

The descriptor contains `4*6+3*6+1*4=46` active wire bits. The row has
23 active switches, since each switch has two paired wires. In general,
the active-bit count is the sum of the three rectangle areas, and the
active-switch count is half this sum. These are counts for the canonical
row. They are not minima over all routing networks or swap factorizations.

## 5. Emit the row without a full-width query at each wire

The output order is increasing `y`, then increasing `t`. Sort all quotient
endpoints together with `0` and `2^H`. At most seven nonempty phases result.
Within one phase the pattern over `t` is fixed. Sort all remainder endpoints
together with `0,D`. There are at most seven runs, including zero runs.
Evaluate the constant bit of each run once per phase.

For a phase of `R` quotient values, repeat its run pattern `R` times.
Use canonical least-significant-bit-first countdowns for `R` and each run
length `L`. Zero is the empty list. A decrement of `n>0` visits
`v_2(n)+1` bits; if it clears the highest bit, remove that bit. Across a
complete countdown from `n` to zero, the exact number of visits is

```text
sum_(k=1)^n (v_2(k)+1) = 2n-popcount(n) < 2n,    n>0.
```

Return scans to the low end add only a constant factor. Empty-list tests
do not scan a fixed-width zero field. Retain one binary template for each
run length. Reset the inner counter by copying this template. For positive
`L`, its binary length is at most `L`. Thus all inner resets in one block
copy at most `D` bits. Across the whole row they copy at most `N` bits.

There are `2^H<=N` outer decrements. Inner counters have exactly `N`
decrements. The sum of their bit visits is less than `4N`. Outer resets
copy at most `7(h+1)` bits. The at most seven phases, each with at most
seven run templates and one outer template, use at most `56(h+1)` template
bits in total. Phase preparation and interval comparisons cost `O(h)`.
Loop control is constant per run, block or output bit; each nonempty run
emits at least one bit. Total work is therefore `O(N+h)=O(N)`.

Only a constant number of binary counters, templates and endpoints are
live. They need `O(h)` bits. The lower bound is `N` output writes for an
explicit `N`-bit row. This proves the stated `Theta(N)` bound. It is not
a lower bound for a compressed row or for a consumer that skips outputs.

`row.py` supplies the descriptor and stream control. Its statistics count
counter visits, template bits, copies and outputs. Python object management
and statistics updates are not a literal machine-transition measurement.
The proof describes the bit algorithm; it does not assert that Python's
runtime has that bound under an arbitrary interpreter cost model.

## 6. Verification and remaining boundary

The finite oracle is the unchanged PR4100 deterministic compiler. The
verifier checks every row for every legal modulus and offset at heights
one through six: 2,793 networks, 28,797 rows and 1,633,182 wire entries.
It also compares the retained PR7734 point query, all streamed bits,
rectangle areas, switch pairing, first/center caps and the work inequalities.
The table digest agrees with the predecessor census.

An additional 280 descriptors, with 4,937 boundary and random point checks,
reach height 65,536 without materializing large rows. There are 131,328
individual countdown checks, fourteen input rejection checks, three
rectangle mutation controls and a coordinate-order mutation control.
The executable height cap bounds descriptor input size; the written proof
has no height cap. Wide tests are finite evidence, not its proof.

A literal row producer still needs an ABI, scratch ownership, output
placement, head return and complete transition and historical-space bills.
Comparison with stored ROM requires the actual query/reuse workload and
transport, current-state offsets, payload use and retirement charges.
None is supplied by this descriptor theorem. All five selected framework
assumptions remain. No new kappa or full multiplication theorem is claimed.
