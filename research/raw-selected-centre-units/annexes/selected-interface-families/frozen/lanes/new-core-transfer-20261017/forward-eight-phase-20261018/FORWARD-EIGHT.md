# A direct eight-port phase suffix

The signed eight-port balanced forward word has a useful exact suffix.
It changes the complete X output to `(Qh,k)`. It retains the physical
selected Y value `q d` on arbitrary local input `x=(h,k), y=(d,v)`.
The suffix does not require a clean d or a query from an earlier view.

The complete local word costs 92,784 real scalar primitives and has
native rank mass 5,081 in 3,515 children. Relative to the preceding word,
it adds 1,312 scalar primitives, eight rank-one children, and sixteen
pure-permutation wrappers. It uses no new owned or private field. The
same suffix on the raw forward word costs 89,088 at the same native
profile. The payload contains both words for both providers.

These are local invoices. The new child calls and wrappers remain in
the invoice. A global hosting schedule and the full supplier cost are
not established here.

## Exact map on arbitrary current data

Use the source partition `S=[0,7,15,36,42,46,79,89]` and its complement U.
Write the exact response as `J=[[L,B],[D,H]]`. Let Q be the diagonal
selected port operator, and let `q=Q^-1`. The input convention is
`X=diag(Q_p)x`, `Y=y`. Completed physical arrays have a common FULL
factor F; we remove that factor in the formulas below. The completed
logical Y convention includes a final multiplication by `diag(Q_p)`.

The preceding balanced forward word gives

```text
physical X_S = h + q(L q d + B k),
physical X_U = k,
physical Y_S = q d,
logical  Y_U = H(v+k) + D q d.
```

Apply positive Q_p directly to each current X_p with p in S. Then apply
the following scalar subtraction at the same completed view:

```text
X_S <- X_S - L Y_S - B X_U.
```

Every source in this subtraction is current physical data. The first
step cancels only the adjacent same-port product `Q_p q_p`. The result
of both steps is

```text
physical X_S = Q h,
physical X_U = k,
physical Y_S = q d,
logical  Y_U = H(v+k) + D q d.
```

In particular, d is arbitrary. The subtraction uses its actual physical
value `q d`, not d and not an assumed clean original-source value. No Q
operator is moved through L, B, D, or H. If the initial ordinary H gauge
is omitted, the same proof gives `Y_U=v+Hk+D q d`. This is the raw variant.

For an algebraic composition with the source-diagonal backward map,
the source coefficient of X is consequently `(b,-v)`: the selected
coefficient q b is multiplied by Q, and ordinary X is unchanged. This
statement concerns the displayed endpoint maps. It does not supply a
routed physical transition between two different calls.

## Exact direct live-field native lift

On a spatial array, write `T_v f(z)=f(z+v)` over the nine binary
coordinates. The actual positive intrinsic line is

`Q_v = ((1+i) I + (1-i) T_v)/2`.

All binary translations commute. FULL is the product of the nine
coordinate Q operators. Thus `Q_v F=F Q_v` exactly, including the phase.
This identity permits a direct application to a current completed X
field. If that array is Fw, the result is `F Q_v w`. There is no copy to
C0, no erase of a data-dependent field, and no unpriced field exchange.

Choose an invertible binary matrix G whose first column is the actual
port label v. Let P_G permute spatial positions by G. Then

`Q_v=P_G Q_e0 P_G^-1`.

The emitter stores both binary matrices, with zero translation, zero
quadratic and linear phase, and zero global phase. It emits the right
permutation first, one rank-one child, and the left permutation last.
All eight actual port labels are read from both canonical providers:

```text
port:   0   7   15   36   42   46   79   89
label: 11  21  265  146  322  140  502  445
```

The local child contract is the exact rank-one spatial operation on the
current target, with all other fields preserved. This is the same native
operation type used in the source. Each target is its selected live X
field at the completed view. The calls are serial. The emitted suffix
does not use any helper, private buffer, or owned field. It adds eight
child invocations; it does not claim that their recursive workspace or
global hosting is free. That caller obligation remains explicit.

The checker verifies all 512 spatial basis columns for each recipe. It
also checks the Pauli action and one exact Gaussian state for the FULL
commutation. The latter checks both the Clifford operator and its global
phase. The formulas above give the general proof. A negative-line
replacement fails the phase check even though its spatial support agrees.

## Literal scalar and native invoices

The selected response rows contain 160 nonzero half-coefficients. Of
these, sixteen are in L and 144 are in B. A complex half-coefficient ADD
costs ten real scalar primitives in the retained model. Thus the direct
subtraction costs 1,600. A smaller word scales each target by two,
subtracts its twenty signed unit sources, and scales it by one half.
The sources are selected Y and ordinary X, so the target changes do not
change any source. Each row costs `2+20*8+2=164`, for a total of 1,312.
The checker compares the two subtraction maps on all 640 columns.
No scalar preparation is needed by the pure permutation recipes.

The retained balanced word costs 91,472. The raw word costs 87,776.
Adding the scaled subtraction gives 92,784 and 89,088. Each native profile is

`2441 H1 + 724 H2 + 228 H3 + 102 H4 + 20 H5`.

Its rank mass is 5,081 and it has 3,515 children. The sixteen new
permutation wrappers are serialized in full; they are not included in
the scalar primitive subtotal. Their use in a global access and
descriptor schedule remains a separate supplier obligation.

## Verification and source credit

The signed source freeze is
`controller-followthrough-20261017/bipartite-eight-20261018/FREEZE.json`,
SHA-256 `c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1`.
The preceding physical-transfer freeze is
`new-core-transfer-20261017/bipartite-eight-transfer-20261018/FREEZE.json`,
SHA-256 `84b1156a0c58ced62ee5834a92d02147346032f7a8beb181b3efe35a539d86f1`.
The checker validates every artifact in both freezes. All old native
events are retained exactly. Their earlier orientation-specific phase
review is a pinned dependency; it is not repeated here.

For each of four complete words, the replay checks all 640 ordered
input columns, including arbitrary selected d, 408 arbitrary helpers,
eight arbitrary owned inputs, and all 91 private zero-buffer lifetimes.
Helpers return unchanged, private buffers return zero, and all owned
fields return zero. All boundary and core scalar frames are checked.
The free-operator replay permits only adjacent inverse cancellation, so
it cannot silently commute different port Q operators through J.

Three complete-boundary negative controls omit the positive line, use
the inverse line, or omit the scalar subtraction. Each control fails.
The eight spatial line-sign controls also fail as required.

Run with a new output directory:

```text
python3 work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/forward-eight-phase-20261018/emit_forward_eight.py --out-dir /tmp/forward-eight-normal
python3 -O work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/forward-eight-phase-20261018/emit_forward_eight.py --out-dir /tmp/forward-eight-optimized
```

Both runs must end with `PASS_DIRECT_SELECTED_EIGHT_PHASE_SUFFIX` and
decompressed payload hash
`f2369cd8928d3c6fe64ec87b18e5993db167ef362f326e173a752bbb8fe64de3`.
The normal and optimized payloads and receipts must be byte-identical.
The first direct-subtraction implementation and its two passing runs
are preserved under `emit_forward_eight_direct.py`, `run-normal`, and
`run-optimized`. Those words cost 93,072 and 89,376. The final scaled
implementation is stored under `scaled-normal` and `scaled-optimized`.
Independent review of this extension is a separate artifact.

The controller lane proposed this suffix and supplied the signed
response. The previous transfer supplied its physical boundary. The
native-recipe lane identified the direct-target and wrapper obligations.
The phase interpreter comes from the earlier independent native review.
The direct permutation lift is also the line mechanism used in prior
coherent-port work. This packet gives its current live-data binding and
the complete new replay. This is AI-assisted research.

Routed composition, global child hosting, exterior phase, recursive
precision, and the full supplier invoice remain open. No complete kappa
claim follows. Do not create a PR, commit, or push. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
