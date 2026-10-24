# Actual stage access for the matched involution

The new matched response has a scalar implementation at the final FULL
cut. Its two-stage raw terminal factor still has non-monomial payload
blocks. These are separate results. The first permits late scalar
decoding. It does not remove the two intrinsic line factors in the
second.

This packet uses the new 48-port mode matching, not the preceding signed
physical-partner exchange. The 48-port source is the frozen matrix in
`controller-followthrough-20261017/matched-involution-20261018/`.
It checks both the half-Hadamard64 complement from that source and the
new permutation64 complement from `history-encoding/`.

## The routed response and the raw terminal factor

Let E be either specified symmetric involution. Every physical diagonal
entry is zero. The half-Hadamard64 version has four nonzero entries in
each row. The permutation64 version has four in each of the 48 matching
rows and one in each of the other 64 rows.

Use the literal DATA stage route rho_(s,p). On the regular orthogonal
cover, the stage response has entries

```text
(E_s x)_p(h) = sum_r E_pr x_r(h rho_(s,p) rho_(s,r)).
```

This formula defines the logical response. Its physical implementation
must include the DATA translations and the field frames. In particular,
the input code Q must not be discarded when a terminal is designed.

For the isolated balanced pair with data code C=E_t E_s, the physical
input bank is Qx. The completed fields have the form

```text
X = F (E_s x-y),       Y = F q C x.
```

The desired raw outputs are FQx and Fy. After F is removed from the
notation, their exact decoder is

```text
[ 0   Q C^-1 Q      ]
[ -I  E_s C^-1 Q    ].
```

Thus its upper block is Q E_s E_t Q. This equation is an isolated-pair
identity. A complete three-call or multi-pair controller must establish
its own endpoint before it uses this decoder. In particular, a single
Y normalization followed by scalar inverses returns logical x. It does
not by itself return the original physical input Qx.

## Exact non-monomial path blocks

Fix distinct positive stages s and t. A path through intermediate port j
in Q E_s E_t Q has coefficient E_pj E_jr and cover word

```text
A_j = rho_(s,p) rho_(s,j) rho_(t,j) rho_(t,r).
```

Its payload operator, before the final common F conjugation, is

```text
C_(q_p) C_(A_j q_r) P_(A_j).
```

All these paths are distinct for fixed p and r. To prove this, cancel
the fixed outside routes. The remaining map is
rho_(s,j) rho_(t,j). Its action on the l-th axis of the s block is the
l-th root complement vector of port j. Equality of all eight such
vectors would give the same root complement and the same intrinsic q.
The actual 112 q values are distinct. Therefore two intermediate ports
cannot give the same cover word. Arbitrary cover inputs can isolate
each path, so coefficients from different paths cannot cancel.

Every nonzero E_jr has j different from r. The first new-stage route
rho_(t,j) sends a nonzero part of q_r into the t block. The two later
s-stage routes preserve that part. Hence A_j q_r has a nonzero t-block
component, while q_p lies in the root nine coordinates. The two line
directions are distinct.

For each orthogonal cover map A, F P_A F^-1 is P_A with a translation.
The checker derives this translation from the full Z4 phase polynomial.
It verifies the constant, odd, even, and quadratic coefficients. Thus
the final physical path has the form

```text
translation(delta_A) C_(q_p) C_(A_j q_r) P_A.
```

The two-line product has four nonzero entries in each one-copy row.
Their phase numerators, in translation order 0,a,b,a+b, are i,1,1,-i,
with common denominator two. At tensor width f, the exact support is
4^f. A translation or invertible address map preserves this count.

The checker covers the actual consecutive pairs (1,2), (3,4), (5,6),
and (7,8). For each pair it checks all 1,792 paths of the half-Hadamard64
version and all 832 paths of the permutation64 version. Every path has
two-line Fourier rank two. This path count is not a lower bound on the
number of native children in a coupled implementation.

A concrete path lies entirely in the first 25 coordinates:

```text
s=1, t=2, p=0, j=15, r=0,
coefficient = 1/4,
line directions = 11 and 2^24,
FULL translation = 17695243.
```

It is a path in the new 48-port matching, so both choices of the 64-port
complement retain it.

A fixed number of scalar and monomial array passes has a row support
bound independent of f. The displayed 4^f support therefore excludes
such a zero-child implementation of this specified terminal factor.
The statement permits a paid native decoder, a new controller, changed
owner routes, or changed local output frames. It is not a circuit lower
bound for arbitrary algorithms.

## A literal scalar E gauge at the final FULL cut

The matching48 plus permutation64 version has an emitted scalar word.
For each physical pair, apply its exact signed two-field mode code.
Apply the specified signed mode transpositions. Reverse the pair code.
On the other 64 fields, apply the 32 specified negative exchanges.
The full word acts as E on arbitrary values in all 112 fields.

For each stage s, take the literal past-X view M_(s,p) from
`BRIDGE-PROGRAMS.json.gz`. Its route and translation satisfy

```text
M_(s,p) F = F P_(rho_(s,p)).
```

Apply all 112 views, execute the scalar word at each common body address,
then undo all views. The result is exactly F E_s F^-1. This uses 224
monomial view calls. It also applies to a Y bank after that bank has
been converted to the same physical FULL frame. It does not convert a
hole frame to FULL for free.

The emitted word has 264 complex ADDs and 230 complex SCALEs. Its exact
inherited scalar invoice is 2,668 real primitives. The checker also runs
the pinned source price function on the emitted word. The largest
intermediate row one-norm is four. There is no native child, owned field,
private buffer, or assumed zero data. The forward word and its reverse
inverse both pass all 112 independent input columns. Monomial map costs
are separate from this scalar invoice.

## Restriction to one pair and 25 coordinates

The root nine coordinates and the first two fresh eight-coordinate
blocks form a 25-dimensional space. Every literal route at stages 0,
1, and 2 preserves this space and fixes the other 48 coordinates.
Every corresponding DATA entry and exit translation lies in it.

The separate dimension checker verifies all 336 orthogonal route
records, all 672 entry phase equations, and all 672 exit phase equations.
The current local types remain X:C_q to F9 and Y:I to F9 C_q^-1, with
the common exterior Fourier factors included. No additional phase or
endpoint adapter is inferred.

These routes belong to O(25,2). Right multiplication therefore permutes
the regular O(25,2) cover. With a data-only local word, the owner views
partition each data field into its body invocations. Complete each local
cover sweep before the next stage. No helper-owner sharing is needed
for this chart statement. The local native word and recursive hosting
are separate obligations.

The same restriction gives the exact scalar-access cones:

- At the initial all-I cut, every routed scalar port matrix is available
  through monomial views.
- On X at completed level l, every stage s at most l is available through
  the literal past-X views.
- On Y at hole level l, every stage t greater than l is available through
  the literal future-Y views.

These statements do not depend on a dedicated centre bank. They apply
to the new sparse E matrix itself. At the B1 Y cut, the global hole level
is zero. E2 is available by the future-Y view. E0 is an old-chart operator;
its off-diagonal blocks have the mixed intrinsic lines and are not made
free by the local label I.

## Validation and scope

Run both checkers from this directory:

```text
python3 -I -B check_matched_access.py
PASS_MATCHED_RESPONSE_STAGE_ACCESS
python3 -I -B check_dimension25.py
PASS_LITERAL_DIMENSION25_STAGE_RESTRICTION
```

Repeat with `-O`. The generated payloads and receipts must be identical.
All checks use exact arithmetic and the pinned source maps. This packet
does not emit the new local forward or backward native word, prove a
complete three-call endpoint, admit recursive children, or establish a
kappa improvement.

The work uses the controller lane's matched mode specification, the
history lane's permutation64 native response, and the earlier exact
DATA phase and access calculations. OpenAI Codex assisted the work.
No PR, commit, or push was made. Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
