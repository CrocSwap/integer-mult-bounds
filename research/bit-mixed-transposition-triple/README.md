# A heterogeneous three-target word needs five coordinate-CNOT calls

**Scoped exact minimum; no new κ.** In the formal model below, the target

```text
diag([a], [b], [s])  in  M_3(F2[GL_2(F2)]),    s = aba = bab
```

requires exactly five paid calls when the only paid address labels are the two
coordinate CNOTs `a` and `b`. The direct word costs `1 + 1 + 3 = 5`. An exact
radius-four search finds no shorter word, even after arbitrary free scalar
`GL_3(F2)` mixing. All three registers may start with arbitrary data. The
endpoint is checked as a full formal group-algebra matrix, so no dirty data can
leak between registers.

This is a new target distribution inside the known coordinate-CNOT model: one
copy of each of its three noncommuting involutions, rather than repeated
coordinate swaps. It does not improve the selected multiplication bound and
does not establish the cost for extra registers.

## Exact model and cost

Let `G = GL_2(F2)`, represented by its six permutations of the three nonzero
binary vectors. Set

```text
a = [[1,1],[0,1]],   b = [[1,0],[1,1]],   s = [[0,1],[1,0]] = aba.
```

The register algebra is the formal group algebra `F2[G]`, not a matrix image of
that algebra. A paid unit is

```text
D_N(g) = I + ([g] + 1) N,     g in {a,b},     N = u v^T,
```

where `u,v` are nonzero binary three-vectors and `v^T u = 1`. There are 28
distinct rank-one idempotents `N`, hence 56 paid generators. Each call costs
one, including repetitions. Free scalar basis changes from `GL_3(F2)` are
allowed as an optimistic relaxation. All three registers are counted; there
are no clean registers or omitted restoration events.

The endpoint is the exact diagonal matrix with entries `[a]`, `[b]`, `[s]`.
It acts correctly on arbitrary values in every register, and every off-diagonal
coefficient must be zero. Applying augmentation `[g] -> 1` sends the endpoint
and every paid unit to the identity. Therefore any trailing free scalar map in
a word must be the identity. Moving intermediate scalar maps through paid
units conjugates `N`; conjugation preserves the rank-one idempotent inventory.
Thus the 56 generators enumerate every normalized word in the stated model.

## Complete exclusion through four calls

Each paid generator is an involution: for `x=[g]+1`, `x^2=0` because `g^2=1`
and the algebra has characteristic two; also `N^2=N`. Therefore every word of
length at most four splits as `U V` with each part of length at most two. If
the target were `U V`, then `V=U^{-1}T`. The verifier enumerates every distinct
formal state in the radius-two ball and checks whether `U^{-1}T` is also in
that ball.

The exact layer sizes are `1, 56, 1750`, for 1,807 states total. The
inverse-target intersection is empty. A separate five-call word applies `a`
to register 1, `b` to register 2, and `a,b,a` to register 3; exact formal
replay gives the target. These two facts establish the minimum of five for
exactly three registers.

The full receipt is [EXPECTED.json](EXPECTED.json). The verifier rebuilds the
ball from its 56 generators, records a SHA256 digest of every formal state, and
checks the direct word, all five call omissions, a wrong label, a wrong target,
an off-diagonal dirty leak, all 28 idempotents and all 56 generator inverses.
It does not accept finite address-matrix equality as a substitute for the
formal algebra identity.

## Reproduce

Python 3.12 or later; standard library only. From the repository root:

```sh
python3 -I -B research/bit-mixed-transposition-triple/verify.py
python3 scripts/research_package.py --package research/bit-mixed-transposition-triple --check-only
python3.12 scripts/research_package.py --package research/bit-mixed-transposition-triple
```

Expected verifier line:

```text
PASS_BIT_MIXED_TRANSPOSITION_TRIPLE minimum=5 ball=1807 hits=0 omission_controls=5 negative_controls=3 involutions=56 no_new_kappa
```

## Cost boundary and limitations

The complete local paid bill is five rank-one address calls. No source reads,
copy/erase operations, frame changes, hosting or precision events appear in
this abstract word. Scalar `GL_3(F2)` mixing is granted for free by the model;
the word and radius-four exclusion cover every such mixing after augmentation
normalization. The possible improvement tested here was one call (`5 -> 4`) on
this one target triple. It was not realized. No embedding into the selected
bit supplier, repeated occurrence count, complete recursive moment or outer
transfer was established, so there is no κ claim.

The result is fixed to exactly three registers, the address group `GL_2(F2)`,
and paid labels `{a,b}`. It does not extend to extra dirty registers, other
paid labels, a different field or a physical supplier. The broader affine
rank-floor argument in PR1333 and the identical-SWAP results in PR1414/1491
are related predecessors; the different target and exact heads are recorded
in [OVERLAP.json](OVERLAP.json).

## Open next questions

What is the exact minimum for the same heterogeneous target after adding a
restored dirty register? A lower cost would identify a genuine register-count
effect absent from this fixed three-register result. The first step is an
exact `r=4` search reduced by augmentation and sign constraints. The
rank-one-idempotent inventory grows quickly, and the active four-SWAP claim is
a different target that needs separate coordination.

## Credit

Predecessor model and group-algebra techniques are credited to Gareth Davidson
(PR1333), commdata2338 (PR1414/1491), and the contributors to the retained
register-model lineage. Prepared by Cinna Davis (@1337isnot1337), with
substantial OpenAI Codex assistance in the exact search, verifier, proof
explanation and package. No independent human proof review is claimed. New
work is Apache-2.0.
