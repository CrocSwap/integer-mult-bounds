# Static binding of the finite merged flow to its integer law

**Conditional source-level PASS.** On the precise default domain below,
`Flow.merged()` implements an exact finite integer inventory law, including
both presence imbalances, every terminal paid letter, rank-one telescoping
and its stated unit/source-count bounds. No scientific execution, source
import, constructor, test, mathematical program or peer-proof reading was
performed. This is a source-aware external written code-to-law review,
not a native census or a new physical/analytic admission.

## Pinned source and domain

Read only the actual constructor, column/points/units/demand and merged code
at lines18–135 of source `flow.py`; the literal/class-limit replay and
floating exploratory helper are outside the target. Raw source is8971B,
SHA256 `460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a`,
Git blob `07175cd6e1f2c2367c2e78eca7f163fef18d301d`, from PR6713 head
`cd666f05c4e9006025b634687cc493911c8371c8`. Length/SHA/Git content ID were
checked as inert bytes. The author/source proof already states finite flow
identities; the contribution here is the explicit source-to-law connection.

Let T and P be fixed nonempty finite maps, with distinct integer target keys
k>=2 and paid keys r>=1, and positive integer multiplicities. Let

    m=max supp(T), k0=min supp(T), rmax=max supp(P)<m,
    n be an integer >=m, C=floor(n/m),
    G=max{g>=0:k0^g<=C}, W=sum T_k, B=sum P_r.

Use only `extra_height=0,height_base=None`; do not mutate the Flow object or
its exposed cached dictionaries between calls. The default constructor
lines27–35 computes exactly this C and G, including G=0 when1<=C<k0.
This domain is stronger than the constructor's validation: it does not check
every key is a positive integer or that n is an integer; Python `isinstance`
also admits booleans as integer values. Thus its `need` guards are not an
admission theorem for arbitrary supplied mappings. For example T={2:1},
P={0:1},n4 passes the displayed key-maximum/value checks but would divide
by zero at a nonterminal child; this invalid-domain case is not a defect in
the restricted law. Nondefault height settings are not covered by this note.

## What points and demand actually enumerate

For a nonnegative integer vector a indexed by sorted target keys, put

    |a|=sum a_k, c(a)=product k^a_k,
    u_h(a)=h!/(product a_k!)*product T_k^a_k  if |a|=h.

The recursive enumeration in lines47–58 chooses each a exactly once. Its
successive binomial factors telescope to h!/(product a_k!), and its powers
give the indicated T weight. Thus `points(h,cap)` returns exactly the
positive integer u_h(a) with c(a)<=cap. Pruning `new_c>cap` is valid because
increasing count multiplies by k>=2. Its zero-cap case returns no units;
height0/cap>=1 returns exactly a=zero with weight1.

At depth j and paid product rho, `units` is therefore

    U_(j,rho)(a)=u_(G-j)(a) * 1[rho*c(a)<=C].

This uses the exact integer equivalence
`c(a)<=floor(C/rho)` iff `rho*c(a)<=C`, with rho>=1. It does not approximate
the nested floors by n/(m*rho). In particular
`floor(floor(n/m)/rho)=floor(n/(m*rho))`, but all source code paths retain
the actual integer cutoff C.

`demand(j,rho)` increments each unit's target coordinate and multiplies by
that target's inventory. Its type-b count is exactly

    D_(j,rho)(b)=sum_(i:b_i>0) T_i*u_(G-j)(b-e_i)
                          *1[rho*c(b-e_i)<=C],  |b|=G-j+1.

There is intentionally no extra cap test on c(b) itself. A demand rank can
be up to m*C, since the primitive's target is k times its column. Imposing
the unit cutoff on demand types would silently delete actual target jobs.
Different vectors with equal column product are allowed; Counter aggregation
adds their integer multiplicities without requiring multiplicative
independence of target keys.

For any b of degree h>=1 the uncapped weighted Pascal identity is

    sum_(i:b_i>0) T_i*u_(h-1)(b-e_i)=u_h(b).

Each summand is (b_i/h)*u_h(b). Child demand at paid product rho*r keeps
only some nonnegative terms of this identity. Consequently, **whenever the
parent type b is present**, child demand never exceeds its full parent
supply. This proves exactly the assertion at line110: demand>supply can
occur only when parent supply is zero. It does not assert equality in the
capped case and does not rule out child-only presence.

## Merged paths, cancellation and pruning

At depth j, `path_counts[rho]` is the sum of product multiplicities
`product P_(r_i)` over ordered paid words of length j with product rho and
retained prefix products<=C. Multiplication of positive integer paid ranks
is monotone, including rank1. Thus a word whose new product exceeds C can
never regain a unit at any later depth: its cap floor is already zero.
The `following` test at lines99–100 safely prunes precisely those words.
Different paid words with the same product may merge because every future
unit/demand depends only on depth and rho and all counters are linear in
their accumulated multiplicities. This is an inventory statement, not a
new chronological or physical scheduling proof.

The code does **not** prune merely because the current batch is empty, and
must not. Height decreases while a later paid rank can be1, so an empty
batch can regain units. The parent/child union at line101 must therefore
cover all four possibilities:

- Both present: child demand is at most parent supply by partial Pascal;
  the minimum matches whole equal-rank jobs, and a strict surplus exits.
- Parent only: its entire paid supply exits and is marked boundary.
- Child only: missing target jobs become new sources, not discarded work.
- Neither: there is no contribution.

Each contribution is multiplied by the actual parent-path multiplicity and
P_r. `following` is updated regardless of current batch emptiness. For a
nonterminal new product>C, child demand is empty, so no omitted child unit
or target is concealed by the safe product pruning.

At depth G, units have degree zero. The terminal loop lines94–97 retains
**every** paid letter as an exit, even when rho*r>C. The unit cap restricts
which current columns exist, not which paid outputs of those columns must
be returned. This is the terminal counterpart to retaining whole child
demand rather than independently capping its target rank.

## Complete finite mirror identity

For a unit (j,rho,a) with column z=rho*c(a), its target inventory is
T_k jobs of rank k*z and its paid inventory P_r jobs of rank r*z. Sum with
the exact unit multiplicity over every retained node/path. At each internal
edge the matched minimum cancels jobs of the same vector type and rank;
leftover paid jobs become exits and missing target jobs become sources.
Root demand is sourced in full, and terminal paid jobs exit in full.
Therefore for **every** real-valued function f on the finite ranks,

    sum_s sources[s]*f(s) - sum_e exits[e]*f(e)
      = sum_(j,rho,a) paths_(j,rho)*U_(j,rho)(a)
            * (sum_k T_k*f(k*rho*c(a))
                         - sum_r P_r*f(r*rho*c(a))).

Taking f to be each rank indicator proves the full signed integer inventory
identity, stronger than only a numerical mass assertion. Setting f(x)=x
gives exactly lines122–125:

    mass(sources)-mass(exits) = Delta*column_mass,
    Delta=sum k*T_k - sum r*P_r,
    column_mass=sum paths*U*rho*c(a).

Setting f=1 also yields source_count-exit_count=(W-B)*units. No positivity
of Delta is required by this generic finite identity. The actual claimed
Delta608 needs the separately pinned caller inventories; it cannot be
deduced from the generic class or rmax<m alone. No analytic limit,
normalization, local-limit theorem or asymptotic saving is used here.

## Source, exit and boundary rank bounds

Sources are nonempty: the root unit at a=(G copies of k0) exists since
k0^G<=C and has positive multiplicity, so root demand supplies positive
target jobs. A root source s=k*c(a) satisfies s<=m*C<=n. Its degree is
G+1, hence s>=k0^(G+1)>C, so integer s>=C+1>n/m.

For a child-only source type b on edge r, some predecessor a=b-e_i is
present at child product rho*r, and therefore

    s=rho*r*c(b)=k_i*(rho*r*c(a)) <=k_i*C<=m*C<=n.

Its parent type is absent, so rho*c(b)>C. Integer ranks and r>=1 imply
s>=rho*c(b)>=C+1>n/m. Partial Pascal ensures there are no additional
positive source differences with a present parent. Thus every returned
source has1<=s<=n and m*s>n, exactly the default top-source bound.

Every paid exit comes from an actually present unit b (or the degree-zero
leaf), with rho*c(b)<=C. Hence e=r*rho*c(b) obeys

    1<=e<=rmax*C<=rmax*n/m<n.

All terminal paid exits satisfy this even when their new paid product is
greater than C. The `boundary` subset contains only premature nonterminal
paid surplus. If this surplus is positive, at least one Pascal predecessor
term with b_i>0 was omitted: rho*r*c(b-e_i)>C. This quantity is an integer,
so it is at least C+1. Therefore

    e=k_i*(rho*r*c(b-e_i)) >=k_i*(C+1)>=k0*(C+1)>k0*n/m,

which proves m*e>k0*n at line120. The integer divisibility step is essential:
the weaker statement e>k0*C alone would not justify the bound at a
nonzero n mod m. All three rank checks are consequences of this exact
capped code, not extra optimistic filters applied after the accounting.

## Unit and source budgets

At depth j, total retained paid-word multiplicity is at most B^j. The sum
of capped unit weights is at most the full multinomial W^(G-j). Therefore

    units <= sum_(j=0..G) B^j*W^(G-j).

There are exactly W target jobs per actual primitive unit. Returned sources
are a subset of these jobs after matching removes whole jobs. Consequently
source_count<=W*units. These are full integer count bounds, not probabilities,
floating estimates, host-time bounds or a native unit-cost invoice.

## Hand-derived discriminating controls, not executed

1. **Do not prune an empty batch.** Take T={2:1,5:1}, P={1:1,3:1}, n40.
   Then C8,G3. At depth1,rho3 the height2 batch is empty (minimum column4
   exceeds floor(8/3)=2). The following rank1 child at depth2,rho3 has its
   height1 column2 unit present. Its target type(2,0) has rank12 and is a
   genuine missing-parent source. Dropping the empty depth1 batch loses it.
2. **Do not cap terminal outputs.** In the same example the depth3 word
   with product rho3 has a degree-zero unit. Its terminal paid rank3 emits
   exit9>C8, which still fits the actual required exit domain9<n40. Dropping
   this paid letter changes the finite inventory identity.
3. **Present supply need not equal demand.** With the same T/P and n50,
   C10,G3, depth1/rho1 has type(1,1), column10, supply2. On paid rank3 the
   predecessor column5 is absent at product3 while column2 is present;
   demand1 leaves one boundary job at rank30. Treating capped Pascal as
   equality would erase a real exit.
4. **Constructor value guards are not key admission.** The P0 example above
   violates the external positive-rank contract despite passing displayed
   constructor checks. Noninteger/negative paid keys, nondefault heights,
   mutable cached objects and arbitrary malformed inputs are not silently
   added to this theorem.

These are written consequences of the code and elementary integer algebra,
not newly run fixtures. The `literal` method's paid-word chronology/class
limit and `approximate_leaves` floating recurrence are explicitly unreviewed.
Native supplier chronology, paid/productive pricing, the actual Delta608
caller, analytic propagation and all selected frontier assumptions require
their own bindings. No source program or new scientific program ran here.

Credit the actual flow authors/source (zxv with substantial OpenAI Codex
assistance, retaining Jacob Alan Sussman's separated multinomial lineage),
current PR6713/alephnan source custody and all pinned caller predecessors.
Prior PR6729's conditional analytic argument remains a separate predecessor,
not a re-executed or replaced result. This note adds external source-aware
code-to-finite-law review only; no independent human, maintainer or kernel
acceptance is implied. Apache-2.0/source attribution remains retained.
