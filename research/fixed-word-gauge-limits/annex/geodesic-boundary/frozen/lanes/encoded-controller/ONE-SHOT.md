# Exact restoration for one-use centre modes

This note gives the full joint map for nine fresh mode cohorts in the
retained nine-call controller. It gives an exact content decoder for all
old data and all arbitrary new modes. The decoder has explicit boundary
queries. Its mode-only factors have legal scalar access. The X-bank parts
of the boundary queries still need a priced native implementation. Thus
this is not yet a closed supplier or a new kappa bound.

The active word and its exact adapters come from the history-encoding
lane. The common Walsh frame was developed by residual-syndrome, root,
and interface-proof. The stopped one-use history below removes a final
frame conversion. The root lane independently computed the final bank
responses. This note derives the joint content factorization and checks
it in a free noncommutative operator algebra.

## One-use native histories

Let stage s have completed space U_s of dimension 9+8s. Let Z_s be the
quadratic sign on U_s, and let G_previous be the canonical real Walsh
transform on the even hyperplane in dimension 8s+1. Use the exact base
adapters from history-encoding/WALSH-MODE-PROOF.md. Their monomial factors
M_s and B_out,s satisfy

    B_out,s F_(U_s) M_s = Z_s F_(U_s) Z_s.

For each of the eight arbitrary mode inputs h at stage s:

1. Apply Z_s and then G_previous, with native rank 8s.
2. Apply the type-zero adapted FULL9 active word.
3. Apply Z_s to the mode output.
4. Apply F to the future 64-8s coordinate axes.

The preparation or completion with rank zero is omitted. Each nonzero
one of rank at most 48 is one native child with the stated monomial
adapters. Split rank 56 as 48+8 and rank 64 as 48+16. The native coordinate
transforms on these disjoint blocks commute, so their product is the
unsplit transform with its unchanged outer adapters. The total rank
per mode is 8s+9+(64-8s)=73. A mode need not advance during any other local
call. Reserve its family for this history.

Set z=Z_s u, where u is the mode content in the active Walsh frame. Then
z starts at the arbitrary input h and has physical output F_73 z'. Put

    N_s = M_s Z_s,
    A_s = D_s^-1 K N_s,       B_s = N_s^-1 R D_s,
    K=R^T/4,                 P_s=A_s B_s.

Here D_s is the actual port-dependent cover router, with the exact native
phase adapters. The mode owner uses the call's cover class. The order of
N_s matters: apply Z_s first. The output-adapter identity gives

    F_73 N_s F_73^-1 = B_out,s^-1 Z_s,
    F_73 N_s^-1 F_73^-1 = Z_s B_out,s.

These are exact monomial maps. The operators outside U_s commute with
the future completion. The cover routes have the same property after
their known phase corrections. Thus A_s, B_s, and B_i A_j are finite sums
of monomial maps both at raw boundaries and at common full-F boundaries.
This statement does not replace the old X line phases by the identity.

The active content maps are

    Forward:   x'=x,
               y'=y+(I-A_s B_s)x-A_s u,
               u'=-u-2B_s x.

    Backward:  x'=x-(I+A_s B_s)y-8A_s u,
               y'=y,
               u'=-u-B_s y/4.

In these two formulas u denotes the standardized mode z. The raw word
restores the other 472 helpers. Every cohort is used once, so its output
content is not an input to a later active call.

## The exact global map

Write D for the eight old bank contents, in order X0,Y0,...,X3,Y3. Write
U for the nine mode cohorts, each with eight arrays. The retained
ordinary controller, with identity shears and its signed terminal
exchange, is the identity on D.

The checker reads the local, bridge, and terminal events from
NORMALIZATION-PROGRAMS.json. It does not execute that earlier experiment's
X_factor or Y_factor events. The retained physical translation events
are part of the native frame contract, not extra scalar bank operations.

For stage t, let a_t be the row that selects its source from the ordinary
pre-stage bank state. Let b_t be the final bank response to its mode
increment, including the scalar alpha_t. Define

    alpha_t=1/2, beta_t=2       for a forward call,
    alpha_t=4,   beta_t=1/4     for a backward call.

The local change from the ordinary shear is exactly
alpha_t A_t (u_t'-u_t) in its target bank. This follows directly from the
two displayed active maps. It includes the arbitrary old mode input.

Let L have block column b_t tensor A_t. Let T have block row
beta_t a_t tensor B_t. The literal source and response rows are in
ONE-SHOT.json. They are computed from the pinned schedule, and the
responses agree with root/ONE-SHOT-ERRORS.json. Set

    H=T L,
    N_minus=I+strict_lower(H),
    N_plus =I+strict_upper(H).

Every diagonal block of H is zero. The same-stage ordinary source is
unchanged by its own shear, so the source row times its propagated target
column is zero. Equivalently this is checked directly on all nine source
and response rows.

The complete joint endpoint is

    D'=D+L(U'-U),                                      (1)
    N_minus U'=-T D+(N_minus-2I)U.                     (2)

To prove (1), propagate each local error by the remaining ordinary bank
gates. This uses linearity, with the actual value of each mode increment.
For (2), the source at stage i is its ordinary source a_i D plus the
errors from earlier stages. Since the ordinary final map is the identity,
the coefficient from earlier stage j is a_i b_j A_j. Substitute this
source into u_i'=-u_i-beta_i B_i source. Only j<i occurs. Move those terms
to the left to obtain (2). No relation between different chart operators
is used.

Both N_minus and N_plus are invertible over any coefficient ring: each
strict triangular part has ninth power zero. All coefficients here are
dyadic. No division by 13, 7, or a new algebraic constant is needed.

## Complete content restoration

The following boundary operations restore every arbitrary input if their
data queries have legal native access:

1. Before the controller, set D<-D+L U.
2. Run the nine one-use calls with the retained ordinary bank bridges.
3. At the output, set D'<-D'-L U'.
4. Set U'<-N_minus U'+T D'.
5. Set U'<- -N_plus^-1 U'.

After step 3, equation (1) gives D'=D_original. Substitute the input
D_original+L U into (2), and use H=TL and its zero diagonal. This gives

    U'=-N_minus^-1 T D_original-N_minus^-1 N_plus U.

Steps 4 and 5 therefore restore U exactly. No mode starts at zero, and
no information is discarded. The mode-only Schur factor is

    -N_minus^-1 N_plus,

with an explicit inverse. A favorable bound on its rank is not needed.

The triangular part has an in-place implementation. To multiply by
N_minus, process target cohorts from 8 down to 0; all lower source cohorts
then retain their old values. To apply N_plus^-1, again process from 8
down to 0 and use the already solved higher cohorts. Each block shear has
the form

    u_i <- u_i+c_ij B_i A_j u_j,       i != j.

The table has 36 nonzero lower and 36 nonzero upper queries. Each query
can use direct monomial ADDs from cohort j to cohort i. It needs no clean
array. The pinned R has four nonzero entries in each of its 112 columns,
so B_i A_j has at most 112*4*4=1792 monomial terms. The two triangular
passes therefore need at most 129024 dyadic monomial ADDs per replica,
plus 72 final array negations. This is a finite macro bound. Address,
phase, arithmetic-format, and real-primitive costs still need a complete
supplier invoice.

The two L boundary maps have 28 bank-to-cohort blocks each. The final T
query also has 28 such blocks. Each has 448 monomial terms before any
combination of equal terms. The resulting bound for all boundary content
operations is 166656 dyadic monomial ADDs and 72 array negations. The
native cost of the X terms is not included in this macro count.

## A smaller decoder from legal local corrections

The residual-syndrome lane proposed a local preload to reduce the decoder.
The native frames require different operations in the two orientations.
Before each forward raw word, add
R^T u/8 to Y. Y and the mode then have the same zero frame. After each
backward raw word, subtract R^T u_out from X. X and the mode then have the
same FULL frame. Each change has 448 ADDs and no native child. The exact
stopped-Walsh adapters carry these changes to the routed A_s operators.

Do not put the same preload before a backward word. Its X input has the
extra C_p frame, so that different operation has no stated free access.

The forward error now equals +alpha_s A_s u_s'. The backward error equals
-alpha_s A_s u_s. Let P select the forward, even-numbered cohorts, and let
Q=I-P select the backward, odd-numbered cohorts. These letters P and Q in
this paragraph are mode selectors, not the port matrix P_s or line Q.
The modified joint equations are

    D'=D+L(P U'-Q U),
    (I+lower(H)P)U'=-T D-(I-lower(H)Q)U.

The proof is the same causal substitution as above, with each earlier
mode increment replaced by P U'-Q U. Set

    N_F=I+lower(H)P,       N_B=I+upper(H)Q.

Use only the following data corrections:

    Before: D<-D+L Q U,
    After:  D'<-D'-L P U'.

They restore the old data, and the remaining mode equation is

    N_F U'=-T D_original-N_B U.

The full mode decoder is therefore

    U <- -N_B^-1 (N_F U'+T D_original).

Both triangular factors again use in-place mode shears. There are now
twenty lower queries and sixteen upper queries. The initial data
correction uses only four backward cohorts; the final correction uses
only five forward cohorts. The stage-zero final column has no X support.
Thus each boundary X injection uses 32 mode columns, with ten nonzero
bank blocks. The final source query T still has eight X blocks.

The total macro bound falls to 93632 dyadic monomial ADDs per replica,
including the 4032 added local ADDs, plus 72 mode negations. The recursive
child invoice is unchanged. The verifier checks this full modified word
and its complete restoration separately from the unmodified word. The
history-encoding lane emitted the two added local scalar rows in
ONE-SIDED-MODE-PROGRAMS.json.gz. The uncompressed payload has SHA-256
89bac9604fd59308e75766a01adb1bad4eccf88b635c1f662c99d8874faaaa2e.
Its all-704-column replay passed, including all 472 ordinary helpers.
The interface-proof lane also reviewed the literal word. Its scalar
primitive bounds are 210690 forward and 208002 backward; both have rank
mass 5522. The X parts of these smaller boundary corrections remain
the concrete construction obligation.

## A direct inverse at one common output frame

There is a smaller scalar decoder when a separate construction brings
all old data and all modes to the same full-F output frame. Reverse the
modified controller skeleton, including its bridges and signed terminal
exchange. For a forward local call, use these operations in order:

    y <- y-x-A_t u/2,
    u <- -u-2B_t x.

For a backward local call, use these operations in order:

    u <- -u-B_t y/4,
    x <- x+y+4A_t u.

The second backward row uses the restored input mode. These are the exact
local inverses of the one-sided words. They use two 448-term monomial
queries and one 112-entry ordinary bank ADD each. All coefficients are
dyadic. The decoder does not need private array scratch or clean arrays.

The nine local inverses use 8064 monomial-query ADDs and 1008 ordinary
ADDs. The nine inverse bank bridges use 2016 further ordinary ADDs. Thus
the complete decoder uses at most 11088 dyadic monomial ADDs per replica,
72 mode-array negations, and the four inverse signed bank exchanges.
The latter include 448 array negations. All A_t and B_t operations use
their exact full-F monomial conjugates. Address and phase costs remain
part of the implementation invoice.

The signed terminal exchange can instead use three arithmetic shears on
each array pair: `x-=y; y+=x; x-=y`. With this lowering, the full decoder
uses at most 124688 real dyadic primitives per replica. This bound includes
the scalar coefficients and the mode negations. It excludes monomial
address and phase computation. If each input real and imaginary component
has absolute value at most B, every intermediate component has absolute
value at most 7521998513 B. An input grid with p fractional bits requires
at most p+11 fractional bits in this exact decoder. Thus 33 extra magnitude
bits and 11 extra fractional bits suffice for the standalone decoder.
These bounds do not include growth from the preceding coupled circuit.

The ordered inverse program is in ONE-SHOT.json. The verifier checks it
as both a left and a right inverse over the free operator algebra. This
decoder avoids the initial L preload and the separate Schur queries; the
Schur factorization remains useful when only some boundary queries have
cheap native access.

A concrete but unprofitable normalization gives the required common
frame: apply Q to each old X input, run the one-sided controller, and
apply Q^-1 to the postterminal old X outputs. Then apply the direct
inverse. This returns the full F transform of every old and new arbitrary
input. The two unfused normalizations cost 896 rank-one children per
replica. They cancel the original 320 deficit plus the new 576 allowance.
The original 320 equals 4*2*112-9*64: the 896 endpoint line ranks exceed
the nine calls' centre cost by 320. The pinned local bill gives the centre
cost 64 as 5586-1792-3730. The separate source-domain GEODESIC proof shows
that 896 is also a lower bound within the retained persistent wire paths
with these common input and output frames. That proof rules out a gain
from frame fusion alone in this route. A different boundary encoding or
content controller is needed. The two-normalization invoice
belongs to this common-frame route, not to two independent conjugations
of the initial and final Schur corrections.

## The exact remaining source-access obligation

The old X logical inputs have physical type Q=diag(C_p), and their final
type is F_73 Q. The old Y types are I and F_73. Modes now have types I and
F_73. Thus every Y part of L or T has monomial access at the relevant
boundary. An X part of L needs Q A_t at input, or F_73 Q A_t F_73^-1 at
output. An X part of T needs B_t Q^-1, with its full-F conjugate at output.

The source row a_t has exactly one X bank for t=0,...,7, and none for t=8.
Hence T has eight X queries and twenty Y queries. L has twenty X queries
and eight Y queries. The smaller decoder uses each L column at just one
boundary. The labels, signs, and bank indices are all explicit
in ONE-SHOT.json. The source extractor T D cannot be omitted after the
old data is repaired: then the modes still contain a nonzero old-data
term. The checker has a negative control for this omission.

The common-frame route above costs 896 rank-one boundary children per
replica before fusion. It is an upper bound for one repair, not a lower
bound for the factored boundary problem. A useful construction must use
the query structure, intermediate access, boundary fusion, a different
code, or another paid method.

## Conditional recursive invoice

Each of the nine calls promotes eight old helpers. Retain every old owner
job by the exact rank-nine backfill in history-encoding/HOSTING-PATCH.json.
The nine fresh cohorts give 72 new full output families per replica. The
unsplit preparation and completion profile has 16 children of each rank
8,16,...,64. The retained native admission requires 73^2>2*r_max^2, so the
rank-56 and rank-64 children cannot remain in that form. The exact splits
stated above give the admitted profile

    {8:32, 16:32, 24:16, 32:16, 40:16, 48:48}.

The maximum rank is 48, and 73^2-2*48^2=721. The total rank is unchanged.

Per replica, the change is:

    remove 72 rank-eight centre children:       -576 rank,
    add 72 old-owner rank-nine backfills:        +648 rank,
    add all new mode preparations and tails:   +4608 rank,
    add 72 full output families:                +5256 productive rank.

The paid rank increase is 4680. The provisional deficit gain is 576 per
replica, or 9216 across 16 replicas, before the boundary source repairs.
The stock becomes 15978 families. The higher-rank children, the larger
stock, scalar work, and boundary repairs must all enter the full recurrence.
This rank difference alone is not a kappa calculation.

## Verification

Run from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/verify_one_shot.py \
  --schedule work/centre-encoding-campaign-20261014/lanes/encoded-controller/NORMALIZATION-PROGRAMS.json \
  --responses work/centre-encoding-campaign-20261014/root/ONE-SHOT-ERRORS.json \
  --out work/centre-encoding-campaign-20261014/lanes/encoded-controller/ONE-SHOT.json
```

Expected status: PASS_EXACT_ONE_SHOT_JOINT_SCHUR_AND_RESTORATION.
The verifier uses exact rational coefficients and free noncommutative
symbols A_t and B_t. Its 17 independent input blocks represent all 968
arbitrary old and mode arrays per replica. It checks both joint equations,
the triangular inverses, and every step of the full content restoration.
It also rejects removal of the mode decoder or its old-data source query.
This is an operator identity check, not a replay of a global native word.
The native one-use histories have a separate review in interface-proof.

Prepared with substantial OpenAI Codex assistance and coordinated agent
research. No independent human review is claimed.
