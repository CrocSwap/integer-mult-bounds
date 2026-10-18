# Complete moment optimum for twelve fixed block interfaces

This note proves an all-order and all-length result. It does not use a bound
on the number of scalar gates or a list of coordinate changes. The finite
checker verifies the interface premises. The argument below proves the result
for every program in the stated class.

## 1. Interface and program class

A replacement uses the retained single-word provider interface. One canonical
forward word defines both orientations. The backward scalar program is the
same-order inverse-transpose dual of that word. Each ADD exchanges its source
and destination and negates its coefficient; each SCALE takes its reciprocal.
Both orientations use the same array-frame itinerary. Independent redesign of
the backward supplier with a different boundary contract is outside this class.

Each block has eight helper arrays of the same volume. Four helpers start at
one-dimensional frames contained in a common frame U. Four helpers start at U.
Write u = dim(U), where u is 4 or 5. Their eight initial scalar values are
independent and arbitrary. Let x be the four values that start at U, and let y
be the other four values.

There are eight read-only external input arrays. Their independent values are
z_i. Input i has a fixed frame F_i. Every F_i contains U. The F_i are pairwise
incomparable. Their dimensions f_i are 5 or 6. If u=5, every f_i is 6.

There are four additive output ports. Port j has its retained late entry frame
G_j, of dimension 7 or 8, and its distinct final hyperplane H_j, of dimension 8.
The source word gives G_j immediately before the first late read from this
block into that target. For every i,j, dim(F_i+G_j) is at least 8. Earlier target
reads and all exterior operations remain fixed. This is the late block
interface: output retiming to an earlier exterior frame is not part of it.

The required increment at these ports is R y + Q z. There is no x term.
Every column of Q is nonzero at exactly two distinct output ports. All eight
helpers must retain their independent dirty information and end at the full
nine-dimensional frame. The retained helper endpoint map can be imposed in
addition; the proof grants any invertible helper endpoint map for its lower
bound.

A program may use any finite number and order of invertible scalar additions
and nonzero scalar multiplications on the eight helpers. Its coefficients are
fixed, not functions of the input values. It may read an
external input repeatedly into helpers, and add helpers to the four output
ports repeatedly. Each addition uses one common frame on its two arrays.
Frames only grow by inclusion. We allow every such frame in the lower bound,
including one that might fail a separate native phase condition. The exact
native transport for a rank-r growth
is charged as one rank-r recursive child. Splitting a growth is allowed and
every part is charged. The class does not allow an extra array, a frame descent,
a target used as scratch, a write to an external input, a changed centre path,
or communication between different blocks. Coefficients may be arbitrary
rational numbers; the argument also works over any characteristic-zero field.

The sources contain twelve blocks with helper bases
592, 600, 608, 624, 632, 640, 648, 656, 672, 680, 688, and 696.
For a base b, its helpers are b,...,b+7. The scalar correction can move past
intervening exterior events to the input segment: it touches only these eight
helpers, and no intervening exterior event uses them. No new operation or
frame is needed for this move. The different times at which the external ports
are ready remain part of the exterior interface; granting all fixed input
ports for the whole block only enlarges the program class used in the lower
bound.

### Binding the interface to the emitted words

Move only the helper-only correction to immediately before its eight input
additions. The checker verifies that these additions are contiguous, use eight
distinct external arrays, and have no intervening exterior operation. It also
verifies that every external array has its specified F_i at this common
boundary. The low helpers still have their old one-dimensional frames before
the deferred correction. The high helpers still have frame U. Thus this is
one common boundary with sixteen distinct physical main arrays.

These sixteen values can vary independently. All main arrays in the retained
native contract have arbitrary initial data. Each addition, nonzero scaling,
and frame transport is invertible. The copied-centre cut adds into target
arrays from copies of non-target arrays. No cut source is a cut target. The
cut is therefore an invertible shear on the main arrays, even though the
copied centre arrays are not independent new inputs. The prefix after the
unchanged preconditioner is invertible. Removing the deferred invertible
helper correction preserves this fact. Any sixteen distinct coordinates of
these main arrays are independent at the boundary.

The certificate gives an additional exact scalar witness for each block. It
pulls the sixteen boundary rows back through the literal A, cut, and B prefix,
with only that correction removed. It selects sixteen original scalar columns
and gives a nonzero 16-by-16 minor. A second calculation replays those columns
forward through the prefix and verifies the same minor. Every minor uses only
eight original source columns and the same eight dirty helper columns. The
checker verifies that the unchanged preconditioner touches only targets.
Thus these witnesses need no independently variable target value. They do not
assume clean helper values or introduce extra physical arrays.

The checker derives R and Q from all subsequent emitted gates that touch the
eight helpers. It records each input index, each late output index, the target
frame immediately before its first late output, and the final target frame.
It verifies that no late target is subsequently scaled or used as a source.
Other additions into those targets commute. Thus the four accumulated port
increments are the actual required increments in the emitted word, and not a
separate handwritten correction matrix.

Universal replacement of this block must therefore satisfy the displayed
matrix identity on all sixteen inputs. Earlier asynchronous availability does
not create a relation between these values. Giving the replacement all eight
external inputs from the start only enlarges the class in the lower bound.

## 2. Exact finite premises

The checker reconstructs Q and all frames from each frozen word. It checks:

1. Q has rank 4. For every set S of at most four coordinates, projection of
   ker(Q) onto S has rank at least ceil(3|S|/4). It computes this rank as
   |S|-4+rank(Q restricted to the complementary columns).
2. No nonzero vector in ker(Q) is supported on a set of input frames whose
   union has dimension at most 6.
3. If a kernel support has frame union F of dimension 7, every input frame
   contained in F has dimension 5, and F is contained in at most one H_j.

These statements concern all subsets of eight columns, not a sampled set.
They also apply to an arbitrary frame F of dimension at most 7. If F contains
a kernel support, premise 2 forces that support's frame union to have dimension
7. Hence that union equals F, and premise 3 applies.

## 3. Input barrier, with repeated reads allowed

Each external input must be read, because its required output column is
nonzero. A helper cannot read two different inputs: it would have to visit
both of their incomparable fixed frames. There are exactly eight helpers and
eight inputs. Thus input-to-helper assignment is a bijection.

This does not assume one read. A helper can read its assigned input repeatedly
at that input's frame. It cannot mix with an as-yet-unread helper after its own
first read: their common frame would contain its F_i and would have to lie in
the other helper's incomparable F_j. When two already-read helpers mix, both
advance strictly beyond their individual input frames. Neither can read its
input again. A target read also precludes any later input read, because target entry rank
is at least 7, above every input rank. In particular, a helper cannot emit
an output before its first assigned input: that would leave one of the eight
required inputs without an available helper.

It follows that all pre-input mixing can be moved before all input reads, and
all post-input mixing after them. Operations moved past each other use disjoint
helpers. Repeated reads and scalar multiplications combine to a nonzero
coefficient d_i for input i. A zero coefficient would erase that input from
all outputs. The helper values at this barrier are therefore

    h = P (y,x) + D z,

up to an input permutation, where P is invertible and D is invertible diagonal.
No helper is assumed clean. An invertible scalar program on eight independent
dirty values cannot create an identically zero helper. A helper may evaluate
to zero on a particular input. That fact cannot change the required linear
identity on arbitrary inputs, or the common-frame requirement of an addition.
There is no read-once assumption or value-based frame reset in this argument.

Let P_x be the four columns of P for x. The output map from h is Q D^-1.
Since x has zero output response, Q D^-1 P_x=0. The matrix P_x has rank 4,
so its scaled column space is exactly ker(Q). Thus the projection bounds in
premise 1 apply to every choice of helper coordinates in the program.

## 4. Cost before the input barrier

For 0<s<1, splitting a rank change cannot reduce its cost: sum d_i^s is at
least (sum d_i)^s.

First take u=5. Every low helper must acquire a nonzero x coefficient, by
premise 1. A surviving x dependency requires the common source frame U.
Before the inputs, an interaction of two helpers has rank at most 5 because
their future input frames are incomparable and have rank 6. Thus every low
helper visits U exactly as a frame stop. The pre-input cost is at least

    4*4^s + 8.

Now take u=4. A pre-input interaction has rank at most 5. A low helper can
first acquire an x coefficient either at U (rank 4) or at rank 5. Call the
latter helpers S, and let k=|S|. A helper in S must be assigned an input of
rank 6; a rank-5 input frame cannot be a common frame with any other input's
helper. Grant the best cost 4^s+1 to each helper in S. Relative to the usual
rank path 1->4->6, its possible saving is at most

    A(s)=3^s+2^s-4^s-1.

The x information in these k rows must come through helpers that entered the
rank-5 region carrying x information from rank 4. Each such carrier supplies
at most one new independent x direction when it first enters that region.
It cannot return to rank 4. Later mixing within rank 5 adds no new direction.
A low helper that first acquires x at rank 5 is already counted in S, so it is
not a new source of x information. Thus, if c is the number of carriers,

    c >= rank(P_x restricted to S) >= ceil(3k/4).

Every carrier must be assigned an input of rank 6: a helper assigned a
different rank-5 input cannot meet another helper at that frame. Each carrier
therefore pays a rank-4 stop, a rank-5 stop, and its rank-6 input stop. It is
not in S. Relative to a direct 4->6 growth, its extra cost is at least

    B(s)=2-2^s.

The elementary inequality 4A(s)<=3B(s), proved below, gives kA(s)<=cB(s).
All possible savings are paid by distinct carrier costs. If n_5 and n_6 are
the counts of input ranks 5 and 6, the complete pre-input cost is at least

    4*3^s + n_5 + n_6*2^s.

For the power inequality, put t=2^s in (1,2) and p=log_2(3). We need

    f(t)=4t^2-7t-4t^p+10 >= 0.

The integer inequalities 9>8 and 243<256 give 3/2<p<8/5. Hence f''(t)>0
on [1,2], while f'(2)=9-6p<0. Thus f is decreasing on [1,2], and f(t)>=f(2)=0.
The inequality is strict for 0<s<1.

## 5. Cost after the input barrier

Use h as eight independent formal inputs. Scaling or permuting its coordinates
does not change any support or rank premise. Its output matrix is Q D^-1.

Every target read has rank at least 8. The reading helper contains its F_i,
the target contains G_j, and dim(F_i+G_j)>=8. The output caps are the distinct
rank-8 hyperplanes H_j.

Each helper must mix with another helper before it first reaches rank 8.
Until that first mixing, its injected variable occurs in no other helper.
If it reached rank 8 first, every later path for that variable would contain
that rank-8 frame and could reach at most one of the distinct H_j. Its required
column has two nonzero entries. This is a contradiction. The first mixing has
rank at least f_i+1, because it includes another incomparable input frame.

It remains to account for a helper that has already helped deliver outputs
and then jumps from rank at most 7 directly to rank 9. This case is permitted;
the proof does not impose a rank-8 stop on every helper.

Just before such a jump, put a nonzero perturbation on that helper and zero
on all other current helpers and outputs. Reverse the full executed prefix.
At each reversed addition, the perturbation can reach only a register whose
frame is contained in the retiring frame F. Thus it cannot reach an earlier
target read, all of which have rank at least 8. All outputs already written
have zero response to this perturbation. At the input barrier it is a nonzero
vector v supported only on input frames contained in F. It is nonzero because
the helper transformation is invertible.

After the jump to rank 9, no path from that helper can reach a rank-8 target
cap. Hence all later outputs also have zero response. Exactness implies Qv=0.
This argument includes arbitrary information splitting and all earlier output
writes, not only a terminal kernel condition.

Premises 2 and 3 now imply dim(F)=7, f_i=5, and F is eligible for at most one
output port. This helper must have mixed earlier at rank 6. If its first
post-input mixing occurred at rank 7, that frame would be F by monotonicity;
the still unique injected variable could then reach at most one output, a
contradiction. Its rank path therefore includes 5->6->7->9 and costs at least

    2+2^s.

If a rank-5 input helper does visit rank 8, its first mixing is at rank 6 or 7.
The cheapest path through such a stop, rank 8 and final rank 9 has the same
cost 2+2^s. A rank-6 input helper cannot retire below rank 8 by premise 3.
Its path includes 6->7->8->9 and costs at least 3. The total post-input cost is
therefore at least

    n_5*(2+2^s) + 3*n_6.

## 6. Attainment and complete supplier moment

Combining the two parts gives the following optimum for one block:

    u=4: 24 + 8*2^s + 4*3^s;
    u=5: 32 + 4*4^s.

The exact native source word attains these expressions. The checker recounts
all eight helper paths, including their final growth to rank 9. This is an
optimum over arbitrary finite scalar factorizations in the declared class,
not a finite search optimum.

The orientation rule matters for the controller conclusion. The pinned
`hpe_emit_local.py` computes the frame climbs from the canonical gate before
it applies its `dual` scalar rule. Swapping an ADD's two arrays leaves its
common-frame requirement unchanged. A reciprocal SCALE uses the same array.
Thus every scalar replacement emits the same ranked helper climbs in both
orientations. Algebraically, same-order inverse-transpose replaces a complete
matrix M by M^-T. It does not require reversing the frame itinerary. The centre
copy path reverses direction but retains each absolute rank change and the
same complete charge. Centres are fixed in this theorem.

The selected emitted LOCAL-PROGRAMS file is included as exact evidence. The
checker verifies equality of all 3486 climb events, inverse-transpose duality
of every non-centre scalar, and equality of the complete paid profile. The
same retained emitter is the native provider path for the two pinned PR1319
words. This is a source-bound orientation contract, not a claim that every
possible independently synthesized backward circuit has equal cost.

Let L(a) be the sum of block costs at s=1-a. For any replacement of any subset
of the twelve blocks, L_new(a)>=L_old(a) for every 0<a<1. All arrays have the
same retained volume. Source access, phase maps, restoration and extra scalar
work are not negative charges. The other local paths, copied centre charge,
endpoint law, owners, idle paths and bit supplier are fixed. Consequently the
complete complex supplier moment satisfies

    Psi_new(a) >= [H_rest(a) + sum_calls L_new(a)] / (W*73^(1-a))
               >= Psi_old(a).

Any additional paid source, phase, or restoration work explains the first
inequality. The retained word attains equality with its original block costs.
The comparison holds pointwise, not just at one claimed endpoint. The complex
admissible exponent cannot increase under this replacement class. The bit
constraint and all other outer-recipe conditions are unchanged. Every admissible tuple
of exponents and outer parameters for a replacement is therefore also
admissible for the retained supplier. This feasible-set inclusion proves that
the optimum complete outer kappa cannot improve through this class. It does
not identify the bit primitive exponent c with the outer kappa, or turn the
complex-only moment root into an outer exponent.

The selected PR1094 word has seven u=4 and five u=5 blocks here. Their total is
328H1+56H2+28H3+20H4. The PR1319 base provider has ten u=4 and two u=5 blocks,
with total 304H1+80H2+40H3+8H4. Its extra provider has eleven u=4 and one
u=5 block, with total 296H1+88H2+44H3+4H4. The conclusion applies separately to each
provider and hence to the stronger pending mixed construction as well.

This closes the fixed eight-array late-interface coalescing approach. It does
not exclude changed external availability or output frames, target scratch,
extra arrays, cross-block coding, frame descents, an independently designed
backward interface, or another native operation alphabet. Such changes need their own complete cost and interface proof.
