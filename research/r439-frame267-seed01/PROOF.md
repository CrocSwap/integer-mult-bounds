# A 12-ADD factorization and its precise minimum

This is a finite circuit result. Indices in the circuit are ordered physical
registers `(222,351,353,369,379,486)` of DreamingOfClouds' PR589 word. The
source slice is phase A `[615,636)`, entirely at frame 267 (rank four).
All six registers are dirty helpers; none is assumed zero. A gate `(d,s)`
is `x[d] ^= x[s]`. Its positive lift replaces XOR by integer addition.

The positive transfer of the original 21 gates is

```
M = [1 2 1 1 2 1]
    [0 1 1 1 1 0]
    [1 3 3 2 3 1]
    [1 3 2 3 3 1]
    [1 3 3 3 4 1]
    [0 1 1 1 1 1].
```

The replacement, in execution order, is

```
(1,4), (0,1), (1,3), (1,2), (5,1), (3,1),
(0,5), (3,0), (4,3), (4,2), (2,1), (2,0).
```

Independent column evolution checks `P(new)=P(old)=M` over the integers;
reduction modulo two therefore gives the identical ordered F2 map on every
incoming state. All 64 Boolean inputs are also checked. The two literal
reverse positive matrices satisfy `P(reverse(new)) <= P(reverse(old))`
entrywise; both matrices are retained in `CERTIFICATE.json`.

## What is minimized

**Proposition (finite positive-transfer class).** Twelve is the minimum
number of operations `row[d] += row[s]`, `d != s`, taking the ordered 6-by-6
identity to M, with six wires and no additional registers. Repeated writes,
repeated reads, and all 30 ordered pairs are allowed. The certified witness
also obeys the reverse-domination guard.

To enumerate the class, remove a circuit's last operation: subtract its
source row from its destination row. Every intermediate positive-addition
matrix is entrywise at least I: it starts at I and each nonnegative row
addition only increases entries. Thus a candidate predecessor is retained
exactly when the subtracted row is nonnegative and its diagonal entry is at
least one. This necessary test cannot remove an actual positive circuit.
Conversely every edge retained by this test is reversed by the specified
legal row addition. A path ending at I therefore constructs a valid circuit.
Each subtraction decreases total entry mass strictly (the source has a
positive diagonal), so the predecessor graph is a finite DAG.

`search.py` enumerates its entire closure from M: **416,508 states and
2,366,680 directed edges**. The recurrence is `d(I)=0` and
`d(A)=1+min d(B)` over all retained predecessors, with infinity for a dead
end. It gives `d(M)=12`; `999` in the saved histogram denotes infinity,
not an actual circuit length. The total entry mass of M is 58, so every retained path has at most
58 - 6 = 52 edges. The sentinel exceeds every possible finite distance.

`optimality.py` shares no nomination code. It stores flat byte matrices and
performs breadth-first search from M. It fully expands distances 0 through
11, testing **2,271,945 transitions** and discovering **410,887 states**
through layer 12. I first occurs in layer 12. Its layer sizes are

```
1, 14, 121, 738, 3294, 11132, 28779,
56137, 82349, 91299, 75736, 44081, 17206.
```

The independent traversal checks the lower bound; the explicit circuit checks
the upper bound. These are two implementations of the same justified graph,
not two different mathematical relaxations or independent human reviews.
Neither proves optimality among arbitrary XOR circuits (which may change the
positive integer matrix), extra-wire circuits, or altered frames. No general
multiplication theorem is formalized.

## Substitution, cleanup, and complete local cost

The source slice is contiguous, with no external observer between its gates.
Its identical endpoint permits every later A operation, scatter, B and D to
remain unchanged. Rebuild C as the literal full-frame reverse of *all*
z-destination gates of A followed by B. XOR gates are involutions, so this
restores every source and helper, including its arbitrary incoming dirt.
The original H1-H5 predicates and U/J/K/C decomposition all pass unchanged.

The same six physical registers visit the same common frame, with no other
frame or register introduced. The verifier compares all 661 ordered frame
paths, including final climbs. The unchanged exporter and separate record
interpreter then account for every read, write, move, copy and erase:

| Local charge | Original | Replacement |
|---|---:|---:|
| D additions | 18,085 | 18,085 |
| A additions | 2,130 | 2,121 |
| Scatter additions | 527 | 527 |
| B additions | 934 | 934 |
| C additions | 2,629 | 2,620 |
| **All ADDs** | **24,305** | **24,287** |
| MOVEs | 2,911 | 2,911 |
| COPY / ERASE pairs | 9 | 9 |
| Persistent registers / dirty helpers | 661 / 439 | 661 / 439 |

There is one existing temporary COPY register, reused under the inherited
lifecycle; no extra scratch or child is introduced. The local paid histogram
is exactly `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` on both words; its rank
mass is 5,129. Every paid recursive rank count is retained. Hence the paid
moment is identical for every exponent. This is a scalar-cost saving only.

For every nonnegative input bound vector, the replacement's forward terminal
bound is identical and its reverse terminal bound is no larger. Positive
addition prefixes are bounded by their terminal vector. Substitution within
an otherwise identical monotone stream therefore cannot raise either local
positive prefix bound. Fresh native replay confirms forward bound **49,347**
and reverse bound **1,113,070 -> 1,107,434**. The inherited five-stage payload
formula `64 F^3 B^2` stays at **93 bits**, below its 104-bit cap. Native 9/11
stage receipts retain their respective complete formulas and controls.

The full hosted parent invoice is not reconstructed by this package. The
changed finite word must still be integrated and source-bound by a maintainer.
The selected assembly is complex-bound; its selected kappa is unchanged.
All-size/compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape and analytic hypotheses remain inherited.
