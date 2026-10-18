# Completed fast primitives for the selected BIT caller

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement the source-bound successor in commdata2338's
[PR2399](https://github.com/CrocSwap/integer-mult-bounds/pull/2399), head
`14458fda3cac4441c27980d584582ebbbb3e9233`. I retain its substitution algebra.
I use the completed ordinary B1 from PR2899 and replace both reached primitive
sites in David Arias's PR2753 caller through the PR2809 physical realization.
I retain the exact archives and their source arguments in `inputs/`.

## 1. Statement and mathematical dependencies

Fix a source-admissible prime q>2^80 and the selected finite vocabulary. Write

    c=17/10000, a1=c(1-c)=169711/10^8, p=1-a1.

I assume the pinned C0 endpoint, chronology, source-refinement, complete-fibre,
stock and uniform-cost arguments from PR2753/2809, and the completed B1
composition from PR2899. B1 implements an ordinary exchange on
`[P][q^u][G][q^u][S]`, with positive complete spectators, in
`O_q(PGS q^(2u) u^p)` time. B1 preserves its borrowed source and spectators,
returns a distinct output, and restores its owned work after successful
execution. Its caller consumes the output before reuse. B1 requires no
external row reserve. I include its fixed compilation allowance F_q.

I construct C1 with the same weighted reversed endpoint, coarse children and
fresh-stock domain as C0. For a node of complete payload volume V, atom width
w and n atom pairs, I obtain local work `O_q(V(n+w^p))`. Under the retained
canonical root coupling and moment argument, I obtain

    T_C1(n,w)/V = O_q(n+n^(1-c)w^p),
    space = O_q(V)+F_q.

I compose the preceding ordinary wrapper with C1 to obtain B2, with saving

    a2=c(1-c)+c*a1=c(1-c^2)=1699995087/10^12.

I do not derive these quantified statements from the finite fixtures. I use
the named source arguments and the implementation refinement below. I retain
successful execution on admitted canonical inputs; I make no interrupted-macro
recovery claim. I have not materialized the selected GL64 payload or its entire
transition table, and I claim no formal proof or selected-frontier adoption.

## 2. Separate the stages and bind the reached calls

I keep the dependency order C1 → B1 → C0 → A0. In the authenticated namespace,
the weighted and remainder leaves call `stream_runner.atom_swap`; changing
only `bitstream.atom_swap` would leave its imported alias untouched. Owner
episodes call `routes.route_packet`, whose body resolves `routes.route_cube`.
I specialize those two sites in `stage.py`.

Before entering B1, I restore both original A0 bindings and suspend the C1
scratch factories. I preserve C1's live leases and numerical banks while B1
uses its own fixed roles. I retain the constructor prohibition through this
switch. B1's C0 roots therefore see their preceding elementary routes and
swaps. On return, I restore C1's factories and two bindings. The stage flag
has two states and introduces no input-dependent recursion level.

For a leaf swap, I copy the canonical spectator Counts and derive u by
encoded radix division of the modulus. I lend physical views of the source
and Counts to B1. After B1 returns, I copy its output into a C1-owned lease,
rewind that lease and clear B1's output port. The caller may then consume the
lease through its existing `Machine.commit` ownership rule. I charge the
copy, rewind, clearing and Count disposal.

I establish the closed B1 baseline before C1 starts. At final C1 return I
erase the consumed B1 output marker; before reuse I restore that marker by
an explicit local write. I preserve B1's other fixed roles. The outer adapter
reuses the actual fresh RootSession roles when promoting it to C1; it does
not copy or abandon their physical tapes.

## 3. Compile the actual chart direction and carries

For a fixed owner chart sigma and complete low matrix g0, the existing route
contract sends the high matrix G to

    G' = ((g0+qG)sigma-d0)/q mod Q,  Q=q^(w-1),
    d0 = g0 sigma mod q.

The caller retains its native/common low-label calculation. I bind each data
or host chart matrix from its actual Catalogue to the inverse of PR2157's
retained word, and also register the reverse orientation. I check the exact
rational matrix product during registration. Thus the compiler does not infer
direction from a route name. I cover 999 data and 124 host types. The family
charts used in IDLE coefficient preparation remain in their existing path.

For a column addition `y <- y+(a/d)x`, with dyadic d and canonical low digits
x0,y0, I compute at compilation time

    y1=(d*y0+a*x0)/d mod q,
    C=(d*y0+a*x0-d*y1)/q.

On the high coordinates I execute `Y <- d^-1(dY+aX+C) mod Q`. For a scale
`y <- (a/d)y`, I instead use `y1=a*y0/d mod q`,
`C=(a*y0-d*y1)/q` and `Y <- d^-1(aY+C) mod Q`.
I update the low state after each factor and require its final matrix to equal
the route's complete target low class. I retain the signed carry, with
`|C|<=4`, and never compute it from an already updated source low digit.

I use magnitudes 1, 2, 4 and their reciprocals, with either
sign. Since q is odd, I can invert 2 and 4 modulo Q. I expand each column factor
across the fixed 64 rows. All chart matrices, low labels, carries and resulting
opcodes belong to a finite q-dependent vocabulary. The compile cache has no
w, n, high coordinate or ancestor in its keys. I may precompile this finite
table or charge its bounded lazy compilation to F_q.

I choose a registered word with minimum ordinary-swap count when several
words have the same matrix. This preserves the retained count as an upper
bound; I do not call it an exact minimized instruction count.

## 4. Realize each high-field operation with complete streams

I initialize a separate canonical high-modulus bank from an encoded Count(Q).
I do not reinterpret the parent context's margin-padded cap as a Ring modulus.
For field positions a<b among m^2 coordinates, I use encoded extents

    before=Q^a, middle=Q^(b-a-1), suffix=Q^(m^2-b-1)*fibre.

An ordinary high-field swap calls native same-q B1 at u=w-1. I avoid binary
padding here. An ordered addition uses the retained sequential `add_pass`;
for the reverse field order I perform B1, ordered ADD, B1. I form the fixed
numerator modulo Q on the high bank and close its arithmetic temporaries.

For doubling modulo odd Q, I split the source into `(Q+1)/2` origins and
`(Q-1)/2` origins for each prefix. I interleave their suffix blocks into even
and odd destinations. For halving, I demultiplex even/odd source blocks and
concatenate them. I traverse and erase a constant number of complete streams.
I use encoded ripple counters and preserve each suffix block's order.

I use the retained linear sign pass for negation and the retained+1 pass for
positive translation. For a negative unit translation I execute sign,+1,sign.
I repeat at most four times for C. These extra translation passes differ from
PR2157's combined controlled-shift census; I charge them in the linear term.
I do not present that predecessor's nonordinary census as the exact new word.

At Q=1 I return a fresh copy of the unique high cube. I create neither Ring(1)
nor a zero-width B1 call. This handles identity charts and width one under the
same owned-output contract.

## 5. Preserve old-prefix order and charge complete local work

The retained `route_packet` visits old-prefix ordinals in order. It copies one
complete cube to a local stream, calls `route_cube` with that cube and appends
the returned cube to its output. I preserve that contract. I check exact input
length, rewind the borrowed source, and release each intermediate after the
next complete pass. I erase the high bank after the cube.

Let W=28416 and N be the retained number of low labels. One owner packet has
volume `v=V/(WN)`. From PR2157's source-bound invoice I obtain at most

    2*(128352256+76197888)*N = 409100288*N

ordinary calls over the entrance and return owner routes. Therefore the route
ordinary charge is at most

    C_B * (1598048/111) * V * (w-1)^p.

I omit that term at w=1. Native B1 supplies the same-q field interface, so I
add no binary-padding factor to this coefficient. The selected schedule and
equivalent-word minimum can only reduce the bound.

For w>=2, one complete cube has volume `r=Q^4096*fibre`. I bound its new setup
and disposal by a fixed polynomial in `w+log(2*fibre)`: encoded extent products,
radix-width derivation, numerical templates, and fixed-bank marker scans.
For fixed q, I have `P(w,log(2*fibre))<=C_q*r`. I prepare the template once per
cube. After closing live Words, I erase their fixed origins and the template;
I do not scan the template once per payload bit. For C old prefixes, I sum
these costs as `C_q*C*r=C_q*v`. I traverse the outer ripple counter once.
I do not multiply a complete-packet charge by C again.

I include extraction, appending, the initial cube clone, intermediate clearing,
rewinds and the returned B1 copy. I also retain family gather/scatter, latest
canonical commits, COPY clones, transported ERASE, bridge XOR, terminal content
exchange, directories, program copies, numerical parking and restoration.
Their retained fixed schedule contributes `A_q*V*(n+1)` after preparation.

I use four B1 calls for each of at most 63 peeled pairs. A more explicit local bound is

    C_B*V*(252*w^p+(1598048/111)*(w-1)^p)
       + A_q*V*(n+1) + E_prep.

I charge stopped recursive leaves through the recurrence below, without adding
them to this local bound a second time. I retain the linear sign implementation;
an elementary digitwise sign would restore an unwanted width factor.

For generated coefficients, I retain PR2753's canonical root coupling:
`n<=e`, `w=ceil(e^c)`, and its chronological-history bound. Then 2^h times a
fixed polynomial in the numerical widths remains polynomial in w. I charge
each preparation to its complete q^w target fibre. I keep unrelated spectator
counters outside that preparation and use their own canonical lengths. Under
these premises I absorb E_prep into the displayed local toll. Outside that
domain I retain E_prep explicitly and make no stronger estimate.

## 6. Retain the coarse recurrence and apply the outer wrapper

I retain the selected paid profile

    (H1,...,H7,H42)=(381024,400416,22752,26880,29376,17376,26784,288),
    W=28416, epsilon=10^-16, F=118606528512.

Let T1 denote normalized time per payload bit and f=floor(n/64). I have

    T1(n,w) <= C_q*w^p                                      (0<n<64),
    T1(n,w) <= sum_r (H_r/W)*T1(r*f,w)
                 +(epsilon*F/W)*max_{1<=j<=f} T1(j,w)
                 +C_q*(n+w^p)                              (n>=64).

The earlier B1 invocations belong to the local toll. They create no C1 coarse
children or parent-stock factor. From the retained moments in PR2234 and the
substitution algebra in PR2399, I obtain

    T1(n,w) <= 200*C_q*n + 10000*C_q*n^(1-c)*w^p.

For B2 I keep PR2899's encoded setup, stock K(w)^D(e), two unweighted ROOT
calls, below-two padding ratio, restrictions, remainder and high exchanges.
I specialize its fresh inner RootSession to C1 with a separate sealed B1.
I retain its selector `w=ceil(e^c)`, `n<=e/w`, `k=O(w log e)` and finite
elementary fallback. The complete ordinary time per bit is therefore

    O_q(n+n^(1-c)*w^p+k+w)
      = O_q(e^(1-c+c^2-c*a1)).

The first term n and the setup/high/remainder terms have smaller exponents.
I reuse the same binary rectangle completion, which adds only q-dependent
volume factors. Thus I obtain saving a2 in both ordinary interfaces. I retain
the existing stock-fit proof; I infer no new numerical cutoff from this bound.

## 7. Bound the fixed inventories and lifetime

I preserve the C0/C1 role-parking argument through proper-width descent. A B1
call finishes before C1 resumes a child or another primitive. During B1 I
retain C1's live fixed roles and add one complete preceding-stage inventory.
B1's payload volume equals that primitive's cube or stream volume. Its private
reserve, output and templates contribute `O_q(V_root)+F_q` at the root scale.

I add 128 fixed scratch tapes to the retained completed-block pool. In the new
high-route layer I retain fewer than 32 simultaneous extra pool roles: its
modulus/current stream, at most three extents, fixed-power/product temporaries,
scaling buckets and counters, marginal Counts, or B1 width/extent copies.
These branches run in sequence. I retain the preceding completed-block scratch
allowance for the underlying ADD, sign and copy routines.

I count the high bank's `capacity+1` physical Word tapes separately, and I
charge their markers, templates and live contents. Capacity depends on the
fixed compiled vocabulary. I also count B1's fixed inventory separately. Any
blank backing allocation that remains between calls is bounded by the largest
previous use of that fixed role; I charge it at the root volume. I claim no
per-return deallocation of backing arrays. I thus retain `O_q(V_root)+F_q`
space without retaining one B1 inventory per child or per prefix.

I exclude provenance masks, test observers and counters from machine state.
They never supply numerical operands or choose a runtime instruction.

## 8. Evidence, selected consumer and stopping decision

I compare complete kernel and route outputs with independent affine-column
maps while payload cells remain Boolean. I check an actual selected Route
producer and the entire finite owner-matrix vocabulary at q3. I check signed
carry and source-binding rejection with Python assertions disabled. I check
the full retained reduced COPY/IDLE/MOVE schedule and both padded F returns
in the outer wrapper, before the two-call cancellation could hide a defect.
These tests complement the written argument; they do not establish its
universal dependencies or execute the selected high-dimensional payload.

For the current selected ASSEMBLY, let a_req be `outer.bit_positive`, let
`b=67018507072324140917/(4*10^22)` and beta=10^-24. I checked

    a_req < (1-beta)*b < b < a1.

I can therefore weaken preceding B1 to a_req for the current complex consumer,
retaining its 47 outer inequalities and selected kappa. I must not substitute
a1 into the convenience assembler's `complex_above_bit` predicate, which asks
for b>a. The generic compact-movement, complex-layer and outer implications
already belong to PR2250, PR2287 and PR2298.

I stop ordinary-stage expansion after this current-caller construction. I
leave actual complex callback binding, common-label realization, complete
hosting, precision, exact recovery and analytic transfer to their separate
source obligations. C1/B2 could help a future consumer with a larger complex
saving; they do not raise the present selected frontier.
