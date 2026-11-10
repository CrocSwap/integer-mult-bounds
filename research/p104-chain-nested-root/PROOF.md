# Chain-nested root: identity, chain merge, invoice

Tags: **[P]** proved below by hand, **[C]** checked by exact replay on the literal
data, **[A]** inherited assumption. `chain_root.py` and `independent/check_root.py`
do the exact checks. The native word is #6824's, and its proof is `PROOF-6824.md`
and `PROOF-6805.md`.

## 1. The family

Take child sizes `sL`, `sR`, with `gL`, `gR` entries. The fields are `A, f_0..f_{gL-1},
h_0..h_{gR-1}`, plus one empty field `E` when the count would be odd, so `n` is even.
The priced shape is `(9|9)`, with `n = 20`.

Each query is `T_k = I + (S-1) R_k`, `R_k = x_k y_k^T`, `y_k x_k = 0`. Here
`S = λ Q^-1` with `λ = (1+i)/2 + ((1-i)/2) Q^2`, so `S^2 = 1` on `Q^4 = 1`: `S = 1` at
`Q = 1, i` and `S = -1` at `Q = -1, -i`. The time order is L sites, thin queries, R sites.

| Site | `x` | `y` | Support `M` |
|---|---|---|---|
| L, `i` | `A + f_i + 2Σ_{j<i} f_j` | `A* - f_i*` | `{A, f_0..f_i}` |
| R, `m` | `-A + h_m + 2Σ_{l>m} h_l` | `A* + h_m*` | `{A, h_l : l >= m}` |

For `gL, gR` odd the three thin queries have parameters
`(a,u,p,q) = (0,1,0,1), (-1,2,1,0), (-1,3,1,-1)`:

```text
x = aA + (a+1)Σ f_i + (1-a)Σ h_l + qE
y = uA* + (1-u)Σ (-1)^i f_i* + (u-1)Σ (-1)^(gR-1-l) h_l* + pE*
```

Other parities have their own closed forms in `chain_root.thin_vectors`. They are not
priced here and this proof does not cover them.

## 2. The root endpoint [P]

**Lemma 1 (sign Gram).** Let `(x_k, y_k)`, `k = 0..n`, with `n` even, satisfy
`y_i x_j = sgn(i-j)`, let the `x_k` span the `n`-dimensional space, and let
`Σ (-1)^k x_k = 0`. Then `(I-2R_n)...(I-2R_0) = -I`.

*Proof.* With `L` the strictly lower part of `G = Y^T X`, the product expands to
`I - 2X(I+2L)^{-1}Y^T`. All entries of `L` below the diagonal are 1, so
`I + 2L = G + J`, where `J` is the all-ones matrix. Let `c_k = (-1)^k`. Then `Gc = 0`,
because an odd alternating sum of signs vanishes, and `Jc = e` because `n+1` is odd.
So `(G+J)^{-1} e = c`. Put `B = X(G+J)^{-1}Y^T`. Then
`BX = X(G+J)^{-1}(G+J-J) = X - X(G+J)^{-1}e e^T = X - (Xc)e^T = X`.
The `x_k` span, so `B = I`, and the product is `I - 2I = -I`. QED.

**The family satisfies it for `gL, gR` odd.**

- Within L, `y_i x_l = 1 - [l=i] - 2[l>i]`, which is `sgn(i-l)`. Within R the same
  computation gives the same sign. Across, `y_R x_L = 1`, `y_L x_R = -1`.
- For thin `(u,p)` against `(a',q')`, `y x = a'(2-u) + pq'`, because both alternating sums
  equal 1. The three parameter rows give exactly the sign pattern.
- `y_{L,i} x_thin = a' - (a'+1) = -1`. `y_thin x_{L,i} = u + (1-u)[(-1)^i + 2Σ_{j<i}(-1)^j] = 1`.
  The R side mirrors this: `y_{R,m} x_thin = 1`, `y_thin x_{R,m} = -1`.
- Alternating sum: the L sites contribute `A + Σf`, the R sites `-A + Σh`, and the thin
  queries `-Σf - Σh`.
- Span: `x_1 - x_2 = E` for the second and third thin queries. Modulo `A`, the sites give
  all `f_i`, `h_l` triangularly. And `A = x_thin1 - 2(-A + Σh)` lies in the span.

`verify_root` also checks all of this by exact multiplication for the replayed shapes [C].

## 3. Stage factors [P]

Let `P_k` be the coordinate projector on `M_k`, and `Δ_k = I + (D_k-1)P_k`. Each `R_k` lies
inside `M_k`, so `P_k R_k = R_k P_k = R_k`.

**Lemma 2.** `P_k` commutes with the product `U_k` of all `T_s` with `s` after `k`.

For an R site, every later `x_s, y_s` is supported in `M_k`. For an L site, `U_k` is the
inverse of the prefix `T_k...T_0` up to the endpoint scalar (`S = 1`: trivially `T = I`;
`S = -1`: `U_k = -(T_k...T_0)^{-1}`), and that prefix is supported in `M_k`.

Hence `Π (Δ_k T_k) = (Π Δ_k)(Π T_k) = S · Π Δ_k`, where each `Δ_k` moves left across
exactly `U_k`. (Thin queries are `T` factors with no `Δ`.) This is the only place the
endpoint is used. Here `Π Δ_k` is diagonal with `A -> all D`,
`f_i -> D` over L sites `>= i`, `h_m -> D` over R sites `<= m`, `E -> 1`.

## 4. Chain-merge lemma [P]

**Lemma 3 (chain merge).** Fix one group (L or R) with sites in time order, and for each
site a decomposition `P_k = Π_k + Σ_{ℓ ∋ k} E_ℓ`, where `E_ℓ = φ_ℓ γ_ℓ^T` and `C(ℓ)` is a
set of consecutive sites. Assume:

1. `γ_ℓ φ_ℓ = 1`, and `γ_ℓ φ_ℓ' = 0` for `ℓ != ℓ'`;
2. `φ_ℓ, γ_ℓ` are supported in `M_k`, and `y_k φ_ℓ = 0`, `γ_ℓ x_k = 0`, for all `k` in `C(ℓ)`;
3. `Π_k` is idempotent with `Π_k x_k = x_k` and `y_k^T Π_k = y_k^T`.

Set `G_k = (I + (D_k-1)Π_k) T_k` and `W_ℓ = Π_{k in C(ℓ)} D_k`. Then the ordered product of
`Δ_k T_k` equals the ordered product of `G_k` with one factor `I + (W_ℓ-1)E_ℓ` inserted
anywhere within or right after `C(ℓ)` such that only sites of `C(ℓ)` are crossed.

*Proof.* The `E_ℓ` are orthogonal idempotents inside `P_k` by (1) and (2), so
`E_ℓ Π_k = Π_k E_ℓ = 0`, and
`Δ_k = (I + (D_k-1)Π_k) Π_{ℓ∋k}(I + (D_k-1)E_ℓ)`. By (2), `E_ℓ T_k = E_ℓ = T_k E_ℓ`, so
`E_ℓ` commutes with `G_k` for each `k` in `C(ℓ)`. Factors for different lines commute by (1).
So each factor `I + (D_k-1)E_ℓ` slides to the chosen time, and they multiply to
`I + (W_ℓ-1)E_ℓ`, since `E_ℓ^2 = E_ℓ`. QED.

**Instance.** L line `j >= 1`: `φ = f_{j-1}`, `γ = f*_{j-1} - 2A*`, `C = {sites j..gL-1}`,
paid at site `j`. R line `j <= gR-2`: `φ = h_{j+1}`, `γ = h*_{j+1} + 2A*`, `C = {sites 0..j}`,
paid at site 0. Then `γ x_i = 2 - 2 = 0` and `y_i φ = 0` for `i` in `C`.
The lines fill each support outside a rank-two plane, because `|M_k| - 2` lines cover site `k`.
`verify_root` checks each hypothesis exactly, including that `Π_k` has rank two [C].

**Scope.** The lemma needs nothing about the fields beyond these hypotheses, and no statement
is made about other merge structures.

## 5. The literal caller [C, with P for the gadget]

At a full site, the gates `LAMBDA(x,-1); LOCAL(s,y,x); LAMBDA(x,1); ADD(x,y,-1)` act on
registers `(x,y)` as `D_s (x + (S-1) y, y)`. That is `G_k` in the site's basis, whose first
two columns are `x_k` and a vector `w_k` with `y_k w_k = 1` [P]. A thin query is the same
without `D`. A final `LAMBDA(r,-1)` turns `S·Π Δ` into the target `Q^-1 · Π D`.

**Theorem.** For the priced word and all 20 arbitrary caller inputs, the output of role `r`
is `Q^-1 Π_{s in W_r} D_s` times input `r`, exactly, with no other coefficient.

Sections 2 to 4 prove this for the root at `(9|9)`. These literal checks bind the word to it:

- `caller.replay` (forward) and `rows.transpose` (reverse), all 400 coefficients over
  `Q(i)[q, D_s]`;
- `independent/check_invoice.caller_columns`, a separately written adjoint;
- `independent/check_root.family`: the symbolic matrix product from the formula; the
  literal word at `Q = ±1`, `D = 1`, giving `±I`; and at each of the 16 `IDLE_ONE` events,
  the register's line and dual read from the word itself, compared with the formula, with
  each covered native call shown to miss that line.

Tree children in the gate use the retained binary supplier, whose proof is in the retained
caller lineage; there the identity is checked by replay and is not re-proved here.

## 6. Whole-job contract, and what is not proved here

Every credited target is a whole transform of one independent arbitrary input, and every
paid idle is one whole transform of one field per port. The word has 2,080 main fields and
10,152 native helper fields, all distinct, with no copied input.

A whole idle on stage set `W` has rank `8|W|`, on disjoint fresh axes. The physical replay
checks its phase, and the two-coordinate exchanges on both boundaries are charged.

**Caveat.** Ranks 48 to 64 and spans of up to 8 sites extend the rule that #6726 used at
rank 40; this package gives no new compiler proof. Also, the merged line crosses sites with
different ordinary bases, while #6716's coordinates sit in one shared basis: see
`ADAPTERS.md`. The job is applied once, to one register, so the accepted identity is
the theorem of section 5. Reviewers should confirm that the `compiler` assumption covers it.

## 7. Invoice and gate

Per port, the outer histogram at `(9|9)` is `T = {1:1, 9:2, 17:2, ..., 73:2, 145:1}` and
`P = {1:3, 8s:2 for s = 1..8}`, for an outer rank margin of 305. Over 18 native calls the
total is `T - P` rank mass 760, unchanged from #6824. `pricing.py` compares this formula with
the literal histogram and the physical checks.

**Gate [C].** The same constructor at `(4,4,1|1,4,4)` gives a word with 32 roles and 518
events that passes both replays. On the same native word, its target and paid histograms
equal those of the retained #6726 caller minus one cancelling pair `T_32 = P_32 = 208`.
Both interval engines then place its crossing in `(0.00330823456614, 0.00330823456615)`,
which is #6824's interval. So the family reproduces #6824 exactly at that shape.

**Crossing [C].** Both interval engines place the crossing of the priced word in
`(0.0033718004754, 0.0033718004755)`. The Decimal value `.00337180047549672` is a diagnostic
in the independent audit, not a certificate. The retained derivative bound through `.0034`
gives uniqueness.

## 8. Theorem context

This is a finite construction plus a complete invoice. The conditional statement is the
retained chain's: given `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery` [A], the outer theorem admits `κ = 0.00337180`. The claim is below the
retained BIT saving `.0034`, so #6805's pin is unchanged. The selected `κ` is unchanged.

| Item | Status |
|---|---|
| Root endpoint and sign Gram, odd/odd | P, and C at both shapes |
| Stage factors and chain merge | P, hypotheses C at both shapes |
| Whole-word identity at `(9|9)` | P + C |
| Whole-word identity at the gate | C (binary supplier retained) |
| Native word | C here; proof in `PROOF-6824.md`, `PROOF-6805.md` |
| Physical contacts, adapters, allocation, invoice | C, two implementations |
| Crossing, strictification, compiler arithmetic, 54+4 outer inequalities | C |
| Five framework assumptions | A, not discharged |
| Compiler acceptance of whole idles at ranks 48 to 64 across several sites | Not proved here |
