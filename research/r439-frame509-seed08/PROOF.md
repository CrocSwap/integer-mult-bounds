# Finite replacement, restoration and complete local bill

Let `E(d,s)` be the integer elementary row addition `x_d <- x_d + x_s`.
The original and candidate operators are products of these additions on the
same eleven physical registers at frame 509. `verify.py` executes each
operator separately on all eleven integer unit columns and obtains exactly
the same columns. It does not import `search.py` or its matrix routine.
Since both operators are Z-linear, this proves equality for arbitrary
integer entering values, and therefore for arbitrary values after coefficient
reduction in any commutative ring, including F2. The 2,048-input Boolean
table is additional finite evidence, not the reason for the ring statement.

Register 468 starts with its own independent dirty-input column. The equality
includes that column and its complete output; scratch is never initialized
to zero. All other columns, including entering values accumulated earlier
in A or B, are also arbitrary. Thus the two words agree at the end of the
substituted slice, and all later target reads receive the same values.

The source and candidate use the same frame and all eleven participants.
Every participant's first touch may move within this slice, but no earlier
operation in that slice acts on it before its first touch. Its climb carries
the same entering value to the same frame. The verifier compares every
register's full ordered frame path, and the unchanged source checker checks
E8 labels, closed frames and nested climbs. Native legality checks all MOVE,
ADD, COPY and ERASE records chronologically.

Only B and C change. Every altered B gate writes a source or helper and reads
only a source or helper. C is rebuilt as the literal reverse of all
z-destination A/B gates at the full frame. Over F2 each elementary addition
is an involution, so this is the same inverse on arbitrary dirty contents.
The unchanged owning checker rechecks H1-H5 and the separate U/J/K/U-inverse
conclusions on all 661 independent input columns. In particular, stale C
can preserve the endpoint while violating literal H4; the stale-cleanup
negative control therefore checks that exact interface requirement.

Replacing 31 B ADDs by 21 also removes ten corresponding C ADDs. D, A,
scatter and all other B gates agree. Every non-ADD exported record is retained
in the multiset, every register has the same ordered frame path, and the
native chronological check independently validates all lifecycles. Thus
20 deletions are the entire complete local saving: 24,305 -> 24,285 ADDs.
All 439 helpers, nine copied totals, source accesses, frame climbs,
restoration and recursive charges are accounted for. The paid histogram
and rank mass are unchanged. This provides no larger bit exponent.

For positive growth, the two forward integer operators agree and the new
reversed positive operator is entrywise no greater than the old one. The
reverse entry sums are 52 and 94, respectively; the verifier checks entries
individually rather than inferring domination from sums. It also replays
the entire exported stream in both directions with cancellation-free
nonnegative bounds, including COPY/ERASE resets and copied-source immutability.
Both Python and unchanged native checkers give

```text
F = 49347, B = 1106918
64 F^3 B^2 = 9423085667358616084409488128 < 2^104
```

The bit length remains 93, and the old charged cap is retained. This is a
finite native payload obligation. It does not prove the inherited all-size
precision/tape interface or a new globally hosted invoice.

Fresh unchanged C++ checkers execute the original and candidate words at
5/9/11 stages on 883/1,327/1,549 independent columns, including independent
dirty inputs and all required bridges. The specialized five-stage checker
and general KPAIRS=2 checker agree field for field. The distinct bridge
omission controls total 96 across the two words; the equivalent KPAIRS=2
recheck is not double-counted. Literal reverse cleanup, paid rank and prefix
fields are compared with the independent local receipt.

The search coverage is only the 12,000 recorded trajectories. Dead ends and
incumbent cutoffs are distinct from accepted factorizations. An incumbent
cutoff does not exclude shorter circuits with other reduction orders, and
the diagonal restriction does not describe every positive factorization.
Neither the finite search nor the native replay is an optimality theorem
or a formal proof of the full asymptotic multiplication bound.
