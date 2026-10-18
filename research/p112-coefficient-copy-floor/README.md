# P112 coefficient changes preserve the sharp nine-term COPY floor

**Scoped proof with an exact finite certificate; no supplier or new κ.**
For the fixed P112 port pair `(j,k)=(0,1)`, changing the nonzero complex
coefficient in PR2021's two-column completion cannot improve its optimal
separate COPY bill. For **every λ ∈ C\{0}**, every exact nine-term
factorization with ordinary transpose satisfies the sharp bound

\[
\min\sum_{i=1}^9 \rho_i^q=7\,8^q+7^q+1,\qquad 0<q\le1.
\]

Here each `ρ_i` is the binary pairing rank on that term's **actual two
supports**, with the original labels. The minimum COPY sum is 64. For
`0<q<1` the optimum is strictly greater than the eight-rank-eight benchmark
`8·8^q`, since `7^q+1>8^q`.

[Hanhong Zhao's PR2321](https://github.com/CrocSwap/integer-mult-bounds/pull/2321),
head `0665be26c2db1bd7f393d829e786698b34b626e4`, established the same optimum
at **λ=1**, including the support classification, duality method and attaining
basis. Those are credited predecessors, not new claims. The new result is the
whole nonzero coefficient family, with an exact support-preserving parameter
map and the previously excluded duality case at **λ=−8**. At that value a
legal basis contains both a left special compensation column and a right
special mixed column. The generic exclusion fails, but the optimum survives.
The certificate includes that exceptional basis explicitly.

Evidence is author-checked. No independent human review or proof-assistant
verification is claimed. The claim is in
[Discussion #2006](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18942817).

## Fixed matrix family and scope

Let `X=root_lines[8:]` in the pinned
[PROTOTYPE.json](../direct-delivery504-global/inputs/hamming/PROTOTYPE.json),
with its original order. It has 112 integer rows of squared norm four.
Put `G=XXᵀ`, `e=e_0`, `f=e_1`, `s=X[0,:]ᵀ`, and `t=X[1,:]ᵀ`. Define

\[
K_\lambda=G-(Ge-4e)e^T+\lambda ef^T,
\quad L=[X,e],\quad
R_\lambda=[(I-ee^T)X,4e+\lambda f].
\]

Then `K_λ=L R_λᵀ`. Its correction changes 53 rows in columns 0 and 1,
has rank two for `λ≠0`, and vanishes on every constrained binary-pairing-one
entry. In particular the diagonal is unchanged. These completion facts are
from [this account's PR2021](../p112-two-column-completion/README.md);
the checker also verifies the mask and the source geometry directly.

An allowed factorization is `K_λ=D Tᵀ`, with `D,T` each `112×9` over C.
For term i, let A_i and B_i be its two nonzero supports. Its charge is
`ρ_i=rank_F2(P[A_i,B_i])`, where
`P_ab=(G_ab/2+1) mod 2`. The root labels realize this pairing by ordinary
binary dot product. Complex coefficients themselves are never reduced mod 2.

The theorem fixes the ports, term count, labels and separate billing. It says
nothing about more terms, another completion, physical sharing between terms,
frame costs, or native execution. The card's positive five-percent supplier
construction gate is not met: this is an explicitly changed algebraic cost
screen. A COPY floor alone is not a complete recursive moment bound, and no
ordinary matrix rank is fed to the packing-ceiling calculator.

## Proof

### 1. Transport the entire support catalogue, not just sampled factors

Let `J_λ=diag(I_8,λ)` in coefficient space, and let `S_λ` scale physical row
0 by `1/λ` while fixing the other 111 rows. Direct inspection gives

\[
R_\lambda=S_\lambda R_1J_\lambda.                 \tag{1}
\]

Both diagonal maps are invertible for every nonzero complex λ. Consequently
`R_λ n` and `R_1 J_λ n` have identical supports, for **every complex n**.
There is no specialization or generic-parameter assumption. The checker
verifies all coefficients of the denominator-cleared polynomial identity
`λR_λ=diag(1,λ,…,λ) R_1 J_λ`.

The exact finite certificates below prove that L and R_1 have rank nine, so
(1) gives rank nine for R_λ and K_λ. Thus every nine-term factorization has
`D=LM`, `T=R_λN`, with `M,N∈GL(9,C)` and `MNᵀ=I`. Writing their columns
as `m_i=(a_i,c_i)` and `n_i=(b_i,d_i)` gives

\[
m_i^Tn_j=\delta_{ij},\qquad \sum_i a_i b_i^T=I_8. \tag{2}
\]

Call a term *mixed* when both a_i and b_i are nonzero. At least eight terms
are mixed, by the rank of the last identity in (2).

For completeness, the PR2321 support catalogue is re-established from the
root input here. For each nonzero binary character h, take the rows of L
or R_1 whose labels have `h·label=1`. The nullspace consists exactly of
coefficients producing support inside `h^⊥`. Each of the 1,022 recorded
kernels has an exact annihilating basis and a nonzero **integer determinant**
minor of complementary rank. This proves equality over C. Modular
elimination is only a way to select the minor; Bareiss integer arithmetic
certifies its determinant.

Set `z=(0,…,0,1)`, `l=(s,−4)`, `v=(s,0)`, and `u_λ=(t,−4/λ)`.
The source has `sᵀs=4`, `sᵀt=2`, and both s,t have nonzero coordinate set
`{1,2,4,7}`. The complete classes are:

| Side / class | Coefficient vectors | Binary span of physical support |
| --- | --- | --- |
| Left Z | nonzero multiples of z | line at port 0 |
| Left E_r | `(a e_r,c)`, `a≠0`; arbitrary c if `s_r≠0`, else `c=0` | hyperplane at removed-frame label r |
| Left V | nonzero multiples of l | hyperplane at live port 0 |
| Left F | all remaining nonzero vectors | full dimension 9 |
| Right W | nonzero multiples of z | span of live labels 0 and 1, dimension 2 |
| Right E_r | `(b e_r,d)`, `b≠0`; arbitrary d if `t_r≠0`, else `d=0` | hyperplane at removed-frame label r |
| Right V | nonzero multiples of v | hyperplane at live port 0 |
| Right U | nonzero multiples of u_λ | hyperplane at live port 1 |
| Right F | all remaining nonzero vectors | full dimension 9 |

The nonzero character kernels at λ=1 have nullity histograms
`L:{0:251,1:256,2:4}` and `R_1:{0:378,1:129,2:4}`.
Distinct nonzero kernels intersect only in zero or the pure z line; this is
also checked exactly. Therefore each non-pure proper support has exactly
one nonzero annihilating character and hence dimension eight. This justifies
the catalogue for every coefficient, including cancellations and nonreal
choices. Equation (1) transports it to all nonzero λ: only the right U line
changes its displayed coefficient vector.

Bilinearity means that the support-pairing rank depends only on the two binary
spans. The recorded 11-by-12 table of actual support ranks proves:

1. Every mixed term costs at least seven. Cost seven requires left V or
   right V/U. The V/V pair costs eight.
2. The only zero-cost class pair is left Z/right V.
3. Left Z costs one against every right class except V.
4. Right W costs one against left Z or V, and two against left E/F.

These are the same finite support facts as PR2321; the parameter transfer is
what permits their use for this larger family.

### 2. The exceptional dual pairing

The relevant coefficient pairings, under ordinary transpose, are

\[
z^Tv=0,\qquad l^Tv=4,\qquad
l^Tu_\lambda=2+16/\lambda,\qquad z^Tu_\lambda=-4/\lambda. \tag{3}
\]

The unique zero-cost class pair cannot occur at a diagonal factor index,
because its coefficient pairing is zero, contrary to (2). Every term has
positive COPY rank.

The third pairing in (3) vanishes precisely at **λ=−8**. PR2321's exclusion
of an off-diagonal right U when a left V occurs is therefore unavailable at
this value. We handle it explicitly below. No other pairing used in the
argument acquires a new zero on C\{0}.

There are nevertheless at most **two cost-seven mixed terms**, uniformly
in λ. Without a left V, only the fixed right V and U lines can provide them,
and an invertible basis uses each line at most once. If a left V occurs at
index i, any right V must also have index i, since `lᵀv=4`. If it does, that
term costs eight and only right U can provide a cost seven elsewhere. If it
does not, only the left V term itself and the one right U term can cost seven.
This argument does not assume `lᵀu_λ≠0`.

### 3. Complete compensation cases

If all nine terms are mixed, their sorted ranks dominate seven eights and
two sevens. Otherwise exactly eight are mixed and one term is not:

- **Left pure Z.** Off-diagonal duality forces `d_j=0` for all other indices.
  Right U cannot occur among the mixed terms. Only left V and right V can
  supply cost seven; `lᵀv=4` and the V/V cost of eight permit at most one.
  The complete profile dominates seven eights, a seven and a one.
- **Right pure W, left V at that same index.** All other left columns have
  `c_j=0`, so none is V. Right V cannot occur elsewhere. If `λ≠−8`, neither
  can right U: the profile dominates eight eights and a one. If `λ=−8`,
  right U is allowed once: the profile still dominates seven eights, a seven
  and a one. This is the additional case missing from a verbatim transfer
  of the fixed-coefficient proof.
- **Right pure W, left E/F at that index.** The pure-right term costs two,
  and among the other eight at most two terms cost seven. The complete
  profile dominates six eights, two sevens and a two.

The left-pure case includes a term that is pure on both sides. These cases
exhaust the possibilities by (2), so no compensation term is omitted.

Let `P=(8,8,8,8,8,8,8,7,1)`. All these lower profiles dominate P componentwise
when sorted, except `Q=(8,8,8,8,8,8,7,7,2)`. The latter has the same mass 64
and is majorized by P (all nine integer partial sums are checked). More
directly, its power-sum difference from P is
`7^q+2^q−8^q−1≥0`: concavity makes the increment from 1 to 2 at least the
increment from 7 to 8. Thus every case costs at least `7·8^q+7^q+1` for
`0<q≤1`.

### 4. Uniform attainment and a genuine exceptional basis

The PR2321 attaining basis works unchanged. Let p=1, the first nonzero
coordinate of s. Form N from I_9 by replacing column p with `v=(s,0)`;
`s_p=1` proves invertibility. Set `M=N^(−T)`, `D=LM`, `T_λ=R_λN`.
The first eight physical T columns are independent of λ and the last is
`4e+λf`. Its support is exactly `{0,1}` for every nonzero λ. Hence all nine
COPY ranks stay `(8,7,8,8,8,8,8,8,1)`. The checker verifies both coefficient
matrices of `D T_λᵀ=K_λ` (25,088 exact entries), as well as the fixed mixed
supports and the last column's support formula.

There is also an explicit exceptional attainer. Let B be I_8 with column
p=1 replaced by t. Define the first eight columns of N by
`n_r=(B_r,sᵀB_r/4)`, and its last column by `(0,−1/4)`. Then its dual M has
last column `l=(s,−4)`. At λ=−8, column p of N is exactly
`u_−8=(t,1/2)`, orthogonal to l. The certificate verifies invertibility,
the complete endpoint and the same COPY profile P. This exhibits the newly
allowed case rather than merely observing a vanishing scalar. It is a
counterexample to extending the **generic exclusion step**, not to PR2321's
λ=1 theorem and not to the optimum proved here.

## Reproduction and verification boundary

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -O -B research/p112-coefficient-copy-floor/verify.py
python3 -I -O -B research/p112-coefficient-copy-floor/test_controls.py
python3 scripts/research_package.py --package research/p112-coefficient-copy-floor --check-only
python3 scripts/research_package.py --package research/p112-coefficient-copy-floor
```

Expected main marker:

```text
PASS_P112_COEFFICIENT_COPY_FLOOR kernels=1022 lambda=nonzero_complex exception=-8 copy_sum=64 controls=8 no_new_kappa
```

The canonical receipt SHA256 is
`ca9b5b26f4571c08ec9f3163c9daf9c29ec9556be0b79797a220d203fb5bb289`.
The normal verifier is read-only and imports neither PR2021 nor PR2321 code.
`--write NEW.json` creates a complete freshly checked receipt exclusively;
it refuses an existing output. A Git-free export needs this package and the
source prototype at its original relative path. Metadata checks separately
validate Git provenance.

The eight mathematical controls cover zero-parameter exclusion, a wrong
anchor in the symbolic map, a left kernel wrongly used on the right, missing
compensation, omission of the pure factor, exact nonreal phase versus
Hermitian transpose, the exceptional legal basis, and forbidden zero-cost
diagonal duality. The separate CLI controls test source/receipt corruption,
type preservation, duplicate keys, nonfinite numbers, wrong witness ranks,
wrong exceptional basis, output preservation and an optimized Git-free replay.

The universal conclusion is the written proof using finite premises and the
exact parameter identities. Finite replays are not a coefficient search and
not a formal proof of integer multiplication. No full native, frame, dirty
restoration, owner/idle invoice, precision/tape, all-size, analytic-transfer,
selected cold replay, Lean or hosted CI check has been performed.

## Open next questions

Can **additional terms** lower the separate COPY power for this fixed family?
A concrete first step is a ten-term tight-frame coefficient model
`M,N∈C^(9×10)`, `MNᵀ=I_9`, at the now-identified λ=−8. The catalogue above
still describes individual supports, but dual-basis off-diagonal exclusions
no longer follow; classify that replacement constraint before any search or
physical synthesis. This matters because the present result closes the
coefficient-only escape for nine terms. The blocker is redundant-factor
compatibility, not a missing coefficient sample. No favorable candidate or
physical realization is claimed.

The adjacent [overcomplete-factor claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18942846)
fixes λ=+1 and allows arbitrary term counts. Coordinate with that work before
following up; this theorem does not settle its changed factor-count premise.

## Credit and provenance

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Hanhong Zhao / @Hope7Happiness / PR2321 supplied the fixed λ=1 optimum, its
support classification, duality/compensation proof, and the uniform basis used
here. This account's PR2021 supplied the rank-nine completion and its COPY65
factorization. Arham Tahir / PR1591 and Gareth Davidson / @bitplane / PR1652
supplied related one-anchor support and compensation methods. Credit remains
with woklerx / PR1447 and PR1077, DreamingOfClouds / PR717, themilkman216 /
PR968, and the PR845/523/514/507/425/433 root-data and decoder lineage.

Base main: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Scientific input bytes and Git blob are pinned in [SOURCES.json](SOURCES.json).
PR2321 is a mathematical predecessor, not an executable dependency or an
assumed maintainer-approved result; all used finite premises are rechecked.
[TASK.json](TASK.json) records the changed task scope and overlap. Frozen
predecessors and the selected frontier are untouched. New work is Apache-2.0.
