# Rigidity of the two existing feedback edges

This scoped proof and its new verifier were produced by Nick Petalas.
Apache-2.0. The saved-bank interface and its known attaining pair are credited
to unpaidmoon, PR #6961, building on Cinna Davis's PR #5220 active schedule.

## The inherited interface

Rightmost operators act first. Write Q for the central Gaussian, C for C1,
D for D1 and b for the unchanged third-input coefficient
Q^-1 C3 D1 D3. Let F and G be the two feedback operators, respectively.
The predecessor's saved first-FULL Y row and the pre-query-2 coded X row are

```text
L = [Q^-1 C D, D, -Q^-1 C D, 0],
K = [0, -Q D, C D, 0].
```

Here K is C times the pair-0 X row at that cut. Query 2 returns
S = Q^-1 (K + F L). The cancellation identity in #6961 gives the row after
query 4 as

```text
R(F,G) = B + Q^-1 G Q^-1 (K + F L),
B      = [0, 0, b, 0].                            (1)
```

These are inherited schedule premises, not a new native replay. For reference,
the zero x0 column of K is the cancellation of the first thin against FULL1;
the bridge adds D x1 to that X bank. The full schedule, phase conventions,
owned captures and helper contracts remain those of the cited predecessors.
This contribution begins with (1) and classifies both F and G simultaneously.

## Theorem

Let A be any associative unital ring. Let Q,D be units in A, let C^2=1,
and assume QD=DQ. Take any b in A and define (1). The operators F,G may
be arbitrary elements of A; their invertibility is not assumed. Then

```text
R(F,G) = [D Q^-1, 0, b, 0]
    if and only if
F = Q and G = C Q.                                (2)
```

It already suffices to impose the following two constraints on the row:

```text
R_1 = 0,
R_0 + R_2 = D Q^-1 + b.                           (3)
```

Subscripts 0,1,2,3 correspond to the four original input banks x0,y0,x1,y1.
This is a statement about independent coefficients, so it retains arbitrary
values in all four banks.

### Proof

The saved row satisfies L_0+L_2=0, whereas K_0+K_2=C D. Hence (1) gives

```text
R_0+R_2-b = Q^-1 G Q^-1 C D.                      (4)
```

The sum has eliminated F without any assumption about F. If (3) holds,
equation (4), followed by right multiplication by D^-1, gives

```text
Q^-1 G Q^-1 C = D Q^-1 D^-1 = Q^-1.
```

Multiply on the left by Q and on the right by C Q. Since C^2=1,
this forces G=C Q. In particular, G is forced to be a unit even though
the theorem did not assume it.

Substituting this value into the second-input column of (1) gives

```text
R_1 = Q^-1 C (F-Q) D.
```

Both outside factors are units. Therefore R_1=0 forces F=Q.
This proves necessity using only (3). Conversely, with F=Q and G=C Q,

```text
K+Q L = [C D, 0, 0, 0],
R(Q,C Q) = B + Q^-1 C [C D, 0, 0, 0]
         = [Q^-1 D, 0, b, 0]
         = [D Q^-1, 0, b, 0].
```

This also proves sufficiency and the equivalence of (2) and (3). No field
division, determinant, degree argument, word enumeration, faithful group
representation, Q^4 relation or C/D commutation was used. In particular,
the classification survives any quotient in which the interface equations
and the stated unit relations hold. This is the same rigidity theorem,
not a physical-cost claim. ∎

## What the classification changes

PR #6961 supplied the pair (Q,C Q), both one-edge obstructions, and explicitly
excluded classification of every pair from its claim. The new step is the
elimination (4), which forces that pair even when both operators vary over
the entire algebra. A larger polynomial or word search on these same two
edges cannot yield another way to meet this row contract. A further relation
among physical operators cannot create a second pair of operator values while
preserving (1) and its unit hypotheses; it can identify different expressions
for the same pair.

The existing attaining pair is not new. Its ordinary bill and unchanged scalar
suffix are studied separately in unpaidmoon's open PR #7077. The new proof
does not replay or recertify that bill or the complete final banks. It does
not exclude a new saved source, a changed insertion point, a new decoder,
an altered row target, or a changed source schedule.

## Executable evidence and its boundary

The verifier independently represents (1) by exact 2-by-2 matrices over
Z/2, Z/3 and Z/4, including noncommuting Q,C and nonunit candidate F,G.
It enumerates every F,G for each declared fixture and checks the complete
accepted set, plus the aggregate predicate (3). A separate scalar evaluator
applies the two feedback operations to every eight-scalar input for its
three designated fixtures. This finite corroboration is distinct from the
all-ring proof above. These reduced-interface fixtures are not native
realizations of the inherited full schedule.

Controls reject a reversed noncommutative product, show why either an x0-only
check or a zero-y0-only check is insufficient, and reject singular Q/D,
noninvolutory C, noncommuting Q/D and malformed fixture values. The verifier
imports no predecessor scientific program and runs no predecessor census.

All loops have fixed domains: modulus at most four, four matrix entries,
two scalar coordinates, at most 75 fixtures, at most 65,536 operator pairs
per fixture and at most 65,536 scalar inputs per designated fixture.
There is no recursion or dynamic code evaluation. Checks use explicit failures
and remain enabled under optimization. The script owns no subprocesses or
network resources; its optional new receipt uses an exclusive context-managed
file and binds all six authored package files by SHA256.

Power-of-Ten rule 3 deviation: CPython's integers, tuples, dictionaries and
iteration machinery allocate during verification. Fixed allocation is not
available in this interpreter. The fixed domains above bound live data; a
census retains at most its 65,536 matrix pairs if every pair were accepted,
and all 75 small result records. Normal and optimized warning-strict replays
check the actual path. A fixed-allocation port would need a separate native
implementation. No low-level fixed-allocation compliance is claimed.
Functions stay below 60 physical lines. There are no callback dispatch tables,
hidden imports, mutable shared state or suppressed diagnostics. The repository's
registered-package checks provide the applicable recurring validation; a new
whole-repository lint configuration is outside this isolated result.
