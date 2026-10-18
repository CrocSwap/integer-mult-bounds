# A mixed affine target triple needs six calls in a restricted label alphabet

**Seed:** `818dbf90f2581f79a4e4150cdd77e415`

**Track/task:** `bit-mechanisms` / `bit-new-register-model`

**Priority revision:** 3

**Base:** `0b1cccf86e2f5132ed286a26ef0a681a495740ea`

**Selected-record SHA256:** `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`

## Result

In the exact three-register formal model below, the target

\[
  \operatorname{diag}([a],[b],[h]),\qquad h=a b a t_x,
\]

has paid-call cost **six**, even when arbitrary free binary changes of register
basis are allowed. A complete radius-three search found no representation with
five or fewer paid calls. The direct six-call word is

```text
D_(e0 e0^T)(a), D_(e1 e1^T)(b),
D_(e2 e2^T)(a), D_(e2 e2^T)(b),
D_(e2 e2^T)(a), D_(e2 e2^T)(t_x)
```

The target-specific homogeneous displacement-rank lower bound is four:
`rho(a)=rho(b)=1`, while `h(x0,x1)=(x1,x0+1)` has `rho(h)=2`. Thus the
experiment closes a two-call gap for this fixed label set. It is a scoped
negative result about register mixing, not a new general affine theorem, a
supplier construction, or a new conditional multiplication bound.

## Exact model and complete charge

Let `G = AGL_2(F2)` and `R = F2[G]` be the formal, noncommutative group
algebra. Group elements act on all four points of `F2^2`; multiplication is
composition with the rightmost map acting first. A register state is a
`3 x 3` matrix over `R`, so equality means equality of every formal group
algebra coefficient. This is the arbitrary-dirty-input contract: no register
is assumed zero, copied clean, or discarded.

The source labels are exactly

```text
a(x0,x1)   = (x0+x1,x1)
b(x0,x1)   = (x0,x0+x1)
t_x(x0,x1) = (x0+1,x1)
```

Each occurrence of

\[
D_N(g)=I+([g]-1)N,\qquad N=uv^T,\quad u,v\ne0,\quad v^Tu=1,
\]

costs one paid call. There are exactly 28 binary rank-one idempotents `N`
and three labels, hence 84 paid generators. All three labels are involutions,
so each paid generator is its own inverse.

Arbitrary `B in GL_3(F2)` scalar mixing is free. It does not enlarge the
normalized paid alphabet: move each `B` through the paid calls, conjugating
each `N` to another rank-one idempotent; all 28 are already included. The
augmentation `[g] -> 1` sends each paid call and the required target to the
identity, so the total scalar map in a successful word must be `I`. This is
the same normalization principle proved in the pinned
[binary affine register bound](../binary-affine-register-bound/PROOF.md).

For the optimistic charge screen, the direct bill is six calls. The
homogeneous displacement rank gives the lower bound four because
`[A-I | b]` has rank one for `a,b` and rank two for `h`. Every paid call has
rank-one displacement in this representation. The full rank-one affine-label
alphabet has a general theorem in the pinned predecessor; this experiment
restricts the available paid address labels to `{a,b,t_x}` and asks whether
dirty-register mixing can still reduce the direct bill to five. Extra address
labels, precision, hosting, frame conversion, source access, and supplier
interfaces are outside this finite model, so the answer does not translate to
the selected `kappa`.

## Exhaustive evidence

`verify.py` stores each of the nine matrix entries as a 24-bit coefficient
vector, one bit for each element of `AGL_2(F2)`. It performs a breadth-first
search of the complete right-multiplication ball through radius three, then
checks every canonical prefix through radius two against the radius-three
ball. A word of length at most five must split into such a prefix and suffix.
For prefix `U` and target `T`, the join checks whether `U^-1 T` lies in the
right ball. The prefix gates are applied by left multiplication in forward
word order, which yields `U^-1 T` because each gate is involutive.

The completed layers contain `1, 84, 4,697, 232,720` distinct formal states.
All `4,782` joins were checked and none hit the target. Since the explicit
six-call word replays to `T`, the minimum in this stated paid alphabet is
exactly six. The search does not quotient by a point-action representation;
it retains all 24 formal basis coefficients.

Controls also check all 84 generator matrices and involutions, compare three
products with an independent dense group-algebra matrix multiplier, remove
each direct call in turn, and reject a wrong affine label and wrong target.
`EXPECTED.json` records deterministic breadth-first layer digests as well as
the state counts and control totals.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py \
  --package research/bit-affine-mixed-target-triple-seed818dbf
```

Expected marker:

```text
PASS_BIT_AFFINE_MIXED_TARGET_TRIPLE group=24 generators=84 layers=1,84,4697,232720 probes=4782 minimum=6 hit=False
PASS_REGISTERED_RESEARCH_PACKAGE research/bit-affine-mixed-target-triple-seed818dbf outcome=negative-result
```

Source commits, Git blobs, and SHA256 pins for the selected record, task
catalogue, and predecessor results are in [SOURCES.json](SOURCES.json).
The selected record was used only as the current frontier/provenance pin; it
was not changed.

## Overlap and attribution

The final refresh covered all 403 open PRs and a repository-scoped `AGL2`
Discussion search, which returned only #1317. The most recent complete
paginated discussion snapshot had 351 records at 07:28 UTC; a later helper
refresh hit GitHub's GraphQL rate limit, so I cross-checked the current
rendered thread and repository search page. Open PR #1711 studies two-register
endpoints `diag([h],[h])` and
`diag([h],[h^-1])` with the four-label alphabet `{a,b,t_x,t_y}` (24
generators). This result instead uses exactly three registers, target tuple
`(a,b,h)`, and the restricted alphabet `{a,b,t_x}` (84 generators). The
adjacent claim for two identical `h` targets is the same two-register,
four-label scope as #1711. PR #1696 studies the related but linear target
`(a,b,aba)` in `GL_2(F2)`. The two-coordinate-swap packages and mixed-`GL_3`
target-pair work also change the target or address group. The exact claim and
its expiry are recorded in Discussion
[#1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18918291).

This package builds on the affine rank argument in
`research/binary-affine-register-bound/PROOF.md` and the coordinate CNOT
formal-register model in `research/coordinate-cnot-register-bound/PROOF.md`.
It does not claim either result as new. Prepared by Cinna Davis
(@1337isnot1337), with substantial OpenAI Codex assistance in the scoped
experiment design, verifier, exact-search implementation, and package draft.

## Open next questions

Can another three-label subset of the nine affine rank-one maps produce a
dirty-register compression for a mixed target triple? A bounded next step is
to enumerate those label subsets and select targets whose direct label-word
bill exceeds the homogeneous-rank lower bound. This cycle deliberately fixed
`{a,b,t_x}` and did not search other alphabets.
