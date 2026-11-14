# Literal direct-switch plan and optimistic complete budget

Base e54523517d0f03e58352e647c403a5af3e525a57.
Exact arithmetic predecessor: Nick Petalas #7504,
4eece58f5cebdb70a92d65447974f1c02383f60b. Formula/child closure are credited.

## Scope and proposed ABI

One fixed finite graph on14 tape roles. Five borrowed records encode h,s,a,j,x;
output is one separate owned Boolean; eight private roles hold an initial
height countdown, unary width, s,a,j,x,last-row and one temporary. All input
heads begin at first body cells with supplied LEFT guards. h is positive
canonical LSB-first binary terminated by blank. The other four numbers are
exactly h+1 LSB-first bits followed by blank (zero padding is part of this
explicit ABI). Their unused high bits are validated by mathematical domain
checks, not interpreted as signs. Inputs are preserved byte-for-byte.

The graph creates/retires its private guards on supplied blank disjoint
windows, constructs its own h+1-cell width guide, validates every domain,
follows at most h literal child steps and clears/returns all private and
borrowed roles on success. The owned output remains one bit at its original
owner/head. Current CRT offset production and serialization into this ABI
remain caller obligations. No ROM, runtime callback or host integer acts
inside the graph. A finite malformed encoding rejects; no infinite-stream
recognition or enclosing caller rollback is claimed.

## Complete optimistic bill before coding

With W=h+1, setup constructs the unary width using O(h log(h+1)) bit steps,
then reads/validates/copies O(h) bits. Every direct-query iteration uses a
constant number of complete W-cell comparisons, shifts, +/-1 steps and
head returns. At most h iterations give O(h^2) complete steps. Initial
private writes, final erasure and all returns are O(h). Eight fixed private
roles have O(h) total active bits; historical backing retains their full
visited spans. A conservative explicit constant will be proved from the
emitted loop bodies, not fitted to execution timings.

For Q queries at identical physical origins, the full proposed workload is

    T_produce/serialize + Q*C*(h+3)^2 + T_consume/retire,

with O(h) reusable private backing and inherited history retained. Repeated
point queries do not become free. No repeated workload or caller price is
assumed from the one-bit lemma.

For a supplied retained ROM, write its complete build cost as B and its
actual query/movement/restoration bill as sum R_q. Its workload is

    T_produce/serialize_ROM + B + sum R_q + T_dispose.

Direct queries improve this total only after the corresponding inequality
is established for the same actual query sequence. In the optimistic
resident/streaming ROM comparison, R_q may be constant and build is amortized;
then sufficiently many repeated queries can favor the ROM. All offsets at
h5,s17,j6 comprise544 bits: asking for all544 individually pays544 quadratic
point-query bills. No speedup over building and scanning those544 retained
bits is asserted. A single query avoids exponential-size table production,
which is the meaningful missing physical-predicate premise here, not a
complete-system asymptotic improvement.

Stop if the literal proof requires runtime host arithmetic or exceeds
O(h^2) steps/O(h) work; no larger caller integration or kappa claim.
