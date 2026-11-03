# A native warp, child and ADD at one emitted boundary

## Result and source

This is an enabling local proof with an exact finite certificate. It closes
one forward interface in [JoyboyBrian's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19234842).
It does not close the global native integration question in
[PR #4424](https://github.com/CrocSwap/integer-mult-bounds/pull/4424).
There is no new complete kappa, selected assumption discharge or frontier change.

The historical supplier is [PR #4088](https://github.com/CrocSwap/integer-mult-bounds/pull/4088),
head `72d7efc181edb21806a878f174847c96dd410ab0`. Its source bytes here are
pinned to canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a` in
[SOURCES.json](SOURCES.json). The [source phase receipt](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/staged544-mixed-fourth-entry/evidence/NATIVE-PHASES-base.json)
separates local recipe checks from scalar-interface and global composition.
The [cover audit](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/complex-cover-lift-audit/README.md)
already establishes the native warp class and formal lift. Those results
are credited inputs, not new claims here.

Run the unchanged `bw_emit.py` on the retained canonical base word. The
forward stream has 22,808 events and SHA256
`6a084558a9c99578d8fa3e0276af52032f207737d25362b039ac9ca1a1364532`.
This equals the retained `NATIVE-LOCAL-base.json` digest. Events at zero-based
positions 6683, 6684 and 6685 are exactly:

```text
['warp', ['L', 83], 52, 85, 137]
['climb', 'A', 126, 0, 137, 1]
['scalar', ['add', ['L', 126], ['L', 83], -1, 2], 137]
```

Frame 0 is empty, frame 85 is spanned by binary vector 382, and frame 137
is spanned by vector 45. The nine columns of operator 52 are
`[1,2,4,16,392,128,162,68,401]`. Use the frame pair in the emitted event.
The canonical operator definition has a different frame pair; its stored
pair must not replace the actual caller's frames.

## Local identity

Let T_U be the source's canonical frame operator for U. Let K be the source's
phase-corrected operator 52. Set A = T_85 and B = T_137. All operators act
on 512 complex coordinates. The physical warp is W = B K A^-1. The target
climb is B, since T_0 = I. For arbitrary source and target values s and t,
the input banks are (A s, t). The three events give

```text
(A s, t) -> (B K s, t) -> (B K s, B t)
         -> (B K s, B (t - K s / 2)).
```

The last equality needs the target climb: scalar addition commutes with a
common linear frame, but it cannot mix two different frames. Thus the
emitted boundary realizes the logical reference change s -> K s followed
by t -> t - s/2, with both physical banks in frame 137.

The source compiler factors W as one rank-zero monomial. It factors B as
L C R with rank one, where C acts on the first binary coordinate. The full
serialized recipes, including constant phases, are in [RESULT.json](RESULT.json).
`produce.py` uses the unchanged `lower_child` compiler. It does not invent
or assume the recipes. The separate `bw_gauss.py` coordinate implementation
builds A, B K and B directly from the canonical frames and G columns.
`verify.py` decodes only the serialized recipes with a new exact interpreter.
It compares all 1,024 input columns of both banks with these independent
coordinate matrices. This proves the finite linear identity over complex
numbers, subject to correctness of the executable integer checks; no random
or projective equality is used.

The inverse first applies target += source/2. It then applies B^-1 to the
target and W^-1 to the source. In each serialized child, this reverses the
order of the two monomials and conjugates the coordinate transform and all
phases. The result is exactly (A s, t), including arbitrary dirty values.
This literal inverse is not the source program's backward/inverse-transpose
orientation. That distinct orientation is not checked here.

## Tensor statement

For each positive integer f, set A_f = A^(tensor f), B_f = B^(tensor f),
and K_f = K^(tensor f). Tensor multiplication gives
W^(tensor f) = B_f K_f A_f^-1. The same three-step proof gives

```text
(A_f s, t) -> (B_f K_f s, B_f (t - K_f s / 2)).
```

Here s and t are arbitrary vectors of dimension 512^f; they need not be
pure tensors. This follows from equality of the factor operators and
linearity. It is not obtained by taking the tensor power of the complete
two-bank ADD matrix. The ADD coefficient stays -1/2; it does not become
(-1/2)^f. A monomial constant phase i^p becomes i^(f p), and its coordinate
phase is the sum of the f phase forms modulo four. The retained recipes
have constant phase zero; the controls change it by one to detect a
checker that accepts equality only up to a global phase.

The tensor statement is a local algebraic identity. It does not supply
an accelerated child, physical tape implementation or precision theorem.

## Operation account and verification limits

At f = 1 the forward boundary uses three serialized monomial passes,
one rank-one child (256 C butterflies), and one complex vector ADD with
coefficient -1/2 (1,024 real scaled additions). The literal inverse has the
same macro counts. The compiler is used only to generate the fixed recipes.
Dense matrix preparation and all-column checking are verification work.
They are not part of a claimed multiplication algorithm.

For f > 0, let N = 512^f. The direct interpretation has three monomial
passes, f N/2 coordinate butterflies, and 2N real scaled additions. Each
monomial address and phase evaluation uses O(9f) operations per entry.
Thus direct work is O(fN), with O(N) complex storage in an implementation
that uses separate input and output arrays. These are arithmetic and
address-operation counts, not bit-operation, rounded-integer, in-place
storage or physical-tape tariffs. The new checker uses arbitrary-size
integer numerators. No machine-word bound is assumed for dirty inputs.
The old matrix oracle has only two rank-one frame factors at most; all
its integer intermediates are bounded by four, far below int64 overflow.

Normal and optimized runs use explicit rejection checks in the new verifier.
The predecessor files require assertions. They run unchanged in a separate
normal Python process in both modes; their guards are never removed.
The exact NumPy pin is `numpy==2.3.4`.

All 1,024 columns pass the endpoint and inverse tests. Four fully nonzero
complex dirty pairs with integers wider than 64 bits pass independently
formed expected outputs and restoration. Eight controls reject omitted
warp, omitted child, reversed child, ADD before the child, wrong ADD sign,
and a changed constant phase in each of the three monomials. All six
changed source files fail authentication. These controls are parts of one
result, not separate contributions.

The source emitter also performs its inherited free-word checks for both
streams. This package authenticates the forward stream and joins only the
three listed events numerically. It does not join all 22,808 events, rerun
all native phases or residual adapters, prove the centre/endpoint invariant,
admit the historical supplier, rerun the selected supplier or change its
five open framework assumptions. Independent human and proof-kernel review
have not occurred. The next distinct obligation is an emitted centre or
residual-wrapper boundary, followed by a complete global invariant.

## Attribution

Cinna Davis / @1337isnot1337 supplied the historical PR4088 construction
and the borrowed-reference operators from
[PR #2226](https://github.com/CrocSwap/integer-mult-bounds/pull/2226).
The [retained borrowing notice](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/staged544-mixed-fourth-entry/native/vendor/native/new/code/borrow/NOTICE-PR2226.md)
credits icekylinx for scalar and wrapper machinery, DreamingOfClouds for
hyperplane and cold-helper extensions, and the vendor531 exact Clifford
compiler. The emitter and `bw_adapters.py` retain those original notices.
The [native lineage](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/staged544-mixed-fourth-entry/native/NATIVE-LINEAGE-NOTICE)
retains Rohan Arun, Tekalign and the earlier contributors. The
[PR4088 notice](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/staged544-mixed-fourth-entry/NOTICE.md)
retains the supplier, frame, owner and audit lineage. Mark / @Matarener
supplied PR4424's audit; JoyboyBrian / @JoyboyBrian supplied the released
handoff. The byte-exact sources and their licenses remain unchanged.
Prepared by Ali Romman with substantial OpenAI Codex assistance. New work
is Apache-2.0. The contribution is this specific emitted interface join,
its independent exact interpreter and controls, not the predecessor
compiler, warp theorem, tensor-lift principle or supplier construction.
