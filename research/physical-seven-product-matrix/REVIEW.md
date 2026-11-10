# Independent exact-matrix and physical-interface review

Prepared for @CubeJerry with substantial OpenAI assistance by a reviewer
separate from the kernel author. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

Reviewed `seven_product.py` SHA256:
`3e6639aca88822e879abd563b427eb499e1b7650c3d209ad51587ac8756da401`.
This reviews a physical refinement of the inherited seven-product identity
and exact #5059 product interface. It claims no new identity, rounded
residual theorem, original-reference bridge or multiplication exponent.

## Independent mechanism

`classical_oracle.py` computes expected entries by ordinary exact
Python-integer i,j,k dot sums. It imports no physical kernel, coefficient
table, quadrant schedule or seven-product expression. It also checks
admitted signed input/output carriers. Host integers are confined to
fixture encoding and expected/observed results, outside the physical call.

`independent_physical.py` serializes and observes raw two's-complement
bits directly, without the author's Signed matrix encoder/decoder.
The actual invocation runs under the authenticated `no_decode` guard
and unchanged scalar-word child. Input contents and heads are compared
before and after. An observer-only traversal of the owner's object graph
discovers its physical Tape closure independently of `forbidden()`.
The sets agree and contain 1338 roles. Every role, including historical
allocated backing, is blank and restored after consuming the return.

## Executed finite coverage

Both `-I -W error` and `-I -W error -O` passed the same six cases on one
reused owner, in this order:

| Case | B | Input bits | Exact scalar calls |
| --- | ---: | ---: | ---: |
| Signed-minimum singleton | 1 | 2 | 1 |
| Two noncommuting matrices | 2 | 4 | 7 |
| Mixed signs and cancellation | 4 | 4 | 49 |
| All signed minima | 8 | 2 | 343 |
| Singleton after the large call | 1 | 1 | 1 |
| Mixed signs after the short call | 8 | 3 | 343 |

Each B=8 call executes 400 nodes and 399 matching pushes/pops, along with
343 actual Arithmetic scalar-child calls. Output agrees bit for bit with
the independent classical result. The fixed role inventory is unchanged
across the long-short-long history.

The all-minimum B=8 case is a guard adversary. Completed entries equal 32
and fit the inherited nine-bit return. A repeatedly summed leaf operand
has magnitude 16, whose square 256 equals the excluded positive endpoint
of that carrier. Reusing the root return width internally would fail on
an admitted input. The independently checked kernel uses its wider carrier.

Four oracle failure controls reject reversed operand order, a transposed
second operand, transposed output and one-unit corruption. These inject
wrong output arrays; they are not presented as executions of mutated
physical source. Separate author controls test physical failure recovery.

## Static obligations and limits

The flat controller retains one current encoded dimension. Its stage tag
ranges over seven fixed values. Pop removes the last frame from the tip
into a reverse buffer and restores parent streams without traversing older
frames. Recovering the parent dimension as twice the returned child size
matches the actual frame-body length. The root narrows exact completed
integers to the inherited return carrier, with no P-grid truncation inside.

A manual source-activation audit checked the fixed temporary pool: eight
persistent kernel Counts, bounded helper state, and at most eight fresh
roles inside the largest retained primitive fit a conservative 64-role
reserve within the declared 256. This bound reads the Count/Counter,
encoded arithmetic and signed-record source; it is not extrapolated from
the measured peak. Child scalar allocations use a separate suspended scope.

The kernel's `PROOF.md` was checked for exact carriers, frame correctness,
the complete movement/control recurrence and retained historical backing.
Its explicit conservative tariff
`O(B^log2(7)[M(U)+V L^3])`, with
`L=1+log2(B)+ceil(log2(w+2))`, is valid without assuming w comparable to
log B. A simpler log-B-only overhead must be derived separately or use
an explicitly compatible caller regime; B<=4p alone is not sufficient.
Finite timings/product counts do not prove the asymptotic invoice.

The finite matrices use the retained word owner's base branch. Its
larger-word correctness and cost remain inherited from the pinned scalar
service, rather than newly established by these tests. Canonical Count
metadata, ordinary uncorrupted private state and the stated external
stream admissions are retained assumptions of the physical interface.

The separately read `FastBoundaryPages` adapter suspends its parent scope
around the matrix child, copies the complete exact wide return and consumes
it in a finally block. Every P-grid rounding stays in inherited
`pass_blocks`. Its dyadic-only entry is explicit; the unchanged classical
BoundaryPages entry remains available for arbitrary positive B. This is
static adapter review, not a claim of an independent whole Gaussian or
original-S replay. The caller's own exact-factor/block oracle and measured
baseline are documented separately in `BOUNDARY.md`.
