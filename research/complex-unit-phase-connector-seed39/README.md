# All unit complex phases inherit the signed connector minimum

**Scoped negative result; no new kappa.** Ross Richardson's
[PR944](https://github.com/CrocSwap/integer-mult-bounds/pull/944) signed connector
still requires **fourteen complete child queries** when every query may carry
an arbitrary exact complex coefficient of modulus one. Any number of unit
rotations of the dirty root is also allowed, even free in the lower-bound
relaxation. The result covers the canonical matrix and its 288 signed/permuted
variants. It extends the operation alphabet; it does not rerun a larger search
inside the predecessor's signed alphabet.

For positive fixed complete prices `c_F`, common to all phases of operator F,
the exact minimum remains

```
2 sum_F c_F + 2 min_F c_F.
```

The attaining words are the six existing repairs from
[@martinxxx9's PR1088](https://github.com/CrocSwap/integer-mult-bounds/pull/1088),
retained unchanged. The new evidence is the continuous-phase reduction, the
thirteen-query exclusion and a separately implemented triangle-collapse check.
Concurrent [PR1551](https://github.com/CrocSwap/integer-mult-bounds/pull/1551)
establishes the finite sixth-root case. This contribution independently
corroborates that case and adds the whole unit circle, arbitrary unit root
rotations, and a geometric collapse to the older signed obstruction. Priority
for the sixth-root result is not claimed here.
An explicit thirteen-query **nonunit** control succeeds: replacing the first
two adjacent `B0-` calls in PR944's canonical word by one `B0^{-2}` preserves
the map. Thus this result does not extend to arbitrary magnitudes.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/complex-unit-phase-connector-seed39
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/complex-unit-phase-connector-seed39 outcome=negative-result`.
The registered commands check [CERTIFICATE.json](CERTIFICATE.json), independently
recompute the finite domains and reject damaged packages. For a direct replay:

```sh
python3 -I -O -B research/complex-unit-phase-connector-seed39/verify.py
python3 -I -O -B research/complex-unit-phase-connector-seed39/independent.py
```

These report 720 signed paths, 30,240 normalized triangle paths, 1,728 attaining
orbit words, 172 semantic controls, and 444 dense forward/inverse pairs. The
written reduction below addresses all unit complex phases; finite phase samples
alone would not prove that statement. This is not a proof-assistant theorem.

## Exact interface and optimistic budget

There are seven distinct length-L rows `x0,x1,x2,y0,y1,y2,z` over C, all with
arbitrary incoming contents. The fixed maps `A_i,B_j` are complex-linear and
need not commute or be invertible. The required endpoint is

```
x_j unchanged; z unchanged;
y_i += sum_j M_ij A_i B_j x_j,

M = [[1,1,1], [1,1,-1], [1,-1,0]].
```

The allowed complete calls are `B_j^b: z += b B_j x_j` and
`A_i^a: y_i += a A_i z`, with `|a|=|b|=1`, independently chosen at every
occurrence. Optional root passes are `z *= rho`, with `|rho|=1`. These are
exact constants, central in the complex-linear maps. The source rows are
immutable. Each child restores its own scratch and prescribed head positions;
its increment is independent of old target contents. All seven data rows are
excluded from child scratch. Only final outputs may be observed.

The straight-line word must work for arbitrary admissible maps and inputs.
There are no extra connectors, source/output rotations, source mutations,
combined queries, direct products, free copies, overwrites, conjugate-linear
readers or other data operations. Special maps and restricted input states are
outside the generic lower bound. Rounded arithmetic is outside this exact model.

The proposed saving was one complete child: fourteen to thirteen. The favorable
budget prices a phase-bearing query exactly as its signed counterpart and grants
root rotations for free. Since even this relaxation requires fourteen, no
implementation of these phase operations with additional nonnegative costs can
give that query saving. This rejects this mechanism, not other helper inventories
or a different selected-supplier construction. Actual phase preparation, scalar
multiplication, storage, traversal, frame and precision costs are not declared free
in an implementation.

## Proof of the fourteen-query floor

**1. Remove root rotations.** Let `p_t` be their cumulative product. In the
moving coordinate `w=p_t^{-1}z`, a B call has coefficient `b/p_t`, and an A call
has coefficient `a*p_t`. Both remain unit. Restoring arbitrary incoming z
forces the final product to equal one. Consequently any word with root rotations
gives a word with the same number of A/B queries and no rotations. This is an
algebraic relaxation for the lower bound, not an uncharged implementation pass.

**2. Every active operator occurs at least twice.** In a word without rotations,
restoration of z gives zero sum of the coefficients of each B_j. Elimination of
`A_i z_initial` gives zero sum for each A_i. Every row and column of M is active,
so one occurrence is impossible. These statements already follow by setting the
maps to identities and varying the independent source and root inputs. Thus
fewer than twelve queries cannot work. Two unit coefficients with sum zero are
opposites.

**3. Twelve queries reduce to signed queries.** Each B_j then has a pair `b_j,-b_j`
and visits coefficient values `0,b_j`; each A_i has a pair `a_i,-a_i`. A nonzero
entry `M_ij` forces `a_i*b_j` to be 1 or -1, because that output's two readouts
differ in coordinate j by `b_j` or `-b_j`. The bipartite support graph of M is
connected. Propagating these relations gives a unit `a` such that every
`a_i/a` and `a*b_j` is a sign. Rescale the bookkeeping coordinate by a; all
queries become signed and the requested M is unchanged.

There are `6! = 720` labeled signed B paths, containing each `B_j+` and `B_j-`
once. A row can be read with its two A calls exactly when it is a difference
of two visited source-prefix vertices. No path supports all three rows of M.
The original PR944 certificate supplies that exclusion; both new implementations
recompute it. The histogram below records the bit mask of supported rows:

| Row mask | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Signed paths | 72 | 84 | 84 | 48 | 264 | 84 | 84 | 0 |

**4. A thirteen-query word has one triple and five pairs.** First suppose B_j
is tripled. Delete its column from the support graph. For this M the remaining
graph is still connected and contains every output vertex, for each j=0,1,2.
Applying the preceding relations to the two paired source operators again
makes all A coefficients and both other B pairs signed, using one unit coordinate
rescaling. The three coefficients `u,v,w` of B_j remain unit and satisfy
`u+v+w=0`.

They cannot be collinear over R: three collinear unit numbers are signs of one
unit number, and an odd number of signs cannot sum to zero. In their actual
order the B_j coordinate visits the triangle `0,u,u+v,0`. Any nonzero difference
between its three vertices is one of `+-u,+-v,+-w`. At least one output uses
column j, so a required difference is 1 or -1. One triangle side is therefore
real of length one. The other sides cannot be parallel to it.

Collapse the third vertex onto either endpoint of that real side, then translate
the initial image to zero. Every zero or real unit difference used by a readout
is preserved: the only nonzero real differences are the chosen side; equal
vertices remain equal. Around the three-step triangle, the collapsed path has
exactly two nonzero increments, +1 and -1, and one zero increment. Drop that
zero query. Keeping all readouts at their corresponding boundaries gives a
twelve-query signed word for M, contrary to step 3.

Alternatively, `u+v+w=0` with unit lengths is an equilateral triangle. After
one side is real of length one, its increments are precisely
`sigma*(1,omega,omega^2)`, where `sigma=+-1`,
`omega^2+omega+1=0`. The other four source increments are the two signed pairs.
Thus `3 choices of j * 2 signs * 7! = 30,240` labeled paths exhaust the
normalized case. Both exact implementations find zero full covers;
`independent.py` additionally performs and checks all 30,240 collapses. This
finite census supports the geometric argument with a separate route to exclusion.

If an A operator is tripled, reverse chronology and exchange A/B roles. An
original ordered pair B_j before A_i becomes a new source A_i before a new
readout B_j; its scalar product is unchanged. Balanced sums preserve root
restoration and dirt cancellation, and the coefficient matrix transposes.
Since this M is symmetric, the resulting word is the already excluded tripled-B
case. No noncommuting operator factors have been commuted: this is a statement
about the universal coefficient word in renamed roles.

**5. Attainment and prices.** PR1088 supplies a fourteen-query word for each
choice of the repeated operator, with four occurrences there and two elsewhere.
They use only signs and so belong to the larger alphabet. For any correct word
write the occurrence counts as `n_F=2+e_F`, where `e_F>=0` and `sum e_F>=2`.
Positive fixed prices imply
`sum n_F*c_F >= 2 sum c_F + 2 min c_F`. Repeating a cheapest operator attains
equality without rotations. Nonnegative root-rotation charges do not change it.
The same conclusion holds when other unit phases cost extra relative to these
signed complete prices. It need not hold for sign-, phase-, state- or word-dependent
prices that violate that comparison.

Row/column permutations and sign changes preserve the extended alphabet and
its operation counts, so the result passes to all 288 matrices in the existing
orbit. The verifier replays all six attaining words for each matrix.

## Complete cost and what the result does not establish

A complete fixed-port price `c_F(L)` includes coefficient/source access, the
entire child, its target updates, phase/sign work, scratch restoration, frame
adapters, head return and per-call dispatch. Charge reusable preparation `P_F`,
initial admission/layout `I`, and any additional instruction emission/storage
`E` separately. The optimal fixed-price bill is

```
I + sum_F P_F + E + 2 sum_F c_F(L) + 2 min_F c_F(L).
```

Phase-specific preparation or root rotations add their actual bills; no helper
is silently introduced. A port- or word-dependent implementation must price
its actual invocations rather than apply this fixed-price formula.

For the predecessor's balanced dirty factor lowering, split an ordered product
F into R followed by S, borrow a distinct dirty row w, and execute
`R(x,w); S(w,y); inverse(R); inverse(S)`. The complete recurrence is

```
C([f]) = complete leaf cost + leaf dispatch,
C(F)   = 2 C(R) + 2 C(S) + node dispatch,
h([f]) = 0; h(F) = 1 + max(h(R),h(S)).
```

Every inverse includes all its leaves. Source access and restoration are included
in each complete leaf. Peak borrowed storage is one root row plus the largest
child depth, with data ports excluded from scratch. This is the inherited
factor-length recurrence, not an input-size contraction or a new physical compiler.

Seed `39 mod 6 = 3` places the shortest product at A0 in B0,B1,B2,A0,A1,A2
order, giving lengths `[5,6,7,2,3,4]`. With unit leaf prices and separately charged
dispatch, preparation and physical access, the complete expansions have

| Repeated operator | B0 | B1 | B2 | A0 | A1 | A2 |
|---|---:|---:|---:|---:|---:|---:|
| Leaf queries | 356 | 380 | 404 | 308 | 320 | 332 |

All six expansions restore all ten incoming rows in the free noncommutative
module; all literal inverses restore too. Four length-L dirty rows, including
the root, are borrowed. The 308 count is an inherited fourteen-query construction
with a seed-selected tariff, not a new scalar saving or runtime measurement.
The magnitude-two thirteen-query control requires its own complete lowering and
is not assigned a free single-query implementation here.

No occurrence of this abstract connector in the selected supplier is supplied.
Selected-call realization, owner/whole-call hosting, frames, coefficient/phase
preparation, precision and rounded linearity, tape compilation, all-size recurrence
and outer analytic transfer remain unresolved or inherited. No selected cold
replay, improved paid rank profile, larger kappa, unconditional multiplication
theorem, or independent human review is claimed.

## Evidence, provenance and overlap

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`; OS-random assignment seed **39**,
complex-supplier track. [TASK.json](TASK.json) records all three candidate tasks,
the local claim and the scope change from the broad helper-inventory card to
this optimistic complex circuit question. There was no pinned sprint issue.
Source hashes, Git blobs and predecessor heads are in [SOURCES.json](SOURCES.json).
The selected context is reviewed PR1094 at
`0fc329d0bec93ca7cd288eaea1295172e8789810`, kappa
`836330098538459/500000000000000000`. Its source manifest leads to
`research/complex-t16-rare-pattern-exchanges`, with unchanged PR589 bit ancestry.
The selected binding check is orientation evidence, not a fresh circuit replay.

`verify.py` uses integer coefficients in the basis `(1,omega)`, a full
prefix-difference census, and free operator words on arbitrary incoming rows.
`independent.py` imports no primary or predecessor executable: it uses doubled
real/imaginary integer coordinates, recursive position assignment, grouping by
imaginary parts, explicit triangle collapse, and separate rational dense arithmetic
on noncommuting maps of sizes two and three. These are separate implementations
authored in the same AI-assisted session. The dense checks are finite fixtures.
The all-size identity and exclusion rely on the written linear-algebra reduction.

Controls delete and change signs of every gate in all six attaining words,
reject a missing final root rotation, distinguish characteristic zero from F3,
and accept the exact nonunit thirteen-query map while rejecting it from the
unit alphabet. A five-query unit-phase word restores the root and adds a
nonreal output, explicitly preventing reuse of the signed evenness argument.
Package tests additionally reject source/certificate damage and
run a read-only relocated copy. No floating point or solver is used.

The closest concurrent result is
[PR1551](https://github.com/CrocSwap/integer-mult-bounds/pull/1551), head
`be8768d5fd8e9e7a1f714424f25b34b0e807daa0`, published from
[Discussion1539](https://github.com/CrocSwap/integer-mult-bounds/discussions/1539).
Its finite sixth-root alphabet excludes root scaling and exhausts 291,600
source paths. This package covers every complex unit coefficient and unit root
rotations by support-graph normalization, then proves the thirteen-query
exclusion geometrically. Only the 720 signed paths are needed for that proof;
the normalized 30,240-path census and explicit collapses are additional
corroboration. Its code was authored before the concurrent package was found
and imports none of it. These distinctions, not a different seed, justify the
separate contribution. The final literal-term search missed Discussion1539;
following Discussion1540's link found it, and its published proof was inspected
before submission. No novelty guarantee is inferred from that search.

Another concurrent comparison is
[PR1526](https://github.com/CrocSwap/integer-mult-bounds/pull/1526) at
`1fb85dc6813b88483f4f0a359ccd722376acd292`: paid doubling/halving changes magnitude
and reaches thirteen child calls plus two root scans. This package explains why
phase-only root passes cannot supply that saving. It does not claim that earlier
construction or depend on its implementation. [PR1349](https://github.com/CrocSwap/integer-mult-bounds/pull/1349)
at `8adb25ce6d2090de170e241a170668e8fd7cf5a2` instead changes the field to F3;
three equal signs can cancel there. [PR1490](https://github.com/CrocSwap/integer-mult-bounds/pull/1490)
at `db410cbd344bcf58f754689ae893d4c31a01f32d` prices Gaussian helper gauges in a
different selected-word model. [OVERLAP.json](OVERLAP.json) retains search coverage
and limits; absence of a match is not proof of novelty.

## Open next questions

Can magnitude-changing calls be compiled at a complete cost that beats this
fourteen-query bill in an actual complex supplier? This matters because phase
changes alone are now excluded in this model. PR1526 is an existing concrete
starting point: compare its two complete scaling scans and coefficient precision
against the one child it removes on a specified fixed-port backend. The blocker
is a selected supplier instance and complete physical/precision admission, not
more phase samples. Do not reopen this unit-only domain with a denser phase grid.

## Credit

Ross Richardson's PR944 (`5dbcfbc63f646de5a1354f6b9760ec03837233f0`) supplies the
signed obstruction, interface, canonical word and dirty lowering. @martinxxx9's
PR1088 (`b0396aad724fec58630fbd4d13a809c562f18d9e`) supplies the six weighted
repairs; both are incorporated in the base review ledger. Earlier connector
credit remains with Richardson's PR934, CubeJerry's PR889, Chafik Boukhalfa's
PR628 and the retained framework. The concurrent results above retain their
separate credit. No predecessor package is modified or reattributed.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in reasoning, implementation, verification and prose. New work is Apache-2.0.
The mathematical claims were checked against the sources and replay evidence;
this is not independent human review or proof-assistant verification.
