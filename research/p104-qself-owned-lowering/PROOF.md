# An E-free caller identity and owned-bank lowering of QSELF

Prepared for **@CubeJerry**, with substantial OpenAI assistance. Apache-2.0.
**No new κ. No unconditional multiplication theorem.**

## 1. Exact sources, novelty and theorem boundary

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The proposed source is DreamingOfClouds' [#6937](https://github.com/CrocSwap/integer-mult-bounds/pull/6937),
head `a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`, files
`research/p104-two-chain-findings/data/caller_efree.json` and
`data/root_A_efree.json`. Its unchanged local native word and comparison caller
come from [#6936](https://github.com/CrocSwap/integer-mult-bounds/pull/6936),
head `03626137d0bd57f09b0bf9597376183ce6fa9683`, under
`research/p104-main-wire-native/`. DEPENDENCIES.json authenticates each used
source byte string; the published package does not depend on a mutable branch.

The E-free construction and the idea of trading an empty-mask role and a
query for one QSELF per chain belong to DreamingOfClouds. That source reports
an exact 76-by-76 caller replay at the four central characters. Its shipped
`check.py` only parses the caller and checks its serialized length; it does
not contain that replay. The README does not say whether the reported replay
kept the 18 D variables formal. This package makes no claim that four q
characters are insufficient, or that the earlier reported identity is false.
Indeed, four exact characters suffice when the D variables remain formal.

The additions here are a reproducible formal operator certificate and a
separate backward-covector certificate; a source-specific implementation of
both QSELF sites in the existing owned lifecycle alphabet; its complete
target/paid, ordinary-cost and stock comparison; and an explicit all-column
phase/interface proof for the new requests. No root search or replacement
native word is performed.

**Conditional theorem.** Let V be a complex vector space. Let Q,D_1,...,D_18
be commuting linear operators on V, with Q^4=I. Interpret the exact 2,991
source events with the coefficients below, applying each scalar to the whole
field. For all 76 arbitrary, independently variable input fields, the caller
returns exactly its declared diagonal Q^-1 times the selected D products.
Each of its two QSELF source events has a source-bound typed expansion, for
each of its 96 ports, using one completed rank-one request on one disjoint
owned bank, with the query-adapter, COPY, SWAP and physical-clearance contracts.
Given a faithful dispatch registry for its new SERVICE tokens, and under the
retained whole-job, ownership, common-format and cost contracts stated below,
this introduces no additional productive input and no additional paid call
beyond QSELF's declared one. Compared with the exact #6936 caller, both
complete rank-one counts decrease by 192 and all other rank counts agree.

The full caller theorem is **not** for arbitrary noncommuting Q or D, or for
Q without Q^4=I. Only the local copied-bank substitution lemma in §4 works
for an arbitrary completed operator A. Native all-column correctness,
rounded precision, physical primitive rates, installation of the new token/provider
registry, the recursive compiler join and
analytic recovery remain inherited obligations. This is not physical
execution of the entire caller.

## 2. Exact source semantics and formal certificate

Work in the commutative ring

    R = Q(i)[q,D_1,...,D_18] / (q^4-1).

Every field starts as its own independent input generator. The forward
checker stores each coefficient as two exact Fractions, with a key consisting
of the input generator, q exponent modulo four, and a square-free D mask.
Multiplication by a mask rejects if a factor is already present: it never
silently imposes D_j^2=D_j or drops a repeated factor. Each actual prefix is
checked to remain in this representation. A formal D monomial is not a
numerical probe and no D value is substituted.

ADD and SCALE are the literal rational row operations. SWAP exchanges the
ordered fields. QUERY(dst,src,k) adds q^k src to dst; QSELF(x,k) multiplies x
by q^k. IDLE_ONE multiplies its field by the product of the listed D stages.
LAMBDA_s multiplies its field by

    ((1+s i) + (1-s i) q^2)/2.

It acts on the total q operator; this scalar formula is not tensor-powered
one column at a time. At a joint stage j, the type-A four fields (u,v,x,y)
are updated by

    (u,v,x,y) <- D_j (u, v+q^-1 u, x-q y, y).

The type-B pair (s,t), with the source's alpha=-1 and beta=1/2, is updated
simultaneously by

    (s,t) <- D_j (s+alpha q t,
                  beta q^-1 s + (1+alpha beta)t).

These ordered semantics are independently read from the exact predecessor
`jclib.py`; both old rows are used for the dense B update. The source validator
checks all role ranges, disjoint types, exact host coefficients, distinct
operands, positive idle stage sets and the ordered 18 fresh joint contacts.

Induction over these operations proves that each stored row is exactly its
formal input expansion. Rational arithmetic is exact; the four residue
classes of q form a basis over Q(i)[D_1,...,D_18]. The final row comparison
therefore proves all coefficient identities, rather than checking one
particular vector. The certificate has 76 final monomials and peak 2,713
stored monomials at source-event boundaries, at most 90 in a field.

There is a unique homomorphism from this ring to the commutative algebra
generated by any operators satisfying the theorem's hypotheses. Applying it
to every coefficient proves the operator identity on every vector in V.
No dimensional restriction on V is used. D_j need not be involutions or
numeric scalars, and their inverses are not used.

The two type blocks do not algebraically mix: each tagged scalar event stays
within its own role range, and each J event is the direct sum of the displayed
A and B blocks. Therefore each block identity can be substituted separately
at every actual port, using that port's own Q_q. The 96 A copies and eight B
copies do not require different physical ports to have the same Q operator.
Completing the unchanged native word with its independent helpers before
resuming the caller is the retained contact contract used in this substitution.

### A different critical check

`dual_certificate.py` does not import the forward engine. It starts with
independent output covectors and scans the source backwards, multiplying by
the **transposes**, not inverses, of the literal gates. In particular, an
ADD into x contributes to the coefficient of its source, and the dense B
contact is transposed as a simultaneous block. Its exact coefficient type is
an integer pair divided by a power of two; normalization and arithmetic are
separate from the forward Fraction implementation.

It retains all 18 D variables formally and performs this backward propagation
at q=1,i,-1,-i. Evaluation at these four distinct roots is injective on R:
for each D monomial, a polynomial of q degree at most three vanishing at all
four roots is zero. Thus these are four faithful coefficient checks of the
same universal identity, not finitely sampled operator inputs. This is a
second algorithmic check, not independent human or proof-kernel acceptance.

## 3. Exact query orientation, absolute phase and ambient format

The inherited physical audit represents a one-column central Gaussian C_q
by its Walsh-frequency multiplier i^(q dot omega), with binary dot product.
This specifies its absolute phase, not only its projective Clifford action.
It gives C_q^2=X_q, the address translation by q, and C_q^4=I.

For each actual native port q, the source recipe supplies an orthonormal
nine-axis basis (q,b_1,...,b_8). Define the binary address map

    B(x) = (q dot x, b_1 dot x, ..., b_8 dot x).

Then B(q)=e_0, B is orthogonal, and B^-1=B^T. Its permutation P_B satisfies

    P_B C_q P_B^-1 = C_e0,
    P_B^-1 C_e0 P_B = C_q,
    X_q P_B^-1 C_e0 P_B = C_q^-1.

The last equality is exact because i^h (-1)^h = i^(-h) for h in {0,1}.
It requires the Q^2 translation on return. Omitting it implements Q, rather
than Q^-1. No phase that happens to be harmless at one tensor width is dropped.

At every positive column count f, tensor these binary maps and C operators
column by column and leave the other 144 coordinate blocks fixed. The rank-one
request acts on the f selected e_0 coordinates; both nine-axis maps preserve
all remaining coordinates. Tensoring the exact displayed equality gives
Q_f^-1 with every absolute phase raised correctly across all f columns.
This is the all-f argument. The executable 49,152 one-column spectral checks
bind its finite bases and signs to the actual 96 new source ports; those
checks alone are not claimed to prove the tensor statement.

The source's D_j acts only on fresh coordinate blocks
9+8(j-1),...,9+8j-1. These sets are pairwise disjoint and disjoint from the
nine central blocks. Consequently the intended physical Q and D operators
commute and Q^4=I, at every f, under the retained exact native contact contract.
All other local-word maps and helper endpoints remain the #6936 dependency.

Both query boundaries return to the same complete ambient coordinate order.
The coded implementation additionally requires the same component boundaries,
grids and signed widths on the returned bank and its caller field. In the
unchanged Controller, INIT uses payload 0 as its shape guide. Thus that guide
must have the same complete numerical format too; rank equality alone is not
enough. A whole-job provider must return within this format's representable
range, or the physical execution has no success guarantee. This common-format
and precision obligation is explicit and remains inside precision_tape and
the recursive provider join. The present operator identity does not establish
rounded-state equality or claim that every finite signed input is an exactly
representable Gaussian output.

## 4. One owned bank, exact history and source-preserving lowering

The canonical source is
`research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md`, Git blob
`4badb40f0919c515823cb07e44c6470d4d6469ca` at the stated canonical base.
Section 1 permits: “Constantly many owned fields may be supplied with their
full cost and no productive output credit.” Section 6 expressly permits a
paid child on an owned field containing a copied correlated value; the parent
waits for complete child return before reading or erasing that bank. Each
live unit retains its own distinct banks. These are existing conditional
contracts, not a new restoration waiver or a proof of owned_erasure.

Let x be the actual caller field and z a disjoint owned bank. The expansion is

    INIT z
    COPY z <- x
    SERVICE query-in(z)
    PAID(z, rank=1)
    SERVICE query-out(z)
    SERVICE SWAP(x,z)
    CLEAR z

Every opcode is already accepted by the unchanged published lifecycle
`source_ir.Unit.check` and `machine.Controller`. The first five events are the
existing query-bank prefix. The return service uses the exact orientation in
§3; SWAP replaces the old query-add service. There are no Python payload
callbacks or newly assumed free field transfers in this statement.

This proves **relative typed-IR and lifetime compatibility**, not an installed
physical service dispatcher. The exported tokens contain `qself6937`, and
the SWAP token also differs from the frozen current-caller source grammar.
`Unit.check` checks event structure and lifetimes; it does not validate a
SERVICE registry or numerical provider. This package installs no new registry
and does not claim that an earlier source-specific binder accepts those
tokens. The conditional semantic realization requires an exact mapping of
these tokens to the stated query providers and existing SWAP table, including
their actual headers, ordered fields and common-format predicates. Producing
and validating that dispatch/export is an explicit remaining obligation.

**Local substitution lemma.** More generally, suppose the three middle
events implement any completed whole-field operator A, with the required
format and spectator preservation. Immediately after COPY, z=x; after complete
return z=Ax and the caller's x is its original value; after SWAP, the ordered
pair is (Ax,x); after CLEAR, it is (Ax,0). Every other public field is unchanged.
This proof does not require Q^4=I, commutation, invertibility or statistical
independence of current values. If the recursive controller parks the parent,
its x is preserved in protected ancestor storage and restored at return;
the same current physical tape need not be untouched while a child runs.

CLEAR erases the old x **now stored in the owned z bank**. The canonical
contract conditions erasure on bank ownership and completed descendants,
not on the numerical content having originated independently. It does not
require restoring an arbitrary prior value of z. The returned child is
complete before the parent reads, swaps or erases z. Every descendant has a
different owned-bank identity. Borrowed public helpers are never used as z.

A literal wrapper INIT z; QUERY(z,x,-1); SWAP(x,z); CLEAR z would have two
simultaneously live banks: z and QUERY's internal copied bank. The fused
expansion above uses the internal copied bank as the returned value and
omits the redundant outer zero target and ADD. Its exact semantics follows
from the local lemma; it is not a claim that the two implementations have
identical rounded trajectories.

The exact source QSELF sites are event 457 on A role 0 and event 575 on A
role 19. Each is applied to the 96 A ports, for 192 expansions and 1,344 IR
events. Their source tokens retain site, port, literal operation and actual
ordered owner. Injective compiler remapping preserves the owned recipient
and the SWAP order. The generated patch is checked through the unchanged IR
class; a separate whole-local-source structural pass accepts 71,144 native
events as 83,790 typed events. Neither pass is a fullcaller tape replay.

The actual raw source processes each port's complete expansion before the
next one, and every joint native invocation is complete before the next
outer event. One outer query bank is therefore reused across the 416 new
QUERY-or-QSELF instances. It overlaps no local owned lifetime. The local
word still has 51 labels, 54 lifetimes and peak 43; an unreused safe finite
inventory is 18*51+1=919 raw-unit private names, with maximum 43 live locally.
Suspended recursive unit instances retain distinct banks: this is not one
scratch tape per recursion depth. Old erased backing remains counted at its
high-water extent.

## 5. Positive costs, complete invoices and numerical limitations

The generic request has two nine-axis conversions, one Q^2 translation and
one rank-one child. It also pays INIT, numerical COPY as addition, both SWAP
outputs, physical raw erasure, all source access, heads, child continuation,
complete child return, and existing descriptor/row services. An initially
dirty bank is disposed of rather than assumed empty. The two work ports of
the published SWAP table are reusable existing primitive work, with current
backing 2V+3; z adds V. Adapter work is retained separately and may be reused
only after successful primitive retirement.

Here is a physical cost statement independent of a numerical historical cap.
Let V be a complete field's physical coded length, D total initially occupied
bank/work bytes, and q_0 the fixed supplied work/context inventory. Given
actual query-provider costs A_in,A_out and the actual paid-boundary/child
cost B_paid, the new fragment is bounded by

    A_in + A_out + B_paid + 2048(V+1) + 16D + 64q_0.

This deliberately loose remainder covers the unmodified initialize,
copy_as_add and retire scans and the published SWAP ceiling
1024(V/3+1)+8D+32q_0. Every term is positive. The boundary/child term is not
hidden in a scalar allowance or counted as zero. Provider work, all other
public fields, parked ancestors and descriptors remain in the complete caller
stock. The bound is conditional on their declared physical interfaces; it is
not a construction of those interfaces.

Here are the scan constants behind that remainder, using the lifecycle's
physical read/write/unit-move metric and charging executed SWAP table rows as
in its published theorem. Set L=V/3. From its current origin, `origin` costs
3 actions; from offset h it costs 2h+3. A raw `retire` of d occupied bytes
therefore costs exactly 5d+7, including both head resets. `read_code` costs
7 actions per present codeword and 1 at the frontier; `write_code` costs 6.
Thus INIT on an initially d-byte dirty bank, guided by a V-byte complete
field, costs 5d+25V/3+17. COPY costs 14L+9b+4V+14, where b<=L is the number
of numerical-bit codewords; it is at most 35V/3+14. CLEAR after the successful
SWAP costs 5V+7. Their sum is at most 25V+5d+38. Adding the SWAP bound gives
at most (1100/3)V+1062+5d+8D_work+32q_0, plus a fixed seven-event dispatch.
It is below the displayed 2048(V+1)+16D+64q_0, for D=d+D_work. Query providers
are separately charged for their own work retirement and head reset; on
successful return through `Controller.primitive` their declared work ports
are blank. These constants count actual coded bytes and both output writes;
they do not equate this tape metric with the historical scalar/pass tariff.

For comparison with #6936's **inherited scalar/routing accounting convention**,
`invoice.py` reconstructs the local scalar and route terms directly from the
unchanged word, all caller/idle/main/query terms directly from both callers,
and adds a separate 128 ordinary units for each new QSELF instance. This
extra 24,576-unit charge covers four lifecycle/scalar operations at the
retained 32-unit gate envelope, in addition to the thin lifecycle allowance
and the general caller envelope. Both full nine-axis conversions and the
translation are charged at 1,000 each. These retained scalar/pass rates are
not an independent verification of physical precision_tape tariffs.

The exact results are:

| Quantity | #6936 comparison caller | E-free caller with owned lowering |
| --- | ---: | ---: |
| Main arbitrary input fields | 4,144 | 3,952 |
| Fresh helper fields over 18 local calls | 19,098 | 19,098 |
| Complete productive count | 23,242 | 23,050 |
| Complete paid calls | 118,038 | 117,846 |
| Outer rank-one QUERY/QSELF calls | 608 | 416 |
| Source local rank-one/other paid calls | unchanged | unchanged |
| Reviewed raw ordinary upper | 832,255,648 | 796,934,944 |
| Extra LAMBDA reading | 12,560,000 | 11,792,000 |
| Per-call 1125 conversion reading | 2,734,992 | 2,734,992 |
| Both extra readings included | 847,550,640 | 811,461,936 |
| Margin below 10^9 in that convention | 152,449,360 | 188,538,064 |

At each joint call the same 1,461 local public fields map to four A mains per
A port, two B mains per B port, and 1,061 distinct helpers. Those helpers have
fresh stage-specific identities. Neither their arbitrary inputs nor their
productive outputs are erased or replaced by the query bank. The B stream is
byte-for-byte the same sequence of operations after its offset shifts by two.
Every main target in the new caller has a nonempty D mask.

For every rank r the exact complete profiles satisfy

    T_new(r) = T_old(r) - 192*[r=1],
    P_new(r) = P_old(r) - 192*[r=1].

Consequently the complete moment polynomial is identical at **every** κ,
not merely at a sampled decimal root. The rank-mass surplus remains 1520;
the new paid rank mass is 317,324. The two removed empty-mask E roles no
longer receive 192 rank-one productive credits, and the corresponding paid
debit falls by the same amount. There is no new κ from this substitution and
no claim that the unreviewed #6936 bound is the accepted frontier.

These changes must replace the raw-unit counts in any future compiled
precision/stock certificate. It is not enough to observe a smaller scalar
cap. COPY propagates its actual residual as addition; it does not overwrite
an ideal value for free. With adapters E,F and child C satisfying FCE=A,
the output error includes FC times input/copy/entry error, F times child
error, and exit error. SWAP exactly permutes stored words and its errors;
erasure of the other bank does not erase these terms. The full rounded
recursion and source-entry predicates are not established here.

## 6. A precisely scoped obstruction without owned initialization

Consider the formal commuting caller algebra above, allowing arbitrary
independent auxiliary fields which must all be restored. QUERY is an
elementary shear of determinant one. Constant scalings and permutations
have q-independent determinants. LAMBDA determinants depend only on q^2;
IDLE determinants depend only on D. The joint HOST/HOST2 determinant is a
power of D and is also unchanged under q -> -q. Thus any finite word in this
alphabet has determinant even in q.

A single QSELF with every auxiliary field restored would have determinant
q^-1. Evaluating at q=1 and q=-1 (and any fixed nonzero D) contradicts the
evenness of the word's determinant. This excludes that universal single-job
restored-workspace realization in this formal alphabet.

It does not exclude every concrete Clifford specialization: spectral
restrictions or cancellation in a concrete large determinant require their
own analysis. It also does not exclude the **pair** of QSELF sites; their
combined q determinant is q^-2=q^2, which is even. No bound on a paired
QUERY-only synthesis follows. Owned initialization and erasure invalidate
the restored-arbitrary-workspace hypothesis, exactly as the explicit copied
bank does. This obstruction explains that distinction; it is not a global
impossibility theorem or a substitute for the constructive result.

## 7. Remaining obligations and credit

The five selected framework assumptions remain native_all_columns,
owned_erasure, compiler, precision_tape and analytic_recovery. The #6936
native/A6, odd-scalar exact-return and BIT dependencies also remain. No
selected certificate is changed. Actual all-column native word execution,
all caller field-format predicates, complete rounded-return contracts and
compiled recursive stock/precision substitution still require review. The
new token-to-provider/table registry and concrete header export are also
unfinished; accepting a seven-opcode IR fragment does not discharge them.

The E-free root, caller, source claim and proposal are DreamingOfClouds' work
with Claude Opus assistance. Retain Romman and the productive native/compiler
lineage; @CubeJerry's [#6912](https://github.com/CrocSwap/integer-mult-bounds/pull/6912)
caller blocks, [#6914](https://github.com/CrocSwap/integer-mult-bounds/pull/6914)
owned-rise work and published lifecycle/scalar/SWAP implementations;
unpaidmoon's [#6930](https://github.com/CrocSwap/integer-mult-bounds/pull/6930)
width-two phase work; and icekylinx's [#104](https://github.com/CrocSwap/integer-mult-bounds/pull/104)
odd-grid contribution. This package was prepared for @CubeJerry with
substantial OpenAI assistance in source analysis, proofs, code and review.
