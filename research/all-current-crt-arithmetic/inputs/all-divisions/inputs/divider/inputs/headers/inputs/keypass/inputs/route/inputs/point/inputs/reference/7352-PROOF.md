# Uniform encoded inverse of the padded balanced CRT address-state map

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
This is a source-relative inverse construction, **no new kappa**.

## 1. Exact claim, full budget and dependencies

Use the physical padded axis encoding of CrocSwap/integer-mult-bounds#5353
and CrocSwap/integer-mult-bounds#7154. There are d >= 2 axes, d is a power
of two, widths h_i belong to {ell-1,ell}, ell >= 2, the moduli satisfy
2 <= s_i < 2^h_i and are pairwise coprime, and 0 <= x_i < 2^h_i. These
conditions imply h_i >= 2. The physical records, including their unary
widths, modulus bits, coordinate bits and delimiters, are already supplied.
The source head enters at one. Put

    A = sum_i h_i,  M = 2 + 3A + 4d,
    P_G = 1 + sum_(i in G) h_i,  P* = A+1.

The source has a retained backing of K_source >= M cells. Its inaccessible
historical tail after RIGHT can be nonblank and is preserved and charged.
Private backing enters clean. Each numerical invocation borrows the source
read-only; the enclosing endpoint evaluator owns source mutation.

**Theorem, relative to the pinned source contracts.** Binding
`inverse_frontend.bind(frontend)` and `inverse_producer` into the unchanged
published `endpoint.Endpoint` gives a fixed finite-symbol evaluator of the
complete inverse of the padded balanced CRT address-state map. `run()`
takes no node list, level, start, precision or runtime numerical parameter.
It enumerates decreasing balanced levels and increasing starts within each
level, reading the actual current source at each node. On the whole padded
rectangle both compositions with the pinned forward evaluator are identity.

Only coordinate bits change during an invocation. All other source bytes,
backing identity, backing length and the incoming head are preserved. The
invocation uses exactly 79 private roles, and every historical private cell
is blank with its head at one at successful completion. A fresh forward
invocation followed by a fresh inverse invocation has **158 retained private
histories**, not 79. Reusing one retired inventory for a second invocation
is not established here.

The complete source-operation bound is

    C_inv (M+2)^2 + 4096
      + sum_G [2^21(P_G+2)^4 + 2^16(P_G+2)^2 + 4096].       (1)

C_inv is a fixed input-independent control refinement constant, whose exact
value is not certified. The raw frontend/adapter reads, writes and unit
moves fit 2^19(M+2)^2; (1) adds numerical, entry and owner traffic. Section
6 proves O(A^4) source time and K_source + O(A^2) retained backing. Thus
A <= p gives an O(p^4) helper bill in this source model. No selected
application is charged this bill without a separately proved caller join.

### Exact changed and unchanged sources

`INPUT-PINS.json` records nine byte-exact exports by repository, commit,
Git blob and SHA256. The forward writer is unchanged from
CubeJerry/integer-mult-bounds commit
`532b60ac427f47191175aba2e1317db0f3508d51`,
`research/encoded-balanced-crt-endpoint/endpoint.py` (SHA256
`c24ae2c90d175d276120438809e7c7401b8a8c04dec139f1b7345e9778984ced`).
Its frontend is the unchanged CrocSwap/integer-mult-bounds#7154 source at
`cc35ecedce6f208d5056fab6d17c58555affc73c`. Its numerical, entry, owner,
word, record and canonicalization sources are pinned at the canonical base.

There are exactly two implementation seams, described in `SEAMS.json`.
The new frontend subclasses the pinned frontend, changes initial half-size
manufacture, and overrides the existing level-transition hook with unary
halving. Every other method is inherited unchanged. The inverse producer
is the original CrocSwap/integer-mult-bounds#5053 producer with two credit
comments and exactly one scientific line changed:

    updated = a.add(canonical, offset, modulus)
    updated = a.subtract(canonical, offset, modulus)

The verifier checks this replacement byte for byte. The already present,
proved modular-subtraction implementation is unchanged. The ninth export,
canonical `unconditional-batched-crt/check_batched_crt.py`, is a verifier
oracle only; none of its host geometry or numerical values enters runtime.

### Predecessors and scope of novelty

CrocSwap/integer-mult-bounds#4100 already gives the reverse-level,
subtractive balanced algebra. CrocSwap/integer-mult-bounds#4195 already
supplies a logical mixed-width forward/reverse caller on padded addresses.
CrocSwap/integer-mult-bounds#7152, pinned at
`66adbede4bd4ab603ba3e0a7f6708403905b753c`, supplies physical forward and
inverse complete source-state trees using compiled geometry and 127 roles.
CrocSwap/integer-mult-bounds#7154 supplies encoded forward node selection.
The published forward writer explicitly leaves this reverse encoded
schedule/subtractive consumer as its first open next question.

CrocSwap/integer-mult-bounds#4024 already has an encoded bidirectional
triangular payload converter. Its original-lower-coordinate format,
payload/router contract and padded extension are different. The inverse
consumer in CrocSwap/integer-mult-bounds#5095 uses that converter after
integer recovery. No first CRT inverse or first encoded inverse is claimed.
The raw compact macro S^-1 in CrocSwap/integer-mult-bounds#4169 is another
different interface; this package cannot be substituted for its invoice.

The new result is the exact encoded reverse join on the published forward
writer's same owned-source interface, including current-left reconstruction,
real precision changes, retired source commits and full history accounting.
It supplies no physical payload conversion, synchronized row schedule,
exceptional-key epoch, raw compact macro or selected outer caller.

## 2. One inverse node and the full padded permutation

Let G=[a,a+2H), with left child L and right child R. In the current source,
the pinned producer reconstructs k_L in [0,S_L), S_L=product_(i in L)s_i,
from the left coordinates. If any of those coordinates is invalid padding,
it uses k_L=0. Otherwise the defining congruences are

    k_L = x_i product_(a <= j < i)s_j  (mod s_i), i in L.  (2)

These are current transformed coordinates, not original mixed-radix
digits. The source reconstruction loop is unchanged. For each right axis
i, define Q_i=product_(a <= j < i)s_j and

    c_i = k_L Q_i^-1 mod s_i.

Pairwise coprimality gives the inverse. Every preceding right modulus is
included in Q_i, regardless of coordinate validity. The changed output is

    y_i = (x_i-c_i) mod s_i,  if x_i < s_i;
    y_i = x_i,               if x_i >= s_i.               (3)

For 0 <= u,v < s, the inherited `Arithmetic.subtract(u,v,s)` computes
u-v directly when u>=v, and (u+s)-v otherwise. In the second branch
u+s<2s<2^P_G, so the raw addition cannot overflow. Both branches return
the unique representative in [0,s). The second branch needs at most two
new numerical words at once, just as the old add-and-reduce branch. It
uses the same borrowed operands and returns their heads. The unchanged
producer frees these words and serializes its positive offset followed
by the new coordinate. No offset is negated in the stored offset field.

Because (3) is in [0,2^h_i), all bits above the declared destination width
are zero. The unchanged writer can therefore use exactly its existing
projection: skip the full P_G-bit offset, copy h_i updated bits, and reject
any nonzero high remainder. Invalid right padding is copied unchanged.

For fixed left coordinates, the forward and inverse node maps keep the
left child unchanged and apply inverse rotations to each valid right
coordinate, fixing its padded values. Their controls depend only on the
unchanged left child and moduli. Thus they are mutual inverses on the
entire padded product, even when the left child is invalid. Different
nodes of one level have disjoint support and controls, so commute.

Writing F_j for the complete forward level j, the forward endpoint is
F_k ... F_1, k=log2(d). Its inverse is F_1^-1 ... F_k^-1, executed by
levels k,k-1,...,1. This proves both composition identities once Sections
3-4 establish that the physical reverse caller uses these actual maps
in this order. It does not require the input to be in the all-valid box.

In particular, global invalidity does not make the whole inverse identity.
For moduli (2,3,5,7), widths (2,2,3,3), the input (1,3,1,1) maps under
the inverse to (1,3,1,5): an invalid left subtree disables its parent
offset, while the disjoint valid right-child node still acts. Conversely,
subtracting at forward rather than reverse levels is wrong: the forward
image (0,1,2,1) of (0,1,0,0) would return (0,1,0,1).

## 3. Encoded descending topology without a traversal list

The inherited `_shape` reads the actual stream and establishes d=2^k,
k>=1, by repeated exact unary halving. It leaves k ONE tokens on `depth`,
one ONE on `half`, and a unique STEP at the first axis on `axis`. All
heads are at one; the temporary `double` role is blank. These are actual
symbol streams, not decoded k, d or H.

The reverse constructor steps past the first depth token, then invokes
the *base* doubling method once for each remaining ONE. This produces
H=2^(k-1)=d/2 on `half`, sees RIGHT after exactly k-1 doublings, and
restores `depth` to one. At d=2 there are no doublings. No new tape or
iteration counter is acquired; the existing depth stream drives the work.

At the j-th processed level, the invariant is:

1. `half` contains H=2^(k-j) ONE tokens followed by RIGHT, at head one.
2. STEP marks the first axis of the current aligned group of 2H axes.
3. The inherited scanner's temporary VALUE, when present during a lease,
   marks exactly the next group start; there is no saved node list.
4. `depth` is on its j-th ONE token and the numerical bank is retired
   outside the single active lease.

The inherited `NodeEntry` consumes two passes over the encoded half-size,
copies the actual chosen source fields and derives its precision guide
from their actual unary widths. The same marker argument as the forward
frontend visits increasing group starts without host indices. On closing
a nonlast node, unchanged `_advance` moves STEP to the saved VALUE.

On closing the last node of a level, `_advance` consumes one depth token.
If it sees RIGHT, it retires all topology roles and ends the traversal.
Otherwise it calls the overridable `_double_half` hook. In this adapter
that compatibility hook performs **halving**: a finite parity flag emits
one ONE to `double` per pair of ONE tokens in `half`, checks an even
nonempty result, clears the old logical half word, copies the temporary
back, and clears the temporary. The inherited code then places STEP at
the first axis. H is at least two whenever this transition is needed.
Startup explicitly calls the base method, so cannot invoke this halving
hook accidentally. This proves the invariant and exactly d-1 nodes.

All accesses are local symbols, unit moves and fixed-role calls. The
subclass has no decoded precision, axis count, level or start and no
host sequence of nodes. The module factory fixes a provider class, not
runtime geometry. The inherited Python lease objects retain only the
current linear-use continuation; no unbounded stale-object history is
being compiled into constant space.

## 4. Current source, exact precision and retired writes

Every node uses the unchanged forward writer's full-source staging
protocol. While the lease is live, `stage` copies all source fields to
its separate role, replacing only the right coordinates by (3), and
returns the source, result, guide, axis and half heads. It does not write
the source. The lease then retires its numerical result, canonical input,
guide and guards, releases the physical bank, and advances topology.
Only after that close may `commit` copy the equal-length staged source
to the original backing and erase staging completely.

Source headers, widths, moduli, record delimiters and logical extent are
unchanged, so the encoded topology's invariant is preserved by commit.
The next `NodeEntry` rereads coordinates from that actual source; it
caches neither old digits nor an earlier reconstructed left integer.
This applies after undoing the root as well as between lower nodes. The
last lease may clear all topology before commit because commit reads
only the staged word and source. The unchanged writer therefore needs
no reversal-specific cursor or cleanup change.

For each new node, actual precision remains exactly P_G. With
m=min_i h_i>=2, all widths lie in [m,m+1]. An n-axis level has
P_G>=1+nm, while the next descending level has
P_G'<=1+(n/2)(m+1). Hence

    P_G - P_G' >= n(m-1)/2 > 0.                          (4)

This is a decrease across a level boundary. There is **no** assertion
that successive precisions within a level decrease. Widths (2,2,3,3)
produce reverse precisions 11,5,7; the larger example includes
36,17,20,9,9,10,11. Thus the implementation must handle shrinkage followed
by regrowth on the same retained roles.

The inherited guide and protected-word preparation uses the exact current
guide each time. The owner retires every previous live extent before a
new one is admitted, and all older cells beyond that extent are already
blank. A shorter current word therefore exposes no old data. A later
larger one reuses blank backing or extends it through local writes. The
eight guards have current RIGHT exactly at P_G+1; a historic root marker
cannot substitute for that delimiter. Full historical backing, including
the root's largest allocation, remains in the space invoice after erasure.

Induction on the encoded schedule now establishes (2)-(3) from the actual
source left by all prior commits, preserves the physical source invariant,
and proves the complete inverse endpoint asserted in Section 1.

## 5. Ownership and the failure boundary

The same fixed inventory is used: 63 physical numerical-bank roles,
eight guards, seven topology roles and one full-source staging role.
The reverse bootstrap and halving reuse `depth`, `half` and `double`.
No new word, arena, Port or provider is acquired per level or node.

The interface is the successful linear-use lifecycle of `step`/`run`.
Internal `stage` consumes this endpoint's current lease once; clients
must not bypass the endpoint, keep stale borrowed aliases or mutate its
ports between phases. A live result prohibits source commit. Each
successful step erases staging, numerical and guard roles, and the final
step additionally erases topology. Source head and all retired heads
return to one. None of those erasures shortens or forgets backing.

For a fresh forward/inverse pair, retain the complete first inventory
while acquiring the second. The two inventories are disjoint and both
stay charged and blank at the final boundary. This gives 158 private
histories. A same-bank restart, arbitrary dirty-private-memory acquisition,
crash recovery and numerical-premise failure rollback are separate tasks.
The negative controls establish failure detection at named boundaries,
not a universal rollback or malformed-stream termination theorem.

## 6. Complete source time and retained capacity

All inherited costs remain charged: source scans, canonicalization,
exact-width guards, numerical production, output consumption, head
returns, owned erasure and bank release. The unchanged writer additionally
pays full-source staging, projection and same-source commit at every node.

The inverse numerical seam uses an already proved operation. The pinned
#5053 numerical proof bounds **both** modular addition and subtraction by
2048(P+2) source operations, including their initialization and erasure.
Its slot schedule allows at most 24 newly live words plus eight borrowed
words. The changed line fits that same operation and two-temporary-word
envelope. There is no new arithmetic loop, additional axis pass, larger
word or new output field. Consequently the structural numerical proof
continues to apply; (1) conservatively allows twice its 2^20(P+2)^4
bound. Entry still contributes 2^16(P+2)^2, and the physical owner still
contributes 4096 initially and per node.

The reverse bootstrap doubles half sizes 1,2,...,d/4, whose sum is less
than d/2. Descending transitions halve d/2,d/4,...,2, whose sum is less
than d. The displayed unary loops use a fixed number of scans, copies,
rewinds and erasures per processed token. Bounding this extra work by
1024(d+2) raw Port actions leaves ample slack inside 2^19(M+2)^2 after
the forward writer/frontend's 2^18(M+2)^2 envelope. Reverse node order
does not change the multiset of selected groups or paid source scans.

For completeness, the writer's per-node raw bill is at most

    2048[M+n_G(P_G+2)] + 32,                              (5)

where n_G is its number of axes. It includes source copying, skipped
offset bits, full updated-field validation, width manufacture/erasure,
all cursor/guide/result returns, source writing and staging erasure. Over
all balanced groups,

    sum_G M = (d-1)M,
    sum_G n_G(P_G+2) = 3d log2(d) + 2A(d-1).

Thus this entire added copying cost is O(A^2), not one uncharged copy at
the endpoints. All variable controller loops read a local symbol; their
role selectors, parity flags, phase state and call depth are fixed.
Expanding the fixed control supplies C_inv in (1). This is a fixed-alphabet
source tariff, not a count of Python instructions or binary-TM transitions.

The numerical sum is O(A^4) uniformly in the admitted widths. At an
n-axis level there are d/n groups. With m=min_i h_i>=2,
P_G+2<=n(m+1)+3<=3nm for n>=2, and A>=dm. Therefore

    sum_G (P_G+2)^4
      <= 81 d m^4 sum_(n=2,4,...,d) n^3
      < (648/7) d^4 m^4 <= (648/7) A^4.                 (6)

The analogous squared sum is O(A^2); M=O(A) because d<=A/2. This proves
the full asymptotic bound, including the helper work, under the stated
source-model premises. It does not improve a multiplication recurrence.

The inherited numerical history envelope at P*=A+1 is

    B_num = (P*+1) + 2(2A+2d+2) + 57(P*+2)
            + 3[d(P*+2)+2].

Let

    D = B_num + 8(P*+2) + 6(d+2) + (A+2) + M.             (7)

The retained-backing bound for one invocation is K_source+D. The seven
topology terms cover six count/position roles and the reused width role.
The reverse temporary never exceeds the already allowed d+2. Staging
retains exactly its at-most-M backing cells. Appending or erasing its
last delimiter can visit head index M, so a literal visited-span invoice
uses M+1 for that role instead; the other terms keep their predecessor's
declared backing model. This is not a literal binary space certificate.

Every term is a maximum for one physical role over its whole history.
Shrinking a current word and erasing old bytes subtract nothing from (7).
A fresh two-invocation round trip has K_source+2D, with the source counted
once and all 158 private histories counted. Even though its endpoint
restores the initial coordinates, its source time is the sum of both
invocation bills, including both shape constructions and cleanups.

## 7. Executed evidence and limits

`verify.py` authenticates nine exports and the exact one-line producer
change. The runtime frontend, inverse adapter and unchanged writer have
host geometry/decode names poisoned. After initial fixed acquisition,
constructors for Ports, numerical Words and Arenas are sealed, and runtime
`Word.inspect` is prohibited. These controls accompany the written
finite-control argument; name poisoning alone is not a compiler proof.

The main fixed domain has 53 input fixtures: all 32 padded pairs for
moduli (3,5), fifteen four-axis cases for (2,3,5,7), four composite-modulus
cases for (4,9), and two eight-axis mixed-width cases. Each fixture runs
both F^-1(F(x)) and F(F^-1(x)) with fresh real inventories: 380 actual
numerical nodes. Nonblank source tails of lengths 17,23,31 and 97 remain
intact. At each node an independent exhaustive congruence oracle computes
the current-left integer and offset, without supplying a runtime value.
The complete endpoint also agrees with the pinned `balanced(reverse=True)`
oracle. Every source mutation, head, role identity, historical length,
exact current guard extent and final cleanup is checked.

A separate three-node test calls `endpoint.run()` without any supplied
iteration count or node schedule, while the same constructor/decode seals
remain active. It returns (0,1,0,0) from (0,1,2,1) and retires all 79 roles.
This makes explicit that observer-side loops in the main tests do not
perform production traversal.

Eleven controls reject forward level order with subtraction, addition in
inverse nodes, stale pre-root left data, old root precision at a smaller
node, nonblank older guard tails, a hidden fresh Port, doubling instead
of halving, silently shortened backing, current coordinates misread as
original digits, a global-invalid identity shortcut, and source commit
before numerical retirement. The stale-left mutant still runs the actual
encoded numerical producer on a deliberately wrong borrowed descriptor;
it is not replaced by an oracle that manufactures the expected failure.

Finite cases and AI cross-review corroborate this source-relative proof;
they do not establish independent human or proof-kernel acceptance. The
five foundational assumptions, selected certificate and complete kappa
are unchanged. No analytic accuracy, integer recovery theorem, payload
transport or all-size compiler theorem follows solely from this package.

## Open next questions

1. Bind one actual exceptional-key caller to this admitted source encoding,
   paying source production, representation conversion, return transport
   and its raw compact macro costs. This is required before a selected
   caller can use the helper; generic inverse endpoint equality is not
   that interface proof.
2. Prove a persistent restart interface that reinitializes the existing
   79 retired roles, including all prior backing, rather than acquiring a
   second fresh inventory. The present complete round trip charges 158.
3. Supply synchronized encoded numerical row/target/header schedules for
   the actual balanced payload caller. The #4024 triangular converter is
   a different admitted path; address-state evaluation is not payload
   routing and does not erase that cost.
4. Lower the complete actual provider closure to a common literal binary
   program/tariff, including clean private acquisition. Source-operation
   O(A^4) and retained backing O(A^2) do not discharge that obligation.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Retain the published forward writer and #7154/#7152 work prepared for
CubeJerry; JoyboyBrian's #5053/#5219/#5505 numerical, entry and persistent
owner contracts; Ali Romman's #5353 axis encoding and #5625 retired-write
boundary; Cinna Davis's #4100 balanced algebra; Hiroki KUMAZAKI's padded
mixed-width/current-state and raw inverse work; Tekalign's #4024 encoded
bidirectional converter; ToikY's arena lineage; commdata2338's storage
accounting; and every notice in the unchanged source exports. The CRT
inverse identities are known predecessor results. The claimed contribution
is this exact encoded reverse consumer, source-preserving lifecycle and
complete source budget on the forward endpoint's physical interface.
