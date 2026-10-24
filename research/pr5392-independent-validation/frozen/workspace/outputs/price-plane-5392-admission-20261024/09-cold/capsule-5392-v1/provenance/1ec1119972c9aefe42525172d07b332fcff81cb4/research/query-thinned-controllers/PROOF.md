# Query-thinned productive controllers

## Conditional result

Under the retained native, whole-job matching, owned-erasure, tape, analytic,
precision and exact-recovery contracts of #4359/#4416, the construction below
gives

    T(n) = O(n (log n)^(1 - kappa)),  kappa = 37/12500 = 0.00296.

This is a new author-checked conditional construction. It is not an
unconditional theorem, a formal-kernel proof, a practical implementation or a
change to the selected record. It improves #4416/#4433's conditional 0.00268647
by about 10.1818%, and the selected 0.0023 checkpoint by about 28.6957%.
Those percentages compare exponent savings, not running times.

The new mechanism replaces selected full native invocations by copied
rank-one query shears. Losing their productive helpers is charged. Removing
their stage multipliers also removes the corresponding parts of every idle
transform and main target. These coupled changes improve the complete moment;
merely deleting a local bill would not.

## 1. Exact local interfaces

Retain the source local word's all-column interpretation. For complex data,
on each of 112 ports write Q for its central rank-one Gaussian and D_s for
the commuting fresh eight-axis multiplier at stage s. Stage zero instead
uses the source nine-axis multiplier times Q^-1. The forward and backward
physical local maps are

    D_s S_y(Q^-1),   D_s S_x(-Q).

The complete THREE-base supplier has independent helper targets

    {5:28, 6:18, 7:56, 8:93, 9:213}

and unsplit paid profile

    {1:2487, 2:713, 3:224, 4:102, 5:20, 8:8}.

Its 408 helpers are arbitrary original fields. The one sequentially reused
owned center receives no productive credit. These source words and their
all-column/phase evidence are retained unchanged; this contribution does not
repeat their full historical physical replay.

For BIT, retain the PR589 local word on 111 ports and 439 arbitrary helpers.
Each helper target has rank 8, D_s has rank 7, Q is the port's rank-one
projector involution, and the paid profile is

    {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}.

Its nine copied-center episodes remain in that profile. Its rational charts
and common-weight delayed-cover interpretation remain explicit premises.

### The new query-only call

To implement S_y(Q^-1) on arbitrary X,Y, clear one owned stream Z, copy X
into Z, perform Q^-1 on Z, add Z to Y, and erase Z. Return X unchanged and
Z zero. Backward uses Q and subtracts from X. Each port costs exactly one
paid rank-one job, plus the copy/add/erase and fixed matching/routing work.
There is no independent input or output credit for Z.

For complex data Q^-1 is one positive Gaussian followed by its physical
Pauli translation: the Z4 phases -q and q+2q agree. It is not replaced by Q
using an order-two assumption. For BIT Q^-1=Q. The same construction at
column multiplicity f makes a rank-f request; this cost is never treated as
a scalar operation. Erasure is the inherited owned-stream erasure operation,
not a claim about reversible or dirty-borrowed erasure.

## 2. The two actual finite controller words

Start with the credited paired path controller, keeping all middle idle
windows and splitting the initial/terminal windows at a. Let p be the pair
count, with 2p+1 local stages. Keep the full native call at stages

    S = {0, 2p} union {1,3,...,2p-1}.

Replace each other local call by its query-only shear. In every idle word,
remove those same stage multipliers. Every scalar bridge and signed exchange
remains in its original chronological place. Thus there are p+2 full native
calls and p-1 query shears. Thin stages have no fresh axes or helpers.

`controller.py` constructs the words and constant scalar boundaries. The
verifier replays the emitted LOCAL, QUERY_SHEAR, IDLE, ADD and exchange events
directly, compares with the original polynomial specialized by D_s=1 on thin
stages, and checks every coefficient of L A R against the advertised diagonal.
The complex check is over rational Laurent polynomials, with all Q signs
retained. BIT has a separate exact binary group-ring factorization.

Only two finite words are needed:

| Family | p | a | Full native calls | Query shears | Active ambient rank |
|---|---:|---:|---:|---:|---:|
| Complex | 17 | 8 | 19 | 16 | 153 |
| BIT | 16 | 7 | 18 | 15 | 127 |

Unused fresh blocks can be removed by an injective relabeling. All noninitial
complex native contacts occur on the same old-nine plus fresh-eight space;
other blocks are fixed spectators. Exact forward/inverse phase checks on
all 112 ports establish this contact independently of the number of stages.
The initial native call is unchanged. The binary rational 15-dimensional
charts are likewise checked on all 111 ports. Tensoring these identities with
I_f preserves them for each positive column multiplicity under the inherited
all-column implementation contract.

For block rank d and port count v, the main targets are two v-field copies
of rank 1+d(p+2), and two v-field copies of rank 1+d(j+1) for j=1..a and
j=1..p-1-a. The corresponding whole idle ranks are d(j+1), each with 2v
calls. The old one-stage middle idles have become identities. In addition,
there are (p+2) fresh helper inventories, (p+2) native paid inventories, and
v(p-1) paid rank-one queries. Literal and formula-derived ledgers agree.

All helper identities are allocated freshly per full invocation. The main
fields, helpers and suspended centers have distinct physical slots. Scalar
boundary changes are invertible, so independent arbitrary main inputs remain
independent. Thin copies introduce no new sources. Center/query ownership is
retained until the relevant call returns, and every matcher is undone.

The exact invoices are in RESULT.json. Their basic resource counts are:

| Family | Productive fields | Paid jobs | Productive rank mass | Paid rank mass | Surplus |
|---|---:|---:|---:|---:|---:|
| Complex | 11,560 | 72,902 | 258,271 | 257,471 | 800 |
| BIT | 11,454 | 57,555 | 217,506 | 216,753 | 753 |

Both paid and target ranks overlap. They are not directly admitted to the
strict compiler. Raw numerical roots near 0.002960345565 and 0.003464248972
were discovery aids; the argument uses the exact strict tests below.

## 3. Charged tensor completion and splitting

Apply #4416's chronological product construction and #4433's higher-moment
tail theorem to each new native unit. This is composition of actual programs:
copies are paused at the same paid position, a complete child unit runs on
distinct current owners, and it returns before any parent resumes. Correlated
values in distinct slots are allowed. No product of sums of operator matrices
is substituted for this schedule.

Write T_t,P_t for the raw moments, B for the productive field count,
t=1-C, and choose cutoff c, target floor b, u>=C and integer power v.
After the product finishes, complete every rank K<b^v by a paid transform on
b^v-K missing disjoint axes of that same owner. Split every original and
added paid job at c^v, preserving whole-job normalizers around each complete
replacement. The complete normalized paid moment is bounded by

    alpha^v + 2 gamma^v + 2 delta^v,
    alpha = P_t/T_t,
    gamma = P_(t+u)/(c^u T_t),
    delta = B b/(c^C T_t).

The proof and exact disjoint-axis charges are retained in the pinned
`higher-moment-strictification/README.md`. Target completion does not create
inputs, and neither tail is dropped. Rank-one surplus is preserved.

Here both use v=1024 and u=1/5:

| Family | Tested C | c | b | Certified alpha gap |
|---|---:|---:|---:|---:|
| Complex | 0.00296030 | 20 | 21 | alpha < 1-1/30,000,000 |
| BIT | 0.00346 | 17 | 18 | alpha < 1-1/250,000 |

Both gamma<31/32 and delta<19/20. Each of these upper bounds to the power
128 is below 1/16. Therefore both tails at power 1024 are below 2^-32.
Bernoulli gives alpha^v <= 1/(1+v*gap), and the verifier proves
1/(1+v*gap)+4/2^32<1 exactly. Two separate rational interval implementations
agree on the strict raw moment signs. No floating result is used for admission.

The resulting maximum paid rank is c^1024, below the minimum target b^1024.
Both c^64<b^63, and both raw ambient ranks are below 256. Consequently the
retained integer compiler's exit exponent can use h=1/64. For a chosen
uniform saving C_u<C, put t=1-C, z=1-C_u, z0=(t+z)/2 and delta0=z0-t.
A conservative effective bound is

    B0 = (5+8h)*1024,
    D0 = 1+8*1024*(1-z0),
    H0 = ceil((delta0*B0+D0)/(h*delta0)),
    H1 = floor(H0*(1-z0)/(z-z0))+1,  N=2^H1.

The verifier checks the induction and final strict inequalities. Complex uses
C_u=kappa+6d with d=(0.00296030-kappa)/7; BIT uses C_u=0.003459.
The actual integer H0,H1 are in RESULT.json. These specify finite algorithms;
their huge instruction lists have not been materialized.

## 4. The stronger ordinary BIT interface and outer parameters

Keep one external cover weight throughout the entire finite BIT compilation,
including every thin copied query. Lower only the final rank-one leaves.
This retains the source delayed-cover proof instead of normalizing unequal
internal weights for free. Use C0=0.003459 before covering and C1=0.00345
afterward. An odd prime q>2^26*N^5, also avoiding the finite denominators and
rank witnesses, exceeds 256/(C0-C1)*N^5 and pays the complete fallback.

Change the atom power to delta=0.004. With retained old ordinary saving
a_old=0.0000384599, the ordinary saving is exactly

    (1-delta)*C1+delta*a_old = 0.0034363538396 > 0.0034.

Admit 0.0034. The linear adapter has saving delta>0.0034363538396; stock
is sublinear because delta<1-0.0034363538396. The old delta=0.003 fails
this adapter comparison and is explicitly rejected. All compiled dimensions,
role counts, routes, centers and leaf counts replace the old p3 constants in
the delayed-cover stock formulas. For fixed compiled N,B,P, the borrowed
digits remain O(w log e)=o(e), with w=ceil(e^0.004).

Put kappa=0.00296, C=0.00296030, d=(C-kappa)/7, and

    complex_uniform = kappa+6d, b=kappa+5d,
    a=kappa+4d, q=kappa+3d,
    epsilon=1-d, beta=1-3d, r0=d/10, stop=layout=d.

Use the admitted BIT saving 0.0034 in the unchanged nine-row outer ledger.
All 54 named strict predicates and the three retained functional predicates
pass. An additional functional predicate binds the new BIT atom explicitly,
beta*(1-0.004)>0. The smallest outer saving exceeds kappa by
629378373/4900000000000000. Old BIT admission, zero layout, closed epsilon,
closed complex slack and an unfunded endpoint each fail their intended checks.

## 5. Finite constants, precision and scope

No new operation is declared free. Raw scalar programs, signed swaps, copy/
erase records, affine port charts and inverse routes are finite emitted lists.
The conservative raw scalar record bound is 10^9, above the checked local,
query and boundary bills. Every query adds its own paid job and its own
fixed routing records. Initial/end charts and target normalizers are retained.

For a raw unit with productive count B, paid count P and scalar bound L0,
a v-fold chronological product has at most
L0*v*(B+P)^v nonrecursive records before final completion. Its old paid rank
mass is P1^v, and added completion rank is at most B^v*b^v. Bound all new
completion/splitting records by their integer rank masses, then multiply by
10*m^(2v)+10 to cover whole-job normalizers and inverse routes. This is a
constructive finite overestimate, not a claim that those movements vanish.
Allocate a distinct center to each simultaneously suspended instance; a
bound by the total expanded record count suffices. The integer compiler adds
only finitely many effective classes and clears their batch denominators.

Apply the retained semantic-precision and stock prescriptions to these new
finite lists, coefficient heights, prefix row norms, owned centers and
matchers. They are fixed constants before the asymptotic input size varies.
All raw complex boundary coefficients are unit signed scalars; native dyadic
coefficients and BIT rational cover entries retain their pinned bounds. A
brute-force product of per-record row-mass bounds supplies an effective
prefix bound if a sharper bound is unnecessary. Increase the fixed precision
constant and fixed stock coefficient accordingly. The outer slack conditions
are strict, so absorbing these fixed constants does not change their powers.
This inherits the same all-column, physical tape, native movement/repair,
precision, analytic and recovery contracts as the reviewed source; it does
not independently prove that historical implementation stack.

## 6. Sources, attribution, validation and next questions

Canonical baseline: 3a23e9d9d2e67833515d1c60a17e966bcdcab43c, priority
revision 7. Refreshed main and PR checks are recorded in TASK.json. Live
overlap covered all open PR bodies and Discussion pages; sparse local README
coverage and closed-PR-body coverage are incomplete. No novelty theorem is
claimed. #4194's coded/clean local hybrid addresses a different interface;
this construction uses complete native calls and copied rank-one shears.

Credit: zxv for the retained controller/native construction and higher-moment
tail proof (#4359/#4433); Jacob Alan Sussman for mixed-target integer flow
(#4268); Cinna Davis for the p7 paid-completion/native construction (#4416);
DreamingOfClouds, eumemic and their retained PR589/PR555 BIT lineage;
David Ganz, Jeremy Kothe, Rohan Arun, Marius-Paul Dumitrean, Erwan Secousses
and the native/outer contributors named in the unchanged source notices and
the selected contributor map. New query-thinning construction, proofs and
checks were prepared for Cinna Davis with substantial OpenAI Codex assistance.
Apache-2.0. No subagents were used.

Reproduce with the registered command in README.md. Finite source, physical
operator, phase, interval, invoice and outer checks support this written
conditional proof; they do not constitute formal verification. Full old native
word replays, Lean and Docker were not rerun for this contribution.

Open next questions, with first steps and blockers, are in TASK.json. The
next useful audit is the whole-job/owned-query lowering at arbitrary column
multiplicity. The next improvement question is a changed local query/native
alphabet or controller topology. A larger path census alone gives no global
optimality or assurance of a stronger complete construction.
