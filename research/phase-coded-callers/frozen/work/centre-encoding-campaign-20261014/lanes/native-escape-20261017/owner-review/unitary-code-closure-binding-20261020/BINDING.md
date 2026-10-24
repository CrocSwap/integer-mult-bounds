# Final binding of the corrected D25 closure proof

The corrected producer proof passes this review. Its representation
argument has no remaining gap within the stated scalar-code class.
Logical monomial closure requires f at least 2. Physical affine
closure and the Q-commutation criterion require f at least 3.
The result does not give a native decoder lower bound.

This binding preserves the standalone review freeze
`b3fc9ddc6fdc4cc6c2226b3b9fa101abdb21d22e50ceb3d6c9cefa9280062deb`.
The final producer pins are:

```text
CLOSURE.md
63c0deeb7e13b359ca410dfb085e1a89866aa87383d6bd1cec02cba688a4ce3e

check_closure.py
45d1e215c4dc6f7735deaed0d9df57cf3efa83a0bc4e354c43375187cbe7f01e

bound-normal/CHECKS.json
f1e418155b89f8add0f066c80da2ab3a1120e6d78f047753e7e0698daf506a3a
```

The checker imports only the frozen independent review module. It
imports no producer module. It compares all corrected producer
artifacts with their optimized copies. It then:

- Applies the four literal affine views, in order, to all 12,544
  three-column common inputs and compares their stored outputs.
- Reconstructs both nonzero Gaussian coefficients and both output
  tuples in each of the 896 monomial-obstruction witnesses.
- Matches all 896 character witnesses to the independent review,
  then computes each literal affine sign and complete nonzero
  commutator coefficient.
- Compares all eight exact route-support profiles.

## Cover lift and action convention

Let L map a spatial function g to

```text
(L g)(d,z) = g(d^-1 z).
```

The same d acts on every spatial column. This map is injective:
evaluation at the identity owner recovers g. For the stated owner
view, substitution gives

```text
M_(h,delta) Lg(d,z)
  = Lg(dh,z+d delta)
  = g(h^-1(d^-1 z+delta))
  = L(T_delta P_h g)(d,z).
```

Here `P_h g(x)=g(h^-1 x)` and `T_delta g(x)=g(x+delta)`.
These are exactly the function forms of the stated position
convention. No inverse order is changed.

A translation by the owner-dependent line d q_p gives
`g(d^-1 z+q_p)`. Therefore the intrinsic Q at that owner also
intertwines with the spatial Q_p. Scalar port matrices preserve
the lifted subspace. Spatial non-equality thus gives non-equality
on the declared arbitrary-input cover.

## Why a cover monomial would induce a spatial monomial

A covariant point basis function has one nonzero coordinate at
each owner. Its support has size |G|. These supports, including
the input-port label, are pairwise disjoint and partition the
full coordinate set.

A full-coordinate monomial is a weighted coordinate permutation
with all weights nonzero. It preserves support size. If it
preserves the covariant subspace, the image of one covariant
point basis function must be a union of complete fibers, each
with size |G|. Its support size is still |G|, so that union
contains exactly one fiber. The induced spatial operator sends
each basis vector to a nonzero multiple of one basis vector.
Its invertibility makes it monomial.

This is the needed justification for restriction to the covariant
subspace. Invariance alone would not justify a general statement
about monomiality on an arbitrary subspace.

The corrected coordinate row/column argument also passes. Two
paths in one p,k block give two outputs from one input basis
coordinate. If two terms instead lie in distinct input-port
blocks, each affine term is a bijection onto the entire output
fiber. Every output coordinate in that port has two input
coordinates. Either case contradicts full-coordinate monomiality.

## Verification and limits

Both commands return `PASS_CORRECTED_PRODUCER_BINDING`:

```text
python3 -B check_binding.py --out run-normal
python3 -O -B check_binding.py --out run-optimized
```

Their two JSON outputs are byte-identical. Source hashes are
checked again at the end. No frozen source is changed.

No native word, recursive host, implementation cost, precision
bound, or complete supplier is certified here. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
No PR, commit, push, or publication is authorized.
