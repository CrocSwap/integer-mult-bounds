# Two independent central commutators still cost eight calls

**Scoped exact minimum in a new nonabelian address model; no new kappa.** In the full group algebra `F2[UT_3(F_4)]`, two independent central commutator outputs on two arbitrary dirty registers have exact minimum eight paid factors. The direct construction costs eight, the complete exact search excludes every word through six, and an augmentation-ideal parity argument excludes seven. The result tests whether separate commutators can share calls through rank-one register mixing; this target profile has no saving.

The selected result remains the conditional `kappa = 0.001672660197076918` from #1094. Its complex side binds (`0.001675462676808103...` versus bit `0.001733427039589844...`). This formal word result has no physical supplier mapping and changes no selected primitive budget.

## Model and construction

Let `F_4 = F_2[w]/(w^2+w+1)` and write the unitriangular group as

```text
H = UT_3(F_4) = {(a,b,c): a,b,c in F_4}
(a,b,c)(a',b',c') = (a+a', b+b', c+c'+a b').
```

The group has order 64 and abelianization `F_4 x F_4`, an elementary abelian group of rank four. The four paid labels are

```text
X_1 = (1,0,0), X_w = (w,0,0), Y_1 = (0,1,0), Y_w = (0,w,0).
```

Each label is an involution. Their central commutators include

```text
Z_1 = [X_1,Y_1] = (0,0,1),
Z_w = [X_w,Y_1] = (0,0,w).
```

A paid factor is `D_N(g) = I + ([g]+[e])N`, where `g` is one of those four labels and `N` is any rank-one idempotent in `M_2(F_2)`. There are six such idempotents and 24 paid factors. Every factor costs one call; the identity must hold coefficientwise in all 64 group elements, so it applies to arbitrary dirty register values.

For `E_11` and `E_22`, the eight-call word

```text
D_E11(X_1) D_E11(Y_1) D_E11(X_1) D_E11(Y_1)
D_E22(X_w) D_E22(Y_1) D_E22(X_w) D_E22(Y_1)
```

is exactly `diag([Z_1],[Z_w])`. Each four-factor block is one central commutator on its coordinate. This is a fully charged upper bound: no call, clean role, copy, frame change or restoration is free in the model.

## Exact lower bound

Let `I` be the augmentation ideal of `F_2[H]`. Since `H/[H,H]` has the four paid labels as an `F_2` basis, `I/I^2` has four independent label coordinates. Both central target elements lie in `[H,H]`, so the target matrix is the identity modulo `M_2(I^2)`.

For a word of paid factors, multiplication modulo `I^2` gives

```text
I + sum_i ([g_i]+[e]) N_i.
```

Independence of the four label coordinates forces `sum_{i:g_i=g} N_i = 0` for each label `g`. Every rank-one idempotent over `F_2` has trace one, so each label occurs an even number of times. Thus every word for this target has even length. The only possible improvement on the eight-call upper bound is therefore a word of length at most six.

The verifier builds the complete radius-three ball for the 24-factor alphabet, merging only equal exact `2 x 2` matrices over the full group algebra. Its new-state layer sizes are `[1, 24, 412, 6440]`, for 6,877 states total; the 14,425 raw words of lengths zero through three are all represented. For every left state `A`, it computes `A^{-1} target` exactly and checks whether that state lies in the same ball. Since each factor is an involution, any word of length at most six splits into two radius-three words. No match exists. Together with parity and the direct word, this proves the exact minimum eight in this finite model.

The certificate records the exact state-layer SHA-256 digests. The packed transition implementation is cross-checked against generic group-algebra matrix multiplication on 10,488 transitions. The group law is checked on all 64^3 triples; all six idempotents, all factor inverses, the four-call one-output commutator, and the direct eight-call pair are checked. All eight one-factor deletions of the direct word and a mutation of `Z_w` to `Z_{w^2}` fail their endpoint controls.

## One bounded pivot: a dependent three-output target

The central relation `Z_{w^2}=Z_1 Z_w` suggests a separate three-role construction. The direct coordinate bill is 14 calls: four for `Z_1`, four for `Z_w`, and six for `Z_{w^2}` using the composite label `X_{w^2}=X_1 X_w`, which is not a primitive label.

I tested the specific sharing mechanism that first builds commutators and then combines their rank-one updates. For each rank-one idempotent `N` in `M_3(F_2)`,

```text
D_N(X_1) D_N(Y_1) D_N(X_1) D_N(Y_1) = D_N(Z_1)
D_N(X_w) D_N(Y_1) D_N(X_w) D_N(Y_1) = D_N(Z_w).
```

Each is a fully charged four-call block. The complete ordered family of up to three such blocks has 56 block choices and 178,808 total candidate sequences. Exact multiplication in the central four-element group algebra finds no sequence for `diag([Z_1],[Z_w],[Z_{w^2}])`. This rules out only that block family; it is not a lower bound for arbitrary words of 12 calls or fewer.

An explicit 14-call control applies the first commutator on role 1, the second on role 2, and
`X_1 X_w Y_1 X_1 X_w Y_1` on role 3. The full group-algebra endpoint matches the target under both the packed engine and generic matrix multiplication. The verifier also checks all 56 four-call block endpoints, 3,136 pairwise block products against full group-algebra multiplication, and all 14 single-factor deletions of the direct word.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/ut3-f4-central-pair-seedfcd785a2/verify.py
python3 -I -O -B research/ut3-f4-central-pair-seedfcd785a2/verify.py
```

Both print `PASS_UT3_F4_CENTRAL_PAIR` and the certificate summary. `CERTIFICATE.json` contains the state counts and exact layer digests. `SOURCES.json` pins the base, selected-result chain and predecessor notes.

## Scope and attribution

This is a finite group-algebra result for this exact order-64 group and four-label alphabet: an exact two-role minimum plus a bounded three-role block-family obstruction. All paid matrices use the listed rank-one idempotents; the three-role pivot uses the 28 rank-one idempotents of M3(F2). It changes the address group and commutator geometry from the `Q8` central-pair result by Aaron Wang, while retaining the scalar-idempotent register model descended from eumemic's PR #288 and woklerx's PR #1443. It is distinct from the three-register abelian rational-frame obstruction and the `GL_2(F_2)` mixed-target census. It says nothing about larger alphabets, other groups, a physical bit supplier, or the multiplication exponent.

## Open next questions

Can an arbitrary word of at most 12 paid factors realize the dependent central triple `diag([Z_1],[Z_w],[Z_{w^2}])` outside the tested commutator-block family? A witness would reduce the 14-call direct bill. The first step is to derive a quotient bound or a small structured extension that admits noncentral intermediate factors, then screen its complete cost. The blocker is the 112-factor alphabet in `M_3(F_2)` and its larger exact state space.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No independent human or proof-assistant review is claimed. Apache-2.0.
