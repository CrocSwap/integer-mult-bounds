# Exact nine-call certificates for a transposition path and star

**Scoped formal-model proof; no new kappa.** Three target registers carrying
swaps `(01),(12),(23)`, or swaps `(01),(02),(03)`, require exactly **nine**
paid coordinate-CNOT calls. The theorem holds for every address dimension
`n>=4` and every register count `R>=3`, with arbitrary restored dirty
registers and free scalar register mixing.

[PR #4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968)
reported numerical order-pattern bounds near 8.33 and 8.14 and a nine-call
path word. Its scratch LP certificates were not in the package. This
contribution supplies exact rational certificates and the uniform implication.
The bounds are **25/3** and **57/7**. Each exceeds eight. The result does
not claim a new numerical observation or an optimum over all cut methods.
The selected kappa remains `60403/20000000`.

## Formal contract

Let `G=GL_n(F2)`. Work in `M_R(F2[G])`, the formal group algebra.
A paid call is `I+([g]+1)N`, where `g` is one coordinate CNOT and `N` is a
scalar rank-one idempotent. Each such call costs one. Free `GL_R(F2)`
register maps are allowed. The target is diagonal, with the three specified
coordinate swaps on distinct registers and identity on every other register.
Every register input is arbitrary; extra registers must be restored.

No native address representation, clean workspace, rank-two paid unit,
physical compiler, storage bill or recursive supplier is supplied here.
Natural-matrix equality is not substituted for a formal group-algebra identity.

## Crossing-rank argument

Use the left regular representation on `F2^G`. For a cut `A` in `G`, define

```text
q_A(M) = rank_F2 M[A^c x registers, A x registers].
out_A(g) = |{x in A : gx not in A}|.
```

Block multiplication and rank subadditivity give
`q_A(MN)<=q_A(M)+q_A(N)`. A free scalar register map has crossing rank zero.
A paid call has crossing block `P_g[A^c,A] tensor N`, hence crossing rank
`out_A(g)`, since the permutation submatrix has that rank and `rank(N)=1`.
The diagonal target has crossing rank equal to the sum of its three `out`
counts. These are formal-algebra consequences, valid for every `R`.
Positive weighted sums and averages of these inequalities remain valid.

## Relative-order cuts

Fix a total order on the nonzero binary vectors. For an invertible address
matrix `x`, record the relative order of its first four rows as a permutation
of `0123`. A subset `C` of the 24 patterns defines a cut in `G`. Now average
this cut inequality over every total order of the nonzero vectors.

A CNOT writing one of these four rows replaces it by the sum of two
independent rows. This sum is nonzero and differs from all original rows.
Thus the four selected row vectors and the new vector have 120 equally
likely relative orders. This holds whether the read row is selected or is
an address spectator. A CNOT writing outside the four rows changes no pattern.
A target swap only relabels the four original rows, whose 24 orders are uniform.

For pattern set `C`, define `g_i(C)` by counting transitions from `C` to its
complement when label `i` is deleted and inserted at one of four positions.
The unchanged position contributes zero. Define `h_ab(C)` by counting patterns
in `C` that leave `C` after labels `a,b` are exchanged. Then

```text
average paid crossing, writing i = |G| g_i(C) / 120,
average target crossing, swap ab  = |G| h_ab(C) / 24.
```

The first formula can also be checked by all 120 orders of five labels:
remove the new label for the input; remove the old row and rename the new
label for the output. Each changed insertion occurs once. The two positions
that give the unchanged pattern contribute zero. The verifier uses both
counting methods and compares them exactly.

Consequently, positive cut weights with each weighted `g_i` at most one
prove the paid-call lower bound `5 sum_C weight(C) sum_targets h(C)`.
All cut sets and weights are explicit in [CUTS.json](CUTS.json).

## The two certificates

Each base cut has twelve patterns. The exact counts are:

| Cut | Write counts g_0,g_1,g_2,g_3 | Sum of target h counts | Weight |
| --- | --- | --- | --- |
| Path P | 18,18,18,18 | 30 | 1/18 |
| Star A | 8,24,24,24 | 24 | 1/56 |
| Star B | 20,0,20,20 | 28 | 3/70 |

The path cut already has equal paid loads. Its weighted target count is
`5*30/18=25/3`.

For each star cut, average over the six permutations of the three leaf
labels `123`, with label zero fixed. This preserves the target sum and
makes each leaf load equal to the mean of its three base counts. The
weighted center load and each weighted leaf load are respectively

```text
8/56 + 20*(3/70) = 1,
24/56 + (40/3)*(3/70) = 1.
```

The weighted target bound is
`5*(24/56 + 28*(3/70))=57/7`.
The verifier checks the sets, all relabelings, both count methods and all
four exact rational paid loads. The certificate has no numerical tolerance.
Neither certificate is claimed optimal within its cut family.

The number of calls is an integer, so both lower bounds imply at least nine.
For the upper bound, implement each swap on its own register by
`CNOT(a,b), CNOT(b,a), CNOT(a,b)`. Each register entry stays a single formal
group basis element. Their product is the required swap; all other entries
are identity or zero. Thus nine calls suffice in the full formal algebra.
This proves the theorem, including arbitrary extra dirty registers and
address spectators.

## Verification and reproduction

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/swap-path-star-certificate
python3.12 -I -W error -O -B research/swap-path-star-certificate/verify.py
```

Expected markers: `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_SWAP_PATH_STAR_CERTIFICATE path=9 star=9 no_new_kappa`.
The normal and optimized commands recompute [RESULT.json](RESULT.json).
`--emit-receipt` emits JSON to standard output for explicit regeneration.
Normal replay writes no files and needs neither Git nor network.

The checks cover the three base cuts, all required symmetry images, all
120 five-item orders per image, twelve formal diagonal endpoints across
`n=4,5,6` and `R=3,5`, and 108 single-call omissions. Eight certificate
controls reject changed weights, a claimed bound of nine, a wrong symmetry
orbit and an invalid pattern. The receipt binds all six source files.
The endpoint calculation uses group labels only because these particular
attaining words remain diagonal monomials; the lower bound concerns all
allowed formal words, including scalar register mixing.

A disposable exhaustive pattern search found the certificates. No search,
C++ compiler or LP solver is needed for verification. The proof uses their
explicit counts, not search completeness or a floating point optimum.

## Limits

This gives exact cost for one path or star with three target registers.
It does not prove `3t` for every connected target graph, or for repeated
batches on the same four coordinates. The argument is a scoped formal-model
screen, not a native construction, a full multiplier theorem or a kappa gain.
Independent human and proof-kernel review remain open. No selected cold
replay or larger formal-word census is required or claimed.

## Open next questions

Can repeated path or star batches on the same four coordinates share calls?
The scaled lower bounds need not round to nine per batch. Compare a bounded
multi-batch formal word with those bounds before seeking a general additive
claim. This package has no repeated-batch optimum or construction search.

## Credit and provenance

Prepared for Ali Romman with substantial OpenAI Codex assistance.
New work is Apache-2.0. James Reed supplied the component-cut proof, the
numerical path/star observations and the path upper word in
[PR #4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968), and
the all-order spectator method in
[PR #4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950).
Mihir Srivastava supplied the spectator-model statement in
[PR #4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939).
Their retained notices credit Ross Richardson, commdata2338, Gareth Davidson
and the earlier register-model/cut contributors. No predecessor code is
imported. Source documents are provenance only and are pinned in
[SOURCES.json](SOURCES.json). Base:
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7.
