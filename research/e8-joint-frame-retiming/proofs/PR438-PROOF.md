# Split centres and a joint conditional exponent

The finite construction gives

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),
\qquad \kappa=0.001120864952258278,
$$

conditional on the retained all-size compiler, compressed-window, correlated
bank-dirt, restored-work, fixed-tape/common-grid, precision and analytic
interfaces. The changes below concern both finite suppliers. Original source
proofs and notices are retained; they do not replace the changed checks.

## 1. Cancel coordinate terms before lifting the complex decoder

Partition the 120 Hamming E8 root lines into the 112 code lines C and the eight
coordinate lines F, represented by 2e_i. Write r_s for a root representative and
G_ts = r_t · r_s / 2. The parent decoder is the rank-eight centre factorization
G/2 together with its negative off-diagonal entries.

For each code target t, the coordinate-source centre contribution is
r_ti x_(2e_i)/2. Its side contribution is its negative. Cancel this pair before
constructing the lifted program. For code targets retain only

$$
Z_i=\sum_{s\in C}r_{si}x_s,
\qquad
\sum_i\frac{r_{ti}}4Z_i
-\sum_{\substack{s\in C\\s\ne t}}\frac{G_{ts}}2x_s=x_t.
$$

For coordinate targets, implement the identity x_(2e_i) directly. Thus the
entire 120-by-120 clean decoder is still the identity, including both cross
blocks between C and F.

In the parent's binary address realization,

$$
p_s\cdot p_t=1+G_{st}\pmod2.
$$

Every code source contributing to Z_i is orthogonal to p_(2e_i), because its
ith root coordinate is ±1. The already constructed global sum Z_i lies in that
rank-eight hyperplane. Copy it there, lower the private copy to frame zero with
one rank-eight child, and scatter into the code targets. The eight coordinate
identities copy their source lines with one rank-one child each. Each private
copy has a sequential lifetime, and is erased before the next episode.

The total copied rank is unchanged:

$$
8\cdot8+8\cdot1=72.
$$

The 112 coordinate-source helpers and eight dedicated full-centre helpers are
removed. Own-block corrections use their original source-copy rows directly;
all remaining signed packets and selected target butterflies are retained.
The actual helper count is 560. No rank-four recovered row is substituted for
a rank-three input.

## 2. Arbitrary dirt and heterogeneous copy frames

The explicit main word has block form z' = Uz and y' = Vy + x + Ks, where
z=(x,s), and U,V are invertible. No target feeds z. At the common initial frame,
apply V^-1 to the target basis and the literal correction -V^-1 Ks. Recompute K
from the new word. After all main gates and final climbs, apply the literal
inverse of the source/helper subword at the common full frame. This restores
all sources and arbitrary helpers while adding x to y.

The parent common-frame proof applies to each copy separately. A private copy
created at label L(F) is lowered by the exact operator L(0)L(F)^-1, whether F
has rank one or eight. Scalar operations occur only at equal labels. Adding
the common exterior window to both labels cancels it exactly. The proof
therefore does not require a full-frame centre, or infer an operator from rank
alone. The inverse-transpose negates/transposes each scalar shear in the same
order and reverses each private gather/child/scatter operation as emitted.

Both scalar orientations and the serialized private-work programs replay all
800 input columns. Both restore arbitrary source/helper inputs and erase private
work. The changed exact Gaussian recipes include the heterogeneous centre
transitions and their global phases. Of 2,918 selected directed pairs, 248 were
newly computed; 2,670 were unchanged source-bound exact pairs already checked in
the local phase run. The release optionally replays all selected pairs.

The local paid profile is

$$
\{1:1912,\ 2:784,\ 3:168,\ 4:224,\ 5:392,\ 8:24\}.
$$

The compressed complex geometry uses m=73, eight replicas and nine stages.
There are 560 banks per stage, each holding eight whole rank-nine residuals and
one paid rank-one pad. Live width is 12,720; physical stock is 13,298, including
16 centre slots, the conservative 560-row tableau reserve and two coefficient
streams. The global rank deficit is 2,496. Explicit owner tables, padding,
terminal translations and the cover correction are independently decoded.
The largest child is 48; 73² > 2·48² gives two-level halving.

The fresh invoice fits the retained 2^30000 router, 2^100000 literal and 2^210000
precision reserves. Two exact rational engines certify

$$
b=0.001183986549206329.
$$

## 3. Source-centre bit composition

Start with the exact R767 word from PR426. Its nine retained rows are written
only by original sources at the full frame and are not read by ordinary A/B
gates. Their nine independent binary forms have an invertible minor in source
columns 0,1,2,4,8,9,16,32,64.

Replace those rows of the 120-dimensional identity by the nine retained forms.
Exact elimination produces an invertible source basis T, emitted as 559 XOR
additions. Delete the nine retained helper rows and their old-dirt columns.
After A apply T, perform the same nine sequential copies using the designated
source rows, and immediately apply T^-1 before B. The copies have unchanged
rank eight. All scalar operations of T and its inverse use the full frame.

All 998 columns, arbitrary dirt, frame incidences and restoration pass. Omitting
T^-1 or the remaining old-dirt correction fails. The actual exported record
stream is reflected in reverse order with complementary frames. A reflected
ERASE becomes a fresh COPY at that chronological point; the original source
row remains unchanged within each copy episode. Both reflected programs and
all nine composed invocations are replayed, rather than assuming that mutable
source rows meet an old immutability restriction.

Use the unchanged compressed bit windows in dimension 64: a local eight-space
and eight exterior seven-spaces. The root data, rational frame family, form,
port isometries and bank slots are source-bound to PR386. Every changed nested
pair is checked by exact rational spans; positive definiteness gives the
projector identity and its reflected version. There are 758 banks per stage,
each filled by eight rank-eight residuals, with no padding. Live width is 14,502
and physical stock is 14,511. All 54,576 owner assignments are checked. The
unbanked global replay restores all 7,782 independent columns.

The bit local profile is

$$
\{1:2367,\ 2:875,\ 3:475,\ 4:321,\ 5:164,\ 7:14,\ 8:9\}.
$$

Its global deficit is again 2,496. The maximum child is 42 and 64² > 2·42².
The actual cancellation-free prefix bound needs 223 bits; the new charge is
256 bits, replacing the parent's 192-bit allowance. The finite two-level
coefficient needs 483 bits and fits the retained 2^512 allowance. The row
coefficient is 18,355 < 20,161. These costs, including the basis operations,
are recomputed from the emitted word. Two exact rational moment engines give

$$
c=0.001122122700265139220566.
$$

## 4. Joint strict assembly

Both moments include the inherited 10^-16 bad-branch allowance. The bit supplier
binds because c < b. Let eta=beta=10^-18 and

$$
s=\min\{c,(1-\beta)b\}-10^{-24}.
$$

Starting at a_0=384599/10^10, use six fixed ordinary bootstrap levels

$$
a_{j+1}=(1-s)s+sa_j.
$$

All bootstrap cutoff inequalities are checked with the actual charged finite
coefficient. With q=a_6(1-2eta), choose the greatest 10^-18 grid point strictly
below (1-eta)q/(1+q). It is

$$
\kappa=\frac{560432476129139}{500000000000000000}
       =0.001120864952258278.
$$

All 47 retained strict outer inequalities pass. The next grid point, zero eta,
zero beta and unit beta are rejected. The candidate is computed from both
actual new templates; no independently reported savings are added together.

The source-bound finite claims above do not discharge the inherited all-size
interfaces or establish unconditional integer-multiplication complexity.


## Addendum: shared-donor kernel entrances in the compressed bit geometry

The kernel stage changes only helper chains: a pivot p starts at its entrance E (a root-closed frame inside the first frame
of p and of every donor) instead of the zero frame and drops its frame-0 completion reads; every donor d of E adds p at E
before the first A gate and again at FULL after the last C gate. Over F2 the completion responses satisfy
resp(p) = XOR resp(D), so every target column is unchanged and every helper column is restored (checked by the exact replay
on all 998 local columns, with arbitrary dirt, and by the global scalar replay). Frame nesting and the integer source-span
rule are rechecked. In the compressed nine-stage construction a helper's residual is its endpoint dimension minus its
entrance dimension; a helper of entrance rank e occupies a width-(8 − e) coordinate block of a 64-dimensional bank. The
tiling places 8 × 758 slots per stage into 733 banks with every coordinate used exactly once, so the injective-owner and
arbitrary-dirty-bank arguments apply with block isometries in place of whole rank-eight slots. The live stock drops by
9·(200/8) = 225 families while the paid mass drops by 72·200, keeping the rank deficit 64·W − mass = 2,496.
