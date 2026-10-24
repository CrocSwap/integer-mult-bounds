# Active coefficient recovery and the remaining coupling

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.

This is a conditional component construction on the inherited physical ABI.
It supplies neither four autonomous Gaussian jobs nor a profitable caller.

## Source and conventions

Use Dugongue's PR4948 backward involutive producer, Dillon's signed PR4933
normalizers and the mixed p2 chronology retained in the passive saved-query
package. There are four independent 112-owner main banks and two disjoint
408-owner helper inventories. Original helpers are never scratch. Rightmost
operators act first. On each main pair the inherited FULL is

    B_s = diag(D_s,D_s) [[I,-Q C_s],[0,I]].

Here Q is the central Gaussian, D1 and D3 are the two fresh eight-axis
Gaussians, C1 and C3 are the actual normalized F-transpose codes, and

    C_s^2=I, [C_s,D_s Q]=0, [C_s,D_t]=0 (s != t).

Q commutes with D1,D3, which commute with each other. C_s need not commute
with Q or its own D_s. Q^4=I, and P=Q^2 is the physical monomial Pauli.
The source's all-width phase, chart and helper-autonomy results are premises;
this package does not independently replay their native words.

The original thin inputs are X at query0, C1 X at query2, and C3 X at
query4. Their paid response is Q^-1 times that input; query0's response is
subsequently multiplied by C1 before addition. Retain the two FULLs, paid
IDLE, all bridges, signed swaps, scalar boundaries and all three queries.

## The changed inputs

Save h, the first FULL's Y output, before the subsequent IDLE and bridge.
At query2 replace its argument C1 X by C1 X+h, obtaining response r2.
At query4 replace its argument C3 X by C3 X+C1 Q^2 r2.
Both additions use owned query copies before the destination is updated.
No extra Gaussian query is introduced.

Let x0,y0,x1,y1 denote the four original independent input banks, before
the scalar right boundary. After query4, before the last scalar operations,
the second pair's Y bank is exactly

    D1 Q^-1 x0
    + Q^-1 C1 Q (I-Q) D1 y0
    + [(Q^-1 C1 Q C1-Q^-1)D1 + Q^-1 C3 D1 D3] x1.

Its y1 coefficient is zero. `verify.py` checks this complete four-block
row against chronological multiplication. No selected-column substitution
is used in that equality.

For a short independent derivation of the x0 coefficient, restrict the
input to x0 only. After FULL1, X vanishes and h=Q^-1 C1 D1 x0.
Query2's response is Q^-1 h. Bridge-minus sends this response to the
second pair's Y input. FULL3 produces

    X=-D3 Q C3 Q^-1 h,  Y=D3 Q^-1 h.

The old part of query4's response is -Q^-1 D3 h, cancelling this Y.
Its new part is Q^-1 C1 Q h=D1 Q^-1 x0. Thus the previously absent
rank-nine coefficient has appeared through active use of two paid responses.
The finite passive trace's missing-grade invariant does not apply to this
changed trace. This observation is not independent-job credit.

## The output is coupled at every positive width

The y0 coefficient is an invertible left factor times (I-Q) times an
invertible right factor. It is nonzero whenever Q != I. At every positive
digit-column width, Q has an eigenvector of eigenvalue i (one column has
odd central frequency and the other columns have even central frequency).
Consequently an arbitrary y0 input changes this output. The old autonomous
job has not been recovered.

There is also an exact size for the contamination. At column count f, in
the common 17-axis ambient address space, define

    b0(f) = sum_{0<=k<=f, k=0 mod 4} binomial(f,k).

Q has eigenvalue i^k on a central Walsh frequency of Hamming weight k.
Hence, including the sixteen spectator axes and all 112 owners,

    rank(Q^-1 C1 Q (I-Q)D1)
        = 112 * 2^(16f) * (2^f-b0(f)).

The fraction of the full owner-bank dimension is 1-b0(f)/2^f, tending
to 3/4: the root-of-unity filter gives
`b0(f)=(2^f+(1+i)^f+(1-i)^f)/4` for f>=1, and both extra terms have
magnitude 2^(f/2). For example the rank fraction is 1/2,3/4,7/8 at
f=1,2,3. This is ordinary
complex linear rank, not a lower bound on recursive calls or free circuit
cost. It does not price a correction or exclude a changed caller.
The checker independently compares binomial sums, a four-residue recurrence
through f=64, and central frequency enumeration through f=12.

## Inventory and ordinary work

The attempted complete caller still invokes exactly two source FULLs,
one IDLE on two 112-owner banks, and three 112-query banks. Its recursive
paid histogram is the inherited

    {1:4754,2:824,3:1020,4:254,5:80,8:224}.

All 816 original helper jobs remain autonomous once; no owned copy earns
a productive target. The old proposed main rewards cannot be retained.

For the explicit component, one extra owned 112-field bank can first hold h,
then be reset and reused for r2. One extra eight-field mode workspace
implements C1. The additional field-level upper ledger is:

| Added operation | Count |
| --- | ---: |
| Two feedback additions | 224 scalar ADDs |
| One inherited F-transpose recoding | 896 ADDs, 224 monomial passes, 16 mode CLEARs |
| Q^2 on the saved response | 112 monomial passes |
| Captures of h and r2 | 224 COPYs |
| Initial, intermediate and final reset of the saved bank | 336 owned resets |
| Extra owned capacity | 112 saved fields plus 8 modes |
| Gaussian children | 0 |

Query buffers already required by the three thins stay charged. Read h
before changing its source; save r2 before releasing its query buffer.
The native helpers and original inputs are never cleared. These are
field-level counts under inherited owned-reset and monomial implementation
contracts. A fixed-tape implementation, precise rounding budget, completion,
compiler and outer bill are not supplied.

## Bounded synthesis and its limits

The search uses the semidirect-product algebra of the inherited gauge engine,
adding C1^2=C3^2=I and Q^4=I. Its fresh D exponents are formal integers.
In particular D^4=I and other additional physical source relations are not
imposed. This is a sufficient algebra for a positive identity; a failure in
it is not a faithful physical impossibility proof.

For each feedback, allow it to be absent, or use a reduced C1/C3 word of
length at most seven with coefficient in {-2,-1,-1/2,1/2,1,2}. There are
91 choices per edge and 8,281 policies. The second word is followed on the
right by Q^2. Keep both original thin-input coefficients equal to one.
The passive left decoder may use the thirty words W and W Q^2, for reduced
C1/C3 words W of length at most seven, and arbitrary rational scalar sums
across all 39 recorded bank observations. This is a restricted whole-bank
decoder grammar; arbitrary port-dependent controls are not included.

After query4 only scalar operations occur. Thus the span of all observations
equals that of the thirty preceding observations and response4, with the
same thirty left controls. This justifies caching the pre-query basis.
All 8,281 policies attain only the positive first-pair job in this formal
span. `SEARCH.json.gz` retains every policy, exact rank and attainment mask;
the full registered replay recomputes all of them.

The smaller 49-policy pilot uses code-word length one, coefficients +/-1
and decoder length three with the same Pauli placements. For all 196 target
questions it checks either a constructive recipe or a rational separating
functional directly against every declared generator. These checks do not
trust the elimination pivots. Deleted recipes and false dual pairings reject.

The finite span result excludes the specified recipes only in the declared
formal algebra. Different feedback sources, earlier active changes, input
weights, additional Pauli placements, port-dependent controls, native prefix
observations and further physical relations remain outside it.
