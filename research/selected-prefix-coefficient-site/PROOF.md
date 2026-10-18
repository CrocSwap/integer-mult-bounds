# Raw-prefix refinement at the selected coefficient boundary

We connect three existing interfaces: PR2234's selected raw-header producer,
PR2332's generated-weight table binding, and PR2364's completed stream
operations. We add a canonical prefix decoder and serialize the generated
program and its continuation stacks. We retain the earlier normal-form
identities, control envelope and marked parking construction.

## 1. Quantified raw-header interpretation

Fix an odd prime q, w>=1, B=q^w, Q=q^(w-1), and an actual selected request
rho of dimension m=64 and rank r. Let P_rho be its source projector and
let B_rho be the retained image/kernel basis. Thus

    P_rho = B_rho E_r B_rho^-1.

Let sigma_rho be the request's owner chart, and put S=sigma_rho B_rho.
For a COPY request the payload already has the common header d, and
sigma_rho=I. Its source chart belongs to the preceding source alignment.
These are the source conventions in PR2234's provider; a same-rank label
cannot replace rho. All matrices in this section act over Z/B.

Keep the physical raw field g=g0+qG, for a fixed g0 in GL_m(F_q) and the
complete high cube G in [Q]^(m*m). We compute h=gS in control arithmetic.
For fixed representatives of S, define entrywise

    h0 = (g0 S) mod q,
    c = (g0 S-h0)/q mod Q,
    psi(G) = G(S mod Q)+c mod Q.

Then h=h0+q psi(G) modulo B. For w>1, S remains invertible modulo Q,
so psi is an affine bijection of the complete high cube, with inverse

    psi^-1(Y) = (Y-c)(S mod Q)^-1.

For w=1 the two high cubes are singletons. The identity also gives

    h E_r h^-1 = g sigma_rho P_rho sigma_rho^-1 g^-1.

We therefore prepare the intended selected projector while keeping the
payload field g fixed. We need no payload route through B_rho or S.
We do not assume that psi preserves lexicographic order.

## 2. Canonical prefix coordinates

The input specification lists frozen raw matrix fields in chronological
global slots. A slot records q,w, the exact request and its raw low class.
The specification also records the complete spectator factors between these
fields. Unit resets discard weight dependence, not physical coordinates or
slot numbers. The current fresh field occupies the next slot and is outside
the incoming-weight domain.

For each generated field, keep its m*m high entries as a lexicographic
mixed-radix counter of radix Q. A finite odometer increments the last entry,
resets it on overflow and carries left. Induction on the number of increments
gives the canonical lexicographic high matrix. Nested field loops give the
canonical chronological prefix. At w=1 each field has one state.

Keep these generated counters in a compact band. Keep unused-row, collapsed
body and arbitrary spectator counters on separate bands. A coefficient
request scans only the generated band and the local program. It must not
derive a field by division of a flattened address that contains arbitrary
spectators. The decoder copies the requested high digits, joins them to the
specified raw low class, and restores its local head.

This is an input representation contract, not a test on payload values.
We never infer a header from opaque payload bits. Nor may an external list
choose a different header order while retaining only the same prefix length.
For example, over Z/9, the two matrices

    [[1,1],[1,2]],  [[4,1],[1,2]]

have the same low matrix and rank-one label but first good pivots 2 and 5.
Interchanging their external header entries changes the weighted operator.
The canonical decoder fixes that association by construction.

## 3. Serialized local evaluation

Encode each generated step with its kind, source slot, parent/child extent,
rank, diagonal field and orientation. Encode natural numbers as finite binary
words with delimiters. A fixed alphabet suffices for words, records and local
origins. Read a program record by a sequential scan from its own delimiter;
restore the head after the read. No program scan includes a spectator band.

For fixed q, the selected requests and raw low classes form a finite source
vocabulary. A code denotes one exact pair, with q and w supplied by the common
context. We use equality of those codes after fixing this vocabulary, rather
than probabilistic equality of hashes. The decoder's schema records each
global slot's code and dimension on a separate delimited binary tape.

Evaluate the retained Good/Pair/unit grammar with separate marked pending
and value stacks. Pending records contain a finite operation tag and binary
operands. A root or unit step returns its constant. A Good step pushes a
multiply continuation and its parent request. A Pair pushes its quotient
continuation and two ordered bank requests. The bank index includes the
physical reversal when the selected pair lies in the tail bank.

Before reading a table, validate the original global slot against the exact
field specification. Decode that raw high field, prepare gS, and construct
the same full-ring pivot or terminal-diagonal/permutation page as PR2332.
Read the needed page, retain its bounded local operands, and erase the
numerical page. The incoming evaluator cannot request the current fresh
field or an unused-row coordinate. A unit returns without requesting dead
numerical preparation, while later steps retain their original slot numbers.
To reach a later live slot, the field head can cross earlier encoded fields;
the decoder ignores their symbols and charges those head movements.

Induction over the pending expression forest proves equality with the
PR2310 evaluator and PR2332's bound expression. Each push appends above the
current marker. Each pop scans back to that marker, restores the preceding
top, and erases its own record. Neither operation reads an absolute parking
address. Induction over evaluation steps proves empty pending/value stacks
and restored program/field heads on return. The marked-stack argument is the
existing PR1379 construction; we apply it to serialized continuation data.

Local empty work means marked-empty tapes. The caller supplies the local
origin markers and includes their fixed installation/removal cost when it
opens or closes those work roles. The finite tests preload that interface;
they count the subsequent symbol operations. After erasure, successive
evaluations can reuse the same finite list of tape roles. Constructor calls
in the Python simulator do not imply a depth-dependent tape inventory.

## 4. A complete selected coefficient site

Consider the selected good head slot, with i>k and column j in [f):

    H_(if+j) <- H_(if+j) + c H_(kf+j),
    c = ell_ik(gS) A_(if+j) / A_(kf+j).

The current preparation may read raw g. The two incoming A evaluations may
read only older frozen fields. For the first elimination column,
ell_i0=-P_i0/P_00; later coefficients use the retained chronological
elimination state. The denominator is a unit on the admitted good class.

Regroup the complete fields around these two atoms as

    frozen prefix x before x X x middle x Y x suffix.

For each canonical prefix state, prepare c, then traverse the complete
before/source/middle loops. For a source x, set t=c*x mod B. Copy the first
B-t target blocks to one sequential scratch stream and the remaining t
blocks to another. During the merge pass regenerate the same canonical
prefix and c, then copy the second part before the first. Preserve the
records within each suffix block. This maps Y to Y+cX and fixes the prefix
and spectators, for arbitrary correlated payloads. Erase split scratch and
numerical preparation, and restore the local heads.

For the inverse site, regenerate the same raw prefix and use -c. The two
passes compose to identity. No stored array indexed by all high matrices is
needed. In particular, a nontrivial psi does not authorize permuting raw
prefix rows: we compute c(gS) while visiting raw G in its own order.

The same substitution applies to the other good slots and to each fallback
shear with its own original-row permutation snapshot. Its validity follows
from pointwise coefficient equality. Induction over the fixed-low trace
therefore refines the complete selected residual, assuming its completed
child contracts. At a child, append the raw current field and its exact
FieldSpecification; keep the whole high packet. PR2364's embedded-field
interpretation then supplies the child view without moving records.
For f=1 the completed leaf implements each selected child of width at most
42. For general f retain the proper-child contract and its separate cost.
An all-leaf replacement would not establish the selected saving.

## 5. Local work and the uniform charge

Keep the original root coupling w=ceil(e^(17/10000)) and the retained global
depth bound h<=2 ceil(log2(max(2,e))). Fix q and the selected finite catalogue.
The generated band has O_q(hw) bits. Program records, continuations and local
operands have O_q(h(w+log(e+1))) bits. Request identities and low matrices
have fixed q-dependent sizes. The raw-to-prepared matrix multiplication and
bounded-dimensional modular preparation have the existing polynomial cost.

The sequential program and stack scans add polynomial local work already
within PR2310's conservative O_q(w^1800) allowance. We do not sharpen its
request count. Schoolbook arithmetic supplies the scalar lowering; finite
Python arithmetic timings are not transition counts. For w>=1,

    w^1800 / q^(w-1) <= 2^1800 * 1800!.

Each body target fibre contains B=q^w complete blocks. Recomputing the
coefficient on split and merge therefore contributes O_q(V), as do payload
copies and erasure. Generated counters use their own ripple-carry scans;
arbitrary spectator counters use separate complete traversals. Their resets
are charged to the blocks they precede. We do not scan an L-bit spectator
band on each coefficient request, which would introduce an uncontrolled
factor proportional to L/B.

The site has one bound C_q V, independent of high values, spectator sizes,
row multiplicity and parking origin. A selected residual contains O(n) such
slots, with O(Vw) fixed header work under the retained route contracts.
The resulting local toll is the existing C_q V(n+w), provided the caller
implements the stated canonical schema and the remaining selected macrosteps.

## 6. Scope of the result

We prove a raw-prefix and local-control refinement under the named producer,
stream and child contracts. We implement the canonical decoder, serialized
continuation operations and a joined selected head-coefficient site. We
separate source-bound selected fixtures from complete small stream domains.
We do not enumerate the GL64 high cube or execute the selected global
family/owner/XOR/COPY/ERASE interpreter. That caller must still instantiate
this interface at its actual physical fields and close its other work.

We retain credit for source527, commdata2338's normalizers, descriptor and
table binding, Ross Richardson's fallback algebra, rfu08's marked tapes,
and the selected supplier contributors. Jose Manuel (`jmbarrancoml`) prepared
this work with substantial OpenAI Codex assistance. Independent review and
formalization remain open; we claim no new multiplication exponent.
