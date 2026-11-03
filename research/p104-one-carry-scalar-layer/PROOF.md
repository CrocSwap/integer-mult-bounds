# Reused ADD mechanism and source binding

Each record is a signed W-bit integer. For an ADD coefficient n/2^k, require the source to be divisible by 2^k and the exact endpoint to fit its signed record. The source may be written during the scalar macro, but must be restored before any other event observes it.

The pinned PR3152 circuit expands the coefficient into signed powers. Each positive power uses distinct source and target bit windows. For a negative power, the known zero low source bits are filled from its sign, used as the wrapped high sign-extension bits, and then cleared by the inverse fill. This avoids extra sign-copy storage. Its MAJ/UMA circuit keeps the running carry in source bits, then restores them in reverse order. The one initially zero carry returns to zero. Reversing the gate list implements subtraction. These are retained PR3081/3152 results.

The independent source-grid replay starts every public component and native return as 32 times a distinct integer atom. Every exact source coefficient division is checked. Thus all actual ADD and SCALE alignments hold for arbitrary returned grid values. No dirty public source is assumed zero. The strict numerical range premise remains the separately proved PR6499 interface; it is not inferred from random fixtures.

# Paired SCALE and known zero bits

For two arbitrary encoded components x,y, the four modular shears

`x+=y; y-=2*x; x+=y; y-=2*x`

return (-x,-y). Direct substitution proves this identity in every ring. PR3159 supplied its one-carry implementation and paired-owner contract. Intermediate wrap modulo 2^W is permitted. No third dirty bank is needed.

For a negative coefficient -2^k with k>0, shift both records first. Their low k bits are zero. Negate only the high W-k bit pair. For k<0, source alignment already gives -k zero low bits; negate the high pair first, then shift right. For k=0, use the full pair. The ignored low bits stay zero, and the strict signed-range premise makes each high-word negation exact. The four-shear identity remains valid modulo the smaller high-word modulus.

Each shift uses the frozen PR6506 direct cycle rotation and sign-fill circuit. The cycle decomposition reduces an arbitrary fixed shift in one pass through the bit permutation, instead of repeating a one-bit shift. The source helper is retained byte-exact and authenticated before import. Positive SCALE consists only of the paired shifts. The checker covers widths with different rotation cycle lengths and both signs.

COPY consists of component-wise CNOTs into the declared zero owned destination. INIT and CLEAR are W reset requests per component. Their physical realization is not supplied. In particular, numerical residuals are not erased by an uncharged reversible identity.

# Complete accounting and validation

Each selected ADD runs twice, once per real component. Each selected SCALE runs once on its component pair. COPY runs twice, and both reset events in each of the 31 owned lifetimes are charged. All gate counts come from actual emitted lists. The comparator is the exact PR6506 source; ORIGINS.json identifies its source commit and byte hash. Both bills use the same selected word, width and reset convention.

All scalar circuits return the single clean carry before the next event. The field source is restored after each ADD. SCALE needs only the real/imaginary target pair. This removes the larger carry bank at the logical interface; it does not make paired access or source writes physically free.

The full-word fixtures execute every circuit gate and compare each source event with a separate rational trace. Native calls supply independent coarse-grid values, so these fixtures test the scalar contract rather than physical native operators. Small exhaustive packed truth columns check all actual coefficients, output components, source return, carry return and literal inverses. The supported emitted widths are 26 through 256; no unbounded-width compiler or full multiplication theorem is claimed.
