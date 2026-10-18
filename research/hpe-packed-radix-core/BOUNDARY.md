# Exact theorem and source boundary

`Packed.packed_compare_sound` quantifies over natural C counts k1,k2,K with
k1<=K and k2<=K, and a finite list of corresponding Gaussian-integer entries.
Each entry has a `ColumnEntry` witness: it occurs in the output of a PR2499
`HPEEnergy.Run` on an input of energy one. These witnesses may use different
runs and dimensions; the coefficient-bound proof needs only their energy.
The theorem does not assert that the list came from one common circuit.

Put B=2^(K+2), s1=2^(K-k1), s2=2^(K-k2). If the two Gaussian packed row sums,
multiplied by s1 and s2, agree, then every corresponding scaled entry agrees.
The premise compares both real and imaginary components. The paired list
provides an explicit common finite arity; no truncating zip is in the theorem.

The imported `column_squared_bound` gives each component square<=4^k.
`square_bound` and `four_two` imply absolute component<=2^k. Scaling puts
both sides in [-2^K,2^K], so difference digits have absolute value<=2^(K+1)<B.
`pack_zero` peels signed digits modulo B. `gaussian_zero` handles the two
components separately. `pack_combo` proves the required finite linearity,
so the premise is the actual scaled packed equality, not an assumed zero
coefficient list. All these implications are kernel-checked in Lean4.34.1.

The external Python binding authenticates source files before import, executes
the unchanged PR1859 comparator with its existing controls, and observes all
3,072 literal basis-column outputs. It reconstructs every packed row from
those coefficients and compares 6,144 real/imaginary components against packed
execution. The actual three pairs have k1=9,k2=7,K=9 and scales1,4. Their
literal column energy and entry correspondence are finite Python evidence.
This observer uses the predecessor's compiler/executor; it is not a separately
implemented gate engine or a proof of Python semantics.

No theorem translates the retained Lean4.21/Mathlib `gz/runZ`, Python literal
parser, or source gate compiler into the standalone `Energy.Run` grammar.
PR2499's external gate-correspondence audit remains distinct and credited;
this package does not claim to kernel-check that translation. It neither
changes the retained checker nor proves its entire executable acceptance
predicate. Physical hosting, precision/tape and the multiplication theorem
are outside scope. The new result is the complete standalone comparator
implication that PR2499 left open after proving its energy ingredient.

The sharper K+1-bit threshold of PR1906/PR1934 uses whole-row energy and a
different Gaussian-kernel energy argument. Neither that sharp theorem nor
the required row-energy connection is formalized here. Column-entry bounds
are sufficient for this K+2-bit theorem and do not silently supply row energy.
