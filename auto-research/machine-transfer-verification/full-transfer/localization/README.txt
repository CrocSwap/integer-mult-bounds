Eligible-prime localization of finite rational address tables
============================================================

This package closes the generic algebraic interface between rational matrix
identities and the modular projector equations used by AddressGauges. It uses
the genuine coefficient ring

  Coeff D = Localization.Away (D : Z), namely Z[1/D].

There is no map from all of Q to a finite-characteristic ring. Instead, a
proved injective rationalView maps Z[1/D] into Q when D>0, and reduction maps
Z[1/D] into a commutative ring K only when D is a unit in K.

Finite preparation and exceptional primes
-----------------------------------------

For an arbitrary finite rational coefficient table values : iota -> Q,
denominatorProduct is the product of its positive entry denominators. The
noncomputable liftTable constructs an element of Z[1/D] for every entry, and
liftTable_exact proves that rationalView recovers the original rational.
The table can contain all matrix entries, inverse matrix entries, and
reciprocals of selected nonzero Gram determinants and pivot minors.

reciprocal_numerator_divides_product proves that including a reciprocal also
includes the original rational's nonzero numerator, up to sign, in D. Thus
avoiding D accounts for both denominator and nonzero-minor exceptions; merely
avoiding the original matrix entry denominators would not suffice.

exists_eligible_odd_prime proves that an odd prime p coprime to D exists.
eligible_prime_power proves D is a unit in ZMod(p^f) for every natural f.
The same p works for every block width f. Neither the reduction theorem nor
the address-gauge theorem treats ZMod(p^f) as a field.

Matrix identities and prescribed patterns
-----------------------------------------

LocalizedMatrixTransfer first reflects an equality checked over Q back into
Z[1/D] using rationalView_injective, then applies the reduction homomorphism.
Consequently its premises are rational identities, not assumed reduced ones.
The proved operations and consequences include:

* P*P=P and both nested absorption equations small*large=large*small=small;
* complements, differences, Kronecker tensor products, zero entries and lower
  triangular zero patterns;
* exact three-factor decompositions and the same integral middle pattern;
* stored two-sided inverses of basis/conjugating factors;
* unit determinants for stored Gram/pivot square minors, obtained from their
  nonzero rational determinant and the localized table of their exact inverse;
* scalar unit pivots from the table entries for a nonzero rational and its
  reciprocal.

The nonsingular-minor theorem concerns units over the target ring. It does
not misuse field rank for a prime-power residue ring. Profile realization
still requires the finite tables to have the specified ordered factorization,
triangular patterns, and unit pivot witnesses; these are rational checks that
the theorem transfers exactly.

Direct semantic bridge
----------------------

LocalizedAddressGauges.primePowerGauge constructs an actual partial-swap gauge
on pairs of ZMod(p^f) coordinate vectors from a localized projector, its
rational idempotence proof, and gcd(D,p)=1. It derives the modular idempotence
internally. primePowerGauge_involution proves its inverse law.
primePower_nested_transport similarly derives the modular nested transport
law from rational absorption. Callers do not supply a reduced matrix identity.

Scope and remaining work
------------------------

There are 31 new audited theorems: 11 coefficient/eligibility, 17 matrix-table
transfer, and 3 direct address-gauge results. The fresh build also audits the
50 selected declarations of the unchanged DirtyWrapper, FramedXor and
AddressGauges dependencies. All reported dependencies are only propext,
Classical.choice and Quot.sound, or a subset. There are no custom axioms,
admitted proofs, native_decide or reduced-identity assumptions.

This is an exact generic finite-table interface. It does not construct or
serialize the complete selected circuit's rational basis, Gram inverses,
factorizations, common D or a concrete prime. It does not prove that existing
large-prime CRT checkers happened to use an eligible prime for those as-yet
unassembled tables. Finite rational preparation/verification, complete trace
instantiation, tape costs and the global multiplication theorem remain separate.

The interface matches notes/endpoint-gauge-construction.tex and
notes/batched-algorithms.tex: rational bases and factorizations are fixed before
the address prime is selected, and all denominators and nonzero pivots must be
protected. Mathlib's pinned localization, matrix and ZMod implementations are
the formal authority used by these proofs.

Reproduce
---------

Use an existing project pinned to Lean4.21.0 and Mathlib commit
308445d7985027f538e281e18df29ca16ede2ba3, with dependencies built and matching
Lean/Lake on PATH. From the mission directory:

  python3 outputs/full-transfer/localization/check.py \
    --lake-project work/agents/lean-foundations/formal/lean

--framed-dir overrides the unchanged address-gauge dependency bundle;
--output selects an isolated build/log directory. No source, project or
dependency is modified and nothing is installed. --check-sources-only verifies
pins, hashes and declaration/audit coverage without compiling.

Theorem and dependency hashes are in theorem-manifest.json. The fresh
verification/ directory contains six module logs and axiom-audit.json.
declaration-scope-map.json records the exact proved statement of each new
theorem and the remaining external obligations.
