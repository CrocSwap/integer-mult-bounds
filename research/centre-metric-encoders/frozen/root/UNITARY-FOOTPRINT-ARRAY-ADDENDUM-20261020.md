# The coordinate bound also covers array encodings

This note extends UNITARY-CENTRE-FOOTPRINT-20261020.md. It does not
change that frozen proof or its scalar-code checks.

Let each of the 112 port fields have N complex entries. The entries
can include the owner and payload indices. Let V be the pinned
sixteen-row centre matrix. The corresponding full reader is
V tensor I_N.

In real coordinates, its rank modulo 3 is 32N and the rank of its
Gram matrix modulo 3 is 16N. The same radical argument therefore
requires at least

```text
48N real output coordinates, or 24N complex output coordinates.
```

Consequently, at least 24 output arrays of size N are required.
This conclusion permits an arbitrary Gaussian dyadic unitary
encoder that mixes ports, spatial entries, and owner indices.
It is not limited to a scalar 112-by-112 port matrix. Additional
arbitrary borrowed entries do not change the bound.

The statement counts coordinates. If output arrays have different
sizes, the lower bound applies to their total size; it is not a
lower bound of 24 names or registers of unrestricted size.

## Change of physical frame

Let A be the real form of V tensor I_N. Let U be any dyadic
orthogonal input-frame map. Let L be any dyadic output-frame map
whose inverse is also dyadic. For the transformed reader

```text
A_physical = L A U,
```

the rank of A_physical modulo 3 remains 32N. Its Gram matrix is

```text
A_physical A_physical^T = L (A A^T) L^T.
```

Its Gram rank modulo 3 therefore remains 16N. The same coordinate
bound applies. In complex form the corresponding hypothesis is a
Gaussian dyadic unitary input map. The output map and its inverse
must both be Gaussian dyadic.

In particular, a routed unitary phase or a monomial owner view on
the input does not remove the coordinate obstruction. This
statement applies to the actual physical centre reader whenever
its pinned frame maps satisfy these hypotheses. It is not a
claim that every change of encoding or representation must be
unitary or dyadic.

## Proof for arbitrary recovery

The bound does not require the recovery routine to be declared
linear. Let the unitary code be C and let y=Cx. Every y is a
possible output because all inputs, including borrowed inputs,
are arbitrary. The required centre values are A C* y.
If those values depend only on a selected coordinate set, every
column of A C* outside that set must be zero. Otherwise changing
only that output coordinate would change a required centre.
Thus exact recovery already gives the row-support premise used
in the finite-field proof.

All steps are finite-dimensional identities. The result applies
separately at every finite N. It gives no native-gate, map-call,
rounding, or total supplier-cost lower bound. The implemented
24-coordinate port code attains this information bound
entrywise; a legal complete native supplier still needs its
separate phase, access, restoration, and recursion proofs.
