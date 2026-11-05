# Static review of the actual nested compiler and its width policy

**Conditional source-level PASS.** `compile_counts` implements the stated
strong-induction count recurrences under its default nested replication
policy. The proposed uniform width lower/upper bounds apply to that exact
policy and fixed raw-p7 dictionaries. They do not lower-bound optimal or
arbitrary compilers, establish a paid-leaf saving obstruction, or admit a
native physical invoice. No import, execution, constructor, checker,
mathematical program, compilation, experiment or peer-draft reading occurred.

## Exact source and scope

The reviewed canonical main is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, with actual
`research/direct-mixed-flow/verify.py`, inert alias verify.py.txt:
13,533B, Git blob `df9ca12ad0dae5437ed7d65688e962b9abda5af4`, SHA256
`9ae067eadf17ff9d97737805eb642a69375a5ff2ddb08988fef59aa0771f9b7c`.
The original six source objects (132,276B) and added PR4476 README context
(seven objects total134,692B) were authenticated as inert length/SHA/Git
bytes. The earlier six-object manifest remains preserved.

This review targets lines57–102 and their actual default `Flow(...).merged()`
call, with the raw dictionaries selected in lines211–213. It does not adopt
the source's verify()/finite-census results, the target-failure observation
at1000, inherited_rank_size_bound/native blobs, chronology or physical
allowances merely because their text was read. Flow, raw-p7 data and source
README were previously exposed; this is source-aware written code binding,
not discovery of the original compiler theorem or independent execution.

Fix the exact raw T/P throughout the loop. Their positive integer keys/
multiplicities give minimum target5, maximum target m=121, maximum paid48,
W=7688, P=55998 and Delta=608>0. These are dictionary-data premises and
elementary sums, not an independent proof of native inventory origin. Let
`maximum=N` be an integer>=121, use `force_unit_replication=False`, and do
not mutate input/cached state during the call. The source does not validate
all foreign API types; no such admission guarantee is added here.

The finite Flow laws used below are exact whole-integer source/exit support,
positive columns, rank-one cancellation and full multiplicity counts. They
are the previously exposed written source-law boundary, not a probabilistic
relaxation or a scientific result inferred from nine finite tests.

## 1. What the arrays and loops really represent

Use B_n,L_n,U_n,C_n,R_n for widths, leaves, units, columns and slots. Below
m, lines61–65 initialize, including rank0,

    B_e=1, L_e=e, U_e=C_e=R_e=0   (0<=e<m).

For each actual n>=m let the local Flow output have source histogram S_s,
exit histogram E_e, source multiplicity S_n=sum_s S_s, local unit count u_n
and local column mass c_n. Distinguish these local counts from the fully
expanded U_n,C_n arrays. The code sets

    a_n=B_(n−1), B_n=a_n*S_n,
    U_n=a_n*u_n, C_n=a_n*c_n,
    R_n=a_n*(S_n+sum_e E_e+(W+P)*u_n), L_n=0

before adding smaller subprogram records. A source occurrence of rank s
recurses at rank e=n−s; a paid exit recurses at its rank e. Their multiplicity
c yields exactly `copies=c*(a_n//B_e)`. All four record arrays receive that
many copies of the smaller record. Even if different occurrences lead to
the same rank, the code adds all copies; it does not deduplicate them.

Every recursive rank is strictly smaller: sources have1<=s<=n and exits
have1<=e<n. Hence complements include e=0, but never n. That proves line78
under the finite-flow domain. It is not an extra rank cap imposed after
accounting and does not delete terminal paid rank48 at low column caps.

## 2. Whole batches and strong-induction identity

All B_e are positive integers. Base widths1 divide every integer. If widths
through n−1 form a divisibility chain, every B_e with e<n divides
a_n=B_(n−1). Thus all child `copies` are whole integers. Since S_n is a
positive integer, B_n=a_n*S_n is again a multiple of B_(n−1), proving the
chain and both line79/83 guards for every finite N by strong induction.
The code chooses a concrete nested product rather than an LCM of just
the presently used child widths; no minimality follows.

Assume the smaller identities B_e*e−L_e=Delta*C_e. Substituting the actual
copies from both histogram loops gives

    B_n*n−L_n
      = a_n*(S_n*n−sum_s S_s*(n−s)−sum_e E_e*e)
                     +Delta*sum_children copies*C_child
      = a_n*(sum_s s*S_s−sum_e e*E_e)
                     +Delta*sum_children copies*C_child
      = Delta*(a_n*c_n+sum_children copies*C_child)
      =608*C_n.

The base identity is zero=zero, including rank0. This proves line84 for
the fully expanded records rather than only for one local flow. The actual
code includes the child's column count at line82, so this is genuine
expanded telescoping at the count level.

Nonnegative leaves imply C_n<=B_n*n/608, and integrality gives the exact
floored upper bound used in line85. Every local raw column is a positive
integer, so u_n<=c_n; smaller U_e<=C_e and nonnegative whole copies give
U_n<=C_n. No physical center/allocation theorem is inferred from naming an
integer array `units` or `columns`.

At n121 the local height is0: S=T, E=P, u=c=1 and a=B120=1. Source rank121
has224occurrences. They create rank-zero complement calls with L0=0, but
still count in S_121=W and hence B121=W. Dropping those source occurrences
from the denominator/width would leave the child leaf sum unchanged while
changing B121*121 by224*121. Zero complement leaves do not make productive
source occurrences dispensable or free. The unchanged symbolic identity is
L121=121*W−608, U121=C121=1.

## 3. Slots and the normalized leaf recurrence

An actual local unit supplies W target jobs and P paid jobs. Every source
is an unmatched target and every exit an unmatched paid job, so

    S_n<=W*u_n, sum_e E_e<=P*u_n.

Therefore the line74 local slot term is at most2*(W+P)*a_n*u_n. Adding the
child slot records at line82 and applying their inductive bounds yields

    R_n<=2*(W+P)*U_n.

The local identity can also be expressed as source+exit+target+paid slots
=2*(W+P)*local_units−2*local_matches. The global proof requires the child
slot accumulation, not only that one-flow identity. These are symbolic
whole-job adapter/movement positions. Native lowering, ownership, scalar
heights, initialization/erasure, stock and execution tariff require their
own admitted implementation and cannot be assigned a universal unit cost
from this count bound.

Let ell_e=L_e/B_e. Dividing the actual leaf recurrence by
B_n=a_n*S_n cancels the common replication factor and gives

    ell_n=(sum_s S_s*ell_(n−s)+sum_e E_e*ell_e)/S_n,
    ell_e=e for0<=e<m.

This is exactly the source README normalized recurrence. Retaining e=0
in the source multiplicity remains necessary even though ell0=0. Any
alternative **valid** replication policy changes integer widths/total
records but leaves this normalized recurrence unchanged. Consequently a
width-growth obstruction for the old policy is not a proof that the
normalized paid-leaf saving is asymptotically impossible.

## 4. The candidate uniform width bounds fit the actual code

Let M=N−m+1 and

    G_n=max{g>=0:5^g<=floor(n/121)}, H_N=sum_(n=121..N) G_n.

Default lines69–70 and base widths give the exact equality

    B_N=product_(n=121..N) S_n.

The root batch always contains its all-minimum-target unit of degree G_n:
column5^G_n fits the cap and its multinomial weight is420^G_n, since T5=420.
Every such root unit contributes all W target jobs to the initial source
demand; matching never cancels an external root target. Counter aggregation
preserves multiplicity even when ranks coincide, and later missing sources
only add nonnegative counts. Hence

    S_n>=W*420^G_n,
    W^M*420^H_N<=B_N.

This is a count of original unit/source occurrences, not a count of distinct
types. Replacing source_count by the number of histogram keys would destroy
the premise and would not describe this code.

The full local unit budget gives

    S_n<=W*sum_(j=0..G_n) P^j*W^(G_n−j).

For this raw profile P>W, the finite geometric sum is
`(P^(G_n+1)−W^(G_n+1))/(P−W)`, which is strictly less than
`P^(G_n+1)/(P−W)`. Thus the proposed weaker closed product bound is valid:

    (P−W)^M*B_N <= (W*P)^M*P^H_N.

All terms are positive integers; no floating geometric estimate or
division-by-zero P=W case is used. The strict per-step inequality is
available here, but the displayed weak upper bound is sufficient.

These bounds fit exactly the source's old nested policy. They do not
assert that every legal compiler must multiply by B_(n−1), nor that raw
P/W satisfy the same relation for unrelated separated/homogeneous rules.
The source's existing coarser C_N envelope follows as well: all local
heights through N are at most G_N, S_n<=C_N, so B_N<=C_N^M<=C_N^N.
The README already states that upper bound and expanded telescoping; those
author claims are not reintroduced as new discoveries.

## 5. Exact floors, asymptotics and the finite-window limit

Integer floor equivalence gives

    G_n=floor(log_5(n/121)),
    H_N=sum_(g>=1) max(0,N−121*5^g+1).

The latter is a finite exact sum counting each threshold crossing. In
particular G(3000)=1 and height2 begins at3025=121*25. Small finite data
below that threshold cannot see the next layer of this policy.

The elementary floor bounds show H_N differs by at most M from
`sum_(n=121..N) log(n/121)/log5`. Integral bounds on the increasing log
function give `sum_(n=121..N) log n=N log N+O(N)`. Therefore

    H_N=N log N/log5+O(N).

Taking logs of the two product bounds establishes

    log B_N=Theta(N log N),
    liminf_(N->infinity) log B_N/(N log N)
                       >=log420/log5=log_5(420)>3.

The final strict inequality is exact because420>5^3=125. It excludes a
limiting coefficient near2 (or any proposed limiting value<=3) **for this
one default nested policy**. It does not contradict finite values through
2000/3000, prove existence of an exact limiting coefficient, or give an
optimal/universal batching lower bound. The upper product similarly gives
a finite limsup bound by logP/log5; it does not identify the actual limit.

## 6. Written discriminating controls and explicit exclusions

All controls below are hand-derived and unexecuted:

- Discarding the224rank-zero source complements at n121 changes the width
  and breaks the expanded identity, even though they add no leaves. The
  source code correctly keeps their source_count and loops through e0.
- For the raw rule a=1 happens to give legal integer children through
  n122, since every child is below121. It gives B122=W rather than the
  default W^2. This is an explicit reason not to extend the default-policy
  lower bound to every replication choice. By n126, the rank5 source has
  complement121 with width B121=W>1, so a=1 fails the actual divisibility
  guard. A valid all-rank alternative needs its own batching proof.
- Counting only current local slots/units discards the records added by
  line82. It cannot justify the expanded bound for a rank with a compiled
  child. The actual code accumulates all four child arrays.
- Replacing exact G by a smooth logarithm before the product loses integer
  threshold information. A finite near2 observation with G<=1 is not an
  asymptotic counterexample to the uniform lower bound.

The added PR4476 README explicitly excludes its coverage of expanded
telescoping; it covers its own finite width/local-slot/growth observations
(including levelling-off language), not the new uniform lower proof. The
canonical PR4436 README itself already claims expanded telescoping and the
coarse upper envelope. Related4507/4586 chronological batches,6612
homogeneous LCM/gcd analysis and5318 separated flow are different scopes;
raw paid48>=minimum target5 is not the separated hypothesis. None is
silently substituted as a proof of this raw mixed policy or its optimum.

The result is a written actual-code connection and a policy-specific growth
qualification. Source native inventory origin, arbitrary-input/whole-job
adapters, physical control/ownership/stock/erasure, native records, compiler
precision/tape, analytic/onset/outer recovery, full supplier and all five
selected assumptions remain unadmitted. No κ/frontier, merge or adoption
change follows. No human or proof-kernel acceptance is implied.

Credit zxv/PR4436 source compiler/code/theorem/README claims and disclosed
Codex work; Jacob Alan Sussman and retained raw-p7, mirror, chronological
and uniform-program lineage; PR4476 and other listed source-specific
predecessor scopes. Prior6741written finite-law and6742bounded histogram
work remain separate, not recounted as new results. This review uses
substantial source-aware OpenAI Codex assistance, not independent source-
unexposed discovery or executed native evidence. Source notices/license
remain retained.
