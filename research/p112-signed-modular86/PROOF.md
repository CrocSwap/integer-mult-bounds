# Why one modulus recovers the exact signed determinant

Let A be a square integer matrix of dimension n<=8 whose actual rows satisfy
sum_j A_ij^2<=4. The determinant's absolute value is the volume of the row
parallelotope. Successive orthogonal projection cannot increase a row's norm,
so the product of the orthogonalized lengths is at most the product of the
original lengths. Hence |det A|<=2^n<=256, including singular matrices. Column
selection from the predecessor's doubled E8 root rows preserves the squared-norm
bound, but the kernel checks it rather than relying on that provenance alone.

521 is prime: it has no divisor from2 through22, and23^2>521. Ordinary elimination
over F521 multiplies the pivot values, flips the sign at each row exchange and
uses determinant-preserving row additions. Its final residue is det A modulo521.
Failure to find a pivot gives residue zero by the same elimination argument.

Two integers in [-256,256] differ by at most512. They cannot be congruent modulo521
unless equal. Therefore the balanced representative of the computed residue is
the unique possible determinant. The implementation checks that the recovered
representative stays within2^n. For residue zero the same uniqueness proves exact
singularity. This is a deterministic integer argument, not a probabilistic rank
heuristic.

The fast path requires square rows, n<=8, genuine Python integers, and the norm
bound for every row. Otherwise it calls the unchanged original rational routine.
Thus its replacement does not silently apply the finite bound to larger or
rational matrices. In particular [521] goes through the fallback and returns521;
unbounded modular zero would be unsound. The diagonal8x8 matrix2I has determinant
256, and one row swap gives-256. A modulus257 would conflate256 with-1, explaining
why the recovery guard requires a modulus strictly larger than twice the bound.

The finite certificate audit still checks every signed determinant against the
supplied integer, then all support, repair, rank and case obligations. Speeding
this internal computation neither changes the free-sink model nor strengthens
its original mathematical conclusion. The signed-matrix census is a control on
the implementation; the all-input exactness claim within the envelope follows
from the argument above, not extrapolation from the census.
