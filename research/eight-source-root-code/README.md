# Five dirty roots are exactly necessary at eight sources

**Exact paired-call interface boundary; no new kappa.** Four arbitrary dirty
root rows cannot realize all 255 nonzero eight-source masks when every source
and output map is called exactly twice. The construction of **conorholds,
[PR2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182)**, uses five roots and attains these map counts. Thus **five is the
exact minimum root count at eight sources** in the model below.

This settles **[Mason Hale's PR2282](https://github.com/CrocSwap/integer-mult-bounds/pull/2282), Open next question 1**. Its seven-source
four-root theorem is retained and independently calibrated, not claimed again.
The new reduction replaces paired-word enumeration by `n!` source orders and
represents normalized root axes by binary linear codes. Two implementations
exclude all **40,320 orders × 11,811 codes = 476,219,520 reduced cases**.
Every case already fails a necessary condition; no heuristic search or
unproved solver answer is used. This is a computer-assisted finite exclusion,
not a proof-assistant theorem or a physical supplier improvement.

## Model

Retain the generic binary connector interface of Ross Richardson's PR943 and
the multi-root contract of PR2182/PR2282. Distinct arbitrary dirty rows are
immutable sources `x_j`, outputs `y_m`, and roots `z_p`, all of positive length
L over F2. For independent, arbitrary compatible fixed F2-linear maps B_j,A_m,
including singular and noncommuting maps, the target is

```
y_m += A_m(sum_{j: m_j=1} B_j x_j),   1 <= m < 2^n.
```

The data-independent word has exactly two complete calls per B_j and A_m.
A B call adds B_j x_j to one root; an A call adds A_m z_p to its own output.
Ports may vary per occurrence. Arbitrarily many invertible **scalar binary
root-row frames** are allowed; paid elementary shears `z_p += z_q` generate
them. Sources and roots restore; outputs are not observed before completion.
Every child preserves other rows, restores private scratch, and meets its
agreed frames, access and head-return obligations. Data/root rows are excluded
from that scratch. Additional child calls, clean roots, output feedback,
source mutation, aliases, nonlinear updates and matrix-valued transformations
inside a row change the model and are outside the exclusion.

The lower bound grants every invertible scalar frame without a cost limit.
The upper construction below charges all its actual root shears and complete
child calls. No operation is asserted free in an adoption comparison.

## Normalized root codes: an exact feasibility criterion

Write b_j=B_j x_j and let R be the current invertible root frame. In normalized
coordinates a B occurrence at physical port p injects `R^-1 e_p b_j`.
Restoration of arbitrary independent incoming root dirt forces the final
frame to be identity. Since source j occurs twice, restoration also forces
its two normalized axes to be equal; denote the nonzero axis by v_j.
Necessity follows already from scalar identity A/B maps and independent input
bits, so no unjustified independence of matrix entries is needed.

Let V have columns v_j and let q_t be the binary source-prefix parity at a
cut. A physical reader with dirty covector r sees

```
r dot z_initial + sum_j (r dot v_j) q_t[j] b_j.
```

The two calls to A_m must have the same dirty covector. Therefore the achieved
mask is `h AND d`, where `h = r V` and `d = q_s XOR q_t`. Put

```
H = rowspace(V) <= F2^n,
D(w) = {q_s XOR q_t : s,t are source cuts}.
```

H has dimension at most the number of roots. The all-ones output forces both
`h=ones` and `d=ones`, so `ones in H` and `ones in D(w)`.
Consequently feasibility requires

```
{h AND d : h in H, d in D(w)} = F2^n.                  (1)
```

**Sufficiency with all frame costs paid.** Conversely, take any H containing
ones, a row basis V with k independent rows, and a restored paired source word
w satisfying (1). Columns v_j are nonzero. For every nonzero output choose
h,s,t witnessing (1), and solve rV=h. At its two cuts change the physical
frame to have first row r, then read root zero. Before every B_j occurrence
change the frame so `R v_j=e_0` and inject at root zero. Every nonzero row or
column extends to an invertible matrix. Restore the identity frame at exit.
The normalized axes and paired readouts prove the complete dirty-state map;
all output targets are separate, so the readout pairs can coexist.

`compile_code()` implements this construction using literal paid root XORs;
a swap is three XORs. Gaussian elimination gives at most `k(k-1)+3k` XORs per
frame change, with at most `2n+2(2^n-1)+1` changes. This loose implementation
bound proves finite realizability, not competitive cost. The five-source
compiler control pays **58 XORs**, versus the credited star's **8**; the
criterion is a feasibility result, not a transfer optimizer.

Thus (1), minimized over codes of dimension at most k and paired words, is an
exact finite test for k-root feasibility under this unrestricted paid-frame
contract. The eight-source exclusion uses only its necessary direction.

## The all-ones cut reduces the source domain to n! words

In a word with two occurrences of every label, an interval whose parity is
ones contains each source exactly once: every odd count must be one.
Its length is n. Rotate the closed source word so this interval comes first,
then rename labels by their order in that interval. The result has the form

```
0,1,...,n-1, permutation(0,1,...,n-1).
```

Rotating a closed path translates its prefix set, which preserves all pair
XOR differences; renaming coordinates permutes both H and D. We do not assume
that the physical frame word itself can rotate for free. Only this necessary
algebraic test is rotated. Enumerating all n! permutations and all codes is
therefore complete, though different pairs may represent equivalent schedules.
Words with no all-ones difference cannot be universal and are safely omitted.
The checker tests this reduction on **all 1,069 paired words at n=1..5**;
549 have an admissible cut. This reduces the eight-source source-order domain
from 2,027,025 canonical pairings to 40,320 orders, without changing coverage.

## Complete eight-source exclusion

It suffices to check codes of dimension exactly four. Any lower-dimensional H
containing ones extends to such a code; more reader supports only relax (1).
There is a bijection

```
H = <ones> + S,   S = H intersect {h: h[0]=0}.
```

Delete coordinate zero to identify S with a dimension-three subspace of F2^7.
The number of these spaces is

```
[7 choose 3]_2 = (127*126*124)/(7*6*4) = 11,811.
```

For a code H define its mandatory masks

```
M(H) = {m != 0 : no h in H other than ones contains support(m)}.
```

If `m=h AND d` and m is mandatory, then h must be ones, and d must equal m.
Thus `M(H) subset D(w)` is necessary. This condition is **not asserted
sufficient**. Both censuses test it for every reduced pair and find **zero
survivors**. The maximum |D| is 97. Code mandatory-set sizes range from 31 to
149. Complete size histograms are in [RESULT.json](RESULT.json).

The Python engine builds complete quotient subspaces by repeated span extension
and deduplication, forms pair differences of prefix points, and tests each
mandatory mask against every proper codeword. The C++ engine independently
enumerates unique RREF bases, forms contiguous-interval parities, and removes
all subsets of proper codewords from the required bitset. They agree on the
**entire 11,811-code inventory**, both histograms and all domain counts, not
just the final zero. Python recomputes every case in registered replay;
no native receipt is trusted by the default command.

The same reduction reproduces the known seven-source/three-root exclusion in
5,040 × 651 = 3,281,040 cases. This is a calibration of PR2282, not a new result.
Specializing extra source maps to zero extends the new lower bound to **at
least five roots for n>=8**, under the same paired-call restrictions. It does
not assert that five roots suffice for every larger n.

## Credited attainment and full local invoice

PR2182's star family uses n-3 roots and `8(2^(n-4)-1)` shears. Its proof is
independently transcribed in `star()`; no predecessor executable is imported.
At n=8 it reserves center z0 and leaves z1..z4. Run the closed center cycle
B0 B1 B0 B1, touring every four-bit leaf frame at each of its four distinct
bulk prefixes. Alternate forward/reverse reflected Gray tours. Inject B4..B7
once into their corresponding leaves, run B2 B3 B2 B3 with the same tours,
then repeat the leaf injections. All roots restore.

For `m=a | (b<<2) | (c<<4)`, read A_m at first-phase bulk prefix a/frame c and
second-phase bulk prefix b/frame c. Their root dirt cancels and their sum is
exactly the requested source mask. This gives **16 B, 510 A and 120 shears**,
or 646 paid calls, on five arbitrary dirty roots.

Let p_j=0 for j<4 and p_j=j-3 otherwise. With complete actual-port child prices
and complete root-XOR prices the construction costs

```
H_5 + 2 sum_j c_Bj(p_j) + 2 sum_(m=1..255) c_Am(0)
    + 64 c_X(0,1) + 32 c_X(0,2) + 16 c_X(0,3) + 8 c_X(0,4).
```

Per-call prices include their access, routing, restoration, frame and head
obligations and dispatch. H_5 additionally pays the five full root rows,
input admission, coefficient preparation, schedule generation/storage/reads
and residual control costs, without double counting included dispatch.
Child-private scratch and all source/output rows remain reserved as required.
The root-count optimum does **not** minimize this complete tariff, transfers,
child lowering or total storage. No selected supplier/caller or favorable
physical budget is supplied.

## Reproduction and evidence

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -O -B research/eight-source-root-code/verify.py
python3.12 -B scripts/research_package.py --package research/eight-source-root-code
```

Expected scientific marker:

```
PASS_EIGHT_SOURCE_ROOT_CODE words=40320 codes=11811 cases=476219520 survivors=0 roots=5 star_B=16 star_A=510 star_X=120
```

For a fresh independent native comparison (Clang/GCC, C++17):

```sh
c++ -O3 -std=c++17 -Wall -Wextra -Werror research/eight-source-root-code/census.cpp -o /tmp/eight-root-census
/tmp/eight-root-census > /tmp/eight-root-native.json
python3.12 -I -O -B research/eight-source-root-code/verify.py --native-result /tmp/eight-root-native.json
```

The comparison appends `native=agree`. The complete fresh Python and native
checks passed locally on macOS arm64 with CPython 3.12.14 and Apple Clang;
normal/optimized Python results are identical. The registered replay also
runs the constructor and semantic controls. The symbolic replay represents
each arbitrary initial root and each B_j x_j independently, so its per-output
linear identities apply to arbitrary exact A/B maps and L, not only zero dirt
or random small matrices. Known n=4..8 stars and their literal reversed words
pass. All **646** eight-source star operation omissions and all **130**
compiled-five-source omissions reject. Wrong readout port, reversed transfer,
insufficient root-code and typed-receipt mutations reject.

Not checked: proof-assistant formalization, hosted CI, native/recursive child
implementations, physical stock/hosting, tape/precision, the selected global
cold replay or outer analytic transfer. Selected inputs are unchanged.

## Open next questions

1. Does a real recursive caller need this complete-mask, minimum-incidence
   interface? Bind its actual child/port, stock and head-return costs before
   another construction campaign; no qualifying caller is supplied here.
2. Can the new complete reduction assist a different **cost** question, such
   as permitting extra child calls to save root stock? First specify one caller
   and a fully charged target. The paired-call root minimum does not settle
   that tradeoff. No automatic nine-source expansion is proposed.

Structured questions, the bounded stop decision and overlap checks are in
[TASK.json](TASK.json). The known five-root construction completes this task;
there is no new dependent search campaign.

## Sources, credit and scope change

Started from canonical main `7788b59946ebf3803dc38b6a19b47b4acb27f40b`, priority
revision 5, picker nonce `ceb645200d35eb9706fafdcc129b4ead`. The selected
conditional exponent remains 0.001672660197076918. The card scope is explicitly
**changed** from a small alphabet-extension experiment to a root-capacity side
result. Live overlap exposed the already completed seven-source result, which
was credited before the one bounded eight-source pivot. Public coordination:
[Discussion2785](https://github.com/CrocSwap/integer-mult-bounds/discussions/2785).

Credit **Mason Hale / PR2282** (`74e57135608dade29029a1107fdfceec8419c932`) for
the seven-source minimum, mandatory-mask method and explicit eight-source
handoff; **conorholds / PR2182** (`dc252de1cc594829c3031abdb4de104713bc474a`)
for normalized axes, root contracts and the attaining star; **Ross Richardson /
PR934/PR943** for the generic dirty connector/prefix model; **Douglas Colkitt /
PR1185** for the six-source/Gray lineage. Cinna Davis/PR1887, woklerx/PR1438,
Gareth Davidson/PR1498, Adam Gall/PR2065 and the retained one-way, compiler and
common-factor predecessors retain their original credit. Exact base blobs and
SHA256 provenance are in [SOURCES.json](SOURCES.json); frozen inputs are not
modified. Metadata overlap cannot rule out unpublished work or every code diff.

Prepared by **Arham Tahir**, with substantial **OpenAI Codex** assistance in
proof derivation, implementation, verification and writing. Apache-2.0.
Separate implementation paths are AI-assisted checks, not independent human
review. No selected-frontier, maintainer allocation or upstream source changes.
