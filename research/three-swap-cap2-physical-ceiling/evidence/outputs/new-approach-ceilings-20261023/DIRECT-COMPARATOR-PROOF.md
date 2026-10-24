# A direct-target price screen for the cap-two proposal

**Scoped conditional economic result.** Nick Petalas's #5083 correctly compares
its five-call cap-two word with the six-call word in its restricted formal
alphabet. That comparison is not sufficient for its proposed BIT physical
interpretation: the source also has a direct ordinary-swap implementation.
For the reversed primitive interpretation, a candidate must satisfy

```
c2 < (2*cF + 6*cHalf - Delta)/4,
```

to beat that direct recipe. This can be substantially stronger than `c2<2*cF`.
Here cF,cHalf and c2 are actual complete, identically typed prices; Delta is
only the new minus direct overhead not already inside those prices. No
physical cap-two supplier or completed output inventory is supplied by this
note. There is no new κ and no impossibility claim for changed interfaces.

## Exact source and ownership

The #5083 formal source is frozen at
`d2b3f35275cab6fbf18bee40e3fb411496732e54`, with its README, the #2415
product-preserving GL2/S3 bridge, and two unchanged BIT notes in `frozen/`.
`SOURCES.json` binds exact bytes. The source author establishes the five-call
formal result; its formal replay is not rerun here.

The physical interface/source extraction is owned by sibling worker
`sol_1337_contact_frontier`; it supplied the exact reversed/ordinary distinction,
whole-volume interpretation and source snapshots. This note independently
derives the economic comparison, its sharp price boundary and exact rational
controls. Astra selected this paired question. The monitor's bounded 08:28–08:33
checkpoint found no newer competing physical owner; this is delegated overlap
evidence, not a complete or current survey.

## The three distinct comparisons

**Formal a/b-only model.** #5083 gives scalar-owner-rank profile
`(2,2,1,2,2)`, total price `c1+4*c2`. Its comparator is `3*c1+3*c2`.
They have the same formal endpoint `diag(s,s,s,I_dirty)`. The difference is
`2*c1-c2` under the source tariff `0<=c1<=c2<=2*c1`. This is credited source
work, not the new result of this note. Scalar owner rank is not address width
or recursive-child rank.

**Ordinary-swap interpretation.** Under the source #2415 bridge, `a=(12)`,
`b=(23)`, `s=(13)`. If the implemented primitive is an ordinary interchange J
of any two equal chunks, the target (13) is itself an available J of the same
width. Three target roles cost at most `3*cJ`. Taking c1=cJ, the formal word
costs at least `5*cJ` when c2>=cJ. This is a changed physical alphabet, so it
does not contradict #5083's exact minimum in its restricted formal alphabet.
It does show that the restricted six-call comparator is unsuitable here.

**Reversed-swap interpretation.** The actual source BIT primitive is

```
F_A(H,D)=(A*C_f*D, C_f*A^-1*H),  C_f^2=I.
```

Use unweighted a=F_12 and b=F_23 on three whole equal address chunks.
Writing C=C_f, the chronological actions are

```
(x,y,z) -> (C*y,C*x,z) -> (C*y,C*z,x) -> (z,y,x).
```

Thus aba is ordinary J_13; the two reversals cancel. The analogous bab has
the same endpoint. This calculation includes the middle chunk unchanged.
The source #2415 group isomorphism supplies the formal label correspondence;
it does not supply a rank-two physical implementation.

The source `notes/three-stage-cover-bit.tex:172-187` constructs
`J_A=R_tail F_A R_tail`. Each R_tail is one unweighted reversed call on
first/last floor(f/2) atoms, fixing the middle atom. Therefore its explicit
recursive tariff is at most

```
cJ(f) <= cF(f)+2*cF(floor(f/2)).
```

These calls preserve complete spectators; they are on the same logical volume
V. The source `notes/batched-bit-rows.tex:9-25` separately defines a larger
address-width child on exactly V/W, and repeats separate calls explicitly.
Concatenating two role owners changes volume to 2V/W, so a larger address-width
tariff is not a justified price for the cap-two owner invocation.

## Sharp threshold against this recipe

Fix the same required complete target, volume, address chunk width, orientation,
precision and spectators for the two programs. Let

```
F = complete price of one unweighted reversed width-f call,
Q = complete price of one unweighted reversed width-floor(f/2) call,
B = complete price of the proposed cap-two owner call at width f,
wNew,wDirect = costs outside those complete calls only,
Delta = wNew-wDirect.
```

The proposed word has tariff `F+4B+wNew`. The direct recipe has constructive
upper tariff `3F+6Q+wDirect`. Therefore beating that available recipe requires

```
F+4B+wNew < 3F+6Q+wDirect,
B < (2F+6Q-Delta)/4.                       (1)
```

Equation (1) is exact for the stated tariffs and tight as a comparison to this
recipe: equality is break-even, either strict side reverses the ordering. It
does not assert this direct recipe is optimal. If another direct implementation
is cheaper, the necessary price is even lower. Costs already inside F,Q,B must
not be charged again in Delta. Unknown overhead prevents a complete physical
decision; it is not silently set to zero. The useful free grant Delta=0 is an
explicit recursive accounting comparison, not a proof of zero physical overhead.

The uniform tariff is an explicit hypothesis for both labels and every selected
owner pair. Without it the five-call subtotal is `F_a+2*B_a+2*B_b`, with further
pair-dependent prices if necessary. The unweighted calculation does not identify
different ancestor-dependent weight arrays; such jobs need a fresh matched bill.
If the actual required targets are raw F rather than J, this word has the wrong
endpoint. Wrapping its three J targets to become F adds six half-width reversal
calls, unless a proved caller layout absorbs them. That particular wrapped
recipe costs `F+4B+6Q` before outside work and loses against `3F` for B>=F.

Even a constructive upper bound B<=2F from separate role calls is insufficient
to prove strict improvement, and it is not a lower bound on a novel supplier.
If a larger-alphabet physical cap-two implementation also applies directly to
J_13, two roles can be batched directly and the comparator improves again to
`F+ B` (with F now the complete rank-one J price), subject to its actual ABI.

## Exact conditional power-tariff screen

This subsection assumes a declared **accounting model**, not a source physical
claim: at fixed logical volume, F=K*f^tau, Q=K*floor(f/2)^tau,
and a hypothetical cap-two owner invocation is priced B=2^tau*F.
K>0, `tau=1-C`, `H_0=0`, and Delta=0 for the recursive comparison.
In particular, the expression B here is a hypothetical tariff; it is not an
identification of scalar owner rank two with recursive child rank two.

Put x=2^tau. For every integer f>=2,

```
Q/F <= 1/x,
(new - direct-upper)/F >= 1+4x-(3+6/x)
                         = 2*(2x-3)*(x+1)/x.                (2)
```

The bound is attained at even f, so it is sharp uniformly over integer widths
for this tariff model. At odd f the floor only strengthens exclusion. At f=1,
Q=0 and direct cost is 3F, which is cheaper still in the screened domain.
The exact transition in (2) is x=3/2, equivalently
`C=log2(4/3)`. This is a tariff/comparator transition, not a κ ceiling.
For x<3/2 the sign can reverse, preventing a universal rejection.

Declare the screen domain **0<=C<=17/5000=.0034**. Then
`tau>=4983/5000`. The exact integer inequality

```
399^5000 < 2^4983 * 200^5000
```

proves x>399/200 throughout the domain, without floating point, logarithm
evaluation or extraction of the unchanged #4610 crossing. Consequently

```
B/F > 399/200,
necessary break-even B/F < 1/2+3/(2x) < 333/266,
(new-direct-upper)/F > 19767/6650 > 0.        (3)
```

The last expression follows because 4x-2-6/x increases for x>0 and its value at
399/200 is 19767/6650. Thus the nominal concave-power price is decisively too
expensive even though it is strictly below 2F. A new physical B must be far
cheaper than that nominal price, or a proved outside-call advantage must pay
the difference. For nonzero Delta the exact threshold remains (1); a negative
Delta of sufficient magnitude could change the complete decision. None is
proved in the inspected physical interface.

## Smallest next test and stopping rule

Before any emitter or native/compiler expansion, provide one actual eligible
caller occurrence with the same autonomous target and spectators, and actual
complete F,Q,B,wNew,wDirect tariffs. Test (1) on that one occurrence, keeping
every dimension, column multiplier and owned/helper credit explicit. Include
the direct J competitor; do not compare only to the restricted six-call word.
Reject expansion if the complete strict inequality fails. If B or overhead is
unknown, retain the missing cost as a blocker. An inequality pass licenses only
the next physical test, not native correctness, compiler or κ admission.

The independent exact checker verifies source hashes, the integer power bound,
the rational factorization, equality and both sign controls, floor cases at
tau=1, and rejection of scalar/address rank confusion and missing complete-cost
declarations. It executes no author formal-word verifier, native program,
compiler, parameter/root scan or Lean campaign.

## Open next questions and credit

1. Does any actual caller require the a/b-only representation while excluding
   the direct J recipe? Specify its eligible occurrence and binding; do not
   assume the formal restricted alphabet is the physical instruction set.
2. Can a physical cap-two invocation beat (1), including its complete returned
   jobs, finite work, actual payload volume, precision and restoration?
3. Only after that gate, does a changed full supplier inventory improve the
   retained #4610 complex moment with funded compiler reserve and outer transfer?

Credit Nick Petalas (#5083 formal word and tariff), Ross Richardson (#2415
GL2/S3 bridge), David Arias (#2738 rank-priced theorem), and the source BIT,
physical/compiler contributors retained in the frozen notes. The sibling
physical worker supplied exact source-interface extraction and corrected the
initial ordinary/reversed ambiguity before this result was frozen. Cao Yifan,
Cinna Davis, zxv, Jacob Alan Sussman and their predecessors retain the compiler
and selected-result credit. Substantial OpenAI Codex assistance. Local only;
publication and independent scientific acceptance are separate.
