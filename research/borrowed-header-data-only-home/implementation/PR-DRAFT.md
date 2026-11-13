# Borrow immutable Gamma6 headers for DATA-only permanent homes

The existing native HOME adapters put Gamma6||DATA into a common body, so
the body's extent includes the changing header length. Add a literal
fixed-rho wrapper whose HOME contains exactly V scientific DATA bits and
whose distinct supplied Gamma6 HEADER remains immutable. Embed the frozen
positive core unchanged, then check exact returned extent and retire every
private/head/guard before the same-owner B1 scatter.

Wrapper overhead is at most256(V+1), with64(V+1) added historical backing;
the actual core's full2^24(fV+E+1) time and2048(V+E+1) increment remain.
Both prior larger storage and borrowed header storage stay charged.
F_HOME=V is independent of E; total core cost still charges every header
bit. B1 bank delivery/reservation is separate.

Two complete f1/rho1 calls physically reuse the same6144-bit HOME and native
banks with two immutable headers supplied at entry (10/268 bits; cutoff
bit lengths1/130). The exact result is C^2's selected-axis swap. Normal and
optimized replays also check cutoff, short DATA, late nonintegrality,
returned-length mismatch and wrong/unfinished scatter. Test monitors are
identified separately from compiled protection.

Credit the frozen generic core and native/B1 predecessors. No Gamma6
producer, nine-Gamma root conversion, view packing, cutoff derivation,
all-MOVE/caller admission, faster nonleaf rate, assumption discharge or
new kappa is claimed. No remote publication performed by this worker.
