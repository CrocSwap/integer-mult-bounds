# Cross-block mixing at the twelve frozen late interfaces

The source is the selected PR1094 local word, retained in the PR1042 replay
archive. Ali Romman's PR1429 proves a moment minimum separately for twelve
eight-helper blocks and explicitly excludes communication between blocks.
This note removes that exclusion for the **joint fixed late interface** below.
It uses PR1429's carrier-count and retirement arguments, adding global
localization and a simultaneous boundary. It does not claim a new supplier.

## Statement and exact scope

Let `0 < s < 1`. A frame growth of rank `d` costs `d^s`. At the joint
interface, there are 96 helpers, 96 independent read-only input values,
and 48 additive output ports, all of the retained equal array volume.
The helpers are those in the twelve blocks with bases

```
592, 600, 608, 624, 632, 640, 648, 656, 672, 680, 688, 696.
```

Block `j` has four initial helpers at its common frame `U_j`, of rank
`u_j = 4` or `5`, and four initially at rank one. Write their independent
initial values as `x_j` and `y_j`. Input `z_ji` is available at its fixed
frame `F_ji`, of rank five or six. The required four-port increment is
`R_j y_j + Q_j z_j`, with no `x_j` response. The matrices and every frame
are extracted from the word, rather than stipulated from an aggregate bill.
Each output has the retained late entry frame `G_t` and final hyperplane
`H_t`. Every helper must end at the full rank-nine frame with its dirty
information retained. We relax its endpoint to any invertible helper map.

Allow any finite rational ADD/SCALE program on **all 96 helpers**, including
cross-block mixing, arbitrary order, arbitrary nonzero scaling, repeated
reads of a fixed input port, repeated additive writes to the output ports,
and assignment of an input to a helper from a different original block.
Input reads add into helpers; output writes add from helpers into targets.
Every interaction requires a common frame in F2^9; frames only grow by inclusion.
All helper growth, including completion to rank nine, is charged.

There are no extra arrays, frame descents, writable input ports, target
scratch, additional later versions of an input port, earlier target access,
changed centre paths, or changes to the exterior program. In particular,
the physical input arrays undergo later exterior updates; granting repeated
access to their **fixed early values** is a relaxation of this port interface,
not permission to read their later updated values as additional inputs.
This distinction is material.

**Theorem.** Every such joint replacement has helper-growth cost at least

```
328 + 56*2^s + 28*3^s + 20*4^s.
```

The retained twelve blocks attain equality. Thus arbitrary cross-block
coding cannot improve this cost with the declared interfaces. This is an
all-length written argument; the executable checks establish its finite
source premises. It is not a proof-assistant theorem or a global circuit
lower bound.

## 1. One genuine joint boundary

The earliest retained correction starts at zero-based B index 283. All
96 helpers already have their stated initial frames there. From each
block's correction start until its input segment, only that block's own
helper-only correction touches its helpers. The 144 correction ADDs
therefore commute past all intervening exterior operations and can be
deferred to immediately before B index 1054, the first selected input.
No input value or helper value is copied for this rearrangement.

At index 1054, all 96 distinct input arrays are already at their stated
frames. None changes before its own input segment. The 96 helper arrays
are distinct from these inputs and from the 48 targets. Removing the
corrections leaves a prefix of 4537 scalar operations on the 704 main
arrays. Every ADD has distinct source and destination, and every SCALE
is nonzero. The copied-centre contribution here is its retained main-array
shear. This prefix is invertible; its determinant is the checked nonzero
product of SCALE factors. Hence any 192 distinct coordinates at this
boundary are independent under the retained arbitrary-main-input contract.

As a separate check, `independent.py` executes the prefix over each of
the primes 65521 and 65537 and exhibits 192 pivot columns. All rational
denominators are invertible modulo each prime. Either nonzero minor alone
certifies rational independence; these are exact witnesses, not a
probabilistic rank estimate. Duplicate-coordinate and singular-prefix
controls reduce the witnessed rank to 191.

Allowing all fixed inputs from the outset and all targets at their late
entry frames removes timing restrictions and only enlarges the replacement
class. The theorem can therefore use this common abstract boundary. It
does not silently assume asynchronous values to be independent.

## 2. Checked local and global premises

For every block, `Q_j` has rank four and each of its eight columns has
exactly two nonzero entries at distinct output ports. For every set `S`
of at most four input coordinates,

```
rank(projection_S ker(Q_j))
    = |S| - 4 + rank(Q_j on the complementary columns)
    >= ceil(3|S|/4).
```

All 255 nonempty supports per block are checked. A nonzero local kernel
vector cannot have input-frame union of rank at most six. There are
exactly 24 distinct rank-seven kernel frames, twelve each in blocks
592 and 696; these are all such frames, not sampled examples.

The new global checks establish:

1. The 96 input frames form an antichain: none contains another.
2. `U_j` is contained in no input frame of another block (1056 tests).
3. The 48 target caps are distinct, and every input frame joined with
   every target entry frame has rank at least eight (4608 tests).
4. Each rank-seven kernel frame contains input frames from its own block
   only, all of rank five, and is contained in at most one of the **48**
   target caps. Previously the corresponding target check was local.

Because output ports are disjoint, the complete input response is
`Q = diag(Q_j)`. If a nonzero vector in `ker(Q)` is supported on input
frames contained in a frame `E` of rank at most seven, one of its nonzero
block components is a local kernel vector. The local support result
forces that component's union to have rank seven, and hence to equal `E`.
Premise 4 then forces all supported inputs to belong to that same block.
Consequently every such global kernel is local, all contained inputs
have rank five, and `E` reaches at most one global output. This argument
covers every support in 96 coordinates without a finite-support cutoff.

The two implementations use rational elimination versus integer Gram
principal minors, and binary pivot bases versus explicit sets. They
reproduce all 3060 subset cases and the global premises.

## 3. Input barrier and high-information confinement

Every input must be read because its required output column is nonzero.
A helper cannot read two incomparable fixed input frames while its own
frame grows. There are exactly 96 helpers and 96 required inputs, so the
input-to-helper assignment is a bijection.

An already-read helper cannot mix with an unread one: their common frame
would have to contain the first helper's input frame and fit inside the
second helper's incomparable future input frame. After two read helpers
mix, both exceed their individual input frames and cannot read again.
A target read also prevents a subsequent input read. A helper cannot
write an output before its assigned input, as that would leave one input
without a reader. Moving operations on disjoint helpers past one another
therefore gives a barrier after all input reads and before post-input
mixing. Repeated reads and scaling combine to one nonzero coefficient
per input. In input order the barrier values are

```
h = P(y,x) + D z,
```

where `P` is invertible and `D` is invertible diagonal. This uses the
192 independent boundary coordinates established above.

Each initial high value `x_j` starts at `U_j`. Any physical route for its
information retains that subspace. A helper that ever receives this
information must eventually read an input whose frame contains `U_j`.
By global premise 2, that input belongs to block `j`. The original four
high helpers of block `j` are also confined to its eight input slots.
No high helper from another block can occupy those slots. They thus
contain exactly four original high helpers and four rank-one helpers,
although the latter may have migrated from other blocks.

All columns of `P` belonging to `x_j` are supported on those eight rows,
have rank four by invertibility, and are annihilated by `Q_j D_j^-1`,
since high dirty input has zero output response. Their scaled column
space is exactly `ker(Q_j)`. The same local projection lower bounds
therefore hold after arbitrary cross-block pre-input mixing. The labels
of the four low helpers do not matter for these bounds.

## 4. Complete pre-input cost

For positive growth increments and `0<s<1`, splitting a growth cannot
make it cheaper: `sum d_i^s >= (sum d_i)^s`.

If `u_j=5`, all eight input ranks are six. Every low helper needs a
nonzero `x_j` coefficient by the singleton projection bound. It must
visit `U_j`: pre-input mixing between two distinct future input slots
has rank at most five. The pre-input cost is at least `4*4^s + 8`.

If `u_j=4`, let `S` be the low helpers that first receive `x_j`
information at rank five, and put `k=|S|`. They must have rank-six input
slots; rank-five slots cannot meet another slot at their own frame.
Relative to `1 -> 4 -> 6`, each can save at most

```
A(s) = 3^s + 2^s - 4^s - 1.
```

Their independent `x_j` directions must arrive through carriers that
already possess such information at rank four and then enter rank five.
A carrier cannot return to rank four; later mixing inside rank five
does not supply an additional independent direction. Hence there are
at least `ceil(3k/4)` distinct carriers, by the projection bound.
Confinement keeps every such carrier in this same group. Each carrier
has a rank-six input and a paid `4 -> 5 -> 6` path, and is not in `S`.
Relative to direct `4 -> 6`, its excess is at least `B(s)=2-2^s`.

The inequality `4 A(s) < 3 B(s)` for `0<s<1` pays for all potential
savings. To prove it, let `t=2^s`, `p=log_2(3)`. Then it is equivalent to
`f(t)=4t^2-7t-4t^p+10 > 0` for `1<t<2`. The integer comparisons
`9>8` and `243<256` give `3/2<p<8/5`. Thus `f''(t)>0` on `[1,2]`,
whereas `f'(2)=9-6p<0`. So `f` is decreasing there and exceeds `f(2)=0`.

Writing `n_5+n_6=8` for the input rank counts, the pre-input cost is
therefore at least `4*3^s + n_5 + n_6*2^s`.

## 5. Complete post-input cost, including early retirement

Treat all 96 barrier helper values as independent inputs. Their required
output matrix is `Q D^-1`. Every output write requires rank at least
eight by global premise 3. A helper must mix with another helper before
first reaching rank eight. Otherwise its injected variable, still unique
to that helper, could reach at most one of the distinct target caps,
contrary to its two required outputs. This first mixing strictly exceeds
its incomparable input frame.

Now consider any helper jumping from rank at most seven to its final
rank nine. Put a nonzero perturbation in that helper just before the jump,
with all other current helper and output perturbations zero, and reverse
the executed post-input program. Monotone common-frame interactions keep
every reachable barrier input frame inside the retiring frame `E`.
No earlier target output can respond, since every output write has rank
at least eight. After the jump, no later output cap can be reached either.
The nonzero barrier perturbation is therefore in `ker(Q D^-1)`.

Diagonal scaling does not change supports. Section 2 forces `E` to have
rank seven, to contain only rank-five input frames, and to reach at most
one target. The retiring helper must also have mixed at rank six earlier:
if its first mixing were at rank seven, all routes for its initially
unique injected variable would contain `E` and reach at most one target.
Its path thus includes `5 -> 6 -> 7 -> 9`, costing at least `2+2^s`.
This argument allows previous output writes, information splitting and
mixing with every other block; it is not merely a final-kernel test.

A rank-five input helper that does visit rank eight also costs at least
`2+2^s`, including its first mixing and final restoration. A rank-six
input helper cannot retire below rank eight, since its own input frame
would be contained in `E`. Its path includes `6 -> 7 -> 8 -> 9`, costing
at least three. The complete post-input cost is at least
`n_5*(2+2^s) + 3*n_6`.

## 6. Attainment and supplier accounting

Adding the two parts gives `24+8*2^s+4*3^s` per rank-four group and
`32+4*4^s` per rank-five group. The selected word has seven of the former
and five of the latter, giving the stated bound. Both checkers recount
the literal paths, including completion to full rank, and obtain exactly
`{1:328, 2:56, 3:28, 4:20}`. The original unmixed word is an attaining
member of the enlarged class. There is no proposed replacement to admit.

With the remaining paid profile, role inventory, copied centres, source
ports, target paths, owner map and recurrence held fixed, this lower bound
applies pointwise at `s=1-a` in the complete supplier moment. For each
call, the unchanged exterior contribution plus this minimum is the
original numerator; extra accesses, wrappers, frames or restoration are
nonnegative charges. Multiplication by the unchanged positive call counts
and division by the unchanged normalization preserve the inequality.
The admissible moment region cannot increase by this mechanism.

This does not assert an optimum for scalar primitive counts or constant
compiler allowances. The one-canonical-word orientation convention and
all-size/compiler, common-label/mutable-source, hosting, precision/tape,
exact recovery and analytic interfaces remain inherited. No new kappa,
native admission, full cold replay, hosted CI or unconditional multiplication
theorem is claimed. Extra helpers, altered source/target availability,
additional versions of the input ports, frame descents and changed
centres remain outside the result.
