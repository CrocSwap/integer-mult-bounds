# Fixed-prime descriptors for complete dyadic cover matchers

Status: scoped all-size construction with exact finite corroboration;
independent mathematical review is still required. This is a source-specific
constructive supplement to the recovered dyadic compiler closure. Gaussian
elimination and the retained streaming primitives are credited inputs, not
new algorithms claimed here.

## 1. The precise statement and source alphabet

Let N>=1 and let S be one complete fixed matcher in
`GL_N(Z[1/2])`, with its full image and kernel already carried by the dyadic
compiler construction. Fix an odd **prime** q. There is an effective finite
list of rational elementary operations which implements right multiplication
by S over `Z/q^w` for **every** w>=1. The list can depend on q and S, and
does not depend on w. Its inverse is the same stored list in reversed order,
with each operation inverted.

For the cover chart `g=g0+qX`, the list and its finite low-type/carry data
implement the exact source route

```
rho_S(g0,X) = (h0, X S + C_S(g0) mod q^(w-1)),
h0 = g0 S mod q in fixed representatives,
C_S(g0) = (g0 S-h0)/q.
```

One directed application, on the complete cover field, uses at most

```
2N^3 previous-stage ordinary interchanges,
N^3 ordered shifts, including every carry translation,
N^2 fixed rational-unit scaling records,
```

plus the source's finite low-type selection, unselection, setup and scans.
These are exactly the categories and conservative counts in #7840 Section
4. Inverse routes and applications to separately owned payload fields are
charged separately.

The coefficient qualification matters. The actual alphabet is stated in
`upstream/build/sections/02-streams.tex`,
`lem:ordered-affine-streams`, retained as `SOURCE-STREAMS.tex`:

* Every rational coefficient has a denominator prime to q.
* A coefficient used for **unit scaling or division** also has numerator
  prime to q.
* An additive shear coefficient can have numerator divisible by q. Its
  inverse changes the sign of that coefficient and needs no division by it.

Thus this theorem supplies q-integral coefficients and q-unit pivots and
scalings. It does not impose an unsupported requirement that every nonzero
addition coefficient be a unit. For example, `I+qE_12` is a valid source
shear and is nontrivial modulo q^2. Nor does this source impose a bounded
integer alphabet such as the unrelated plus/minus-20 restriction.

The source pins are canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`, Ali Romman's #7828 head
`03b572b3b9ab72c6ba67762e85e1630cda1daad5`, and the selected #7840 head
`adf2e0aa6777977a280ce50f8938f4a0f4f19b76`. `ORIGINS.json` binds the exact
proofs, primitive statement, cover construction and finite basis inputs.

## 2. Construct one descriptor after q is fixed

Work in the local subring

```
R_(q) = {a/b in Q : gcd(b,q)=1}.
```

The dyadic matrix S and its inverse lie in this ring. Eliminate `A=S^t`
over the rationals. At column k, among rows k through N-1 choose the first
entry whose numerator is prime to q. Exchange it with row k, scale row k
by the reciprocal of that pivot, and clear column k in every other row.
Skip identity scalings, zero additions and trivial swaps. The implementation
records the exact rational coefficients, without reducing them modulo a
particular power of q.

Here is why a pivot always exists. After the previous columns have been
cleared, the remaining Schur block is invertible over R_(q): its determinant
differs from the original unit determinant by products of earlier unit
pivots and signs. Reducing modulo q gives an invertible matrix over a field.
Its first remaining column cannot be zero. Every selected pivot is
therefore a unit in R_(q), and all subsequent entries still belong to this
ring. The process ends at the identity.

Write the recorded elimination operations in execution order as
`E_1,...,E_m`. They satisfy

```
E_m ... E_1 S^t = I.
```

The forward data word is consequently

```
E_m^-1, E_(m-1)^-1, ..., E_1^-1
```

in execution order. Its total operator is `S^t`, so on a row x it gives
`x -> xS`. The inverse data word is `E_1,...,E_m`. This transpose and order
convention is part of the descriptor format and is independently checked.

At most N row swaps, N unit scalings and N(N-1) additions are recorded.
Thus each high-row word has at most `N^2+N` records. All divisions were by
units selected modulo q. Applying the homomorphism
`R_(q) -> Z/q^w` to the exact identity proves correctness at every width,
including q-powers where a shear coefficient that vanished modulo q becomes
nonzero. No second pivot selection or extra prime exclusion is required.

The prime hypothesis is substantive. Over modulus 15 the determinant-one
matrix `[[3,5],[1,2]]` has, after transposition, a first pivot column with
entries 3 and 5, neither a unit. A general composite-modulus construction
would need additional work. The retained source chooses a prime, so this
case is outside the theorem.

## 3. Exact coefficient and descriptor sizes

Let `D=2^s` clear the input denominators, write `S=A/D` with A integral,
and put

```
M = max(1, max_ij |A_ij|),
h = bit_length(M), u = bit_length(N),
K = s+N(h+u)+1.
```

Every numerator and positive denominator appearing in either stored word
has magnitude less than `2^K`. This is an input-sensitive bit bound. It is
independent of q and w, although the selected coefficients can depend on q.

To prove it, set `Delta=N! M^N`. Every square minor of A has magnitude at
most Delta by the determinant expansion. At an elimination checkpoint with
k selected pivot rows, normalized pivot-row entries are ratios of k-minors
of A, by Cramer's rule. A remaining Schur entry is

```
(one (k+1)-minor of A)/(D times one nonzero k-minor of A).
```

Row pivoting only changes which row subset occurs in these minors. The
next reciprocal pivot has the reverse ratio, with D in its numerator.
During a column-clearing pass a row is either at the old checkpoint or has
already acquired its new checkpoint expression. The normalized new pivot
row itself is a ratio of two (k+1)-minors. Hence each recorded addition or
scaling, and the reciprocal of every recorded scaling, has numerator and
denominator at most `D Delta` before reduction to lowest terms.

Since `N<2^u` and `M<2^h`,
`D Delta <= D N^N M^N <2^(s+N(h+u))<2^K`. This proves the bound. The
selected pivot minors are nonzero modulo q; therefore these bit bounds do
not hide a nonunit denominator.

An operation record needs an opcode, at most two indices of u bits, and one
signed rational of at most K bits per numerator and denominator. A forward
word has at most `N^2+N` records. Its explicit inverse doubles that storage
bound. Thus the linear descriptor has

```
O(N^2(K+log(2N))) bits.
```

The source #7828 logical-record theorem does not itself bound the bit height
of every generated matrix solely in N. This result uses the actual input
height of the completed matcher. It gives an effective bound for each member
of the fixed finite catalogue; it does not claim that materializing the
astronomical selected catalogue is efficient or that its entries cost one
tape step.

## 4. The finite low type, exact carry and all high fields

Use representatives `0,...,q-1` for each entry of g0 and h0. The defining
congruence gives

```
C_S(g0) = [(g0 A-D h0)/q]/D.
```

The bracket is an integer matrix, because D is a unit modulo q. In
particular, the carry is still dyadic: division by q here cancels in the
integer numerator. Its positive denominator divides D. Each bracketed
integer has absolute value strictly less than `NM+D`, since

```
|g0 A-D h0| <= (q-1)(NM+D).
```

The carry's rational bit size is therefore bounded independently of w and,
for these representatives, independently of q. The low labels themselves
need `N^2 ceil(log2 q)` bits each.

There are `|GL_N(F_q)|<=q^(N^2)` low types. A fully materialized low table,
storing each source label, target label and rational carry, has an explicit
finite bound

```
O(q^(N^2) N^2 [log(2q)+s+log(1+NM+D)]) bits.
```

Such a table is allowed only as fixed-template preprocessing with its
source selection and scanning costs retained. The executable finite checker
does not materialize this table for the 8- or 15-coordinate fixtures. It
computes particular low charts exactly. A formula-based evaluation from g0
is also possible by ordinary rational/modular arithmetic; it is not a free
random-access lookup.

For w>=2, perform the stored elementary word on each of the N rows of the
high matrix X, then add each of the N^2 entries of `C_S(g0)`. Every high
field is included. The result satisfies

```
h0+q(XS+C_S(g0)) = (g0+qX)S mod q^w.
```

To invert, recover g0 from h0 using the finite inverse low permutation,
subtract that same carry, and execute the inverse elementary word. This
is literal inverse chronology. Equivalently, the canonical inverse chart
uses

```
C_(S^-1)(h0) = -C_S(g0) S^-1.
```

For two fixed matchers S,T, the carry identity is

```
C_(ST)(g0)=C_S(g0)T+C_T(h0), h0=g0S mod q.
```

Thus `rho_T` after `rho_S` equals `rho_(ST)`, with the displayed order.
At w=1 the high cube is a singleton. Only the finite low permutation is
performed; no zero-width interchange or shift is invoked.

## 5. Source tariff and elementary lowering

Order the N high fields in one row by their coordinate index. An addition
to a later field from an earlier field is directly an ordered affine
update. For an earlier target, exchange the two complete fields, perform
the resulting later-target update, and exchange them back. These are two
charged ordinary interchanges. A pivot row exchange costs one such
interchange. All intervening gaps and complete suffix records are preserved
by the retained primitives.

Let a,s,d be the addition, swap and scaling counts for one high row. Even
charging every addition as upper gives

```
a<=N(N-1), s<=N, d<=N,
N(2a+s)<=2N^3-N^2<=2N^3,
Na+N^2<=N^3,
Nd<=N^2.
```

The second line pays all N^2 carry translations, even if some happen to be
zero. Counting only actual upper additions gives a smaller explicit bill in
each emitted descriptor, but the theorem retains the source bound. The
same bound applies to the inverse word: reversing chronology does not
change the addition target/source indices, swaps remain swaps and unit
scalings are inverted.

Here one fixed rational-unit scaling record has the source meaning. For
`a/b`, it expands to multiplication by the positive integer `|a|`, inverse
multiplication by b, and possibly a sign operation. Thus fully expanding
these scaling records yields at most `2N^2` positive-integer scaling/inverse
subroutines and `N^2` sign subroutines. Their bucket streams and scans remain
inside the retained fixed-scaling tariff. They are not ordinary-interchange
calls, and a rational scaling is not asserted to take one bit operation.

The positive-integer bucket construction can use up to `|a|` or b streams.
These numbers can be exponential in K. They are fixed after the matcher
and q have been fixed, independent of w; their cost belongs to the fixed
constant. The result does not assert a uniform polynomial-time physical
service in N or K.

For the variable-width residue preparation, a rational coefficient of
height K can be reduced modulo `q^(w-1)` with ordinary long arithmetic and
extended Euclid. With
`L=K+w ceil(log2 q)+O(log(2N))`, the elementary school-arithmetic bound is
`O(L^3)` bit operations per coefficient and polynomial workspace. The fixed
number of coefficients and control fields then gives a polynomial in w
after the template is fixed. The ordered-affine lemma charges this
preparation per prefix and absorbs it in the complete target fibre of
`q^(w-1)` records, with the effective fixed constant or eventual cutoff
enlarged as needed. Small widths retain the source elementary treatment.
No unit-cost multiplication, inverse or descriptor evaluation is assumed.

Consequently the source's `O_fixed(V w^(1-a_old))` directed-route tariff
continues to apply under its completed previous-stage ordinary service,
ordered-affine, complete-fibre, row ownership and tape interfaces. This
package supplies explicit admissible descriptors and their fixed bounds;
it does not reprove or replace those physical services.

## 6. Coupled roles and source chronology

The selected native off-diagonal X/Y contacts require a common route. The
descriptor records one route identifier, referenced by both coupled roles.
Both fields enter that route, complete the child/scalar job at the common
row, and return through its inverse before a dependent caller instruction.
Using the same control descriptor does not merge two separately owned
payload fields into one charged physical application.

For a scalar contact from role i to role j, routing the two roles by S_i
and S_j would otherwise make the returned target at parent row g read the
source at

```
g S_j S_i^-1.
```

When `S_i=S_j`, this is exactly g. The independent negative control takes
unequal determinant-one routes over `GL_2(F_3)` and changes the source row
at all 48 group elements. Equality of endpoint ranks, or invertibility of
the two routes separately, would not repair that error.

Independent completed compiler roles can retain their distinct complete
matchers, as in #7828 and #7840. The common external weight depends only on
the allowed ancestor/atom data, not on this fresh cover; it therefore
commutes with these fresh right routes under the same source contract.
No additional cover is inserted at an unfinished proper-projector boundary.

## 7. Executable evidence

`routes.py` produces `DESCRIPTORS.json.gz`, containing each rational input
matrix, its provenance, q, pivots, forward and inverse words, both coupled
role references, coefficient bounds and source operation counts.
`EXAMPLES.json` is a readable extract showing the pivot, nonunit-shear and
fractional-carry boundaries. There is no width argument in the constructor.

`check.py` does not import the constructor, the earlier basis engine or
their checkers. It reconstructs expected source matrix identities from the
pinned complete bases and port charts, multiplies elementary words
independently, uses reverse-direction rational elimination for inverses,
and applies words directly to modular basis vectors and high rows.

The initial finite catalogue contains:

* 513 complete equal-rank matchers between the previously reviewed
  nested-difference bases;
* all 111 essential 15-coordinate source stage routes, with the other
  coordinates regarded as spectators in the source's full ambient;
* five explicit boundary fixtures, including dimension one;
* q=3,5,7,11 and tested widths w=1,2,3 for each descriptor.

The 15-coordinate evidence is an essential-block algebra check. It does
not substitute 15, 8 or the old raw ambient for the final compiler N in the
source's physical counts or prime inequality.

The separate verifier records 2,516 descriptors, 5,032 exact rational
forward/inverse products, 15,096 prime-power word actions and 7,548 affine
chart checks. It also checks all 3,888 elements of `GL_2(Z/9)` for the
fractional-carry route and its inverse, and all 48 low classes for the
noncommutative carry cocycle. The checked words have at most 62 records
per high row and observed rational coefficient components of at most six
bits. Those observed maxima are finite evidence, not universal height or
count improvements.

Rejection/boundary controls cover:

* pivot 3 at q=3 versus a valid different row pivot; the q=5 word chooses
  the original pivot and can contain denominator 3;
* discarding a shear coefficient because it is zero modulo q, which fails
  at q^2;
* wrong forward order and wrong inverse order;
* unequal coupled X/Y routes;
* the failure of the local-field pivot guarantee for a composite modulus.

The finite coefficient population includes nonunit addition numerators and
odd denominators that are units for their particular q. This is expected:
the complete matcher is dyadic, but its fixed-q factor word need not be.
No extra odd-prime exclusion follows from those q-selected denominators.

## 8. Retained limitations and next question

The dyadic closure removes additional forbidden odd primes arising from
these complete fixed bases and matchers. For the physical cover, retain
the quantitative source requirement `q>2^45 N^5` with the actual final N,
all weighted fallback/stock inequalities, complete fibres, owned storage,
precision-tape service and every inverse/movement charge. The small primes
used by the exact algebra tests are not claimed to meet that physical
budget. No numerical q is selected for the astronomical final compiler.

This is full GL routing. It is not the restricted prescribed
lower/permutation/lower factorization from #6201, and does not alter that
route's rank-profile obligations. It does not address the growing outer
fine primes or analytic integer-recovery exclusions. No selected
assumption, physical storage theorem, rate or kappa changes here.

The immediate next step is a separate review of the minor-ratio bit bound,
transpose/inverse chronology and exact source tariff binding, followed by
consolidation into the dyadic contribution if accepted. Broader descriptor
generation for the astronomical catalogue remains finite preprocessing;
it must not be presented as an executed or newly priced streaming service.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit the retained compiler, native cover, ordered-affine primitive and
dyadic basis contributions. This package does not modify their frozen files.
