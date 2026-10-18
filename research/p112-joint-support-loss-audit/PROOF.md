# Sharp joint P112 deletion loss through 43 ports

## Statement and scope

Use the exact integer matrix X, source labels l_t and dual labels v_i in
`research/p112-single-lift/reference-geometry.json`, pinned in SOURCES.json.
For coordinate j let S_j = {i : X_ij != 0}. For an arbitrary set T of
source ports define

    b_j(T) = rank_F2 [(v_i dot l_t)]_(i in S_j, t in S_j minus T),
    L(T) = sum_(j=0..7) (8 - b_j(T)).

For every integer 0 <= M <= 43, the exact maximum over |T|=M is

| M | max L(T) |
|---|---:|
| 0..23 | 0 |
| 24..35 | 2 |
| 36..39 | 3 |
| 40..43 | 4 |

The maxima are over arbitrary deletion sets. They are not asserted to be
attainable by a cheap two-total decoder. PR1787's upper bounds 0/2/4/5
are correct; the last two are conservative. This note sharpens those bounds,
without claiming an error in the predecessor or priority for its support
method, generalized weights, four-reader census or 43-port no-saving result.

## Exact finite premises and completeness

For each j, form the binary evaluation code C_j by the XOR span of the
actual 56 pairing rows on S_j. The verifier checks that its 256 words agree
with the separate construction using all 512 ambient binary functionals.
The nonzero weights are 24 (63 words), 28 (128), 32 (63), and 56 (one).
Nullity gives

    8 - b_j(T) = dim {c in C_j : supp(c) subset T}.

Thus losing a rank requires a nonzero codeword support, and losing two
requires the union of supports of two distinct nonzero words. Over F2 two
distinct nonzero words are independent. This is a complete enumeration of
2-spaces by generators, with support duplicates removed; no RREF generator
or proof checker from PR1787 is imported.

For each reader the complete distinct 2-space supports of size below 44
number 5,313. Their minimum size is 36. Each contains exactly four codewords
including zero. Every extension by a word with a new support coordinate
has union size at least 44, with equality attained. This proves that no
reader loses three ranks below 44: if a 3-space fit, choose two of its
independent words. Their support is in the enumerated list. Its third
independent word cannot be supported there, because exactly four codewords
are supported there, so it violates the extension bound. The argument
covers all deletion sets through 43, not just tested witnesses.

All supports S_a and S_b meet in24 positions. Two distinct readers each
losing two ranks would therefore require at least 36+36-24=48 deleted
ports. Hence at most one reader can lose two in our domain.

The verifier next constructs every union of a nonzero word from two
specified distinct readers whose size is below 44. Joining a third word
proves the minimum three-reader union is40. Joining the pair lists for
all four-reader choices produces exactly 42 distinct unions below 44,
each of size 40. Completeness follows because any four-reader loss chooses
one nonzero word from each kernel, and its pair unions are subsets of T.
The literal pairing-matrix rank oracle checks all 42 supports: each has
exactly four losses, all of size one.

For every one of these 42 supports U, the complete inventories additionally
show both **sharp extension margins**:

- A word from any fifth reader needs at least 8 positions outside U.
- A 2-space support from any of its four affected readers needs at least 12
  positions outside U.

Only the lower bounds are needed. Consequently T of size at most 43 cannot
hit five readers, and if it hits four none can lose a second rank. The
predecessor's weaker fifth-reader margin was sufficient for its theorem;
these sharper margins concern exactly the42 minimal supports, not every
arbitrary40-port set or a global two-total construction.

## Deriving and attaining the maxima

Below 24 no codeword fits. Below 36 each affected reader loses one, and
below 40 fewer than three readers are affected, so the maximum is at most 2.
For 36..39 fewer than three readers are affected; only one may lose two,
so the maximum is at most 3. For 40..43, at most four readers are affected.
If four are affected each loses one. If at most three are affected, only
one loses two, again giving at most 4.

The verifier derives an explicit common 24-port cut, a 36-port 2-space
support with loss vector of total 3, and a 40-port four-reader support.
RESULT.json contains an explicit sharpness witness for **every** M=0..43,
formed by filling these anchors with extra ports. Each complete eight-entry
loss vector is checked twice: by code-kernel cardinalities and by Gaussian
elimination of the literal restricted pairing matrices. Filling cannot
decrease loss, and the proved upper bounds prohibit a further increase.
Dropping one port from the common 24-port cut restores all eight ranks.
Counting affected readers instead of nullity fails on the 36-port witness.

## Consequence for full-rank on-column two-total decoders

Consider the predecessor's exact factorization

    XX^T = XT^T + DZ^T,  D=XA,  T=X-ZA^T,

where both A (8 by 2) and Z (112 by 2) have complex rank two. Both added
readers and sources are nonzero. Let M=|supp(z_1) union supp(z_2)|<=43.
Outside this union each retained source equals its coordinate source;
extra nonzero entries can only increase pairing rank. The retained COPY
charge is therefore at least 64-max L(T_source).

For completeness the added-reader premise of #845 / PR1787 is rechecked
using a different arithmetic certificate. For each nonzero nine-bit q,
form X[{i:q dot v_i=1},:]. Exactly 503 such matrices have rank 8 modulo 3.
They therefore have nonzero integer eight-minors and complex rank 8. The
remaining 8 have rank 7 modulo 3 and one identically zero coordinate column,
which proves complex rank exactly 7, with eight distinct coordinate-axis
kernels. No live source label is one of these exceptional q. This uses
modular rank only as a lower bound, plus a symbolic upper bound; it never
assumes arbitrary matrices have the same rank over Q and F3.

For d=Xa nonzero, its active dual span has dimension at least 8. Otherwise
its annihilator in F2^9 contains at least three nonzero q, each putting a
in the corresponding rational kernel. Full-rank q allow only a=0, and the
eight exceptional kernels are distinct axes, whose pairwise intersections
are zero. Every live source label is visible to d for the same reason:
none is exceptional. Evaluation on the active dual span has kernel
dimension at most one. A source z on m distinct ports, with pairing rank r,
has m distinct labels in the preimage of an r-dimensional image. Thus

    r >= p(m) := min {r>=1 : m <= 2^(r+1)}.

This intentionally retains PR1787's weak support-price bound, descending
from PR1432. No new or sharp added-source price is claimed. If m_1,m_2
are the two source support sizes, then m_1+m_2>=M. The exact integer
minimization over 1<=m_1,m_2<=M in RESULT.json checks

    64 - max L(T_source) + min[p(m_1)+p(m_2)] >= 66

for every M=1..43. Therefore the **full-rank on-column** case has COPY
charge at least 66 in this domain, strengthening the predecessor's strict
bound above 64. No 66 floor is asserted for the complementary rank-one or
off-column cases. PR1197 retains credit and responsibility for those
reductions; the general 64 no-saving result through 43 already belongs to
PR1787. No claim is made for M>=44.

## Limits and credit

This is a finite geometry theorem with an exhaustive premise certificate
and written completeness argument. It does not enumerate every deletion
set, formalize the proof in Lean, solve two-column complex realizability,
construct an improved supplier, or price physical frames, restoration,
hosting, precision, recursive children or a new kappa.

PR1787 at `2b821b14a7cd5888df95531c98d18ee3797e36c3` (Josie Elliston;
OpenAI Codex preparation and Claude review) is the immediate predecessor.
Philipp / mightyOil's PR1197 supplies the two-total setting; Mihir
Srivastava's #845 and woklerx's #998 the single-lift and complex lineage;
commdata2338's PR1375 the first erasure weight; Hanson Sun / bbMisk's
PR1432 the support-price argument; DreamingOfClouds and Joel Pulikkan /
GamingPuzzled the decoder/COPY lineage. The retained geometry and labels
remain unchanged. Substantial OpenAI Codex GPT-6 Astra assistance for
Philipp / mightyOil; no independent human review. Apache-2.0.
