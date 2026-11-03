# Actual width-one targets with a third dirty role

## The finite statement

There are three arbitrary binary streams, each indexed by one point of F2^2.
The complete payload space is F2^12. A paid call applies either

    a(x0,x1) = (x0+x1,x1),
    b(x0,x1) = (x0,x1+x0)

to one role. Each call, including an inverse or restoration, costs one.
Arbitrary GL3(F2) mixing of the roles, applied identically at all four
addresses, is free. There are no clean inputs, resets, erasure, free address
permutations or unfinished endpoint couplings.

Let P_g be the actual permutation of the four addresses induced by
`g in GL2(F2)`, and let ell(g) be its shortest a/b length. For every ordered
pair g,h, require the full endpoint

    diag(P_g, P_h, I_4).

**Finite certificate.** The minimum paid count is ell(g)+ell(h) for all 36
ordered pairs. Thus a third fully restored dirty role gives no saving for
these targets. The minimum histogram at counts zero through six is

    1, 4, 8, 10, 8, 4, 1.

This answers the first Open next question of ywz65's PR2620. That package
settles two roles; the new computation covers three. The conclusion concerns
all candidate lengths, since every shorter length is exhaustively excluded
and an attaining word is supplied. It is not a census of the entire GL6(F2)
active group, a result for a fourth role, or an all-width theorem.

## Exact normalization of free scalar operations

Every address operation fixes zero. On the three arbitrary payload bits at
address zero, the paid calls act as identity. The required endpoint is also
identity there. The chronological product of free scalar role maps must
therefore be I_3. Moving those maps to one end by conjugation leaves no
residual free factor. This argument uses the actual stream action and never
assumes faithful group-algebra coefficients.

A coordinate paid call has the form

    I + E_jj tensor (P_s + I),  s in {a,b}.

Conjugation by a free scalar Q replaces E_jj by Q E_jj Q^-1. Over F2, all
rank-one idempotents are exactly u v^t with u,v nonzero and v^t u=1.
Conversely, any such projector has image span(u), complementary kernel
ker(v^t), and is a conjugate of a coordinate projector. There are seven
choices for u and four choices for v per u, giving 28 projectors and 56
normalized paid maps. Each map is an involution, since `(P_s+I)^2=0`.

This is a cost-preserving equivalence with the declared free-mixing model.
The same zero-address normalization is credited to ywz65's PR2620/PR2599;
here it is applied to the changed three-role domain.

## The new transfer and mixed-target completion

The six-call natural-image exclusion is prior work. commdata2338's PR1495,
`research/coordinate-cnot-address-spectator/PROOF.md`, Sections 3-4, excludes
every at-most-five-call natural-matrix word for two coordinate SWAP targets
with exactly three scalar roles. Its alphabet has all six GL3 coordinate
CNOTs and all 28 binary rank-one scalar projectors. We cite that finite
exclusion as a premise and do not replay its checker. Its formal theorem
alone would not justify applying it to the present nonfaithful stream action.

The needed actual-module bridge is explicit. On one four-point stream let

    c = e_1+e_2+e_3,
    f_1 = e_2+e_3,   f_2 = e_1+e_3.

Then `F2^4 = span(e_0,c) direct-sum span(f_1,f_2)`. Both labels fix the first
summand pointwise. In the displayed f basis, their restrictions are exactly

    a = [[1,1],[0,1]],    b = [[1,0],[1,1]].

Thus an actual normalized word restricts to the natural two-dimensional
CNOT word on all three scalar roles. Adjoining one fixed address coordinate
per role embeds this as a word in PR1495's natural three-dimensional model,
using only its two labels on coordinates 1 and 2. An actual two-SWAP endpoint
would give PR1495's forbidden natural endpoint. Consequently its inherited
six-call lower bound transfers to this actual-stream boundary. No faithful
algebra representation is assumed and no formal endpoint is inferred.

Now let s=aba be the longest element. Every g in GL2(F2) admits a left
completion c_g with `c_g g=s` and `ell(c_g)=3-ell(g)`:

| g | e | a | b | ab | ba | s |
| --- | --- | --- | --- | --- | --- | --- |
| c_g | s | ab | ba | b | a | e |

If a word for g,h had fewer than `d=ell(g)+ell(h)` calls, append the direct
coordinate completions on the two target roles. The third role is untouched
by these completions. The total would be fewer than `d+(6-d)=6` calls for
two SWAPs, contradicting the transferred natural-image exclusion. The direct
words attain d. This proves the entire mixed-target table. The new step is
this actual-stream bridge and completion argument; the base six-call
exclusion and the formal adjacent-label tariffs retain predecessor credit.

The verifier checks this bridge on all 56 paid maps and all 64 active vectors,
and checks all six completion identities and lengths. The following fresh
certificate corroborates the complete three-role classification directly. It does not rerun any predecessor scientific code.

## Two complete finite computations

The first engine stores the nine by nine binary operator on the three
nonzero addresses in each role. The three zero-address coordinates are fixed
pointwise and have no cross coupling, so these nine rows determine the full
operator. For each u,v and label, `step` XORs the indicated source rows into
the indicated destination rows. It enumerates every transition out of every
state of distance at most two. Breadth-first deduplication uses exact Python
integers, with no digest or probabilistic state equality.

The second engine works directly with twelve full input columns. It
independently enumerates all 168 scalar GL3(F2) bases and conjugates each of
three coordinate role calls of each label. The 1,008 conjugations yield the
same 56 distinct paid operators. It builds a full-column breadth-first ball
by literal linear composition, using complete 4,096-entry vector action
tables for these fixed twelve-dimensional operators. It imports no primary
transition routine or predecessor executable.

Both engines return the exact radius-three layers

    1, 56, 1750, 45144,

for 46,951 distinct operators. Each expands 101,192 directed transitions.
The verifier compares every state and every distance after the injective
full-to-packed conversion. It checks every full paid operator is an
involution. These comparisons authenticate the new domain; no predecessor
scientific certificate is replayed.

## Why the short-word joins prove exact minima

The single-role address action generated by a,b has six distinct permutations,
all reached by length three. A direct word on role one followed by a direct
word on role two attains the required endpoint with d=ell(g)+ell(h)<=6.
The verifier checks all twelve input columns of every attaining word,
including the four arbitrary dirty spectator columns.

For d>0 put k=d-1, r=floor(k/2), and t=k-r. Then r<=2 and t<=3. Every
word of length at most k splits as L R with L in the radius-t ball and R
in the radius-r ball. The split also covers lengths below k: assign at most
r calls to R and put the remaining calls in L. Therefore a shorter word
exists exactly when some R in the smaller ball satisfies

    T R^-1 in B_t,

where T is the full required endpoint. All generator inverses are available
at the same price. The second engine inverts the full twelve-column R by
binary elimination and forms the literal residual T R^-1. The first engine
replays reversed paid words and performs the equivalent packed-row operation.
Both independently decide every join membership, and no join hits for any
of the 35 nonidentity targets. The identity target already has minimum zero.

This covers every possible cheaper word, including arbitrary scalar
interleavings by normalization. There is no missing longer-word obligation
for the stated minima. It does not imply that all longer words have formal
endpoints, or that this representation is faithful. PR2599's nonfaithfulness
result remains a cited premise and motivation, not a new deliverable.

## Rejection controls and boundary

The verifier rejects a missing radius-three operator, a false distance, and
an injected false short target. Every single-call omission from the attaining
words fails its actual endpoint. A dirty source bit leaking into the restored
third role also fails. These controls exercise semantic predicates before
the report's source hashes are computed.

The certificate uses unit call prices, exactly three roles, one point column,
binary scalar mixing and both specified coordinate labels. It does not price
physical mixing or address delivery. Extra roles, alternate alphabets, rank-two
unit-priced calls, clean workspace and partial restoration change the model.
No native supplier, complete recursive invoice, precision/tape/stock bound,
new kappa or complete multiplication theorem follows. All five selected
framework assumptions remain. Independent human and formal proof-kernel
review are unclaimed.
