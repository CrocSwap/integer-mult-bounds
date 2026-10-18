# Equivalence of the gated packed-kernel substitution

The domain is exactly n=9, nine integer row masks in [0,512), and (for D)
nine integer linear coefficients in [0,4). The wrapper checks this domain.
It snapshots mutable gate lists into value tuples on each call. Original P
bijection checking remains after table construction; malformed/singular input
is never silently accepted as a valid permutation. No claim of identical
exception behavior for arbitrary out-of-domain Python objects is made.

For P, let x=y xor 2^j where 2^j is x's lowest set bit. Each output row is a
linear F2 functional, so Gx=Gy xor G(2^j). The credited recurrence starts at
G0=0 and constructs exactly the original sum of row parities. Induction on x
proves equality of all 512 entries. This is the existing PR662 argument,
restated only to justify its integration into the different packed kernel.

For D, the original scalar exponent is
q(x)=sum_i a_i*x_i+2*sum_{i<j} Q_ij*x_i*x_j modulo4. Removing the lowest set
bit i leaves only larger indexed set bits in y. Therefore
q(x)=q(y)+a_i+2*parity(Q_i & y) modulo4, exactly the credited recurrence.
Diagonal and lower-triangle Q bits are irrelevant in both expressions. Again
induction proves equality of all512 entries. A PH gate is not redirected.

Both tables are immutable tuples keyed by the complete dimension and gate
contents. No gate object identity, source identity alone, input state, packed
radix or operator output is cached. A changed coefficient changes the key;
eviction recomputes the same pure function. Since the cache only substitutes
exact table values, its capacity and eviction order affect cost only.

For each admitted P/D gate, replacing its table by an equal table leaves every
real/imaginary packed row unchanged. The surrounding loops, other gate
branches, allocations and arithmetic are byte-identical modulo the three
listed source edits. Induction over the circuit gives identical output pairs
for every beta and every admitted circuit, with the original C-count/radix
comparison retained. No projective equality, floating arithmetic, digit
truncation or column sampling is introduced.

The executable audit independently compares all actual table entries to the
unchanged scalar formulas while running every original record check and
control. Its 5,140 P and3,721 D keys include the native calibration and mutation
paths, not merely accepted certificate records. The full baseline/candidate
runs additionally reproduce identical result and receipt bytes. These finite
checks bind this integration; they do not prove the retained source's entire
mathematical theorem or substitute for its existing sound-radix argument.

The source gate is part of the contract. All14 captured runtime byte strings
must match SOURCES before any predecessor code is compiled. Only those captured
bytes are written into the disposable replay tree, so later checkout edits
cannot alter this run. Exact-anchor uniqueness prevents applying the transform
to a drifted source. The new companion record authenticates the transformed
kernel and adapter separately because the unchanged legacy header identifies
only the original retained source. Trust in the adapter, interpreter and source
pins remains ordinary code-review trust, not a signed attestation.
