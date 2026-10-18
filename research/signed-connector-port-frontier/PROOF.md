# Exact port-tariff frontier in the twelve-query, four-unit-shear class

This is a finite exact optimization of a stated ordinary-query circuit class.
The reduction below is mathematical; its remaining finite census is checked by
independent programs and attaining literal words. It is not proof-assistant
verification, a universal circuit optimum, or a new multiplication bound.

## 1. Fixed interface and inherited premises

Work over characteristic zero, for example Q or C. There are eight distinct
arbitrary-dirty arrays of a common positive length:
`x0,x1,x2,y0,y1,y2,z,w`. The six fixed linear maps `A_i,B_j` need not commute,
be invertible, or obey any other identity. Uniform correctness means correctness
for every such collection of maps and every independent initial array value.

An ordinary source query is `r += s B_j x_j`; an ordinary reader query is
`y_i += s A_i r`, where `r` is `z` or `w` and `s` is +1 or -1. The only other
array operation allowed here is the one-way unit shear `z += s w`. Sources,
coefficients, the unused root and other data rows are preserved by each query.
Every child restores its private workspace and required head positions; outputs
are not subsequently read. Each candidate contains exactly twelve ordinary
queries and exactly four unit shears. Initializing roots, aliasing their initial
dirt, scaling queries, using opposite-direction shears or reading outputs would
change the class.

The required update is

```
y_i += sum_j M_ij A_i B_j x_j,
M = [[1,1,1], [1,1,-1], [1,-1,0]],
```

with all source arrays and both roots restored. The signed connector and its
one-root obstruction are predecessor work from Ross Richardson's PR944. The
twelve-query two-root construction is Charles Bethin's PR1637; the one-way
four-transfer construction and source/read port reduction are Ross Richardson's
PR1651. This package completes the port census at exactly four unit transfers
and optimizes arbitrary complete port tariffs within that finite class. It does
not need an exclusion of three transfers in a broader alphabet.

## 2. Twelve queries force one signed pair at one port per operator

Every target row and every target column is nonzero. Thus every named operator
must occur: otherwise choose all maps to be identities and vary that row's
source to contradict the required update. Moreover, each operator must occur
at least twice. A single source occurrence injects a nonzero root vector whose
coefficient cannot vanish under subsequent invertible shears; later distinct
source operators cannot cancel it uniformly for independent source values.
A single reader occurrence leaves a nonzero coefficient of the arbitrary
initial root dirt in its output. These statements can already be witnessed by
scalar identity operators. Exactly twelve queries therefore force exactly two
occurrences of each of the six operators.

Let `h` be the sum of shear signs before an event. The effect of shears on the
independent initial root dirt is

```
U(h) = [[1,h],[0,1]],       U(h)^(-1) = [[1,-h],[0,1]].
```

Restoration of arbitrary independent `z_initial,w_initial` forces final `h=0`.
Consequently four unit shears have two signs +1 and two signs -1.

Normalize the current root vector by `U(h)^(-1)`. A source query to z injects
its signed source symbol in direction `(1,0)`; one to w injects it in direction
`(-h,1)`. Between source events a shear leaves this normalized vector unchanged.
The two injections of a fixed B_j must sum to zero at the end. If their ports
differ, their second coordinates cannot cancel. If both use z, their signs must
be opposite. If both use w, their signs must be opposite and their heights h
must agree. No equality or zero assumption about initial dirt is used.

For readers, the initial-dirt coefficient row of a z read is `(1,h)` and that
of a w read is `(0,1)`. Two reads of a fixed A_i cancel the initial dirt only
if their ports agree and their signs are opposite; z reads must additionally
have equal h. In particular, the ability of source coefficients to agree does
not permit reads at unequal dirt heights. Using the same symbol for both
initial roots, or silently making either root clean, would invalidate this
necessity and admit false port assignments.

Thus each operator F has a well-defined root port `r(F)` and contributes one
positive and one negative ordinary query there. Encode this as six bits in
`B0,B1,B2,A0,A1,A2` order, with bit 0 meaning z and bit 1 meaning w.

## 3. Complete source-trace domain

Delete all six readers from a candidate. Since outputs are never read and a
reader leaves both roots unchanged, what remains determines every possible
root value available to readers. It consists of six labeled signed source
events and four signed unit shears. The domain is exactly:

- 8 assignments of the three B pairs to z or w;
- all `6! = 720` orders of the distinct events `B0+,B0-,B1+,B1-,B2+,B2-`;
- all `binom(10,4) = 210` choices of shear positions among ten events;
- all `binom(4,2) = 6` shear sign words with two + and two -.

The product is **7,257,600 source traces**, before restoration filtering. This
is a bijective encoding: from a trace one recovers its three source ports,
source-event order, four occupied shear positions and four shear signs. It
includes consecutive shears, source events at either end, and arbitrary source
pair nesting. There is no a priori bound on intermediate coefficients and no
assumption that a first source occurrence is positive. It is not a random search;
seed 31 chooses the research track/task; the enumeration uses no random
pruning or seed-dependent coverage. The stopping rule is full exhaustion.

Represent the root values after each prefix as

```
z = z_initial + h w_initial + q_z dot u,
w = w_initial + q_w dot u,       u_j = B_j x_j,
```

where `q_z,q_w` are integer triples. Both start at zero. A source query adds
`s e_j` to its root's q vector. A shear of sign s replaces
`(h,q_z)` by `(h+s,q_z+s q_w)`. Retain exactly the traces with final
`h=0,q_z=(0,0,0),q_w=(0,0,0)`. This is necessary and sufficient for full root
restoration for arbitrary independent inputs. Equivalently, each w-source pair
occurs at one common height, as proved above.

There are eleven reader gaps, indexed 0 through 10, before the first source/
shear event, between consecutive events and after the last. These eleven
coefficient states are exhaustive even if an original word has several readers
at one gap.

## 4. Necessary and sufficient reader-gap test

For row i and port r, choose two distinct gaps `a<b`. Let q_r(a) and q_r(b)
be the source coefficient triples there. The first reader has sign s and the
second sign -s. Their contribution is

```
s A_i (root_r(a) - root_r(b)).
```

It equals the required row exactly if the initial-dirt rows agree and

```
s (q_r(a) - q_r(b)) = M_i.
```

For r=w the dirt always agrees. For r=z it agrees exactly when `h(a)=h(b)`.
Consequently a row is available at a port if and only if some gap pair has the
same dirt and source difference either +M_i or -M_i. If a checker computes
`delta=q_r(b)-q_r(a)`, then `delta=M_i` requires signs minus then plus;
`delta=-M_i` requires signs plus then minus. The reader orientation is not a
free extra factor after a signed difference is selected.

Necessity follows from section 2 and the literal root states. Sufficiency is
also exact: insert the specified two reads at their gaps for each row. Different
reader pairs do not alter roots, sources, or one another's output rows, so all
three pairs can be inserted independently and reads sharing a gap can be put
in any order. Every admitted port mask therefore has an attaining full word;
every valid full word has a source trace and reader pairs admitted by this test.
No factor commutation occurs: a reader always applies A_i to the already
formed B_j x_j contribution, giving A_i B_j in that order.

One immediate independent consistency condition is that a z-source can never
contribute to a w-reader, because the only shear direction is w to z. Hence
`r(A_i)=w` and `M_ij != 0` imply `r(B_j)=w`. This directed support test is
necessary but is not used as a substitute for the complete gap census.

## 5. Why the port assignment is forced

There is also a short structural derivation of the singleton result. Its only
finite input is the inherited one-root obstruction: among all 720 permutations
of the six signed source steps, none has differences of visited vertices equal
to all three target rows up to sign. In row-availability mask order 0 through 7,
the exact counts are `72,84,84,48,264,84,84,0`. This is the PR944 obstruction,
not a new lower bound attributed to this package.

First suppose all three B pairs use w. Then z changes only at root shears.
For a nonzero z-reader row, its two equal-height gaps enclose an even number
of the four unit shears. Enclosing zero shears gives identical z values.
Enclosing all four gives the restored z value: there is no z-source update
before, between or after them. Thus a nonzero row encloses exactly two shears,
and their signs must be opposite. If their signs are s and -s, the difference
of the z source-coefficient vectors is

```
s (q_w at the first shear - q_w at the second shear).
```

Both w values are visited vertices of the six-step signed source walk. Since
s is a unit sign, every row available through z is therefore also a difference
of two visited w vertices, up to sign. A row read directly from w already has
this property. All three required rows would be available in one signed source
walk, contrary to the one-root obstruction. Hence **not all B pairs use w**.
The unit-coefficient premise is material here: a nonunit shear would give a
scaled difference, which need not itself be a permitted ordinary read pair.

Next, **not all A pairs use z**. To see this, transpose the complete linear
circuit, reverse its event order, exchange source and output roles, and swap
the two root names. A source update becomes a reader update and vice versa;
`z += s w` becomes `w += s z` under transpose and becomes `z += s w` again
after swapping the root names. The signs, query count and four unit-shear count
are unchanged. The full input/output map transposes, including the restored
root block. Set the new maps to `A'_j = B_j^T` and `B'_i = A_i^T`; since M is
symmetric, the renamed target is precisely the same connector. Arbitrary
linear maps remain arbitrary under transpose. If all original A pairs used z,
all transformed B pairs would use w, contradicting the previous paragraph.
This is a feasibility argument; it does not assert that physical tariffs are
invariant under transposition or port exchange.

Therefore at least one A pair uses w. The directed support condition at the
end of section 4 shows this cannot be A0 or A1: either full-support row would
force all three B pairs to w. Consequently A2 uses w, which forces B0 and B1
to w. Since not all B pairs use w, B2 must use z. Finally A0 and A1 must use z
because they both have a nonzero B2 entry. This forces exactly

```
B0=w, B1=w, B2=z, A0=z, A1=z, A2=w,
mask = 1 + 2 + 32 = 35.
```

PR1651 supplies this attaining word, retained with its attribution:

```
y0 += A0 z; z -= w; w -= B0 x0; y2 -= A2 w;
w -= B1 x1; z += w; y1 -= A1 z; z -= B2 x2;
y0 -= A0 z; z -= w; w += B0 x0; y2 += A2 w;
w += B1 x1; z += w; y1 += A1 z; z += B2 x2.
```

Writing `u=B0 x0,v=B1 x1,t=B2 x2`, the two A0 reads see
`z_initial` and `z_initial-u-v-t`; the two A1 reads see
`z_initial-u-v` and `z_initial-t`; the two A2 reads see
`w_initial-u` and `w_initial-v`. Their indicated opposite signs produce the
three required rows, and both roots finally restore. Thus the forced mask is
attainable for arbitrary dirty values without exchanging the order of A and B.

The complete census independently corroborates this necessity and supplies
literal witnesses: of 7,257,600 source
traces, **3,343,680 restore the roots**, and **80 restored source traces admit
all three reader rows**. Every one of those 80 admits precisely mask 35.
The number 80 counts source/shear traces, not all reader insertions or complete
sixteen-event words. No other port mask is feasible in the stated class.

## 6. Exact additive tariff optimization

Let `c_F,r,+` and `c_F,r,-` be positive complete fixed prices for signed ordinary
queries at a given root port, independent of incoming data and event order.
Define `q_F,r = c_F,r,+ + c_F,r,-`. These prices include source/coefficient
access, child arithmetic, routing and frame adapters, private restoration, head
return and dispatch. Let `t_+,t_-` pay complete signed unit shears. Let `I,P,D`
pay any remaining admission, coefficient preparation, selector/program loading
and control work, provided these charges are common to all candidate words.

By section 5 the feasible set is the singleton S={35}. The exact complete
additive optimum in the stated class is therefore the forced value

```
I + P + D + 2 t_+ + 2 t_-
  + q_B0,w + q_B1,w + q_B2,z + q_A0,z + q_A1,z + q_A2,w.
```

Every candidate necessarily pays this sum, by sections 2 and 5. The literal
witness attains it with twelve ordinary queries and two unit transfers of each
sign. This covers all positive real tariffs mathematically; the executable
selector uses exact positive rational tariffs. Sign-asymmetric prices are
supported because each operator's two signs are necessarily paired at one port.
Every feasible schedule has the same price under this model, even when port
prices differ. Reordering the four-transfer schedule cannot change that price.

Let r_F be the forced port above and let the other port be 1-r_F. Relative to
the optimistic, unconstrained bill that independently selects every operator's
cheapest port, the exact unavoidable surcharge is

```
sum_F max(0, q_F,r_F - q_F,1-r_F).
```

For example, if every pair costs 20 at z and 200 at w, and both unit-shear
prices are 1, the actual query-plus-shear bill is 664. Independently selecting
six cheap z ports would misleadingly give 124. The forced surcharge is 540.
These figures exclude shared I,P,D. This is an interface constraint even if
additional computation cannot improve any transfer count. A different query
budget is a different optimization: with sign prices 10 at z, an inherited
fourteen-query one-root witness costs 140 before its separately paid shared
work, so the twelve-query constraint can be expensive under these tariffs.

The exact optimizer is restricted to these fixed tariffs and this circuit
class. If preparation, control, child cost or routing depends on the particular
word beyond its operator port, its actual additional price must be included;
minimizing only the six query-pair tariffs would then not establish a complete
cost optimum. It also does not compare against more ordinary queries, nonunit
or bidirectional transfers, extra roots, changed operator identities, or mutable
sources. The 664-versus-140 illustration does not compare complete physical
backends until their respective admission, preparation, scratch and control
work are also paid.

## 7. Recursive lowering and unresolved multiplication obligations

A tariff is paid for a complete child, not merely for its abstract operator
label. The inherited exact recursive construction for an ordered product F=LR
uses a fresh private dirty row s and the literal commutator

```
R(x,s); L(s,y); inverse(R)(x,s); inverse(L)(s,y).
```

The inverse reverses every instruction and negates its sign; it does not assume
invertibility of L or R. Private descendants exclude both roots and every active
data/ancestor row and restore before sibling reuse. With complete sign-symmetric
child costs the inherited recurrence is

```
C([f]) = complete leaf cost + leaf dispatch,
C(F) = 2 C(R) + 2 C(L) + node dispatch,
h([f]) = 0,    h(F) = 1 + max(h(R),h(L)).
```

For sign-asymmetric primitive costs, sum the prices of the four actual signed
invocations instead of silently applying the symmetric recurrence. Root passes
remain separately paid, and no source access, full-array initialization, frame
change, private restoration or recursive child is free. A symbolic expansion
with independent dirty rows can verify the literal algebra of a chosen fixture;
it is not a physical tape compiler or a multiplication theorem.

Realization at the selected supplier's ports, compatible frames, whole-call
ownership/admission, precision, tape work and outer analytic assembly remain
unresolved or inherited. The selected construction, its conditional bound and
its kappa are unchanged. This result identifies the forced tariff in this
class and warns against assigning the six operators independently to cheap
ports when their full two-port realization is not yet known.
