# Proof: the two fourteen-port subsystems have different sharp dimensions

All port numbers denote zero-based positions in the authenticated P104 source
array identified in [README.md](README.md). The zero relation is

\[
Z(v,w)\iff v\ne w\quad\text{and}\quad
\operatorname{popcount}(p_v\mathbin{\&}p_w)\equiv0\pmod2.
\]

Throughout, `k` is a positive integer, `F` is an arbitrary field, and
`U_v,W_v` are `k × d` matrices over `F` satisfying the stated zero relation
and invertible diagonal pairings. A smaller subsystem imposes only the
constraints among its retained ports.

## 1. Rank axioms from asymmetric labels

Put `V_v=im(U_v^T)` and

\[
f(A)=\dim_F\!\left(\sum_{v\in A}V_v\right).
\]

The diagonal invertibility gives `dim(V_v)=k`: if `U_v^T x=0`, then
`W_v U_v^T x=0`, whence `x=0`. Also `f(empty)=0`, `f(A)<=d`, and `f` is
monotone. The dimension formula, together with
`span(V_{A intersection B})` contained in
`span(V_A) intersection span(V_B)`, gives submodularity:

\[
f(A)+f(B)\ge f(A\cup B)+f(A\cap B).
\]

If `v` is forced zero to every member of `A`, then `W_v` annihilates
`span(V_A)` and is injective on `V_v`. Their intersection is therefore zero,
so

\[
f(A\cup\{v\})-f(A)=k. \tag{Z}
\]

This uses no symmetry assumption. Every subsequent inequality concerns
integer dimensions, so the rational certificate coefficients do not require
division by two in the field.

## 2. Original subsystem: lower bound `ceil(17k/2)`

Define

\[
I=\{74,81,86,91\},\qquad
S=\{62,63,69,99,67,68,95,100,101\}.
\]

The original fourteen-port set in #6846 is `R0=I union S union {57}`.
Every member of `I` is forced zero to every member of `S` and to the other
members of `I`. Thus repeated application of (Z) gives
`f(I union S)=4k+f(S)`. Thirteen ports already suffice for the lower bound.

To prove `2f(S)>=9k`, set

~~~text
A = {62,69,99,68,100}
B = {62,99,67,95,100}
C = A union B
E = {69,67,100}
F = {62,100}
Q = {69,99,67,68,100}
T = {62,69,67}
~~~

The following finite premises are checked directly against the pinned ports:
`63` is forced zero to `A`; `101` to `B`; `99` to `F`; `95` to `Q`;
`68` to `E`; and the three members of `T` are pairwise forced zero.
The relevant set identities are

\[
A\cap B=F\cup\{99\},\quad E\cap F=\{100\},\quad
Q\cup\{95\}\subseteq C,\quad E\cup\{68\}\subseteq Q,
\quad T\subseteq E\cup F.
\]

Consequently,

\[
\begin{aligned}
2f(S)
&\ge f(A)+f(B)+2k &&\text{by (Z) and monotonicity}\\
&\ge f(C)+f(F)+3k &&\text{by submodularity and (Z) for 99}\\
&\ge f(Q)+f(F)+4k &&\text{by (Z) for 95 and monotonicity}\\
&\ge f(E)+f(F)+5k &&\text{by (Z) for 68 and monotonicity}\\
&\ge f(E\cup F)+f(\{100\})+5k &&\text{by submodularity}\\
&\ge 3k+k+5k=9k. &&\text{since T is pairwise forced zero}
\end{aligned}
\]

Therefore

\[
d\ge f(I\cup S)=4k+f(S)\ge\frac{17k}{2}.
\]

Since `d` is an integer, `d>=ceil(17k/2)`. The verifier independently expands
the displayed argument into 17 elementary axiom rows whose exact sum is
`2f(S)-9k>=0`, including every monotone inclusion and the empty-set identity.

## 3. Original subsystem: matching upper bound for every field and block size

A coordinate group assigns one ambient standard basis coordinate to every
port listed in that group. Let the rows of `U_v=W_v` be the distinct standard
coordinates assigned to port `v`. If every port receives `k` coordinates and
every forced-zero pair receives disjoint coordinate sets, the diagonal
pairing is `I_k` and all required off-diagonal products vanish over every
field. The ordering of the rows within a port can be fixed by increasing
coordinate index.

For `k=2,d=17`, use two coordinates for each group in the first row and one
for each group in the second:

| Multiplicity | Coordinate groups |
|---|---|
| 2 | `{74}`, `{81}`, `{86}`, `{91,57}`, `{99,67}`, `{69,100}` |
| 1 | `{62,68}`, `{62,95}`, `{63,95}`, `{63,101}`, `{68,101}` |

There are `12+5=17` coordinates. Every original port receives two distinct
coordinates. Every two-port group is an allowed pair, as checked against the
source. This proves the `k=2,d=17` upper bound without arithmetic cancellation
or characteristic restrictions.

For `k=1,d=9`, use one coordinate for each group

~~~text
{74}, {81}, {86}, {91,57}, {99,67}, {69,100}, {62,68}, {63,95}, {101}.
~~~

For `k=2q+r`, `r in {0,1}`, take the direct sum of `q` copies of the first
construction and `r` copies of the second. Its inner dimension is

\[
17q+9r=\left\lceil\frac{17k}{2}\right\rceil.
\]

Together with Section 2 this proves exactness for the original fourteen
ports. Restricting the same constructions proves exactness for the
thirteen-port lower-bound subset `I union S` as well. The nine-core `S`
itself has exact minimum `ceil(9k/2)`, by deleting the four isolated coordinate
blocks (each of dimension `k`) from the construction.

## 4. Replacing port 57 by 61: the Petersen core

Let

\[
P=S\cup\{61\}=\{61,62,63,67,68,69,95,99,100,101\}.
\]

All four members of `I` are forced zero to every member of `P`; in fact `P`
is their complete common forced-zero neighborhood among all 104 ports.
The graph of allowed distinct pairs on `P` is the Petersen graph. An explicit
isomorphism to its outer-pentagon / inner-pentagram presentation is

~~~text
outer = [61,69,100,62,95]
inner = [99,101,67,68,63].
~~~

Its edges are exactly `outer[i]--outer[i+1]`, `outer[i]--inner[i]`, and
`inner[i]--inner[i+2]`, with indices modulo five. The verifier compares the
complete unordered edge sets; degree counts alone are not used to identify
the graph. The following rank argument is checked directly against the
source relation and does not rely on recognizing the graph name.

### Exact all-field certificate for `f(P)>=5k`

The file [petersen-dual.json](petersen-dual.json) contains 43 rows. The ordered
vertex list is `P` in the ascending order displayed above. For a subset mask
`s`, its set is `{P[i] : the i-th bit of s is 1}`. The row meanings are:

| Descriptor | Left side | Right side | Type |
|---|---|---|---|
| `["mono",s,i]` | `f(s)-f(s+i)` | `0` | `<=` |
| `["submod",s,i,j]` | `f(s)+f(s+i+j)-f(s+i)-f(s+j)` | `0` | `<=` |
| `["zero",s,i]` | `f(s+i)-f(s)` | `k` | `=` |
| `["empty"]` | `f(empty)` | `0` | `=` |

Here `s+i` denotes adjoining `P[i]`, not integer addition; each named vertex
is required to lie outside `s`. Every `zero` row has all its required
forced-zero contacts checked. All 26 inequality multipliers are `-1/2`, so
each multiplied inequality has the correct `>=` orientation. The 16
zero-additivity rows have signed half-integer multipliers; equalities allow
either sign. The remaining row is the empty-set equality.

Adding the rows gives **exactly**

\[
f(P)\ge5k.
\]

More explicitly, the coefficient of `f(P)` is `1`; the coefficients of all
other subset-rank variables are zero; and the weighted sum of the
zero-additivity right sides is `5k`. Multiplying the entire certificate by
two yields integer coefficients. `verify.py` reconstructs the rows as
frozensets of actual port IDs and checks this identity with rational
arithmetic. The separately written `audit_petersen.py` reconstructs the rows
using bitmask variables and a different coefficient accumulator. Neither
uses numerical tolerances or trusts the reported LP objective.

This finite exact axiom combination is a proof for every field and every
positive integer `k`, because Section 1 proves each axiom for every such
label system. A numerical linear program was used only to discover it.

It follows that the replacement subsystem
`R1=I union P=(R0 minus {57}) union {61}` satisfies

\[
d\ge f(I\cup P)=4k+f(P)\ge9k.
\]

The replacement subsystem attains `9k` over every field. Assign one block of
`k` standard coordinates to each singleton in `I` and to each matching edge

~~~text
{61,69}, {62,95}, {63,101}, {67,100}, {68,99}.
~~~

These are five allowed disjoint edges covering all ten core ports. Every
port receives exactly one coordinate block, with `U_v=W_v` its standard
basis rows. This proves exactness of `9k` on `R1`, and of `5k` on `P`.

## 5. Consequence for the full mask and its limits

Any realization of all 104 ports restricts to `R1`, hence has `d>=9k` over
every field. In every characteristic-two field, interpreting each original
nine-bit port as a vector gives a scalar realization: odd weight makes the
diagonal one, and even overlap makes each forced-zero product zero. Tensoring
with `I_k` attains `9k`. Thus the full-mask minimum is exactly `9k` in
characteristic two.

Over other characteristics, a binary dot product that is zero modulo two
need not be zero in the field. The argument therefore supplies only the
full-mask lower bound there. It supplies no necessity theorem for the label
pattern in a legal multiplication circuit and no reduction in complete
supplier cost. **No new κ.**

The general Petersen lower bound and four-isolate construction precede this
work: see Thiago's #1744 and its credit to Blasiak, Kleinberg and Lubetzky.
The source-specific advance is the explicit P104 transfer, the sharp
original-subsystem contrast, and the exact closure of the open block
interval in DreamingOfClouds' #6846.

## 6. Exact nonlinear binary broadcast corollary

Use the same allowed-pair graph as a side-information graph. Each vertex `v`
has an independent uniform `k`-bit message `X_v`; receiver `v` knows the
messages at its allowed neighbors and must recover `X_v` without error.
Let `B` be any deterministic fixed-length binary broadcast, permitting
arbitrary nonlinear encoding and decoding. Write `V` for the vertex set and
define, with entropy measured in bits,

\[
r(S)=H(B\mid X_{V\setminus S}).
\]

This function satisfies exactly the axioms used in both preceding proofs.
Deterministic encoding gives `r(empty)=0`. Removing conditioning variables
proves monotonicity. Moreover

\[
r(S)=H(B,X_{V\setminus S})-k|V\setminus S|.
\]

Entropy submodularity, complementation of the index sets, and subtraction of
the displayed modular function prove submodularity of `r`. If `v` is forced
zero to every member of `S`, all neighbors of `v` belong to
`Z=V\setminus(S\cup\{v\})`. Independence and zero-error decoding give

\[
\begin{aligned}
r(S\cup\{v\})-r(S)
 &=I(B;X_v\mid X_Z)\\
 &=H(X_v\mid X_Z)-H(X_v\mid B,X_Z)=k.
\end{aligned}
\]

Thus the same 17-row short proof and 43-row certificate, already checked
exactly, are also entropy inequalities. In the full 104-port problem the
certificates bound `r(I union P)`, which is at most `r(V)=H(B)` by
monotonicity. Since an `L`-bit fixed-length broadcast has `H(B)<=L`, they imply

| Side-information graph | Minimum fixed binary broadcast length |
|---|---|
| Original fourteen ports `R0` | `ceil(17k/2)` |
| Replacement fourteen ports `R1` | `9k` |
| Complete 104-port graph | `9k` |

Here the lower bounds apply to nonlinear encoders. The upper bounds are
explicit linear codes. For each coordinate in a subsystem witness, transmit
the XOR of the message bits assigned to that coordinate. Every other port
sharing the coordinate is an allowed neighbor, so a receiver subtracts the
known bits and recovers its own bit. The verified coordinate assignments give
the stated lengths for every `k`, using direct sums for the original odd-width
case.

For the full graph, broadcast the nine `k`-bit blocks
`B_a = XOR_{v: ports[v]_a=1} X_v`. Receiver `v` XORs those blocks selected by
its port vector. Its own coefficient is one; every other nonzero coefficient
is on an allowed neighbor, so it can subtract those known messages. The
existing full binary Gram check verifies all these coefficients.

This is a source-specific index-coding corollary of the same certificate,
following the established entropy/Petersen method in #1744. The general
nonlinear Petersen result is credited there to Blasiak, Kleinberg and Lubetzky.
No new universal entropy inequality is claimed. This fixed-length zero-error
broadcast model is an explicit assumption and is not a physical reversible
supplier or a paid multiplication algorithm.
