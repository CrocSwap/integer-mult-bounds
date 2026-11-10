# Physical completion of the ordinary wrapper

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I compose the fixed-role reversed caller from PR2809 with Nick Petalas's
PR2808 wrapper. I retain David Arias's PR2753 endpoint and p=1 cost argument,
the selected source vocabulary, and the earlier ordinary borrowing proof.
I add encoded setup, numerical-template initialization, two-call ownership
and physical erasure. I do not claim a new borrowing identity or exponent.

## Statement and source boundary

Fix a source-admissible prime q>2^80 and the pinned selected vocabulary. Put
c=17/10000 and a=c(1-c)=169711/10^8. I use the completed p=1 caller C0 from
PR2753/2809, with its written endpoint, chronology, source-refinement and
uniform charge arguments. These are explicit mathematical dependencies,
not consequences of this package's small tests.

On a complete stream `[P][q^e][G][q^e][S]`, e>=1 and P,G,S>=1, I construct
the ordinary interchange with unchanged borrowed input, a distinct owned
output, pointwise spectator restoration and empty owned work at return.
I obtain O_q(V e^(1-a)) time and O_q(V)+F_q space on a fixed tape inventory,
where V=P G S q^(2e). I include the source's finite compilation charge F_q.
The binary completion has O_q(V E^(1-a)) time at positive binary width E.

I prove successful execution on admitted canonical inputs. I do not promise
transactional recovery after an interruption or a failing internal macro.
The wrapper's stronger arbitrary-exception API therefore remains outside
this composition statement. I retain the selected GL64 compilation argument;
I have not materialized its entire finite instruction word or a microtransition
table. I make no supplier-admission or multiplication-exponent claim.

I receive the borrowed payload and canonical parameter tapes on external ports,
outside the owned work inventory. The caller consumes each returned output
before reusing that output port. I preserve the caller's other state on disjoint
roles; I require no external fresh-row factor.

## 1. Keep the recursion levels separate

I retain the elementary digit interchange A0 inside C0. I define B1 by applying
the ordinary wrapper to that sealed C0. C0 never calls B1. A later caller C1
may use the completed B1 only after this construction; I do not implement C1
here. This order avoids assuming the faster ordinary primitive during its own
construction.

I use C0's unweighted endpoint

    F_I(H,D) = (C_n D,C_n H),

where C_n reverses the n atom positions. An arbitrary weighted involution
does not satisfy the same two-call wrapper identity. I encode unit weight 1
in the initial ROOT record, with depth 0 and no STEP records.

## 2. Compute the parameters on tapes

I keep e on its original canonical Count tape and compute

    w = min { j>=1 : j^10000 >= e^17 },
    D(e) = 0 for e<64; D(e)=1+D(42 floor(e/64)) otherwise,
    K(w) = 269241600 |GL_64(F_q)| q^(4096(w-1)),
    stock = K(w)^D(e),
    k = min { j>=0 : q^j >= stock }, R=q^k.

I find w by binary bisection using Count comparison, addition and division by
two. Fixed-power multiplication may saturate at e^17: min(xy,T) preserves the
predicate needed for each comparison. I store no numerical result in finite
control. The exponents 17 and 10000, q and the finite source dimensions are
compiled constants. I compute D by its encoded contraction loop and form
stock through encoded multiplication and a countdown of D levels.

I use the elementary branch if 2k>=e. Otherwise I compute

    (n,ell) = divmod(e-k,w),

and also use the elementary branch when n<64. The fitted branch therefore
satisfies e=k+nw+ell, 0<=ell<w, n>=64 and stock<=R. I choose w and stock from
the original e before removing any borrowed digits. I never substitute D(n)
for D(e) in setup.

The retained sharp-fit proof in `research/bit2234-stock-threshold` gives
2k<e for e>=311311 for this exact K and every permitted prime. Since
w<=2e^c, I also have n>e^(1-c)/4-1. At that cutoff this exceeds 64, using
c<1/2 and 311311>260^2. Thus only finitely many widths use the elementary
branch. I reuse this predecessor theorem; I do not claim its cutoff or stock
coefficient as a new result.

All new setup integers have O_q(e+log(PGS)+1) bits. In particular,
log_q(stock)=O(w log e)=O(e). Schoolbook binary Count arithmetic, fixed-power
bisection, and the encoded loops take a fixed polynomial in 1+log V; a fourth
power suffices for this implementation. I absorb that polynomial into O_q(V),
since its ratio to V has a finite supremum for V>=1. I retain a fixed number
of integer tapes rather than a tape per loop iteration.

## 3. Initialize the actual numerical contexts

I allocate fixed register roles before reading numerical widths. PhysicalArena
has no `bits` attribute. It supplies the retained Arena operations with a
preallocated free map and sequential PhysicalWord views.

For a positive canonical maximum M, I scan its binary digits and write one
zero per digit, one additional zero margin and RIGHT to the permanent template.
I copy values into slots through that template. For the internal body I use
M=q^w; for its index bank I use n. The resulting extents are

    L=bitlength(q^w)+1, I=bitlength(n)+1.

I keep these templates throughout the coarse recursion, including unit
resets. I use separate fixed banks for q^k and, when ell>0, q^ell. I omit the
remainder Ring when ell=0. The elementary branch instead initializes its
modulus from q^e. No decoded length enters Arena construction.

I emit the ROOT record with append_word(n), append_word(1), append_word(0)
and RECORD_END. I do not use Program.fixture or Arena.input at runtime.
The small dimension-2 fixture needs an explicit index floor for the retained
Geometry constructor's literal 64. I exclude that fixture exception from the
selected statement: in production n>=64 already supplies the required extent.

## 4. Bind the exact wrapper order

Write J=q^ell. I use PR2808's input order

    [P][H_hi:R][H_body:(q^w)^n][H_rem:J][G]
       [D_hi:R][D_body:(q^w)^n][D_rem:J][S].

I preserve the predecessor's remainder exchange and chronological body word:

    D-=H; F_I; D+=H; F_I; D=-D; D+=H.

The body states are (H,D-H), (C(D-H),CH), (C(D-H),CD), (D,D-H),
(D,H-D), (D,H). I then exchange the two original high fields. This proves
the complete ordinary endpoint with each original spectator fixed.

For each F_I, I pass the following actual C0 arguments:

    old_count=P, depth=0, old_directory=empty,
    fresh_rows=ceil(R/stock)*stock, before=1,
    gap=J*G*R, suffix=J*S, body_size=n.

The R in the gap is the genuine D_hi extent. I do not replace it by the padded
row count. The empty directory represents P distinct empty frozen tuples;
old_count retains their multiplicity. I do not collapse P to one.

I preserve PR2786's literal row padding and restriction. From stock<=R I get
R<=R'<2R. Since n<=e, D(n)<=D(e), so R' is a compatible positive multiple of
K(w)^D(n). C0 restores each row ordinal. I restrict after each completed F_I,
before the next arithmetic step on the original ring. Both calls reuse the
same row stock; I do not multiply sequential reserves.

## 5. Preserve ownership across the physical calls

I keep the outer Counts, rings and payloads outside the C0 banks and pool.
At the callee boundary I expose a borrowed physical view of each outer lease.
This is necessary because Machine.commit consumes Lease results; passing the
outer Lease object as a root input would transfer ownership incorrectly.

The outer invocation owns the initialized C0 markers and templates. After
each successful F_I I require empty canonical bodies, empty numerical live
sets, no scratch leases and the initial parking state. I retain the templates
as borrowed session workspace. Padding consumes and clears the protected
output before the second call. At the end I erase the session markers,
templates, parking port and the now-consumed protected output marker.

I suspend the outer allocation-site specialization while C0 runs, preserving
the outer leases and the prohibition on new physical Tape/Arena construction.
The inner pool then specializes the authenticated source sites for its own
roles. I restore the outer factories on return. I specialize only padding's
allocation function, retaining its nominal Tape checks for returned outputs.

At final transfer I erase the source cells and release the emptied lease.
I reinitialize erased markers by explicit local writes before a later call.
The output must have been consumed before reuse. I retain slot identities,
and I may rebuild different template extents on the same physical roles.

## 6. Charge the complete ordinary invocation

PR2808 charges 3n ADDs, n sign passes, k+ell elementary digit passes, two
complete F_I calls and two padding/restriction bills. I retain its intermediate
output-disposal scans. Unit ordered ADD costs O_q(V): I charge its polynomial
coefficient arithmetic against the complete q^w target fibre. Sign has the
retained linear scan bound. Thus the added body arithmetic costs O_q(nV).

The padding planner costs O(R+stock), including its countdown resets; R and
stock are at most V on the fitted domain. Padding, restriction, output copies,
lease disposal and initialization/erasure contribute O_q(V) in total. The
complete C0 bound from the retained moment argument is

    T_C0(n,w)/V <= C_q (n+n^(1-c)w).

After the below-two padding factor and two calls, I obtain

    T_B1(e)/V = O_q(n+n^(1-c)w+k+w).

Now n<=e/w, e^c<=w<=2e^c, and k=O(w log e). Therefore

    n <= e^(1-c),
    n^(1-c)w <= 2^c e^(1-c+c^2),
    k+w = O(e^c(1+log e)) = O(e^(1-c+c^2)).

I get the retained saving a=c(1-c). The finite elementary fallback widths fit
the same bound after increasing C_q. I do not use timings as evidence for it.

Outside C0, I retain only a fixed number of input-sized payloads, padded
payloads of volume below 2V, and O_q(log V) setup/template cells. During C0 I
add its O_q(V')+F_q reserve to the retained outer data. I therefore obtain
O_q(V)+F_q space. Register counts, stream roles and the instruction vocabulary
depend on q and the selected source, not on e or recursion depth.

For the explicit outer pool, I bound setup by 64 simultaneous Count/Counter
roles: fixed_power retains two accumulators, Count.product adds three roles
and one addition copy, and bisection/select retain fewer than twenty other
operands. Iterations release their predecessors before advancing. During the
wrapper I retain fewer than 64 outer roles, including the seven plan Counts,
prepared extents/program, PR2808's thirteen Counts at a call, and payloads.
The reached nonrecursive primitives are a subset of PR2809's completed blocks,
whose conservative bound is q^2+128 scratch roles. Thus q^2+256 outer roles
suffice. C0 uses its separate unchanged pool. Binary padding retains fewer
than 32 Count/Counter/payload roles, within its fixed allowance of 96.

I exclude the explicit observer counters, provenance maps and test callbacks
from machine state and cost. Production uses no observer callback; those
observations neither select instructions nor supply numerical operands.

## 7. Complete the binary interface

For E>=1, I construct B=2^E and the least e with Q=q^e>=B by encoded loops.
Then B<=Q<qB and e<=E. I pad the first field with prefix P and body G*B*S;
I pad the second with prefix P*Q*G and body S. This gives `[P][Q][G][Q][S]`
with volume below q^2 V, without padding any spectator region.

I invoke the completed radix-q B1 once, then restrict the second field and
the first field in reverse order. The genuine B-by-B rectangle is invariant
under the ordinary interchange. At the completed endpoint the dummy cells
again contain zero, so restriction loses no input. I close padding before
return and erase the consumed native output marker.

The four scans and encoded setup cost O_q(V); the native call costs
O_q(V E^(1-a)). I preserve the fixed inventory, arbitrary complete spectators
and O_q(V)+F_q space. At E=0 I return an owned identity copy and erase unused
workspace. This is a completion of the retained rectangular-padding method,
not a new reduction.

## 8. Evidence and remaining successor obligation

The finite engine checks use a dimension-2, q=2 grammar and explicit interface
parameters. They do not execute the selected GL64 payload or the fitted
large-prime domain. I check a separate affine provenance mask for every input
column while physical payload cells remain Boolean. These masks are checker
state, not machine workspace or an enlarged runtime alphabet.

The binary rectangle checks use completed elementary native backends at
q=2,3,5; they test the adapter, not the faster all-size rate. The written
composition above supplies the quantified statement subject to its named
source arguments. I claim no independent human or proof-assistant review.

commdata2338's PR2399 still requires source binding for the successor's header
route. PR2753's current route decorates and sorts high keys; it does not call
the older ordinary_fields hook. A leaf-only substitution leaves O(wV) routing.
The completed B1 is a predecessor for that work, not its replacement. The
complex supplier, selected bootstrap-stage adoption and analytic transfer
remain separate.
