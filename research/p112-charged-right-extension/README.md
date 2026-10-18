# Charged auxiliary terms do not beat the P112 right-extension COPY floor

For the fixed PR2021 P112 completion, left factors in `col_C(X,e0)` and right
factors in `col_C(X,e0,e1)`, the sharp separate COPY-power minimum is
**`8*8^q` for every real `0<q<=1`**, over any finite number of complex terms.
This includes **charged pure-projection terms**. COPY itself has minimum 64.

This closes the explicit remaining case in ywz65's [PR2515](https://github.com/CrocSwap/integer-mult-bounds/pull/2515):
exactly eight mixed terms and charged pure compensation. Its free-pure result,
the support catalogue and its many-mixed-term argument retain their credit.
The added lemma is stronger than required: **any eight-term projected dual
basis has at most one cost-seven term**, regardless of its pure terms. This
uses the shared coordinate support of the fixed two roots, a premise not used
in the predecessor's coarser two-exception count.

This is a scoped written proof supported by independently implemented exact
finite checks. It supplies no physical word, complete supplier or new kappa.

## Model and finite premises

Remove the first eight coordinate-frame rows from the pinned root prototype.
The remaining norm-four root matrix is `X` (112 by 8), with its original binary
labels `lambda_i` in `F2^9`. Write

```text
e=e0, f=e1, s=X[0,:]^T, t=X[1,:]^T, G=XX^T,
K=G-(Ge-4e)e^T+ef^T,
D_i=Xa_i+c_i e,       T_i=Xb_i+u_i e+v_i f,
rho_i=rank_F2 B[supp(D_i),supp(T_i)],  B_ij=lambda_i dot lambda_j.
```

All transposes are ordinary, including for complex coefficients. Exactness is
on **all entries of this fixed K**; its required mask entries equal G. A term
is mixed when both `a_i,b_i` are nonzero, and pure otherwise. Zero physical
factors may be discarded. Pure terms with nonzero factors and zero COPY remain
allowed; their number is unrestricted. Every term is billed separately.

The factor matrices `[X,e]`, `[X,e,f]` have ranks nine and ten. Their full column
rank makes coefficient comparison valid. The exact root data give

```text
s=(0,1,1,0,1,0,0,1),     t=(0,1,1,0,1,0,0,-1),
s.s=t.t=4,              s.t=2,
supp(s)=supp(t)={1,2,4,7}.
```

Let `F_j` denote the removed coordinate root's label. The proper binary support
spans of factors with nonzero root projection are exactly:

| Side | Root direction | Required extra coefficients | Support span |
|---|---|---|---|
| left | coordinate `e_j` | `c=0` if `s_j=0`; otherwise arbitrary | `F_j^perp` |
| left | `gamma s` | `c=-4gamma` | `lambda_0^perp` |
| right | coordinate `e_j` | `u=0` if `s_j=0`, `v=0` if `t_j=0`; otherwise arbitrary | `F_j^perp` |
| right | `gamma s` | `u=-4gamma`, arbitrary v | `lambda_0^perp` |
| right | `gamma t` | `v=-4gamma`, arbitrary u | `lambda_1^perp` |

Here each root multiplier is nonzero. Every other non-pure factor has full
binary support span. Distinct character kernels share no nonzero root
projection, so the displayed hyperplanes cannot hide a smaller mixed support.

`verify.py` reconstructs all 1,022 character kernels. For each, rational RREF
agrees with the displayed model, exact annihilation gives the rank upper bound,
and a separately implemented modular rank gives the matching lower bound.
These rational kernel identities hold over C. This is an exhaustive algebraic
classification of arbitrary complex coefficients, not rational sampling.

The 110 support-class pairings are recomputed by two binary eliminators. All
mixed terms cost at least seven. The cost-seven class pairs are precisely:

```text
(left coordinate e_j, right s), (left coordinate e_j, right t),
(left s, right coordinate e_j), for j in {1,2,4,7};
(left s, right t).
```

Left s / right s costs eight. A full-span factor paired with any non-pure
factor costs at least eight. These are the predecessor's support facts,
independently rechecked here.

## Proof, including the charged-pure case

**1. Projection and term count.** Comparing the root/root block gives
`sum_i a_i b_i^T=I8`, involving mixed terms only. Thus at least eight mixed
terms occur. If exactly eight occur, matrices `A=[a_i]`, `B=[b_i]` satisfy
`AB^T=I8`; hence `b_i^T a_j=delta_ij`.

**2. New dual-basis lemma: at most one cost-seven term.** Suppose first a
cost-seven term has left direction s at index j. Another left-s term cannot
occur because the a columns form a basis. Any other cost-seven term must
therefore have right direction s or t. At a distinct index its pairing with
`a_j` is nonzero, since `s.s=4` and `t.s=2`, contradicting duality.

If no cost-seven term has left direction s, all such terms have a coordinate
left direction and right direction s or t. Basis independence permits at most
one right-s and one right-t column. If both occurred, the left coordinate at
the right-s term would have `s_j!=0`. Then also `t_j!=0`, so its off-diagonal
pairing with the right-t column is nonzero, again contradicting duality.
This proves the lemma. The checker exhausts all **169 ordered pairs** of the
13 cost-seven classes and records a forced nonzero cross pairing for each.
Nonzero complex rescalings cannot change those nonzero pairings.

**3. With free pure compensation, no cost-seven term occurs.** We retain
PR2515's coefficient argument and recheck its premises. The complete zero-COPY
pure terms span just

```text
(Xs-4e)e^T,       e(Xs-4e)^T,       ef^T.
```

Indeed, for a left-pure e factor the right factor must annihilate lambda_0,
whose kernel is `span((s,-4,0),(0,0,1))`. A pure right factor has support e,
f, or both; the corresponding left annihilator kernels are `C(s,-4)`, `Ce`,
and zero. This covers cancellations and any number of free pure terms.

Let their aggregate coefficients be alpha,beta,gamma in the displayed order.
Comparing root/e, root/f and e/root blocks yields

```text
u_i=-(1+alpha) b_i.s,      v_i=0,      c_i=-beta a_i.s.
```

The e/e coefficient is
`4beta(1+alpha)-4alpha-4beta=4`, so `alpha*(beta-1)=1`.
Thus alpha is nonzero and beta differs from one. A left-s exceptional factor
would force beta=1; a right-s exceptional factor would force alpha=0; a
right-t exceptional factor needs `v_i!=0`. Each is impossible. (The e/f
block fixes gamma=1.) Consequently a cost-seven mixed term forces at least
one positive integer COPY charge among the pure terms.

**4. Exactly eight mixed terms, arbitrary pure charges.** By the new lemma
there are zero or one cost-seven terms. In the first case, the mixed bill
alone is at least `8*8^q`. In the second it is at least `7*8^q+7^q`, and
Step 3 forces a pure term of integer charge at least one. Thus the full bill
is at least `7*8^q+7^q+1 >= 8*8^q`, using `7^q+1>=8^q` for `0<q<=1`.
This argument allows all charged pure terms; none is declared free or omitted.

**5. Nine or more mixed terms.** Retain PR2515/PR2398's rank argument. All
cost-seven root/root contributions have aggregate form `s x^T+y s^T+z t^T`,
of rank at most three. Since their sum plus the other rank-one mixed terms
is I8, at least five other mixed terms occur, each costing at least eight.
With at least nine mixed terms, the sorted charge list therefore dominates
`Q=(8,7,7,7,7,7,7,7,7)`. The list `P=(8,8,8,8,8,8,8,8,0)` majorizes Q
(both sum to 64). Concavity of `x^q`, including `0^q=0`, gives
`sum Q_i^q >= sum P_i^q=8*8^q`. Additional terms cannot lower the bill.

**6. Sharpness.** The credited PR2398 identity

```text
K=sum_j X[:,j]X[:,j]^T + (4e-Xs)e^T + ef^T
```

attains `(8,8,8,8,8,8,8,8,0,0)`. It lies in the stated spaces. This proves
the minimum for all finite complex decompositions in this extension.

## Reproduce and evidence limits

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p112-charged-right-extension
```

The mathematical check is read-only and works without Git:

```sh
python3 -I -O -B research/p112-charged-right-extension/verify.py
```

It checks the complete finite premises, 169 dual conflicts, six exact rational
fixtures (75,264 matrix entries), and nine rejecting controls. In particular,
the credited PR2321 nine-term attainer has profile `(8,7,8,8,8,8,8,8,1)`:
it is **accepted with its actual positive pure charge**, rather than rejected
at PR2515's former scope boundary. Four free-term witnesses and an overcomplete
mixed-pair witness exercise the other cases. Exact Gaussian unit arithmetic
checks the ordinary/Hermitian phase distinction. `--out NEW.json` exclusively
creates regenerated evidence; default replay compares the entire RESULT.json.

The finite certificate does not formally verify the written quantified proof.
No independent human review, formal-kernel build, hosted CI, selected supplier
cold replay, native/frame/restoration program, chronological hosting, physical
COPY sharing, precision/reserve or all-size multiplication theorem is claimed.
This fixed coefficient, port pair and two factor spaces remain essential scope
restrictions. The selected record is unchanged.

## Open next questions and expansion decision

The present right extension is closed for separate COPY power: paying pure
terms does not justify another optimization round in these same spaces.
**Decision: stop this fixed-space route.** A useful next experiment must change
the factor spaces, target completion, or actual shared-work contract.

One bounded question is whether enlarging the **left** space to `col(X,e0,e1)`
permits two cost-seven dual positions without repaying their saving. First
compute that side's character kernels and test the smallest ten-term exact
factorization, with every pure charge retained. The new dual-conflict lemma
uses the one-sided left restriction and does not exclude this changed problem.
This is an exploratory next step, not authorization for a larger search or a
prediction of success. A physical use still needs its complete consumer and
restoration invoice; unknown costs are not zero. [TASK.json](TASK.json) records
the structured question and blocker.

## Sources, attribution and task selection

Base canonical main `6ca6f217708b075814de409ad693fea9a2aaa760`, priority revision 5.
The task picker nonce `1a351e5f7fedbf33ddba063ff9f468ae` selected complex
mechanisms. The rank-shape card was explicitly **changed** to PR2515's algebraic
handoff after overlap checks; this does not meet that card's physical 5% gate.
The source-binding baseline and prescribed local-ceiling example passed.
[SOURCES.json](SOURCES.json) pins the prototype, historical catalogue/selection
and exact retained predecessor texts. No predecessor executable is imported.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2006#discussioncomment-18959554)
records the precise object and changed premise.

- **ywz65, PR2515**, `92231f9e4a4737aaae21e2bc01f4d3dee5ead140`: extended
  support catalogue, free-pure theorem, coefficient comparison, many-mixed
  argument and explicit charged-pure handoff. Its README is retained verbatim.
- **commdata2338, PR2021/PR2398**, the completion, arbitrary-term minimal-space
  argument and ten-term boundary; PR2398 head
  `8051d99dfd91a788d25bfc92c3863a33c658a5a9`. Its proof is retained verbatim.
- **Hanhong Zhao, PR2321**, the minimal-space support and nine-term attainer.
  Related geometry/support lineage: Mihir Srivastava/PR845, Arham Tahir/PR1591,
  Gareth Davidson/PR1652, woklerx/PR1077/1447/1180, DreamingOfClouds/PR717,
  themilkman216/PR968, icekylinx's retained prototype and its source notices.

New contribution: the stronger projected dual-conflict lemma, the removal of
the free-pure premise, an independent exact checker and explicit paid-pure
positive fixtures. Prepared by **Arham Tahir with substantial OpenAI Codex
assistance** in derivation, implementation, verification and writing.
Apache-2.0; predecessor notices and licenses remain applicable.

## Submission validation

The registered replay passed on Windows with bundled CPython 3.12.14, normally
and with an optimized Git-free renamed export. All four actual-CLI test groups
passed, including changed source bytes, full-receipt corruption, deterministic
regeneration and exclusive output. The normal Python 3.14.6 regeneration gave
the same entire receipt. Windows sandbox TEMP/TMP were set to a writable
workspace directory after the system temporary directory rejected access.
The final upstream checkpoint is `84f8e607779b81c05edc962d4981d1f9b4b9bc9f`;
guidance, selected record, source prototype and package runner are unchanged.
Final overlap coverage and exact timestamps are recorded in TASK.json.
