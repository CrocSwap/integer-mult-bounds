# Two-coefficient rigidity of single-contact frame contractions

Jerry Chen / @CubeJerry, with substantial OpenAI assistance. Apache-2.0.

## 1. Claim and source

**Claim type: a finite, source-bound obstruction, proved by an exhaustive exact
certificate and a general algebraic reduction. No new κ.**

The source is the 18,622-event, 772-public-register native word of #6824, at
`2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`. Its canonical JSON payload digest is
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`.
The byte-preserved export comes from #6835 at
`44316f3e6023a7f8c516360e22e9efd6f0fe48c5`; the exact source path, Git blob,
container digest and payload digest are in `retained/SOURCE-PINS.json`.

A **single-contact visit** of a register consists of two consecutive MOVE
events in that register's lifetime, with exactly one ADD touching the register
between them. Any number of SCALEs on it may occur between the MOVEs. There
are no intervening COPYs or lifetime boundaries on the register. Both MOVE
ranks must be positive. These definitions concern that register's event
sequence; arbitrary events on other registers may intervene.

There are exactly **1,466 visits**, involving **1,278 distinct ADD events**.
Deleting the ADD would let the two consecutive frame changes be contracted,
after commuting the SCALEs out of the intermediate frame. For public registers
both changes ascend; for owned registers both descend. The combined rank is
the sum of the two ranks, so for `0 < t < 1` it would replace a positive paid
term `a^t + b^t` by the smaller term `(a+b)^t`, without changing helper
endpoints. This explains why the attempted edit is relevant to the invoice.
No claim is made that an arbitrary deletion preserves the native operator.

**Theorem 1 (source-bound).** Choose any one of these 1,278 ADDs. Delete it.
One may additionally change the coefficient of any one other existing ADD,
COPY or SCALE to an arbitrary rational number. One may replace both boundary
hub maps by arbitrary invertible rational maps supported on their original
zero-frame and full-frame register sets. Even with all of this freedom, the
result cannot have the original public endpoint.

The theorem also rules out deleting the selected ADD without another
coefficient change. Indeed its coefficient is individually rigid: any
nonzero rational change violates the invariant boundary block.

This is a statement about **fixed scalar-event operands and order**, with at
most the two coefficient changes specified above. It does not rule out a
third coefficient change, a new scalar gate, changed operands, a new helper,
changed helper endpoints, an interior basis change, or a different native
word. It is not a universal lower bound on κ or on native transformation
cost. Contracting the two MOVEs does not change the scalar calculation used
in the proof, so it cannot bypass the obstruction.

## 2. A boundary block that free hubs cannot change

Work over the rationals; a rational impossibility also excludes dyadic
implementations. Let `V` be the public coordinates, `K` the registers whose
initial frame is zero, and `R` those whose final frame is full. A map
supported on `K` is an arbitrary invertible map on those coordinates and the
identity on the complement, with no cross-block entries. Define supported
maps on `R` similarly.

For every public matrix `T`, zero-hub map `G0` and full-hub map `G9`,

```
(G9 T G0)[R̄,K̄] = T[R̄,K̄].                         (1)
```

Rows outside `R` of `G9` and columns outside `K` of `G0` are the corresponding
unit vectors. This proves (1) directly. Thus repairing a changed word to the
original endpoint `A` requires

```
T[R̄,K̄] = A[R̄,K̄].                                (2)
```

The condition is C1 of #6835's hub normal form. We use only this elementary
necessary condition, not the sufficiency theorem or its gauge constructor.
The other necessary fact is that `T` must be invertible: multiplication by
invertible boundary maps cannot repair a singular public endpoint.

The actual hub parts are those of #6835 §3.4, not all events that happen to
carry a zero/full frame label. Its 5,766 / 7,356 / 5,500 pre/middle/post
split commutes events only across disjoint registers and preserves every
per-register sequence. The post private lifetimes are wholly inside that
part. Hence the three parts induce square public maps whose product is the
invertible original endpoint. Both original public hub maps are therefore
invertible. Some owned boundary-frame events remain in the middle; the
certificate includes them as possible compensators.

The pinned word has `|K|=556`, `|R|=571`, and
`A = I + Σ_r E_(r+112,r)` for its 104 live ports. In particular `A` is
invertible, with `A⁻¹ = I − Σ_r E_(r+112,r)`.

For edits in the middle word, allowing arbitrary boundary maps before and
after the whole word is equivalent to allowing replacement of its original
hub maps: the unchanged original hub maps are invertible on the same
coordinate sets. The chosen deleted contact lies at an intermediate frame.
If the compensating event is itself part of a boundary hub, arbitrary
replacement of that hub already subsumes its coefficient change. It adds
nothing beyond the one-deletion case, which the nonzero boundary derivative
rules out. The certificate nevertheless considers every scalar event as a
possible compensator; no middle event is removed from the search by a hub
classification.

## 3. Exact response of one or two coefficient changes

All scalar events are linear. We allow COPY to overwrite its owned
destination even when that destination is nonzero. INIT and CLEAR reset an
owned coordinate. This is a relaxation used only for the obstruction:
every legal native word is included, and failure in this larger linear model
implies failure under the stricter COPY-zero contract. In particular we do
**not** impose a zero-before-CLEAR condition; the retained owned-erasure
contract allows nonzero erasures.

For a scalar event `e`, let `d_e` be its destination and let `s_e` be its
source (the destination itself for SCALE). Let `v_e` be the row of that
source immediately before the event, expressed in public inputs. Let `u_e`
be the final public response to inserting one unit in the destination
immediately after the event. Both are calculated in the unmodified source
word. Changing the event's coefficient by `α` changes the public endpoint by

```
α u_e v_e.                                           (3)
```

Here vectors `u` are columns and vectors `v` are rows. Formula (3) applies
to ADD, COPY and SCALE. For COPY, its destination-reset part is independent
of the coefficient, so only the source contribution changes.

For two events `a < b`, let `τ_ab` be the response in `s_b`, just before `b`,
to a unit inserted in `d_a` just after `a`, propagated through the intervening
original events. If their coefficient changes are `α` and `β`, then

```
T − A = α u_a v_a + β u_b v_b + αβ τ_ab u_b v_a.       (4)
```

To prove this, expand the product of event matrices with the two rank-one
increments. There are the unchanged term, two single-increment terms, and
one term using both increments. The middle contraction in the last term is
exactly `τ_ab`. Rectangular public-input injection and public-output
projection may be placed at the two ends; owned resets in the middle do not
alter the expansion. No invertibility of intermediate events is needed.

Set

```
p_e = u_e restricted to R̄,
q_e = v_e restricted to K̄.
```

The necessary boundary equation is consequently

```
α p_a q_a + β p_b q_b + αβ τ_ab p_b q_a = 0.          (5)
```

Deleting an ADD with original coefficient `c` fixes its coefficient change
to `−c`, a nonzero rational. Equation (5) is therefore **linear in the one
remaining unknown coefficient change**. There is no sampling of rational
coefficients and no numerical tolerance.

## 4. A complete filter for the second event

The certificate first checks `p_d ≠ 0` and `q_d ≠ 0` for every possible
deleted event `d`. Therefore a nonzero change of that coefficient alone
violates (2).

Two nonzero vectors have the same **direction** if they are proportional
over the rationals. A direction is stored canonically by dividing by the
first nonzero coordinate. The following list is complete for a possible
compensator `c`.

1. If `p_c` and `q_c` are both nonzero, then `p_c` must be proportional to
   `p_d`, and `q_c` must be proportional to `q_d`.
2. If `c > d`, `p_c ≠ 0`, and `q_c = 0`, then `p_c` must be proportional to
   `p_d`.
3. If `c < d`, `p_c = 0`, and `q_c ≠ 0`, then `q_c` must be proportional to
   `q_d`.
4. All other cases are impossible.

For item 1, rewrite (5) as a sum of two outer products,

```
α p_a q_a + β p_b (q_b + ατ_ab q_a) = 0.
```

Neither coefficient change can be zero in a repair. A nonzero outer product
can be the negative of another only if their column directions and row
directions agree. This forces both proportionalities. For item 2, (5)
becomes `α(p_d + βτ_dc p_c)q_d=0`. For item 3 it becomes
`β p_d(q_d + ατ_cd q_c)=0`. The remaining zero cases leave the deleted
event's nonzero outer product uncancelled.

**The zero-block cases in items 2 and 3 are essential.** A compensator can
have zero original boundary derivative while the mixed term in (4) repairs
the deletion. The positive controls include an explicit such example. A
filter that groups only nonzero outer products is incomplete.

For a surviving ordered pair, choose common normalized directions `p,q`
and write `p_a=a_u p`, `p_b=b_u p`, `q_a=a_v q`,
`q_b=b_v q`; the relevant absent vector has scale zero. Equation (5) is

```
α a_u a_v + β b_u b_v + αβ τ_ab b_u a_v = 0.          (6)
```

If `a` is deleted, solve

```
β (b_u b_v + ατ_ab b_u a_v) = −α a_u a_v.
```

If `b` is deleted, solve

```
α (a_u a_v + βτ_ab b_u a_v) = −β b_u b_v.
```

The right side is nonzero because the deleted event has nonzero `p_d,q_d`
and a nonzero coefficient. Thus a zero coefficient on the left proves an
inconsistent equation; otherwise there is exactly one rational solution.

## 5. Exhaustive certificate and singularity witnesses

The verifier reconstructs the visit domain from the literal per-register
event sequences. It derives all prefix rows and all suffix responses by
exact rational arithmetic. The complete direction filter leaves exactly
**172 ordered (deleted event, compensator) pairs**, considering every existing
ADD, COPY and SCALE as a possible compensator.

For **157 pairs**, the coefficient on the left of (6) is zero and its right
side is nonzero. For the remaining **15**, the unique rational solution makes
the complete public map singular. These cases are not discarded merely
because a coefficient is nondyadic or because a zero SCALE would be illegal.
They fail even in the relaxed rational linear model.

For the singularity calculation, write (4) as `T=A+UV`, where

```
U = [αu_a, βu_b],
V = [v_a; v_b + ατ_ab v_a],
B = I₂ + V A⁻¹ U.
```

The determinant identity gives `det(T)=det(A)det(B)`. In all 15 cases
`det(B)=0` exactly. More concretely, take a nonzero vector `z` with `Bz=0`
and put `x=A⁻¹Uz`. Then `Tx=U(Bz)=0`. The vector `x` cannot be zero:
otherwise `Bz=z+VA⁻¹Uz=z`, contradicting `Bz=0` and `z≠0`.

The replay does not stop at this two-dimensional calculation. It rebuilds
the changed literal program separately for each case, evaluates all 772
public rows directly, and checks the displayed nonzero `x` against those
rows. Thus each exceptional case has an exact, source-bound null vector.

Together, the complete filter, the 157 inconsistent equations and the 15
literal null-vector checks prove Theorem 1.

## 6. Controls and limits

The controls check the two-event identity against literal matrix products,
including nonzero mixed terms and COPY resets. A two-parallel-ADD example
admits a deletion and a coefficient retuning, so the method must accept a
possible repair on another word. A second example has a compensator with
zero original boundary derivative, and repairs the endpoint using supported
boundary maps. It checks the zero-direction cases that a naive filter misses.
Both time orders of the zero-derivative example are exercised. Twelve
two-event identities include COPY overwriting a nonzero owned row and
CLEAR erasing a nonzero row in the relaxed model. Mutating a retained
source byte or each of the 15 actual certified null vectors must fail.

A separately written verifier reconstructs every register trace and tests
all ordered deletion/compensator possibilities without the primary
direction buckets. It solves the sparse boundary matrix equations directly,
then performs Gaussian elimination on each complete 772-by-772 matrix,
without using the two-by-two determinant formula. All 15 exceptional maps
have exact rank 771. This independent computational check complements the
written completeness argument; it is not independent human acceptance.

This package proves an algebraic obstruction to a clearly specified change
of one finite native word. It does not replay or strengthen the complete
#6833 caller, the BIT supplier, compiler strictification, or the outer
multiplication theorem. The selected result and its five inherited framework
assumptions remain unchanged. A successful edit outside this class would
still require full native legality, arbitrary-input replay, the complete
productive/paid invoice and the outer proof obligations.

## 7. Open next questions

* The companion `JOINT-PROOF.md` closes the next coefficient class for
  deletion 10947: two additional jointly solved compensators also fail.
  Can that larger class work for another deletion, or can three compensators
  repair deletion 10947? The joint theorem does not cover all triples or
  other operation classes.
* Can an interior basis change remove a stop while changing the scalar
  operands? The theorem allows only boundary gauges and fixed operands.
  Specify one available co-frame bank and charge its complete entry, exit
  and restoration operations before searching.

Both questions require a genuinely changed edit class. Repeating the present
two-coefficient search on the same pinned word is unnecessary.
