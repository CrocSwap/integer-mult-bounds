# Sharp puncture threshold for arbitrary off-target proper stars

**Research note / scoped negative result; no new kappa.**

For the paired-port model of PR231 and PR669, arbitrary off-target stars cannot lower the one-target puncture threshold below `2(p-k)+1` at a power-of-two k. This closes the punctured global-star class that PR669 explicitly leaves open. The local intersection-cell criterion does not extend: the concrete ten-star example below reaches the threshold while every intersection cell survives.

## Algebraic class

Let p >= k >= 2 and let P_{p,k} be the signed k-ports: choose k of p disjoint coordinate pairs and one coordinate from each chosen pair. Over F_2, let C_{p,k} be the evaluation space spanned by the functions

    m_L(S) = 1[L subset S],   0 <= |L| < k,

where L itself is a partial signed port. This includes the empty star as a strengthening of the stipulated decoder class. A function in C_{p,k} is the evaluation of a multilinear polynomial of total degree less than k on P_{p,k}.

**Theorem.** The smallest nonzero Hamming weight in C_{p,k} is exactly

    d(C_{p,k}) = 2(p-k+1).

This statement holds for every k, not only powers of two. Consequently, for power-of-two k, a retained target T can be decoded by arbitrary global proper stars and permitted target overlap-class corrections only after deleting at least 2(p-k)+1 other ports. A single (k-1)-star containing T attains that threshold.

The theorem concerns one retained target and scalar identities. It supplies no simultaneous decoder, paid recursive profile, circuit construction, restoration guarantee, or new kappa.

## Lemma 1: parity on a generalized cube

Take k slots. Slot i has two distinct coordinates a_i and b_i. Suppose the pair indices used by different slots are disjoint; a_i and b_i may belong to the same original pair or to two different original pairs. Every one of the 2^k selections of one coordinate per slot is then a valid signed k-port, and all these ports are distinct. Call the resulting family G a generalized cube.

For every monomial m_L of degree |L|<k, its sum on G is zero in F_2. If L uses a coordinate unavailable in G, or uses both alternatives of one slot, the count is zero. Otherwise L fixes exactly |L| slots, and the count is 2^(k-|L|), which is even. The same conclusion holds for the empty monomial, whose count is 2^k. Therefore every f in C_{p,k} satisfies

    sum_{S in G} f(S) = 0.

The ordinary sign cube for each fixed k-pair set is one such G. Since these ordinary cubes partition P_{p,k}, every codeword has even total weight.

## Lemma 2: even faces force large support

Let W be a nonempty subset of the binary cube {0,1}^m. Assume that every face obtained by fixing at most r coordinates contains an even number of points of W, where 0 <= r < m. Then

    |W| >= 2^(r+1).

If r >= m, no such nonempty W exists, because fixing all m coordinates isolates any chosen point.

Proof by induction on m. For r=0 the entire cube is a face, so nonempty W has even cardinality, hence at least two. For r>=1, split W into its two first-coordinate slices. If both are nonempty, each slice inherits the even-face property up to r-1 additional fixed coordinates; the induction hypothesis gives at least 2^r points in each slice. If only one slice is nonempty, that slice inherits the property up to r fixed coordinates, because a face fixing other coordinates has the same intersection with W as its corresponding face in the surviving slice. If r>=m-1 this would isolate a point and is impossible; otherwise induction gives at least 2^(r+1) points in the surviving slice. This proves the lemma.

## Proof of the minimum distance theorem

Put q=p-k and induct on q while keeping k fixed.

For q=0 the whole family is one ordinary sign cube. Lemma 1 makes every nonzero weight even, hence at least two. A monomial m_J for any (k-1)-port J has exactly two extensions, so the distance is two.

Now take q>=1 and assume the claimed lower bound for p-1 pairs, namely 2q. Suppose for contradiction that a nonzero f in C_{p,k} has weight w<2(q+1). Its total weight is even by Lemma 1, so w<=2q. Choose a support port T, and let Q be its k pair indices.

For each of the q pairs r outside Q, restrict f to ports avoiding pair r. All monomials containing a coordinate of r become zero; all other monomials still have degree less than k. Thus the restriction belongs to C_{p-1,k}. It remains nonzero because it contains T. By induction its weight is at least 2q. This restriction has weight at most w<=2q, so equality holds and no support port of f contains pair r. Repeating for every outside pair shows that all of f's support lies in the ordinary sign cube on Q, and w=2q.

Fix any face of that ordinary cube obtained by fixing a set A of s<=min(q,k) signs. For each fixed slot i in A, choose a distinct outside pair r_i, and use in slot i the fixed coordinate of Q together with either coordinate of r_i. For each remaining slot use both coordinates of its original Q pair. These slot pair indices are disjoint, so this is a generalized cube. Its intersection with the original ordinary cube is exactly the chosen face: selecting an outside alternative leaves Q, whereas selecting all fixed coordinates leaves the other signs free.

Because f vanishes outside the ordinary cube, its sum on this generalized cube equals the support cardinality in that face. Lemma 1 makes this cardinality even. Therefore every face fixing at most q signs is even. If q>=k this contradicts the presence of T directly. If q<k, Lemma 2 gives

    w >= 2^(q+1) > 2q,

again a contradiction. The strict inequality holds for every q>=1 (base 4>2, and induction or elementary doubling).

This proves the lower bound. For sharpness, choose any (k-1)-port J. Its extensions consist of choosing one of the p-(k-1)=q+1 remaining pairs and one of its two coordinates. Thus m_J has exactly 2(q+1) nonzero evaluations. The distance theorem follows.

## Absorbing overlap corrections when k is a power of two

Fix T and write j=|S intersect T|. For 1<=l<k, define

    B_l(S) = sum_{L subset T, |L|=l} m_L(S)
           = binom(j,l) mod 2.

For j=1,...,k-1, the matrix (binom(j,l) mod 2) is lower triangular with diagonal entries one. Consequently, every desired vector of overlap coefficients (b_1,...,b_{k-1}) has a unique expression as a sum of the B_l on those intermediate j values.

At j=0 all B_l vanish. If k is a power of two, all binom(k,l) for 0<l<k are even, so all B_l also vanish at j=k. Thus that same expression represents the correction function

    sum_{j=1}^{k-1} b_j 1[|S intersect T|=j]

on every port, including the disjoint and target classes. Each B_l is a sum of proper stars supported inside T. Hence permitted corrections add no functions to the arbitrary global proper-star space at a power-of-two k.

## Passing from codeword weight to puncturing

Let D exclude T and let F=P_{p,k} minus D. A scalar decoder on F has a coefficient function f from the proper-star-plus-correction space. Its coefficient equations say f(T)=1 and f(S)=0 for all other surviving S. The same coefficient expression evaluated on the full family therefore has support contained in {T} union D. By correction absorption it belongs to C_{p,k}, so

    |D|+1 >= wt(f) >= 2(p-k+1).

Thus |D|>=2(p-k)+1, even after granting the empty star. Conversely, choose J subset T of size k-1 and delete every other extension of J. This deletes exactly 2(p-k)+1 ports and leaves star_J(F)=x_T. The lower and upper bounds agree.

## A sharp off-target witness that defeats the local cell criterion

Take p=5, k=4, and T={1,2,7,9}, using coordinate pairs {0,1}, {2,3}, ..., {8,9}. Delete exactly

    {0,2,4,6}, {0,2,5,6}, {1,2,7,8}.

The following ten nonempty proper stars sum to x_T on the surviving family:

    {2}; {0,2}, {2,4}, {2,5}, {2,6};
    {0,2,4}, {0,2,5}, {0,2,6}, {2,4,6}, {2,5,6}.

One compact description of their coefficient function is

    1[2 in S] * (1+a+b+c+ab+ac+bc),
    a=1[0 in S], b=1[4 in S]+1[5 in S], c=1[6 in S].

All arithmetic is in F2. The two summands in b are disjoint because a port cannot contain both coordinates of one pair. The parenthesized expression is one exactly at (a,b,c)=(0,0,0) or (1,1,1). Its complete support is the three deleted ports together with T. This is a degree-three expression with no empty-star term.

No intersection cell S intersect T is emptied: the first two deleted ports occupy a seven-port cell {2}, and the third occupies a three-port cell {1,2,7}. Therefore PR669's target-local cell criterion excludes a local decoder for this deletion set. The exact full coefficient calculation in verify.py also checks local infeasibility directly. The example shows why extending the minimum threshold must not be confused with extending that criterion.

## Provenance and distinction

The symmetric binomial obstruction is the retained PR231 result (Joel Pulikkan / GamingPuzzled). PR669 (Sam Sung / the-missionary-company; source head 308f1e6ec3bb0b6ec0584cf7bfe219addc219b1e) already proves the full-family obstruction for arbitrary global stars and proves the sharp threshold only for target-local stars. This proof addresses PR669's explicitly unclosed arbitrary off-target puncture class. Its restriction induction and generalized-cube face bound apply to arbitrary global coefficients; they do not use the local intersection-cell argument.

The stronger space including the empty star is deliberate: its exact minimum-distance result implies the required no-empty-star lower bound, while sharpness uses a nonempty (k-1)-star. No implementation of a supplier or accepted-frontier change is inferred.


## Reproduce and inspect the evidence

From the repository root, with Python 3.10 or newer and no third-party dependencies:

```sh
python3 -B research/global-star-puncture/verify.py
```

Expected:

```text
PASS_GLOBAL_STAR_PUNCTURE: sharp deletion thresholds 3/5; 2 independent F2 engines; 960 correction rows; 12 negative controls
```

The default command recomputes and compares the entire committed RESULTS.json, without writing files. `--write PATH` additionally exports the same receipt after all checks. The checks remain active under `python3 -I -O -B`. The standalone independent implementation is `independent.py` (use `--json` for its full receipt).

The two implementations generate actual ports separately. verify.py computes the star row space and its quotient map with packed integer elimination. independent.py uses list-valued RREF and a full nullspace parity-check matrix, checking its rank and every orthogonality equation. Neither imports predecessor or supplier code.

| Domain | Ports | Star rank / dual rank | Exact minimum weight | Pair sums checked |
|---|---:|---:|---:|---:|
| p=5, k=4 | 80 | 65 / 15 | 4 | 3,160; 1,345 distinct |
| p=6, k=4 | 240 | 155 / 85 | 6 | all 28,680 distinct |

Even codeword weights and distinct nonzero dual columns exclude weights one through three. In the second domain, distinct unordered-pair sums also exclude weight four; parity excludes weight five. Single three-stars attain four and six. Full syndrome columns, selected targets, sharp deletions, independent nullspace data and the off-target witness are in RESULTS.json. All 960 target-specific overlap corrections are checked in both implementations, including overlaps zero and k.

Additional complete coverage comprises all codewords for (p,k)=(2,2),(3,2),(4,2),(5,2),(6,2),(3,3),(4,4), and all binary support sets in dimensions one through four for every face-codimension budget. This includes q>=k cases of the induction. For the two principal domains, all faces fixing at most p-k coordinates at the seed-selected target are realized by valid generalized cubes and checked against every star, by both packed and direct incidence counts. These finite checks support the written general proof; they are not its logical replacement or a proof-assistant formalization.

The twelve named controls reject single-entry incidence corruption, parity-preserving two-entry corruption, forbidden degree-k singleton stars, forbidden overlap-zero corrections, damaged dual columns, and invalid generalized cubes, in each principal domain. The independent engine repeats both incidence controls. A positive k=3 control uses a permitted overlap correction to isolate a target on the unpunctured family, demonstrating why the power-of-two condition is necessary for the decoder corollary.

## Scope, cost and stopping rule

This is an exact scalar decoder obstruction and an attaining scalar identity for **one specified retained target**. It permits target-dependent coefficients, arbitrary off-target support, arbitrarily many stars, and even the empty star for the lower bound. The upper witnesses use nonempty stars. Stars and corrections are recomputed on the surviving family.

A proposal to isolate a target with fewer than 2(p-k)+1 deleted ports fails the identity even if all helpers, source reads, copies, frame changes, restoration and recursive children are free. It therefore cannot become a paid supplier in this decoder class. At or above the threshold, no complete cost is asserted. Simultaneous all-target decoding, cost of preparing the totals, arbitrary dirty restoration, reader frames, hosting, outer assembly and other decoder geometries remain separate questions. Source-dependent coefficients inside an overlap class, degree-k stars and nonlinear mechanisms are outside the corollary.

This was a bounded structural experiment, with OS-random assignment seed 43. The seed selected k=4, primary p=k+(43 mod 3)=5, and target index 43 in the deterministic port order; p=6 supplied an adjacent region. The initial finite quotient experiment led to a restriction/face-parity proof, not a larger solver search. The finite domain, complete enumerations and all stopping conditions are fixed in verify.py; no uncompleted heuristic search is reported as an impossibility theorem. CLAIM.json records the three candidate tasks and narrow local claim. No pinned coordination issue existed; no separate reservation issue was opened.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. SOURCES.json records context and predecessor source pins. At that base, the accepted conditional result is `51110230636731/31250000000000000`, from #626/#622/#623 with #543. The selected pointer, accepted construction and upstream/ are unchanged. Its all-size compiler, mutable-source/common-label realization, whole-call hosting, precision/tape/exact recovery and analytic-transfer obligations remain inherited; this result discharges none of them.

## Attribution and validation

Prepared by Luke Mansoor (@lukemansoor) with substantial OpenAI Codex assistance in proof development, implementation, independent AI implementation/review and writing. No independent human review is claimed. New work is Apache-2.0 under the repository license. NOTICE.md preserves predecessor and selected-context credit. VALIDATION.md records completed local checks separately from GitHub CI.
