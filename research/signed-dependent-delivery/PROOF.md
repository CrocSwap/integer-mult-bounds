# Signed source dependence with sequential dirty readouts

Prepared by Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
This is a written all-parameter argument with finite exact checks and a separate
AI mathematical review, not a proof-assistant or independently human-checked theorem.

## Exact contract

Work over Q or C (or a characteristic-zero vector space). Fix k>=1, d>=1,
nonzero rows M_i in Q^d, and independent arbitrary vector inputs v_j. During
request i the available source is x_i=sum_j M_ij v_j. Its acquisition, imposed
mutations, coefficient preparation and any required final source restoration
are paid caller operations. They do not modify z or any output and do not
occur inside requests. They need not be cheap or available in a selected caller.

There is one arbitrarily dirty connector z and a distinct arbitrarily dirty
output y_i for each request. Fixed compatible linear maps B and A_i are exact,
additive, and independent of old target contents. Allowed data queries are only

    B_i^s: z += s B x_i,       A_i^s: y_i += s A_i z,    s in {-1,+1}.

Only request i may write y_i, and it must deliver y_i+=A_i B x_i before the
next request. The hidden connector remains exclusively reserved and has no
intermediate observer; at batch exit it must equal its arbitrary entry value.
Inputs, maps and other outputs are preserved by each query. No source mixing,
extra connector, direct product, combined query, free scalar multiplier or
correction call is admitted. Any number and order of permitted queries is allowed.

The word is fixed independently of data and works uniformly for all compatible
linear maps and independent inputs. Each A_i query has fixed positive complete
price a_i, each B_i query price b_i, identical for its two signs and all admissible
states. Complete prices include the literal inverse implementation, private
scratch restoration, source/coefficient access, target update, routing, frames,
head return, and dispatch of that call. State-, sign-, position- or path-dependent
costs require another optimization. A zero fixed A_i B can be cheaper; this is
not a lower bound for every specialized map or unrestricted circuit.

## All-word tariff theorem

Put phi(0)=2 and phi(t)=|t| for nonzero integers t. The exact universal-word
query price in this alphabet is

    Q(M,a,b) = 2 sum_i a_i
                + min_{t in Z^k, M^T t=0} sum_i b_i phi(t_i).        (1)

Add every external caller charge specified above; (1) does not price them as zero.

For necessity, specialize all maps to scalar identities. Nonzero M_i ensures
that output i has a nonzero requested increment for some independent input.
Every signed reader occurrence has the same coefficient on the arbitrary z_0.
Therefore its signs sum to zero, and it appears at least twice. If there were
no B query during request i, the connector would be constant throughout that
request, so all its signed readouts would cancel: at least one B query is needed.
Let t_i be the signed net number of B queries in epoch i. Restoring z for all
independent v_j forces M^T t=0. A net t_i needs at least |t_i| occurrences; if
t_i=0, its already established positive occurrence count must be at least two.
Positive complete tariffs give the lower bound (1). No two-read restriction,
intermediate coherence, or bound on multiplicities was used in this argument.

For sufficiency, choose any feasible integer t. For t_i!=0 put s=sign(t_i) and use

    A_i^(-s); B_i^s; A_i^s; [|t_i|-1 more B_i^s calls]; deliver i.

For t_i=0 use A_i^-; B_i^+; A_i^+; B_i^-; deliver i. The two readouts differ by
exactly A_i B x_i, whatever dirty or stale value entered z. All other B calls
are outside the readout pair. The final connector change is

    sum_i t_i B x_i = B sum_j (sum_i t_i M_ij) v_j = 0.

The construction pays phi(t_i) source calls and exactly two reader calls, keeps
every output in its own request, and preserves all other ports. It attains (1).
No factors commute or exchange roles in this derivation.

The minimum exists and has a finite exact search domain. t=0 gives source bill
C0=2 sum b_i. Any improving solution satisfies |t_i|<=floor(C0/b_i). An exact
dynamic program on prefix source vectors, restricted to that bill, therefore
computes the minimum. Clearing each column's rational denominators preserves
the kernel. This finite algorithm is not claimed polynomial in encoded inputs,
nor a free/efficient uniform recursive controller. The proof of (1) is not
inferred from its finite tests.

## Three deliveries and second differences

For x_1=x, x_2=x+u, x_3=x+2u, the source rows are (1,0),(1,1),(1,2).
The integer kernel is exactly t=q(1,-2,1), q in Z: the u coefficient gives
t_2=-2t_3, then the x coefficient gives t_1=t_3. At q=0 the source bill is
2(b1+b2+b3); for q!=0 it is |q|(b1+2b2+b3). Hence

    Q = 2(a1+a2+a3) + b1+2b2+b3,                          (2)

strictly below the closed-call bill by b1+b3. The vector (1,-2,1) gives

    A1^- B1^+ A1^+;
    A2^+ B2^- A2^- B2^-;
    A3^- B3^+ A3^+.

The source after each request is updated by the paid caller. Connector offsets
after these epochs are Bx, -Bx-2Bu, and 0. Intermediate coherence with the
current source is not required. The doubled negative middle net is essential:
there is no nonzero kernel vector with all t_i in {-1,0,1}. It uses two literal
negative source calls, not an unpaid scalar multiplication.

This is not a lift of a binary parity witness. For example, (1,0,1) annihilates
the two source rows modulo two but has integer residual (2,2). Adam Gall's
PR2060 remains a theorem over its stated F2 alphabet. The signed exact-query
model and complete-price convention follow the credited signed connector
lineage; the new obligation here is its imposed dependent-source delivery boundary.

## Restoration and size obligations

The full pilot implements x+=u after requests 1 and 2 and x-=u twice after
request 3, restoring the original x. All four source mutations are paid by
every comparator. Its inverse is the reversed primitive list with every sign
negated, including reversed source mutations. The forward-only imposed source
schedule is not automatically an admitted inverse caller: one must grant its
reverse schedule and observation cuts for inverse execution.

At macro endpoints, if ||x||<=X, ||u||<=U, ||z0||<=Z and ||B||<=beta, the displayed
connector offsets are bounded by beta(X+2U), including the partial middle
offset -Bu. Thus ||z||<=Z+beta(X+2U). A temporary reader value costs at most
Y_i+||A_i||(Z+beta(X+2U)); completed outputs obey the same bound. These endpoint
bounds do not certify a compiled child's internal magnitude. Rounded/nonlinear
children, bad incoming ranges, forbidden borrows or incompatible frames can
invalidate the construction and must be checked in a real caller.

## Fully charged recursive comparison and stopping boundary

Let S include identical preparation, imposed source updates, source restoration
and all other common costs; let E_plan/E_closed include every noncommon
controller, precision, storage lifetime, hosting, movement and caller charge
outside the complete tariffs. Then for this three-epoch interface

    C_plan   = S+E_plan  +2 sum a_i+b1+2b2+b3,
    C_closed = S+E_closed+2 sum a_i+2b1+2b2+2b3.

The actual gain is b1+b3-(E_plan-E_closed), not just a scalar ADD count. The
hidden connector's full reservation is a premise. If a closed caller can lend
its capacity at intermediate cuts, that lost opportunity belongs in E_plan.
Sign-asymmetric tariffs need literal separate billing and are outside (1).

When each source query is one completed recursive child of rank r with matching
uniform ports/tariff, the changed child profile is exactly -2 H_r. When its
full internal profile is nu_s, the change is -2 nu_s at every rank s, including
the inverse implementations. This follows from removing two whole completed
queries; it is not inferred from their primitive scalar representation. No
extra D child is present. If normalization m,W is unchanged, the normalized
moment decrease at exponent a is

    (1/W) sum_s 2 nu_s (s/m)^(1-a),

before adding the actually incurred profile of E_plan-E_closed. Changes to
m,W, widths, stock, setup or the other supplier must also be accounted for.
The package provides no actual selected-source occurrence or complete supplier
histogram, so it certifies no new root, outer transfer or kappa.

The fully expanded finite pilot checks every primitive operation, uses nine
dirty ports without clean ancillas, restores source and connector, and preserves
each output's entry dirt additively. It is a calibration instance. The
primitive word has maximum row-L1 9 for the candidate versus 8 for the
closed word (7 for direct fusion). Equal input magnitude bounds consequently
need four versus three conservative extra magnitude bits. Endpoint macro bounds
do not erase that measured interior charge. Any real admission must either pay
its actual direction-specific change or provide a compatible precision argument.
The inverse primitive-prefix maxima are 8 for the candidate and 9 for closed
(7 for direct). Thus a caller reserving a common forward/inverse input-range
capacity already needs maximum 9 for both words. The forward-only increase
does not prove a mandatory extra precision charge for every caller.
Opening its A/B maps yields a cheaper direct program; therefore its macro optimum is
explicitly not unrestricted circuit optimality or physical speedup. Stop here
until one named real recursive caller supplies exactly this source dependence,
legal persistent reservation, full tariffs and a better complete comparator.
