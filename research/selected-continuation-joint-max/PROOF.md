# Joint historical maxima for a fixed level grammar

## Contract and source

The scientific source is Jose Manuel/jmbarrancoml's PR2697,
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The unchanged PR2758
[exports](../selected-continuation-storage/SNAPSHOT.json) authenticate
[controller.py](../selected-continuation-storage/vendor/controller.py) and
[records.py](../selected-continuation-storage/vendor/records.py).
PR2758 supplies the prior stack grammar and live-content proof. Nick Petalas's
[PR2925](https://github.com/CrocSwap/integer-mult-bounds/pull/2925), exact
`9570df6e69824dd32bf58b6d66a8e57a790e3b85`, supplies the separate value-stack
allowance and the residue-dominant handoff. Neither predecessor is modified.

Fix index/residue word lengths `I,R >= 2`, ancestor depth `h >= 0`, and a
successful `Callback.weight` call. Retain the source's valid-coordinate,
chronology, arithmetic, unit-denominator and fixed-width premises. Its pending
and values stacks are private and empty, all four heads start at one, and
all retained cells after LEFT are blank. For the absolute envelope below,
the arrays initially have constructor lengths `(1,1,1,1)`, or their lengths
already fit this same grammar's coordinate vector c defined below. Program
and field data remain fixed throughout the call. Observers do not mutate
scientific state. Arbitrary longer entry arrays use the separate history rule.

Count only the four `Tape.cells` lengths, including LEFT and erased tails.
This is neither allocator capacity nor total machine memory. Input programs,
fields, numerical words and other callers are excluded. A successful-call
bound does not prove success, exception cleanup or a physical implementation.

Write `A=2I+4`, `B=R+3`. VALUE has A symbols; CONSTANT, MULTIPLY, PAIR and
RETURN each have B. The new result is the joint historical-maximum bound

```text
h = 0                 2A + 2B + 2
h >= 1, A >= B        (h+2)A + (2h+2)B + 2
h >= 1, B > A         (h-1)A + (2h+5)B + 2.
```

The last line improves PR2925's allowance by `(h-1)(B-A)`. It does not lower
the individually sharp pending-main bound. Both nonzero-depth envelopes are
sharp for the level-uniform grammar, conditional on realizing the indicated
successful branch trace at those widths. This does not assert that every
selected catalogue item realizes an attaining trace.

## Why the literal source has a level-uniform grammar

In `weight`, a VALUE's numerical coordinate changes arithmetic values and
indices. Its continuation types depend only on the level. `step(level)` reads
the fixed program's level record. `prepare(slot,code,self.depth)` reads the
same raw field and receives no coordinate argument. Deterministic
`good_pivots` or `fallback` therefore produce the same branch classification
for every request at that level. UNIT, GOOD or PAIR is fixed there. In PAIR,
the two predicates `row < 64`, for `field` and `permutation[field]`, are also
fixed there. All real children at the next lower level consequently share
the same continuation shape. Numeric coefficients need not be equal.

This argument uses fixed program/field data and the literal deterministic
preparation. It is not a property of an arbitrary recursive expression tree
or a coordinate-dependent replacement callback.

## Exact per-program recurrence

Let P and V be the separate historical symbol maxima on pending main and
values main during a complete subtree evaluation. Let D be the retained
length of pending reverse. Values reverse always has length B after the final
RETURN pop. At depth zero `(P,V,D)=(A,B,A)`.

For a PAIR, left/right mean push order. The right child executes first.
The following table extends a lower-level triple `(P,V,D)` to the next level.

| Level | P' | V' | D' |
| --- | --- | --- | --- |
| UNIT | A | B | A |
| GOOD | max(A,B+P) | V | max(D,B) |
| PAIR, two real children | A+B+P | B+V | max(D,B) |
| PAIR, left real/right constant | max(A+2B,B+P) | B+V | max(D,B) |
| PAIR, left constant/right real | 2B+P | max(V,2B) | max(D,B) |
| PAIR, two constants | max(A,3B) | 2B | max(A,B) |

For two real children, pending first retains the PAIR and the left VALUE
while evaluating the right subtree, giving `B+A+P`. The same lower subtree
later runs above one completed right RETURN on values, giving `B+V`.
For left-real/right-constant, pushing both tasks gives `A+2B`, then evaluating
the left subtree leaves only its PAIR below it, giving `B+P`. The completed
right constant adds B to the left subtree's value maximum. For
left-constant/right-real, pending retains two B-sized records below the
right subtree, while values peaks either inside that subtree or when the
left constant joins its completed result. The two-constant and GOOD cases
follow their literal push/pop order. UNIT never consults lower levels.

These maxima include statement interiors. Push writes one prefix of a
record at a time and cannot exceed the completed push. Pop never extends
main; it copies `L-1` symbols to reverse after erasing RECORD_END. Thus a
popped record of length L leaves exactly L reverse cells including LEFT.
PAIR and MULTIPLY pop old returns before pushing their replacement. The
main arrays remain contiguous, so their maximum lengths are P+1 and V+1.
No erasure shortens any array. Starting with constructor-length arrays,
the final four lengths are exactly

```text
c = (P+1, D, V+1, B).
```

Separate temporal peaks can be added here because each array retains its
own maximum to return. This is a backing statement, not simultaneous live
content. The executable recurrence is `capacities` in [verify.py](verify.py).

## The residue-dominant induction

Assume B>A. The component inequalities are

```text
P_d <= (2d+1)B,       V_d <= (d+1)B.
```

They follow directly from the table, including UNIT and the base P_0=A.
For d>=1, the stronger joint invariant is

```text
S_d = P_d+V_d <= Q_d = (d-1)A+(2d+3)B.
```

At d=1, direct substitution into all six rows gives maximum `5B=Q_1`,
attained by two constants. For d>=2, write P,V,S for the lower triple.
The two-real row gives `S'=S+A+2B <= Q_d`. The mixed rows give

```text
left real/right constant: S' = max(A+3B+V, S+2B)
left constant/right real: S' = max(S+2B, P+4B).
```

Use `V <= dB`, `P <= (2d-1)B`, and `S <= Q_(d-1)`. The first row is at most
`max(A+(d+3)B, Q_(d-1)+2B) <= Q_d`; the second is at most
`max(Q_(d-1)+2B, (2d+3)B) <= Q_d`. GOOD gives `S+B <= Q_d`; UNIT and two
constants give at most A+B and 5B. Pending reverse contributes at most B,
values reverse B, and the main LEFT cells contribute two. This proves the
new envelope. A bottom two-constant PAIR followed by h-1 two-real levels has

```text
P = (h-1)A+(h+2)B,     V = (h+1)B,     D = B,
```

so equality holds. At h=2,I=14,R=32, lengths are `(173,35,106,35)`, total
349. Pure binary gives 343 and is not maximal. PR2925's allowance is 352.

For A>=B the table gives `P_h <= (h+1)A+hB`, `V_h <= (h+1)B`, and D<=A.
This recovers the already established request-dominant bound, attained by
h two-real levels. At h=0 the initial VALUE and final RETURN give the exact
depth-zero formula independently of the relation between A and B.

## Entry history and necessity of the premises

For arbitrary blank restored-head entry lengths K_j and a fixed grammar,
the exact final lengths are `max(K_j,c_j)` coordinatewise. Repeated calls with
the same grammar preserve c. Fixed program/fields and fixed h,I,R therefore
allow repeated requests for different valid coordinates under this bound.

Arbitrary histories across different grammars need the coordinatewise rule.
At h=2,A=32,B=35, bottom two constants followed by left-constant/right-real
has lengths `(176,35,71,35)`. Reusing those arrays for the attaining grammar
gives `(176,35,106,35)`, total 352. The sharper fresh envelope is 349.
No improved arbitrary-history theorem follows.

Nonuniform trees also defeat the envelope. At h=3, put a two-real PAIR at
the top. Its first-evaluated subtree is a mixed left-constant/right-real PAIR
above two constants; its later subtree is a two-real PAIR above two constants.
This yields P=A+6B and V=4B, total `A+12B+2`, larger than the uniform bound
by B-A. The literal weight control at I=20,R=64 reaches 850 versus 827 by
deliberately varying the fixture metadata between level-two requests.
This is outside the fixed-program contract. Both rejection examples are
executed in [verify.py](verify.py), with unchanged weight/Stack/Tape code.
