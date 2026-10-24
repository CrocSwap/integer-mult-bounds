# Exact q-inverse W fanout: construction and cost contract

Status: **STATIC_METHOD_READY; ACTUAL_GROUP_COST_AWAITS_ROOT_RUN**.

This contract specifies one executable upper-bound construction for all 112 rows of one source map `q^-1 W_s` on eight arbitrary whole-field sources. It is not another 35-class lower-bound test. The required result is an emitted literal program, its exact paid/ordinary/owned bill, and certificates for every source row. The actual cost is the sum of the rational row ranks within the complete exact left-monomial classes. It is not merely the number of classes.

The construction builder owns `lanes/construction/coset-fanout/`. Root alone executes the bounded checker. This adviser has performed no classifier, matrix-rank census, scientific execution, pricing, feed lookup or new delegation. No numerical grouped-query count is claimed here. A direct per-row construction already supplies the conservative upper bound of at most112 H1 calls; the grouped program must demonstrate any improvement over it.

## One frozen source and interface

Use the #5402 source at `3348fccea855082786d5f0fc5558b73d4974e745` and these files, relative to the shared project root:

| Source | SHA256 |
|---|---|
| `swarm-provider-audit-sol-high-20261024/repository/research/coded-native-caller/NORMALIZERS.json` | `ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da` |
| `swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/PROVIDER.json` | `676de7551d3364598f4a7e29ae97cae0e4364348786bbe70435b84294ba7dd65` |
| `swarm-provider-audit-sol-high-20261024/repository/research/native-rank8-helper-provider/PROOF.md` | `2d59282f3b5e9fb848d0099ce91729fa433162e6975f877a441e2ab4f57a29c5` |

Extract the complete `Kp_p` word from `NORMALIZERS.ports[p].K_word`, for p=0..111. Set `M[p,j]=NORMALIZERS.mode_columns[j][p]`, for j=0..7; the stored matrix is transposed relative to the displayed W formula. Extract the eight exact Km words from the provider's `mode_boundaries[j].input_K`, binding each mode index explicitly. The source's boundary factor2 must NOT be included in Km here. The exact map being implemented is

```text
W_p h = Kp_p^-1 sum_j M[p,j] Km_j h_j / 2,
(q^-1 W h)_p = A_p sum_j M[p,j] b_j / 2,
A_p = q^-1 Kp_p^-1,
b_j = Km_j h_j.
```

The single emitted interface is the shear

```text
y_p <- y_p + (q^-1 W_s h)_p,    p=0..111,
h_j unchanged at EVERY instruction, j=0..7.
```

All y and h fields are arbitrary independent original fields. They are disjoint from each other and from17 declared owned fields. The owned fields have arbitrary entry dirt and must all return zero. This creates no productive input or target from scratch. A caller asking for `q^-1 W_s q h` must separately supply and charge the actual qh version; this contract does not grant eight input queries for free.

The one-column classification dimension is9. Its stage embedding into the common25-axis ABI maps the central coordinate to axis0 and the other eight coordinates to the chosen stage's eight fresh axes, with identity action on all other axes. The exact embedding must be emitted and bound. No 2^25 dense matrix is required.

## Exact left-monomial classes

Use

```text
p ~ r  iff  L_p,r := A_p A_r^-1
                 = q^-1 Kp_p^-1 Kp_r q
                 is a computational-basis monomial operator.
```

This is LEFT equivalence: a valid alias satisfies `A_p = L_p,r A_r`. A right alias would require a different input-program factorization and is not licensed here.

Represent a Pauli as `i^phase X^x Z^z`, including its phase modulo4. Obtain each A_p's signed Clifford tableau from the literal source words. Let Z0 denote the nine-dimensional diagonal Pauli subspace `{(0,z)}`. With S_A the binary symplectic action of conjugation by A, the deterministic class key is

```text
canonical binary RREF basis of S_Ap^-1 Z0.
```

The key is a nine-plane in18 binary coordinates. Equal keys are equivalent to `S_Ap S_Ar^-1` preserving Z0, hence to `A_p A_r^-1` being monomial. Indeed a unitary preserving the diagonal Pauli algebra sends its simultaneous one-dimensional eigenspaces to each other, so it permutes computational basis vectors up to phases. Conversely every computational-basis monomial preserves that algebra. Signs do not affect class membership, but they do affect the required emitted alias.

This proves a complete classifier, not merely a necessary central-image test. The earlier 35 distinct central images may be retained as an optional sanity witness; they must not replace the full112-row classification or the rank calculation. Every source port must occur in exactly one class. Use a deterministic representative, such as the smallest port index in each class.

For each p in the class of representative r, compile L_p,r into a literal source-compatible monomial word. One canonical chronological form is

```text
D(Q,alpha); P(G); X(b); phase(gamma).
```

The displayed chronological word represents `i^gamma X_b P_G D(Q,alpha)`. Emit G, b, the symmetric quadratic data Q, linear Z4 coefficients alpha, and the exact global phase gamma. Validate all source parity/invertibility constraints and the full signed tableau. Equality merely up to global phase is a rejection.

The monomial predicate is equivalent to every image of Z_j having zero X part; its Hermitian phase must then be even. That predicate alone does not provide the alias's absolute phase. A matching complete signed tableau plus one exact nonzero state-column anchor proves full operator equality, since two operators with identical Pauli conjugation differ by a scalar. Prefer the additional direct audit of ALL512 base computational columns for every accepted alias. The source-specific word `q^-1 Kp_p^-1 Kp_r q` has at most four terms per column, so this audit need not store a512-by512 dense matrix.

The required literal identities are `L_p,r = A_p A_r^-1` and therefore `L_p,r A_r = A_p`. Do not classify from `A_p|0>` alone. Here the inherited Kp words fix the zero address with phase0; many distinct A_p have exactly the same zero column, making that shortcut particularly unsafe.

## Scalar basis: integer certificates avoid new odd divisions

For one class C, let M_C be its m-by8 integer row matrix, retaining the original port ordering. Its rational rank is r_C<=min(m,8). The factor1/2 is kept outside this matrix and does not change its rank.

The preferred basis is an integer basis of the row lattice generated by M_C. An extended-gcd row-Hermite procedure can emit integer unimodular matrices U,V with

```text
U V = V U = I_m,
U M_C = [ H_C ; 0 ],
H_C = S_C M_C,       S_C = first r_C rows of U,
M_C = T_C H_C,       T_C = first r_C columns of V.
```

Require H_C to have r_C independent rows and verify r_C against exact rational rank. Verify all displayed integer equalities independently of the basis-generation procedure. This guarantees both that the queries span precisely the required row space and that all recovery coefficients T_C are integers. No runtime Hermite algorithm or division by a pivot is part of the emitted field program.

For each basis row l, form the whole-field input

```text
u_l = sum_j H_C[l,j] b_j.
```

Apply A_r once to each u_l. Then reconstruct port p in C using

```text
(q^-1 W h)_p
 = L_p,r sum_l (T_C[p,l]/2) A_r u_l.
```

This is a constructive program with exactly r_C H1 calls for that class. It does not pack several independent fields into one query: r_C independent scalar forms receive r_C separate calls.

An original-row basis with rational recovery weights would also give a formal algebraic factorization, but any odd denominators would require a newly implemented and charged arithmetic contract. The frozen construction should use the integer certificate above, whose runtime coefficients are integers for input preparation and integer halves for recovery. Do not silently introduce DIV3, DIV7, DIV13 or an expanded source grid. Exact Fraction arithmetic used by the checker is not a runtime field operation.

Coefficient growth matters. Emit the complete H and T matrices, maximum integer bit lengths, and a cap on the fully lowered instruction count. Exceeding the cap is a reported construction/resource failure, not permission to truncate, omit large coefficients, widen a search or claim a completed program. The source permits a fixed finite ordinary program; it does not make large coefficients or precision growth free.

## One explicit owned-field schedule

The agreed copy variant uses17 reusable owned fields:

```text
b0..b7       eight common normalized-input copies,
t0..t7       up to eight queried basis fields for one class,
z            one port-reconstruction field.
```

All17 receive entry CLEAR and zero-retag before use. They are disjoint from originals and every live caller cache or helper bank. At entry COPY h_j into zero b_j and apply the exact Km_j word. h is never normalized in place.

Process classes sequentially. For a class of rank r_C:

1. Form each u_l in zero t_l using repeated unit ADDs with sign from H_C[l,j], reading the unchanged b_j. This is an explicit lowering of integer coefficients, not an uncharged arbitrary-scalar operation.
2. Apply the literal inverse Kp_r word to t_l, then one positive central Q child, then the phase-zero central X word implementing q². The resulting array is exactly `q^-1 Kp_r^-1 u_l`. The last X is ordinary but charged. No second paid child is used for the inverse.
3. For each nonzero row p in the class, form `z=sum_l (T_C[p,l]/2)t_l` using repeated signed half-ADDs. Apply the exact phase-bearing L_p,r word to z. Execute the unit ADD `y_p += z`. CLEAR and zero-retag z after this read.
4. After every port in that class has read the queried basis, CLEAR and zero-retag t0..t(r_C-1). Their next class use starts from actual zero. The unused t fields stay zero.

After the last class, CLEAR and zero-retag all eight b fields. Every original h is unchanged, each original y has received its prescribed row once, and all17 arbitrary owned directions are zero at exit. Zero source rows require no target update. No live nonzero field receives a zero-retag.

The program is a pure source fanout, so y updates cannot change later queries: all query inputs depend only on the read-only h copies. An actual caller must bind the physical h version, y destination version, source/owned IDs and lifetime placement before using this component. This note does not borrow the17 fields from occupied source scratch.

## Exact bill to emit

Let

```text
C = sum_C r_C,
N = number of nonzero source rows M[p,:],
H_abs = sum_C sum_l,j |H_C[l,j]|,
T_abs = sum_C sum_p,l |T_C[p,l]|.
```

For the fixed schedule above, using one record per whole-field monomial word and retaining identity aliases as explicit records if present:

| Item | Exact count |
|---|---:|
| Paid positive H1 | C |
| Ordinary inverse-Q central-X maps | C |
| Km input monomial maps | 8 |
| Kp representative inverse monomial maps | C |
| Left alias monomial maps | N |
| Owned COPY | 8 |
| Unit ADDs for query preparation | H_abs |
| Half-ADDs for recovery | T_abs |
| Unit ADDs into original targets | N |
| CLEAR | 25+C+N |
| Zero-retag | 25+C+N |
| Peak additional owned fields | 17 |

The CLEAR count is17 at entry, C queried-field returns, N reconstruction-field returns, and8 normalized-input returns. Emit primitive monomial gate counts separately from whole-field map counts, and retain every phase word. If the emitter omits proven identity maps, report the actual reduced bill with that exact omission policy; do not mix its count with the conservative table.

At a fixed whole-field capacity, the emitted Gaussian upper bound is C. Since r_C is at most the number of nonzero rows in its class, C<=N<=112. Singleton classes with H=M[p,:] and recovery1 supply the conservative direct program independently of any sharing claim. The actual root result must print the full class sizes/ranks, C, H_abs, T_abs, maximum coefficient size, and the literal program's independently recounted bill. A class count by itself is insufficient.

This is an upper construction and the exact bill of this program. It is not a lower bound for layered query circuits, operator-valued cross-class cancellation, changed source versions, cached paid values or a different complete caller. The old three-call34/42.5 moment allowances are not applied here. Any global120 termination budget and actual occurrence multipliers belong to a later complete invoice.

## All-width proof, including absolute phases

At one source column, the positive Q gate is

```text
q|x> = ((1+i)/2)|x> + ((1-i)/2)|x xor e0>,
q^-1|x> = ((1-i)/2)|x> + ((1+i)/2)|x xor e0>.
```

These formulas are permitted for the finite one-column classifier and its sparse exact column checks. They are NOT a whole-field two-term implementation for arbitrary fiber width f. The physical `q_f^-1` is the columnwise tensor product of the one-column gate and has2^f support per central row. One positive paid Q_f followed by the columnwise X_f implements it because `q_f²=X_f`.

The source proof §5 fixes the lift: P and X act columnwise, D sums its Z4 polynomial over columns, and a phase gate gamma contributes `i^(f gamma)`. Consequently an alias identity `A_p=L_p,r A_r` checked as an exact9-axis one-column operator lifts, after the declared stage embedding and spectator identities, to

```text
A_p,f = L_p,r,f A_r,f
```

for every positive f. Its absolute phase is part of L_p,r,f. It must not be replaced by an exterior scalar `i^gamma`, nor folded into a rational recovery coefficient. In particular a source phase2 is `(-1)^f`, whereas an ordinary negative ADD coefficient is the exterior scalar -1 applied once.

The finite owner matrices H_C, T_C and M_C and the scalar1/2 remain OUTSIDE the tensor product. For arbitrary whole-field inputs,

```text
L_p,r,f sum_l (T_C[p,l]/2) A_r,f (sum_j H_C[l,j] b_j)
 = sum_j ((T_C H_C)[p,j]/2) L_p,r,f A_r,f b_j
 = A_p,f sum_j (M[p,j]/2) Km_j,f h_j.
```

This is the uniform lift proof. It uses linearity of the whole-field operators after each individual operator identity has been lifted; it does not tensor a scalar sum, raise a source coefficient to f, or expand q into two whole-field monomials. Inactive axes are identity factors, so the same proof holds on arbitrary25-axis fields without a dense25-axis evaluation.

## Required bounded checker output and controls

The builder should freeze the checker, input manifest and deterministic emission policy before root's one run, with the agreed30-second/256-MiB cap. It must not import or run the source author evaluator. Static source parsing, a fresh exact signed-tableau/column implementation, integer/Fraction matrix certificates and a literal owner-lifetime counter suffice.

The output must contain all112 source row IDs; every class key and representative; each member's exact L word, signed tableau and absolute phase/full-column receipt; M_C,H_C,S_C,T_C and U,V certificates; all basis preparation and per-port recovery records; the source/stage hashes; the complete literal shear program; exact paid/ordinary/owned counts; and the all-width scope above. It must retain arbitrary original y/h columns and arbitrary owned entry directions, with strict source read-only and complete owned zero return. No result may depend on dropping a source row with an inconvenient phase or coefficient.

Required negative controls include: grouping from one impulse only; a nonmonomial pair incorrectly merged; reversed left/right alias order; altered alias absolute phase despite unchanged tableau; wrong Kp inverse or Q sign; omitted inverse-Q X; a dropped or transposed M coefficient; altered basis/recovery coefficient; tensoring an exterior1/2; treating a per-column phase as an exterior scalar; omitted dirty-entry CLEAR; writing an original h; and premature query-field CLEAR. A small f=2 witness distinguishes the illegal two-term whole-field Q shortcut and exterior/columnwise scalar confusion without constructing a2^25 matrix.

Only a root-executed complete PASS can establish the actual grouped upper count and program component. It will still not establish source precision/tape realization, caller storage compatibility, a full decoder, funding or a new kappa. Source notices and predecessor credit remain inherited; this contract adds only the explicit grouping, integer-basis realization and resource certificate requirements.
