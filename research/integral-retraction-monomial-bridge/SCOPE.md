# Exact formal interfaces and boundaries

Lean 4.30.0 locally accepted the universal source, positive fixtures and
197 queried axiom reports. The producer delivered source without executing
Lean; local execution is recorded separately in `REPLAY.json`. The interface
description below is retained from the producer, without mathematical changes.

## 1. Concrete meanings and the only certificate structure

All names below are within namespace `PR1497` unless stated otherwise.

* `Row n` is literally `Fin n → Int`; `Mat m n` is `Fin m → Fin n → Int`.
* `fsum` is recursion through coordinates `0,1,...,n-1`, with the empty sum
  equal to zero. `rowMul v A j` is `fsum intGroup m (fun i => v i * A i j)`.
  `matMul A B i` is `rowMul (A i) B`. These are ordinary built-in integer
  operations, not a primitive composition operation with an assumed law.
* `basis n i j` is 1 when `j=i` and 0 otherwise; `eye n i = basis n i`.
  `matSub A B i j = A i j - B i j`.

The proposition `MatrixIdentities M P Q W` has exactly three fields:

```text
mp       : matMul M P = zeroMat m d
qp       : matMul Q P = eye d
residual : matSub (eye N) (matMul P Q) = matMul W M
```

There are no image/kernel, reconstruction, independence, rank, generation, or
nonzeroness fields. Dimensions are arbitrary natural numbers; the proof source
includes the empty-index cases of its finite-sum arguments.

`Rows.rowMul_assoc`, `Rows.rowMul_eye`, `Rows.rowMul_basis`,
`Rows.rowMul_matSub`, and `Rows.rowMul_linear_combination` supply the concrete
interpretation. `matrixRetraction` then derives the abstract three identities.
In row-map order the abstract maps are

```text
m(z)=zM,  p(v)=vP,  q(z)=zQ,  w(v)=vW,
p(m(z))=0,  p(q(z))=z,  v-q(p(v))=m(w(v)).
```

Thus matrix composition/orientation is a proved interface, not an unfinished
assumption of the abstract bridge.

## 2. Additive result and precise quotient

`AbGroup` exposes zero, addition, negation, associativity, commutativity,
two identity laws, and two inverse laws. `Hom` exposes only a function,
zero preservation, and addition preservation. Negation, subtraction, natural
multiples, and integer multiples are handled by derived theorems.

`Retraction.L a` is defined as `∃ c, m(c)=a`. The proof of
`Retraction.mem_image_iff` has the two usual directions: `mp` gives the forward
direction; the residual identity at a kernel element gives the explicit
coefficient vector `w(a)` for the reverse direction. Surjectivity uses `q(b)`.

The quotient is **not defined to be the parameter group**. It is
`Quotient s.latticeSetoid`, whose actual relation is

```text
s.Rel a b := ∃ c, s.m.run c = GA.sub a b.
```

`Retraction.rel_iff` proves that this relation is equivalent to `p(a)=p(b)`.
That equivalence supplies the setoid laws and well-definedness of the descended
map. `qadd` and `qneg` use `Quotient.liftOn₂` and `Quotient.liftOn` to implement
`[a]+[b]=[a+b]` and `-[a]=[-a]`. Their representative-independence proofs are
explicit. `quotientGroup` proves the resulting abelian-group laws.
`quotientIso` constructs inverse **additive homomorphisms**, not just a set
bijection. Its inverse is precisely `b ↦ [q(b)]`.

Principal concrete interfaces:

| Declaration | Conclusion |
|---|---|
| `MatrixBridge.lattice_iff_integer_span` | The row-map image is exactly the displayed finite integer row combinations. |
| `MatrixBridge.lattice_eq_kernel` | Pointwise membership iff `rowMul v P = 0`. |
| `MatrixBridge.lattice_eq_kernel_as_predicate` | Literal equality of the two predicates. |
| `MatrixBridge.phi_surjective` | Every integer parameter row has a preimage. |
| `MatrixBridge.quotient_relation` | The relation is exactly `∃ z, zM = (v-w)`. |
| `MatrixBridge.quotient_equal_iff` | Equality of representative classes iff their difference lies in the row image. |
| `MatrixBridge.quotientIso` | The constructed abelian-group isomorphism. |
| `MatrixBridge.quotient_forward_on_representative` | Forward map sends `[v]` to `vP`. |
| `MatrixBridge.quotient_inverse_on_parameter` | Inverse sends `z` to `[zQ]`. |
| `MatrixBridge.quotient_left_inverse` / `quotient_right_inverse` | Both inverse equations. |
| `MatrixBridge.lattice_saturated` | A nonzero integer multiple in the lattice implies membership of the original row. |

`MatrixBridge.row_torsion_free` is proved using `Int.mul_eq_zero`; it is not an
assumption about integer rows. `Rows.row_zsmul` connects the recursive group
integer multiple to actual coordinatewise integer multiplication. The generic
saturation lemma has a torsion-free hypothesis; the concrete corollary supplies
it by this proof. No formal rank invariant or rank theorem is supplied.

## 3. Multiplicative meaning is constructed, not postulated

`CommGroup D` lists multiplication, identity, inverse, associativity,
commutativity, and the left/right identity and inverse laws. It has no exponent,
finite-product, monomial, composition, or reconstruction law fields.
`CommGroup.asAdd` merely renames these operations so that the elementary group
proofs can be reused.

The ordinary meanings are exposed by the definition equations:

```text
npow a 0        = 1
npow a (n+1)    = (npow a n) * a
zpow a (ofNat n)= npow a n
zpow a (-(n+1)) = inverse (npow a (n+1))
prod 0 f        = 1
prod (n+1) f    = f(0) * prod n (fun i => f(i.succ))
monomial x v    = prod n (fun i => zpow (x i) (v i)).
```

`AbGroup.zsmul_add` derives the exponent-addition law by two-sided integer
induction. `Finite.sum_add` derives product distribution in the multiplicative
interpretation from associativity and commutativity. `monomialHom` is then a
constructed homomorphism on actual integer rows. In particular, the file does
not assume an evaluation map that already preserves the desired compositions.
`Monomial.add`, `sub`, and `scale` expose the resulting algebra laws.

The individual-row interface is central:

```text
Monomial.individual_rows_to_span:
  (∀ r, monomial G x (M r) = G.one) →
  ∀ z, monomial G x (rowMul z M) = G.one.
```

Its proof goes through `Rows.rowMul_linear_combination`, `Hom.map_zsmul`, and
`Finite.map_sum`. Every integer coefficient, including every negative
coefficient, is handled there. The universal abstract factorization lemma has
an annihilation hypothesis, but the concrete theorem supplies that hypothesis
from the **individual** rows by this bridge. It is not an extra certificate
assumption.

`Monomial.substitution` proves the exact finite-product substitution identity
for arbitrary integer matrices. Define

```text
parameters G Q x j       = monomial G x (Q j)
realization G P theta i  = monomial G theta (P i).
```

The main interfaces in `MonomialBridge` are:

| Declaration | Conclusion |
|---|---|
| `reconstruction_all_exponents` | `x^v = theta^(vP)` for every integer exponent row, under the individual relations. |
| `reconstruct_coordinate` / `reconstruction` | `x_i = theta^(P_i)`, respectively equality of tuples. |
| `converse_relations` | Every arbitrary parameter tuple produces a solution, using `MP=0`. |
| `parameters_recover` | Applying the Q monomials to a realization recovers the arbitrary tuple, using `QP=I`. |
| `parameters_unique` / `unique_parameterization` | Every tuple realizing a solution equals its Q-defined tuple. |
| `residual_exponent_formula` | The coordinate ratio equals `x^(e_i-(PQ)_i)`. |
| `residual_relations_formula` | That ratio equals the literal product `∏r (x^(M_r))^(W_ir)`. |
| `residual_eq_one` | Under the individual relations, the ratio equals one. |

The first residual formula does not need the certificate identities; the
second uses the residual identity, and the last uses the relation hypotheses.
These formulas provide the requested chain without root extraction or a
characteristic/divisibility assumption. There is no supplied Lean field API,
`Units` adapter, or Laurent-scheme construction. Applying this interface to a
particular field's nonzero elements still requires that ordinary group adapter.

## 4. Remaining application boundaries

The universal source and synthetic fixtures passed the exact local kernel
replay. The observed dependency union is `propext` and `Quot.sound`;
`Classical.choice` remains permitted by the unchanged parser but was not observed.
The three intended false-`decide` controls also failed at their specified
propositions. See `REPLAY.json` for actual outputs and source hashes.

Not included: geometric generation and coverage; actual P112/P120/E8 matrices
and W witnesses; matrix certificates from the audit; field/unit and scheme
adapters; the nonzero-field-element premise; a rank API; local Lemma 5; decoder K;
and all all-size, precision, tape, analytic, hosting, and integer-multiplication
consequences. A specific E8 application must supply and check its actual
`MatrixIdentities` term and any field adapter separately. This package cannot
supply the remaining geometric generator-to-relation bridge merely by proving
its conditional algebraic implication.

## 5. Conditional certificate boundary

The 20 matrix-conditional public declarations in `MatrixBridge` and
`MonomialBridge` each have an explicit `(h : MatrixIdentities M P Q W)` binder.
`Lattice`, `lattice_iff_integer_span`, `row_torsion_free`, and
`residual_exponent_formula` remain certificate-independent. The explicit
ordinary group laws and the three matrix identities are legitimate hypotheses,
not hidden conclusion fields. No custom axiom declaration is introduced.

The source statement is PR1497 `audit.md` sections 8.2-8.3 at commit
`7a1309f18f56d04c2db33bf1607e0332d19f72b3`; its exact bytes were checked locally.
The producer worked from the supplied statement. See `SOURCES.json` for the Git
blob and SHA256, and `README.md` for predecessor and substantial AI attribution.
